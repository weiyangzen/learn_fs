# subset-b-000802 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-imc.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-imc.c

### Purpose
`opal-imc.c` discovers OPAL In-Memory Collection counter units on PowerNV, creates Linux IMC PMUs for nest/core/thread/trace domains, exposes nest control blocks through debugfs, and stops firmware counters during shutdown or kdump boot.

### Important APIs, Types, And Functions
Key functions are `imc_pmu_create()`, `imc_get_mem_addr_nest()`, `export_imc_mode_and_cmd()`, `disable_nest_pmu_counters()`, `disable_core_pmu_counters()`, `get_max_nest_dev()`, `opal_imc_counters_probe()`, and `opal_imc_counters_shutdown()`. It relies on `struct imc_pmu`, `struct imc_mem_info`, `init_imc_pmu()`, `unregister_thread_imc()`, and OPAL `opal_imc_counters_stop()`.

### Control Flow
The platform driver probes `ibm,opal-imc-counters`, scans compatible IMC unit nodes, maps each device-tree `type` to an IMC domain, creates a PMU, and tracks whether core/thread PMUs registered. Nest PMUs read chip IDs and base addresses from firmware properties, apply the counter offset, and build a `mem_info` array ending with a zero entry. The first nest PMU also creates debugfs files for `imc_mode_*` and `imc_cmd_*`. If thread IMC exists without core IMC, thread support is unregistered.

### State, Persistence, And Dependencies
The driver persists registered PMU objects, debugfs dentries, and nest counter virtual addresses for the boot lifetime. Firmware counter state persists outside Linux, so shutdown and kdump paths explicitly stop nest and core engines. Dependencies include Open Firmware properties, `arch_debugfs_dir`, CPU/node topology, endian conversion for control words, and the shared IMC PMU layer.

### Integration Points
It is a built-in platform driver and is instantiated by `opal.c` via `opal_imc_init_dev()`. PMU registration feeds the perf IMC subsystem, while debugfs gives privileged operators direct control over nest mode/command words.

### Risks
The debugfs helpers use `debugfs_create_file_unsafe()` over firmware-shared memory, so invalid writes can perturb counters. Nest memory uses `phys_to_virt()` and assumes OPAL-provided memory is mapped. Error cleanup is partial, and shutdown explicitly notes that PMU unregister/memory cleanup is not handled.

### Test Signals
Useful checks include DT variants for each IMC type, missing `type`, `size`, `chip-id`, `base-addr`, and `offset` properties, kdump boot counter-stop behavior, debugfs read/write endian correctness, perf PMU registration, and shutdown stopping one counter per node/core sibling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-imc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-irqchip.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-irqchip.c

### Purpose
`opal-irqchip.c` turns OPAL firmware event bits into Linux IRQs. It builds an IRQ domain for up to 64 OPAL events, handles firmware interrupt sources, records outstanding events, and wakes the OPAL poller thread when work is pending.

### Important APIs, Types, And Functions
Important pieces are `struct opal_event_irqchip`, `opal_handle_events()`, `opal_have_pending_events()`, `opal_interrupt()`, `opal_event_init()`, `opal_event_shutdown()`, and exported `opal_event_request()`. The local `irq_chip` supplies mask, unmask, and level-high type handling.

### Control Flow
Initialization finds `/ibm,opal`, creates a linear IRQ domain, determines OPAL interrupt resources from either standard `interrupts` or legacy `opal-interrupts`, maps them to Linux IRQs, and requests `opal_interrupt()` for each. The interrupt handler calls `opal_handle_interrupt()`, stores returned event bits in `last_outstanding_events`, and wakes `kopald`. The poller drains masked-in bits with `generic_handle_domain_irq()`, clears the cached event word, calls `opal_poll_events()`, and loops while firmware reports more events.

### State, Persistence, And Dependencies
State is global: the event mask, IRQ domain, resource array, IRQ count, and the last outstanding event bitmap. Masking is bit-level and controls which event bits become Linux IRQs. It depends on OPAL interrupt/poll calls, the core PowerNV poller in `opal.c`, Linux IRQ domains, and DT interrupt descriptions.

### Integration Points
`opal_event_init()` is a PowerNV arch initcall. Other OPAL services request event IRQs either through device tree interrupt mappings or the legacy exported `opal_event_request()`. Shutdown is called by `opal_shutdown()` before host reboot sync.

### Risks
`last_outstanding_events` is a single global cache written by interrupt context and drained by the poller, so lost-event resistance depends on polling firmware after clearing the cache. IRQ names allocated with `kasprintf()` are not freed after successful `request_irq()`. Legacy and new interrupt schemes must both stay functional.

### Test Signals
Test event delivery with masked/unmasked events, legacy and standard DT bindings, missing IRQ resources, shutdown from interrupt-disabled contexts, repeated firmware event bits that require level-style rehandling, and `opal_event_request()` before/after domain creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-irqchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-kmsg.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-kmsg.c

### Purpose
`opal-kmsg.c` registers a kmsg dumper whose only job is to flush OPAL console output on panic so panic messages are not left buffered in firmware.

### Important APIs, Types, And Functions
The key functions are `kmsg_dump_opal_console_flush()` and `opal_kmsg_init()`. The file owns one static `struct kmsg_dumper` that calls `opal_flush_console(0)` for panic dumps.

### Control Flow
Initialization registers the dumper with `kmsg_dump_register()`. During dump callbacks it checks `detail->reason`; non-panic dumps return immediately because normal OPAL pollers should continue flushing. Panic dumps synchronously flush virtual terminal 0.

### State, Persistence, And Dependencies
There is no persistent state beyond kmsg dumper registration. It depends on the OPAL console flushing implementation in `opal.c` and the kernel kmsg dump framework.

### Integration Points
`opal_init()` installs this after creating other OPAL platform services. It complements `panic_flush_kmsg_start()` and the OPAL console backend by draining firmware state when the regular poll loop is no longer running.

### Risks
The code assumes vterm 0 is the relevant panic console. If firmware flush never completes, `opal_flush_console()` can spin in panic context. Registration failure only logs an error, leaving panic output dependent on the existing poll/console path.

### Test Signals
Test kmsg dumper registration, panic-only behavior, firmware with and without `OPAL_CONSOLE_FLUSH`, busy/partial console responses, and panic output visibility on OPAL-backed consoles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-kmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-lpc.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-lpc.c

### Purpose
`opal-lpc.c` provides LPC bus access on PowerNV through OPAL. It installs special ISA/PCI I/O callbacks for non-memory-mapped LPC buses and optionally exposes raw LPC IO/MEM/FW address spaces through debugfs.

### Important APIs, Types, And Functions
Important functions are byte/word/long accessors `opal_lpc_in*()` and `opal_lpc_out*()`, string I/O helpers, `lpc_debug_read()`, `lpc_debug_write()`, `opal_lpc_init_debugfs()`, and `opal_lpc_init()`. `struct lpc_debugfs_entry` records the OPAL LPC address type.

### Control Flow
Boot scans for an available primary `ibm,power8-lpc` node, records its chip ID, and either initializes a non-PCI ISA bridge for memory-mapped LPC ranges or installs `ppc_pci_io` callbacks backed by `opal_lpc_read()` and `opal_lpc_write()`. Debugfs creates `lpc/io`, `lpc/mem`, and `lpc/fw`. Debugfs reads and writes choose 1-, 2-, or 4-byte accesses based on alignment and address type, then adjust endian/layout quirks around OPAL's right-justified big-endian 32-bit data word.

### State, Persistence, And Dependencies
The main state is the selected `opal_lpc_chip_id` and debugfs entries. Real persistence is in LPC devices and firmware. Dependencies include OPAL LPC calls, OF primary bus properties, ISA bridge setup, `ppc_pci_io`, endian conversion, and user-copy APIs.

### Integration Points
Low-level I/O operations used by ISA-style drivers can route through this file when the LPC bus is not directly mapped. Debugfs is a privileged diagnostic and firmware access surface.

### Risks
Endian handling for unaligned and small accesses is delicate, especially on little-endian kernels. The driver supports only one primary LPC bus despite the OPAL API allowing more. Debugfs exposes raw firmware/LPC address spaces and uses manually allocated entries without removal cleanup.

### Test Signals
Tests should cover mapped and non-mapped LPC DT setups, invalid chip ID/port bounds, unaligned word/long accesses, little-endian debugfs byte layout, partial user-copy failures, debugfs IO/MEM/FW reads/writes, and ISA driver access through `ppc_pci_io`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-lpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-memory-errors.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-memory-errors.c

### Purpose
`opal-memory-errors.c` handles asynchronous OPAL memory error messages and converts affected physical address ranges into Linux `memory_failure()` calls.

### Important APIs, Types, And Functions
Key elements are `struct OpalMsgNode`, `opal_memory_err_event()`, `mem_error_work`, `handle_memory_error()`, `handle_memory_error_event()`, and `opal_mem_err_init()`.

### Control Flow
The initcall registers a notifier for `OPAL_MSG_MEM_ERR`. The notifier filters message type, allocates a queue node with `GFP_ATOMIC`, copies the `opal_msg`, appends it to a spinlock-protected list, and schedules work. The worker drains the list outside the spinlock, decodes resilience or dynamic-deallocation ranges from `OpalMemoryErrorData`, and calls `memory_failure()` for each page in the firmware-provided range.

### State, Persistence, And Dependencies
State is the one-time registration flag, a queued message list, and its spinlock. Persistent system effects are page poison/offline handling triggered through the memory failure subsystem. Dependencies include OPAL message notifiers from `opal.c`, endian conversion, kernel workqueues, and memory error data structures.

### Integration Points
This file plugs firmware memory health events into Linux memory failure handling. It is initialized as a PowerNV device initcall, after OPAL message infrastructure is available.

### Risks
The notifier can drop events on allocation failure. Large address ranges schedule one `memory_failure()` per page and may be expensive. Unknown event types are silently ignored, and there is no unregister path. Correctness depends on firmware range end values and page alignment behavior.

### Test Signals
Inject OPAL memory error messages for resilience and dynamic deallocation, unknown types, empty and large ranges, allocation failure paths, concurrent queued events, and verify `memory_failure()` receives page frame numbers derived from big-endian physical addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-memory-errors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-msglog.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-msglog.c

### Purpose
`opal-msglog.c` exposes OPAL's in-memory console/message log through `/sys/firmware/opal/msglog` and provides reusable memcons helpers.

### Important APIs, Types, And Functions
The firmware layout is `struct memcons`. Key functions are `memcons_init()`, `memcons_get_size()`, `memcons_copy()`, `opal_msglog_copy()`, `opal_msglog_init()`, and `opal_msglog_sysfs_init()`.

### Control Flow
Initialization reads the `ibm,opal-memcons` physical address from the OPAL node, maps it with `phys_to_virt()`, validates the magic value, and sizes the sysfs binary attribute from input plus output buffer sizes. Reads snapshot `out_pos`, issue an `smp_rmb()`, then copy from the wrapped or linear output buffer with `memory_read_from_buffer()`.

### State, Persistence, And Dependencies
The only Linux state is the global `opal_memcons` pointer and the bin attribute size. The log buffer is firmware-owned persistent memory. The file depends on OPAL DT properties, endian conversion, physical-to-virtual mapping, and sysfs binary attributes.

### Integration Points
`opal_init()` initializes the memory console before creating the sysfs file under `opal_kobj`. `powernv.h` exposes the memcons helpers for other PowerNV code.

### Risks
The code trusts firmware buffer addresses and sizes after validating only the memcons magic. Wrap handling mutates the local `pos` after the first read and depends on `memory_read_from_buffer()` semantics. Corrupt `out_pos` aborts reads, but corrupt buffer pointers cannot be validated here.

### Test Signals
Test absent property, bad magic, wrapped and non-wrapped logs, reads with nonzero offsets and small counts, corrupt `out_pos` greater than buffer size, and sysfs creation after failed initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-msglog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-nvram.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-nvram.c

### Purpose
`opal-nvram.c` implements the PowerNV `ppc_md` NVRAM hooks on top of OPAL read/write calls and initializes NVRAM partition scanning for logs/oops storage.

### Important APIs, Types, And Functions
The file provides `opal_nvram_size()`, `opal_nvram_read()`, `opal_nvram_write()`, `opal_nvram_init()`, and the arch initcall `opal_nvram_init_log_partitions()`.

### Control Flow
Boot discovers `ibm,opal-nvram`, reads its `#bytes` property, stores `nvram_size`, and installs read/write/size callbacks in `ppc_md`. Reads clamp offsets to the NVRAM size and call `opal_read_nvram()`. Writes clamp similarly, then loop on `OPAL_BUSY` and `OPAL_BUSY_EVENT`, using `mdelay()` when interrupts are off and `msleep()` otherwise; busy-event responses also poll OPAL events.

### State, Persistence, And Dependencies
Linux stores only the NVRAM size and platform callbacks. NVRAM contents persist in firmware-backed nonvolatile storage. Dependencies include OPAL NVRAM calls, `ppc_md`, device tree, delay APIs, and generic NVRAM partition/oops helpers.

### Integration Points
Generic PowerPC NVRAM users call through `ppc_md`. Partition scanning and oops partition setup happen as an arch initcall after callbacks are registered.

### Risks
Writes can spin for repeated busy statuses, including panic paths with interrupts disabled. All OPAL failures are collapsed to `-EIO`. The code assumes buffers passed to OPAL are physically addressable via `__pa()`.

### Test Signals
Exercise boundary reads/writes, offsets at and beyond end of NVRAM, OPAL busy and busy-event retry loops, panic/interrupt-disabled writes, missing `#bytes`, partition scanning, and OPAL error conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-nvram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-power.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-power.c

### Purpose
`opal-power.c` connects OPAL shutdown, EPOW, and DPO firmware messages to Linux orderly reboot or poweroff handling.

### Important APIs, Types, And Functions
Important functions are `detect_epow()`, `poweroff_pending()`, `opal_power_control_event()`, and `opal_power_control_init()`. It registers three notifier blocks for `OPAL_MSG_SHUTDOWN`, `OPAL_MSG_EPOW`, and `OPAL_MSG_DPO`.

### Control Flow
Initialization always registers the shutdown notifier, then checks `/ibm,opal/epow` for `ibm,opal-v3-epow` support. If supported, it registers EPOW/DPO notifiers and immediately checks for pending DPO/EPOW conditions. Shutdown messages decode parameter 0 as soft reboot or soft off. EPOW status masks out non-shutdown power-change classes before deciding whether to power off.

### State, Persistence, And Dependencies
There is no mutable local state beyond notifier registration. Firmware state persists as power-control events and EPOW/DPO status. Dependencies include OPAL status calls, OPAL message notifiers, device tree compatibility, and Linux `orderly_poweroff()`/`orderly_reboot()`.

### Integration Points
`opal_init()` calls this late in OPAL service setup. It consumes messages delivered by `opal.c` and affects global system power state.

### Risks
Failure to register one notifier does not prevent initialization from returning success. EPOW interpretation depends on firmware class semantics. Unknown shutdown types are logged but otherwise ignored.

### Test Signals
Test existing DPO/EPOW at boot, shutdown messages for soft off and reboot, unsupported EPOW DT nodes, `opal_get_epow_status()` failures, filtered power class bits, and notifier registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-powercap.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-powercap.c

### Purpose
`opal-powercap.c` creates `/sys/firmware/opal/powercap` attribute groups for OPAL power capping handles, allowing current caps to be read and, where supported, written.

### Important APIs, Types, And Functions
The main types are `struct powercap_attr` and the `pcaps` array. Important functions are `powercap_show()`, `powercap_store()`, `powercap_add_attr()`, and `opal_powercap_init()`.

### Control Flow
Initialization finds `ibm,opal-powercap`, creates a `powercap` kobject, then for each child creates attributes based on `powercap-min`, `powercap-max`, and `powercap-current` properties. Reads allocate an async OPAL token, take `powercap_mutex`, call `opal_get_powercap()`, wait if needed, and print the big-endian result. Writes parse a numeric cap, use the same token/mutex pattern with `opal_set_powercap()`, and return `count` on success.

### State, Persistence, And Dependencies
Linux state is the kobject, per-child attribute groups, handles, and a mutex serializing firmware calls. Persistent values live in OPAL/platform power policy. Dependencies include OPAL async completion, `opal_error_code()`, sysfs/kobject APIs, and OF child properties.

### Integration Points
`opal_init()` calls this after `opal_kobj` exists. User space interacts through sysfs, and firmware validates/updates cap values.

### Risks
Some failure paths free only groups already counted by `i`, so partial setup must be scrutinized. Attribute `name` strings point at DT property/static strings for cap files and allocated group names for nodes. All firmware calls are serialized globally, which is simple but can block unrelated cap reads.

### Test Signals
Test child nodes with every property combination, async and immediate OPAL responses, interrupted token or mutex acquisition, invalid numeric writes, min/max read-only permissions, current write permissions, and cleanup after mid-loop allocation/sysfs failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-powercap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-prd.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-prd.c

### Purpose
`opal-prd.c` implements the `/dev/opal-prd` runtime diagnostics channel used by user-space PRD daemons to exchange messages with OPAL firmware and map firmware-provided diagnostic memory ranges.

### Important APIs, Types, And Functions
Important types are `struct opal_prd_msg`, `struct opal_prd_msg_queue_item`, and `struct opal_prd_scom`. Key functions include `opal_prd_open()`, `opal_prd_mmap()`, `opal_prd_poll()`, `opal_prd_read()`, `opal_prd_write()`, `opal_prd_ioctl()`, `opal_prd_msg_notifier()`, `opal_prd_probe()`, and `opal_prd_remove()`.

### Control Flow
Probe registers notifiers for `OPAL_MSG_PRD` and `OPAL_MSG_PRD2`, then registers a misc device. Only one opener is allowed through `prd_usage`. Firmware messages are copied in notifier context into a spinlock-protected queue and wake waiters. Reads block or return `-EAGAIN`, pop one queued message, validate user buffer size, and requeue on copy failure. Writes copy a sized PRD message from user space and forward it with `opal_prd_msg()`. IOCTLs expose kernel version info and SCOM read/write passthroughs. `mmap()` validates the requested physical range against reserved-memory children with `ibm,prd-label`.

### State, Persistence, And Dependencies
State includes the active PRD node, message queue, waitqueue, spinlock, and single-open atomic. Persistent behavior is firmware diagnostics state and reserved memory mappings. Dependencies include OPAL PRD messages, OPAL XSCOM calls, miscdevice, user-copy, remap APIs, and reserved-memory DT metadata.

### Integration Points
`opal.c` instantiates the platform device for `ibm,opal-prd`. The user-space PRD daemon uses reads/writes/poll/ioctls, while firmware sends messages through the OPAL message notifier bus.

### Risks
`opal_prd_write()` trusts the user-provided header size after only checking the initial count is at least a header; malformed sizes are delegated to `memdup_user()`. `opal_prd_range_is_valid()` requires labeled reserved-memory ranges but otherwise maps raw physical memory. Queue allocation can fail in atomic context and drop firmware messages.

### Test Signals
Test single-open enforcement, blocking and nonblocking reads, requeue on undersized buffers or copy faults, PRD and PRD2 message delivery, malformed user message sizes, FINI on release, SCOM ioctl endianness, mmap range overflow and label checks, and probe/remove notifier unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-prd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-psr.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-psr.c

### Purpose
`opal-psr.c` exposes OPAL power-shift-ratio controls under `/sys/firmware/opal/psr`, with one read/write sysfs file per firmware-described ratio handle.

### Important APIs, Types, And Functions
The main type is `struct psr_attr`. Important functions are `psr_show()`, `psr_store()`, and `opal_psr_init()`.

### Control Flow
Initialization finds `ibm,opal-power-shift-ratio`, allocates per-child attributes, creates a `psr` kobject, reads each child `handle` and `label`, and creates 0664 sysfs files. Reads and writes allocate an async token, take `psr_mutex`, call OPAL get/set functions, wait for async completion when required, translate OPAL return codes, and release the token.

### State, Persistence, And Dependencies
State is the sysfs kobject, attribute array, handles, and mutex. The PSR value is firmware/platform state. Dependencies include OPAL async calls, `opal_error_code()`, device tree child metadata, and sysfs.

### Integration Points
`opal_init()` invokes this after OPAL sysfs setup. User space can inspect and change platform PSR settings through the generated sysfs files.

### Risks
Partial initialization failures rely on `kobject_put()` and array free but do not remove already created sysfs files explicitly. All attributes use labels from DT directly. Concurrency is globally serialized; interrupted locks or tokens return to user space.

### Test Signals
Test missing node, missing handle/label, async and immediate OPAL get/set paths, invalid writes, interrupted lock/token acquisition, sysfs permissions, and cleanup after mid-loop sysfs creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-psr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-rtc.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-rtc.c

### Purpose
`opal-rtc.c` provides boot-time RTC reading and platform-device creation for OPAL RTC/TPO services.

### Important APIs, Types, And Functions
Key functions are `opal_to_tm()`, exported-by-declaration `opal_get_boot_time()`, and initcall `opal_time_init()`.

### Control Flow
`opal_get_boot_time()` checks for the `OPAL_RTC_READ` token, loops through `OPAL_BUSY` and `OPAL_BUSY_EVENT` with millisecond delays and event polling, decodes OPAL's BCD year/month/day and hour/minute/second fields, and converts the result to `time64_t`. `opal_time_init()` creates an OF-backed `opal-rtc` platform device if `/ibm,opal/rtc` exists; otherwise it registers a simple device if RTC read or TPO read tokens are present.

### State, Persistence, And Dependencies
The file keeps no persistent state. Time is firmware-backed. Dependencies include OPAL RTC/TPO tokens, BCD conversion, RTC time helpers, OF platform-device creation, and busy-event polling.

### Integration Points
The platform RTC driver binds to `opal-rtc`. Early boot time code can call `opal_get_boot_time()` to seed system time.

### Risks
Invalid BCD values are not separately validated before conversion. Busy loops use `mdelay()` because this is init/early behavior. If token checks fail, boot time silently returns zero.

### Test Signals
Test valid BCD decoding across century/month boundaries, absent tokens, OPAL busy and busy-event loops, failure returns, DT-backed versus simple platform device registration, and TPO-only fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-secvar.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-secvar.c

### Purpose
`opal-secvar.c` implements the `secvar_operations` backend for secure variables managed by OPAL firmware.

### Important APIs, Types, And Functions
Important functions are `opal_status_to_err()`, `opal_get_variable()`, `opal_get_next_variable()`, `opal_set_variable()`, `opal_secvar_format()`, `opal_secvar_max_size()`, `opal_secvar_probe()`, and `opal_secvar_init()`. The file defines `opal_secvar_ops`.

### Control Flow
Probe verifies OPAL supports get, get-next, and enqueue-update tokens, then registers operations with `set_secvar_ops()`. Get and get-next convert size arguments to big-endian before OPAL calls and convert them back on return. Set enqueues an update through firmware. Format and max-size are read from an available `ibm,secvar-backend` DT node.

### State, Persistence, And Dependencies
Linux keeps only the registered operations table. Secure variables and pending updates persist in firmware. Dependencies include OPAL secvar calls, secure boot/secvar core APIs, platform driver probing, device tree backend metadata, and OPAL error conventions.

### Integration Points
`opal.c` creates the `ibm,secvar-backend` platform device, and the generic secvar subsystem calls through this backend. It bridges secure boot variable storage to OPAL.

### Risks
`of_find_compatible_node()` may return NULL in `opal_secvar_format()` before `of_device_is_available(node)` is called, which relies on that helper tolerating NULL. OPAL status mapping collapses unknown returns to `-EINVAL`. Set requires non-NULL data, so deletion semantics must be represented by firmware-specific update payloads rather than NULL data.

### Test Signals
Test unsupported token combinations, endian size round trips, buffer-too-small `OPAL_PARTIAL`, empty variable iteration, unavailable backend node, missing `format` or `max-var-size`, firmware hardware/no-memory/resource errors, and `set_secvar_ops()` registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-secvar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-sensor-groups.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-sensor-groups.c

### Purpose
`opal-sensor-groups.c` exposes OPAL sensor group operations, currently group clearing through sysfs and group enable/disable through an exported kernel API.

### Important APIs, Types, And Functions
Key types are `struct sg_attr`, `struct sensor_group`, and `sg_ops_info`. Important functions are exported `sensor_group_enable()`, `sg_store()`, `add_attr_group()`, `get_nr_attrs()`, and `opal_sensor_groups_init()`.

### Control Flow
Initialization finds `ibm,opal-sensor-group`, creates `/sys/firmware/opal/sensor_groups`, and for each child inspects its `ops` array. Supported operations become attributes, currently `clear` for `OPAL_SENSOR_GROUP_CLEAR`. Writes accept only value `1`, allocate an async token, take `sg_mutex`, call `opal_sensor_group_clear()`, wait if needed, and return `count` on success. The exported enable API calls `opal_sensor_group_enable()` with async completion handling.

### State, Persistence, And Dependencies
State is the sensor group array, sysfs kobject, group names, operation handles, and mutex. Sensor group state persists in firmware and affects sensor collection. Dependencies include OPAL async APIs, `opal_error_code()`, DT group IDs/chip IDs/ops arrays, and sysfs.

### Integration Points
`opal_init()` creates the sysfs controls. Other kernel drivers may call `sensor_group_enable()` to control sensor groups before reads.

### Risks
The `ops` property length is passed as bytes but iterated as if it were an element count in `get_nr_attrs()` and `add_attr_group()`, which is a potential over-iteration risk unless firmware/properties are constrained elsewhere. Group names are fixed 20-byte buffers assembled with `sprintf()`. Only clear is exposed despite extensible operation metadata.

### Test Signals
Test supported and unsupported ops arrays, ops length handling, group IDs and chip IDs, clear writes with values other than 1, async/immediate completion, enable/disable API, sysfs cleanup after failures, and long node names for fixed-size group names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-sensor-groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-sensor.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-sensor.c

### Purpose
`opal-sensor.c` provides exported helpers for reading OPAL sensor handles and creates the OPAL sensor platform device.

### Important APIs, Types, And Functions
The exported functions are `opal_get_sensor_data()` and `opal_get_sensor_data_u64()`. Initialization is handled by `opal_sensor_init()`.

### Control Flow
Sensor reads allocate an interruptible OPAL async token, call `opal_sensor_read()` or `opal_sensor_read_u64()`, wait for async completion if returned, translate OPAL status, and convert big-endian data to CPU order. The u64 helper falls back to the u32 helper if `OPAL_SENSOR_READ_U64` is unavailable. Initialization finds `/ibm,opal/sensors` and creates an `opal-sensor` OF platform device.

### State, Persistence, And Dependencies
The file keeps no local state. Sensor data is firmware-owned and read on demand. Dependencies include OPAL async completion, OPAL token checks, OF platform-device creation, and exported symbols for other drivers.

### Integration Points
`opal_init()` invokes sensor platform setup. Hardware monitoring or platform drivers can call the exported read helpers using handles from device tree.

### Risks
In async read paths, the data output is assigned after converting the async return code; callers must check the returned error before using it. `OPAL_WRONG_STATE` is specially mapped to `-EIO`. Token acquisition can be interrupted and directly returned.

### Test Signals
Test immediate and async reads, u64 token fallback to u32, wrong-state handling, OPAL error mappings, interrupted token allocation, missing `/ibm,opal/sensors`, and consumers reading handles from DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-sensor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-sysparam.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-sysparam.c

### Purpose
`opal-sysparam.c` exposes OPAL system parameters as sysfs files under `/sys/firmware/opal/sysparams`, using firmware-described IDs, sizes, names, and permissions.

### Important APIs, Types, And Functions
The central type is `struct param_attr`. Important functions are `opal_get_sys_param()`, `opal_set_sys_param()`, `sys_param_show()`, `sys_param_store()`, and `opal_sys_param_init()`.

### Control Flow
Initialization validates `/ibm,opal/sysparams`, creates a kobject, allocates a shared 64-byte transaction buffer, reads parameter names, IDs, lengths, and permissions, and creates sysfs files whose modes reflect read/write flags. Reads lock `opal_sysparam_mutex`, call async `opal_get_param()`, copy the fixed-size result into `buf`, and return the parameter size. Writes clamp input to 64 bytes, copy it into the shared buffer, call async `opal_set_param()` with the DT-declared parameter size, and return the user count on success.

### State, Persistence, And Dependencies
State is the kobject, shared buffer, allocated attribute array, and mutex. Parameter values persist in OPAL/platform firmware. Dependencies include OPAL async tokens, `opal_error_code()`, DT property arrays, sysfs, and kobject lifetime.

### Integration Points
`opal_init()` calls this once `opal_kobj` is available. User space reads and writes sysfs files to query or update platform parameters.

### Risks
`sys_param_store()` clamps the copied user count but still sends `attr->param_size` bytes to firmware, so if `count` is shorter than the parameter size, trailing bytes are whatever remained in the shared buffer. Attribute objects are allocated as one array and not retained in a global pointer for removal. DT array count consistency is assumed after each read.

### Test Signals
Test missing/incompatible node, mismatched property counts, parameters larger than 64 bytes, read-only/write-only/read-write modes, short writes, async wait failures, interrupted token allocation, concurrent sysfs access, and cleanup after sysfs creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-sysparam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-tracepoints.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-tracepoints.c

### Purpose
`opal-tracepoints.c` manages OPAL call tracepoint enablement and recursion-safe trace emission around OPAL entry/exit.

### Important APIs, Types, And Functions
Key functions are `opal_tracepoint_regfunc()`, `opal_tracepoint_unregfunc()`, `__trace_opal_entry()`, and `__trace_opal_exit()`. Depending on configuration it uses either `struct static_key opal_tracepoint_key` or the TOC-visible `opal_tracepoint_refcount`.

### Control Flow
Tracepoint registration increments a static key or refcount; unregistration decrements it. Entry and exit trace helpers save local IRQ state, check a per-CPU recursion depth, emit `trace_opal_entry()` or `trace_opal_exit()` only at depth zero, and restore IRQ state. Entry disables preemption before tracing, and exit re-enables it after tracing.

### State, Persistence, And Dependencies
State is the tracepoint enable counter/static key and per-CPU recursion depth. It depends on Linux tracepoint infrastructure, jump labels, per-CPU storage, local IRQ control, and the assembly OPAL call wrapper hooks.

### Integration Points
OPAL call wrappers can call these helpers when tracepoints are enabled. Trace subscribers use the standard tracing subsystem to observe firmware call opcodes, arguments, and returns.

### Risks
The preemption disable/enable pairing is split across entry and exit helpers, so wrapper call paths must invoke them in balanced order. Recursion suppression is necessary because tracing itself may invoke OPAL calls. Non-jump-label refcount manipulation assumes tracepoint mutex serialization.

### Test Signals
Test tracepoint enable/disable transitions, nested OPAL calls during tracing, IRQ/preemption state balance, jump-label and non-jump-label builds, and tracing of both successful and failing OPAL calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-tracepoints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-wrappers.S -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-wrappers.S

### Purpose
`opal-wrappers.S` implements the low-level PowerPC transition into OPAL firmware and restoration back to Linux, including MSR and endian handling.

### Important APIs, Types, And Functions
The file defines `_GLOBAL_TOC(__opal_call)`, which receives OPAL arguments in `r3-r10`, the OPAL opcode in stack parameter `R11`, and the saved MSR in stack parameter `R12`.

### Control Flow
The wrapper saves LR, derives an OPAL MSR by clearing IR, DR, and LE bits, loads the OPAL base/entry pair from the global `opal` structure, sets HSRR0/HSRR1 for the firmware entry, loads the opcode into `r0`, and enters OPAL with `hrfid`. On return it restores the caller MSR. Big-endian builds use `mtmsrd`; little-endian builds use encoded instructions to byte-reverse the saved MSR and return through HSRR so endian state can switch correctly. The wrapper then restores the TOC and LR and returns.

### State, Persistence, And Dependencies
The wrapper consumes the global `opal` descriptor initialized from device tree by `opal.c`. It mutates privileged processor state only for the duration of the firmware call. Dependencies include PowerPC SPRs, HSRR return semantics, stack layout constants, TOC conventions, and endian-specific instruction encodings.

### Integration Points
Generated OPAL C wrappers and exported OPAL symbols eventually call this routine to enter firmware. It is also the natural place for OPAL tracing hooks in the wider build.

### Risks
Any stack parameter offset, MSR mask, TOC restore, or endian transition error would corrupt kernel execution after firmware return. Little-endian restoration relies on raw encoded instructions, making assembler/disassembler review important. Firmware calls run with translation disabled according to the prepared MSR.

### Test Signals
Validation should include big- and little-endian boots, simple OPAL token calls, failing/invalid calls, trace-enabled builds, nested call avoidance at higher layers, and stress around interrupts/preemption disabled by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-wrappers.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-xscom.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-xscom.c

### Purpose
`opal-xscom.c` exposes OPAL XSCOM access through debugfs for each chip with a `scom-controller` node.

### Important APIs, Types, And Functions
Important functions are `opal_scom_unmangle()`, `opal_scom_read()`, `opal_scom_write()`, `scom_debug_read()`, `scom_debug_write()`, `scom_debug_init_one()`, and `scom_debug_init()`. `struct scom_debug_entry` records chip ID, device path blob, and debugfs name.

### Control Flow
Initialization checks for OPAL firmware, creates debugfs `scom`, scans nodes with `scom-controller`, derives chip IDs, and creates a per-chip directory containing `devspec` and `access`. Reads and writes require 8-byte-aligned offsets/counts, translate file offsets into SCOM register numbers, unmangle debugfs indirect-address bits, and call `opal_xscom_read()` or `opal_xscom_write()`.

### State, Persistence, And Dependencies
State consists of debugfs entries and per-chip metadata. Register effects persist in hardware/firmware. Dependencies include OF chip IDs, OPAL XSCOM calls, debugfs, user-copy helpers, and address bit conventions for indirect SCOM.

### Integration Points
The file is a device initcall and provides operator diagnostics rather than a normal driver API. `opal-prd.c` also exposes XSCOM through PRD ioctls for daemon use.

### Risks
Debugfs gives privileged raw register access and can destabilize hardware. `scom_debug_write()` increments `done` but does not advance `*ppos`, unlike reads. Address unmangling is specialized to debugfs offset limitations and can be misunderstood by users.

### Test Signals
Test aligned and unaligned reads/writes, indirect address bit mangling, missing OPAL feature, chip ID failures, user-copy errors, OPAL read/write failures, multiple chip directories, and write offset progression expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-xscom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci-ioda-tce.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci-ioda-tce.c

### Purpose
`pci-ioda-tce.c` manages IODA2 TCE table allocation, multi-level lookup, build/free/exchange operations, userspace table copies, and links between IOMMU tables and PowerNV PE table groups.

### Important APIs, Types, And Functions
Important functions are `pnv_ioda_parse_tce_sizes()`, `pnv_pci_setup_iommu_table()`, `pnv_tce()`, `pnv_tce_build()`, `pnv_tce_xchg()`, `pnv_tce_useraddrptr()`, `pnv_tce_free()`, `pnv_tce_get()`, `pnv_pci_ioda2_table_alloc_pages()`, `pnv_pci_ioda2_table_free_pages()`, `pnv_pci_link_table_and_group()`, and `pnv_pci_unlink_table_and_group()`.

### Control Flow
Supported page sizes are read from `ibm,supported-tce-sizes`, with defaults based on CPU generation. Table allocation validates levels and power-of-two window size, computes per-level table sizes, allocates zeroed pages, optionally allocates a userspace mirror, and initializes `struct iommu_table`. `pnv_tce()` walks indirect levels, allocating lower levels atomically with `cmpxchg()` when requested. Build writes permission and real page number TCEs, free clears entries and skips missing lower levels, exchange atomically swaps one TCE, and free recursively releases allocated levels.

### State, Persistence, And Dependencies
State lives in `struct iommu_table`: base, offset, size, page shift, indirect level count, userspace mirror, NUMA node, and RCU-linked table groups. Hardware-visible persistence is the TCE table memory mapped into OPAL/PHB DMA windows by `pci-ioda.c`. Dependencies include PowerNV IOMMU constants, TCE permission helpers, OF properties, page allocator, RCU list links, and `iommu_tce_table_get/put()`.

### Integration Points
`pci-ioda.c` uses these helpers to create default and VFIO/userspace DMA windows, install table ops, invalidate PHB TCE caches after mutations, and manage table group ownership.

### Risks
Multi-level allocation uses `GFP_ATOMIC`, so memory pressure can fail DMA mapping. The direct allocation helper's partial-allocation handling is subtle for multi-level tables. Link/unlink functions assume matching table/group references and warn if not found. TCE entries encode pointers with read/write bits, so masking must be exact during recursive free and traversal.

### Test Signals
Test page-size property parsing, invalid levels/window sizes, single- and multi-level table allocation, userspace-copy allocation failure, concurrent lower-level allocation, build/free/xchg/get behavior, recursive free, RCU table/group linking, and VFIO table-size accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci-ioda-tce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci-ioda.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci-ioda.c

### Purpose
`pci-ioda.c` is the main PowerNV IODA PHB implementation. It initializes PHBs, allocates and configures partitionable endpoints (PEs), maps MMIO segments, sets up DMA/IOMMU windows and bypass, creates MSI domains, handles PE freeze/unfreeze for EEH, integrates hotplug/release, and configures IODA2/NPU OpenCAPI controller operations.

### Important APIs, Types, And Functions
Important APIs include `pnv_ioda_alloc_pe()`, `pnv_ioda_free_pe()`, `pnv_ioda_configure_pe()`, `pnv_ioda_deconfigure_pe()`, `pnv_pci_bdfn_to_pe()`, `pnv_ioda_get_pe()`, `pnv_pci_ioda2_setup_dma_pe()`, `pnv_pci_ioda2_release_pe_dma()`, `pnv_opal_pci_msi_eoi()`, `is_pnv_opal_msi()`, `pnv_pci_init_ioda2_phb()`, and `pnv_pci_init_npu2_opencapi_phb()`. Core internal paths cover M64 parsing, PE setup for devices/buses, PELTV setup, TCE invalidation, IOMMU table group ops, MSI allocation/composition, resource alignment/fixups, and PHB shutdown.

### Control Flow
PHB initialization reads OPAL PHB IDs, allocates `pci_controller`/`pnv_phb`, parses bus/MMIO resources, maps registers, derives PE counts and reserved/root PEs, parses M64 windows, allocates PE/segment arrays, installs PCI/controller hooks, initializes MSI domains, resets IODA tables, optionally resets PHBs for kdump/forced reset, configures M64, and creates dynamic PCI nodes. During device setup, buses or devices are associated with PEs, OPAL `opal_pci_set_pe()` maps RIDs, PELTV tables connect child/parent error domains, MMIO segments are mapped to PEs, and non-bridge devices trigger DMA setup. DMA setup creates a default 32-bit TCE table, maps it through OPAL, optionally enables 64-bit bypass, registers IOMMU groups, and supports VFIO ownership transfer. MSI setup allocates hwirqs from a bitmap, maps them through a parent IRQ domain, asks OPAL for MSI address/data, and performs PHB3 EOI through OPAL.

### State, Persistence, And Dependencies
`struct pnv_phb` persists PHB model/type, OPAL ID, register mapping, diagnostic buffer, MSI bitmap, PE arrays, segment maps, reverse RID map, and controller callbacks. `struct pnv_ioda_pe` persists PE ownership, device/bus/VF association, table group, bypass base/state, MVE number, DMA setup state, and compound PE links. Firmware persists IODA tables, MMIO BAR windows, TVE/TCE mappings, freeze state, and XIVE/PE assignments. Dependencies include OPAL PCI calls, generic PCI core hooks, EEH, IOMMU/VFIO APIs, MSI domains, OF resources, debugfs, memblock memory size, and TCE helpers from `pci-ioda-tce.c`.

### Integration Points
`pci.c` discovers IODA-compatible PHB nodes and calls the init entry points. `pci-sriov.c` shares PE allocation and M64 state for VF setup. `pci.h` defines the shared structures. KVM uses `pnv_opal_pci_msi_eoi()` for passthrough interrupts. EEH paths call freeze/unfreeze/get-state callbacks, and generic PCI DMA hooks call the controller ops installed here.

### Risks
This file has high coupling between Linux resource assignment, OPAL IODA state, and hardware PE segmentation. PE allocation/release must keep bitmaps, lists, reverse maps, device counts, DMA windows, and PELTV entries balanced across hotplug and EEH recovery. M64 alignment and segment ownership are easy to break. TCE invalidation differs between PHB3 MMIO register and OPAL kill calls. VFIO ownership transfer must disable bypass and remove default windows without leaving stale device table bases. Several failure comments note unresolved "what do we do here" cases after PE configuration failures.

### Test Signals
Test PHB DT parsing for IODA2/IODA3/NPU, kdump and forced PHB reset, root/reserved PE allocation, bus/device PE setup, compound PE M64 selection, PELTV parent/slave behavior, MMIO segment mapping, DMA table creation failure, bypass enable/disable and 64-bit workaround, TCE invalidation paths, MSI allocation/free/compose/EOI, hotplug release and re-add, EEH frozen-state recovery, debugfs diag/PE dumps, VFIO ownership transfer, and shutdown IODA reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci-ioda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci-sriov.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci-sriov.c

### Purpose
`pci-sriov.c` adds PowerNV-specific SR-IOV support by reshaping VF BAR resources, allocating one PE per VF, programming M64 windows, shifting VF BARs to match allocated PE numbers, and tearing everything down on disable.

### Important APIs, Types, And Functions
Public hooks are `pnv_pci_ioda_fixup_iov()`, `pnv_pci_iov_resource_alignment()`, `pnv_pcibios_sriov_enable()`, and `pnv_pcibios_sriov_disable()`. Internal helpers include `pnv_pci_ioda_fixup_iov_resources()`, `pnv_pci_vf_assign_m64()`, `pnv_ioda_map_m64_segmented()`, `pnv_ioda_map_m64_single()`, `pnv_pci_vf_resource_shift()`, `pnv_ioda_setup_vf_PE()`, and `pnv_ioda_release_vf_PE()`.

### Control Flow
PF fixup allocates `struct pnv_iov_data`, rejects unsupported non-M64 VF BARs, expands segmented VF BAR resources to `vf_bar_size * total_pe_num`, and records single-window mode for very large VF BARs. Resource alignment returns the expanded size for segmented windows. Enabling SR-IOV verifies IODA2-style PHB support, allocates a contiguous PE range, programs segmented or single M64 windows for each VF BAR, shifts BAR resources by the base PE when needed, configures each VF PE/RID, links VF PDNs, and sets up DMA for each VF PE. Disabling releases VF PEs/DMA, unshifts resources, disables used M64 windows, and removes VF PDNs.

### State, Persistence, And Dependencies
State is stored in `pdev->dev.archdata.iov_data`: number of VFs, contiguous PE array, per-BAR single-mode flags, shift flag, used M64 BAR bitmap, and reserved hole resources. Firmware persists M64 BAR programming and PE/RID mappings. Dependencies include the generic PCI SR-IOV hooks, PowerNV PE allocation/configuration, OPAL M64 MMIO calls, PCI resource management, and IODA2 DMA setup.

### Integration Points
`pci-ioda.c` installs these hooks in `ppc_md` when `CONFIG_PCI_IOV` is enabled. VF `pcibios_device_add()` fixups attach created VF `pci_dev`s back to their preallocated PEs.

### Risks
The order of arguments in the single-mode call site must match `pnv_ioda_map_m64_single(phb, pe_num, window_id, start, size)`; confusing PE and window IDs would map the wrong hardware target. BAR shifting creates reserved holes and must be fully undone. Enable failure paths must free contiguous PE runs and M64 windows. The design only supports M64 VF BARs and IODA2-style OPAL APIs, so 32-bit/non-prefetchable VF BARs disable IOV resources.

### Test Signals
Test PFs with unsupported VF BAR flags, small segmented BARs, large single-mode BARs, M64 window exhaustion, contiguous PE allocation failure, BAR shift bounds and hole reservation, enable failure unwinding at each stage, VF PDN association, DMA setup per VF, disable cleanup, and repeated enable/disable cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci-sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci.c

### Purpose
`pci.c` contains generic PowerNV PCI support shared by PHB implementations: slot/power helper exports, OPAL config-space access, EEH checks around config operations, PHB diagnostic data printing, controller shutdown, and platform PCI discovery.

### Important APIs, Types, And Functions
Exported functions include `pnv_pci_get_slot_id()`, `pnv_pci_get_device_tree()`, `pnv_pci_get_presence_state()`, `pnv_pci_get_power_state()`, `pnv_pci_set_power_state()`, `pnv_pci_dump_phb_diag_data()`, `pnv_pci_cfg_read()`, `pnv_pci_cfg_write()`, `pnv_pci_table_alloc()`, `pnv_pci_shutdown()`, and `pnv_pci_init()`. The file defines global `struct pci_ops pnv_pci_ops`.

### Control Flow
Slot helpers derive OPAL slot IDs from PHB DT nodes and BDFN or call OPAL for device tree/presence/power state. Config reads/writes translate `pci_dn` to OPAL PHB ID and BDFN, call byte/halfword/word OPAL config functions, and return PCI BIOS status. When EEH is enabled, reads detect all-ones failure values and call EEH failure checks; otherwise both reads/writes probe and clear OPAL frozen state when needed. Diagnostic printers decode P7IOC, PHB3, and PHB4 OPAL diagnostic structures and compact repeated PEST entries. `pnv_pci_init()` disables PCIe port services, initializes all compatible IODA/NPU PHBs, and installs IOMMU DMA ops.

### State, Persistence, And Dependencies
This file has little private state; it allocates IOMMU table structures and uses global hose lists/controller ops. Persistent state is in PHB firmware, PCI device state, and EEH status. Dependencies include OPAL PCI calls, PowerPC PCI DN structures, EEH, MSI/IOMMU headers, PHB-specific init functions, and generic PCI core flags.

### Integration Points
`powernv.h` declares `pnv_pci_init()` and `pnv_pci_shutdown()`. `pci-ioda.c` provides PHB-specific init and controller operations. External drivers can use exported slot and power-state helpers.

### Risks
Config read failures return all-ones values while still reporting `PCIBIOS_SUCCESSFUL`, relying on EEH/failure detection at higher layers. Power-state set returns `1` when an async message is copied, not just boolean success. Diagnostic printing must match firmware structure versions. PCIe port services are globally disabled due to platform/firmware assumptions.

### Test Signals
Test slot ID derivation for standard and NPU PHBs, missing OPAL tokens, async power-state setting, config accesses of all sizes, EEH frozen-state clearing, diagnostic buffer printing for each ioType, IOMMU table allocation initialization, PHB shutdown callbacks, and PCI init discovery of IODA2/IODA3/OpenCAPI nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci.h

### Purpose
`pci.h` is the private PowerNV PCI/IODA header. It defines PHB and PE data structures, PE flag semantics, SR-IOV state, shared helper macros, and cross-file prototypes for `pci.c`, `pci-ioda.c`, `pci-ioda-tce.c`, EEH, and SR-IOV code.

### Important APIs, Types, And Functions
Important definitions include `enum pnv_phb_type`, `enum pnv_phb_model`, PE flags such as `PNV_IODA_PE_DEV`, `PNV_IODA_PE_BUS_ALL`, `PNV_IODA_PE_MASTER`, and `PNV_IODA_PE_VF`, `struct pnv_ioda_pe`, `struct pnv_phb`, optional `struct pnv_iov_data`, `pnv_pci_is_m64()`, `pnv_pci_is_m64_flags()`, PE logging macros, IOMMU level constants, and declarations for PE, DMA, TCE, PHB init, SR-IOV, and EEH helpers.

### Control Flow
As a header it has no runtime control flow, but it defines the contracts used by source files. `pci-ioda.c` mutates `pnv_phb.ioda` state across init, PE allocation, DMA setup, and release. `pci-sriov.c` uses `pnv_iov_data` stored in `pdev->dev.archdata.iov_data`. `pci-ioda-tce.c` implements the TCE prototypes declared here.

### State, Persistence, And Dependencies
`struct pnv_phb` persists controller, OPAL ID, register mapping, MSI bitmap, diagnostic buffer, PE arrays, segment maps, reverse maps, and callback pointers. `struct pnv_ioda_pe` persists PE association and IOMMU group/table state. Dependencies include Linux IOMMU, MSI bitmap, PCI resource structures, and PowerPC PCI controller objects.

### Integration Points
All PowerNV PCI implementation files in this group include this header. It is not a public UAPI but is the internal ABI between PHB initialization, config access, DMA/TCE management, EEH, and SR-IOV support.

### Risks
Structure fields encode invariants not enforced by the type system: exactly one of device/bus/VF ownership, balanced `device_count`, valid PE reverse maps, consistent segment maps, and stable table group references. `pnv_pci_is_m64()` intentionally tests addresses rather than flags because PCI allocation can place 64-bit BARs in 32-bit windows.

### Test Signals
Compile coverage across `CONFIG_PCI_IOV`, `CONFIG_IOMMU_API`, and debugfs variants is important. Runtime tests should validate PE flags, M64 detection by address, SR-IOV archdata lifetime, table group declarations, and cross-file prototypes after API changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/powernv.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/powernv.h

### Purpose
`powernv.h` is a local platform header for PowerNV internals that need to be shared across architecture files without becoming general public API.

### Important APIs, Types, And Functions
It includes `<asm/powernv.h>` and declares or stubs `pnv_smp_init()`, `pnv_platform_error_reboot()`, `pnv_pci_init()`, `pnv_pci_shutdown()`, `pnv_get_supported_cpuidle_states()`, `pnv_lpc_init()`, `opal_handle_events()`, `opal_have_pending_events()`, `opal_event_shutdown()`, `cpu_core_split_required()`, memcons helpers, and `pnv_rng_init()`.

### Control Flow
The header has no runtime flow. Conditional compilation provides no-op PCI/SMP functions when those subsystems are disabled, allowing common platform code to call them unconditionally.

### State, Persistence, And Dependencies
It declares access to state owned by other files, such as OPAL event state, PCI controller state, and memcons pointers. Dependencies include PowerPC platform types, `struct pt_regs`, `struct device_node`, and `struct memcons` forward declarations.

### Integration Points
`opal-irqchip.c`, `opal-msglog.c`, and other PowerNV platform files include this header for cross-file prototypes. The declarations connect platform init/shutdown, OPAL event polling, PCI setup, LPC setup, and memory console helpers.

### Risks
Because this is an internal header, prototype drift can silently affect multiple architecture files at once. Stubbed functions must preserve call-site expectations when optional configs are disabled.

### Test Signals
Build matrix coverage with and without `CONFIG_SMP` and `CONFIG_PCI` is the main signal. Runtime checks should confirm callers tolerate stubbed PCI/SMP paths and that OPAL event/memcons declarations match their implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/powernv.h -->
