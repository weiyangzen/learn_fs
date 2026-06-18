# sources/distributed-fs/ceph-client/drivers/tty/serial/sh-sci-common.h

## Purpose

`sh-sci-common.h` is the shared private contract for the SuperH/Renesas SCI, SCIF, SCIFA, SCIFB, HSCIF, and RSCI serial implementations. It defines port type identifiers, clock and IRQ indexing, shared register-description structures, the `struct sci_port` extension of `struct uart_port`, operation tables, OF match payloads, exported helper prototypes, and early-console setup declarations. The source was read as a complete 184-line file.

## Important APIs, Types, and Functions

Important constants include private `enum SCI_PORT_TYPE` values for RSCI variants, `enum SCI_CLKS` clock indexes, `SCIx_*_IRQ` offsets, `SCI_SR()` and `SCI_SR_RANGE()` sampling-rate masks, and `SCI_NR_REGS`. `struct plat_sci_reg` describes per-register offset and access width. `struct sci_port_params_bits`, `struct sci_common_regs`, and `struct sci_port_params` describe type-specific enable bits, common register indexes, FIFO size, overrun/error behavior, and sampling-rate support.

`struct sci_port_ops` is the internal polymorphic interface for reading/writing registers, clearing status, TX/RX character movement, polling, RX trigger configuration, shutdown completion, console save/restore, and suspend-register sizing. `struct sci_of_data` is the OF match payload that selects params and operations. `struct sci_port` carries platform config, clocks, IRQ arrays, GPIO modem control, reset control, suspend save area, optional DMA channels/cookies/buffers/work/timers, RX FIFO tuning, type/regtype, and flow-control booleans. Public helpers declared here include `sci_startup()`, `sci_shutdown()`, resource helpers, PM helper, `sci_port_enable()`, `sci_port_disable()`, and `sci_scbrr_calc()`.

## Control Flow

This header has no executable control flow, but it defines the call graph shape used by `sh-sci.c` and RSCI support. Platform or OF probe fills a `struct sci_port` with params, ops, register type, IRQs, clocks, and flags. UART core operations call the helpers declared here, and the helpers dispatch through `sci_port_ops` where type-specific behavior is needed. Earlycon setup is conditionally exported through `scix_early_console_setup()`.

## State and Persistence Behavior

No storage is allocated by the header, but it defines all per-port runtime state for the SCI family. State includes clock handles/rates, IRQ names and numbers, DMA cookies and buffers, RX trigger/timeouts, saved suspend registers, GPIO modem control, reset control, and booleans such as `has_rtscts`, `autorts`, and `tx_occurred`. This state persists for the lifetime of each registered platform device and is reset or restored by the implementation during probe, shutdown, PM, and console handoff.

## Dependencies and Integration Points

The header includes `linux/serial_core.h` and assumes definitions from `linux/serial_sci.h`, DMA engine types, reset control, clocks, timers, and GPIO modem control are available to implementation users. It is consumed by `sh-sci.c` and by RSCI-related code included through `rsci.h`. The exported namespace `"SH_SCI"` lets related modules share the common helpers without exposing a generic user-space ABI.

## Risks and Edge Cases

Because this header is the internal ABI between SCI-family implementations, field ordering and semantic changes can break RSCI or OF data users. Register descriptors must match the hardware access width; a bad `.size` causes warning paths or wrong MMIO accesses. The private RSCI type IDs intentionally overlap generic UART type space using `BIT(7)`, so callers must use `SCI_PUBLIC_PORT_ID()` style translation before exposing port type to serial core. Optional DMA fields are present only under `CONFIG_SERIAL_SH_SCI_DMA`, so shared code must keep conditional layout and helper assumptions consistent.

## Test Signals

Compile tests with and without `CONFIG_SERIAL_SH_SCI_DMA`, `CONFIG_SERIAL_SH_SCI_EARLYCON`, and `CONFIG_SERIAL_RSCI` are essential. Probe tests for SCI, SCIF, HSCIF, and RSCI-compatible nodes should confirm `sci_of_data` to `sci_port` initialization. Namespace export users should link cleanly, and suspend/resume/earlycon tests should confirm the ops table contract is complete for every registered port family.
