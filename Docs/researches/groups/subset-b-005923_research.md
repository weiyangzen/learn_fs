<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysfs.h -->
# sources/distributed-fs/ceph-client/include/linux/sysfs.h

## Purpose
defines the kernel-facing sysfs attribute model layered over kernfs: text attributes, binary attributes, attribute groups, visibility callbacks, permission helpers, link/group/file creation APIs, ownership-changing APIs, and no-op stubs for builds without CONFIG_SYSFS.

## Important APIs, Types, and Functions
The file is 825 lines and exports these visible symbol families: types/enums `kobject`, `module`, `bin_attribute`, `kobj_ns_type`, `attribute`, `attribute_group`, `file`, `vm_area_struct`, `address_space`, `sysfs_ops`, `kernfs_node`; macros/constants `_SYSFS_H_`, `SYSFS_PREALLOC`, `SYSFS_GROUP_INVISIBLE`, `__ATTR_NULL`, `__ATTR_IGNORE_LOCKDEP`, `__BIN_ATTR_NULL`; function-like macros `sysfs_attr_init`, `__SYSFS_FUNCTION_ALTERNATIVE`, `DEFINE_SYSFS_GROUP_VISIBLE`, `DEFINE_SIMPLE_SYSFS_GROUP_VISIBLE`, `DEFINE_SYSFS_BIN_GROUP_VISIBLE`, `DEFINE_SIMPLE_SYSFS_BIN_GROUP_VISIBLE`, `SYSFS_GROUP_VISIBLE`, `__ATTR`, `__ATTR_PREALLOC`, `__ATTR_RO_MODE`, `__ATTR_RO`, `__ATTR_RW_MODE`, `__ATTR_WO`, `__ATTR_RW`, and 21 more; inline helpers `sysfs_enable_ns`, `sysfs_create_dir_ns`, `sysfs_remove_dir`, `sysfs_rename_dir_ns`, `sysfs_move_dir_ns`, `sysfs_create_mount_point`, `sysfs_remove_mount_point`, `sysfs_create_file_ns`, `sysfs_create_files`, `sysfs_chmod_file`, `sysfs_break_active_protection`, `sysfs_unbreak_active_protection`, `sysfs_remove_file_ns`, `sysfs_remove_file_self`, and 36 more; external prototypes `umode_t`, `DEFINE_SYSFS_GROUP_VISIBLE`, `DEFINE_SIMPLE_SYSFS_GROUP_VISIBLE`, `sysfs_create_dir_ns`, `sysfs_remove_dir`, `sysfs_rename_dir_ns`, `sysfs_move_dir_ns`, `sysfs_create_mount_point`, `sysfs_remove_mount_point`, `sysfs_create_file_ns`, `sysfs_create_files`, `sysfs_chmod_file`, `sysfs_unbreak_active_protection`, `sysfs_remove_file_ns`, and 34 more.

## Control Flow
Drivers declare `struct attribute`, `struct bin_attribute`, or `struct attribute_group` objects, usually through the `__ATTR*`, `ATTRIBUTE_GROUPS`, and `BIN_ATTR*` macros, then attach them to a `kobject` with create/group/link helpers. Show/store/read/write callbacks are invoked later by VFS/sysfs paths through `sysfs_ops` or binary attribute callbacks. Removal APIs tear down nodes, and `sysfs_notify*` wakes pollers when values change.

## State and Persistence Behavior
The header itself stores no state, but its objects become kernfs nodes with lifetime bound to the owning kobject and module/static storage of callback tables. Attribute visibility and ownership are evaluated at creation/update time; `sysfs_break_active_protection()` temporarily alters active protection for self-removal paths.

## Dependencies and Integration Points
It depends on kobject, kernfs, namespace, stat, lockdep, and uid/gid types. It is a central integration point for device model, driver-core attributes, module parameters exposed through kobjects, and any subsystem exporting kernel state through `/sys`. Direct includes are `linux/kernfs.h`, `linux/compiler.h`, `linux/errno.h`, `linux/list.h`, `linux/lockdep.h`, `linux/kobject_ns.h`, `linux/stat.h`, `linux/atomic.h`.

## Risks and Edge Cases
Common failure modes are unsafe permissions, non-terminated attribute arrays, callbacks returning more than PAGE_SIZE, lifetime bugs when dynamic attributes are removed while callbacks run, and forgetting that CONFIG_SYSFS stubs return success while exporting nothing. `VERIFY_OCTAL_PERMISSIONS()` intentionally rejects world-writable files and non-octal-like modes.

## Test Signals
Build with CONFIG_SYSFS on and off, enable lockdep for dynamically allocated attributes, exercise create/update/remove/link/group paths under kobject teardown, validate permissions with sysfs selftests, and run poll/notify plus binary read/write/mmap coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syslog.h -->
# sources/distributed-fs/ceph-client/include/linux/syslog.h

## Purpose
declares the in-kernel syslog/printk ring-buffer control surface used by `syslog(2)` and `/proc/kmsg` style readers.

## Important APIs, Types, and Functions
The file is 43 lines and exports these visible symbol families: types/enums none; macros/constants `SYSLOG_ACTION_CLOSE`, `SYSLOG_ACTION_OPEN`, `SYSLOG_ACTION_READ`, `SYSLOG_ACTION_READ_ALL`, `SYSLOG_ACTION_READ_CLEAR`, `SYSLOG_ACTION_CLEAR`, `SYSLOG_ACTION_CONSOLE_OFF`, `SYSLOG_ACTION_CONSOLE_ON`, `SYSLOG_ACTION_CONSOLE_LEVEL`, `SYSLOG_ACTION_SIZE_UNREAD`, `SYSLOG_ACTION_SIZE_BUFFER`, `SYSLOG_FROM_READER`, `SYSLOG_FROM_PROC`; function-like macros none; inline helpers none; external prototypes `do_syslog`.

## Control Flow
`do_syslog()` dispatches action codes such as read, read-all, read-clear, clear, console on/off, console level, and size queries. `SYSLOG_FROM_READER` and `SYSLOG_FROM_PROC` let implementation code distinguish a direct log reader from procfs access, while `log_wait` is the wait queue for blocking log consumers.

## State and Persistence Behavior
Runtime state lives in printk's log buffer, console loglevel, reader cursors, and the exported wait queue; this header only names actions and the public entry point.

## Dependencies and Integration Points
It depends on wait queues and user-pointer annotations, and integrates with printk, syscalls, procfs, and console policy. Direct includes are `linux/wait.h`.

## Risks and Edge Cases
The main risks are action-code ABI drift, privilege mistakes around clear/console-level operations, user buffer length handling, and wakeup/cursor bugs that can lose log records or spin readers.

## Test Signals
Exercise each action through syscall/proc paths, check capability gating, verify blocking readers wake on printk, and validate unread-size and buffer-size accounting across clear and read-clear operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syslog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysrq.h -->
# sources/distributed-fs/ceph-client/include/linux/sysrq.h

## Purpose
defines the Magic SysRq registration API and enable-mask categories for emergency kernel commands.

## Important APIs, Types, and Functions
The file is 84 lines and exports these visible symbol families: types/enums `sysrq_key_op`; macros/constants `SYSRQ_ENABLE_LOG`, `SYSRQ_ENABLE_KEYBOARD`, `SYSRQ_ENABLE_DUMP`, `SYSRQ_ENABLE_SYNC`, `SYSRQ_ENABLE_REMOUNT`, `SYSRQ_ENABLE_SIGNAL`, `SYSRQ_ENABLE_BOOT`, `SYSRQ_ENABLE_RTNICE`; function-like macros none; inline helpers `handle_sysrq`, `__handle_sysrq`, `register_sysrq_key`, `unregister_sysrq_key`, `sysrq_mask`; external prototypes `handle_sysrq`, `__handle_sysrq`, `register_sysrq_key`, `unregister_sysrq_key`, `sysrq_toggle_support`, `sysrq_mask`.

## Control Flow
Drivers or core code register `struct sysrq_key_op` handlers by key. `handle_sysrq()` and `__handle_sysrq()` dispatch a key, optionally checking the mask returned by `sysrq_mask()`. CONFIG_MAGIC_SYSRQ=n builds compile to inert stubs that reject registration.

## State and Persistence Behavior
Registered key operations and the enable mask are global kernel state. Individual operations may sync disks, remount filesystems, dump state, signal tasks, adjust RT priority, or reboot.

## Dependencies and Integration Points
It depends on errno/types and integrates with keyboard/serial console input, proc/sysctl sysrq mask control, crash/debug code, and reboot/sync/remount paths. Direct includes are `linux/errno.h`, `linux/types.h`.

## Risks and Edge Cases
SysRq handlers are emergency paths and may run in hostile contexts. Incorrect enable masks can expose destructive actions, and handlers must not assume normal scheduler or locking progress.

## Test Signals
Build with CONFIG_MAGIC_SYSRQ enabled and disabled, register/unregister test handlers, verify mask enforcement per category, and run selected non-destructive commands through keyboard and proc-trigger paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysrq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/t10-pi.h -->
# sources/distributed-fs/ceph-client/include/linux/t10-pi.h

## Purpose
defines SCSI/T10 Protection Information tuple formats and helpers for computing protection reference tags from block requests.

## Important APIs, Types, and Functions
The file is 77 lines and exports these visible symbol families: types/enums `t10_dif_type`, `t10_pi_tuple`, `crc64_pi_tuple`; macros/constants `T10_PI_APP_ESCAPE`, `T10_PI_REF_ESCAPE`; function-like macros none; inline helpers `full_pi_ref_tag`, `t10_pi_ref_tag`, `lower_48_bits`, `ext_pi_ref_tag`; external prototypes `blk_rq_pos`, `lower_32_bits`, `lower_48_bits`.

## Control Flow
Block integrity code determines a request's logical reference tag with `full_pi_ref_tag()`, narrows it with `t10_pi_ref_tag()` for classic 32-bit PI, or `ext_pi_ref_tag()` for 48-bit CRC64 PI. Storage drivers then fill or verify guard, application, and reference tags around payload sectors.

## State and Persistence Behavior
There is no persistent state in the header. The computed tag derives from request position, queue logical block size, and optional integrity interval exponent.

## Dependencies and Integration Points
It depends on request/queue helpers from blk-mq, endian types, and wordpart helpers; it integrates with block integrity profiles, SCSI/NVMe target/initiator code, and DIF/DIX-capable storage. Direct includes are `linux/types.h`, `linux/blk-mq.h`, `linux/wordpart.h`.

## Risks and Edge Cases
Bad sector-shift math or interval-exp handling corrupts protection tags. Endian mistakes in `t10_pi_tuple` and CRC64 tuple fields can cause media verify failures or silent data-integrity gaps.

## Test Signals
Run block integrity tests across 512B/4K and non-default interval sizes, verify 32-bit and 48-bit reference tags at large LBAs, and use sparse/endian checks for tuple assignments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/t10-pi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/task_io_accounting.h -->
# sources/distributed-fs/ceph-client/include/linux/task_io_accounting.h

## Purpose
defines the per-task I/O accounting record embedded in `task_struct` when extended accounting options are enabled.

## Important APIs, Types, and Functions
The file is 47 lines and exports these visible symbol families: types/enums `task_io_accounting`; macros/constants none; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Accounting helpers increment character I/O counters (`rchar`, `wchar`, `syscr`, `syscw`) and block I/O counters (`read_bytes`, `write_bytes`, `cancelled_write_bytes`) as syscalls and storage operations proceed. Exit/accounting paths aggregate these fields into taskstats and process summaries.

## State and Persistence Behavior
The structure is persistent for the lifetime of a task. Fields compile in only under CONFIG_TASK_XACCT and CONFIG_TASK_IO_ACCOUNTING, so consumers must tolerate absent or zeroed counters in smaller configurations.

## Dependencies and Integration Points
It is intentionally included through scheduler headers and depends on kernel integer types already available there. Direct includes are none.

## Risks and Edge Cases
Configuration-dependent layout and semantics are the main concern. Cancelled writes are not negative write bytes, and block counters represent bytes caused rather than necessarily completed by the task.

## Test Signals
Build all relevant config combinations, compare `/proc/<pid>/io` and taskstats values with known read/write/truncate workloads, and verify fork/exit aggregation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/task_io_accounting.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/task_io_accounting_ops.h -->
# sources/distributed-fs/ceph-client/include/linux/task_io_accounting_ops.h

## Purpose
provides inline helpers that initialize, increment, convert, and aggregate `struct task_io_accounting` fields.

## Important APIs, Types, and Functions
The file is 115 lines and exports these visible symbol families: types/enums none; macros/constants `__TASK_IO_ACCOUNTING_OPS_INCLUDED`; function-like macros none; inline helpers `task_io_account_read`, `task_io_get_inblock`, `task_io_account_write`, `task_io_get_oublock`, `task_io_account_cancelled_write`, `task_io_accounting_init`, `task_blk_io_accounting_add`, `task_chr_io_accounting_add`, `task_io_accounting_add`; external prototypes none.

## Control Flow
Callers use `task_io_account_read/write/cancelled_write()` against `current`, convert byte counters to 512-byte block counts with `task_io_get_inblock()` and `task_io_get_oublock()`, initialize records, and aggregate character plus block accounting through `task_io_accounting_add()`.

## State and Persistence Behavior
The helpers mutate per-task accounting in `current->ioac` when enabled. Disabled configurations compile to no-op or zero-return helpers, preserving call-site code without collecting state.

## Dependencies and Integration Points
It depends on `linux/sched.h`, `current`, `task_struct`, and the configuration-selected fields from `task_io_accounting.h`. Direct includes are `linux/sched.h`.

## Risks and Edge Cases
Counters are plain increments and rely on appropriate task context; using the helpers for another task without locking is not supported. The block conversion is approximate because it shifts byte counters by nine.

## Test Signals
Compile CONFIG_TASK_IO_ACCOUNTING and CONFIG_TASK_XACCT combinations, run accounting selftests or proc/taskstats checks, and cover aggregation from child to group statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/task_io_accounting_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/task_work.h -->
# sources/distributed-fs/ceph-client/include/linux/task_work.h

## Purpose
declares task-work callbacks: small deferred callbacks attached to a task and run on return-to-user, signal delivery, NMI-current, or explicit task-work drain paths.

## Important APIs, Types, and Functions
The file is 44 lines and exports these visible symbol families: types/enums `task_work_notify_mode`, `callback_head`; macros/constants none; function-like macros none; inline helpers `init_task_work`, `task_work_pending`, `exit_task_work`; external prototypes `void`, `READ_ONCE`, `task_work_add`, `task_work_cancel`, `task_work_run`.

## Control Flow
A callback head is initialized with `init_task_work()`, queued with `task_work_add()` using a notify mode, optionally cancelled by callback or match function, and executed by `task_work_run()` at safe task checkpoints. `exit_task_work()` drains pending work during task exit.

## State and Persistence Behavior
Pending work is held on `task_struct::task_works`; `task_work_pending()` reads that pointer. Callback ownership transfers to the task-work machinery once successfully queued.

## Dependencies and Integration Points
It depends on callback_head/list and scheduler task structures. It integrates with io_uring, fput/deferred file cleanup, task exit, signal/resume hooks, and architecture return-to-user notification. Direct includes are `linux/list.h`, `linux/sched.h`.

## Risks and Edge Cases
Callbacks run in the target task context and must handle cancellation, exit, and ordering carefully. Queuing to exiting tasks or assuming immediate execution can leak resources or defer cleanup too long.

## Test Signals
Exercise each notify mode, cancellation by function and predicate, exit draining, nested callback addition, and races with task exit and signal delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/task_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/taskstats_kern.h -->
# sources/distributed-fs/ceph-client/include/linux/taskstats_kern.h

## Purpose
declares kernel internals for the taskstats subsystem, including exit hooks and per-thread-group statistics cache handling.

## Important APIs, Types, and Functions
The file is 38 lines and exports these visible symbol families: types/enums none; macros/constants none; function-like macros none; inline helpers `taskstats_tgid_free`, `taskstats_exit`, `taskstats_init_early`; external prototypes `kmem_cache_free`, `taskstats_exit`, `taskstats_init_early`.

## Control Flow
When CONFIG_TASKSTATS is enabled, early init creates the cache, exit paths call `taskstats_exit()`, and signal teardown frees thread-group stats with `taskstats_tgid_free()`. Disabled builds use empty stubs.

## State and Persistence Behavior
State is in `taskstats_cache`, `taskstats_exit_mutex`, and optional `signal_struct::stats` allocations. The header only exposes lifecycle hooks.

## Dependencies and Integration Points
It depends on taskstats UAPI structures, scheduler signal state, slab allocation, and mutex protection in the implementation. Direct includes are `linux/taskstats.h`, `linux/sched/signal.h`, `linux/slab.h`.

## Risks and Edge Cases
Exit accounting is sensitive to group-dead ordering and locking. Failing to free `sig->stats` leaks memory, while racing netlink/taskstats queries against exit can expose partially updated data.

## Test Signals
Run taskstats netlink tests across single-threaded and thread-group exits, build CONFIG_TASKSTATS off, and check kmem-cache lifetime with slab debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/taskstats_kern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tboot.h -->
# sources/distributed-fs/ceph-client/include/linux/tboot.h

## Purpose
defines the shared-memory ABI between Linux and Intel TXT/tboot for measured launch shutdown, S3 resume, ACPI sleep handoff, MAC regions, and DMAR-table retrieval.

## Important APIs, Types, and Functions
The file is 142 lines and exports these visible symbol families: types/enums `tboot_mac_region`, `tboot_acpi_generic_address`, `tboot_acpi_sleep_info`, `tboot`; macros/constants `TB_KEY_SIZE`, `MAX_TB_MAC_REGIONS`, `TBOOT_UUID`; function-like macros `tboot_enabled`, `tboot_probe`, `tboot_shutdown`, `tboot_sleep`, `tboot_get_dmar_table`; inline helpers none; external prototypes `tboot_enabled`, `tboot_probe`, `tboot_shutdown`.

## Control Flow
On TXT systems, `tboot_probe()` locates and validates the shared tboot page, runtime code asks `tboot_enabled()`, shutdown/suspend calls `tboot_shutdown()` with a `TB_SHUTDOWN_*` code, and IOMMU setup may use `tboot_get_dmar_table()`.

## State and Persistence Behavior
The packed `struct tboot` page holds versioned state supplied by tboot plus kernel-updated ACPI sleep info, shutdown type, S3 key, MAC regions, and wait-for-SIPI count. Non-TXT builds compile to stubs.

## Dependencies and Integration Points
It depends on ACPI table structures for CONFIG_INTEL_TXT and integrates with x86 TXT boot, ACPI sleep/shutdown, IOMMU DMAR discovery, and low-level CPU rendezvous. Direct includes are `linux/acpi.h`.

## Risks and Edge Cases
This is a firmware ABI: packing, alignment, version fields, physical addresses, and UUID values must not drift. Incorrect sleep/shutdown fields can break secure resume or leave measured state inconsistent.

## Test Signals
Build with and without CONFIG_INTEL_TXT, validate structure offsets against tboot documentation, boot TXT-capable hardware, and test reboot, S3/S4/S5, and DMAR handoff paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tc.h -->
# sources/distributed-fs/ceph-client/include/linux/tc.h

## Purpose
declares TURBOchannel bus, device, driver, ROM-offset, and PROM-access interfaces for legacy DEC/MIPS systems.

## Important APIs, Types, and Functions
The file is 143 lines and exports these visible symbol families: types/enums `tcinfo`, `tc_bus`, `tc_dev`, `tc_device_id`, `tc_driver`; macros/constants `TC_OLDCARD`, `TC_NEWCARD`, `TC_ROM_WIDTH`, `TC_ROM_STRIDE`, `TC_ROM_SIZE`, `TC_SLOT_SIZE`, `TC_PATTERN0`, `TC_PATTERN1`, `TC_PATTERN2`, `TC_PATTERN3`, `TC_FIRM_VER`, `TC_VENDOR`, `TC_MODULE`, `TC_FIRM_TYPE`, and 2 more; function-like macros `to_tc_dev`, `to_tc_driver`; inline helpers `tc_get_speed`, `tc_register_driver`, `tc_unregister_driver`; external prototypes `tc_register_driver`, `tc_unregister_driver`, `tc_preadb`, `tc_bus_get_info`, `tc_device_get_irq`.

## Control Flow
Architecture code obtains bus info through PROM helpers, scans slot ROMs using the defined offsets, creates `tc_dev` instances, and binds `tc_driver` instances registered on `tc_bus_type`. `tc_get_speed()` derives bus frequency from PROM clock period.

## State and Persistence Behavior
Runtime state is in `tc_bus` device lists/resources and `tc_dev` resources, DMA masks, slot IDs, and interrupt numbers. CONFIG_TC=n leaves driver registration as no-op stubs.

## Dependencies and Integration Points
It depends on the Linux device model, resources, list handling, and architecture-provided PROM/IRQ helpers. Direct includes are `linux/compiler.h`, `linux/device.h`, `linux/ioport.h`, `linux/types.h`.

## Risks and Edge Cases
ROM parsing offsets and fixed-size vendor/name strings are ABI-like. Bad slot resource or DMA-mask setup can make legacy drivers access the wrong bus window.

## Test Signals
Compile MIPS/TURBOchannel configs, scan representative ROM images or hardware, verify driver match tables, and check resource/IRQ assignment during probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tcp.h -->
# sources/distributed-fs/ceph-client/include/linux/tcp.h

## Purpose
defines the kernel TCP socket state structures, request/time-wait variants, option records, SACK/Fast Open helpers, TSQ deferred flags, and socket option setter prototypes used by the networking stack.

## Important APIs, Types, and Functions
The file is 663 lines and exports these visible symbol families: types/enums `tcp_fastopen_cookie`, `tcp_sack_block_wire`, `tcp_sack_block`, `tcp_options_received`, `tcp_request_sock_ops`, `tcp_request_sock`, `tcp_sock`, `tsq_enum`, `tsq_flags`, `tcp_timewait_sock`, `sk_buff`; macros/constants `TCP_FASTOPEN_COOKIE_MIN`, `TCP_FASTOPEN_COOKIE_MAX`, `TCP_FASTOPEN_COOKIE_SIZE`, `TCP_SACK_SEEN`, `TCP_DSACK_SEEN`, `TCP_NUM_SACKS`, `TCP_RMEM_TO_WIN_SCALE`, `TCP_RACK_RECOVERY_THRESH`, `TCP_DEFERRED_ALL`, `tw_rcv_nxt`, `tw_snd_nxt`; function-like macros `tcp_rsk`, `BPF_SOCK_OPS_TEST_FLAG`, `tcp_sk`, `tcp_sk_rw`; inline helpers `__tcp_hdrlen`, `tcp_hdrlen`, `inner_tcp_hdrlen`, `skb_tcp_all_headers`, `skb_inner_tcp_all_headers`, `tcp_optlen`, `tcp_clear_options`, `tcp_rsk_used_ao`, `tcp_passive_fastopen`, `fastopen_queue_tune`, `tcp_move_syn`, `tcp_saved_syn_free`, `tcp_saved_syn_len`, `tcp_mss_clamp`, and 1 more; external prototypes `__tcp_hdrlen`, `skb_transport_offset`, `skb_inner_transport_offset`, `WRITE_ONCE`, `tcp_skb_shift`, `__tcp_sock_set_cork`, `tcp_sock_set_cork`, `tcp_sock_set_keepcnt`, `tcp_sock_set_keepidle_locked`, `tcp_sock_set_keepidle`, `tcp_sock_set_keepintvl`, `__tcp_sock_set_nodelay`, `tcp_sock_set_nodelay`, `tcp_sock_set_quickack`, and 4 more.

## Control Flow
Packet paths use header helpers (`tcp_hdr()`, `tcp_hdrlen()`, inner-header variants, `skb_tcp_all_headers()`) to locate TCP headers in skbs. Listener/SYN processing uses `tcp_request_sock`; established sockets use `struct tcp_sock` embedded after `inet_connection_sock`; time-wait sockets use `tcp_timewait_sock`. Timers, release callbacks, ACK processing, congestion control, Fast Open, SACK/RACK, ECN/AccECN, MPTCP/SMC, MD5/TCP-AO, BPF sock_ops, and pacing update fields in `tcp_sock`.

## State and Persistence Behavior
`struct tcp_sock` is long-lived per connection and stores send/receive sequence space, windows, RTT estimators, congestion state, retransmit and out-of-order queues, timers, ECN counters, Fast Open state, security options, and statistics. Request sockets and time-wait sockets hold reduced state for handshake and TIME_WAIT lifetimes.

## Dependencies and Integration Points
It depends on skbuff, socket, inet connection/timewait state, UAPI TCP definitions, hrtimers, lists, rbtree state, optional TLS, MPTCP, SMC, MD5, TCP-AO, and BPF features. Direct includes are `linux/skbuff.h`, `linux/win_minmax.h`, `net/sock.h`, `net/inet_connection_sock.h`, `net/inet_timewait_sock.h`, `uapi/linux/tcp.h`.

## Risks and Edge Cases
Cacheline layout and field semantics are performance-critical and documented externally. Lockless listener reads require READ_ONCE-style care; endian/header-length mistakes corrupt skb parsing; optional feature fields change layout; and deferred TSQ/timer flags must be drained in release callbacks.

## Test Signals
Run TCP selftests, packetdrill, MPTCP/SMC/TCP-AO/MD5 config builds, GSO/encapsulation header tests, Fast Open and SACK/RACK recovery tests, BPF sock_ops coverage, and cacheline/layout checks from networking documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tee_core.h -->
# sources/distributed-fs/ceph-client/include/linux/tee_core.h

## Purpose
declares the internal API that the generic TEE core provides to concrete TEE drivers, including device allocation/registration, driver operation vectors, shared-memory pools, protected-memory pools, DMA-heap registration, and context/shared-memory reference helpers.

## Important APIs, Types, and Functions
The file is 439 lines and exports these visible symbol families: types/enums `tee_dma_heap_id`, `tee_device`, `tee_driver_ops`, `tee_desc`, `tee_protmem_pool`, `tee_protmem_pool_ops`, `tee_shm_pool`, `tee_shm_pool_ops`, `tee_shm`, `tee_context`; macros/constants `TEE_SHM_DYNAMIC`, `TEE_SHM_USER_MAPPED`, `TEE_SHM_POOL`, `TEE_SHM_PRIV`, `TEE_SHM_DMA_BUF`, `TEE_SHM_DMA_MEM`, `TEE_DEVICE_FLAG_REGISTERED`, `TEE_MAX_DEV_NAME_LEN`, `TEE_REVISION_STR_SIZE`, `TEE_DESC_PRIVILEGED`; function-like macros none; inline helpers `tee_shm_pool_free`, `tee_shm_is_dynamic`, `tee_shm_get_id`, `tee_param_is_memref`; external prototypes `tee_device_alloc`, `tee_device_register`, `tee_device_unregister`, `tee_device_register_dma_heap`, `tee_device_put_all_dma_heaps`, `tee_device_get`, `tee_device_put`, `tee_device_set_dev_groups`, `tee_session_calc_client_uuid`, `tee_shm_pool_alloc_res_mem`, `tee_protmem_static_pool_alloc`, `tee_get_drvdata`, `tee_shm_alloc_priv_buf`, `tee_dyn_shm_alloc_helper`, and 7 more.

## Control Flow
A TEE driver fills `tee_desc` and `tee_driver_ops`, allocates a `tee_device`, optionally attaches sysfs groups and shared-memory pools, registers it, and serves open/session/invoke/cancel/supplicant and shared-memory callbacks through the core. Shared memory is allocated from pools, registered dynamically, referenced by ID, and released through refcount helpers.

## State and Persistence Behavior
`tee_device` owns the device/cdev, user count, completion used during unregister, IDR of user-visible shared memory, mutex, and pool pointer. `tee_shm` objects have flags, IDs, physical/kernel/user backing, secure-world IDs, and references. Protected-memory pools encapsulate implementation-owned state through ops.

## Dependencies and Integration Points
It depends on cdev/device/dma-buf/idr/kref/list/scatterlist/TEE UAPI/UUID APIs and integrates with OP-TEE or other TEE drivers, tee-supplicant, DMA heaps, reserved memory, and client-driver contexts. Direct includes are `linux/cdev.h`, `linux/device.h`, `linux/dma-buf.h`, `linux/idr.h`, `linux/kref.h`, `linux/list.h`, `linux/scatterlist.h`, `linux/tee.h`, `linux/tee_drv.h`, `linux/types.h`, `linux/uuid.h`.

## Risks and Edge Cases
Device unregister must block new users while existing contexts and shared memory drain. Dynamic shared-memory registration requires page lifetime, DMA visibility, secure-world unregister, and IDR cleanup to match. Protected-memory update hooks can expose wrong parent buffers or physical addresses.

## Test Signals
Run TEE core and OP-TEE tests for device register/unregister, concurrent opens, session open/invoke/cancel, supplicant absence, shared-memory alloc/register/free by ID, DMA-heap protected memory, and error unwinding under refcount debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tee_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tee_drv.h -->
# sources/distributed-fs/ceph-client/include/linux/tee_drv.h

## Purpose
declares the public kernel client-driver API for interacting with TEE devices and trusted applications.

## Important APIs, Types, and Functions
The file is 338 lines and exports these visible symbol families: types/enums `tee_device`, `tee_context`, `tee_shm`, `tee_param_memref`, `tee_param_ubuf`, `tee_param_objref`, `tee_param_value`, `tee_param`, `tee_client_device`, `tee_client_driver`; macros/constants none; function-like macros `to_tee_client_device`, `to_tee_client_driver`, `tee_client_driver_register`, `module_tee_client_driver`; inline helpers `tee_shm_get_size`, `tee_shm_get_page_offset`; external prototypes `tee_shm_alloc_kernel_buf`, `tee_shm_register_kernel_buf`, `tee_shm_register_fd`, `tee_shm_free`, `tee_shm_get_va`, `tee_shm_get_pa`, `tee_client_open_context`, `tee_client_close_context`, `tee_client_get_version`, `tee_client_open_session`, `tee_client_close_session`, `tee_client_system_session`, `tee_client_invoke_func`, `tee_client_cancel_req`, and 2 more.

## Control Flow
Kernel clients open a context with `tee_client_open_context()`, allocate or register shared memory, open a TA session, invoke functions with `tee_param` arrays, optionally cancel requests, close sessions, free memory, and close the context. TEE bus drivers bind through `tee_client_driver` and module helper macros.

## State and Persistence Behavior
`tee_context` tracks the selected device, driver-private data, refcount, release state, supplicant wait policy, and NULL memref capability. `tee_shm` tracks backing pages/addressing, object ID, secure-world ID, flags, and reference count. Parameters carry memrefs, user buffers, object refs, or value triples.

## Dependencies and Integration Points
It depends on the device model, kref, module device IDs, TEE UAPI definitions, and the TEE core's private types. It integrates with in-kernel OP-TEE consumers such as RPMB, firmware, trusted keys, and service devices. Direct includes are `linux/device.h`, `linux/kref.h`, `linux/list.h`, `linux/mod_devicetable.h`, `linux/tee.h`, `linux/types.h`.

## Risks and Edge Cases
Shared-memory offsets and sizes must be bounds-checked before passing to secure world. Context refcycles during release are explicitly called out; supplicant blocking policy matters for non-blocking kernel clients. Session return codes and Linux errno are separate channels.

## Test Signals
Exercise client open/match/close, kernel-buffer allocation and fd registration, VA/PA/page accessors with bounds failures, TA session lifecycle, cancellation, tee bus probe/remove/shutdown, and refcount leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tee_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tegra-icc.h -->
# sources/distributed-fs/ceph-client/include/linux/tegra-icc.h

## Purpose
defines NVIDIA Tegra interconnect client classes and BPMP memory-controller client IDs shared by Tegra interconnect and firmware-facing code.

## Important APIs, Types, and Functions
The file is 66 lines and exports these visible symbol families: types/enums `tegra_icc_client_type`; macros/constants `LINUX_TEGRA_ICC_H`, `TEGRA_ICC_BPMP_DEBUG`, `TEGRA_ICC_BPMP_CPU_CLUSTER0`, `TEGRA_ICC_BPMP_CPU_CLUSTER1`, `TEGRA_ICC_BPMP_CPU_CLUSTER2`, `TEGRA_ICC_BPMP_GPU`, `TEGRA_ICC_BPMP_CACTMON`, `TEGRA_ICC_BPMP_DISPLAY`, `TEGRA_ICC_BPMP_VI`, `TEGRA_ICC_BPMP_EQOS`, `TEGRA_ICC_BPMP_PCIE_0`, `TEGRA_ICC_BPMP_PCIE_1`, `TEGRA_ICC_BPMP_PCIE_2`, `TEGRA_ICC_BPMP_PCIE_3`, and 32 more; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Tegra drivers or device-tree-interpreting code select an ICC client type and BPMP client ID, then use the interconnect/BPMP path to request bandwidth or classify memory traffic for display, VI, audio, GPU, PCIe, DLA, XUSB, and other engines.

## State and Persistence Behavior
The header has no runtime state; the numeric IDs are stable firmware/protocol tokens.

## Dependencies and Integration Points
It is self-contained and integrates with Tegra BPMP firmware, memory controller clients, interconnect providers, and device-tree bandwidth consumers. Direct includes are none.

## Risks and Edge Cases
Renumbering or assigning the wrong BPMP client ID can throttle or over-provision the wrong hardware engine. ISO/non-ISO classification affects latency-sensitive display/camera/audio traffic.

## Test Signals
Compile Tegra configs and DTS users, compare IDs against BPMP ABI documentation, and validate bandwidth requests for display, VI, PCIe, XUSB, and GPU clients on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tegra-icc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tegra-mipi-cal.h -->
# sources/distributed-fs/ceph-client/include/linux/tegra-mipi-cal.h

## Purpose
declares the Tegra MIPI calibration provider/consumer API for CSI/DSI PHY calibration control.

## Important APIs, Types, and Functions
The file is 58 lines and exports these visible symbol families: types/enums `tegra_mipi_device`, `tegra_mipi_ops`; macros/constants `__TEGRA_MIPI_CAL_H_`; function-like macros none; inline helpers none; external prototypes `devm_tegra_mipi_add_provider`, `tegra_mipi_free`, `tegra_mipi_enable`, `tegra_mipi_disable`, `tegra_mipi_start_calibration`, `tegra_mipi_finish_calibration`.

## Control Flow
A calibration provider registers with `devm_tegra_mipi_add_provider()`. Consumers request a `tegra_mipi_device` by phandle/index, then enable, start calibration, finish calibration, disable, and free the handle through provider operations.

## State and Persistence Behavior
`tegra_mipi_device` carries provider ops, device pointer, MMIO register block, index, and opaque provider data. Calibration state lives in the provider hardware and driver data, not in this header.

## Dependencies and Integration Points
It depends on platform devices, OF nodes, MMIO pointers, and the provider-specific `tegra_mipi_ops`; it integrates with Tegra camera/display PHY drivers. Direct includes are none.

## Risks and Edge Cases
Consumers must pair request/free and enable/disable, and calibration sequencing must match the PHY lane state. Wrong index/regmap wiring can calibrate the wrong MIPI pad.

## Test Signals
Build Tegra CSI/DSI users, validate OF lookup failures, test enable/calibrate/disable order on hardware, and run suspend/resume with active consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tegra-mipi-cal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/termios_internal.h -->
# sources/distributed-fs/ceph-client/include/linux/termios_internal.h

## Purpose
declares internal termios conversion helpers and default control-character initialization used by tty compatibility and UAPI translation code.

## Important APIs, Types, and Functions
The file is 50 lines and exports these visible symbol families: types/enums none; macros/constants `INIT_C_CC_VDSUSP_EXTRA`, `INIT_C_CC`; function-like macros none; inline helpers none; external prototypes `user_termio_to_kernel_termios`, `kernel_termios_to_user_termio`, `user_termios_to_kernel_termios`, `kernel_termios_to_user_termios`, `user_termios_to_kernel_termios_1`, `kernel_termios_to_user_termios_1`.

## Control Flow
TTY ioctl paths convert user `termio`, `termios`, or `termios2` records into `ktermios`, apply driver changes, and copy back to user formats through the declared helpers. `INIT_C_CC` provides initial control characters with architecture-dependent `VDSUSP` support.

## State and Persistence Behavior
The header has no global state; converted `ktermios` records persist in tty state owned elsewhere.

## Dependencies and Integration Points
It depends on tty termios UAPI types, user-pointer access, and architecture definitions for optional control characters. Direct includes are `linux/uaccess.h`, `asm/termios.h`.

## Risks and Edge Cases
Compat conversion must preserve speed, flags, and control characters without leaking padding or truncating newer fields. Architecture differences around `VDSUSP` can change initialization.

## Test Signals
Run tty ioctl and compat tests across termio/termios/termios2, verify default control characters, and fuzz invalid user pointers and size-limited copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/termios_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/text-patching.h -->
# sources/distributed-fs/ceph-client/include/linux/text-patching.h

## Purpose
provides a generic fallback `text_poke_copy()` helper for architectures without specialized live text patching support.

## Important APIs, Types, and Functions
The file is 16 lines and exports these visible symbol families: types/enums none; macros/constants `text_poke_copy`; function-like macros none; inline helpers none; external prototypes `memcpy`.

## Control Flow
Callers copy replacement bytes into an executable text area through `text_poke_copy()`, which defaults to `memcpy()` unless an architecture overrides the macro.

## State and Persistence Behavior
No state is held here; patched instruction state is in executable kernel text and architecture instruction-cache/TLB machinery.

## Dependencies and Integration Points
It depends on string/memory primitives and integrates with jump labels, alternatives, probes, static calls, or other text-patching users where an architecture permits plain copying. Direct includes are `asm/text-patching.h`.

## Risks and Edge Cases
Plain memcpy is not sufficient on architectures requiring synchronization, W^X transitions, cache maintenance, or stop-machine coordination. Callers must rely on architecture overrides where needed.

## Test Signals
Compile architectures with and without overrides, run jump-label/static-call/kprobe alternatives tests, and validate instruction cache coherency after patching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/text-patching.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/textsearch.h -->
# sources/distributed-fs/ceph-client/include/linux/textsearch.h

## Purpose
declares the generic textsearch framework used by networking and other subsystems to prepare pattern-matching configurations and scan blocks of text or packet data.

## Important APIs, Types, and Functions
The file is 181 lines and exports these visible symbol families: types/enums `module`, `ts_config`, `ts_state`, `ts_ops`; macros/constants `TS_AUTOLOAD`, `TS_IGNORECASE`, `TS_PRIV_ALIGNTO`; function-like macros `TS_PRIV_ALIGN`; inline helpers `textsearch_next`, `textsearch_find`, `textsearch_get_pattern_len`; external prototypes `int`, `get_next_block`, `if`, `textsearch_next`, `textsearch_register`, `textsearch_unregister`, `textsearch_destroy`, `textsearch_find_continuous`, `ERR_PTR`.

## Control Flow
An algorithm registers `ts_ops`. Users call `textsearch_prepare()` with an algorithm name, pattern, length, flags, and gfp mask, then repeatedly call `textsearch_find()` or continuous search helpers. `textsearch_next()` abstracts block-by-block data access through callbacks.

## State and Persistence Behavior
`ts_config` holds algorithm ops, flags, pattern length, algorithm-private data, and module owner. `ts_state` tracks block offset, consumed offset, finish flag, and caller-provided storage across searches.

## Dependencies and Integration Points
It depends on module refcounts, skbuff-style block access patterns, and alignment helpers; it integrates with netfilter/string matching and any caller needing pluggable string search. Direct includes are `linux/types.h`, `linux/list.h`, `linux/kernel.h`, `linux/err.h`, `linux/slab.h`.

## Risks and Edge Cases
Search state must be initialized and preserved correctly across fragmented buffers. Algorithm modules must remain referenced while configs live; ignore-case and pattern length handling can diverge by algorithm.

## Test Signals
Register/unregister algorithms, scan contiguous and fragmented buffers, test ignore-case/autoload paths, run netfilter string-match tests, and check module unload while configs are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/textsearch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/textsearch_fsm.h -->
# sources/distributed-fs/ceph-client/include/linux/textsearch_fsm.h

## Purpose
defines token types, recursion limits, and token layout for the finite-state-machine textsearch algorithm.

## Important APIs, Types, and Functions
The file is 50 lines and exports these visible symbol families: types/enums `ts_fsm_token`; macros/constants `TS_FSM_TYPE_MAX`, `TS_FSM_RECUR_MAX`; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
FSM parser/compiler code builds `ts_fsm_token` arrays with value, type, repetition, recursion, and next-token offset. Runtime matching interprets these tokens to consume literal values, wildcard classes, alternation, and control tokens.

## State and Persistence Behavior
Compiled token arrays are algorithm-private configuration state owned by textsearch configs.

## Dependencies and Integration Points
It depends only on kernel types and is consumed by the FSM textsearch implementation. Direct includes are `linux/types.h`.

## Risks and Edge Cases
Token recursion and repetition limits protect against unbounded matching. Bad `next` offsets or type values can make the matcher skip tokens or overrun compiled patterns.

## Test Signals
Compile valid and invalid FSM patterns, cover recursion/repetition boundaries, fuzz token streams, and compare matches against expected pattern-language behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/textsearch_fsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/thermal.h -->
# sources/distributed-fs/ceph-client/include/linux/thermal.h

## Purpose
declares the kernel thermal framework API: thermal trips, zone operations, cooling-device operations, registration helpers, notification events, OF registration, and disabled-config stubs.

## Important APIs, Types, and Functions
The file is 362 lines and exports these visible symbol families: types/enums `thermal_zone_device`, `thermal_cooling_device`, `thermal_instance`, `thermal_debugfs`, `thermal_attr`, `thermal_trend`, `thermal_notify_event`, `thermal_trip`, `cooling_spec`, `thermal_zone_device_ops`, `thermal_cooling_device_ops`, `thermal_zone_params`, `device`; macros/constants `__THERMAL_H__`, `THERMAL_CSTATE_INVALID`, `THERMAL_NO_LIMIT`, `THERMAL_WEIGHT_DEFAULT`, `THERMAL_TEMP_INVALID`, `THERMAL_TRIP_FLAG_RW_TEMP`, `THERMAL_TRIP_FLAG_RW_HYST`, `THERMAL_TRIP_FLAG_RW`; function-like macros `THERMAL_TRIP_PRIV_TO_INT`, `THERMAL_INT_TO_TRIP_PRIV`; inline helpers `devm_thermal_of_zone_unregister`, `thermal_zone_device_unregister`, `thermal_zone_device_update`, `thermal_cooling_device_register`, `thermal_of_cooling_device_register`, `devm_thermal_of_cooling_device_register`, `thermal_cooling_device_unregister`, `thermal_zone_get_temp`, `thermal_zone_get_slope`, `thermal_zone_get_offset`, `thermal_zone_device_id`, `thermal_zone_device_enable`, `thermal_zone_device_disable`, `thermal_pm_prepare`, and 1 more; external prototypes `devm_thermal_of_zone_unregister`, `ERR_PTR`, `for_each_thermal_trip`, `thermal_zone_for_each_trip`, `thermal_zone_set_trip_temp`, `thermal_zone_get_crit_temp`, `thermal_zone_device_unregister`, `thermal_zone_device_id`, `thermal_zone_device_update`, `thermal_of_cooling_device_register`, `devm_thermal_of_cooling_device_register`, `thermal_cooling_device_update`, `thermal_cooling_device_unregister`, `thermal_zone_get_temp`, and 8 more.

## Control Flow
Drivers register zones with trips and `thermal_zone_device_ops`, register cooling devices with `thermal_cooling_device_ops`, and the framework polls or updates temperatures, evaluates trips, binds cooling instances, calls governors, notifies events, and exposes sysfs/hwmon interfaces. OF helpers bind device-tree-described sensors and cooling devices.

## State and Persistence Behavior
Thermal zones and cooling devices are device-model objects with IDs, type strings, ops, private data, trip tables, cooling instances, locks, stats, and optional debugfs state. Trip values and hysteresis may be writable when flags allow it.

## Dependencies and Integration Points
It depends on devices, OF, mutex/list/sysfs/workqueue, UAPI thermal types, and optional CONFIG_THERMAL/CONFIG_THERMAL_OF/CONFIG_THERMAL_DEBUGFS code. Direct includes are `linux/of.h`, `linux/idr.h`, `linux/device.h`, `linux/sysfs.h`, `linux/workqueue.h`, `uapi/linux/thermal.h`.

## Risks and Edge Cases
Bad trip temperatures, hysteresis, or cooling-state bounds can overheat hardware or throttle too aggressively. Disabled-config stubs return ERR_PTR/-ENODEV and must be handled by drivers. Power allocator parameters require coherent units.

## Test Signals
Run thermal selftests, OF probe tests, sysfs trip read/write checks, cooling-device bind/unbind and state transitions, suspend/resume notifications, emulated temperature tests, and CONFIG_THERMAL=n builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/thread_info.h -->
# sources/distributed-fs/ceph-client/include/linux/thread_info.h

## Purpose
provides common low-level accessors for `thread_info` flags, syscall-work bits, restart-block setup, stack-frame checks, and architecture task-structure hooks.

## Important APIs, Types, and Functions
The file is 239 lines and exports these visible symbol families: types/enums `syscall_work_bit`; macros/constants `SYSCALL_WORK_SECCOMP`, `SYSCALL_WORK_SYSCALL_TRACEPOINT`, `SYSCALL_WORK_SYSCALL_TRACE`, `SYSCALL_WORK_SYSCALL_EMU`, `SYSCALL_WORK_SYSCALL_AUDIT`, `SYSCALL_WORK_SYSCALL_USER_DISPATCH`, `SYSCALL_WORK_SYSCALL_EXIT_TRAP`, `SYSCALL_WORK_SYSCALL_RSEQ_SLICE`, `TIF_NEED_RESCHED_LAZY`, `_TIF_NEED_RESCHED_LAZY`, `TIF_RSEQ`, `_TIF_RSEQ`, `THREAD_ALIGN`, `THREADINFO_GFP`; function-like macros `current_thread_info`, `arch_set_restart_data`, `set_thread_flag`, `clear_thread_flag`, `update_thread_flag`, `test_and_set_thread_flag`, `test_and_clear_thread_flag`, `test_thread_flag`, `read_thread_flags`, `read_task_thread_flags`, `set_syscall_work`, `test_syscall_work`, `clear_syscall_work`, `set_task_syscall_work`, and 2 more; inline helpers `set_restart_fn`, `set_ti_thread_flag`, `clear_ti_thread_flag`, `update_ti_thread_flag`, `test_and_set_ti_thread_flag`, `test_and_clear_ti_thread_flag`, `test_ti_thread_flag`, `arch_within_stack_frames`, `arch_setup_new_exec`; external prototypes `set_ti_thread_flag`, `clear_ti_thread_flag`, `test_and_set_bit`, `test_and_clear_bit`, `test_bit`, `READ_ONCE`, `arch_test_bit`, `tif_test_bit`, `arch_task_cache_init`, `arch_release_task_struct`, `arch_dup_task_struct`.

## Control Flow
Entry, scheduler, signal, seccomp, audit, tracing, rseq, and preemption code set/test/clear TIF or syscall-work bits through inline wrappers. `tif_need_resched()` is optimized for noinstr paths, and restartable syscalls use `set_restart_fn()`.

## State and Persistence Behavior
State is stored in per-task `thread_info` flags and optional syscall_work fields. CONFIG_THREAD_INFO_IN_TASK maps current_thread_info() onto `current`.

## Dependencies and Integration Points
It depends on arch `asm/thread_info.h`, current task definitions, bitops, restart blocks, and generic-entry configuration. Direct includes are `linux/types.h`, `linux/limits.h`, `linux/bug.h`, `linux/restart_block.h`, `linux/errno.h`, `asm/current.h`, `linux/bitops.h`, `asm/thread_info.h`.

## Risks and Edge Cases
Flag numbering and arch definitions must match entry assembly. Instrumentation in noinstr paths, non-atomic flag use in the wrong context, or mismatched lazy preemption flags can break scheduling and syscall exit handling.

## Test Signals
Build multiple architectures and CONFIG_GENERIC_ENTRY variants, run seccomp/audit/ptrace/rseq tests, exercise preemption/resched flags, and enable objtool/noinstr validation where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/threads.h -->
# sources/distributed-fs/ceph-client/include/linux/threads.h

## Purpose
defines global CPU/thread/PID sizing constants such as `NR_CPUS`, PID maximum defaults, root thread reserve, and per-CPU PID heuristics.

## Important APIs, Types, and Functions
The file is 47 lines and exports these visible symbol families: types/enums none; macros/constants `CONFIG_NR_CPUS`, `NR_CPUS`, `MIN_THREADS_LEFT_FOR_ROOT`, `PID_MAX_DEFAULT`, `PID_MAX_LIMIT`, `PIDS_PER_CPU_DEFAULT`, `PIDS_PER_CPU_MIN`; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Core PID and scheduler setup code uses these constants to size static CPU masks, choose default `/proc/sys/kernel/pid_max`, and derive thread limits.

## State and Persistence Behavior
No runtime state is stored here; constants influence compile-time sizing and boot-time tunables.

## Dependencies and Integration Points
It depends on configuration options such as CONFIG_NR_CPUS and CONFIG_BASE_SMALL plus PAGE_SIZE and long width from surrounding headers. Direct includes are none.

## Risks and Edge Cases
Using `NR_CPUS` for large static allocations wastes memory; code should prefer dynamic cpumasks when possible. PID limit values are ABI-visible through proc/sysctl behavior.

## Test Signals
Build small and large NR_CPUS configurations, validate pid_max defaults on 32-bit and 64-bit builds, and run fork/thread-limit stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/threads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/thunderbolt.h -->
# sources/distributed-fs/ceph-client/include/linux/thunderbolt.h

## Purpose
declares the Thunderbolt/USB4 service API, domain and XDomain structures, property-directory helpers, service-driver binding, NHI/ring DMA structures, and ring enqueue/poll interfaces.

## Important APIs, Types, and Functions
The file is 699 lines and exports these visible symbol families: types/enums `fwnode_handle`, `device`, `tb_cfg_pkg_type`, `tb_security_level`, `tb`, `tb_property_dir`, `tb_property_type`, `tb_property`, `tb_link_width`, `tb_xdomain`, `tb_protocol_handler`, `tb_service`, `tb_service_driver`, `tb_nhi`, and 3 more; macros/constants `THUNDERBOLT_H_`, `TB_LINKS_PER_PHY_PORT`, `TB_PROPERTY_KEY_SIZE`, `RING_FLAG_NO_SUSPEND`, `RING_FLAG_FRAME`, `RING_FLAG_E2E`, `TB_FRAME_SIZE`; function-like macros `tb_property_for_each`, `TB_SERVICE`; inline helpers `tb_phy_port_from_link`, `tb_xdomain_disable_all_paths`, `tb_xdomain_find_by_uuid_locked`, `tb_xdomain_find_by_route_locked`, `tb_xdomain_put`, `tb_is_xdomain`, `tb_service_put`, `tb_is_service`, `tb_service_set_drvdata`, `tb_ring_rx`, `tb_ring_tx`, `usb4_usb3_port_match`; external prototypes `tb_property_format_dir`, `tb_property_free_dir`, `tb_property_add_immediate`, `tb_property_add_data`, `tb_property_add_text`, `tb_property_add_dir`, `tb_property_remove`, `tb_register_property_dir`, `tb_unregister_property_dir`, `tb_xdomain_lane_bonding_enable`, `tb_xdomain_lane_bonding_disable`, `tb_xdomain_alloc_in_hopid`, `tb_xdomain_release_in_hopid`, `tb_xdomain_alloc_out_hopid`, and 22 more.

## Control Flow
A Thunderbolt domain owns a root switch, control channel, workqueue, security level, and connection-manager ops. XDomain discovery exchanges property blocks, allocates hop IDs, enables paths, and creates service devices. Service drivers match with `TB_SERVICE`. NHI ring users allocate TX/RX rings, start them, enqueue `ring_frame` DMA buffers, receive callbacks or poll completions, then stop/free rings.

## State and Persistence Behavior
`tb`, `tb_xdomain`, `tb_service`, `tb_nhi`, and `tb_ring` carry substantial runtime state: devices, locks, work items, property generations, ID allocators, path/ring queues, DMA descriptors, interrupt vectors, link width/speed, unplug state, and debugfs pointers.

## Dependencies and Integration Points
It depends on the device model, IDA/IDR, list/mutex/workqueue, PCI, UUID, module device tables, DMA mapping, and CONFIG_USB4. The only always-available helper is USB4/USB3 port matching, stubbed to false without USB4. Direct includes are `linux/types.h`, `linux/device.h`, `linux/idr.h`, `linux/list.h`, `linux/mutex.h`, `linux/mod_devicetable.h`, `linux/pci.h`, `linux/uuid.h`, `linux/workqueue.h`.

## Risks and Edge Cases
External hotplug, DMA rings, and security levels make lifetime and authorization critical. Service properties can change asynchronously, ring buffers require correct DMA mapping and stop cancellation, and lock ordering between NHI and ring locks is documented in the structs.

## Test Signals
Build CONFIG_USB4 on/off, run Thunderbolt/USB4 hotplug and authorization tests, validate XDomain property parsing/formatting, service driver probe/remove, lane bonding and path allocation, ring TX/RX cancellation, polling, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/thunderbolt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ti-emif-sram.h -->
# sources/distributed-fs/ceph-client/include/linux/ti-emif-sram.h

## Purpose
defines TI AM33xx EMIF register save/restore layouts and SRAM-resident power-management function table interfaces.

## Important APIs, Types, and Functions
The file is 140 lines and exports these visible symbol families: types/enums `emif_regs_amx3`, `ti_emif_pm_data`, `ti_emif_pm_functions`, `gen_pool`; macros/constants none; function-like macros none; inline helpers `ti_emif_asm_offsets`; external prototypes `offsetof`, `BLANK`, `DEFINE`, `ti_emif_copy_pm_function_table`, `ti_emif_get_mem_type`.

## Control Flow
Platform PM code copies low-level EMIF routines into SRAM with `ti_emif_copy_pm_function_table()`, uses generated offsets for assembly, saves EMIF register context, enters/exits self-refresh, and restores DDR configuration around low-power states.

## State and Persistence Behavior
`emif_regs_amx3` stores captured controller/PHY register values; `ti_emif_pm_data` stores virtual/physical controller and context addresses; `ti_emif_pm_functions` stores SRAM function offsets. These records persist across suspend transitions.

## Dependencies and Integration Points
It depends on kbuild offset generation, packed/aligned layout, gen_pool SRAM allocation, IO memory, and TI SoC EMIF hardware. Direct includes are `linux/kbuild.h`, `linux/types.h`.

## Risks and Edge Cases
Assembly offsets, packing, and alignment must remain exact. Wrong physical addresses or SRAM function offsets can corrupt DDR during suspend/resume and hang the system.

## Test Signals
Run offset-generation builds, compare struct offsets with assembly users, suspend/resume AM33xx hardware repeatedly, and validate memory type detection for supported DDR variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ti-emif-sram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ti_wilink_st.h -->
# sources/distributed-fs/ceph-client/include/linux/ti_wilink_st.h

## Purpose
declares the Texas Instruments WiLink shared-transport core API and internal data structures for multiplexing Bluetooth, FM, and GPS protocols over a shared UART/TTY link.

## Important APIs, Types, and Functions
The file is 440 lines and exports these visible symbol families: types/enums `proto_type`, `st_proto_s`, `st_data_s`, `chip_version`, `kim_data_s`, `bts_header`, `bts_action`, `bts_action_send`, `bts_action_wait`, `bts_action_delay`, `bts_action_serial`, `hci_command`, `fm_event_hdr`, `gps_event_hdr`, and 1 more; macros/constants `TI_WILINK_ST_H`, `ST_NOTEMPTY`, `ST_EMPTY`, `ST_INITIALIZING`, `ST_REG_IN_PROGRESS`, `ST_REG_PENDING`, `ST_WAITING_FOR_RESP`, `ST_TX_SENDING`, `ST_TX_WAKEUP`, `GPS_STUB_TEST`, `LDISC_TIME`, `CMD_RESP_TIME`, `CMD_WR_TIME`, `GPIO_HIGH`, and 24 more; function-like macros `MAKEWORD`; inline helpers none; external prototypes `char`, `st_register`, `st_unregister`, `st_get_uart_wr_room`, `st_int_write`, `st_write`, `st_ll_send_frame`, `st_tx_wakeup`, `st_core_init`, `st_core_exit`, `st_kim_ref`, `gps_chrdrv_stub_write`, `gps_chrdrv_stub_init`, `st_kim_start`, and 11 more.

## Control Flow
Protocol drivers register `st_proto_s` records with channel IDs and callbacks. KIM coordinates line-discipline installation, firmware script parsing, chip enable/disable, and protocol registration. ST core receives UART frames, reconstructs protocol skbs by channel/header length, queues TX skbs, and low-level PM code moves the chip between asleep/awake states.

## State and Persistence Behavior
`st_data_s` holds protocol tables, registered flags, RX/TX state machines, queues, lock, TTY pointer, PM state, and KIM backpointer. `kim_data_s` tracks completions, firmware entry, response buffer, UART settings, chip version, and line-discipline state. BTS action structs model firmware script records.

## Dependencies and Integration Points
It depends on skbuffs, tty/platform/firmware/completion/workqueue types supplied by implementation files, and integrates with TI BT/FM/GPS protocol drivers and board platform data. Direct includes are `linux/skbuff.h`.

## Risks and Edge Cases
UART framing and PM handshakes are race-prone. Length-field offsets, channel IDs, tx wakeups, firmware waits, and sleep/wake ACK ordering must match chip firmware. Platform GPIO and baud/flow-control callbacks are board-specific.

## Test Signals
Register/unregister each protocol, parse BTS firmware actions, simulate partial UART frames, stress TX queue wakeups, test sleep/wake LL state transitions, and validate firmware download plus BT/FM/GPS traffic on WiLink hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ti_wilink_st.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tick.h -->
# sources/distributed-fs/ceph-client/include/linux/tick.h

## Purpose
declares tick, broadcast tick, NO_HZ idle/full, CPU hotplug, suspend, and tick-dependency APIs used by timekeeping, scheduler, RCU, and clockevent code.

## Important APIs, Types, and Functions
The file is 317 lines and exports these visible symbol families: types/enums `tick_broadcast_mode`, `tick_broadcast_state`, `tick_dep_bits`; macros/constants `tick_cpu_dying`, `TICK_DEP_BIT_MAX`, `TICK_DEP_MASK_NONE`, `TICK_DEP_MASK_POSIX_TIMER`, `TICK_DEP_MASK_PERF_EVENTS`, `TICK_DEP_MASK_SCHED`, `TICK_DEP_MASK_CLOCK_UNSTABLE`, `TICK_DEP_MASK_RCU`, `TICK_DEP_MASK_RCU_EXP`, `tick_nohz_enabled`; function-like macros `arch_needs_cpu`, `tick_nohz_full_cpu`; inline helpers `tick_init`, `tick_suspend_local`, `tick_resume_local`, `tick_assert_timekeeping_handover`, `tick_freeze`, `tick_unfreeze`, `tick_irq_enter`, `hotplug_cpu__broadcast_tick_pull`, `tick_broadcast_control`, `tick_broadcast_oneshot_control`, `tick_broadcast_enable`, `tick_broadcast_disable`, `tick_broadcast_force`, `tick_broadcast_enter`, and 33 more; external prototypes `tick_init`, `tick_suspend_local`, `tick_resume_local`, `tick_cpu_dying`, `tick_assert_timekeeping_handover`, `tick_freeze`, `tick_unfreeze`, `tick_irq_enter`, `hotplug_cpu__broadcast_tick_pull`, `tick_broadcast_control`, `tick_broadcast_oneshot_control`, `tick_nohz_is_active`, `tick_nohz_tick_stopped`, `tick_nohz_tick_stopped_cpu`, and 26 more.

## Control Flow
Clockevent setup calls tick init/suspend/resume and CPU dying hooks. Idle and IRQ entry/exit paths stop or restart periodic ticks in NO_HZ idle. Full dynticks code tracks dependency bits for POSIX timers, perf, scheduler, unstable clocks, RCU, and expedited RCU; setting a dependency restarts/kicks ticks as needed.

## State and Persistence Behavior
Runtime state includes global NO_HZ enable/full masks, per-CPU stopped-tick state, broadcast mode/state, static keys, and dependency masks attached to CPUs, tasks, and signals. Disabled configs compile to stubs.

## Dependencies and Integration Points
It depends on clockchips, irq flags, percpu data, context tracking, cpumasks, scheduler state, RCU, and static keys. Direct includes are `linux/clockchips.h`, `linux/irqflags.h`, `linux/percpu.h`, `linux/context_tracking_state.h`, `linux/cpumask.h`, `linux/sched.h`, `linux/rcupdate.h`, `linux/static_key.h`.

## Risks and Edge Cases
Stopping ticks while dependencies exist can break timers, scheduler accounting, perf, or RCU quiescent-state detection. CPU hotplug and suspend handoff ordering are especially sensitive.

## Test Signals
Run NO_HZ idle/full kernel selftests, CPU hotplug loops, suspend/resume, RCU stall tests, perf/POSIX timer activity on isolated CPUs, and builds for generic clockevents on/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tick.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tifm.h -->
# sources/distributed-fs/ceph-client/include/linux/tifm.h

## Purpose
declares the Texas Instruments FlashMedia adapter bus API, socket/device structures, register bits, DMA/FIFO constants, and MemoryStick/xD/SD socket helpers.

## Important APIs, Types, and Functions
The file is 161 lines and exports these visible symbol families: types/enums `tifm_device_id`, `tifm_driver`, `tifm_dev`, `tifm_adapter`; macros/constants `TIFM_CTRL_LED`, `TIFM_CTRL_FAST_CLK`, `TIFM_CTRL_POWER_MASK`, `TIFM_SOCK_STATE_OCCUPIED`, `TIFM_SOCK_STATE_POWERED`, `TIFM_FIFO_ENABLE`, `TIFM_FIFO_READY`, `TIFM_FIFO_MORE`, `TIFM_FIFO_INT_SETALL`, `TIFM_FIFO_INTMASK`, `TIFM_DMA_RESET`, `TIFM_DMA_TX`, `TIFM_DMA_EN`, `TIFM_DMA_TSIZE`, and 3 more; function-like macros none; inline helpers `tifm_set_drvdata`; external prototypes `void`, `tifm_add_adapter`, `tifm_remove_adapter`, `tifm_free_adapter`, `tifm_free_device`, `tifm_register_driver`, `tifm_unregister_driver`, `tifm_eject`, `tifm_has_ms_pif`, `tifm_map_sg`, `tifm_unmap_sg`, `tifm_queue_work`, `dev_get_drvdata`.

## Control Flow
Host drivers allocate and add a `tifm_adapter`, allocate per-socket `tifm_dev` children, and card-function drivers bind through `tifm_driver` match tables. Data paths use FIFO/DMA register bits and map/unmap scatterlists for socket transfers.

## State and Persistence Behavior
`tifm_adapter` owns sockets, resources, clock, IRQ, eject work, and lock; `tifm_dev` tracks socket address, type, media ID, IRQ status, resources, and callback hooks.

## Dependencies and Integration Points
It depends on device model, PCI, workqueue, clocks, spinlocks, resources, and scatterlists; it integrates with flash-media card drivers. Direct includes are `linux/spinlock.h`, `linux/interrupt.h`, `linux/delay.h`, `linux/pci.h`, `linux/workqueue.h`.

## Risks and Edge Cases
Socket hotplug/eject races, DMA mapping lifetime, and FIFO interrupt masks can lose media events or corrupt transfers. Resource arrays are fixed per socket.

## Test Signals
Probe/remove adapters, hotplug/eject media, run scatter-gather DMA and FIFO transfer tests, validate driver match tables for XD/MS/SD types, and exercise suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tifm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timb_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/timb_dma.h

## Purpose
defines platform data for the Timberdale DMA controller channels.

## Important APIs, Types, and Functions
The file is 44 lines and exports these visible symbol families: types/enums `timb_dma_platform_data_channel`, `timb_dma_platform_data`; macros/constants none; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Board/platform code supplies channel names, DMA request lines, and byte-order flags through `timb_dma_platform_data`; the DMA driver consumes that table at probe to register channels.

## State and Persistence Behavior
The header stores no state; platform-data instances persist in board/device setup.

## Dependencies and Integration Points
It depends on DMA engine direction definitions and platform-device wiring in Timberdale MFD users. Direct includes are none.

## Risks and Edge Cases
Wrong request-line or byte-order data can route DMA to the wrong peripheral or swap data unexpectedly.

## Test Signals
Build Timberdale platform users, probe DMA channels, and run memory-to-device/device-to-memory transfers for each platform-data entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timb_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timb_gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/timb_gpio.h

## Purpose
defines platform data for the Timberdale GPIO block.

## Important APIs, Types, and Functions
The file is 26 lines and exports these visible symbol families: types/enums `timbgpio_platform_data`; macros/constants none; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Platform code provides GPIO count, base, and IRQ base information through `timbgpio_platform_data`; the GPIO driver consumes it during probe.

## State and Persistence Behavior
No runtime state is declared here; the values become driver initialization data.

## Dependencies and Integration Points
It integrates with the GPIO subsystem and Timberdale MFD/platform-device registration. Direct includes are none.

## Risks and Edge Cases
Incorrect base or IRQ numbering can collide with other GPIO controllers or misroute interrupts.

## Test Signals
Build/probe Timberdale GPIO, request lines, toggle GPIOs, and verify IRQ mapping for interrupt-capable pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timb_gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time.h -->
# sources/distributed-fs/ceph-client/include/linux/time.h

## Purpose
declares common kernel time conversion and userspace copy helpers for `timespec64`, `itimerspec64`, `tm`, utimes, itimer clearing, and 32-bit wrap-safe comparisons.

## Important APIs, Types, and Functions
The file is 103 lines and exports these visible symbol families: types/enums `tm`; macros/constants none; function-like macros `time_after32`, `time_before32`, `time_between32`; inline helpers `clear_itimer`, `itimerspec64_valid`; external prototypes `get_timespec64`, `put_timespec64`, `get_itimerspec64`, `put_itimerspec64`, `mktime64`, `clear_itimer`, `do_utimes`, `time64_to_tm`.

## Control Flow
Syscall paths copy timespec/itimerspec values to and from userspace, validate interval timers, convert seconds to calendar `tm`, and compare 32-bit time values with wrap-aware macros.

## State and Persistence Behavior
`sys_tz` is the exposed global timezone record; other state lives in syscall/timekeeping implementations.

## Dependencies and Integration Points
It depends on time64 structures, user access annotations, timer configuration, and syscall implementations. Direct includes are `linux/cache.h`, `linux/math64.h`, `linux/time64.h`, `linux/time32.h`, `vdso/time.h`.

## Risks and Edge Cases
User copy validation, nanosecond range checks, and 32-bit wrap comparisons are easy to misuse. `itimerspec64_valid()` rejects invalid intervals and values before timers are armed.

## Test Signals
Run time syscall selftests, invalid timespec fuzzing, utimes coverage, itimer validation, and wrap-around tests for `time_after32`/`time_before32`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time32.h -->
# sources/distributed-fs/ceph-client/include/linux/time32.h

## Purpose
defines legacy 32-bit time structures and conversion helpers for old syscalls and compat paths.

## Important APIs, Types, and Functions
The file is 73 lines and exports these visible symbol families: types/enums `old_itimerspec32`, `old_utimbuf32`, `old_timex32`, `__kernel_timex`; macros/constants none; function-like macros none; inline helpers none; external prototypes `get_old_timespec32`, `put_old_timespec32`, `get_old_itimerspec32`, `put_old_itimerspec32`, `get_old_timex32`, `put_old_timex32`, `ns_to_kernel_old_timeval`.

## Control Flow
Compat syscall code copies old timespec/itimerspec/timex structures from userspace into 64-bit internal forms, performs operations, then copies converted values back.

## State and Persistence Behavior
No state is held here; it is a translation ABI for legacy userspace layouts.

## Dependencies and Integration Points
It depends on old UAPI time structures, `timespec64`, `itimerspec64`, and timex conversion code. Direct includes are `linux/time64.h`, `linux/timex.h`, `vdso/time32.h`.

## Risks and Edge Cases
Y2038 truncation and signed range handling are the core risks. Padding and timeval/timex field differences must not leak or corrupt data.

## Test Signals
Run compat time syscall tests on 32-bit and 64-bit compat kernels, cover boundary dates near 2038, invalid nsec values, and old adjtimex conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time64.h -->
# sources/distributed-fs/ceph-client/include/linux/time64.h

## Purpose
defines the kernel's 64-bit time scalar/types and inline arithmetic/validation helpers for `timespec64` and `itimerspec64`.

## Important APIs, Types, and Functions
The file is 177 lines and exports these visible symbol families: types/enums `timespec64`, `itimerspec64`, `time64_t`, `timeu64_t`; macros/constants `PSEC_PER_NSEC`, `TIME64_MAX`, `TIME64_MIN`, `KTIME_MAX`, `KTIME_MIN`, `KTIME_SEC_MAX`, `KTIME_SEC_MIN`, `TIME_UPTIME_SEC_MAX`, `TIME_SETTOD_SEC_MAX`; function-like macros none; inline helpers `timespec64_equal`, `timespec64_is_epoch`, `timespec64_compare`, `timespec64_add`, `timespec64_sub`, `timespec64_valid`, `timespec64_valid_strict`, `timespec64_valid_settod`, `timespec64_to_ns`; external prototypes `set_normalized_timespec64`, `ns_to_timespec64`, `timespec64_add_safe`.

## Control Flow
Callers compare, normalize, add, subtract, validate, and convert 64-bit timespecs to/from nanoseconds. Safe add helpers and settimeofday limits protect against overflow and unrealistic wall-clock setting.

## State and Persistence Behavior
No state is stored; the helpers operate on caller-owned time values.

## Dependencies and Integration Points
It depends on kernel time unit constants and 64-bit integer types and is foundational for timekeeping, timers, filesystems, and syscalls. Direct includes are `linux/math64.h`, `vdso/time64.h`, `uapi/linux/time.h`.

## Risks and Edge Cases
Overflow is the key risk: `timespec64_to_ns()` saturates beyond safe ktime limits, and wall-time validation uses stricter settimeofday bounds. Negative nsec or nsec >= NSEC_PER_SEC must be rejected.

## Test Signals
Unit-test normalization, add/subtract, ns conversion saturation, epoch detection, strict and settod validation, and Y2038/ktime boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time_namespace.h -->
# sources/distributed-fs/ceph-client/include/linux/time_namespace.h

## Purpose
declares time namespace structures and helpers that virtualize monotonic and boottime offsets for containers.

## Important APIs, Types, and Functions
The file is 178 lines and exports these visible symbol families: types/enums `user_namespace`, `seq_file`, `vm_area_struct`, `timens_offsets`, `time_namespace`, `proc_timens_offset`, `page`; macros/constants none; function-like macros none; inline helpers `put_time_ns`, `timens_add_monotonic`, `timens_add_boottime`, `timens_add_boottime_ns`, `timens_sub_boottime`, `timens_ktime_to_host`, `time_ns_init`, `timens_on_fork`, `timens_commit`; external prototypes `container_of`, `time_ns_init`, `free_time_ns`, `timens_on_fork`, `proc_timens_show_offsets`, `proc_timens_set_offset`, `do_timens_ktime_to_host`, `ERR_PTR`, `timens_commit`.

## Control Flow
Namespace creation copies or shares a `time_namespace`, fork hooks attach it, procfs shows/sets offsets before commit, and helpers add/subtract namespace offsets for monotonic/boottime values or convert namespace ktime back to host time.

## State and Persistence Behavior
`time_namespace` stores refcounted namespace identity, user namespace, frozen offsets, VVAR page pointer, and per-clock offsets. A task commits a namespace when offsets become active. Disabled configs use init namespace stubs.

## Dependencies and Integration Points
It depends on nsproxy, user namespaces, procfs seq/file interfaces, VMA/VVAR support, ktime, and CONFIG_TIME_NS. Direct includes are `linux/sched.h`, `linux/nsproxy.h`, `linux/ns_common.h`, `linux/err.h`, `linux/time64.h`, `linux/cleanup.h`.

## Risks and Edge Cases
Offsets must be immutable after namespace activation, and conversions must only apply to supported clocks. VVAR page handling and user namespace ownership affect container isolation.

## Test Signals
Run time namespace selftests, unshare/setns/fork offset tests, proc offset write permission tests, VDSO/VVAR time reads, and CONFIG_TIME_NS=n builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time_namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timecounter.h -->
# sources/distributed-fs/ceph-client/include/linux/timecounter.h

## Purpose
declares cyclecounter/timecounter helpers for converting hardware cycles into monotonic nanoseconds.

## Important APIs, Types, and Functions
The file is 165 lines and exports these visible symbol families: types/enums `cyclecounter`, `timecounter`; macros/constants none; function-like macros `CYCLECOUNTER_MASK`; inline helpers `cyclecounter_cyc2ns`, `timecounter_adjtime`, `cc_cyc2ns_backwards`, `timecounter_cyc2time`; external prototypes `register`, `timecounter_read`.

## Control Flow
A driver provides a `cyclecounter` with read/mask/mult/shift/max_idle_ns. `timecounter_init()` seeds state, `timecounter_read()` accumulates cycle deltas, and inline conversion helpers translate forward and backward cycle timestamps.

## State and Persistence Behavior
`timecounter` stores the cyclecounter pointer, current nanoseconds, last cycle value, fractional remainder, and mask. Driver code owns serialization around reads and adjustments.

## Dependencies and Integration Points
It depends on fixed-width types and integrates with PTP hardware clocks, network timestamping, media devices, and other cycle-based clocks. Direct includes are `linux/types.h`.

## Risks and Edge Cases
Cycle wrap, wrong mask/mult/shift, and reading less often than max idle time cause time jumps. `timecounter_adjtime()` changes accumulated time and must be synchronized with readers.

## Test Signals
Unit-test cycle wrap conversion, mult/shift scaling, backward timestamp conversion, adjtime, and compare hardware timestamp streams against PHC/PTP reference behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timecounter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timekeeper_internal.h -->
# sources/distributed-fs/ceph-client/include/linux/timekeeper_internal.h

## Purpose
defines internal timekeeper state: clocksource read bases, sequence counters, NTP/error accumulation, offsets, leap-second state, shadow copies, and VDSO update hooks.

## Important APIs, Types, and Functions
The file is 215 lines and exports these visible symbol families: types/enums `timekeeper_ids`, `tk_read_base`, `timekeeper`; macros/constants none; function-like macros none; inline helpers `update_vsyscall`, `update_vsyscall_tz`, `vdso_time_update_aux`; external prototypes `update_vsyscall`, `update_vsyscall_tz`, `vdso_time_update_aux`.

## Control Flow
Timekeeping core updates `tk_read_base` instances from the active clocksource, advances `timekeeper` raw/monotonic/real/boot/TAI offsets, mirrors values for fast/VDSO readers, and calls architecture VDSO update hooks when clock state changes.

## State and Persistence Behavior
`timekeeper` is central persistent kernel state, containing seqcount-protected read bases, wall-to-monotonic offset, total sleep time, raw time, TAI offset, NTP error/multiplier fields, leap state, cycle interval, and shadow copy for update calculations.

## Dependencies and Integration Points
It depends on clocksource IDs, seqcount, time64, ktime, timecounter concepts, and optional GENERIC_GETTIMEOFDAY/VDSO hooks. Direct includes are `linux/clocksource.h`, `linux/jiffies.h`, `linux/time.h`.

## Risks and Edge Cases
This layout is concurrency-critical. Incorrect seqcount updates, clocksource masks, NTP error math, or VDSO shadow updates can produce non-monotonic time, broken fast reads, or wrong leap/TAI offsets.

## Test Signals
Run timekeeping selftests, clocksource switch tests, NTP adjustment/leap-second simulations, suspend/resume, VDSO correctness checks, and lockdep/seqcount validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timekeeper_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timekeeping.h -->
# sources/distributed-fs/ceph-client/include/linux/timekeeping.h

## Purpose
declares the public kernel timekeeping API for initialization, setting wall time, reading coarse/fine/raw/boottime/TAI clocks, fast nanosecond readers, RTC/persistent clock hooks, cross timestamps, and snapshots.

## Important APIs, Types, and Functions
The file is 361 lines and exports these visible symbol families: types/enums `tk_offsets`, `system_time_snapshot`, `system_device_crosststamp`, `system_counterval_t`; macros/constants none; function-like macros none; inline helpers `ktime_get_real`, `ktime_get_coarse_real`, `ktime_get_boottime`, `ktime_get_coarse_boottime`, `ktime_get_clocktai`, `ktime_get_coarse_clocktai`, `ktime_get_coarse`, `ktime_get_coarse_ns`, `ktime_get_coarse_real_ns`, `ktime_get_coarse_boottime_ns`, `ktime_get_coarse_clocktai_ns`, `ktime_mono_to_real`, `ktime_get_ns`, `ktime_get_real_ns`, and 11 more; external prototypes `timekeeping_init`, `legacy_timer_tick`, `do_settimeofday64`, `do_sys_settimeofday64`, `ktime_get`, `ktime_get_ts64`, `ktime_get_real_ts64`, `ktime_get_coarse_ts64`, `ktime_get_coarse_real_ts64`, `ktime_get_clock_ts64`, `ktime_get_coarse_real_ts64_mg`, `ktime_get_real_ts64_mg`, `timekeeping_get_mg_floor_swaps`, `getboottime64`, and 28 more.

## Control Flow
Core boot initializes timekeeping; syscalls and RTC code set or adjust wall time; readers choose timespec, ktime, seconds, nanoseconds, coarse, or fast accessors. Cross-timestamp code correlates device counters with system time for PTP-style synchronization.

## State and Persistence Behavior
Most state lives in the internal timekeeper, while this header exposes `timekeeping_suspended`, persistent-clock locality, snapshot structures, cross-timestamp structures, and base-clock counter values.

## Dependencies and Integration Points
It depends on clocksource IDs, time64/ktime, time namespaces indirectly through readers, RTC/persistent clock code, and architecture VDSO/fast-time support. Direct includes are `linux/errno.h`, `linux/clocksource_ids.h`, `linux/ktime.h`.

## Risks and Edge Cases
Callers must choose the right clock domain: monotonic excludes suspend, boottime includes suspend, real is wall-clock, raw excludes NTP, and TAI includes TAI offset. Fast readers trade synchronization for speed and have context constraints.

## Test Signals
Run timekeeping and VDSO selftests, clock_settime/adjtimex tests, suspend/resume boottime checks, PTP cross-timestamp validation, persistent clock update tests, and namespace-offset tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timekeeping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timer.h -->
# sources/distributed-fs/ceph-client/include/linux/timer.h

## Purpose
declares the classic jiffies-based `timer_list` API, initialization macros, flag layout, add/modify/reduce/delete/shutdown functions, and CPU hotplug hooks.

## Important APIs, Types, and Functions
The file is 201 lines and exports these visible symbol families: types/enums `hrtimer`; macros/constants `TIMER_CPUMASK`, `TIMER_MIGRATING`, `TIMER_BASEMASK`, `TIMER_DEFERRABLE`, `TIMER_PINNED`, `TIMER_IRQSAFE`, `TIMER_INIT_FLAGS`, `TIMER_ARRAYSHIFT`, `TIMER_ARRAYMASK`, `TIMER_TRACE_FLAGMASK`, `TIMER_NEXT_MAX_DELTA`, `timers_prepare_cpu`, `timers_dead_cpu`; function-like macros `__TIMER_LOCKDEP_MAP_INITIALIZER`, `__TIMER_INITIALIZER`, `DEFINE_TIMER`, `__timer_init`, `__timer_init_on_stack`, `timer_setup`, `timer_setup_on_stack`, `timer_container_of`; inline helpers `timer_init_key_on_stack`, `timer_destroy_on_stack`, `timer_pending`, `tmigr_isolated_exclude_cpumask`; external prototypes `__TIMER_INITIALIZER`, `timer_init_key_on_stack`, `timer_init_key`, `DEFINE_TIMER`, `add_timer_on`, `mod_timer`, `mod_timer_pending`, `timer_reduce`, `add_timer`, `add_timer_local`, `add_timer_global`, `timer_delete_sync_try`, `timer_delete_sync`, `timer_delete`, and 13 more.

## Control Flow
Callers initialize timers with `timer_setup()` or DEFINE_TIMER, arm them with add/mod/reduce helpers, callbacks run from timer softirq context, and teardown uses delete or shutdown variants. Pinned/deferrable/irqsafe flags influence CPU placement, idle behavior, and callback locking expectations.

## State and Persistence Behavior
`timer_list` stores callback, expiry, flags/base encoding, and lockdep map. The timer wheel and per-CPU bases maintain queued state; `timer_pending()` checks whether the hlist node is unhashed.

## Dependencies and Integration Points
It depends on timer types, debugobjects, lockdep, workqueues/cpumasks, hrtimer for real-time interval hook, and CPU hotplug. Direct includes are `linux/list.h`, `linux/ktime.h`, `linux/stddef.h`, `linux/debugobjects.h`, `linux/stringify.h`, `linux/timer_types.h`.

## Risks and Edge Cases
Deleting a timer while its callback can rearm or holds locks is subtle; shutdown variants prevent rearming and are safer for teardown. Flag bitfields encode CPU/base state and must not collide. IRQ-safe timers need callback discipline.

## Test Signals
Run timer selftests, debugobjects coverage, module unload teardown tests using delete vs shutdown, CPU hotplug with pinned timers, deferrable idle behavior, and race tests for mod/delete/rearm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timer_types.h -->
# sources/distributed-fs/ceph-client/include/linux/timer_types.h

## Purpose
defines `struct timer_list`, the storage object for classic jiffies timers.

## Important APIs, Types, and Functions
The file is 24 lines and exports these visible symbol families: types/enums `timer_list`; macros/constants none; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
The full timer API in `timer.h` initializes and queues this object; timer wheel code links it through `entry`, calls `function`, and uses `expires` plus encoded `flags` for scheduling.

## State and Persistence Behavior
Each timer stores hlist linkage, expiry jiffies, callback pointer, flags, and optional lockdep map.

## Dependencies and Integration Points
It depends on hlist and lockdep types and is included separately so structures can embed timers without pulling the full API. Direct includes are `linux/lockdep_types.h`, `linux/types.h`.

## Risks and Edge Cases
Embedding code must not copy initialized timers blindly because list linkage and lockdep state are live. Callback and flags must be initialized before arming.

## Test Signals
Compile embedding users, enable debugobjects timers, and run arm/delete/reinit lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timer_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timerfd.h -->
# sources/distributed-fs/ceph-client/include/linux/timerfd.h

## Purpose
defines kernel-side flag masks for timerfd creation and settime operations.

## Important APIs, Types, and Functions
The file is 21 lines and exports these visible symbol families: types/enums none; macros/constants `TFD_SHARED_FCNTL_FLAGS`, `TFD_CREATE_FLAGS`, `TFD_SETTIME_FLAGS`; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
timerfd syscall code validates user flags against `TFD_CREATE_FLAGS` and `TFD_SETTIME_FLAGS`, sharing close-on-exec and nonblocking bits with file descriptor creation and accepting absolute/cancel-on-set timer modes for settime.

## State and Persistence Behavior
No state is stored here; actual timerfd state lives in fs/timerfd implementation objects.

## Dependencies and Integration Points
It includes the timerfd UAPI and integrates with file-descriptor and hrtimer/alarmtimer code. Direct includes are `uapi/linux/timerfd.h`.

## Risks and Edge Cases
Flag validation drift can accept unsupported bits or reject ABI-defined flags. Cancel-on-set semantics must only apply to relevant real-time clocks.

## Test Signals
Run timerfd syscall selftests for invalid flags, nonblocking/CLOEXEC, absolute timers, cancel-on-set, and clock changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timerfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timeriomem-rng.h -->
# sources/distributed-fs/ceph-client/include/linux/timeriomem-rng.h

## Purpose
defines platform data for timeriomem RNG devices that sample an MMIO register after a configured period.

## Important APIs, Types, and Functions
The file is 22 lines and exports these visible symbol families: types/enums `timeriomem_rng_data`; macros/constants none; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Platform code supplies register address, sampling period, quality estimate, and endianness through `timeriomem_rng_data`; the RNG driver polls the register and feeds hwrng output.

## State and Persistence Behavior
The structure is initialization data; runtime sampling state lives in the hwrng driver.

## Dependencies and Integration Points
It depends on IO memory pointers and hwrng platform-device registration. Direct includes are none.

## Risks and Edge Cases
Incorrect period or quality overstates entropy. Wrong endianness or MMIO address can return deterministic or unrelated data.

## Test Signals
Probe with platform data, verify MMIO reads in little/big-endian modes, run hwrng health/throughput tests, and check entropy quality configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timeriomem-rng.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timerqueue.h -->
# sources/distributed-fs/ceph-client/include/linux/timerqueue.h

## Purpose
declares red-black-tree timerqueue helpers used by hrtimers and other ordered-by-expiry queues, plus linked-list variants for duplicate expiry ordering.

## Important APIs, Types, and Functions
The file is 85 lines and exports these visible symbol families: types/enums `timerqueue_node`, `timerqueue_linked_node`; macros/constants none; function-like macros none; inline helpers `timerqueue_init`, `timerqueue_node_queued`, `timerqueue_init_head`; external prototypes `timerqueue_add`, `timerqueue_del`, `timerqueue_linked_add`, `rb_entry_safe`, `rb_erase_linked`.

## Control Flow
Users initialize a head and nodes, add nodes by expiry, read the earliest node with `timerqueue_getnext()` or linked first, iterate/delete nodes, and test queued state through rb linkage.

## State and Persistence Behavior
`timerqueue_head` stores an rb root and cached next pointer; linked heads also keep a list for nodes sharing or ordering expiry. Nodes store expiry values in `timerqueue_types.h`.

## Dependencies and Integration Points
It depends on rbtrees/lists through the types header and integrates with hrtimer internals and scheduler/time code needing ordered timers. Direct includes are `linux/rbtree.h`, `linux/timerqueue_types.h`.

## Risks and Edge Cases
Nodes must not be added twice, and callers own locking. Cached leftmost pointers must stay consistent with rb mutations; linked variants need list/rbtree synchronization.

## Test Signals
Unit-test insertion/deletion ordering, duplicate expiry ordering, queued-state checks, iteration after deletion, and randomized add/delete sequences under debug rbtree checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timerqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timerqueue_types.h -->
# sources/distributed-fs/ceph-client/include/linux/timerqueue_types.h

## Purpose
defines timerqueue node and head storage types without pulling in the full helper API.

## Important APIs, Types, and Functions
The file is 27 lines and exports these visible symbol families: types/enums `timerqueue_node`, `timerqueue_head`, `timerqueue_linked_node`, `timerqueue_linked_head`; macros/constants none; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Code embeds `timerqueue_node` or `timerqueue_linked_node` in timer objects, initializes heads, and uses `timerqueue.h` functions to manipulate the rb-tree and list linkage.

## State and Persistence Behavior
Nodes store rb linkage and expiry; linked nodes add a list head. Heads store rb roots, cached next node, and optional duplicate-order list.

## Dependencies and Integration Points
It depends on rbtree and list types. Direct includes are `linux/rbtree_types.h`, `linux/types.h`.

## Risks and Edge Cases
The types contain live intrusive linkage, so object lifetime and single-queue ownership must be enforced by callers.

## Test Signals
Compile embedding users and run timerqueue ordering/lifetime tests with debug list/rbtree enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timerqueue_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timex.h -->
# sources/distributed-fs/ceph-client/include/linux/timex.h

## Purpose
declares NTP/adjtimex constants, frequency/phase scaling values, entropy cycle fallback hooks, and kernel adjtime/PPS entry points.

## Important APIs, Types, and Functions
The file is 165 lines and exports these visible symbol families: types/enums none; macros/constants `ADJ_ADJTIME`, `ADJ_OFFSET_SINGLESHOT`, `ADJ_OFFSET_READONLY`, `SHIFT_PLL`, `SHIFT_FLL`, `MAXTC`, `SHIFT_USEC`, `PPM_SCALE`, `PPM_SCALE_INV_SHIFT`, `PPM_SCALE_INV`, `MAXPHASE`, `MAXFREQ`, `MAXFREQ_SCALED`, `MINSEC`, and 6 more; function-like macros `random_get_entropy`, `shift_right`; inline helpers none; external prototypes `Copyright`, `do_adjtimex`, `do_clock_adjtime`, `hardpps`, `read_current_timer`.

## Control Flow
Clock adjustment syscalls call `do_adjtimex()` or `do_clock_adjtime()`, NTP code uses PLL/FLL constants and scaled PPM values to discipline the timekeeper, PPS code calls `hardpps()`, and architectures provide `get_cycles()` or the fallback entropy source.

## State and Persistence Behavior
The header stores no state, but constants govern NTP discipline state in timekeeping code and expose PIT tick rate defaults.

## Dependencies and Integration Points
It depends on UAPI timex, clock IDs, cycle counters, and architecture timer definitions; it integrates with NTP, PTP/PPS, random entropy sampling, and legacy PIT timing. Direct includes are `uapi/linux/timex.h`, `linux/compiler.h`, `linux/types.h`, `linux/param.h`, `asm/timex.h`.

## Risks and Edge Cases
Scaling constants and shift math are subtle. Overflow or sign errors in phase/frequency adjustment can destabilize system time. Entropy fallbacks must not promise more randomness than available.

## Test Signals
Run adjtimex/clock_adjtime selftests, NTP slew/step simulations, PPS tests, frequency boundary checks, and architecture builds with and without native cycle counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tnum.h -->
# sources/distributed-fs/ceph-client/include/linux/tnum.h

## Purpose
declares tristate-number operations used primarily by the eBPF verifier to represent known and unknown bits of scalar values.

## Important APIs, Types, and Functions
The file is 138 lines and exports these visible symbol families: types/enums `tnum`; macros/constants none; function-like macros none; inline helpers `tnum_is_const`, `tnum_equals_const`, `tnum_is_unknown`, `tnum_subreg_is_const`; external prototypes `tnum_const`, `tnum_range`, `tnum_lshift`, `tnum_rshift`, `tnum_arshift`, `tnum_add`, `tnum_sub`, `tnum_neg`, `tnum_and`, `tnum_or`, `tnum_xor`, `tnum_mul`, `tnum_overlap`, `tnum_intersect`, and 13 more.

## Control Flow
Verifier code constructs constants, unknowns, and ranges; propagates uncertainty through shifts, arithmetic, bitwise ops, multiplication, casts, byte swaps, and subregister updates; then tests alignment, subset inclusion, overlap, and formatting for diagnostics.

## State and Persistence Behavior
A `struct tnum` is immutable value/mask data passed by value. No global state is held except the exported `tnum_unknown` constant.

## Dependencies and Integration Points
It depends on integer types and integrates with BPF register range/var_off tracking, verifier logs, and alignment checks. Direct includes are `linux/types.h`.

## Risks and Edge Cases
Tnum ranges are conservative supersets; callers must not treat `tnum_range()` as an exact interval. Incorrect arithmetic propagation can make the verifier unsound or reject valid programs.

## Test Signals
Run BPF verifier selftests, unit-test each tnum operation, check range/subset edge cases, subregister propagation, byte swaps, alignment, and diagnostic formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tnum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/topology.h -->
# sources/distributed-fs/ceph-client/include/linux/topology.h

## Purpose
provides generic CPU/NUMA topology accessors, fallback topology IDs/masks, node-distance constants, NUMA iteration helpers, scheduler NUMA hooks, and CPU capacity scale accessors.

## Important APIs, Types, and Functions
The file is 342 lines and exports these visible symbol families: types/enums none; macros/constants `LOCAL_DISTANCE`, `REMOTE_DISTANCE`, `DISTANCE_BITS`, `RECLAIM_DISTANCE`, `PENALTY_FOR_NODE_WITH_CPUS`, `TOPOLOGY_DIE_SYSFS`, `TOPOLOGY_CLUSTER_SYSFS`, `TOPOLOGY_BOOK_SYSFS`, `TOPOLOGY_DRAWER_SYSFS`, `topology_is_primary_thread`; function-like macros `nr_cpus_node`, `node_distance`, `topology_physical_package_id`, `topology_die_id`, `topology_cluster_id`, `topology_core_id`, `topology_book_id`, `topology_drawer_id`, `topology_ppin`, `topology_sibling_cpumask`, `topology_core_cpumask`, `topology_cluster_cpumask`, `topology_die_cpumask`, `topology_book_cpumask`, and 3 more; inline helpers `numa_node_id`, `cpu_to_node`, `set_numa_node`, `set_cpu_numa_node`, `set_numa_mem`, `numa_mem_id`, `cpu_to_mem`, `set_cpu_numa_mem`, `topology_is_primary_thread`, `sched_numa_hop_mask`, `topology_get_cpu_scale`; external prototypes `arch_update_cpu_topology`, `raw_cpu_read`, `per_cpu`, `cpu_to_node`, `set_numa_mem`, `numa_node_id`, `topology_sibling_cpumask`, `cpumask_of_node`, `sched_numa_find_nth_cpu`, `cpumask_nth_and`, `ERR_PTR`, `for_each_node_numadist`, `sched_numa_hop_mask`, `topology_set_cpu_scale`.

## Control Flow
Architecture topology code supplies overrides; generic code uses fallback package/core/cluster/die/book/drawer IDs and masks where absent. Scheduler and MM code query node distances, CPU-to-node/memory mappings, NUMA hop masks, and CPU capacity scale.

## State and Persistence Behavior
Runtime state includes per-CPU NUMA node/memory IDs, `node_reclaim_distance`, per-CPU `cpu_scale`, and architecture-provided topology masks. The header provides accessors and iteration macros over that state.

## Dependencies and Integration Points
It depends on arch topology, cpumasks, nodemasks, mmzone, SMP/percpu, and optional CONFIG_NUMA and memoryless-node support. Direct includes are `linux/arch_topology.h`, `linux/cpumask.h`, `linux/nodemask.h`, `linux/bitops.h`, `linux/mmzone.h`, `linux/smp.h`, `linux/percpu.h`, `asm/topology.h`.

## Risks and Edge Cases
Fallback masks can hide missing architecture topology. NUMA distance iteration requires RCU protection, and wrong CPU-to-node mappings degrade scheduling, reclaim, and locality decisions.

## Test Signals
Boot NUMA and non-NUMA configs, validate sysfs topology, scheduler NUMA hop masks, memoryless node mappings, CPU hotplug topology updates, and capacity scale values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/torture.h -->
# sources/distributed-fs/ceph-client/include/linux/torture.h

## Purpose
declares common infrastructure for in-kernel torture tests, especially RCU/locking stress modules: parameter macros, logging, CPU hotplug exercise, randomization, high-resolution timeout fuzzing, task shuffling, shutdown/stutter control, and kthread lifecycle helpers.

## Important APIs, Types, and Functions
The file is 138 lines and exports these visible symbol families: types/enums `torture_random_state`, `torture_ofl_func`; macros/constants `TORTURE_FLAG`; function-like macros `torture_param`, `TOROUT_STRING`, `VERBOSE_TOROUT_STRING`, `TOROUT_ERRSTRING`, `torture_init_error`, `DEFINE_TORTURE_RANDOM`, `DEFINE_TORTURE_RANDOM_PERCPU`, `torture_create_kthread`, `torture_create_kthread_cb`, `torture_stop_kthread`, `torture_preempt_schedule`; inline helpers `torture_num_online_cpus`, `torture_random_init`; external prototypes `verbose_torout_sleep`, `pr_alert`, `torture_num_online_cpus`, `torture_ofl_func`, `torture_offline`, `torture_online`, `torture_onoff_init`, `torture_onoff_stats`, `torture_onoff_failures`, `torture_random`, `torture_hrtimeout_ns`, `torture_hrtimeout_us`, `torture_hrtimeout_ms`, `torture_hrtimeout_jiffies`, and 18 more.

## Control Flow
A torture module calls init-begin/end helpers, creates worker kthreads with macros, optionally starts CPU on/offline, shuffler, stutter, and auto-shutdown facilities, logs through TOROUT macros, and stops through cleanup/must-stop checks.

## State and Persistence Behavior
State is held by torture implementation code in worker tasks, hotplug counters, random states, shutdown timers, stutter state, and global torture type/verbosity settings. `torture_random_state` can be global or per-CPU.

## Dependencies and Integration Points
It depends on modules, cpumasks, completions, hrtimers, spinlocks, seqlocks, debugobjects, threads, lockdep, and optional RCU/lock torture configs. Direct includes are `linux/types.h`, `linux/cache.h`, `linux/spinlock.h`, `linux/threads.h`, `linux/cpumask_types.h`, `linux/seqlock.h`, `linux/lockdep.h`, `linux/completion.h`, `linux/debugobjects.h`, `linux/bug.h`, `linux/compiler.h`, `linux/hrtimer.h`.

## Risks and Edge Cases
Torture code intentionally stresses hotplug, scheduler, timers, and locking; cleanup ordering must reliably stop kthreads and undo hotplug/shuffle state. Logging can be high volume and timing-sensitive.

## Test Signals
Run rcutorture and locktorture scenarios with CPU hotplug, stutter, shuffle, timeout fuzzing, preemption variants, and module/built-in initialization failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/torture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/toshiba.h -->
# sources/distributed-fs/ceph-client/include/linux/toshiba.h

## Purpose
declares the Toshiba laptop SMM call entry point and includes the UAPI SMM register layout.

## Important APIs, Types, and Functions
The file is 16 lines and exports these visible symbol families: types/enums none; macros/constants none; function-like macros none; inline helpers none; external prototypes `Copyright`.

## Control Flow
Toshiba platform drivers fill `SMMRegisters`, call `tosh_smm()`, and interpret firmware-updated register fields for laptop-specific control or query operations.

## State and Persistence Behavior
No state is held in the header; firmware/SMM state is mutated by the called platform implementation.

## Dependencies and Integration Points
It depends on `uapi/linux/toshiba.h` and x86/platform SMM access code. Direct includes are `uapi/linux/toshiba.h`.

## Risks and Edge Cases
SMM calls are firmware-specific and privileged. Bad register setup can hang firmware or change hardware state unexpectedly; packing/alignment must match the UAPI layout.

## Test Signals
Build Toshiba platform drivers, validate register ABI, and exercise non-destructive SMM queries on supported hardware with error-path handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/toshiba.h -->
