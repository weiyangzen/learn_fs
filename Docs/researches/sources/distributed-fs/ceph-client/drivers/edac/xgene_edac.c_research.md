# sources/distributed-fs/ceph-client/drivers/edac/xgene_edac.c

## Purpose
`xgene_edac.c` is the EDAC platform driver for AppliedMicro/APM X-Gene SoCs. It registers separate EDAC memory-controller and EDAC-device instances for MCU DRAM controllers, PMD CPU/L1/L2 cache blocks, L3 cache blocks, and SoC fabric/IOB errors, then reports corrected and uncorrected hardware errors through the EDAC core in either polling or interrupt mode.

## Important APIs, types, and functions
The root state is `struct xgene_edac`, which owns syscon regmaps, the PCP CSR mapping, shared interrupt masks, debugfs root, child lists, and MCU active/registered masks. Child state is split into `struct xgene_edac_mc_ctx`, `struct xgene_edac_pmd_ctx`, and `struct xgene_edac_dev_ctx`. Key flows are `xgene_edac_probe()`, `xgene_edac_isr()`, `xgene_edac_mc_add()/check()/irq_ctl()`, `xgene_edac_pmd_add()/check()`, `xgene_edac_l3_add()/check()`, and `xgene_edac_soc_add()/check()`. It uses `edac_mc_handle_error()`, `edac_device_handle_ce()`, `edac_device_handle_ue()`, syscon `regmap_read/write`, MMIO `readl/writel`, and optional EDAC debugfs injection handlers.

## Control flow
Module init refuses to load when GHES EDAC devices are present, normalizes `edac_op_state`, and registers a device-tree platform driver for `apm,xgene-edac`. Probe resolves required syscon phandles (`regmap-csw`, `regmap-mcba`, `regmap-mcbb`, `regmap-efuse`), optionally resolves the register-bus regmap, maps PCP CSRs, requests three shared IRQs in interrupt mode, creates debugfs, and iterates child DT nodes. MCU nodes are filtered against active memory-controller topology before `edac_mc_add_mc()`. PMD nodes are filtered using efuse disabled-PMD bits. L3 and SoC nodes become EDAC devices.

At runtime, polling callbacks or the top-level ISR read PCP high/low priority status and MEMERR status, then fan out to registered child checkers. MCU checking walks ranks, reports MCU uncorrectable/correctable rank errors, logs bank/row/column/count for CEs, clears per-rank status, and handles MCU address decode errors. PMD checking decodes CPU ICF/LSU/MMU L1 errors, shared L2 ECC and timeout status, and clears each status register. L3 checking logs syndrome, tag/data, agent, operation, physical address, bank, and promotes known broken version-1 CE syndromes to UE. SoC checking reports IOB/XGIC/RB/PA/BA transaction errors and SoC parity sources.

## State and persistence behavior
All state is runtime-only. The driver persists child registration in linked lists, MCU active/registered bitmasks, EDAC control structures, debugfs dentries, and hardware MMIO/register bits. Interrupt mask updates are serialized with a spinlock; shared MCU top-level interrupt enable is serialized with `mc_lock` so the shared bit is not unmasked until all active MCUs are registered. No disk or cross-boot state is written.

## Dependencies and integration points
The file depends on device tree, platform devices, Linux EDAC core, EDAC debugfs, syscon regmaps, MMIO resources, IRQs, `ghes_get_devices()`, and X-Gene-specific DT child compatibles. It integrates with the EDAC core as both `mem_ctl_info` and `edac_device_ctl_info` providers, and exposes optional error-injection files when `CONFIG_EDAC_DEBUG` is enabled.

## Risks and edge cases
The shared MCU top-level interrupt can wedge if unmasked before all active MCUs register; the active/registered mask logic is the explicit mitigation. Many hardware status registers are write-to-clear or clear-by-writing-status, so incorrect ordering can lose diagnostics. Probe ignores child-add return values while continuing with other children, which makes partial EDAC coverage possible. L3 v1 syndrome promotion is hardware erratum-sensitive. Optional `rb_map` absence must not block SoC reporting. Debugfs injection writes synthetic error bits directly and is unsafe outside debug use.

## Test signals
Useful signals include boot probing with all DT child compatible variants, poll and interrupt modes, shared IRQ storms, inactive MCU and disabled-PMD filtering, GHES conflict behavior, MCU rank CE/UE injection, PMD L1/L2 debugfs injection, L3 erratum promotion cases, SoC IOB/RB/PA/BA transaction status clearing, remove/unload cleanup, and fault injection for missing phandles, missing IRQs, and failed resource maps.
