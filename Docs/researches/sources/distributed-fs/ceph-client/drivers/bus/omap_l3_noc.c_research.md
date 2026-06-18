# sources/distributed-fs/ceph-client/drivers/bus/omap_l3_noc.c

## Purpose
This is the OMAP4/OMAP5/DRA7/AM437x L3 NOC error handler. It decodes interconnect application/debug faults, identifies the target and master from register tables, emits detailed warnings, clears handled errors, and masks undocumented un-clearable sources to avoid interrupt storms.

## Important APIs, Types, and Functions
The runtime object is `struct omap_l3` from `omap_l3_noc.h`. `omap_l3_probe()` copies SoC-specific static data, maps each L3 module, and requests debug and application IRQs. `l3_interrupt_handler()` locates the active flagmux bit and delegates to `l3_handle_target()`. `l3_handle_target()` reads target stderrlog registers, distinguishes standard versus custom errors, decodes master ID, opcode, request mode, target name, and clears the log with `CLEAR_STDERR_LOG`. `l3_resume_noirq()` reapplies software masks for ignored bits after suspend.

## Control Flow
At `postcore_initcall_sync`, the platform driver registers early enough to catch bus faults. Probe maps module resources, respecting `L3_BASE_IS_SUBMODULE` aliases, then requests two hard IRQ handlers with `IRQF_NO_THREAD`. On IRQ, the handler selects application or debug registers from the IRQ number, masks already ignored bits, handles the first set error bit, and returns immediately after one source. Unknown targets are logged, masked in hardware, and recorded in `mask_app_bits` or `mask_dbg_bits`.

## State and Persistence
SoC tables are static, but probe copies the matched `struct omap_l3` into device-managed memory and mutates runtime bases, IRQ numbers, and ignore masks. The masks persist in memory and are restored to hardware after noirq resume.

## Dependencies and Integration Points
The driver depends on OF matching, platform IRQ/resource descriptions, MMIO, and the SoC tables in `omap_l3_noc.h`. It integrates with kernel diagnostics through `WARN()` and with PM through noirq resume.

## Risks and Test Signals
Risks include table/register offset drift, `BUG_ON()` for out-of-range target indexes, only handling the first pending source per IRQ, and masking real faults if an undocumented bit appears. Test signals are decoded L3 warning messages for injected illegal accesses, no interrupt storm after boot-time stale bits, correct noirq resume mask restoration, and successful probing on each compatible SoC.
