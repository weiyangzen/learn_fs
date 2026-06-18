# sources/distributed-fs/ceph-client/drivers/tty/ehv_bytechan.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/ehv_bytechan.c` implements TTY, console, and optional early udbg support for ePAPR hypervisor byte-channel devices on PowerPC. It exposes each device-tree byte channel as a `/dev/ttyEHV*` TTY, uses the `/chosen/stdout` byte channel as the kernel console, and sends/receives bytes through ePAPR hypercalls. The source was read as a complete 820-line file for this report.

## Important APIs, Types, and Functions

The main type is `struct ehv_bc_data`, holding device pointer, `tty_port`, hypervisor handle, RX/TX IRQs, a spinlock-protected transmit circular buffer, and TX interrupt enable state. Important globals are `bcs`, `stdout_bc`, `stdout_irq`, and `ehv_bc_driver`.

Important helpers include `find_console_handle`, `local_ev_byte_channel_send`, `enable_tx_interrupt`, `disable_tx_interrupt`, optional `udbg_init_ehv_bc`, `ehv_bc_console_write`, `ehv_bc_console_init`, `ehv_bc_tty_rx_isr`, `ehv_bc_tx_dequeue`, `ehv_bc_tty_tx_isr`, `ehv_bc_tty_write`, `ehv_bc_tty_open`, `ehv_bc_tty_close`, `ehv_bc_tty_write_room`, `ehv_bc_tty_throttle`, `ehv_bc_tty_unthrottle`, `ehv_bc_tty_hangup`, `ehv_bc_tty_port_activate`, `ehv_bc_tty_port_shutdown`, `ehv_bc_tty_probe`, and `ehv_bc_init`.

## Control Flow

Console init runs early, locates the device-tree stdout node if it is compatible with `epapr,hv-byte-channel`, reads its interrupt and `hv-handle`, adds it as the preferred `ttyEHV` console, and registers a console that spins on hypervisor send until output is accepted. Optional udbg setup verifies the configured handle with `ev_byte_channel_poll`, installs a putc hook, and emits early output before the normal console/TTY driver.

Driver init counts compatible nodes, allocates the `bcs` array, allocates/registers a dynamic TTY driver, and registers the platform driver. Probe reads each node's `hv-handle`, assigns line 0 to stdout and increasing indices to other byte channels, maps RX/TX IRQs, initializes a `tty_port`, and registers the TTY device.

TTY open delegates to `tty_port_open`. Port activation installs RX and TX IRQ handlers and disables TX IRQ until buffered output needs it. Writes copy bytes into the circular buffer under spinlock, then call `ehv_bc_tx_dequeue`, which sends chunks of up to `EV_BYTE_CHANNEL_MAX_BYTES` through hypercalls and enables TX IRQ when the hypervisor buffer is full. RX IRQs poll available bytes, reserve flip-buffer room, receive chunks from the byte channel, insert them into the TTY flip buffer, and push. Throttle/unthrottle disable and enable RX IRQs.

## State and Persistence Behavior

Per-channel state persists in `bcs[]` for the lifetime of the boot: hypervisor handles, mapped IRQs, `tty_port` state, TX buffer head/tail, and interrupt-enable tracking. Console state persists in `stdout_bc` and the registered `console`. The hypervisor owns the actual byte-channel queues. No filesystem-backed state is maintained.

## Dependencies and Integration Points

The driver depends on PowerPC ePAPR hypercall APIs (`ev_byte_channel_send`, `receive`, `poll`), Open Firmware device-tree parsing, IRQ mapping, TTY core, console subsystem, `tty_port`, flip buffers, circ-buffer helpers, optional PowerPC udbg, and the platform bus. Kconfig requires `PPC_EPAPR_HV_BYTECHAN` and selects `EPAPR_PARAVIRT`; early debug support uses `PPC_EARLY_DEBUG_EHV_BC`.

## Risks and Edge Cases

Hypervisor send requires at least the maximum byte-channel buffer size, so short writes are copied and padded locally. TX IRQ enable/disable is tracked manually because IRQ APIs are reference counted. RX throttling disables the Linux IRQ while the hypervisor may continue queueing data. `ehv_bc_tx_dequeue` advances the tail when the hypervisor accepts bytes or returns `EV_EAGAIN` with a valid partial length, so return-code semantics are important. The driver has no remove path and is initialized with `device_initcall`, matching platform lifetime assumptions.

## Test Signals

Useful signals include device-tree boots with and without `epapr,hv-byte-channel`; console selection through `/chosen/stdout`; optional udbg handle mismatch warning; `/dev/ttyEHV0` assigned to stdout and additional byte channels assigned increasing indices; RX/TX interrupt operation under sustained input/output; throttle/unthrottle behavior under TTY buffer pressure; TX IRQ only enabled when buffered output remains; and hypervisor `EV_EAGAIN` paths for full byte-channel queues.
