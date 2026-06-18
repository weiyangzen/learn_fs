# Research: subset-b-005447

This grouped report covers the requested tty HVC and IPWireless source files. Each source file section is source-tree-aligned and bounded by reconciliation markers for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_console.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_console.c

## Purpose
`hvc_console.c` is the shared hypervisor virtual console core. It exposes early kernel console support and a tty driver named `hvc` on major 229, then lets low-level platform backends provide transport operations through `struct hv_ops`. The file handles generic tty lifetime, buffering, polling, IRQ notifier integration, resize delivery, hangup behavior, and the `khvcd` kernel thread.

## Important APIs, Types, and Functions
The external entry points are `hvc_instantiate()`, `hvc_alloc()`, `hvc_remove()`, `hvc_poll()`, `hvc_kick()`, and `__hvc_resize()`. `hvc_instantiate()` registers an early console slot before a full tty exists. `hvc_alloc()` creates an `hvc_struct`, attaches tty-port state, assigns a stable tty index, and lazily initializes the global tty driver via `hvc_init()`. `hvc_remove()` invalidates early-console arrays and vhangups any attached tty.

TTY operations are implemented by `hvc_install()`, `hvc_open()`, `hvc_close()`, `hvc_cleanup()`, `hvc_hangup()`, `hvc_write()`, `hvc_write_room()`, `hvc_chars_in_buffer()`, `hvc_tiocmget()`, and `hvc_tiocmset()`. Console output uses `hvc_console_print()` and translates LF to CRLF before calling backend `put_chars()`.

## Control Flow
Early boot calls `hvc_console_init()` to register a `struct console`. Backend discovery later calls `hvc_instantiate()` and possibly re-registers the console when the selected index becomes usable. Runtime device discovery calls `hvc_alloc()`, which starts `khvcd` once, registers the tty driver, links the new `hvc_struct`, and wakes console registration if needed.

Writes copy user data into `hp->outbuf`, call `hvc_push()` under `hp->lock`, and kick `khvcd` if data remains or wakeups are needed. Reads are driven by `__hvc_poll()`: it flushes pending output, gets the attached tty, checks throttling, requests flip-buffer room, invokes backend `get_chars()`, handles `-EPIPE` as carrier loss via `tty_hangup()`, processes Magic SysRq for the active console, and pushes flip-buffer data outside the lock. `khvcd()` walks all registered consoles, backs off from 10 ms to 2000 ms when idle, and can be woken by `hvc_kick()` or backend IRQ notifiers.

## State and Persistence Behavior
Persistent state is in global early-console arrays `vtermnos[]` and `cons_ops[]`, global device list `hvc_structs`, `last_hvc`, `hvc_driver`, `hvc_task`, and each `hvc_struct`. Per-device state includes tty-port reference counts, output buffer fill, backend data/ops, IRQ-requested state, terminal size, and deferred resize work. No on-disk persistence exists.

## Dependencies and Integration Points
The core integrates with Linux tty, console, tty-port, kthread, workqueue, Magic SysRq, freezer, and optional console-poll APIs. Backends supply `struct hv_ops` for transports such as OPAL, VIO, Xen, RTAS, SBI, DCC, udbg, and IUCV. IRQ-capable backends commonly use `hvc_irq.c` notifier callbacks.

## Risks and Edge Cases
The file is concurrency-sensitive: `hvc_structs_mutex`, `hp->lock`, `hp->port.lock`, tty krefs, and console locking have distinct roles. Backend `put_chars()` returning zero or `-EAGAIN` causes buffered retry and tty wakeup behavior, while other errors discard buffered output. `hvc_remove()` intentionally does not clear IRQ state because hangup paths may still free it. Early-console slots are limited to `MAX_NR_HVC_CONSOLES`, while additional ttys get indices beyond that range and cannot be kernel consoles.

## Test Signals
Useful signals include successful `hvc` tty registration, early `console=hvcN` output, backend hotplug add/remove, close with pending output, IRQ and polling mode reads, throttled tty input, Magic SysRq over active console, terminal resize delivery, and `-EPIPE` backend hangup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_console.h -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_console.h

## Purpose
`hvc_console.h` is the shared contract between the generic HVC core and low-level hypervisor console backends. It declares the maximum early-console/tty adapter counts, the `hvc_struct` runtime object, the `hv_ops` backend callback table, and the exported HVC lifecycle and notifier APIs.

## Important APIs, Types, and Functions
`struct hvc_struct` embeds `struct tty_port`, per-device spinlock, tty index, virtual terminal number, backend ops/data, IRQ-requested state, output buffer metadata, current window size, resize work, list linkage, backend flags, and flexible `outbuf[]`.

`struct hv_ops` is the main transport interface. Required operations are usually `get_chars()` and `put_chars()`. Optional operations are `flush()`, `notifier_add()`, `notifier_del()`, `notifier_hangup()`, `tiocmget()`, `tiocmset()`, and `dtr_rts()`. The exported allocation path is `hvc_instantiate()` for early console registration and `hvc_alloc()`/`hvc_remove()` for tty runtime.

The inline `hvc_resize()` acquires `hp->lock` and delegates to `__hvc_resize()`. IRQ-based transports can reuse `notifier_add_irq()`, `notifier_del_irq()`, and `notifier_hangup_irq()`.

## Control Flow
Backends include this header, define one or more `hv_ops` instances, optionally instantiate an early console slot, and allocate runtime HVC devices when their platform bus probes. For resize events, backends call `hvc_resize()` or `__hvc_resize()` depending on whether they already hold `hp->lock`.

## State and Persistence Behavior
The header defines in-memory state only. `MAX_NR_HVC_CONSOLES` is the number of first-stage console adapters, while `HVC_ALLOC_TTY_ADAPTERS` is the tty driver allocation count for hotplug-capable devices.

## Dependencies and Integration Points
It depends on tty, kref, spinlock, and optional xmon headers. It is consumed by all HVC backends in this directory and by the generic core.

## Risks and Edge Cases
Backend implementers must obey locking expectations: several callbacks are called while HVC locks are held, `__hvc_resize()` requires `hp->lock`, and notifier callbacks run during tty open/close/hangup. `HVC_ALLOC_TTY_ADAPTERS` is smaller than `MAX_NR_HVC_CONSOLES`, which is an unusual contract inherited by the core and platform drivers.

## Test Signals
Build coverage for every backend is the main signal. Runtime signs include correct tty index assignment, correct modem-control passthrough when optional callbacks exist, and successful IRQ notifier use by backends that pass a real IRQ number.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_console.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_dcc.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_dcc.c

## Purpose
`hvc_dcc.c` adapts ARM Debug Communications Channel access to the HVC core. It provides an early console named `dcc`, direct `hv_ops` get/put methods, and optional SMP serialization through CPU0-backed FIFOs and workqueues.

## Important APIs, Types, and Functions
The backend operations are `hvc_dcc0_get_chars()` and `hvc_dcc0_put_chars()`, backed by raw `hvc_dcc_get_chars()` and `hvc_dcc_put_chars()`. `hvc_dcc_check()` probes DCC availability by writing a test newline and waiting for the TX status bit to clear. Early console setup uses `dcc_early_console_setup()` and `dcc_early_write()`. Runtime init occurs in `hvc_dcc_console_init()` and `hvc_dcc_init()`.

When `CONFIG_HVC_DCC_SERIALIZE_SMP` is enabled, `dcc_lock`, `inbuf`, `outbuf`, `dcc_put_work()`, and `dcc_get_work()` serialize DCC access on CPU0.

## Control Flow
Early console setup waits for the DCC transmitter to become available and assigns the console write callback. Console init probes DCC and calls `hvc_instantiate(0, 0, &hvc_dcc_get_put_ops)`. Device init probes again and calls `hvc_alloc(0, 0, ..., 128)`. Reads poll the DCC RX status bit until no character is available. Writes busy-wait on the TX status bit for each byte.

## State and Persistence Behavior
The driver uses global KFIFOs for serialized SMP input/output and a static `dcc_core0_available` probe result. There is no persistent state outside DCC hardware state.

## Dependencies and Integration Points
It depends on `asm/dcc.h`, CPU hotplug/SMP helpers, kfifo, earlycon, uart console helpers, and HVC core APIs. In serialized mode it disables CPU hotplug in `hvc_dcc_init()` and warns loudly that the kernel is a debug build.

## Risks and Edge Cases
DCC put paths busy-wait, so unavailable or slow debug hardware can stall console output. Serialized SMP mode relies on CPU0 staying online and uses queued work to avoid multi-core DCC corruption. The DCC availability probe writes a newline, which is observable on the debug channel.

## Test Signals
Signals include early `earlycon=dcc` output, successful `hvc0` allocation, no hangs in `hvc_dcc_check()`, input availability through DCC RX, serialized writes from nonzero CPUs, and expected warning output when SMP serialization is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_dcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_irq.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_irq.c

## Purpose
`hvc_irq.c` provides reusable IRQ notifier callbacks for HVC backends. It lets transports that have a conventional Linux IRQ wake the generic HVC polling core when input or output progress is available.

## Important APIs, Types, and Functions
`notifier_add_irq()` requests an IRQ for an `hvc_struct` using `hvc_handle_interrupt()`. `notifier_del_irq()` frees it when present, and `notifier_hangup_irq()` delegates to delete. `hvc_handle_interrupt()` calls `hvc_poll()` on the device and kicks `khvcd` when polling requests more work.

## Control Flow
The generic HVC core calls backend notifier callbacks during tty open, close, and hangup. Backends that reuse this file pass an IRQ number as `hp->data`. If the IRQ is zero, `notifier_add_irq()` reports success and leaves the device in non-IRQ/polling mode. On interrupt, the handler polls the device immediately, then wakes the HVC thread if further read/write polling is needed.

## State and Persistence Behavior
The only persistent per-device state changed here is `hp->irq_requested`. IRQ handler lifetime is bound to tty open/close/hangup rather than backend probe/remove.

## Dependencies and Integration Points
It depends on Linux interrupt APIs and the HVC core. OPAL, VIO, Xen, and other IRQ-capable backends use these callbacks in their `hv_ops`.

## Risks and Edge Cases
Returning `IRQ_HANDLED` unconditionally is intentional because `khvcd` scans all devices, but it can obscure shared-IRQ diagnostics. Passing a stale or invalid IRQ number risks request/free mismatch. `hp->flags` is used as request flags, so backends must set it before open if shared IRQs are needed.

## Test Signals
Useful checks include request/free balance across open/close/hangup, shared-IRQ OPAL behavior, zero-IRQ fallback to polling, and interrupts causing HVC input to appear without waiting for the polling backoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_iucv.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_iucv.c

## Purpose
`hvc_iucv.c` implements a z/VM IUCV-backed HVC terminal driver. It exposes one or more HVC tty lines whose remote peers connect over IUCV paths, supports a first line as the Linux console, filters connection requests by z/VM user ID, and translates IUCV messages into HVC get/put operations.

## Important APIs, Types, and Functions
Important types are `struct iucv_tty_msg`, `enum iucv_state_t`, `enum tty_state_t`, `struct hvc_iucv_private`, and `struct iucv_tty_buffer`. `hvc_iucv_private` owns the HVC pointer, service name, IUCV path state, tty state, send buffer, delayed send work, waitqueue, input/output queues, sysfs device, and peer info.

The HVC ops are `hvc_iucv_get_chars()`, `hvc_iucv_put_chars()`, `hvc_iucv_notifier_add()`, `hvc_iucv_notifier_del()`, `hvc_iucv_notifier_hangup()`, and `hvc_iucv_dtr_rts()`. IUCV callbacks are `hvc_iucv_path_pending()`, `hvc_iucv_path_severed()`, `hvc_iucv_msg_pending()`, and `hvc_iucv_msg_complete()`.

## Control Flow
`hvc_iucv_init()` validates z/VM availability and the `hvc_iucv=` device count, builds the optional allow filter, creates a slab cache and mempool, instantiates console slot 0, allocates each HVC/IUCV line, and registers the IUCV handler. Incoming path requests are matched by service name or wildcard `lnxhvc  `, filtered by VMID, accepted with the IUCV handler, and associated with a disconnected line.

Input messages are queued in `tty_inqueue` by `hvc_iucv_msg_pending()` only when the tty is open. `hvc_iucv_get_chars()` receives message bodies lazily, validates message version/length, copies DATA payload to HVC, applies WINSIZE via `__hvc_resize()`, and schedules another HVC pass when partial data remains. Output is accumulated in `sndbuf` by `hvc_iucv_put_chars()`, then delayed work sends it as an IUCV message and tracks completion in `tty_outqueue`.

## State and Persistence Behavior
The driver keeps global `hvc_iucv_devices`, `hvc_iucv_table[]`, filter state protected by `hvc_iucv_filter_lock`, a slab cache, and a mempool. Each line transitions among `IUCV_DISCONN`, `IUCV_CONNECTED`, and `IUCV_SEVERED`, and between `TTY_CLOSED` and `TTY_OPENED`. No state is persisted beyond module parameters and sysfs views.

## Dependencies and Integration Points
It integrates with the HVC core, z/VM IUCV networking APIs, EBCDIC/ASCII conversion, Linux device attributes, mempools, delayed work, waitqueues, and module/core parameters. Sysfs exposes `termid`, `state`, and `peer`; `hvc_iucv_allow` configures the VMID allow-list.

## Risks and Edge Cases
Path sever is intentionally two-stage: `hvc_iucv_hangup()` sets `IUCV_SEVERED`, then `get_chars()` returns `-EPIPE` so the HVC core performs tty hangup. Console lines are special because console hangups may not call normal HVC notifier cleanup. Buffer allocation uses `GFP_DMA` and mempool elements to satisfy IUCV constraints. Incorrect filter parsing can deny remote access, and oversized or malformed messages are rejected or dropped.

## Test Signals
Signals include successful creation of `hvc_iucvN` devices, VMID filter accept/reject behavior, wildcard and explicit service-name connection, data and winsize message handling, send completion waking `sndbuf_waitq`, DTR/RTS disconnect via `HUPCL`, and `-EPIPE` hangups after remote path sever.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_iucv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_opal.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_opal.c

## Purpose
`hvc_opal.c` connects OPAL firmware consoles on PowerNV systems to the HVC core. It supports raw OPAL consoles and OPAL HVSI consoles, handles early boot console discovery from the device tree, and registers a platform driver for runtime console devices.

## Important APIs, Types, and Functions
`struct hvc_opal_priv` stores protocol selection and optional `struct hvsi_priv`. `hvc_opal_raw_ops` maps directly to `opal_get_chars()`, `opal_put_chars()`, and `opal_flush_chars()`. `hvc_opal_hvsi_ops` wraps `hvsilib_get_chars()`, `hvsilib_put_chars()`, `hvsilib_open()`, `hvsilib_close()`, modem control, and IRQ notifier behavior.

Runtime device handling is in `hvc_opal_probe()` and `hvc_opal_remove()`. Early console setup is in `hvc_opal_init_early()`, with udbg support through `udbg_opal_putc()`, `udbg_opal_getc_poll()`, `udbg_opal_getc()`, and debug init variants for raw/HVSI.

## Control Flow
Early init locates `/chosen/stdout` or OPAL console nodes, reads the `reg` terminal number, chooses raw or HVSI ops by compatible string, initializes boot HVSI if needed, installs udbg callbacks, adds preferred `hvc`, and calls `hvc_instantiate(index, index, ops)`. Runtime probe repeats protocol selection for platform devices, reuses the boot private object if appropriate, otherwise allocates private state and instantiates index-to-terminal mapping. It maps an OF IRQ or requests an OPAL console event IRQ, then allocates the HVC device with shared IRQ flags.

## State and Persistence Behavior
The global `hvc_opal_privs[]` maps terminal numbers to private protocol state. `hvc_opal_boot_priv` and `hvc_opal_boot_termno` preserve early console state across runtime probe. Removal calls `hvc_remove()` and frees non-boot private objects.

## Dependencies and Integration Points
It depends on OPAL firmware APIs, Open Firmware device nodes, platform devices, IRQ mapping, `hvc_irq.c`, and `hvsi_lib.c`. The udbg hooks integrate with PowerPC early debug paths.

## Risks and Edge Cases
Terminal numbers index fixed arrays and are bounded by `MAX_NR_HVC_CONSOLES` only in early init; runtime device-tree term numbers must be sane. OPAL event IRQ fallback is used when no interrupt property exists. HVSI put operations use `opal_put_chars_atomic()` to avoid packet interleaving. Duplicate terminal numbers are rejected.

## Test Signals
Signals include device-tree matching for `ibm,opal-console-raw` and `ibm,opal-console-hvsi`, early boot `hvc` output, udbg input/output, OPAL event fallback, shared IRQ delivery, HVSI handshake and modem control, and clean removal of platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_opal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_riscv_sbi.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_riscv_sbi.c

## Purpose
`hvc_riscv_sbi.c` provides a RISC-V SBI-backed HVC console. It supports the newer SBI debug console extension when available and falls back to legacy SBI v0.1 console calls when configured.

## Important APIs, Types, and Functions
`hvc_sbi_tty_put()` and `hvc_sbi_tty_get()` wrap legacy `sbi_console_putchar()` and `sbi_console_getchar()`. `hvc_sbi_dbcn_tty_put()` and `hvc_sbi_dbcn_tty_get()` wrap `sbi_debug_console_write()` and `sbi_debug_console_read()`. The two `hv_ops` tables are `hvc_sbi_v01_ops` and `hvc_sbi_dbcn_ops`. `hvc_sbi_init()` selects and registers the available backend.

## Control Flow
At device init, the driver first checks `sbi_debug_console_available`. If present, it allocates an HVC device and instantiates console slot 0 using DBCN ops. Otherwise, if legacy SBI v0.1 support is enabled, it allocates and instantiates with legacy ops. If neither path is available, init returns `-ENODEV`.

## State and Persistence Behavior
There is no driver-private persistent state. All state is in the generic HVC instance and SBI firmware.

## Dependencies and Integration Points
It depends on RISC-V `asm/sbi.h` and the HVC core. It has no IRQ notifier and therefore relies on HVC polling.

## Risks and Edge Cases
Legacy SBI console reads return negative when no character is available, while DBCN returns the debug console read result directly. The driver allocates before instantiating; if `hvc_instantiate()` failed, init still returns success after allocation, so console visibility depends on the instantiate result.

## Test Signals
Signals include boot on firmware with DBCN, boot with only SBI v0.1, readable input through polling, console output before userspace, and no registration on systems lacking both SBI console mechanisms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_riscv_sbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_rtas.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_rtas.c

## Purpose
`hvc_rtas.c` exposes IBM RTAS terminal services as an HVC console. It uses RTAS `put-term-char` and `get-term-char` tokens for basic character I/O on PowerPC systems.

## Important APIs, Types, and Functions
`hvc_rtas_write_console()` writes one byte at a time through `rtas_call(rtascons_put_char_token, ...)`. `hvc_rtas_read_console()` reads characters through `rtascons_get_char_token`. `hvc_rtas_get_put_ops` is the HVC ops table. `hvc_rtas_console_init()` registers the early console and preferred `hvc0`; `hvc_rtas_init()` allocates the runtime HVC device.

## Control Flow
Console init resolves both RTAS tokens, instantiates a fixed cookie vterm at index 0, and adds `hvc0` as preferred console. Device init resolves tokens if needed, verifies the runtime device has not already been allocated, then calls `hvc_alloc()` with a 16-byte output buffer.

## State and Persistence Behavior
Global state consists of the RTAS service tokens and the single `hvc_rtas_dev` pointer. The fixed `hvc_rtas_cookie` distinguishes this console in the HVC core. There is no persistent state outside firmware.

## Dependencies and Integration Points
It depends on RTAS firmware APIs, PowerPC IRQ headers, Linux console initcalls, and the HVC core. It has no IRQ notifier and uses polling.

## Risks and Edge Cases
Missing RTAS tokens cause `-EIO` and no console registration. The read/write loops stop on the first RTAS error and return the partial byte count. Only one runtime device is supported, enforced with `BUG_ON(hvc_rtas_dev)`.

## Test Signals
Signals include RTAS token discovery, early preferred `hvc0`, tty allocation at device init, successful character input/output through RTAS calls, and graceful non-registration when tokens are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_rtas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_udbg.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_udbg.c

## Purpose
`hvc_udbg.c` bridges PowerPC `udbg` early debug callbacks into the HVC tty/console framework. It is a minimal backend used when `udbg_putc` and optionally `udbg_getc_poll` are available.

## Important APIs, Types, and Functions
`hvc_udbg_put()` writes bytes via `udbg_putc`. `hvc_udbg_get()` polls bytes via `udbg_getc_poll` and stops when it returns `-1`. `hvc_udbg_ops` is the HVC ops table. `hvc_udbg_console_init()` performs early console instantiation and preferred console selection; `hvc_udbg_init()` allocates the runtime HVC device.

## Control Flow
If no `udbg_putc` callback exists, both init paths return `-ENODEV`. Otherwise console init registers vterm 0/index 0 and adds preferred `hvc0`. Device init allocates one HVC device with a 16-byte output buffer and saves it in `hvc_udbg_dev`.

## State and Persistence Behavior
The only private state is the single `hvc_udbg_dev` pointer. Operational behavior depends entirely on globally installed udbg callbacks.

## Dependencies and Integration Points
It depends on PowerPC `asm/udbg.h` and HVC core APIs. Other platform code such as OPAL and VIO may install udbg callbacks that this backend then exposes through tty/HVC.

## Risks and Edge Cases
Input is unavailable if `udbg_getc_poll` is null, but output can still work. Only one device is supported. Because udbg callbacks are low-level debug hooks, they may have platform-specific polling or blocking behavior.

## Test Signals
Signals include `udbg_putc` availability, preferred `hvc0` registration, output through debug console, optional input polling, and absence of registration when no udbg output callback is installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_udbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_vio.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_vio.c

## Purpose
`hvc_vio.c` connects IBM pSeries VIO virtual terminal devices to the HVC core. It supports raw `hvterm1` consoles and packetized `hvterm-protocol` HVSI consoles, plus early boot and udbg paths.

## Important APIs, Types, and Functions
`struct hvterm_priv` stores the firmware term number, protocol, `hvsi_priv`, a raw-input bounce buffer, and offset/remaining counters. Raw operations are `hvterm_raw_get_chars()` and `hvterm_raw_put_chars()`. HVSI operations are `hvterm_hvsi_get_chars()`, `hvterm_hvsi_put_chars()`, `hvterm_hvsi_open()`, `hvterm_hvsi_close()`, `hvterm_hvsi_hangup()`, and modem-control callbacks. Runtime probing uses `hvc_vio_probe()` and driver registration uses `hvc_vio_init()`. Early setup is in `hvc_vio_init_early()`.

## Control Flow
Early init checks `/chosen/stdout` for a `vty` node, reads its unit address, selects raw or HVSI protocol, initializes HVSI if needed, installs udbg hooks, optionally adds preferred `hvc0`, and calls `hvc_instantiate(0, 0, ops)`. Runtime VIO probe matches compatible strings, reuses the boot private object when the device is the early console, otherwise finds a free HVC slot, allocates private state, initializes HVSI, then calls `hvc_alloc(termno, irq, ops, MAX_VIO_PUT_CHARS)`.

Raw reads call `hvc_get_chars()` into an internal buffer, remove a firmware bug pattern of NUL after CR, and serve callers from the buffered data. Raw writes call `hvc_put_chars()`. HVSI mode delegates packet handling and modem control to `hvsi_lib.c`.

## State and Persistence Behavior
`hvterm_privs[]` maps HVC virtual term numbers to protocol state, and `hvterm_priv0` preserves the boot console private object. State is in-memory and tied to VIO device lifetime.

## Dependencies and Integration Points
It integrates with the VIO bus, Open Firmware nodes, PowerPC hypervisor console calls, `hvsi_lib.c`, udbg, and the generic HVC core. IRQ-capable devices reuse the notifier callbacks from `hvc_irq.c`.

## Risks and Edge Cases
Raw `put_chars()` requires a buffer of at least 16 bytes; udbg output uses a bounce buffer for single-character writes. Array slots are limited by `MAX_NR_HVC_CONSOLES`. The raw input workaround modifies received data and should be tested on firmware that emits CR/NUL. `HVC_OLD_HVSI` can suppress HVC registration for HVSI boot consoles.

## Test Signals
Signals include OF discovery of `hvterm1` and `hvterm-protocol`, early console output, udbg fallback, VIO probe hotplug, IRQ-driven reads, HVSI handshake and DTR handling, and the CR/NUL raw input workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_vio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_xen.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_xen.c

## Purpose
`hvc_xen.c` adapts Xen console mechanisms to the HVC core and early console paths. It supports domU ring/event-channel consoles, initial-domain console hypercalls, HVM console parameter discovery, optional xenbus frontend consoles, raw printk helpers, and `xenboot` early console support.

## Important APIs, Types, and Functions
`struct xencons_info` owns ring/interface pointers, event channel, IRQ, grant reference, vterm number, HVC pointer, xenbus device, and ring lock. DomU operations are `domU_read_console()` and `domU_write_console()`, backed by `__write_console()`. Dom0 operations are `dom0_read_console()` and `dom0_write_console()` using `HYPERVISOR_console_io`.

Initialization paths are `xen_cons_init()` for early console instantiation and `xen_hvc_init()` for runtime allocation. Domain-specific setup is split across `xen_hvm_console_init()`, `xen_pv_console_init()`, and `xen_initial_domain_console_init()`. Frontend hotplug support includes `xencons_probe()`, `xencons_connect_backend()`, `xencons_remove()`, `xencons_resume()`, and `xencons_backend_changed()`.

## Control Flow
Early init decides whether to use initial-domain console I/O based on `xen_console_io=` or `xen_initial_domain()`. Non-initial domains initialize PV/HVM ring state and instantiate `hvc0` with `HVC_COOKIE`. Runtime init repeats setup, binds event channels to late-EOI IRQs, allocates the HVC device, and optionally registers the xenbus frontend driver.

DomU writes fill the shared `out` ring under `ring_lock`, update producer indices with barriers, notify the backend, and yield until the whole buffer is queued. DomU reads consume the `in` ring, update consumer indices with barriers, notify the daemon when data was read, and call `xen_irq_lateeoi()` with spurious hints when appropriate. Xenbus frontend probe allocates a page ring, event channel, grant ref, HVC device, and publishes ring-ref/port in xenstore.

## State and Persistence Behavior
Global state is `xenconsoles`, `xencons_lock`, `xen_console_io`, and early parameter `opt_console_io`. Per-console state persists until device remove/resume/disconnect. No on-disk state exists; xenstore entries are runtime frontend/backend coordination state.

## Dependencies and Integration Points
It integrates with Xen hypervisor APIs, event channels, grant tables, xenbus, shared ring structures, HVC core, earlycon, and architecture-specific x86 port `0xe9` fallback for HVM early writes.

## Risks and Edge Cases
Ring index validation protects against illegal producer/consumer deltas. Memory barriers are required around ring reads/writes. HVM console parameters of zero are treated as absent even though zero is theoretically representable. Frontend device ID parsing only uses the last character of the xenbus node name, which constrains expected names. Cleanup must balance HVC removal, event channel release, grant references, and mapped/free pages.

## Test Signals
Signals include PV domU console I/O, HVM console parameter setup, initial-domain `xen_console_io`, event-channel IRQ wakeups with late EOI, xenbus secondary console hotplug, suspend/resume event-channel rebinding, backend close behavior, `xen_raw_printk()`, and `xenboot` early output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_xen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvcs.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvcs.c

## Purpose
`hvcs.c` is the IBM Hypervisor Virtual Console Server tty driver. Unlike the generic HVC backends that expose this partition's console, HVCS exposes server-side VIO `serial-server` adapters so userspace can connect to partner partition consoles through `/dev/hvcs*`.

## Important APIs, Types, and Functions
`struct hvcs_struct` stores tty-port state, index, todo mask, a 16-byte output buffer, connection status, partner unit/partition/location fields, VIO device, and destruction completion. Sysfs device attributes expose partner vtys, partner/current location codes, vterm state, and driver-assigned index; driver attribute `rescan` refreshes partner info.

TTY operations are `hvcs_install()`, `hvcs_open()`, `hvcs_close()`, `hvcs_cleanup()`, `hvcs_hangup()`, `hvcs_write()`, `hvcs_write_room()`, `hvcs_chars_in_buffer()`, `hvcs_throttle()`, and `hvcs_unthrottle()`. Device lifecycle is `hvcs_probe()` and `hvcs_remove()`. Core runtime setup is lazy in `hvcs_initialize()`.

## Control Flow
Module init registers a VIO driver for `serial-server`/`hvterm2`. First probe lazily allocates the tty driver, index list, partner-info page buffer, and `khvcsd` thread. Probe assigns the lowest free `/dev/hvcsN` index, allocates `hvcs_struct`, fetches partner info, and adds it to the global list. Install/open connects to the partner via firmware, enables IRQs, requests the IRQ, schedules an initial read, and installs the tty port.

Interrupts disable VIO interrupts, mark read work, and kick `khvcsd`. The worker scans all devices, calls `hvcs_io()`, flushes pending writes via `hvc_put_chars()`, reads up to 16 bytes via `hvc_get_chars()`, pushes tty flip buffers, and re-enables interrupts when drained. Close disables interrupts, clears the tty pointer early, waits for sent data, and frees the IRQ. Remove vhangups attached tty and waits for port destruction.

## State and Persistence Behavior
Global state includes `hvcs_index_list`, `hvcs_index_count`, `hvcs_structs`, `hvcs_task`, `hvcs_pi_buff`, and `hvcs_rescan_status`. Per-device partner and connection state persists while the VIO device exists and can be refreshed by sysfs rescan. No durable state exists.

## Dependencies and Integration Points
HVCS depends on the tty core, VIO bus, PowerPC hypervisor console/server calls (`hvc_get_chars()`, `hvc_put_chars()`, `hvcs_register_connection()`, `hvcs_free_connection()`, partner info helpers), kthreads, sysfs attributes, IRQs, and tty-port reference management.

## Risks and Edge Cases
Partner info is not firmware-notified, so stale partner data requires manual rescan and retry-on-`-EINVAL`. `hvcs_partner_free()` loops while firmware returns `-EBUSY`. The driver must not echo by default because remote console echo could recurse. Index reuse on hotplug is manual and must stay balanced with port destruction. Write-room promises are backed by an internal 16-byte buffer and deferred worker retries.

## Test Signals
Signals include VIO probe/remove, `/dev/hvcsN` lowest-free index reuse, sysfs partner fields, rescan status, busy partner open returning `-EBUSY`, IRQ-driven reads, write buffering and `tty_wait_until_sent()`, throttle/unthrottle interrupt toggling, and clean module unload after active tty hangups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvsi.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvsi.c

## Purpose
`hvsi.c` is the standalone Host Virtual Serial Interface tty driver for IBM pSeries service-processor serial ports. It predates or coexists with the generic HVC HVSI library path and implements its own tty major/minor range, packet parser, handshake state machine, IRQ handling, modem-control operations, and console support.

## Important APIs, Types, and Functions
`struct hvsi_struct` stores tty-port state, writer/handshaker work, waitqueues, lock, buffers, vterm/IRQ, packet sequence number, modem control, protocol state, flags, and optional SysRq state. Protocol states are `HVSI_CLOSED`, `HVSI_WAIT_FOR_VER_RESPONSE`, `HVSI_WAIT_FOR_VER_QUERY`, `HVSI_OPEN`, `HVSI_WAIT_FOR_MCTRL_RESPONSE`, and `HVSI_FSP_DIED`.

Key parser functions are `hvsi_load_chunk()`, `hvsi_recv_control()`, `hvsi_recv_response()`, `hvsi_recv_query()`, and `hvsi_recv_data()`. Connection functions are `hvsi_handshake()`, `hvsi_query()`, `hvsi_get_mctrl()`, `hvsi_set_mctrl()`, and `hvsi_close_protocol()`. TTY ops include `hvsi_open()`, `hvsi_close()`, `hvsi_write()`, `hvsi_hangup()`, throttle/unthrottle, and tiocm get/set.

## Control Flow
Console init scans the device tree for `hvterm-protocol` serial nodes, initializes `hvsi_ports[]`, maps IRQs, and registers the `hvsi` console if any are found. Console setup handshakes with the service processor, reads modem status, asserts DTR, and marks the port as console. Device init allocates and registers the `hvsi` tty driver and requests IRQs for discovered ports.

IRQ handling repeatedly reads chunks via `hvc_get_chars()`, parses complete HVSI packets, pushes tty data, schedules re-handshake when a close protocol packet arrives, and delivers throttled overflow when possible. Opens enable VIO IRQs, handshake non-console ports, query modem control, and assert DTR. Writes pack up to 12 bytes into HVSI data packets and use delayed work to retry when firmware does not accept data.

## State and Persistence Behavior
All state is static/in-memory in `hvsi_ports[]`, `hvsi_driver`, `hvsi_count`, and per-port buffers and state fields. `hvsi_wait` switches from polling during console init to waitqueue-based waiting after IRQs are active.

## Dependencies and Integration Points
The driver integrates directly with tty, console, Open Firmware IRQ mapping, PowerPC VIO signaling, hypervisor console calls, HVSI packet definitions from `asm/hvsi.h`, workqueues, waitqueues, and Magic SysRq.

## Risks and Edge Cases
The packet parser must resynchronize on malformed data and compact partial packets. `hvsi_drain_input()` appears to use a time comparison that should be reviewed carefully because it controls stale packet discard. Carrier loss can hang up non-local ttys. Throttle overflow buffering is explicitly uncertain in the comments. Console ports remain open and are treated differently during close and service-processor reset.

## Test Signals
Signals include device-tree discovery, successful console handshake, version query/response transitions, modem-control query and DTR set, IRQ packet parsing, FSP close/re-handshake, delayed write retries, carrier-drop hangup, throttle/unthrottle overflow delivery, and tty registration on major 229 minor 128.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvsi_lib.c -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvsi_lib.c

## Purpose
`hvsi_lib.c` is a reusable HVSI packet helper used by HVC backends such as VIO and OPAL. It encapsulates HVSI handshaking, packet parsing, data packet extraction, DTR/carrier modem-control handling, and open/close behavior around backend-supplied character I/O functions.

## Important APIs, Types, and Functions
Public functions are `hvsilib_get_chars()`, `hvsilib_put_chars()`, `hvsilib_read_mctrl()`, `hvsilib_write_mctrl()`, `hvsilib_establish()`, `hvsilib_open()`, `hvsilib_close()`, and `hvsilib_init()`. Internal helpers include `hvsi_send_packet()`, `hvsi_start_handshake()`, `hvsi_send_close()`, `hvsi_cd_change()`, `hvsi_got_control()`, `hvsi_got_query()`, `hvsi_got_response()`, `hvsi_check_packet()`, and `hvsi_get_packet()`.

## Control Flow
Backends initialize an embedded `struct hvsi_priv` with get/put callbacks and terminal number. Open stores a tty kref and calls `hvsilib_establish()`. Establish first consumes any already-arrived packets, then sends close/restart handshake if needed, waits for version negotiation, reads modem control, asserts DTR, and finally sets `opened` so HVC reads may consume data.

Reads consume any buffered data packet, compact the input buffer, fetch and parse more packets, and return `-EPIPE` when the protocol is no longer established. Writes wrap up to `HVSI_MAX_OUTGOING_DATA` bytes into a VS_DATA packet and send it with an incremented sequence number. Close clears `opened` under the HVC lock for non-console ports, optionally lowers DTR on HUPCL, sends close, and drops the tty kref.

## State and Persistence Behavior
State lives in caller-owned `struct hvsi_priv`: packet buffers/cursors, sequence number, `established`, `opened`, `is_console`, modem-control bits, tty pointer, and backend callbacks. There is no global state in this file.

## Dependencies and Integration Points
It depends on `asm/hvsi.h`, HVC `struct hvc_struct`, tty krefs, timing helpers, and backend character functions such as OPAL or VIO raw put/get calls. It is designed to run both in early boot contexts with IRQs disabled and normal sleeping contexts.

## Risks and Edge Cases
The parser discards the entire input buffer when the first byte is not a valid HVSI header, trading data loss for resynchronization. The `for (tries = 1; count && tries < 2; tries++)` loop in `hvsilib_get_chars()` effectively permits one fetch cycle and should be checked against expected throughput. Carrier drop closes non-console opened sessions. `hvsilib_put_chars()` returns adjusted payload count rather than packet length on success.

## Test Signals
Signals include OPAL/VIO HVSI handshake, close/restart handshake recovery, data packet split reads, DTR set/clear, carrier-drop hangup via `-EPIPE`, early boot operation while IRQs are disabled, and tty kref balance across open/close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/hvsi_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/Makefile

## Purpose
The IPWireless Makefile declares how the IPWireless 3G PCMCIA driver is built. It builds a single composite module/object `ipwireless.o` when `CONFIG_IPWIRELESS` is enabled.

## Important APIs, Types, and Functions
There are no C APIs in this file. The important build variables are `obj-$(CONFIG_IPWIRELESS) += ipwireless.o` and `ipwireless-y := hardware.o main.o network.o tty.o`.

## Control Flow
Kbuild includes this Makefile from the parent tty build. When the config symbol is enabled, Kbuild links `hardware.o`, `main.o`, `network.o`, and `tty.o` into `ipwireless.o`.

## State and Persistence Behavior
The file has no runtime state. Its only persistent effect is the build graph.

## Dependencies and Integration Points
It integrates with Linux Kbuild and the `CONFIG_IPWIRELESS` Kconfig symbol. It establishes that `hardware.c` is not standalone; it links with the device, network, and tty layers.

## Risks and Edge Cases
Object ordering is simple and unlikely to be order-sensitive, but missing one of the listed objects would break unresolved symbols between hardware/network/tty layers. Disabled config means none of the IPWireless driver files are compiled.

## Test Signals
Build signals are `CONFIG_IPWIRELESS=m` producing `ipwireless.ko` and `CONFIG_IPWIRELESS=y` linking the objects into the kernel without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/hardware.c -->
# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/hardware.c

## Purpose
`hardware.c` is the low-level hardware/protocol engine for the IPWireless 3G PCMCIA driver. It manages card startup, version-specific I/O register access, transmit fragmentation, receive reassembly, setup protocol negotiation, modem-control signaling, interrupt handling, deferred bottom halves, and delivery to the network/tty-facing layer.

## Important APIs, Types, and Functions
The main private type is `struct ipw_hardware`, which owns base I/O addresses, hardware version, MTU, lock, setup timer, TX priority queues, RX queue/pool, packet assemblers, tasklet, work item, network pointer, memory-mapped register pointers, IRQ/removal/shutdown state, and control-line state.

Public functions are `ipwireless_hardware_create()`, `ipwireless_hardware_free()`, `ipwireless_interrupt()`, `ipwireless_set_DTR()`, `ipwireless_set_RTS()`, `ipwireless_send_packet()`, `ipwireless_associate_network()`, `ipwireless_stop_interrupts()`, `ipwireless_init_hardware_v1()`, `ipwireless_init_hardware_v2_v3()`, and `ipwireless_sleep()` as declared in the header. Internal core helpers include `do_send_fragment()`, `do_send_packet()`, `do_receive_packet()`, `queue_received_packet()`, `ipw_receive_data_work()`, `send_pending_packet()`, `ipwireless_do_tasklet()`, and setup handlers.

## Control Flow
Creation initializes queues, locks, tasklet, work item, and setup timer. Version init records I/O or memory-mapped register addresses and card callbacks. V2/V3 startup schedules `ipwireless_setup_timer()`, which periodically marks `to_setup`, resets TX readiness, and schedules the tasklet until version negotiation succeeds or retries are exhausted.

TX callers allocate an `ipw_tx_packet`, enqueue it by priority, and call `flush_packets_to_hw()`. The tasklet sends only setup priority while initialization is pending. `do_send_packet()` fragments logical packets into first/following NL fragments with protocol/address/rank headers, writes fragments through version-specific I/O, and requeues partially sent packets at high priority until complete.

Interrupt handling is version-specific. V1 reads/acks IOIR bits and sets `tx_ready` or increments `rx_ready`. V2/V3 reads memory status registers, detects old/new TX register mode, filters timer-recovery duplicate serials, marks RX/TX readiness, acknowledges PCMCIA interrupts, and schedules the tasklet. RX reads a fragment, swaps bitfields on big-endian systems, dispatches DATA/CTRL/SETUP protocols, assembles DATA by channel, queues completed packets, and uses process-context work to notify the network layer because tty flip paths can sleep.

## State and Persistence Behavior
All state is in `struct ipw_hardware` and runtime queues. `control_lines[]` preserves DTR/RTS/CTS/DCD/DSR/RI bits per channel. `packet_assembler[]` holds partially reassembled DATA packets. `rx_bytes_queued` and `blocking_rx` implement backpressure. `to_setup`, `initializing`, `init_loops`, `last_memtx_serial`, and `serial_number_detected` encode setup and interrupt recovery state. No state is persisted to disk.

## Dependencies and Integration Points
The file depends on Linux IRQ, tasklet, workqueue, timer, I/O accessor, spinlock, list, and allocation APIs. It integrates upward with `network.c` through `ipwireless_network_packet_received()`, `ipwireless_network_notify_control_line_change()`, and `ipwireless_ppp_mru()`. It uses setup protocol definitions from `setup_protocol.h` and device constants from `main.h`.

## Risks and Edge Cases
The driver mixes IRQ, tasklet, workqueue, timer, and process-context teardown, so `shutting_down`, timer deletion, `synchronize_irq()`, tasklet state, and `flush_work()` ordering are important. Several allocations in send paths use `GFP_ATOMIC`. RX backpressure blocks hardware reads once queued data exceeds `IPWIRELESS_RX_QUEUE_SIZE`. Bitfield byte order is manually swapped for big-endian builds. V2/V3 interrupt handling must distinguish real serial-numbered events from duplicate timer recovery interrupts and may switch between `memreg_tx_new` and old TX registers.

## Test Signals
Signals include card startup version query/response, fallback from TX2 to TX register, successful setup config/open/info exchange, DTR/RTS control packets, TX fragmentation across MTU boundaries, RX DATA reassembly, CTRL line-change notifications, queue backpressure/unblock, V1 and V2/V3 interrupt paths, reboot message ACK/callback, and clean shutdown/free with no callbacks after `ipwireless_stop_interrupts()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/hardware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/hardware.h -->
# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/hardware.h

## Purpose
`hardware.h` declares the public interface from the IPWireless hardware engine to the rest of the driver. It hides `struct ipw_hardware` internals and exposes lifecycle, interrupt, transmit, modem-control, network association, and version-specific initialization entry points.

## Important APIs, Types, and Functions
The header defines modem-control bit masks: `IPW_CONTROL_LINE_CTS`, `DCD`, `DSR`, `RI`, `DTR`, and `RTS`. It forward-declares `struct ipw_hardware` and `struct ipw_network`.

The exported functions are `ipwireless_hardware_create()`, `ipwireless_hardware_free()`, `ipwireless_interrupt()`, `ipwireless_set_DTR()`, `ipwireless_set_RTS()`, `ipwireless_send_packet()`, `ipwireless_associate_network()`, `ipwireless_stop_interrupts()`, `ipwireless_init_hardware_v1()`, `ipwireless_init_hardware_v2_v3()`, and `ipwireless_sleep()`.

## Control Flow
Higher layers allocate hardware state, initialize it for a card version with I/O/memory mappings and reboot callback, associate a network object, request IRQs using `ipwireless_interrupt()`, and then send data/control-line changes through this API. Teardown calls `ipwireless_stop_interrupts()` before freeing or disconnecting upper layers.

## State and Persistence Behavior
The header exposes no structure fields. State is owned by the opaque `ipw_hardware` implementation in `hardware.c`.

## Dependencies and Integration Points
It depends on kernel types, scheduler declarations, and interrupt return types. It is consumed by IPWireless main/network/tty code and implemented by `hardware.c`.

## Risks and Edge Cases
Callers must honor context expectations: `ipwireless_stop_interrupts()` must run in process context, send/control functions can allocate and queue work, and the IRQ handler expects a device object whose hardware pointer remains valid. Channel indices must correspond to `NO_OF_IPW_CHANNELS` used internally.

## Test Signals
Signals include successful compile-time linkage with the other IPWireless objects, correct modem-control bit propagation to tty/network layers, packet-sent callbacks from `ipwireless_send_packet()`, and teardown without IRQ/work callbacks after stop/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/hardware.h -->
