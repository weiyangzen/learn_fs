# Research: subset-b-005208

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_ftp.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_ftp.h

**Purpose:** This header defines the common HMC drive FTP service contract used by the s390 HMC DVD access stack. It is not a transport implementation; it supplies the command IDs, request descriptor, path-length limit, and public entry points that higher-level cache/device code and lower-level FTP backends share.

**Important APIs and types:** `HMCDRV_FTP_FIDENT_MAX` limits null-terminated file identifiers to 192 bytes. `enum hmcdrv_ftp_cmdid` covers probe/no-op, read, write, append, long directory listing, name listing, delete, and cancel. `struct hmcdrv_ftp_cmdspec` carries command ID, file offset, ASCII filename, kernel transfer buffer, and byte count. Exported prototypes are `hmcdrv_ftp_startup()`, `hmcdrv_ftp_shutdown()`, `hmcdrv_ftp_probe()`, `hmcdrv_ftp_do()`, and user-facing `hmcdrv_ftp_cmd()`.

**Control flow, state, and persistence:** The header is stateless, but its descriptor defines the transactional unit for HMC file operations. Callers must provide a kernel buffer that satisfies the backend alignment expectations documented here, especially the 4 KiB alignment note for `buf`.

**Dependencies and integration:** It depends only on Linux scalar types and is included by `hmcdrv_mod.c` and `sclp_ftp.c`. The command set maps directly onto SCLP Diagnostic Test FTP in the LPAR backend.

**Risks and test signals:** Main risks are ABI mismatch between cache/device layers and the selected backend, filename truncation, unaligned buffers, and incorrect interpretation of transfer lengths versus file size. Useful tests include probe/no-op on supported and unsupported machines, boundary-length filenames, zero-length transfers, offset reads, and all command IDs returning expected errno mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_ftp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_mod.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_mod.c

**Purpose:** This is the module wrapper for HMC drive DVD access. It wires the FTP transport, cache layer, and character/block-like device facade into a single loadable module.

**Important APIs and functions:** The module parameter `cachesize` is stored in `hmcdrv_mod_cachesize` and defaults to `HMCDRV_CACHE_SIZE_DFLT`. `hmcdrv_mod_init()` probes the FTP backend without cache, starts the cache with the selected size, and finally initializes the exported device. `hmcdrv_mod_exit()` tears down the device and cache in reverse order.

**Control flow, state, and persistence:** Initialization is deliberately staged. A failed `hmcdrv_ftp_probe()` aborts without allocating cache state. A failed cache startup aborts before device exposure. A failed device init shuts the cache down. Persistent module state is limited to the cache size parameter; operational state lives in the cache, device, and FTP layers.

**Dependencies and integration:** It includes `hmcdrv_ftp.h`, `hmcdrv_dev.h`, and `hmcdrv_cache.h`. The module metadata identifies it as "HMC drive DVD access".

**Risks and test signals:** Risk centers on cleanup ordering and partial initialization. The file correctly avoids device exposure before the backend and cache exist, but tests should verify load failure paths, cache-size validation in the cache layer, `hmcdrv_dev_init()` failure cleanup, repeated load/unload, unsupported backend probe failure, and absence of stale device nodes after unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/keyboard.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/keyboard.c

**Purpose:** This file implements EBCDIC keycode handling for s390 console drivers. It clones the default EBCDIC keymaps/function strings per keyboard instance, translates keycodes into tty input, supports dead-key composition, handles Magic SysRq sequences, and implements a subset of VT keyboard ioctls.

**Important APIs and functions:** Public exports are `kbd_alloc()`, `kbd_free()`, `kbd_ascebc()`, `kbd_keycode()`, and `kbd_ioctl()`. Key handlers include `k_self()`, `k_dead()`, `k_fn()`, `k_spec()`, and `to_utf8()`. The ioctl helpers `do_kdsk_ioctl()` and `do_kdgkb_ioctl()` service keymap and function-string get/set commands.

**Control flow, state, and persistence:** `kbd_alloc()` deep-copies global EBCDIC maps, function tables, and accent table into `struct kbd_data`; later ioctl writes mutate only that instance. `kbd_keycode()` chooses one of maps 0, 1, 4, or 5 based on the keycode range, normalizes `KT_LETTER` to latin, interprets SysRq prefix state, dispatches key handlers, or emits UTF-8 for direct Unicode keysyms. Dead-key state is stored in `kbd->diacr` until the next character.

**Dependencies and integration:** It integrates with tty flip buffers via helpers in `keyboard.h`, Linux keyboard symbols, console maps, sysrq, and uaccess. Consumers attach `kbd_data->port` to the target tty port.

**Risks and test signals:** Risks include keymap bounds errors, racy tty ownership permission checks, missing null map handling for unexpected keycode ranges, incorrect `KBD_NR_TYPES` validation, and user-copy failures leaving partial ioctl changes. Test signals include default EBCDIC-to-ASCII mapping, dead-key combinations, function-key strings, SysRq prefix handling, ioctl permission checks, map allocation/free paths, and Unicode keysyms above 8 bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/keyboard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/keyboard.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/keyboard.h

**Purpose:** This header declares the s390 EBCDIC keyboard helper interface used by console and terminal drivers. It defines the instance state that connects key translation to a tty port and exposes the global default maps supplied elsewhere.

**Important APIs and types:** `struct kbd_data` stores a `tty_port`, per-instance key maps, function table, special function handlers, accent table, active diacritic, and SysRq state. Public functions are `kbd_alloc()`, `kbd_free()`, `kbd_ascebc()`, `kbd_keycode()`, and `kbd_ioctl()`. Inline helpers `kbd_put_queue()` and `kbd_puts_queue()` insert characters into the tty flip buffer and push immediately.

**Control flow, state, and persistence:** The header makes `struct kbd_data` the persistent per-console state object. The global `ebc_*` externs are templates; `keyboard.c` copies them so ioctls can mutate an instance without changing global defaults.

**Dependencies and integration:** It depends on tty, tty flip buffers, Linux keyboard definitions, and diacritic structures. The `MAX_NR_FUNC`, `MAX_NR_KEYMAPS`, and `NR_KEYS` constants are inherited from the kernel keyboard layer.

**Risks and test signals:** The main risks are consumers failing to initialize `kbd_data->port`, using handlers beyond `NR_FN_HANDLER`, or assuming the inline queue helpers batch output. Test signals are successful allocation, keycode delivery to the attached tty port, ioctl visibility of cloned maps, and clean free of all nested allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/keyboard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/monreader.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/monreader.c

**Purpose:** `monreader.c` provides `/dev/monreader`, a misc character device for reading z/VM `*MONITOR` records from a shared DCSS segment via IUCV messages.

**Important APIs and functions:** Core types are `struct mon_msg` for queued IUCV monitor messages and `struct mon_private` for one opener's ring state. File operations are `mon_open()`, `mon_close()`, `mon_read()`, and `mon_poll()`. IUCV callbacks are `mon_iucv_path_complete()`, `mon_iucv_path_severed()`, and `mon_iucv_message_pending()`. Helpers validate monitor control areas using `mon_check_mca()` and acknowledge records through `mon_send_reply()`.

**Control flow, state, and persistence:** Module init requires z/VM, registers the IUCV handler, validates that the configured `mondcss` segment is shared code, loads it, converts the DCSS name to EBCDIC, and finally registers the misc device. Only one opener is allowed via `mon_in_use`. Incoming IUCV messages fill a 255-entry ring. `read()` first emits the 12-byte monitor control element, then the referenced records from the DCSS, advancing MCA offsets and replying when complete. Message-limit overflow is reported as `-EOVERFLOW` after the limit record is acknowledged.

**Dependencies and integration:** It depends on z/VM IUCV, DCSS extmem APIs, EBCDIC conversion, wait queues, miscdevice, and user-copy helpers.

**Risks and test signals:** Risks include malformed MCA pointers into the shared segment, races in the ring counters, blocking open waiting for connection confirmation, and correct reply accounting when the queue is full. Tests should cover non-z/VM load refusal, invalid DCSS type, single-open exclusion, poll readiness, nonblocking reads, disconnect handling, overflow, and partial reads across MCA and record boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/monreader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/monwriter.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/monwriter.c

**Purpose:** `monwriter.c` exposes `/dev/monwriter`, allowing user space to submit z/VM APPLDATA monitor records through the `appldata_asm()` diagnose interface.

**Important APIs and functions:** `struct mon_buf` stores an active APPLDATA record buffer and its header. `struct mon_private` stores write parsing state for one file descriptor. `monwrite_diag()` builds `appldata_product_id` and parameter-list structures and issues the monitor command. `monwrite_new_hdr()` validates and allocates or finds records; `monwrite_new_data()` starts interval/config records or emits one-shot events.

**Control flow, state, and persistence:** Each write stream is parsed as repeated `struct monwrite_hdr` followed by `datalen` bytes. Partial writes are supported through `hdr_to_read` and `data_to_read`. Interval and config records persist in the descriptor list and consume global `mon_buf_count` capacity until stopped or file close. Event records are sent and immediately freed. `monwrite_close()` stops remaining non-event records and releases all buffers.

**Dependencies and integration:** The driver is z/VM-only, uses miscdevice registration, per-file mutex serialization, `asm/appldata.h`, `asm/monwriter.h`, DMA-capable record data allocations, and Linux user-copy APIs.

**Risks and test signals:** Risks include the global `mon_buf_count` being updated without a global lock across file descriptors, diagnostic errors mapped only coarsely, partial write errors resetting parser state, and ensuring stop records find matching interval/config records. Test signals include fragmented header/data writes, invalid header lengths/functions, max buffer exhaustion, close-time stop calls, event freeing, concurrent writers, and z/VM gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/monwriter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/raw3270.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/raw3270.c

**Purpose:** This is the core IBM 3270 ccw-device driver. It manages 3270 device discovery, request queuing, sizing/reset, active view selection, sysfs attributes, and notifier callbacks for higher-level 3270 console/tty/fs views.

**Important APIs and functions:** Exported request helpers include `raw3270_request_alloc/free/reset()`, `raw3270_request_set_cmd()`, `raw3270_request_add_data()`, `raw3270_request_set_data()`, and `raw3270_request_set_idal()`. View APIs include `raw3270_add_view()`, `raw3270_del_view()`, `raw3270_activate_view()`, `raw3270_deactivate_view()`, `raw3270_start*()`, `raw3270_reset()`, `raw3270_find_view()`, and notifier registration. `raw3270_irq()` is the central ccw interrupt handler.

**Control flow, state, and persistence:** Each `struct raw3270` owns a ccw device, minor, geometry, request queue, view list, active view, init view, and sizing requests. The state machine runs `INIT -> RESET -> W4ATTN -> READMOD -> READY`, or uses VM diagnose calls for geometry. Requests are queued under the ccw-device lock; completions invoke the view interrupt handler, remove finished requests, run callbacks, and start the next request. Device online creates the raw3270 object, sysfs attributes, reset/sizing flow, and notifier events. Removal deactivates and deletes views, notifies destroy, resets, and frees.

**Dependencies and integration:** It integrates with the s390 ccw bus, CIO interrupt model, diag8c/diag210 under VM, the `class3270` device class, sysfs attributes `model`, `rows`, and `columns`, and optional TN3270 console setup.

**Risks and test signals:** Risks include lifetime/refcount mistakes between queued requests and views, busy/intervention-required recovery, reset races, minor allocation gaps, and activation fallback when a view fails. Tests should exercise online/offline, request callback ordering, view add/delete under active I/O, console early setup, geometry detection paths, sysfs attributes, notifier replay, and disconnected-device reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/raw3270.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/raw3270.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/raw3270.h

**Purpose:** This header defines the internal public API for 3270 view drivers. It abstracts ccw request construction, view lifecycle, active-view checks, console setup hooks, and device create/destroy notifications.

**Important APIs and types:** `struct raw3270_request` wraps a ccw1, output buffer, residual count, return code, callback, and owning view. `struct raw3270_fn` is the view vtable with `activate`, `deactivate`, `intv`, `release`, `free`, and `resize`. `struct raw3270_view` stores the owning device, refcount, lock, model/rows/cols, and ASCII-to-EBCDIC table. `raw3270_notifier` reports minors to clients that create per-device views.

**Control flow, state, and persistence:** Views persist until `raw3270_del_view()` drops the refcount and calls the view free hook. Requests must not be reset while on a list; the inline `raw3270_request_final()` treats `-EACCES`, `-ENODEV`, and `-EIO` as final. `raw3270_get_view()` and `raw3270_put_view()` manage asynchronous request ownership through a shared wait queue.

**Dependencies and integration:** It depends on ccw structures, IDAL buffers, `struct irb`, s390 3270 ioctl definitions, and Linux wait queues. Higher-level 3270 tty/console/fs drivers include it.

**Risks and test signals:** Risks are API misuse: starting requests on inactive views, freeing requests still queued, not balancing view references, or not implementing mandatory vtable methods. Test signals include refcount reaching zero on delete, wakeups on request completion, callback status mapping, and resize notifications reaching all views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/raw3270.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp.c

**Purpose:** `sclp.c` is the central Service Call Logical Processor core. It serializes SCLP service calls, manages event masks, dispatches incoming event buffers, supports synchronous waiting during early/console contexts, and exposes console-related driver attributes.

**Important APIs and functions:** Public APIs are `sclp_add_request()`, `sclp_sync_wait()`, `sclp_register()`, `sclp_unregister()`, `sclp_remove_processed()`, `sclp_deactivate()`, `sclp_reactivate()`, and `sclp_init()`. Internal state machines track running request state, read-event state, activation state, and mask-initialization state. `sclp_interrupt_handler()` completes service-call requests and queues read-event requests when pending events exist.

**Control flow, state, and persistence:** Requests are appended to `sclp_req_queue` under `sclp_lock`, optionally with queue timeouts. Only one command is active at a time through `active_cmd` and `sclp_running_state`. Interrupts locate the completed request by physical SCCB address, mark it done, call its callback outside the lock, then process the next queued request. Event readers are synthetic read-event requests whose callback dispatches event buffers to registered `struct sclp_register` listeners. Registration recalculates masks and issues Write Event Mask commands.

**Dependencies and integration:** This file integrates with external IRQ subclass `EXT_IRQ_SERVICE_SIG`, s390 `servc`, debugfs-style debug areas, timers, reboot notifiers, and the platform driver named `sclp`. It is the shared backend for console, tty, PCI/AP/CPU/memory configuration, OCF, SD/SDIAS, FTP, and control interfaces.

**Risks and test signals:** Risks include request timeout recovery, callback reentrancy, mask collision handling, malformed event-buffer lengths, synchronous waits with timer interrupts disabled, and deactivation during reboot. Test signals include successful initialization, mask compatibility fallback, event delivery to only registered receivers, queue timeout callbacks, reboot mask reset, sysfs `con_*` attributes, and stress with concurrent request producers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp.h

**Purpose:** `sclp.h` is the shared SCLP internal ABI for s390 character and platform code. It defines event types, command words, SCCB layouts, request and registration structures, early-console hooks, and helper functions for masks and GDS parsing.

**Important APIs and types:** Key structures are `init_sccb`, `read_cpu_info_sccb`, `read_info_sccb`, `read_storage_sccb`, `sclp_req`, and `sclp_register`. Macros define event masks such as `EVTYP_MSG_MASK`, `EVTYP_DIAG_TEST_MASK`, `EVTYP_STORE_DATA_MASK`, and command words such as `SCLP_CMDW_READ_SCP_INFO`, `SCLP_CMDW_WRITE_EVENT_DATA`, and `SCLP_CMDW_WRITE_EVENT_MASK`. Inline helpers read/write variable-length event masks, issue `sclp_service_call()`, translate ASCII/EBCDIC by environment, and find GDS vectors/subvectors.

**Control flow, state, and persistence:** `struct sclp_req` is the persistent request object while queued/running and carries status, callback, SCCB pointer, and timeout fields. `struct sclp_register` is the persistent event registration object used to compute send/receive masks and dispatch inbound events.

**Dependencies and integration:** It depends on Linux list/types and s390 machine, SCLP, EBCDIC, and assembly exception-table definitions. The global `sclp` capability object is populated by early SCLP discovery.

**Risks and test signals:** Risks are layout drift from hardware SCCB specs, endian/packing mistakes, mask-length compatibility issues, and unvalidated GDS vector lengths in callers. Tests should validate service-call condition-code mapping, mask helpers with 4-byte and 8-byte masks, CPU/storage info parsing, and GDS traversal with malformed lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ap.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ap.c

**Purpose:** This file provides SCLP helpers to configure and deconfigure s390 AP crypto adapters.

**Important APIs and functions:** Exported functions are `sclp_ap_configure(u32 apid)` and `sclp_ap_deconfigure(u32 apid)`. Both call `do_ap_configure()` with command words `SCLP_CMDW_CONFIGURE_AP` or `SCLP_CMDW_DECONFIGURE_AP`. `struct ap_cfg_sccb` contains only the SCCB header.

**Control flow, state, and persistence:** The operation first checks `SCLP_HAS_AP_RECONFIG`, allocates one DMA-capable zero page for the SCCB, encodes the AP ID into bits 8..15 of the command word, and sends a synchronous SCLP request. Accepted response codes are `0x0020`, `0x0120`, `0x0440`, and `0x0450`; other responses become `-EIO`. No state is persisted after the request.

**Dependencies and integration:** It uses the SCLP core synchronous request API and exports symbols for AP bus or crypto reconfiguration code. It depends on the facility bits discovered in `sclp.facilities`.

**Risks and test signals:** Risks include AP IDs wider than 8 bits being truncated by `(apid & 0xff) << 8`, facility bit mismatch, and response-code changes not reflected in the accepted list. Test signals are configure/deconfigure success, unsupported facility returning `-EOPNOTSUPP`, simulated nonaccepted response warning, and memory allocation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cmd.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cmd.c

**Purpose:** `sclp_cmd.c` contains synchronous command helpers for CPU core and channel-path information/reconfiguration.

**Important APIs and functions:** `sclp_sync_request()` and `sclp_sync_request_timeout()` allocate a `struct sclp_req`, install a completion callback, submit through `sclp_add_request()`, and wait. `_sclp_get_core_info()` reads CPU/core information. `sclp_core_configure()` and `sclp_core_deconfigure()` issue CPU configure command words. `sclp_chp_configure()`, `sclp_chp_deconfigure()`, and `sclp_chp_read_info()` manage channel paths.

**Control flow, state, and persistence:** All commands use transient DMA-capable SCCBs and block until callback completion. CPU info chooses extended SCCB length when facility 140 is available. Configure commands check capability bits before allocation, submit the command, validate hardware response codes, and free the SCCB. No durable state is stored here; callers own resulting core/channel-path info.

**Dependencies and integration:** It depends on the SCLP queue, completion API, s390 facility detection, channel-path IDs, and `sclp_fill_core_info()` from `sclp.h`. These functions are used by CPU hotplug and channel subsystem management.

**Risks and test signals:** Risks include synchronous waits hanging if the SCLP core never completes, response-code lists becoming stale, incorrect SCCB length under facility 140, and queue-timeout behavior during reboot or hotplug. Tests should cover unsupported capability bits, successful info parsing, configure/deconfigure accepted responses, queue timeout returning failed status, and memory allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_con.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_con.c

**Purpose:** This file implements the SCLP line-mode console used for printk output through the SCLP message interface.

**Important APIs and functions:** It registers a `struct console` named `ttyS` with `sclp_console_write()` and `sclp_console_device()`. Internal helpers manage page-backed `struct sclp_buffer` objects: `sclp_conbuf_emit()`, `sclp_conbuf_callback()`, `sclp_console_sync_queue()`, and `sclp_console_drop_buffer()`. `sclp_console_notify()` flushes output on panic and reboot.

**Control flow, state, and persistence:** Init runs at `console_initcall` when SCLP or VT220 console is selected. It initializes the SCLP read/write layer, allocates `sclp_console_pages` DMA pages, sets a delayed flush timer, registers panic/reboot notifiers, and registers the console. Write calls fill the current buffer through `sclp_write()`, emit full buffers, and schedule a 100 ms flush for partial lines. Output queues are serialized by `sclp_con_lock`; one buffer can be in flight while others wait.

**Dependencies and integration:** It depends on `sclp_rw.c`, the global console option macros, `sclp_tty_driver` for console-to-tty binding, panic/reboot notifiers, and SCLP core sync waits.

**Risks and test signals:** Risks include console lock recursion during panic, output loss when `sclp_console_drop` is enabled, blocking waits when no pages are available, and flush ordering across timer and notifier paths. Tests should check boot printk replay, delayed partial-line flush, full queue drop counter `sclp_console_full`, panic/reboot flush, and no registration when SCLP consoles are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_con.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_config.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_config.c

**Purpose:** `sclp_config.c` handles SCLP Configuration Management Data events and exposes an "Open for Business" firmware sysfs write path.

**Important APIs and functions:** The receiver `sclp_conf_receiver_fn()` decodes `struct conf_mgm_data` qualifiers for CPU changes and CPU capability changes. Work items `sclp_cpu_change_work` and `sclp_cpu_capability_work` call `smp_rescan_cpus(false)` or update CPU MHz and emit per-CPU `KOBJ_CHANGE`. `sclp_ofb_send_req()` builds an OFB event buffer and sends it synchronously. The sysfs binary attribute is `/sys/firmware/ofb/event_data`.

**Control flow, state, and persistence:** Init registers the event receiver for send and receive masks, then creates the firmware kset and binary file. Inbound events are handled quickly by scheduling work. Outbound OFB writes are capped at 64 bytes, wrapped in a DMA page SCCB, and serialized by a static mutex.

**Dependencies and integration:** It depends on SCLP event masks, CPU hotplug locks, sysfs/ksets, workqueues, and the SMP CPU rescan path.

**Risks and test signals:** Risks include missing receiver availability for OFB, overlength event data, unhandled event qualifiers, and hotplug work racing with other CPU topology updates. Test signals include receiving CPU-change and capability-change events, sysfs OFB writes with boundary lengths, unsupported send mask warnings, and CPU device uevents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cpi_sys.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cpi_sys.c

**Purpose:** This file implements the SCLP Control Program Identification interface, exposing sysfs knobs and an exported helper for sending system identity data to firmware/HMC.

**Important APIs and functions:** `sclp_cpi_set_data()` is exported for in-kernel callers. Sysfs attributes under `/sys/firmware/cpi/` include `system_name`, `sysplex_name`, `system_type`, `system_level`, and write-only `set`. `cpi_prepare_req()` builds the CPI event SCCB, `cpi_req()` registers the event, submits the request, waits for completion, checks response code `0x0020`, then unregisters.

**Control flow, state, and persistence:** Global identity fields are protected by `sclp_cpi_mutex`. String stores validate length and allowed characters, uppercase and blank-pad to eight bytes, and leave changes in memory until `set` or `sclp_cpi_set_data()` sends them. The request path translates fields to SCLP EBCDIC representation and uses a transient DMA page.

**Dependencies and integration:** It uses SCLP Write Event Data with event type `EVTYP_CTLPROGIDENT`, completion callbacks, firmware ksets, sysfs attributes, EBCDIC conversion, and the SCLP mask registration system.

**Risks and test signals:** Risks include sysfs values not being null-terminated display strings after blank padding, registration overhead on every send, unsupported firmware send mask, and identity validation being stricter than user expectations. Tests should cover valid/invalid characters, newline stripping, level hex parsing, unsupported event type, request status failure, and concurrent sysfs/API updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cpi_sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cpi_sys.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cpi_sys.h

**Purpose:** This header exposes the in-kernel CPI helper for setting and sending SCLP control program identification data.

**Important APIs and types:** The single declaration is `sclp_cpi_set_data(const char *system, const char *sysplex, const char *type, u64 level)`. The strings correspond to the sysfs `system_name`, `sysplex_name`, and `system_type` fields, while `level` is the 64-bit system level sent in the CPI event.

**Control flow, state, and persistence:** The header is stateless. Its function mutates the global CPI identity state in `sclp_cpi_sys.c` and immediately sends a CPI request under that file's mutex.

**Dependencies and integration:** It depends only on `u64` being visible through included kernel types in consumers. In-tree users can avoid sysfs by calling the exported symbol directly.

**Risks and test signals:** Risks are mainly caller-side: passing strings longer than eight accepted characters, invalid characters, or calling before SCLP CPI sysfs initialization on platforms where the event type is unsupported. Test signals are exported symbol resolution, valid identity transmission, and expected `-EINVAL`, `-EOPNOTSUPP`, or `-EIO` return propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cpi_sys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ctl.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ctl.c

**Purpose:** `sclp_ctl.c` provides a restricted misc ioctl interface at `/dev/sclp` for user space to submit selected raw SCCB command words.

**Important APIs and functions:** The only supported ioctl is `SCLP_CTL_SCCB`. `sclp_ctl_sccb_wlist[]` whitelists command words `0x00400002` and `0x00410002`. `sclp_ctl_ioctl_sccb()` copies a small user descriptor, validates the command, copies a page-sized user SCCB into DMA memory, validates the SCCB length field, submits a synchronous request, and copies the returned SCCB bytes back.

**Control flow, state, and persistence:** There is no persistent per-open state. The misc device is registered with `builtin_misc_device()`. Every ioctl allocates a zeroed DMA page and frees it before return.

**Dependencies and integration:** It depends on `asm/sclp_ctl.h` for the user ABI, the SCLP synchronous command API, miscdevice, and uaccess helpers.

**Risks and test signals:** Risks include exposing raw firmware calls, insufficient whitelist coverage or overly broad whitelist additions, user SCCB length validation bugs, and 64-bit user pointer conversion via `u64_to_uptr()`. Tests should cover unsupported command rejection, too-short copied SCCBs, invalid length greater than copied bytes, successful round trip with a mocked/valid command, and fault-injection for copy failures and allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_diag.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_diag.h

**Purpose:** This header defines the Diagnostic Test event-buffer layouts used by the SCLP ET7 FTP service.

**Important APIs and types:** Return flags include `SCLP_DIAG_FTP_OK`, `SCLP_DIAG_FTP_LDFAIL`, `SCLP_DIAG_FTP_LDNPERM`, `SCLP_DIAG_FTP_LDRUNS`, and `SCLP_DIAG_FTP_LDNRUNS`. `SCLP_DIAG_FTP_XPCX` and `SCLP_DIAG_FTP_ROUTE` identify the FTP service. `struct sclp_diag_ftp` contains command, offset, file size, transfer length, buffer address, ASCE, and 256-byte file identifier. `struct sclp_diag_evbuf` wraps model-dependent data by route, and `struct sclp_diag_sccb` wraps the event in an SCCB.

**Control flow, state, and persistence:** The header is stateless, but its packed layouts are copied directly to/from firmware-owned SCCBs. `SCLP_DIAG_FTP_EVBUF_LEN` computes the exact event length used by `sclp_ftp.c`.

**Dependencies and integration:** It depends on Linux types and the SCLP event/SCCB headers included before use. The layout is consumed by `sclp_ftp.c`.

**Risks and test signals:** Risks are hardware ABI drift, packing/alignment mistakes, different filename maximums between this 256-byte field and `HMCDRV_FTP_FIDENT_MAX`, and physical versus virtual buffer address confusion. Tests should validate event length, packed offsets, response flag mapping, and filename boundary handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_early.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_early.c

**Purpose:** `sclp_early.c` consumes early SCLP read-SCP information to populate the global `struct sclp_info sclp`, detect machine facilities, save IPL information, and discover line-mode/VT220 console support before normal drivers are initialized.

**Important APIs and functions:** Exported global `sclp` stores detected capabilities. `sclp_early_detect()` runs facility detection and console detection. `sclp_early_get_ipl_info()` returns saved IPL metadata. `sclp_early_get_core_info()` reads CPU info through early SCLP commands. `sclp_early_adjust_va()` converts the preserved early SCCB pointer to virtual addressing.

**Control flow, state, and persistence:** `sclp_early_facilities_detect()` reads the cached early info SCCB, sets many facility booleans, memory increment size/count, max cores, CPU features of the boot CPU, HSA size, machine type IDs, and load parameter. `sclp_early_detect()` then disables SCLP event notifications and inspects the returned masks to determine available console transports. This state persists in `sclp` for later SCLP users.

**Dependencies and integration:** It depends on early SCLP core helpers, IPL structures, memblock allocation, facility tests, CPU entry layouts, and `sclp_sdias.h` for dump-related integration.

**Risks and test signals:** Risks include reading fields not valid for shorter SCCB variants, wrong fallback between legacy and extended memory fields, console detection affected by mask compatibility mode, and boot CPU matching assumptions. Test signals include facility bits on LPAR and VM, IPL loadparm preservation, memory size values, line-mode/VT220 detection, and early CPU info parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_early.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_early_core.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_early_core.c

**Purpose:** This file implements raw early-boot SCLP command execution, early console printing, event-mask setup, and early read-SCP/storage information helpers before the main interrupt and request-queue infrastructure is available.

**Important APIs and functions:** `sclp_early_cmd()` issues a `servc` and waits for the service-signal interrupt using `sclp_early_wait_irq()`. `sclp_early_set_event_mask()`, `sclp_early_con_check_linemode()`, and `sclp_early_con_check_vt220()` manage early masks. `__sclp_early_printk()`, `sclp_early_printk()`, and `sclp_emergency_printk()` emit line-mode and VT220 messages. `sclp_early_read_info()`, `sclp_early_get_info()`, `sclp_early_get_memsize()`, `sclp_early_get_hsa_size()`, and `sclp_early_read_storage_info()` provide boot discovery data.

**Control flow, state, and persistence:** The preserved `sclp_early_sccb` buffer is reused for all early commands. Read-SCP information is copied into `sclp_info_sccb` once valid. Early printing temporarily enables event masks, writes one or both console formats, then disables masks again. Mask setup retries in 4-byte compatibility mode when response `0x74f0` is returned.

**Dependencies and integration:** It manipulates lowcore PSWs/control registers directly, uses early physical memory constraints, EBCDIC conversion, SCLP message structures from `sclp_rw.h`, and physmem range reporting.

**Risks and test signals:** Risks include waiting for the wrong external interrupt, using a buffer not below 2 GiB/page-aligned, early console output after normal SCLP init has begun, and storage-info failures clearing discovered ranges. Tests should cover forced and normal read-SCP commands, mask compatibility fallback, emergency printing on stopped CPUs, early memory-size calculation, and storage range enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_early_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ftp.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ftp.c

**Purpose:** `sclp_ftp.c` implements the LPAR SCLP Event Type 7 Diagnostic Test FTP transport for HMC drive file operations.

**Important APIs and functions:** Public functions are `sclp_ftp_startup()`, `sclp_ftp_shutdown()`, and `sclp_ftp_cmd()`. `sclp_ftp_et7()` builds and submits the outgoing Diagnostic Test FTP SCCB. `sclp_ftp_txcb()` completes the accepted-write request, while `sclp_ftp_rxcb()` handles the asynchronous ET7 completion event and copies result fields into globals.

**Control flow, state, and persistence:** `sclp_ftp_cmd()` initializes a global receive completion, submits the FTP request, waits for the SCLP command to be accepted, then waits unconditionally for the asynchronous FTP completion event. Result globals store load flag, file size, and transferred length because the incoming event buffer belongs to the SCLP core. Return flags map to byte count, `-EPERM`, `-EBUSY`, `-ENOENT`, or `-EIO`. The header explicitly documents non-reentrancy; callers must serialize.

**Dependencies and integration:** It depends on `hmcdrv_ftp.h`, `sclp_diag.h`, SCLP event registration for `EVTYP_DIAG_TEST`, physical addresses for buffers, and real-space ASCE settings.

**Risks and test signals:** Risks include indefinite wait because ET7 cannot be canceled, global result races if callers do not serialize, filename truncation/validation, unsupported event masks, and physical buffer-address validity. Tests should cover startup/shutdown registration, no-op probe, each FTP command, all load-flag mappings, timeout watchdogs at caller level, and concurrent-call exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ftp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ftp.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ftp.h

**Purpose:** This header declares the SCLP ET7 FTP backend interface used by the HMC drive FTP abstraction when running on LPAR.

**Important APIs and types:** It includes `hmcdrv_ftp.h` for `struct hmcdrv_ftp_cmdspec` and declares `sclp_ftp_startup()`, `sclp_ftp_shutdown()`, and `sclp_ftp_cmd(const struct hmcdrv_ftp_cmdspec *ftp, size_t *fsize)`.

**Control flow, state, and persistence:** The header warns that all exported functions are non-reentrant and require exclusive caller-side serialization. The `fsize` out parameter returns the full remote file size when the backend reports it, while the function return value is the actual bytes transferred or a negative errno.

**Dependencies and integration:** It is consumed by the HMC drive transport layer and implemented by `sclp_ftp.c`. The backend relies on SCLP event registration and Diagnostic Test event buffers.

**Risks and test signals:** Risks include callers treating the API as reentrant, ignoring the separate transferred-length and file-size semantics, or calling before startup. Test signals are serialized command execution, unsupported-backend behavior, correct file-size reporting on GET/DIR-like operations, and clean unregister during shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ftp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_mem.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_mem.c

**Purpose:** `sclp_mem.c` implements s390 memory hotplug backed by SCLP storage assignment and storage-info commands.

**Important APIs and functions:** `arch_get_memory_phys_device()` maps PFNs to SCLP memory increment IDs. Internal SCLP operations are `sclp_assign_storage()`, `sclp_unassign_storage()`, and `sclp_attach_storage()`. Sysfs attributes per firmware memory object are `config` and `memmap_on_memory`, implemented by `sclp_config_mem_*()` and `sclp_memmap_on_memory_*()`. Boot setup uses `sclp_setup_memory()`.

**Control flow, state, and persistence:** Boot reads storage-info for each storage ID, builds sorted `memory_increment` entries for assigned and standby increments, infers unassigned standby increments, then creates `/sys/firmware/memory/memoryN` objects aligned to Linux memory block size. Writing `config=1` attaches unqueried storage IDs, assigns intersecting increments, initializes storage keys/CMMA state, and calls `__add_memory()`. Writing `config=0` requires the memory block to be offline, unassigns increments, removes memory, and releases KASAN early shadow mapping if needed.

**Dependencies and integration:** It depends on SCLP core, memory hotplug, firmware ksets, KASAN shadow helpers, page-state/CMMA operations, and early `sclp.rnmax`/`sclp.rzm` discovery.

**Risks and test signals:** Risks include incorrect region-number to address mapping, partial assignment rollback, memory-block alignment losing standby memory, races with device hotplug, and leaks on kset allocation failure paths. Tests should cover storage-info response variants, standby object creation, config on/off with online-memory rejection, memmap-on-memory gating, KASAN cleanup, and kdump mode skipping standby memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ocf.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ocf.c

**Purpose:** `sclp_ocf.c` receives SCLP OCF communication-parameter events and exposes HMC network and CPC name information under firmware sysfs.

**Important APIs and functions:** `sclp_ocf_handler()` parses nested GDS vectors/subvectors for network ID and CPC name. `sclp_ocf_cpc_name_copy()` is exported for in-kernel users needing the raw EBCDIC CPC name. Sysfs read attributes are `cpc_name` and `hmc_network` under `/sys/firmware/ocf/`.

**Control flow, state, and persistence:** The event handler searches for GDS blocks `0x9f00`, `0x9f22`, `0x81`, then subkeys 1 and 2. It updates global `hmc_network` in ASCII and `cpc_name` in EBCDIC under `sclp_ocf_lock`, then schedules a work item that emits `KOBJ_CHANGE` on the OCF kset. Data persists in those globals until a later OCF event overwrites it.

**Dependencies and integration:** It uses SCLP event type `EVTYP_OCF`, GDS traversal helpers from `sclp.h`, EBCDIC conversion, firmware ksets, workqueues, and spinlocks.

**Risks and test signals:** Risks include trusting vector lengths, off-by-one size use when copying subvector payloads, mixed ASCII/EBCDIC storage semantics, and event delivery before sysfs setup. Tests should cover valid nested events, missing vector levels, sysfs rendering, exported raw copy, KOBJ_CHANGE emission, and concurrent reads during event updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ocf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_pci.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_pci.c

**Purpose:** This file implements SCLP PCI I/O adapter configure/deconfigure helpers and PCI error notification reporting.

**Important APIs and functions:** Exported functions are `sclp_pci_configure()`, `sclp_pci_deconfigure()`, and `sclp_pci_report()`. `do_pci_configure()` sends configure command words with adapter type PCI and adapter ID. `sclp_pci_check_report()` validates report version, action, and length. `sclp_pci_report()` wraps a zPCI report in an `EVTYP_ERRNOTIFY` event.

**Control flow, state, and persistence:** Configure/deconfigure are synchronous one-shot commands gated by `SCLP_HAS_PCI_RECONFIG`. Error reporting is serialized by `sclp_pci_mutex`, dynamically registers for error notification send capability, allocates an SCCB page, submits a Write Event Data request, waits for completion, checks request status and response code, then unregisters.

**Dependencies and integration:** It depends on zPCI report structures, SCLP event masks, completion API, mutexes, and SCLP core. PCI hotplug/error-recovery paths call into these helpers.

**Risks and test signals:** Risks include report length validation not matching future structures, repeated register/unregister overhead, mutex contention during error storms, unsupported event mask handling, and response-code assumptions. Tests should cover configure responses, invalid report versions/actions/lengths, successful error notification, unsupported send mask, request failure, and concurrent reports serialized by the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_quiesce.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_quiesce.c

**Purpose:** `sclp_quiesce.c` handles SCLP signal-quiesce events by initiating a machine shutdown/quiesce sequence.

**Important APIs and functions:** `sclp_quiesce_handler()` is the SCLP event receiver. `do_machine_quiesce()` stops secondary CPUs and loads a wait PSW at address `0xfff`. Init registers `sclp_quiesce_event` for `EVTYP_SIGQUIESCE_MASK`.

**Control flow, state, and persistence:** On a quiesce event, the handler replaces `_machine_restart`, `_machine_halt`, and `_machine_power_off` with the quiesce implementation, then calls `ctrl_alt_del()` to enter the normal reboot path. The override persists for that shutdown path so later machine operations load the quiesce PSW instead of restarting normally.

**Dependencies and integration:** It depends on SCLP event delivery, SMP stop, reboot control hooks, PSW loading, and device initcall registration.

**Risks and test signals:** Risks include quiesce events during fragile contexts, callback execution from SCLP event dispatch, and changing global machine operation hooks unexpectedly. Test signals include successful registration, event-triggered `ctrl_alt_del()`, CPUs stopped before PSW load, and no effect when no quiesce event is delivered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_quiesce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_rw.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_rw.c

**Purpose:** `sclp_rw.c` is the reusable line-mode SCLP message writer used by the console and tty drivers.

**Important APIs and functions:** Public functions are `sclp_rw_init()`, `sclp_make_buffer()`, `sclp_unmake_buffer()`, `sclp_write()`, `sclp_buffer_space()`, `sclp_chars_in_buffer()`, and `sclp_emit_buffer()`. Internals `sclp_initialize_mto()` and `sclp_finalize_mto()` construct SCLP message text objects inside an SCCB page. `sclp_writedata_callback()` handles Write Event Data completion and retry logic.

**Control flow, state, and persistence:** A caller supplies a 4 KiB DMA page; `sclp_make_buffer()` places `struct sclp_buffer` at the end and uses the front as the SCCB. `sclp_write()` parses ASCII text, filters nonprintables, translates printable characters to SCLP EBCDIC, expands tab/form/vertical/backspace behavior, and accumulates MTO objects. `sclp_emit_buffer()` finalizes any open line, prepares the embedded `sclp_req`, and submits it. Completion retries selected equipment/resource responses once, including removing processed event buffers for partial completion.

**Dependencies and integration:** It registers send capability for `EVTYP_MSG_MASK`, depends on `sclp.h` request APIs and EBCDIC helpers, and is shared by `sclp_con.c` and `sclp_tty.c`.

**Risks and test signals:** Risks include SCCB space accounting, partial processed-buffer retry, message loss after retry exhaustion, tab/backspace formatting quirks, and `init_done` not synchronized. Tests should cover newline splitting, long-line buffer exhaustion, bell flag, null termination behavior, retry response codes, and buffer space/character counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_rw.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_rw.h

**Purpose:** This header defines the SCLP message-buffer layout and writer API used by s390 line-mode console and tty code.

**Important APIs and types:** Packed hardware-facing structures are `mto`, `go`, `mdb_header`, `mdb`, and `msg_buf`. `struct sclp_buffer` overlays caller-provided SCCB pages with list linkage, embedded `sclp_req`, current message/line pointers, retry count, formatting settings, statistics, and completion callback. `NR_EMPTY_MSG_PER_SCCB` estimates worst-case newline capacity.

**Control flow, state, and persistence:** A `struct sclp_buffer` persists while being filled, queued, emitted, and returned to the caller's free-page list. Its embedded request means callers must not reuse the buffer page until the callback returns.

**Dependencies and integration:** It depends on Linux list handling and `struct sclp_req` from `sclp.h`. Console and tty drivers allocate pages, make buffers, write text, emit, and recycle pages through this interface.

**Risks and test signals:** Risks include callers passing non-DMA pages, reusing buffers before callbacks, inconsistent `columns`/`htab` settings, and assumptions about exact free-character capacity from `NR_EMPTY_MSG_PER_SCCB`. Test signals include buffer creation/unmake round trips, callback recycling, counter accuracy, and worst-case newline capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_rw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sd.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sd.c

**Purpose:** `sclp_sd.c` implements Store Data support and exposes retrieved firmware data entities through `/sys/firmware/sclp_sd/`.

**Important APIs and functions:** It defines Store Data event/SCCB layouts, `struct sclp_sd_data`, listener objects keyed by event ID, and sysfs-backed `struct sclp_sd_file`. `sclp_sd_sync()` submits size, store-data, or halt operations and waits for immediate or asynchronous completion. `sclp_sd_store_data()` retrieves size, allocates vmalloc data, builds an ASCE for the target buffer, and fetches contents. `sclp_sd_file_create()` creates per-entity `data` and `reload` files.

**Control flow, state, and persistence:** Init registers for send/receive Store Data events, creates `/sys/firmware/sclp_sd`, creates the `config` entity with DI 3, and asynchronously loads its data. A request listener is added before submission so an asynchronous event with matching physical SCCB ID can complete it. Retrieved data persists in the `sclp_sd_file` until reload or object release.

**Dependencies and integration:** It depends on SCLP events, completions, async scheduling, firmware kobjects, vmalloc, base ASCE allocation/free, and sysfs binary attributes.

**Risks and test signals:** Risks include timeouts/interrupted requests requiring HALT, leaked data if HALT fails, listener races, asynchronous unsolicited events, large allocation sizes from firmware `dsize`, and reload blocking sysfs writes. Tests should cover no-data `-ENOENT`, immediate and async completion, timeout plus halt, data reads with offsets, reload uevents, and registration failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sdias.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sdias.c

**Purpose:** `sclp_sdias.c` implements "store data in absolute storage" for dump IPL paths, mainly to copy FCP dump data from HSA into absolute storage.

**Important APIs and functions:** Public functions are `sclp_sdias_blk_count()`, `sclp_sdias_copy()`, and init `sclp_sdias_init()`. `sdias_sclp_send()` retries SCLP request submission and waits for accepted and, in async mode, done completions. `sclp_sdias_receiver_fn()` copies asynchronous event data into `sdias_evbuf`. `sclp_sdias_init_sync()` and `_async()` probe supported completion mode.

**Control flow, state, and persistence:** Init only runs for dump IPL. It allocates one shared DMA SCCB page, registers a debug area, then tries synchronous mode without a receiver and asynchronous mode with `EVTYP_SDIAS_MASK` receive. Operations are serialized by `sdias_mutex` and reuse the shared SCCB. Block count sends EQ_SIZE, while copy sends EQ_STORE_DATA with destination physical address, first block, block count, and 64-bit ASA size.

**Dependencies and integration:** It depends on SCLP Write Event Data, dump IPL detection, debug feature, completions, scheduler timeouts, and SDIAS structures in `sclp_sdias.h`.

**Risks and test signals:** Risks include fixed event ID reuse, completion objects not reinitialized between requests, long retry loops, async event races, shared SCCB lifetime, and partial-store semantics. Tests should cover non-dump no-op init, sync and async probing, block count response statuses, full/partial/no-data copy statuses, and retry exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sdias.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sdias.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sdias.h

**Purpose:** This header defines the SDIAS event constants and packed SCCB/event-buffer layouts for SCLP store-data-in-absolute-storage dump support.

**Important APIs and types:** Constants define event qualifiers `SDIAS_EQ_STORE_DATA` and `SDIAS_EQ_SIZE`, data ID `SDIAS_DI_FCP_DUMP`, ASA size selectors, and event states `SDIAS_EVSTATE_ALL_STORED`, `SDIAS_EVSTATE_NO_DATA`, and `SDIAS_EVSTATE_PART_STORED`. `struct sdias_evbuf` contains event qualifier, data ID, event ID, ASA size/status, block count, absolute-storage address, first/last block, and data block size. `struct sdias_sccb` wraps it in an SCCB header.

**Control flow, state, and persistence:** The header is stateless. `sclp_sdias.c` fills these fields per request and stores asynchronous responses in the same structure shape.

**Dependencies and integration:** It includes `sclp.h` for `evbuf_header` and `sccb_header`. The layout is consumed by dump IPL code through `sclp_sdias.c`.

**Risks and test signals:** Risks include packed layout mismatch with firmware, confusion between block counts and byte counts, and status handling that treats partial storage as acceptable but reports no-data as failure. Tests should validate structure sizes/offsets, EQ_SIZE block-count response, copy request encoding, and event-status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sdias.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_tty.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_tty.c

**Purpose:** `sclp_tty.c` implements the SCLP line-mode terminal driver, providing one real raw system tty backed by SCLP message output and SCLP operator-command input.

**Important APIs and functions:** It registers `sclp_tty_driver` with operations `open`, `close`, `write`, `put_char`, `flush_chars`, `write_room`, `chars_in_buffer`, and `flush_buffer`. Output helpers mirror console buffering: `sclp_tty_write_string()`, `__sclp_ttybuf_emit()`, `sclp_ttybuf_callback()`, and delayed `sclp_tty_timeout()`. Input parsing is in `sclp_tty_receiver()`, `sclp_eval_*()`, `sclp_get_input()`, `sclp_switch_cases()`, and `sclp_tty_input()`.

**Control flow, state, and persistence:** Init skips unsuitable VM/console combinations and systems without line mode, allocates DMA pages, registers SCLP input events, initializes a tty port, and registers tty `sclp_line`. Writes fill reusable SCLP buffers; `put_char()` accumulates small writes in a 512-byte static buffer until newline or flush. Inbound SCLP GDS event data is converted from EBCDIC, case-adjusted for z/VM, control-character processed, and pushed to the tty flip buffer with auto-newline behavior.

**Dependencies and integration:** It depends on `sclp_rw.c`, SCLP event registration for operator/priority message commands, tty core, `ctrlchar`, EBCDIC tables, timers, and global console detection.

**Risks and test signals:** Risks include static single-tty state, dropped input while closed, page exhaustion behavior, `sclp_tty_chars_count` lacking locking in some paths, GDS length trust, and VM case-switch semantics. Tests should cover tty open/close, write-room accounting, delayed flush, put-char buffering, input control chars, auto newline suppression, case delimiter handling, and driver skip conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_tty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_tty.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_tty.h

**Purpose:** This small header exposes the SCLP line-mode tty driver pointer to related console code.

**Important APIs and types:** It declares `extern struct tty_driver *sclp_tty_driver;`.

**Control flow, state, and persistence:** The pointer is assigned by `sclp_tty_init()` after successful tty driver registration. `sclp_con.c` uses it in its console `.device` callback so printk's console device can resolve to the SCLP tty. Until initialization succeeds, the pointer remains null.

**Dependencies and integration:** It forward-depends on `struct tty_driver` from the tty core and is included by `sclp_con.c`.

**Risks and test signals:** Risks are limited but important for console integration: console device lookup before tty registration may return null, and failed tty init leaves the console without a tty backing device. Test signals include correct `/dev/ttyS0` association for the SCLP console and graceful behavior when `sclp_tty_init()` is skipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_tty.h -->
