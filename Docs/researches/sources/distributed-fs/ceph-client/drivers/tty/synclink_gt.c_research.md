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
