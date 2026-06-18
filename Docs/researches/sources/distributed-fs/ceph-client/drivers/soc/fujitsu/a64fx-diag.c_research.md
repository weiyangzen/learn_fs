
# sources/distributed-fs/ceph-client/drivers/soc/fujitsu/a64fx-diag.c

## Purpose
ACPI platform driver for Fujitsu A64FX diagnostic interrupts. It enables a BMC diagnostic interrupt bit and registers an NMI or IRQ handler that intentionally triggers a panic for crash dump collection.

## Important APIs, Types, and Functions
- `struct a64fx_diag_priv` stores MMSC register base, IRQ, and NMI mode.
- `a64fx_diag_probe()` maps registers, obtains IRQ index 1, requests NMI first and IRQ fallback, enables interrupt delivery, clears stale status, and enables BMC diagnostic interrupt.
- `a64fx_diag_remove()` disables/clears hardware and frees NMI/IRQ.
- Handlers are `a64fx_diag_handler_nmi()` and `a64fx_diag_handler_irq()`.

## Control Flow
Probe uses ACPI match `FUJI2007`, maps BAR 0, fetches platform IRQ 1, requests the interrupt with per-CPU/no-balance/no-thread/no-auto-enable flags, enables NMI or IRQ, clears any pending diagnostic status, and sets the enable bit. When triggered, the handler panics through `nmi_panic()` or `panic()`.

## State and Persistence
State is devm-managed private data plus hardware enable/status bits. The diagnostic enable bit persists while the driver is bound and is cleared on remove.

## Dependencies and Integration Points
Requires ACPI platform enumeration, interrupt/NMI APIs, and an MMSC register resource. BMC tooling triggers the hardware diagnostic request.

## Risks
- Interrupt delivery is deliberately fatal; accidental BMC requests panic the system.
- IRQ index is hard-coded to 1.
- `request_nmi()` fallback to normal IRQ changes panic path semantics.
- Uses non-devm `request_nmi()`/`request_irq()` and must free correctly on remove.

## Test Signals
ACPI match/probe, register status clear/enable/disable, NMI success path, IRQ fallback path, remove cleanup, and deliberate diagnostic interrupt causing expected panic path.
