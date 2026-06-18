# Research: subset-b-005465

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/synclink_gt.c -->
# Research: sources/distributed-fs/ceph-client/drivers/tty/synclink_gt.c

## Purpose

`synclink_gt.c` is the PCI tty and optional generic-HDLC network driver for Microgate SyncLink GT/GT2/GT4/AC serial adapters. It exposes ports as `ttySLG*` serial devices through `struct tty_driver`, and, when generic HDLC is configured, as HDLC-capable `net_device` instances. The driver owns register programming, interrupt dispatch, DMA descriptor rings, modem/GPIO events, tty line discipline handoff, and hardware diagnostics for each adapter port.

## Important APIs, Types, and Functions

The main device state is `struct slgt_info`, which embeds `struct tty_port`, PCI identity, per-port register mapping, `MGSL_PARAMS`, modem-signal counters, timers, workqueue state, DMA descriptor arrays, temporary receive storage, and optional HDLC netdev state. `struct slgt_desc` describes receive/transmit DMA buffers and stores both little-endian hardware fields and driver bookkeeping such as virtual buffer pointers and DMA addresses. `struct cond_wait` implements the file-local GPIO wait list.

TTY integration is through `ops`, with callbacks including `open`, `close`, `write`, `put_char`, `flush_chars`, `ioctl`, `throttle`, `unthrottle`, `send_xchar`, `break_ctl`, `wait_until_sent`, `set_termios`, `stop`, `start`, `hangup`, `tiocmget`, `tiocmset`, `get_icount`, and `proc_show`. Important ioctl helpers include `get_params`, `set_params`, `rx_enable`, `tx_enable`, `wait_mgsl_event`, `modem_input_wait`, `set_gpio`, `get_gpio`, `wait_gpio`, `set_interface`, `set_xsync`, and `set_xctrl`.

The optional HDLC path is centered on `hdlcdev_init`, `hdlcdev_open`, `hdlcdev_close`, `hdlcdev_attach`, `hdlcdev_ioctl`, `hdlcdev_xmit`, `hdlcdev_rx`, and `hdlcdev_tx_done`. Hardware control is split into `startup_hw`, `shutdown_hw`, `program_hw`, `change_params`, `async_mode`, `sync_mode`, `rx_start`, `rx_stop`, `tx_start`, `tx_stop`, `tx_load`, `rx_get_frame`, `rx_get_buf`, `rx_async`, and register helpers `rd_reg*`/`wr_reg*`.

## Control Flow

Module initialization allocates a dynamic tty driver, registers it, and registers a PCI driver. PCI probe calls `device_init`, which allocates one to four `slgt_info` ports based on PCI device ID, links them into the global list, initializes tty ports, registers optional HDLC devices, claims BAR memory on port zero, allocates DMA rings per port, requests the shared IRQ, runs `adapter_test`, then registers each tty device.

`open` resolves `tty->index` to a `slgt_info`, rejects devices with initialization errors, prevents concurrent HDLC use under `netlock`, increments `port.count`, starts hardware on the first open, and waits for carrier through `block_til_ready` unless nonblocking or `CLOCAL`. `close` drains transmit with `wait_until_sent`, flushes tty buffers and line discipline state, calls `shutdown_hw`, and drops the tty reference. `hangup` performs similar shutdown and wakes blocked opens.

Transmit data enters through `write` or `put_char`/`flush_chars`. Data is copied into the circular transmit DMA ring by `tx_load`; the first descriptor count is written last so an active DMA engine cannot observe a partially populated frame. `tx_start` enables the transmitter, programs the first descriptor address, arms TX interrupts, and starts TDMA. TX completion is detected by serial or TDMA interrupts, finalized in `isr_txeom`, and followed by either another pending DMA chain, HDLC queue wakeup, or tty wakeup through the bottom half.

Receive flow starts with `rx_start`, which resets descriptors, configures either PIO or DMA receive mode, enables receiver interrupts, and enables the receiver. Interrupts set `BH_RECEIVE`; `bh_handler` drains receive data according to mode. Async mode uses `rx_async` to convert byte/status pairs into tty flip-buffer characters. HDLC mode uses `rx_get_frame` to assemble one or more DMA buffers into `tmp_rbuf`, validate CRC/abort/short/long conditions, optionally deliver to generic HDLC, or pass to the tty line discipline. Raw/mono/bisync/xsync modes use `rx_get_buf`.

The shared ISR `slgt_interrupt` loops over global status bits, dispatches per-port serial, RX DMA, and TX DMA interrupts under each port spinlock, handles GPIO interrupts under the adapter lock, and schedules each port's work item when pending bottom-half work exists. Modem signal transitions update `signals`, `input_signal_events`, `icount`, event wait queues, carrier state, CTS flow state, and HDLC carrier state.

## State and Persistence Behavior

Persistent in-kernel state is per loaded module and per PCI device. The global `slgt_device_list` and `slgt_device_count` define tty line numbering. Per-port configuration persists in `info->params`, `if_mode`, `idle_mode`, `xsync`, `xctrl`, `base_clock`, `max_frame_size`, and modem output state until changed by termios or ioctl or until unload. Runtime state includes tty open counts, HDLC open count, DMA ring indexes, TX/RX enable flags, pending bottom-half bits, timers, wait queues, and counters in `mgsl_icount`.

No on-disk persistence is implemented. Hardware state is reprogrammed from `slgt_info` on `startup_hw`, `program_hw`, termios changes, HDLC attach/ioctl, and selected driver ioctls. `shutdown_hw` disables IRQ sources, stops DMA engines, clears waiters, optionally drops RTS/DTR for `HUPCL`, and marks the tty with `TTY_IO_ERROR`.

## Dependencies and Integration Points

The driver depends on the PCI core, tty core, tty ports, tty flip buffers, line disciplines, Linux timers/workqueues, coherent DMA allocation, memory-mapped I/O, wait queues, generic HDLC when configured, and Microgate definitions from `linux/synclink.h`. User space integrates through `/dev/ttySLG*`, termios, modem ioctls, Microgate-specific `MGSL_*` ioctls, optional HDLC netdev ioctls, `/proc/tty/driver` style `proc_show`, and module parameters `ttymajor`, `debug_level`, and `maxframe`.

The hardware register map is abstracted by `calc_regaddr`, which applies per-port offsets for global, extended, and per-channel registers. The first port owns adapter-level resource release and IRQ registration, while all ports share the BAR and IRQ.

## Risks and Edge Cases

DMA addresses are truncated to 32 bits in descriptor setup and descriptor-list address math (`(unsigned int)bufs_dma_addr`, `(unsigned int)buf_dma_addr`) without an explicit DMA mask setup visible in this file. That is only safe if the device and DMA API always return 32-bit addresses for this PCI device.

`change_params` sets `read_status_mask` each call but does not clear `ignore_status_mask` before OR-ing termios-derived bits, so ignore behavior can persist after termios flags are later cleared. `remove_one` is empty, so hot-unplug/remove behavior relies on module cleanup rather than per-device teardown. `device_init` does not check the return value of `alloc_dma_bufs` after claiming resources, so later initialization may proceed with missing DMA buffers. `register_test` appears to set `init_error` to success on failure and address failure on success (`info->init_error = rc ? 0 : DiagStatus_AddressFailure`), which is suspicious compared with the later tests.

Concurrency risk centers on shared state touched by IRQ, timers, tty callbacks, and HDLC callbacks. Most descriptor and signal state is protected with `info->lock`, but some fields such as `bh_running` and `bh_requested` are also read or written in workqueue context. GPIO waits are linked through `gpio_wait_q` and must be removed carefully on interrupt, signal, or shutdown. The receive path uses a single temporary buffer for synchronous frame delivery, so it assumes bottom-half serialization per port.

## Test Signals

Built-in diagnostic signals are `register_test`, `irq_test`, and `loopback_test`, run during adapter initialization; failures set `init_error` and print kernel messages. Runtime test signals include tty open/write/read with termios transitions, `TIOCMIWAIT`, `MGSL_IOCWAITEVENT`, GPIO wait ioctls, CTS/RTS hardware flow, DCD carrier behavior, HDLC attach/open/xmit/timeout paths, RX CRC/abort/overrun counters, TX underrun/timeout counters, and module unload cleanup. Static review should specifically exercise 64-bit DMA addressing assumptions, remove/hotplug behavior, error unwinding after partial DMA allocation, and termios flag toggling for parity/break ignore masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/synclink_gt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/sysrq.c -->
# Research: sources/distributed-fs/ceph-client/drivers/tty/sysrq.c

## Purpose

`sysrq.c` implements Linux Magic SysRq handling for the tty/input subsystem. It maps SysRq keys to privileged emergency operations, exposes registration APIs for modules, handles `/proc/sysrq-trigger`, manages the `/proc/sys/kernel/sysrq` sysctl mask, and, when input support is enabled, filters keyboard input to detect Alt-SysRq combinations and optional reset key sequences.

## Important APIs, Types, and Functions

Global configuration is held in `sysrq_enabled` and `sysrq_always_enabled`. `sysrq_mask`, `sysrq_toggle_support`, `handle_sysrq`, `__handle_sysrq`, `register_sysrq_key`, and `unregister_sysrq_key` are the primary external interfaces. `sysrq_key_table` maps digits and letters to `struct sysrq_key_op` handlers. Built-in handlers cover loglevel, SAK, unraw keyboard mode, crash, reboot, sync, timer display, remount read-only, lock display, CPU backtraces, register display, task state, blocked tasks, ftrace dump, memory display, SIGTERM/SIGKILL to user tasks, manual OOM, filesystem thaw, RT task normalization, and console log replay.

With `CONFIG_INPUT`, `struct sysrq_state` stores per-input-device filter state: input handle, reinjection work, pressed-key bitmaps, active Alt/SysRq state, shift state, reset-sequence state, and reset timer. The input path uses `sysrq_filter`, `sysrq_handle_keypress`, `sysrq_reinject_alt_sysrq`, `sysrq_connect`, and `sysrq_disconnect`. Reset-sequence configuration is provided by device tree (`/chosen/linux,sysrq-reset-seq`) and module parameters `reset_seq` and `sysrq_downtime_ms`.

## Control Flow

At device init time, `sysrq_init` creates `/proc/sysrq-trigger` when procfs is enabled and registers the input handler if SysRq is enabled. A separate `subsys_initcall` registers the sysctl table for `kernel.sysrq`. The `sysrq_always_enabled` boot option bypasses normal mask disabling.

Programmatic handling enters `handle_sysrq`, which checks `sysrq_on` and delegates to `__handle_sysrq` with mask checking. `/proc/sysrq-trigger` calls `__handle_sysrq` without mask checks; when the first written byte is `_`, it processes all following bytes as a bulk sequence. `__handle_sysrq` temporarily unsuppresses printk, enters RCU SysRq context, forces console printing for feedback, looks up the operation, enforces the enable mask if requested, runs the handler, or prints one help entry for each unique registered operation.

The input path registers on devices with `EV_KEY` and `KEY_LEFTALT`. `sysrq_filter` suppresses or passes events. `sysrq_handle_keypress` tracks Alt, Shift, and SysRq; once Alt-SysRq is active, the next non-repeat key is translated through `sysrq_xlate`, optionally uppercased by Shift, and passed to `__handle_sysrq`. If Alt-SysRq was pressed without a command, `sysrq_reinject_alt_sysrq` simulates the original key chord so normal PrintScreen behavior can still occur. Reset-sequence tracking runs when SysRq is inactive and calls `orderly_reboot` or falls back to SysRq reboot after configured key hold timing.

## State and Persistence Behavior

State is kernel-resident and lasts until reboot or module lifetime. The sysctl changes `sysrq_enabled` at runtime and registers or unregisters the input handler when the effective enabled state changes. Registered key operations mutate `sysrq_key_table` under `sysrq_key_table_lock` and use `synchronize_rcu` to prevent module text from being freed while a concurrent handler is running. Each input device gets separate `sysrq_state`; timers and work are torn down on disconnect.

## Dependencies and Integration Points

The file integrates with printk/console control, RCU, reboot/panic paths, emergency sync/remount/thaw, OOM, scheduler diagnostics, lockdep, ftrace, perf debug, VT keyboard support, input core, procfs, sysctl, device tree, and module parameter handling. It exports SysRq registration and dispatch symbols to other kernel code.

## Risks and Edge Cases

SysRq handlers are intentionally powerful and include crash, reboot, process kill, OOM, and remount operations; incorrect enable-mask configuration has direct system-availability impact. Some handlers run from constrained contexts, so the code schedules work for operations such as SAK, manual OOM, and remote CPU backtraces when direct execution is unsafe. Input reinjection uses memory barriers around `reinjecting`; regressions there could either leak Alt-SysRq events or suppress normal keyboard input. Key-table mutation relies on exact old-op matching, so unregistering with the wrong pointer fails. `/proc/sysrq-trigger` intentionally bypasses the sysctl operation mask, so access mode and ownership are the relevant control.

## Test Signals

Useful tests include sysctl toggling of `kernel.sysrq`, direct `handle_sysrq` calls from kernel tests, `/proc/sysrq-trigger` single and bulk writes, registration/unregistration of a temporary key op, input-event simulation for Alt-SysRq with and without a command key, reset sequence parsing through module parameters/device tree, and config-matrix builds for `CONFIG_INPUT`, `CONFIG_VT`, `CONFIG_LOCKDEP`, `CONFIG_SMP`, `CONFIG_TRACING`, `CONFIG_BLOCK`, and `CONFIG_PROC_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/sysrq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty.h -->
# Research: sources/distributed-fs/ceph-client/drivers/tty/tty.h

## Purpose

`tty.h` is the private internal header for the tty core. It centralizes tty-core logging helpers, lock subclass identifiers, flow-change state helpers, and prototypes shared among tty implementation files without exposing them as public UAPI.

## Important APIs, Types, and Functions

The logging helpers `tty_msg`, `tty_debug`, `tty_notice`, `tty_warn`, `tty_err`, and `tty_info_ratelimited` prefix messages with the driver and tty names. The `TTY_LOCK_NORMAL` and `TTY_LOCK_SLAVE` enum values define lockdep subclasses for nested tty, pty, termios, and flip-buffer locking. `enum tty_flow_change` and the inline helpers `__tty_set_flow_change` and `tty_set_flow_change` update `tty->flow_change`; the public helper includes an `smp_mb()` so other CPUs observe the flow-state transition in order.

The header declares internal tty functions for line discipline locking/lifecycle, write locking, job control, tty file allocation/release, session handling, hangup, default file operations, tty buffer lifecycle/work control, baud-rate helpers, audit hooks, redirected writes, and `tty_insert_flip_string_and_push_buffer`.

## Control Flow

This file does not implement runtime control flow beyond the inline flow-change setters. Its role is compile-time coupling: tty core translation units include it to call private helpers implemented in files such as tty buffer, line discipline, audit, IO, and baud-rate code. When `CONFIG_AUDIT` is disabled, audit hooks collapse to no-op inline functions, avoiding conditional code in callers.

## State and Persistence Behavior

The header itself owns no persistent state. It defines how callers update state in `struct tty_struct` and `struct tty_port`, especially `tty->flow_change`, buffer work state, and lock subclass metadata. The memory barrier in `tty_set_flow_change` is the main state-ordering behavior.

## Dependencies and Integration Points

The header depends on tty core types such as `struct tty_struct`, `struct tty_port`, `struct tty_ldisc`, `struct file`, `struct inode`, `struct pid`, `struct ktermios`, `struct iov_iter`, and `struct kiocb` from surrounding kernel headers. It is used internally by tty implementation files and is not a stable external interface.

## Risks and Edge Cases

Because this header declares private cross-file contracts, signature drift can break tty core builds broadly. Lock subclass comments document required pty lock ordering; callers that ignore those subclasses can trigger false lockdep reports or real ABBA deadlocks. The no-op audit stubs must exactly match enabled prototypes so callers remain config-independent. The memory barrier in `tty_set_flow_change` should not be removed without revalidating throttle/unthrottle synchronization.

## Test Signals

Build coverage across `CONFIG_AUDIT` enabled and disabled is essential. Runtime signals include lockdep-enabled pty pair operations, nested tty close/hangup paths, flow-control transitions, line discipline setup/release, and flip-buffer push paths that use internal prototypes from this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_audit.c -->
# Research: sources/distributed-fs/ceph-client/drivers/tty/tty_audit.c

## Purpose

`tty_audit.c` records audited tty input for tasks whose `signal_struct` has tty auditing enabled. It batches input bytes into a per-signal audit buffer, emits `AUDIT_TTY` records with task and tty metadata, logs `TIOCSTI` injection separately, and flushes/free buffers on explicit push and task exit.

## Important APIs, Types, and Functions

`struct tty_audit_buf` stores a mutex, source `dev_t`, canonical-mode flag, valid byte count, and a 4096-byte data allocation. `tty_audit_add_data` is the main input ingestion API. `tty_audit_tiocsti` logs injected characters. `tty_audit_push` flushes the current task's buffer if tty audit is enabled. `tty_audit_exit` pushes and frees a task's buffer during signal teardown, and `tty_audit_fork` copies the audit enable flags to a new signal struct.

Internal helpers include `tty_audit_buf_ref`, `tty_audit_buf_alloc`, `tty_audit_buf_free`, `tty_audit_buf_get`, `tty_audit_buf_push`, and `tty_audit_log`.

## Control Flow

`tty_audit_add_data` first reads `current->signal->audit_tty`; if tty auditing is disabled, size is zero, the tty is a PTY master, or password-style canonical no-echo input should be hidden without `AUDIT_TTY_LOG_PASSWD`, it returns without logging. Otherwise it allocates or retrieves the current signal's buffer, locks it, flushes if the tty device or canonical mode changed, copies data in chunks until the 4096-byte buffer fills, and pushes whenever full.

`tty_audit_push` validates `AUDIT_TTY_ENABLE`, locks the existing buffer if present, and emits pending data. `tty_audit_tiocsti` computes the tty device number, pushes prior buffered data so ordering is preserved, and emits an `ioctl=TIOCSTI` audit record for the injected byte. `tty_audit_exit` atomically marks the signal buffer as exited with `ERR_PTR(-ESRCH)`, pushes final data, and frees the allocation.

## State and Persistence Behavior

Audit buffering is per `signal_struct` via `current->signal->tty_audit_buf`, so threads in the same thread group share the same buffer and mutex. Buffered data persists until full, pushed, device/mode changes, audit disabled, or task exit. Records are persisted only through the kernel audit subsystem; this file does not write storage directly.

## Dependencies and Integration Points

The code depends on the audit subsystem (`audit_log_start`, `audit_context`, `audit_log_n_hex`, `audit_enabled`, loginuid/session helpers), tty driver identity, task credentials, task command names, slab allocation, and the private tty header for declarations. It is compiled behind `CONFIG_AUDIT`; callers use no-op stubs from `tty.h` otherwise.

## Risks and Edge Cases

The shared per-signal buffer requires correct mutex use across multiple threads. `tty_audit_exit` uses an `ERR_PTR(-ESRCH)` sentinel; callers must tolerate that value and avoid dereferencing it. Out-of-memory drops audit data and calls `audit_log_lost`. Password filtering depends on canonical mode and echo state, so noncanonical sensitive input may still be logged if tty audit policy requests it. Audit-disabled transitions clear pending bytes without emission.

## Test Signals

Test coverage should include audit enabled/disabled tasks, fork inheritance of `audit_tty`, canonical echo and no-echo input, PTY master exclusion, buffer-full flushing at 4096 bytes, device/mode-change flushing, `TIOCSTI` ordering, out-of-memory/lost audit behavior, and exit-time flushing/freeing for single-threaded signal teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_baudrate.c -->
# Research: sources/distributed-fs/ceph-client/drivers/tty/tty_baudrate.c

## Purpose

`tty_baudrate.c` converts between termios baud-rate bit encodings and numeric `speed_t` rates, including `BOTHER` arbitrary speeds and independent input/output speeds. It also lets drivers encode actual selected speeds back into `ktermios` so user space can observe the real configured rate.

## Important APIs, Types, and Functions

`baud_table` maps termios baud indexes to numeric speeds, and `baud_bits` maps the same indexes back to `B*` constants. The table is architecture-sensitive for sparc. `tty_termios_baud_rate` returns output speed from `c_cflag`, `tty_termios_input_baud_rate` returns input speed from the `IBSHIFT` field or falls back to output speed for `B0`, `tty_termios_encode_baud_rate` rewrites `c_cflag`, `c_ispeed`, and `c_ospeed`, and `tty_encode_baud_rate` applies the same encoding to `tty->termios`.

## Control Flow

Decode helpers mask out `CBAUD`, handle `BOTHER` by returning `c_ospeed` or `c_ispeed`, handle extended baud values by removing `CBAUDEX` and adding the legacy offset, and return zero for indexes outside `baud_table`.

Encoding stores exact numeric speeds in `c_ispeed` and `c_ospeed`, clears old output and input baud bits, detects whether the user explicitly requested separate input speed, and scans the known baud table for rates within a tolerance of `rate / 50`. If output or input speed is close to a standard baud, it encodes the corresponding `B*` bits. If not, it uses `BOTHER`, preserving exact speeds in the numeric fields. `obaud == 0` also forces input speed to zero for hangup semantics.

## State and Persistence Behavior

This file has no independent runtime state beyond static lookup tables. It mutates caller-owned `struct ktermios` or `tty->termios` in place. Callers are expected to hold the termios lock when operating on live tty termios.

## Dependencies and Integration Points

The code depends on termios constants (`CBAUD`, `CBAUDEX`, `BOTHER`, `IBSHIFT`, and `B*` rates), tty core types, and export symbols. Drivers call these helpers from termios handlers when reporting actual hardware rates, and tty core code uses them to decode user-requested speeds.

## Risks and Edge Cases

The baud tables must remain aligned with architecture termbits definitions; a mismatch decodes or reports wrong rates. The tolerance behavior intentionally reports near-standard rates as standard `B*` values, which preserves compatibility but can hide small hardware rounding differences. Arbitrary speeds require correct `BOTHER` support in user space and architecture headers. Input-speed bits are omitted when input equals output and the user did not explicitly request a separate input speed.

## Test Signals

Tests should cover all standard baud constants, extended rates, sparc/non-sparc table variants, `BOTHER` exact speeds, `B0` hangup behavior, separate input/output rates, near-match tolerance, no-match fallback to `BOTHER`, and live `tty_encode_baud_rate` calls under termios locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_baudrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_buffer.c -->
# Research: sources/distributed-fs/ceph-client/drivers/tty/tty_buffer.c

## Purpose

`tty_buffer.c` implements tty flip-buffer allocation, queuing, flushing, and delivery to tty clients/line disciplines. It provides the producer-side APIs used by drivers to insert received bytes and the consumer-side workqueue path that forwards committed data in order.

## Important APIs, Types, and Functions

The file operates on `struct tty_port` and its `struct tty_bufhead`. Exported APIs include `tty_buffer_lock_exclusive`, `tty_buffer_unlock_exclusive`, `tty_buffer_space_avail`, `tty_buffer_free_all`, `tty_buffer_flush`, `tty_buffer_request_room`, `__tty_insert_flip_string_flags`, `tty_prepare_flip_string`, `tty_ldisc_receive_buf`, `tty_flip_buffer_push`, `tty_buffer_set_limit`, plus internal work controls declared through `tty.h`: `tty_buffer_init`, `tty_buffer_set_lock_subclass`, `tty_buffer_restart_work`, `tty_buffer_cancel_work`, and `tty_buffer_flush_work`.

Key helpers are `tty_buffer_alloc`, `tty_buffer_free`, `__tty_buffer_request_room`, `lookahead_bufs`, `receive_buf`, `flush_to_ldisc`, and `tty_flip_buffer_commit`. Constants define minimum allocation size, 256-byte alignment, default memory limit, and page-friendly chunk sizing.

## Control Flow

Drivers reserve space with `tty_buffer_request_room`, `tty_prepare_flip_string`, or insertion helpers. `__tty_buffer_request_room` either uses space in the current tail buffer or allocates a new aligned buffer, commits the old tail with release ordering, links the new buffer with release ordering, and returns available linear space. Insert helpers copy character data and optional flag data into the tail and advance `used`.

Once a driver has produced data, `tty_flip_buffer_push` commits `tail->used` to `tail->commit` with release ordering and queues `buf.work`. `flush_to_ldisc` runs as the serialized consumer under `buf->lock`: it stops if exclusive priority is active, advances past empty committed buffers, calls the tty client `receive_buf` callback for readable bytes, zeros consumed character data, updates `read`, invokes lookahead when the consumer accepted only part of a buffer, frees fully consumed old buffers, and yields with `cond_resched`.

Flush and teardown paths use `tty_buffer_flush` to discard queued receive data and optionally flush the line discipline, and `tty_buffer_free_all` to release active and free-list buffers when the tty is no longer in use. Exclusive locking increments `priority`, takes the buffer mutex, and later queues work again if unread committed bytes remain.

## State and Persistence Behavior

Buffer state is per tty port. `buf->head` points to the consumer buffer, `buf->tail` to the producer buffer, `sentinel` anchors an empty queue, `free` caches small buffers, `mem_used` tracks allocated buffer payload bytes, `mem_limit` bounds allocation, `priority` blocks worker consumption for exclusive users, and `work` performs deferred delivery. Data persists in memory until delivered, flushed, or freed; no data is persisted outside tty consumers.

Memory ordering is part of the state contract: producers publish `commit` and `next` with `smp_store_release`, while consumers and flush/lookahead paths use acquire loads to see initialized buffer contents and links.

## Dependencies and Integration Points

The code integrates with tty drivers through flip-buffer insertion APIs, tty ports, tty client operations (`receive_buf` and optional `lookahead_buf`), line discipline receive callbacks (`receive_buf`/`receive_buf2`), workqueues, llist free buffers, atomic counters, mutexes, lockdep subclasses, and memory allocation. PTY code uses `tty_insert_flip_string_and_push_buffer` to combine insertion and push under `port->lock`.

## Risks and Edge Cases

The effective memory use can exceed `mem_limit` because buffers store both data and flags and allocation is checked before a new buffer is added. Producers can still fail allocation in atomic context; callers must handle short insertion. Partial line-discipline consumption triggers lookahead and leaves data queued, so receive callbacks must make forward progress or work will repeatedly stop. Exclusive access relies on balanced priority increments/decrements. Incorrect release/acquire ordering would risk consumers observing uninitialized data or broken buffer links.

## Test Signals

Important tests include high-rate driver insertion, allocation failure and memory-limit behavior, flagless-to-flagged buffer transitions, partial `receive_buf2` consumption, lookahead callbacks, exclusive lock/unlock with pending bytes, flush during concurrent producer activity, work cancellation/restart, small-buffer free-list reuse, `tty_buffer_set_limit` validation, and lockdep coverage for slave pty subclassing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_buffer.c -->
