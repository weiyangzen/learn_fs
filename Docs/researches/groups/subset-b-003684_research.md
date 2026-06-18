# subset-b-003684 research

Grouped research for Nouveau NVKM clock, devinit, and fault subdevice files under the ceph-client source tree. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/base.c

## Purpose
Implements the common NVKM clock subdevice policy: BIOS/static pstate discovery, cstate selection, voltage/fan sequencing, power-source and thermal reclock triggers, and the subdevice init/fini/dtor glue used by all Nouveau clock families.

## Important APIs, types, and functions
Key entry points are `nvkm_clk_ctor()`, `nvkm_clk_new_()`, `nvkm_clk_read()`, `nvkm_clk_ustate()`, `nvkm_clk_astate()`, `nvkm_clk_tstate()`, `nvkm_clk_dstate()`, and `nvkm_clk_pwrsrc()`. Internals include `nvkm_pstate_new()`, `nvkm_cstate_new()`, `nvkm_cstate_prog()`, `nvkm_pstate_work()`, and BIOS boost/perf/cstep parsing through `nvbios_*` helpers.

## Control flow
Construction builds the pstate list from a family static table or VBIOS performance tables, applies `NvClkMode*` options, and records VP-state base/boost caps. Init snapshots boot clocks into `bstate`, calls family `init` when present, otherwise chooses the highest application state and schedules a synchronous pstate calculation. Pstate work merges user AC/DC state, automatic state, thermal lower bound, and power-source selection, then programs PCIe link, RAM timing, fan, voltage, and family `calc/prog/tidy` hooks.

## State and persistence
Persistent runtime state lives in `struct nvkm_clk`: pstate/cstate lists, boot-state snapshot, current pstate, user/auto/thermal state requests, temperature, boost limits, waitqueue/work item, and family function pointers. Hardware persistence is delegated to family hooks and voltage/thermal/PCIe/fb subdevices.

## Dependencies and integration points
Depends on BIOS perf/cstep/boost/vpstate tables, `nvkm_volt`, `nvkm_therm`, `nvkm_fb` RAM callbacks, PCIe link management, power supply state, and the `nvkm_subdev` lifecycle. It is the integration point for sysfs/debug/user reclock requests and thermal/power policy.

## Risks
The state resolver is global policy for reclocking. Bad voltage mapping, cstate validity, workqueue waiting, or pstate index conversion can select unsafe clocks or leave callers waiting. The destructor intentionally skips freeing static pstate arrays, so mixed static/dynamic state ownership must remain clear.

## Test signals
Useful signals are `nvkm_trace()` pstate decisions, pstate info debug lines, voltage/fan error logs, suspend/resume reclock behavior, `NvClkMode*` option parsing, and stress that changes AC/DC power, temperature, and user requested states while memory reclocking is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/g84.c

## Purpose
Defines the G84 clock constructor by reusing the NV50 clock engine with a G84/G9x domain table and chipset-specific reclocking enablement.

## Important APIs, types, and functions
The file exports `g84_clk_new()`. Its static `g84_clk` function table points at `nv50_clk_read()`, `nv50_clk_calc()`, `nv50_clk_prog()`, and `nv50_clk_tidy()` with crystal, href, core, shader, memory, and vdec domains.

## Control flow
Construction delegates to `nv50_clk_new_()` and passes `allow_reclock` only for chipsets `>= 0x94`. All real read/calc/prog control flow is inherited from `nv50.c`.

## State and persistence
No local state is introduced. State lives in the allocated `struct nv50_clk`, its hardware-sequencer register descriptors, and the common `struct nvkm_clk` pstate state.

## Dependencies and integration points
Depends on `nv50.h` and the NV50 family implementation. Integrated by the device chipset table for G84-class GPUs.

## Risks
The domain table and reclocking gate are compatibility-sensitive. Enabling reclocking on unsupported early chipsets would run the NV50 hwsq program against hardware paths that may not be safe.

## Test signals
Build linkage of `g84_clk_new()`, boot clock readout, pstate list creation, and reclocking on 0x94+ boards are the main signals; earlier chipsets should expose clocks without allowing dynamic reclock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gf100.c

## Purpose
Implements GF100/Fermi clock reading and reclocking for GPC, ROP, HUBK, copy, PMU, VDEC, and memory-related sources using the Fermi clock tree registers.

## Important APIs, types, and functions
Important functions include `gf100_clk_read()`, `gf100_clk_calc()`, `gf100_clk_prog()`, `gf100_clk_tidy()`, `gf100_clk_new()`, and helpers `read_pll()`, `read_div()`, `read_clk()`, `calc_src()`, `calc_pll()`, and staged `gf100_clk_prog_0..4()`. `struct gf100_clk_info` caches per-engine target source/divider/PLL data.

## Control flow
Reads decode PLL enable/coefficients, mux sources, fixed 27/100/108 MHz paths, divider control, and special memory PLL selection. Calculation tries divider-only output first, then PLL plus final divider for selectable domains, choosing the closest result. Programming is staged across all engines: program divider sources, switch to divider mode, disable/reprogram/lock PLLs, select PLL mode when requested, and finally program output dividers.

## State and persistence
Transient calculation state is stored in `clk->eng[16]` and cleared by `tidy()`. Persistent hardware state is Fermi clock MMIO including 0x137xxx source/select/divider registers and PLL coefficient/control registers.

## Dependencies and integration points
Depends on BIOS PLL limits, `gt215_pll_calc()`, common pstate/cstate policy, and timer polling for PLL lock. Integrated as the GF100 `nvkm_clk_func` with VP-state core domain support but reclocking disabled in constructor.

## Risks
PLL lock waits and source switching order are critical. A bad source mask or coefficient can hang an engine clock, while returning zero for unreadable PLLs may make pstate validation silently fail. Memory clock is read but not programmed here.

## Test signals
Clock debug readouts for all listed domains, PLL-lock timeout behavior, pstate calculation error paths, and comparison of requested versus `info->freq` are useful. Hardware testing should include Fermi boards with varied BIOS PLL tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk104.c

## Purpose
Implements GK104/Kepler desktop clock reading and reclocking, extending the Fermi-style engine clock tree with Kepler fractional memory/source behavior and wider engine coverage.

## Important APIs, types, and functions
Exports `gk104_clk_new()`. Core functions are `gk104_clk_read()`, `gk104_clk_calc()`, `gk104_clk_prog()`, and `gk104_clk_tidy()`, with helpers `read_pll()`, `read_div()`, `read_mem()`, `read_clk()`, `calc_src()`, and `calc_pll()`.

## Control flow
Reads distinguish fixed references, VCO paths, memory PLL source selection, and high-index engine special cases. Calculation follows a divider-only path first, then a PLL path for supported engines, recording select bits and divider fields. Programming is split into masked stages so low-index and high-index engines switch muxes and PLL source bits in a safe order.

## State and persistence
`struct gk104_clk_info eng[16]` stores planned source/divider/PLL fields until `prog()` and is cleared by `tidy()`. Persistent state is the 0x137xxx Kepler clock register set and source PLLs.

## Dependencies and integration points
Uses BIOS PLL parsing, `gt215_pll_calc()`, common `nvkm_clk_ctor()`, and timer polling. Its domain table marks GPC/HUBK/ROP as core-related and GPC as VP-state relevant; constructor enables reclocking.

## Risks
Programming masks differ for low and high clock domains; incorrect staging can switch a domain to a disabled source. Fractional memory PLL reads and `fN` handling must match hardware or reported memory rates are wrong.

## Test signals
Reclock pstate transitions, engine frequency readback, PLL lock status, and debug logs for invalid sources are the main signals. Kepler boards with multiple pstate entries and memory PLL source modes are important coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a.c

## Purpose
Implements Tegra GK20A GPU GPC clock control using the GPCPLL, static pstate table, dynamic NDIV sliding, PLL enable/disable sequencing, and devfreq initialization.

## Important APIs, types, and functions
Exports shared helpers declared in `gk20a.h`: `gk20a_pllg_read_mnp()`, `gk20a_pllg_write_mnp()`, `gk20a_pllg_calc_rate()`, `gk20a_pllg_calc_mnp()`, `gk20a_clk_read()`, `gk20a_clk_calc()`, `gk20a_clk_prog()`, `gk20a_clk_setup_slide()`, `gk20a_clk_fini()`, `gk20a_clk_ctor()`, and `gk20a_clk_new()`.

## Control flow
PLL calculation searches M/N/PL under VCO and input-frequency limits, preferring the lowest usable VCO and closest target. Programming tries an NDIV slide when M and PL are unchanged; otherwise it slides down to a safe low NDIV, programs MNP through bypass with output divider staging, re-enables and locks the PLL, then slides up. Init exits IDDQ, initializes GPC2CLK output, configures slide step parameters from the Tegra parent clock, programs the lowest pstate, and starts devfreq.

## State and persistence
State is in `struct gk20a_clk`: PLL params, cached target PLL, parent rate, conversion callbacks, and devfreq pointer. Hardware state persists in GPCPLL coefficient/config, NDIV slowdown, SEL_VCO, and GPC2CLK_OUT registers.

## Dependencies and integration points
Depends on Tegra platform clock rate, NVKM timer waits, the common clock pstate engine, and `gk20a_devfreq_init()`. Static pstates cover 72 MHz through 852 MHz with voltage IDs.

## Risks
Dynamic ramp completion has a 500 usec timeout, and fallback full programming still depends on PLL lock. Parent rates outside the known table fail init. Incorrect PL/div conversion would make reported and programmed rates diverge.

## Test signals
Boot init at lowest pstate, devfreq OPP registration, rate readback after every pstate, NDIV slide timeout logs, suspend/fini IDDQ behavior, and parent-rate validation on 12/12.8/13/19.2/38.4 MHz Tegra clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a.h

## Purpose
Defines GK20A GPCPLL register constants, PLL parameter structures, clock object layout, and shared helper prototypes for GK20A-derived Tegra GPU clock drivers.

## Important APIs, types, and functions
Important types are `struct gk20a_clk_pllg_params`, `struct gk20a_pll`, and `struct gk20a_clk`. Inline helpers include `gk20a_pllg_is_enabled()` and `gk20a_pllg_n_lo()`. The header exposes GK20A PLL MNP read/write/calc and clock lifecycle hooks.

## Control flow
The header itself has no runtime flow. Its inline helpers read `GPCPLL_CFG` to test enable state and compute the low safe NDIV from minimum VCO, parent rate, and M divider.

## State and persistence
No independent state is stored here. The structures define persistent per-clock driver state and the register macros identify persistent GPCPLL hardware state.

## Dependencies and integration points
Consumed by `gk20a.c`, `gm20b.c`, `gp10b.c`, and devfreq code. It ties common NVKM clock domains to Tegra GPCPLL register programming.

## Risks
Bitfield masks and register offsets are the contract for all GK20A-family clock code. A bad mask in this header affects multiple generations and can corrupt PLL coefficients.

## Test signals
Compile coverage across GK20A, GM20B, GP10B, and devfreq users; runtime validation of PLL enable reads, NDIV low calculation, and programmed rate readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a_devfreq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a_devfreq.c

## Purpose
Implements devfreq support for GK20A-family Tegra GPUs by measuring PMU idle counters and feeding the Linux simple_ondemand governor with GPU utilization and OPP frequencies.

## Important APIs, types, and functions
Defines `struct gk20a_devfreq`, `gk20a_devfreq_init()`, `gk20a_devfreq_resume()`, `gk20a_devfreq_suspend()`, profile callbacks `gk20a_devfreq_target()`, `gk20a_devfreq_get_cur_freq()`, and `gk20a_devfreq_get_dev_status()`, plus PMU counter helpers.

## Control flow
Init allocates managed state, records Tegra register base, registers one OPP per pstate, initializes idle counters, seeds initial frequency, and registers a delayed devfreq device. Status reads total and busy counters, treats overflow or inconsistent counters as fully busy, converts normalized cycles to busy/total time, resets counters, and returns current frequency. Target selects the first pstate at or above the requested frequency and updates both AC and DC user states.

## State and persistence
Persistent state includes devfreq pointer, MMIO base, governor thresholds, busy/total time, and last update timestamp. PMU idle counters and interrupt status are reset each sample.

## Dependencies and integration points
Depends on Linux devfreq/OPP APIs, DRM-managed allocation, Nouveau DRM device data, Tegra register mapping, `nvkm_clk_ustate()`, and GP10B/GK20A clock object lookup by chipset.

## Risks
The debug print divides by `total_time / 100`, so extremely small sampling windows are risky. Targeting mutates both AC and DC user states, which overrides separate power-source preferences. Counter overflow intentionally reports 100% busy.

## Test signals
OPP table creation, devfreq sysfs frequency changes, governor polling at 50 ms, suspend/resume calls, PMU counter overflow handling, and rate agreement between requested pstate and `get_cur_freq()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a_devfreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a_devfreq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a_devfreq.h

## Purpose
Declares the optional GK20A devfreq interface and stubs it out when `CONFIG_PM_DEVFREQ` is disabled.

## Important APIs, types, and functions
Forward declares `struct gk20a_devfreq`; declares `gk20a_devfreq_init()`, `gk20a_devfreq_resume()`, and `gk20a_devfreq_suspend()` for devfreq builds, and provides inline no-op fallbacks otherwise.

## Control flow
No complex flow exists. Configuration decides whether callers get real devfreq functions or no-op inline helpers returning success.

## State and persistence
No state is defined beyond the opaque devfreq pointer type. Real state lives in `gk20a_devfreq.c`.

## Dependencies and integration points
Includes Linux devfreq declarations and is used by GK20A, GM20B, and GP10B clock implementations to avoid conditional code in init/resume paths.

## Risks
The disabled-config stub for init leaves the caller's devfreq pointer untouched; callers must not dereference it unless the real init has populated it.

## Test signals
Build both with and without `CONFIG_PM_DEVFREQ`; runtime no-op suspend/resume should succeed when devfreq is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a_devfreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gm20b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gm20b.c

## Purpose
Implements GM20B Tegra GPU clocking, including GK20A-compatible legacy mode for speedo 0 parts and noise-aware PLL/DVFS programming for speedo >= 1 parts.

## Important APIs, types, and functions
Key structures are `struct gm20b_clk`, `struct gm20b_pll`, and `struct gm20b_clk_dvfs`. Important functions include `gm20b_clk_new()`, `gm20b_clk_calc()`, `gm20b_clk_prog()`, `gm20b_clk_init()`, `gm20b_clk_init_dvfs()`, fused-parameter parsing, safe-fmax calculation, DVFS coefficient programming, and GM20B-specific PLL slide/program helpers.

## Control flow
Speedo 0 delegates to GK20A-style PLL programming with fewer pstates. Speedo >= 1 duplicates PLL parameter limits, clamps M for NAPLL operation, reads fuse calibration if available, computes safe minimum-voltage frequency, and initializes DVFS. Reclocking computes target PLL and voltage-derived DFS settings, optionally steps through a safe frequency before changing voltage-detection coefficients, then slides/programs the PLL to the final rate.

## State and persistence
State includes current and pending PLL/DVFS settings, current and target microvolts, fused ADC slope/offset, safe fmax, and GK20A base clock state. Hardware state spans GPCPLL, BYPASSCTRL_SYS, DVFS coefficient/calibration registers, fuse-derived settings, and devfreq counters.

## Dependencies and integration points
Depends on Tegra speedo/fuse data, NVKM volt tables, GK20A PLL helpers, devfreq, timer waits, and common pstate policy. It integrates with voltage sequencing in `clk/base.c` by computing new UV during `calc()`.

## Risks
Voltage/frequency ordering is safety-critical. Bad fused calibration, zero slope, or safe-fmax evaluation can put the PLL above the F/V curve during voltage changes. The code has fallback legacy mode only when NAPLL parameter clamping fails.

## Test signals
Speedo 0 and speedo >= 1 boot paths, fuse-present and calibration fallback logs, safe-fmax debug output, DVFS calibration timeout, pstate transitions across voltage increases/decreases, and devfreq governor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gm20b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gp10b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gp10b.c

## Purpose
Implements GP10B Tegra clock control using the platform clock framework/BPMP instead of direct Nouveau PLL register programming, while retaining static GPU pstates and GK20A devfreq support.

## Important APIs, types, and functions
Exports `gp10b_clk_new()`. Core hooks are `gp10b_clk_init()`, `gp10b_clk_read()`, `gp10b_clk_calc()`, and `gp10b_clk_prog()`. The static `gp10b_pstates` table covers 114.75 MHz through 1.3005 GHz.

## Control flow
Constructor stores the Tegra clock pointer and initializes static pstate list heads. Init starts at the highest pstate to match the BPMP default, then initializes devfreq. Calculation rounds the requested GPC rate through `clk_round_rate()`, and programming applies it with `clk_set_rate()` before caching actual rate.

## State and persistence
State lives in `struct gp10b_clk`: common NVKM clock state, Tegra `struct clk *`, pending rounded rate, actual rate, and devfreq pointer. Persistent hardware programming is owned by the Tegra clock provider.

## Dependencies and integration points
Depends on Linux common clock framework, Tegra device glue, common NVKM pstate logic, and `gk20a_devfreq_init()`. It is selected for chipset `0x13b` in devfreq lookup.

## Risks
Rate rounding may select a frequency different from the static pstate target; devfreq and pstate reporting need to use the actual rate. This path assumes BPMP/platform clock firmware enforces safe voltage and PLL sequencing.

## Test signals
Clock-framework rate readback, devfreq OPP registration, boot at highest pstate, target transitions through every pstate, and suspend/resume behavior through the shared devfreq helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gp10b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gp10b.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gp10b.h

## Purpose
Defines the GP10B clock object layout and accessor used by GP10B clock and devfreq code.

## Important APIs, types, and functions
The header defines `struct gp10b_clk` with embedded `struct nvkm_clk`, Tegra clock pointer, cached current/new rates, and `struct gk20a_devfreq *devfreq`, plus the `gp10b_clk()` container macro.

## Control flow
There is no runtime control flow in the header.

## State and persistence
The structure fields define all persistent GP10B clock driver state. Actual hardware state is managed by the Tegra clock provider referenced by `clk`.

## Dependencies and integration points
Includes `priv.h`, `<linux/clk.h>`, and `gk20a_devfreq.h`. Used by `gp10b.c` and `gk20a_devfreq.c` for chipset-specific state lookup.

## Risks
The object layout is assumed by `container_of()`; changing the embedded base position or devfreq field expectations would break users.

## Test signals
Compile-time coverage and runtime devfreq lookup for GP10B chipset are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gp10b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gt215.c

## Purpose
Implements GT215/NVA3 clock reading and reclocking for core, shader, memory, display, vdec, host, and intermediate core clocks using PLLs, dividers, and FIFO pause sequencing.

## Important APIs, types, and functions
Exports `gt215_clk_new()`, `gt215_clk_pre()`, `gt215_clk_post()`, and `gt215_pll_info()`. Internal functions include `read_clk()`, `read_pll()`, `gt215_clk_info()`, `calc_clk()`, `calc_host()`, `prog_pll()`, `prog_clk()`, `prog_host()`, and `prog_core()`.

## Control flow
Reads decode fixed references, VCO sources, PLL bypass paths, and host source selection. Calculation tries divider programming first, falls back to PLL if the divider error is outside a small tolerance, and may compute an intermediate core clock. Programming pauses engines/FIFO, selects safe non-PLL paths before PLL changes, waits for lock, adjusts framebuffer delay around core changes, programs shader/display/vdec/host, and resumes FIFO/engines.

## State and persistence
`struct gt215_clk_info eng[nv_clk_src_max]` caches planned clock, PLL, framebuffer delay, and host output mode. Hardware state persists in 0x0041xx source registers, PLL control/coef registers, host control registers, and FIFO gating state during reclock.

## Dependencies and integration points
Depends on engine FIFO pause/start, BIOS PLL parsing, `gt215_pll_calc()`, timer waits, and common NVKM pstate logic. `gt215_clk_pre/post` are reused by MCP77.

## Risks
FIFO pause and engine-idle waits can fail; post handling must avoid restarting FIFO when pause did not complete. PLL bypass and disable ordering is delicate, and host 277 MHz special handling is platform-specific.

## Test signals
Reclock under graphics load, FIFO pause timeout paths, host-source readback, PLL lock polling, framebuffer delay changes, and requested versus actual clock debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gt215.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gt215.h

## Purpose
Declares GT215 clock helper data and pre/post APIs shared with related clock drivers such as MCP77.

## Important APIs, types, and functions
Defines `enum nva3_host_clk_src`, `struct gt215_clk_info`, `gt215_pll_info()`, `gt215_clk_pre()`, and `gt215_clk_post()`.

## Control flow
No runtime flow exists in the header. The declared pre/post helpers wrap clock programming with FIFO/engine gating, while `gt215_pll_info()` computes divider or PLL programming data.

## State and persistence
No independent state is stored. `struct gt215_clk_info` is the transient per-domain calculation record used by implementation files.

## Dependencies and integration points
Includes `priv.h`; used by `gt215.c` and `mcp77.c`.

## Risks
The shared structure must remain compatible with both callers. Misinterpreting `host_out`, `clk`, `pll`, or `fb_delay` changes hardware programming semantics.

## Test signals
Build coverage for GT215 and MCP77, plus runtime reclock paths that call the shared pre/post helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gt215.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/mcp77.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/mcp77.c

## Purpose
Implements MCP77 integrated-chipset clock reading and reclocking for core, shader, host, and vdec domains using a mix of fixed HREF-derived clocks, NVPLL/SPLL, and dividers.

## Important APIs, types, and functions
Exports `mcp77_clk_new()`. Important helpers are `mcp77_clk_read()`, `mcp77_clk_calc()`, `mcp77_clk_prog()`, `read_pll()`, `calc_pll()`, and `calc_P()`. It reuses `gt215_clk_pre()` and `gt215_clk_post()`.

## Control flow
Read paths decode master clock mux bits in `0x00c054`, PLL post dividers, host sources, and VDEC divider source. Calculation chooses HCLKx4 or NVPLL for core, href/NVPLL/SPLL for shader, and core or fixed 500 MHz for VDEC, printing the chosen strategy. Programming switches temporarily to safe href clocks, writes PLL coefficients and post dividers, waits for requested PLL lock bits, writes the final master mux, and disables unused PLLs/dividers.

## State and persistence
`struct mcp77_clk` caches selected sources and register values for core/shader/vdec. Persistent state is in master mux `0x00c054`, PLL coefficient/control registers, post-divider registers, and VDEC divider register.

## Dependencies and integration points
Depends on BIOS PLL limits, `nv04_pll_calc()`, GT215 pre/post FIFO gating, and common NVKM pstate logic.

## Risks
Integrated-chipset muxes are tightly encoded; a bad `mast` value can route clocks to invalid sources. PLL lock wait failure falls through to resume cleanup, so partial programming must remain safe.

## Test signals
Strategy debug logs, PLL lock bits in `0x004080`, clock readback for core/shader/vdec, and reclock tests that choose both fixed-source and PLL-source paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/mcp77.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/nv04.c

## Purpose
Provides the minimal NV04 clock subdevice wrapper and legacy PLL calculation/programming callbacks used by older devinit/display code.

## Important APIs, types, and functions
Exports `nv04_clk_new()`, `nv04_clk_pll_calc()`, and `nv04_clk_pll_prog()`. It installs these callbacks into `struct nvkm_clk` after constructing a clock object with an empty domain list.

## Control flow
PLL calculation delegates to `nv04_pll_calc()` and packs returned values into `struct nvkm_pll_vals`. Programming selects single-stage, double-high-register, or double-low-register setters from `devinit/nv04.c` based on BIOS chip version and target register address.

## State and persistence
No pstate state is created because the domain table is empty. Persistent effects are PLL register writes performed through devinit helpers.

## Dependencies and integration points
Depends on BIOS PLL parsing structures, `pllnv04.c`, and NV04 devinit PLL programming routines. Used by legacy code needing PLL callbacks rather than full dynamic clock domains.

## Risks
Chip-version/register dispatch must match the legacy hardware generation. Calling `pll_prog` without a valid devinit subdevice would fail because programming is routed through `device->devinit`.

## Test signals
Legacy display PLL programming, compile linkage with devinit helpers, and mode-setting tests on NV04/NV3x/NV4x boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/nv40.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/nv40.c

## Purpose
Implements NV40 clock read/calc/prog support for core, shader, and memory clocks with NVPLL/SPLL programming and legacy PLL helper integration.

## Important APIs, types, and functions
Exports `nv40_clk_new()`. Important functions are `nv40_clk_read()`, `nv40_clk_calc()`, `nv40_clk_prog()`, `nv40_clk_calc_pll()`, `read_pll_1()`, and `read_pll_2()`.

## Control flow
Reads decode master mux `0x00c040`, single/double PLL formats, and memory PLL. Calculation programs the core/geometric clock through NVPLL and uses the second PLL for shader/ROP only when shader differs from core. Programming disconnects muxes, writes coefficients/control, delays for settling, and restores the selected mux.

## State and persistence
`struct nv40_clk` caches target master control, PLL controls, coefficients, and SPLL value. Hardware state persists in `0x004000/04/08/20` PLL registers and `0x00c040` mux bits.

## Dependencies and integration points
Uses BIOS PLL limits, `nv04_pll_calc()`, legacy PLL callbacks, and common pstate policy. Constructor enables reclocking and exposes `pll_calc/pll_prog` callbacks.

## Risks
The shader/core split path assumes certain PLL capabilities. A failed PLL calculation returns errors before programming; however, incorrect double-versus-single PLL selection can program invalid coefficients.

## Test signals
Core/shader clock readback, memory PLL readback, pstate transitions with shader equal and different from core, and display PLL callers using the installed legacy callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/nv40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/nv50.c

## Purpose
Implements NV50/G8x/G9x clock reading and hwsq-scripted reclocking for core, shader, memory, VDEC, DOM6, host, and related reference sources.

## Important APIs, types, and functions
Exports `nv50_clk_read()`, `nv50_clk_calc()`, `nv50_clk_prog()`, `nv50_clk_tidy()`, `nv50_clk_new_()`, and `nv50_clk_new()`. Helpers include `read_div()`, `read_pll_src()`, `read_pll_ref()`, `read_pll()`, `calc_pll()`, `calc_div()`, and `clk_same()`.

## Control flow
Reads decode chipset-specific divider registers, reference PLL sources, master mux bits, post dividers, and special chipset cases. Calculation builds a hardware-sequencer script: block FIFO, disable FB, choose safe VDEC/DOM6 clocks, disconnect core/shader from PLLs, program NVPLL/SPLL coefficients, restore FB and FIFO. `prog()` executes the script, while `tidy()` frees/discards it.

## State and persistence
`struct nv50_clk` contains common clock state and `struct nv50_clk_hwsq` register handles/script state. Persistent hardware state is the NV50 PLL/mux/divider register set and FIFO/FB gating touched by the hwsq.

## Dependencies and integration points
Depends on bus hardware sequencer APIs from `seq.h`, BIOS PLL data, `nv04_pll_calc()`, and common pstate logic. It is reused by G84 via `nv50_clk_new_()`.

## Risks
The hwsq sequence blocks FIFO and disables FB, so any missing restore step can hang the GPU. Chipset-specific reference selection is fragile, and some read paths return zero for unsupported mux combinations.

## Test signals
Successful hwsq execution, tidy cleanup after success/failure, FIFO unblock, FB re-enable waits, mode/pstate transitions on NV50/G84/G9x chipsets, and debug logs for bad PLL references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/nv50.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/nv50.h

## Purpose
Declares the NV50 clock object and hardware sequencer register bundle used by the NV50 and G84 clock implementations.

## Important APIs, types, and functions
Defines `struct nv50_clk_hwsq`, `struct nv50_clk`, the `nv50_clk()` container macro, and prototypes for NV50 constructor/read/calc/prog/tidy functions.

## Control flow
No runtime flow exists in the header; the hwsq register fields are populated by `nv50_clk_new_()` and consumed by `nv50_clk_calc/prog/tidy()`.

## State and persistence
The hwsq object stores transient script state plus register descriptors for FIFO, SPLL, NVPLL, dividers, and master mux.

## Dependencies and integration points
Includes common clock private definitions and bus hwsq APIs. Shared by `nv50.c` and `g84.c`.

## Risks
The register bundle must stay synchronized with `nv50.c`; missing a descriptor would make generated hwsq operations target address zero or be skipped.

## Test signals
Compile coverage and hwsq script creation/execution on NV50-family reclocking paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/nv50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/pll.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/pll.h

## Purpose
Declares shared PLL calculation helpers for legacy NV04-style PLLs and GT215-style fractional-capable PLLs.

## Important APIs, types, and functions
Exports `nv04_pll_calc()` and `gt215_pll_calc()` prototypes over opaque `struct nvkm_subdev` and `struct nvbios_pll` inputs.

## Control flow
No runtime flow in this header. Implementations search PLL coefficient ranges and return the closest achievable frequency and coefficient fields.

## State and persistence
No state is stored. Callers pass output coefficient pointers and later program hardware.

## Dependencies and integration points
Used by clock and devinit generations from NV04 through GA100 for core/display/memory PLL calculations.

## Risks
Signature changes affect many architecture-specific clock/devinit files. Callers rely on return-value conventions: positive/zero/negative meanings differ between helper families.

## Test signals
Build coverage and mode-setting/reclock tests that exercise VPLL, memory PLL, and engine PLL calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/pllgt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/pllgt215.c

## Purpose
Implements GT215-generation PLL coefficient search for integer and optional fractional-N PLL programming.

## Important APIs, types, and functions
Exports `gt215_pll_calc()`, which accepts BIOS PLL limits, target frequency, output N/fN/M/P pointers, and returns the achieved frequency or an error.

## Control flow
The function chooses an initial post divider within BIOS limits, computes legal M range from reference input-frequency limits, and iterates M. For integer mode it rounds N based on the remainder and tracks the lowest error. For fractional mode it computes a 13-bit fractional residue and returns immediately with an exact target-oriented representation.

## State and persistence
No persistent state. The computed coefficients are consumed by clock/devinit programming routines.

## Dependencies and integration points
Depends on BIOS PLL limits and NVKM error logging. Used by GT215, Fermi/Kepler display PLL programming, and newer VPLL devinit paths.

## Risks
Fractional mode returns early rather than exhaustive-searching, so callers must request it only for hardware that supports the representation. Bad BIOS limits can produce no match and `-EINVAL`.

## Test signals
PLL coefficient unit checks against known BIOS tables, display mode pixel-clock programming, and debug logs for no matching values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/pllgt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/pllnv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/pllnv04.c

## Purpose
Implements NV04-era single-stage and double-stage PLL coefficient search used by legacy clock and devinit code.

## Important APIs, types, and functions
Exports `nv04_pll_calc()`. Internal helpers `getMNP_single()` and `getMNP_double()` search M/N/P or M1/N1/M2/N2/P combinations under BIOS voltage-controlled oscillator and input-frequency limits.

## Control flow
Single-stage search adjusts M constraints for older chips, iterates post-divider and M/N values, and tracks closest output. Double-stage search chooses a log2 post-divider, walks first-stage and second-stage ranges, applies fixed-gain and old-chip ratio constraints, and tracks the closest output. The public wrapper selects single or double search based on `vco2.max_freq` and caller-provided pointers.

## State and persistence
No persistent state. Outputs are raw coefficient fields later packed into PLL registers.

## Dependencies and integration points
Depends on BIOS PLL limits, chip version, and common NVKM logging. Used by `nv04.c`, `nv40.c`, `mcp77.c`, `nv50.c`, and devinit PLL paths.

## Risks
Legacy hardware quirks are embedded in search bounds. Incorrect max-M or VCO adjustments can produce coefficients that work on one chip family but not another.

## Test signals
Known-clock coefficient comparisons, display pixel-clock setup, memory PLL programming on NV3x/NV4x/NV50, and error logging when no acceptable values exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/pllnv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/priv.h

## Purpose
Defines the private NVKM clock function-table contract and constructor prototypes shared by all clock subdevice implementations.

## Important APIs, types, and functions
Defines `struct nvkm_clk_func` with optional `init/fini/read/calc/prog/tidy`, static pstate support, pstate count, and flexible domain array. Declares `nvkm_clk_ctor()`, `nvkm_clk_new_()`, and legacy NV04 PLL callbacks.

## Control flow
No runtime flow occurs in the header. The function table determines the control flow used by `clk/base.c` during subdevice init, pstate programming, and teardown.

## State and persistence
No state is stored here; the table describes per-generation persistent behavior and static pstate ownership.

## Dependencies and integration points
Includes public `subdev/clk.h` and is included by all implementation files in this directory.

## Risks
The flexible `domains[]` member means function-table definitions must terminate with `nv_clk_src_max`. Missing hooks such as `read` on a domain-bearing implementation would break init.

## Test signals
Compile coverage across every clock generation and boot-time domain enumeration without overrunning the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/seq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/seq.h

## Purpose
Wraps the bus hardware-sequencer API with clock-specific macros used by the NV50 clock implementation.

## Important APIs, types, and functions
Macros include `clk_init`, `clk_exec`, `clk_have`, `clk_rd32`, `clk_wr32`, `clk_mask`, `clk_setf`, `clk_wait`, and `clk_nsec`.

## Control flow
Macros expand directly to hwsq operations on the embedded `base` script and named register descriptors.

## State and persistence
No state is defined. The macros operate on an hwsq object supplied by the caller.

## Dependencies and integration points
Depends on `<subdev/bus/hwsq.h>`. Used by `nv50.c` to build and execute safe reclocking scripts.

## Risks
The token-pasting register names require the hwsq struct fields to be named `r_<name>`. A typo compiles only if a matching field exists and otherwise breaks build.

## Test signals
Build coverage and NV50 reclocking script execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/seq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/Kbuild

## Purpose
Builds the Nouveau devinit subdevice objects for legacy through modern GPU generations, including the R535 GSP-backed wrapper.

## Important APIs, types, and functions
The file lists `nvkm-y` object inclusions for base, generation-specific devinit files, and `r535.o`.

## Control flow
Kbuild has no runtime flow; it controls which translation units are linked into the NVKM module.

## State and persistence
No runtime state. Build state is the linked object set.

## Dependencies and integration points
Integrated by the parent Nouveau Kbuild. The object list must match constructor references in the device chipset table.

## Risks
Missing a generation object causes unresolved symbols or absent support for a chipset. Keeping `r535.o` linked is required for GSP RM paths in TU102/GA100.

## Test signals
Kernel build/link coverage and modpost symbol resolution for every devinit constructor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/base.c

## Purpose
Implements the common NVKM devinit subdevice wrapper for VBIOS post execution, PLL setting, memory init, MMIO address filtering, power-disable hooks, and VGA register lock handling.

## Important APIs, types, and functions
Exports `nvkm_devinit_mmio()`, `nvkm_devinit_pll_set()`, `nvkm_devinit_meminit()`, `nvkm_devinit_disable()`, `nvkm_devinit_post()`, and `nvkm_devinit_ctor()`. Subdevice hooks are `preinit`, `init`, `fini`, and `dtor`.

## Control flow
Preinit runs generation-specific preinit, applies one-shot `NvForcePost`, and unlocks extended VGA CRTC registers. Post calls the generation post callback with the current `post` flag, then disables engines not initialized by firmware. Fini forces full reinit on non-poweroff suspend. Dtor calls generation dtor and re-locks CRTC registers.

## State and persistence
`struct nvkm_devinit` stores the function table, `post`, and `force_post`. Hardware state includes VGA lock state, init-script effects, disabled engine state, and any generation-specific PLL/memory programming.

## Dependencies and integration points
Depends on `nvkm_subdev`, config option parsing, VGA helpers, and generation-specific function tables.

## Risks
The post flag controls whether VBIOS scripts execute; wrong detection can skip needed initialization or rerun scripts unnecessarily. `nvkm_devinit_disable()` always returns zero, so callers do not learn disable failures.

## Test signals
Boot with and without `NvForcePost`, suspend/resume, VGA CRTC lock/unlock behavior, VBIOS post logs, and engine disable state after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/fbmem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/fbmem.h

## Purpose
Provides framebuffer aperture mapping and direct read/write helpers used by legacy devinit memory-size/type probing.

## Important APIs, types, and functions
Defines NV04/NV10 PFB register constants and inline helpers `fbmem_init()`, `fbmem_fini()`, `fbmem_peek()`, `fbmem_poke()`, and `fbmem_readback()`.

## Control flow
Helpers map BAR1 framebuffer memory write-combined, perform atomic page mappings for individual offsets, issue 32-bit reads/writes, enforce a write memory barrier, and compare readback patterns.

## State and persistence
No private state beyond the returned `io_mapping`. Writes affect framebuffer memory and PFB configuration registers controlled by callers.

## Dependencies and integration points
Depends on device resource address/size callbacks and Linux `io_mapping` APIs. Used by NV04/NV05/NV10/NV20 memory init probes.

## Risks
Pattern writes happen before normal memory manager setup, so offsets and mapping size must be valid. Atomic WC mappings and barriers are required to avoid stale or reordered readback.

## Test signals
Legacy memory-size detection, successful BAR1 mapping, and correct RAM amount/width reporting on NV04-NV2x hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/fbmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/g84.c

## Purpose
Defines G84 devinit behavior by reusing NV50 init/post/PLL paths and adding G84-specific engine disable rules.

## Important APIs, types, and functions
Exports `g84_devinit_new()`. Static `g84_devinit_disable()` inspects `0x001540` and `0x00154c` and disables MPEG, VP, BSP, CIPHER, and DISP engines when straps/status indicate they should not remain active.

## Control flow
Constructor delegates to `nv50_devinit_new_()`. Runtime preinit/init/post/pll_set come from NV50/NV04 helpers; final disable is generation-specific.

## State and persistence
No extra software state. Persistent effects are engine disable calls and standard NV50 init-script/PLL state.

## Dependencies and integration points
Depends on NV50 devinit helpers, BIOS init execution, and NVKM engine disable support.

## Risks
Engine-disable register interpretation is chipset-specific. Disabling an engine that firmware initialized and the driver expects would break later engine bring-up.

## Test signals
Boot logs for G84 boards, engine availability after post, display init, and suspend/resume post detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/g98.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/g98.c

## Purpose
Defines G98 devinit behavior by reusing NV50 init/post/PLL paths with G98-era video/security engine disable mapping.

## Important APIs, types, and functions
Exports `g98_devinit_new()` and defines `g98_devinit_disable()` for MSPDEC, MSVLD, MSPPP, DISP, and SEC engines.

## Control flow
The function table delegates preinit/init/post/pll_set to NV50/NV04 helpers and runs the G98 disable hook after post through the common base.

## State and persistence
No local software state. Hardware persistence is the engine disable state and any standard NV50 devinit register changes.

## Dependencies and integration points
Depends on `nv50.h`, BIOS init infrastructure, and engine disable helpers.

## Risks
Wrong status-bit interpretation can leave unsupported media/security engines enabled or disable required ones.

## Test signals
G98 boot with media engines present/absent, display engine initialization, and post/disable behavior across resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/g98.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/ga100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/ga100.c

## Purpose
Implements GA100 devinit PLL programming and display-engine disable behavior, with optional R535 GSP-RM wrapper construction.

## Important APIs, types, and functions
Exports `ga100_devinit_new()`. Important functions are `ga100_devinit_pll_set()` and `ga100_devinit_disable()`.

## Control flow
VPLL programming parses BIOS PLL data, computes GT215-style fractional coefficients, and writes head-indexed 0x00efxx/0x00e9c0 registers for VPLL0-3. Constructor uses `r535_devinit_new()` when GSP RM is active; otherwise it creates a normal NV50-style devinit object. Post uses TU102 wait logic.

## State and persistence
No extra software state. Persistent effects are VPLL register programming, display engine disable, and GSP-reduced devinit function table when active.

## Dependencies and integration points
Depends on BIOS PLL parsing, `gt215_pll_calc()`, GSP RM detection, TU102 post wait, and NV50 init.

## Risks
Only VPLL types are implemented; other PLL requests return `-EINVAL`. GSP mode deliberately exposes only post/disable callbacks, so callers must not expect local init/pll programming in that mode.

## Test signals
GA100 display PLL mode-setting, GSP and non-GSP constructor paths, TU102-style post wait completion, and display engine disable register behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/ga100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gf100.c

## Purpose
Implements GF100/Fermi devinit PLL programming, post detection, and engine disable policy.

## Important APIs, types, and functions
Exports `gf100_devinit_new()`, `gf100_devinit_pll_set()`, and `gf100_devinit_preinit()`. Static disable handles display, MSPDEC/MSPPP, MSVLD, MSENC, and copy engines from register `0x022500`.

## Control flow
Preinit checks bit 1 of `0x2240c`, which devinit sets and suspend clears, to decide whether VBIOS post is required. PLL programming handles VPLL0-3 by writing Fermi display PLL coefficient and fractional registers. Init and post are inherited from NV50/NV04 helpers.

## State and persistence
Software state is the common devinit `post` flag. Persistent hardware state includes Fermi VPLL registers and disabled engine state.

## Dependencies and integration points
Depends on BIOS PLL tables, `gt215_pll_calc()`, NV50 init-script execution, and engine disable helpers.

## Risks
The post heuristic is hardware-specific; if the status bit changes meaning, boards may skip required devinit. Non-VPLL types are unimplemented.

## Test signals
Fermi boot/resume post detection, VPLL programming during display modesets, and engine disable state after post.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gm107.c

## Purpose
Defines GM107/Maxwell devinit behavior by reusing GF100 init/PLL/post logic and adding Maxwell-specific engine disable handling, including a GSP-aware restriction.

## Important APIs, types, and functions
Exports `gm107_devinit_new()` and shared `gm107_devinit_disable()`.

## Control flow
Disable reads `0x021c00` and `0x021c04`, disables CE engines only when GSP RM is not managing the device, and disables display based on status. The function table uses GF100 preinit, NV50 init, NV04 post, and GF100 PLL programming.

## State and persistence
No extra software state. Persistent hardware effects are engine disable calls and standard init-script state.

## Dependencies and integration points
Depends on GSP RM detection and NV50/GF100 helper paths.

## Risks
GSP mode expects only display disable; disabling CE under GSP could conflict with firmware ownership.

## Test signals
Maxwell boot in GSP and non-GSP modes, CE availability, display initialization, and resume post behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gm200.c

## Purpose
Implements GM200/Pascal-era PMU-assisted devinit post flow by loading VBIOS PMU applications, boot-script data, and PRE_OS PMU code.

## Important APIs, types, and functions
Exports `gm200_devinit_new()`, `gm200_devinit_post()`, and `gm200_devinit_preos()`. Internal helpers `pmu_code()`, `pmu_data()`, `pmu_args()`, `pmu_exec()`, and `pmu_load()` upload and launch PMU images from VBIOS.

## Control flow
Post validates BIT 'I' PMU init metadata, loads the DEVINIT PMU application, uploads required tables and boot scripts when post execution is requested, starts DEVINIT via PMU, waits for completion in `0x10a040`, then optionally launches PRE_OS to manage fans until full PMU firmware loads.

## State and persistence
No additional software state beyond NV50 devinit. PMU IMEM/DMEM contents, PMU control registers, and init-script hardware effects persist until firmware takeover/reset.

## Dependencies and integration points
Depends on BIOS BIT/PMU tables, `nvkm_falcon_reset()`, PMU subdevice, NV50 init, GF100 preinit/PLL, and GM107 disable.

## Risks
Missing or malformed VBIOS PMU metadata prevents post. PMU transfer loops assume 4-byte aligned image sizes and fixed PMU register protocol. Timeout leaves device partially initialized.

## Test signals
VBIOS PMU metadata detection, PMU reset success, DEVINIT completion bit, PRE_OS execution, fan behavior before full PMU load, and resume post reliability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gt215.c

## Purpose
Implements GT215 devinit VPLL programming, engine disable policy, and an MMIO filter for problematic init-table register-group writes.

## Important APIs, types, and functions
Exports `gt215_devinit_new()` and `gt215_devinit_pll_set()`. Static helpers are `gt215_devinit_disable()` and `gt215_devinit_mmio()`.

## Control flow
VPLL programming parses BIOS PLL limits, computes GT215 coefficients, and writes PLL control/coefficient/fractional registers for VPLL0/1. The MMIO filter checks known partitioned register ranges, caches `0x001540`, counts enabled partitions, and returns `~0` to suppress writes targeting non-existent partitions. Disable gates media, display, and copy engines based on status registers.

## State and persistence
`struct nv50_devinit.r001540` caches partition state for MMIO filtering. Persistent effects include VPLL programming, skipped init-script MMIO writes, and engine disable state.

## Dependencies and integration points
Depends on NV50 devinit base, BIOS PLL/init tables, `gt215_pll_calc()`, and engine disable helpers.

## Risks
The MMIO filter is a compatibility workaround; wrong ranges or partition counts can skip needed init writes or perform invalid writes that destabilize register access.

## Test signals
Quadro/partitioned-board init-table execution, suppressed register writes, VPLL mode-setting, and engine disable verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gv100.c

## Purpose
Defines GV100/Volta devinit behavior with Volta VPLL programming and GM200 PMU-assisted post execution.

## Important APIs, types, and functions
Exports `gv100_devinit_new()` and static `gv100_devinit_pll_set()`.

## Control flow
PLL programming handles VPLL0-3 by parsing BIOS PLL data, computing GT215-style coefficients, and writing head-indexed 0x00ef10/0x00ef04 registers. Function table uses GF100 preinit, NV50 init, GM200 post, and GM107 disable.

## State and persistence
No local software state. Persistent hardware effects are VPLL register values, PMU DEVINIT execution, and engine disable state.

## Dependencies and integration points
Depends on BIOS PLL/PMU data, `gt215_pll_calc()`, GM200 PMU devinit, and Maxwell-style disable handling.

## Risks
Non-VPLL requests are unsupported. The PMU post dependency means VBIOS PMU metadata and PMU firmware upload must work before display init is reliable.

## Test signals
Volta VPLL mode-setting, PMU DEVINIT completion, display bring-up, and resume post behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/gv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/mcp89.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/mcp89.c

## Purpose
Defines MCP89 devinit behavior by reusing NV50 init/post paths, GT215 VPLL programming, and MCP89-specific engine disable mapping.

## Important APIs, types, and functions
Exports `mcp89_devinit_new()` and static `mcp89_devinit_disable()`.

## Control flow
Constructor delegates to `nv50_devinit_new_()`. Disable reads `0x001540/0x00154c` and disables MSPDEC, MSPPP, display, MSVLD, VIC, and copy engines as indicated.

## State and persistence
No extra software state. Persistent effects are standard NV50 init-script state, GT215 VPLL programming, and disabled engines.

## Dependencies and integration points
Depends on NV50 devinit helpers, GT215 PLL programming, BIOS init execution, and engine disable support.

## Risks
MCP89 has integrated chipset-specific media/VIC mappings; wrong bits could disable required display/media blocks.

## Test signals
MCP89 boot/display mode setting, media engine detection, post execution, and resume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/mcp89.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv04.c

## Purpose
Implements NV04-era devinit: legacy framebuffer memory probing, PLL programming helpers, VBIOS post invocation, VGA owner/preinit handling, and constructor state.

## Important APIs, types, and functions
Exports `nv04_devinit_new()`, `nv04_devinit_new_()`, `nv04_devinit_post()`, `nv04_devinit_preinit()`, `nv04_devinit_dtor()`, `nv04_devinit_pll_set()`, and PLL setters `setPLL_single()`, `setPLL_double_highregs()`, and `setPLL_double_lowregs()`.

## Control flow
Memory init maps BAR1, disables refresh/sequencer, writes probe patterns, and adjusts PFB boot type/width/amount. PLL programming parses BIOS PLL data, computes coefficients, and dispatches to generation/register-specific setters that sequence post-dividers, NM values, RAMDAC bits, powerctrl fields, and master mux masks. Preinit enables I2C access, takes VGA ownership, and decides post based on CRTC timing registers.

## State and persistence
`struct nv04_devinit.owner` persists saved VGA owner for restoration. Hardware state includes PFB memory config, PLL registers, VGA owner, CRTC lock state, and VBIOS post side effects.

## Dependencies and integration points
Depends on framebuffer BAR mapping helpers, VGA helpers, BIOS init/PLL tables, and `nv04_pll_calc()`. Provides PLL setters used by clock code.

## Risks
Legacy memory probing writes live framebuffer offsets and changes refresh/sequencer state. PLL sequences encode many board-specific quirks; wrong ordering can blank display or destabilize memory clocks.

## Test signals
NV04 memory amount/type detection, VGA owner restoration, VBIOS post execution, PLL programming for pixel/core/memory clocks, and suspend/resume full reinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv04.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv04.h

## Purpose
Declares the NV04 devinit object and legacy PLL programming functions shared with later legacy generations and clock code.

## Important APIs, types, and functions
Defines `struct nv04_devinit` with common `struct nvkm_devinit` and saved VGA owner. Declares constructors, dtor/preinit/fini, PLL setter, and low-level PLL programming helpers.

## Control flow
No runtime flow exists in the header.

## State and persistence
The `owner` field preserves VGA ownership across devinit lifetime so teardown can restore it.

## Dependencies and integration points
Includes private devinit definitions and forward declares `struct nvkm_pll_vals`. Used by NV04/NV05/NV10/NV1A/NV20 and `clk/nv04.c`.

## Risks
PLL helper declarations are broad legacy APIs; signature mismatch would break both devinit and clock callers.

## Test signals
Compile coverage for all legacy devinit files and NV04 clock PLL callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv04.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv05.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv05.c

## Purpose
Implements NV05 memory initialization using strap/BMP memory tables, scrambling setup, and framebuffer readback probing.

## Important APIs, types, and functions
Exports `nv05_devinit_new()` and static `nv05_devinit_meminit()`.

## Control flow
Meminit maps BAR1, reads memory strap, loads BMP memory-init table or default config, stops the VGA sequencer, skips UMA devices, programs scramble and PFB config bits, probes bus width using pattern writes, then probes size down from configured amount through 32/16/8/4 MB offsets before restoring sequencer.

## State and persistence
No local software state. Persistent state is PFB boot/config/scramble registers and framebuffer contents touched during probing.

## Dependencies and integration points
Depends on NV04 base devinit, BMP BIOS tables, `fbmem.h`, VGA helpers, and NV04 PLL/post functions.

## Risks
Invalid strap index or missing/incorrect BMP table can produce wrong RAM config. Pattern probing must not run on UMA path.

## Test signals
NV05/NV0x RAM width and size detection, scramble-table programming, UMA skip behavior, and VBIOS post.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv10.c

## Purpose
Implements NV10-generation memory init probing for SDR/DDR width and amount, then registers an NV04-compatible devinit function table.

## Important APIs, types, and functions
Exports `nv10_devinit_new()` and static `nv10_devinit_meminit()`.

## Control flow
Meminit maps BAR1, marks refresh control valid, tries possible memory-width settings based on chipset, uses repeated pattern writes at low offsets to select a working width, then probes installed memory amount by checking aliases at progressively larger offsets. It relies on NV04 base preinit/post/pll behavior.

## State and persistence
No extra software state. Hardware state is PFB width/amount/refctrl programming and framebuffer probe writes.

## Dependencies and integration points
Depends on `fbmem.h`, NV04 devinit constructor/dtor/preinit/post/pll, and BIOS init flow.

## Risks
Framebuffer alias probing is destructive and assumes early boot ownership. Width candidates differ by chipset and must remain accurate.

## Test signals
Correct VRAM size/width reporting on NV10/NV11/NV17-class boards, stable post, and no framebuffer corruption after driver takeover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv1a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv1a.c

## Purpose
Defines NV1A devinit as a small NV04-compatible variant without custom memory initialization.

## Important APIs, types, and functions
Exports `nv1a_devinit_new()` and a static `nv1a_devinit` function table.

## Control flow
All runtime behavior is inherited from NV04 dtor/preinit/post/pll_set. No meminit hook is installed.

## State and persistence
State is the inherited NV04 saved VGA owner and common devinit post flags.

## Dependencies and integration points
Depends on `nv04.h` and NV04 helper functions.

## Risks
If an NV1A board needs memory probing, this function table will not perform it; support relies on firmware/BIOS initialization.

## Test signals
Boot/post and PLL programming on NV1A hardware without custom meminit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv1a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv20.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv20.c

## Purpose
Implements NV20 memory initialization by extending NV10-style probing with chipset-specific register setup and then using NV04-compatible post/PLL behavior.

## Important APIs, types, and functions
Exports `nv20_devinit_new()` and static `nv20_devinit_meminit()`.

## Control flow
Meminit maps BAR1, programs refresh/control defaults, selects memory-width candidates, writes/reads probe patterns to identify working width and installed size, then restores required state. Constructor registers NV04 dtor/preinit/post/pll with the NV20 meminit hook.

## State and persistence
Persistent state is PFB configuration and framebuffer probe content; software state is inherited NV04 owner/post handling.

## Dependencies and integration points
Depends on `fbmem.h`, NV04 base helpers, BIOS init, and VGA access.

## Risks
Memory probing assumptions are board- and chipset-sensitive. Wrong PFB values can produce aliases or unstable memory access.

## Test signals
NV20/NV2x VRAM size and width detection, post execution, and display/memory stability after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv50.c

## Purpose
Implements NV50 devinit: PLL programming, initial-post detection, display-encoder init script execution, and common constructor for NV50-derived generations.

## Important APIs, types, and functions
Exports `nv50_devinit_new()`, `nv50_devinit_new_()`, `nv50_devinit_pll_set()`, `nv50_devinit_preinit()`, and `nv50_devinit_init()`.

## Control flow
Preinit disables old engines and marks post required when display is absent or VGA CRTC registers indicate the adapter was not initialized. Init, when post ran, walks DCB outputs, matches output BIOS records, and executes the first script for each encoder with output/or/link context set. PLL programming handles VPLL, memory PLL, and generic PLL layouts.

## State and persistence
`struct nv50_devinit` extends common devinit with `r001540` cache for later users. Persistent effects include VBIOS init scripts, VPLL/memory PLL writes, and engine disable state.

## Dependencies and integration points
Depends on BIOS DCB/output/init/PLL parsers, NV04 post helper, VGA helpers, and clock PLL calculation.

## Risks
Post detection is heuristic on some systems. DCB script execution depends on correct output matching and context variables. PLL layout differs by type and must be encoded correctly.

## Test signals
Secondary-GPU post, display encoder init after VBIOS post, VPLL/memory PLL programming, and resume reinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv50.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv50.h

## Purpose
Declares NV50 devinit object layout and shared generation helper APIs for NV50 through GM/GV/TU devinit files.

## Important APIs, types, and functions
Defines `struct nv50_devinit` and declares constructors, NV50 init/preinit/pll_set, GT215/GF100 PLL setters, GF100 preinit, GM107 disable, GM200 post/preos.

## Control flow
No runtime flow exists in the header.

## State and persistence
`r001540` caches a register value used by GT215 MMIO filtering.

## Dependencies and integration points
Includes private devinit definitions and is included by most post-NV50 devinit implementations.

## Risks
The shared declaration surface couples many generations; changing a helper signature has broad build impact.

## Test signals
Compile coverage across all NV50+ devinit files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/nv50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/priv.h

## Purpose
Defines the private devinit function-table contract and shared constructor prototypes.

## Important APIs, types, and functions
Defines `struct nvkm_devinit_func` with optional dtor/preinit/init/post/mmio/meminit/pll_set/disable hooks. Declares `r535_devinit_new()`, `nvkm_devinit_ctor()`, `nvkm_devinit_disable()`, `nv04_devinit_post()`, and `tu102_devinit_post()`.

## Control flow
No runtime flow in the header. Hook presence drives `devinit/base.c` behavior.

## State and persistence
No state is stored here; function tables describe per-generation persistent behavior.

## Dependencies and integration points
Included by all devinit implementations and by the R535 wrapper.

## Risks
Missing a mandatory hook for a generation can cause null dereferences in wrappers like `nvkm_devinit_pll_set()`, which assumes `pll_set` exists.

## Test signals
Build coverage and constructor/init/post paths for all devinit generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/r535.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/r535.c

## Purpose
Provides an R535/GSP-RM devinit wrapper that exposes only firmware-compatible post and disable operations while owning a dynamically allocated function table.

## Important APIs, types, and functions
Exports `r535_devinit_new()` and static `r535_devinit_dtor()`.

## Control flow
Constructor allocates a new `nvkm_devinit_func`, copies `post` and `disable` from the hardware table, installs a destructor that frees the table, and delegates allocation to `nv50_devinit_new_()`. On failure it frees the copied table.

## State and persistence
The copied function table is heap-owned by the devinit object and freed at destruction. Runtime hardware effects are limited to callbacks copied from the hardware generation.

## Dependencies and integration points
Used by TU102 and GA100 constructors when `nvkm_gsp_rm()` is active.

## Risks
The wrapper intentionally omits init and PLL programming hooks. Any caller that assumes those hooks are present in GSP mode would fail.

## Test signals
GSP-enabled TU102/GA100 construction, dtor memory cleanup, and post/disable behavior without local PLL/init calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/r535.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/tu102.c

## Purpose
Implements TU102/Turing devinit VPLL programming, post wait logic, and optional R535 GSP wrapper selection.

## Important APIs, types, and functions
Exports `tu102_devinit_new()` and `tu102_devinit_post()`. Static helpers are `tu102_devinit_pll_set()` and `tu102_devinit_wait()`.

## Control flow
VPLL programming computes GT215-style coefficients for VPLL0-3 and writes Turing head-indexed 0x00efxx registers including additional control values. Post waits up to roughly two seconds for initialization status registers `0x118128` and `0x118234`. Constructor uses R535 wrapper under GSP RM or a normal NV50 devinit otherwise.

## State and persistence
No local software state. Persistent hardware effects are VPLL registers, post-completion state, and GM107-style disable behavior.

## Dependencies and integration points
Depends on BIOS PLL parsing, `gt215_pll_calc()`, GSP RM detection, NV50 init, and GM107 disable.

## Risks
Post currently waits for firmware/hardware completion rather than executing VBIOS scripts locally. Timeout can leave display init incomplete. Non-VPLL PLL requests are unsupported.

## Test signals
Turing display mode PLL programming, post wait success/timeout, GSP and non-GSP constructor paths, and resume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/Kbuild

## Purpose
Builds the Nouveau fault subdevice objects for generic fault handling, user exposure, and GP100/GP10B/GV100/TU102 implementations.

## Important APIs, types, and functions
The Kbuild file adds `base.o`, `user.o`, `gp100.o`, `gp10b.o`, `gv100.o`, and `tu102.o` to `nvkm-y`.

## Control flow
No runtime flow; it controls link composition.

## State and persistence
No runtime state.

## Dependencies and integration points
Integrated by the parent NVKM build. Constructors referenced by chipset tables must be present in this list.

## Risks
Omitting `user.o` or a generation object would break user event exposure or chipset-specific fault support.

## Test signals
Kernel build/link coverage and modpost symbol resolution for fault constructors and user object helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/base.c

## Purpose
Implements the common NVKM fault subdevice: fault-buffer allocation/pinning, event setup, lifecycle dispatch, user object registration, and interrupt forwarding.

## Important APIs, types, and functions
Exports `nvkm_fault_new_()`. Important internals include `nvkm_fault_oneinit_buffer()`, `nvkm_fault_oneinit()`, event init/fini callbacks, subdev `init/fini/intr/dtor`, and `nvkm_event` management.

## Control flow
Oneinit allocates each generation-supported fault buffer, queries its entry count and get/put registers, allocates instance memory, pins it through the generation hook, then initializes per-buffer events. Event listeners enable or disable buffer interrupts. Init/fini and intr dispatch to generation hooks. Dtor removes notifications, finalizes events, unreferences memory, and frees buffers.

## State and persistence
`struct nvkm_fault` persists buffer pointers/count, event object, user-class data, and generation function table. Each `nvkm_fault_buffer` stores memory, BAR/device address, register offsets, id, and entries.

## Dependencies and integration points
Depends on `nvkm_memory_new()`, event infrastructure, subdev lifecycle, user fault constructor, and generation buffer hooks. Integrates with FIFO fault processing through generation code.

## Risks
Buffer memory pin failure returns `-EFAULT` after allocation; cleanup relies on dtor paths. Event enable directly controls hardware interrupts, so listener lifetime and buffer id must match.

## Test signals
Fault buffer allocation logs, user event subscription enabling/disabling interrupts, BAR/device address pinning, suspend/resume init/fini, and destructor leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/gp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/gp100.c

## Purpose
Implements GP100 fault-buffer register programming and generic interrupt notification for Pascal-style replayable fault buffers.

## Important APIs, types, and functions
Exports `gp100_fault_new()`, `gp100_fault_buffer_intr()`, `gp100_fault_buffer_fini()`, `gp100_fault_buffer_init()`, `gp100_fault_buffer_pin()`, `gp100_fault_buffer_info()`, and `gp100_fault_intr()`.

## Control flow
Buffer info reads entry count and sets get/put register offsets. Init writes upper/lower BAR2 buffer address and enables the buffer; fini disables it. Interrupt enable masks the MC fault interrupt, and interrupt handling simply notifies buffer-pending events.

## State and persistence
Persistent hardware state is buffer base address and enable bit at 0x002a70/74 plus get/put registers. Software state is inherited common fault buffer metadata.

## Dependencies and integration points
Depends on `nvkm_memory_bar2()`, MC interrupt masking, common fault base, and `MAXWELL_FAULT_BUFFER_A` user class exposure.

## Risks
No entries are parsed in-kernel here; userspace or higher layers must consume the buffer. Incorrect BAR2 pinning prevents hardware from writing faults.

## Test signals
Fault buffer entry-count readback, MC interrupt mask changes, user event notification on faults, and buffer address programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/gp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/gp10b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/gp10b.c

## Purpose
Adapts GP100 fault handling for GP10B/Tegra by using a physical memory address pin instead of BAR2 while reusing GP100 buffer control.

## Important APIs, types, and functions
Exports `gp10b_fault_new()` and `gp10b_fault_buffer_pin()`.

## Control flow
Construction installs a function table identical to GP100 except the pin hook returns `nvkm_memory_addr()` for the instance memory. Init/fini/info/intr reuse GP100 helpers.

## State and persistence
State is inherited from common fault and GP100 buffer metadata. Persistent hardware state is the GP100-style buffer registers programmed with a direct memory address.

## Dependencies and integration points
Depends on common fault base, GP100 helper exports, and Tegra-compatible memory addressing.

## Risks
Using BAR2 on Tegra would be wrong; using direct physical address on non-Tegra would also be wrong. The distinction is entirely in this pin hook.

## Test signals
GP10B fault buffer initialization, correct memory address programmed, event notification on GPU faults, and absence of BAR2 dependency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/gp10b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/gv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/gv100.c

## Purpose
Implements GV100/Volta fault handling with replayable and non-replayable fault buffers, in-kernel non-replayable processing work, direct fault interrupt decoding, and user event exposure.

## Important APIs, types, and functions
Exports `gv100_fault_new()` and `gv100_fault_oneinit()`. Important functions are `gv100_fault_buffer_process()`, `gv100_fault_intr()`, `gv100_fault_intr_fault()`, buffer info/init/fini/intr helpers, and `gv100_fault_ntfy_nrpfb()`.

## Control flow
Buffer info enables size readout, records entries and get/put offsets. Init writes buffer address and enables it. Interrupt handling decodes direct fault status, notifies replayable and non-replayable buffer events when present, and logs unhandled bits. The non-replayable event schedules work that maps the buffer, walks entries from get to put, decodes address/instance/time/engine/access/client/reason fields, advances get, and forwards each fault to `nvkm_fifo_fault()`.

## State and persistence
Persistent state includes two possible fault buffers, an event notification for non-replayable processing, work item `nrpfb_work`, buffer get/put hardware pointers, and direct fault registers. User exposure currently points at replayable Volta fault buffer class.

## Dependencies and integration points
Depends on `nvkm_memory` kmap/ro32, FIFO fault reporting, event notification, MMU/fifo headers, GP100 BAR2 pinning, and NVIF Volta fault buffer class.

## Risks
The TODO notes non-replayable buffer exposure is unresolved because both NVKM and SVM need access. Workqueue processing must keep get/put synchronized with hardware or faults can be lost/reprocessed. Direct interrupt fields must be decoded exactly.

## Test signals
Replayable and non-replayable fault generation, workqueue drain, FIFO fault logs, interrupt status clearing, event subscription, suspend/fini flushing work, and get/put wraparound handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/gv100.c -->
