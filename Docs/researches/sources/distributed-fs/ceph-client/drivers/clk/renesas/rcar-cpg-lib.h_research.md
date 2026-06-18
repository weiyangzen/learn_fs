
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-cpg-lib.h -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-cpg-lib.h

## Purpose
Declares shared R-Car CPG helper APIs and data structures used by generation-specific CPG drivers.

## Important APIs, Types, And Functions
- Declares `extern spinlock_t cpg_lock`.
- Defines `struct cpg_simple_notifier` with a notifier block, MMIO register pointer, and saved 32-bit value.
- Declares `cpg_simple_notifier_register()` and `cpg_reg_modify()`.
- Declares clock registration helpers for SDH, SD, RPC, and RPCD2 clocks.

## Control Flow
This header has no executable flow. R-Car generation drivers include it and call the declared helpers while processing SoC-specific `cpg_core_clk` descriptors. The notifier structure is embedded in helper-allocated clock wrappers or allocated directly by generation drivers when a register must be restored after resume.

## State And Persistence
The header defines the shape of per-register suspend/resume state through `saved`. It also exposes the shared spinlock used by helper and generation code to serialize MMIO read-modify-write operations.

## Dependencies And Integration Points
Depends on CCF `struct clk`, Linux `__init`, `void __iomem`, and raw notifier infrastructure through included users. It is paired with `rcar-cpg-lib.c` and used by R-Car Gen3/Gen4 CPG implementations.

## Risks And Edge Cases
The shared lock is global, so users must avoid taking it recursively. Callers must pass valid CPG register addresses and notifier heads whose lifetime outlives registered notifiers. The helper declarations assume parent names are stable CCF names.

## Test Signals
Compile all users of the header. Runtime signals are indirect: successful registration of SDH/SD/RPC/RPCD2 clocks, correct rates/gates, and suspend/resume restoration for registers registered through `cpg_simple_notifier`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-cpg-lib.h -->
