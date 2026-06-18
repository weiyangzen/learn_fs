<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/axis-fifo.c -->
# sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/axis-fifo.c

Purpose: implements a platform/misc character driver for Xilinx AXI-Stream FIFO IP. It exposes packet-oriented FIFO reads and writes to userspace, interrupt-driven blocking semantics, polling, and a small debugfs register view.

Important APIs/types/functions: `struct axis_fifo` stores MMIO base, FIFO depths/capability flags, wait queues, locks, misc device, and debugfs dentry. File operations are `axis_fifo_open()`, `axis_fifo_read()`, `axis_fifo_write()`, and `axis_fifo_poll()`. Probe/remove are `axis_fifo_probe()` and `axis_fifo_remove()`. `axis_fifo_irq()` handles receive/transmit/error interrupts. `axis_fifo_parse_dt()` requires 32-bit RX/TX data widths and reads FIFO depth and use flags.

Control flow: probe allocates state, maps MMIO, parses OF properties, resets/enables interrupts, requests IRQ, allocates an ID, registers `/dev/axis_fifoN`, and creates debugfs. Reads lock the RX path, wait for receive occupancy unless nonblocking, read packet length, validate user buffer and word alignment, drain data words through a small stack buffer, and flush on errors. Writes validate word-aligned packet length and FIFO depth, wait for vacancy, copy userspace data with `vmemdup_user()`, write data words, then write transmit length. IRQ wakes read/write wait queues and logs FIFO protocol errors.

State and persistence: all state is volatile hardware/device state. FIFO contents are consumed by reads/writes. No persistent storage exists.

Dependencies and integration: depends on platform/OF, MMIO, IRQ, miscdevice, debugfs, poll, wait queues, mutexes, and Xilinx register semantics.

Risks: userspace ABI is packet-oriented and rejects partial buffers. `axis_fifo_read()` flushes unread packet data on several errors, causing data loss by design. Debugfs exposes live registers without locking. Removal does not explicitly reset hardware after deregistration. Correctness depends on Device Tree properties matching generated IP.

Test signals: blocking and nonblocking read/write, poll readiness, packet sizes at zero, unaligned, exact FIFO limit and over-limit, RX packet larger than user buffer, IRQ wakeups, error interrupts, debugfs `regs`, and OF probe failures for non-32-bit widths or missing properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/axis-fifo.c -->
