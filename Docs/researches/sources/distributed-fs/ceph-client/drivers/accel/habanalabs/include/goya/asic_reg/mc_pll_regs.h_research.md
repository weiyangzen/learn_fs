# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mc_pll_regs.h

Purpose: auto-generated register-address map for the Goya MC PLL block, the memory-controller clock PLL instance using the generic `PLL` prototype.

Important APIs/types/functions: no C functions or types. `mmMC_PLL_*` macros describe the same PLL register families as IC PLL but rooted at `0x4A1100`: `NR`, `NF`, `OD`, `NB`, `CFG`, lock/loss/reset/data-change controls, slip watchdog, four divider factor/command/select/enable/busy groups, clock gater/relax registers, reference counter period and thresholds, `PLL_NOT_STABLE`, and frequency calculation enable.

Control flow: constants-only. Clock or hardware-manager code programs PLL ratios and dividers, commands divider updates, waits for busy/lock/stability status, and monitors reference thresholds through these addresses.

State and persistence: configuration persists in the MC PLL hardware until reset or rewrite. Busy/lock/not-stable fields are live hardware status. `goya_blocks.h` maps the containing block as `mmMC_PLL_BASE`.

Dependencies and integration: included by `goya_regs.h`. Its layout mirrors `ic_pll_regs.h`, enabling shared PLL-management assumptions while preserving the MC-specific base address.

Risks: MC PLL mistakes can destabilize memory-controller timing, leading to hangs or memory data loss. Because the register names are a clone of other PLLs, base-address confusion between MC and IC/CPU/TPC PLLs is a realistic integration risk.

Test signals: memory-clock bring-up, PLL lock/stability checks, divider programming readback, memory stress under configured clocks, and reset/suspend/resume paths that reinitialize or validate the MC PLL.
