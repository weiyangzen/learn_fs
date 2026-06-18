## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal.c

### Purpose
`opal.c` is the central PowerNV OPAL integration layer. It discovers the firmware entry, configures CPUs, manages OPAL messages/events, console I/O, HMI/MCE recovery, sysfs exports, platform-device creation, polling, shutdown synchronization, scatter-gather helpers, and common OPAL error translation.

### Important APIs, Types, And Functions
Important globals are `struct opal opal`, `opal_node`, `opal_kobj`, notifier heads, `kopald_tsk`, and `opal_msg`. Key functions include `early_init_dt_scan_opal()`, `opal_configure_cores()`, `early_init_dt_scan_recoverable_ranges()`, `opal_message_notifier_register()`, `opal_handle_message()`, `opal_get_chars()`, `opal_put_chars()`, `opal_flush_console()`, `opal_machine_check()`, `opal_hmi_exception_early*()`, `opal_handle_hmi_exception()`, `opal_mce_check_early_recovery()`, `opal_init()`, `opal_shutdown()`, `opal_vmalloc_to_sg_list()`, `opal_free_sg_list()`, and `opal_error_code()`.

### Control Flow
Early boot scans `/ibm,opal`, records runtime base/entry/size, enables `FW_FEATURE_OPAL`, and parses machine-check recovery ranges. OPAL init creates console and service platform devices, starts message and async completion handling, starts sensors/HMI, initializes the heartbeat poller, creates `/sys/firmware/opal`, registers dump/log/flash/sysparam/msglog/export interfaces, instantiates IPMI/flash/PRD/oppanel/secvar devices, and initializes powercap, PSR, sensor groups, power control, and panic console flushing. The `kopald` thread repeatedly drains OPAL events then sleeps for the firmware heartbeat. Message handling pulls firmware messages via `opal_get_msg()`, validates types, queues messages with no registered notifier, and replays queued messages on registration.

### State, Persistence, And Dependencies
State is global and boot-lifetime: firmware entry descriptor, message queues, notifier arrays, sysfs kobjects, poller thread, OPAL message buffer, heartbeat interval, machine-check recovery ranges, and console write lock. Persistent state lives in firmware services and platform devices. Dependencies include OF, OPAL wrappers/tokens, IRQ events from `opal-irqchip.c`, async completion, PowerPC MCE/HMI machinery, kobjects/sysfs, platform devices, kthreads, and panic/console infrastructure.

### Integration Points
Many files in this directory are initialized from `opal_init()` or consume its exported symbols. The generic PowerPC console, RTC, PCI, PRD, flash, error log, dump, secvar, sensor, and power-control layers all hinge on this core. Exported OPAL symbols are used by drivers and test modules.

### Risks
OPAL message replay is capped at 16 queued messages and can drop early messages on allocation pressure. Console paths must work in atomic and panic contexts while handling busy firmware responses. Machine-check and HMI recovery paths are high stakes and rely on firmware-provided recovery ranges and flags. `opal_shutdown()` spins until firmware sync exits busy states. `opal_vmalloc_to_sg_list()` assumes vmalloc pages can be converted page by page and chained in OPAL SG format.

### Test Signals
Test OPAL DT detection, unsupported OPAL versions, queued message replay and overflow, notifier registration/unregistration, console read/write/flush busy paths, heartbeat poller wakeups, HMI event delivery to `kopald`, MCE recovery for user/kernel/fatal cases, sysfs export creation, shutdown sync busy loops, SG list chaining/freeing, and `opal_error_code()` mappings.
