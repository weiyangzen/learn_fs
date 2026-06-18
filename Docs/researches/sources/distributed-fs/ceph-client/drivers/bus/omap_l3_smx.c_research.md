# sources/distributed-fs/ceph-client/drivers/bus/omap_l3_smx.c

## Purpose
This is the OMAP3 L3 SMX interconnect error handler. It catches application/debug L3 interrupts, decodes 64-bit error logs into error code, initiator, command, and address information, reports severe bus faults, clears agent/error registers, and intentionally BUGs on timeout-class application errors.

## Important APIs, Types, and Functions
`omap3_l3_probe()` allocates `struct omap3_l3`, maps the single L3 MMIO resource, and requests debug/application IRQs. `omap3_l3_app_irq()` handles both IRQ types by choosing status register 0 or 1, using the first set bit to index `omap3_l3_bases`, reading `L3_ERROR_LOG` and `L3_ERROR_LOG_ADDR`, calling `omap3_l3_block_irq()`, and clearing status/log registers. Inline decode helpers extract code, address, command, initiator ID, and request info.

## Control Flow
The driver registers at `postcore_initcall_sync`. Probe uses non-devm allocation and manual unwind for IRQ and ioremap resources. On interrupt, the handler reads a 64-bit status word, finds the first set source with `__ffs`, derives the target block base from static arrays in the header, logs the decoded error, BUGs if application status includes `L3_STATUS_0_TIMEOUT_MASK`, clears IA/TA status, and writes the error log value back.

## State and Persistence
Runtime state is limited to mapped base and IRQ numbers in `struct omap3_l3`. The hardware error log is transient and cleared by the IRQ handler. There is no suspend/resume state or debugfs state.

## Dependencies and Integration Points
The driver depends on `omap_l3_smx.h` for register definitions and source-to-block maps, platform IRQ/resource setup, raw 64-bit MMIO access macros, and OF matching when built with OF. It integrates with platform diagnostics through `pr_err`, `WARN_ON`, and `BUG_ON`.

## Risks and Test Signals
Risks include `__ffs(status)` on a zero status if a spurious IRQ arrives, zero offsets for reserved status bits, deliberate kernel panic on timeout errors, and non-devm lifetime complexity. Test signals are accurate decoded messages for OMAP3 L3 faults, correct clearing of error status, clean remove path, and expected panic behavior only for real timeout-class faults.
