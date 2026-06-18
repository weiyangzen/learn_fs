
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-cpg-lib.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-cpg-lib.c

## Purpose
Provides shared helper code for R-Car CPG drivers, especially synchronized register modification, simple suspend/resume register save/restore, SD/SDH divider clocks, and RPC/RPCD2 composite clocks.

## Important APIs, Types, And Functions
- Defines global `DEFINE_SPINLOCK(cpg_lock)` exported via the header.
- `cpg_reg_modify()` performs locked read-modify-write on one MMIO register.
- `cpg_simple_notifier_call()` and `cpg_simple_notifier_register()` save a register on suspend and restore it on resume.
- `cpg_sdh_clk_register()` registers an SDH divider-table clock and registers a notifier for the SDnCKCR register.
- `cpg_sd_clk_register()` registers the lower SD divider.
- `cpg_rpc_clk_register()` registers a composite divider/gate RPC clock and a notifier for RPCCKCR.
- `cpg_rpcd2_clk_register()` registers a fixed divide-by-2 plus gate clock sharing RPCCKCR.

## Control Flow
Generation-specific drivers call these helpers from their `*_cpg_clk_register()` switch cases. Registration allocates small CCF wrapper structures, initializes divider/gate/fixed-factor members, and calls `clk_register_*` or `clk_register_composite()`. Suspend/resume notifiers are registered on the backend raw notifier chain; on suspend they read the saved register and on resume they restore it.

## State And Persistence
State includes the global spinlock, allocated wrapper objects, CCF clock hardware, and `struct cpg_simple_notifier.saved` snapshots across suspend/resume. Hardware state is SDnCKCR and RPCCKCR content. The helper supports reading legacy/firmware SDH divider encodings but Linux will sanitize by using recommended table entries.

## Dependencies And Integration Points
Used by R-Car Gen3 and Gen4 CPG code, and conceptually by shared CPG-MSSR registration. Depends on Linux CCF divider/gate/fixed-factor/composite operations, raw notifier chains, PM events, and MMIO helpers. The header declares its public surface.

## Risks And Edge Cases
All users share `cpg_lock`; mixing it with generation-local locks must avoid deadlock. The notifier only saves one 32-bit register per object and blindly restores it, so register fields controlled elsewhere during suspend must be considered. RPC and RPCD2 share RPCCKCR but only RPC owns the notifier. SDH divider tables include non-recommended encodings to tolerate firmware state, so initialization must normalize if needed.

## Test Signals
Build Gen3/Gen4 CPG drivers that call these helpers. On hardware, verify SDHI and RPC clocks register, gate, divide, and survive suspend/resume. Use clock debugfs to check rates and gates before and after PM cycles, and test concurrent clock rate/gate operations for lock coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-cpg-lib.c -->
