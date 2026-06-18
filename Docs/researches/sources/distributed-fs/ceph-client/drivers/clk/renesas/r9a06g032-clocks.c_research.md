
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a06g032-clocks.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a06g032-clocks.c

## Purpose
Implements the R9A06G032 system controller clock provider. Unlike the newer table-only Renesas CPG files, this driver owns a custom clock tree, special module gate sequencing, UART source selection, a generic PM domain that attaches managed clocks to devices, a DMAMUX register helper, USB host/device mode setup, and a restart handler.

## Important APIs, Types, And Functions
- `struct regbit`, `struct r9a06g032_gate`, and `struct r9a06g032_clkdesc` compactly describe system-controller bit locations, gate/reset/ready/idle controls, and each clock node.
- Descriptor macros `D_ROOT`, `D_FFC`, `D_DIV`, `D_GATE`, `D_MODULE`, and `D_UGATE` build the static `r9a06g032_clocks[]` table.
- `r9a06g032_sysctrl_set_dmamux()` is exported with `EXPORT_SYMBOL_GPL` and safely read-modify-writes the DMAMUX register.
- Custom CCF operations cover gates (`r9a06g032_clk_gate_ops`), dividers (`r9a06g032_clk_div_ops`), bit-select muxes (`clk_bitselect_ops`), and UART dual gates (`r9a06g032_clk_dualgate_ops`).
- `r9a06g032_clocks_probe()` registers all clocks, adds the OF onecell provider, installs the PM domain, sets reset policy, registers restart handling, and populates child devices.

## Control Flow
`subsys_initcall()` registers a platform driver for `renesas,r9a06g032-sysctrl`, then `platform_driver_probe()` calls the init-only probe. Probe allocates `r9a06g032_priv` and onecell storage, gets the external `mclk`, maps sysctrl registers, selects USB H2 mode based on a `renesas,rzn1-usbf` child node, clears stale reset causes, enables software/watchdog reset paths, and registers a restart handler. It iterates through `r9a06g032_clocks[]` in dependency order, resolving each parent from a prior clock index or `mclk`, and dispatches to fixed-factor, gate, divider, bit-select, or dual-gate registration. After registration it publishes the provider with `of_clk_add_provider()`, adds cleanup action, creates a genpd provider, saves `sysctrl_priv`, and populates child nodes.

## State And Persistence
Runtime state is the memory-mapped sysctrl register block and the singleton `sysctrl_priv`. Clock gate and DMAMUX writes are protected by `spinlock_t lock`. Gate enable writes the gate bit, deasserts reset, delays 5 us, sets ready, and clears the master idle request; disable reverses ready/idle and gate. Divider programming writes the divider value with bit 31 set as a latch bit. Restart persists only as a write to `RSTCTRL`. No filesystem or nonvolatile state is used.

## Dependencies And Integration Points
The driver integrates with Linux CCF, OF clock provider APIs, platform bus probing, generic PM domains, `pm_clk`, `of_platform_populate()`, sys-off restart registration, and the R9A06G032 DT binding IDs. It exposes the sysctrl DMAMUX helper through `<linux/soc/renesas/r9a06g032-sysctrl.h>`. Peripheral device nodes consume clocks through `#clock-cells`, while PM-domain attach scans each device's `clocks` property and only attaches descriptors marked `managed`.

## Risks And Edge Cases
Descriptor order is critical because parent names are pulled from already-registered clocks. Register offsets in `regbit` are encoded in 32-bit words, so byte/word confusion would toggle the wrong sysctrl bit. Some fields in `I_GATE()` are intentionally ignored, making table data look richer than the implementation. `clk_rdesc_get()` has no null-bit guard, so callers must avoid using the all-zero sentinel except where meaningful. Divider rate selection contains a UART-specific escape hatch to avoid changing shared UART group dividers. Gate registration marks already-enabled clocks critical because firmware or the CM3 may own them. `sysctrl_priv` is global and can return `-EPROBE_DEFER` to early DMAMUX consumers.

## Test Signals
Useful signals are successful boot on R9A06G032/RZN1 hardware, complete `/sys/kernel/debug/clk/clk_summary` registration, correct peripheral probe with PM clock attach/detach, working UART source switching without disabling the inactive group incorrectly, successful DMAMUX clients after probe, USB host/device mode matching DT, and successful `reboot` through the sysctrl restart path. Build coverage should include the exported symbol user and DT binding IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r9a06g032-clocks.c -->
