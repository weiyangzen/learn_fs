# sources/distributed-fs/ceph-client/drivers/ptp/ptp_private.h

Purpose: defines private data structures and internal interfaces shared by the PTP core implementation files. It is not a hardware driver; it is the internal contract for the PTP class device, character-device operations, sysfs, pin handling, event queues, auxiliary work, virtual clocks, and debugfs state.

Important APIs/types/functions: `struct timestamp_event_queue` is the external timestamp FIFO with lock, head/tail indices, optional mask, list linkage, and debugfs metadata. `struct ptp_clock` embeds the POSIX clock and device, stores the driver `ptp_clock_info`, PPS source, event queue list, pin config attributes, worker state, virtual-clock limits and indexes, flags for virtual/has-cycles behavior, and debugfs root. `struct ptp_vclock` defines child virtual PHCs backed by a parent clock, cyclecounter/timecounter pair, mutex, and RCU hash linkage. Inline helpers are `queue_cnt()`, `ptp_vclock_in_use()`, and `ptp_clock_freerun()`.

Control flow: the header declares operations implemented in `ptp_chardev.c`, `ptp_sysfs.c`, and `ptp_vclock.c`. `queue_cnt()` uses `READ_ONCE()` to allow lockless non-empty checks paired with writer `WRITE_ONCE()` updates. `ptp_vclock_in_use()` avoids taking `n_vclocks_mux` on virtual clocks to prevent lockdep false positives from nested physical/virtual calls. `ptp_clock_freerun()` forces non-cycle-capable physical clocks into free-running behavior when virtual clocks depend on them.

State and persistence: all structures represent live kernel state. There is no on-disk persistence. The most durable state is user-visible device identity, event queues, pin attributes, virtual-clock child indexes, and debugfs entries for the lifetime of a registered PTP clock.

Dependencies and integration: includes cdev, device, kthread, mutex, posix-clock, PTP kernel/public APIs, list, bitmap, and debugfs headers. It is consumed by PTP core source files rather than external drivers.

Risks and test signals: this header encodes locking assumptions across the PTP core. Misusing `queue_cnt()` without understanding its non-empty-only guarantee can race with dequeues. Virtual-clock locking must avoid stacking virtual clocks on virtual clocks. Test through core PTP registration/unregistration, open/read/poll/ioctl, EXTS FIFO wraparound, pin sysfs creation/removal, vclock creation/deletion, and lockdep under concurrent physical and virtual clock operations.
