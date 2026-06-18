# sources/distributed-fs/ceph-client/drivers/memory/mtk-smi.c

## Purpose
`mtk-smi.c` is the MediaTek Smart Multimedia Interconnect driver. It manages SMI common and local-arbiter (larb) blocks, configures IOMMU port routing, bus selection, outstanding transaction limits, sleep control, clocks, runtime PM, and component binding to the MediaTek IOMMU stack.

## Important APIs, Types, And Functions
`struct mtk_smi_common_plat` describes common/sub-common SoC data, including generation, GALS clocks, bus selection, and init register table. `struct mtk_smi_larb_gen` describes larb port layout, port-configuration callback, direct-to-common mask, feature flags, and outstanding-limit tables. `struct mtk_smi` holds common state and clocks; `struct mtk_smi_larb` embeds it and adds larb base, common-device link, larb generation data, larb id, MMU bitmap, and bank array.

Larb config functions are generation-specific: gen1 writes secure config in the always-on common region, MT8167/MT8173 write a single MMU-enable register, and gen2-general handles throttling, software flags, OSTD limits, secure-world SMC configuration, and per-port `SMI_LARB_NONSEC_CON` MMU/bank fields. Probe paths are `mtk_smi_larb_probe()` and `mtk_smi_common_probe()`. Runtime PM callbacks enable clocks and restore register programming.

## Control Flow
Both common and larb drivers are registered together. Common probe selects SoC data, gets required clocks, maps either AO or gen2 base, optionally links a sub-common to its parent common, enables runtime PM, and stores drvdata. Larb probe maps registers, gets clocks, device-links to common, enables runtime PM, and registers a component. Component bind receives IOMMU larb metadata and stores the larb id plus MMU/bank pointers. Larb resume enables clocks, disables sleep protection when required, then configures ports.

## State And Persistence
Runtime state is mostly clock/runtime-PM and pointers to IOMMU-provided bitmaps. Hardware state includes common init registers, `SMI_BUS_SEL`, larb sleep-control bits, OSTD limits, secure config, non-secure MMU enable bits, and bank selection. These are restored on runtime resume, not persisted across reboot.

## Dependencies And Integration Points
The driver depends on platform devices, OF compatibles for many MediaTek SoCs, component framework, MediaTek IOMMU data structures from `<soc/mediatek/smi.h>`, runtime PM, clock bulk APIs, device links, and ARM SMCCC secure monitor calls for SoCs with secure port control.

## Risks
Correctness is heavily SoC-table-driven; wrong `bus_sel`, OSTD, flags, or larb masks can break display/camera/media DMA. Secure monitor failures abort port configuration. The source contains a duplicated `for` line in `mtk_smi_larb_config_port_gen2_general()`, which would be a compile-time error if present exactly as read. `put_device(common->smi_common_dev)` is called even when that pointer may be NULL for non-sub-common paths, which should be checked against kernel helper tolerance.

## Test Signals
Tests should include compile coverage, probe order with deferred common devices, component bind with IOMMU larb metadata, runtime suspend/resume clock balancing, secure SMC return handling, and per-SoC register traces for bus selection and larb MMU/bank programming.
