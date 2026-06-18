# subset-b-001100 MediaTek clock driver research

This grouped report covers the requested MediaTek clock-controller source files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779.c

## Purpose

This is the main MT6779 clock driver. It registers topckgen clocks, apmixed PLLs, apmixed 26 MHz gates, and infracfg always-on gates for a mobile SoC. The top side exposes a large rate tree made from fixed factors, muxes with update bits, and audio mux/divider composites. The infracfg side exposes peripheral and system bus gates for PMIC, GCE, I2C, PWM, UART, MSDC, UFS, USB, security, modem, audio, and ADSP paths.

## Important APIs, types, and functions

Important local objects are `top_fixed_clks`, `top_divs`, many `*_parents` arrays, `top_muxes`, `top_aud_muxes`, `top_aud_divs`, `infra_clks`, `apmixed_clks`, and `plls`. The registration entry points are `clk_mt6779_apmixed_probe()`, `clk_mt6779_top_probe()`, `clk_mt6779_probe()`, and the `clk_mt6779_init()` `arch_initcall`. The driver uses `struct mtk_pll_data`, `struct mtk_mux`, `struct mtk_composite`, `struct mtk_gate`, `struct mtk_gate_regs`, and `struct mtk_clk_desc`.

## Control flow, state, and persistence

`clk_mt6779_init()` registers two platform drivers: the match-data dispatcher for `"mediatek,mt6779-apmixed"` and `"mediatek,mt6779-topckgen"`, plus a separate simple infracfg driver for `"mediatek,mt6779-infracfg_ao"`. Topckgen maps the MMIO resource, allocates `CLK_TOP_NR_CLK` onecell data, registers fixed clocks, factors, muxes under `mt6779_clk_lock`, and audio composites before adding the OF provider. APMIXED allocates `CLK_APMIXED_NR_CLK`, registers PLLs and apmixed gates, then publishes the provider. Infra uses `mtk_clk_simple_probe()` with `infra_desc`. Runtime state is hardware register state and common-clock registrations; the driver does not persist state across reboot.

## Dependencies and integration points

The file depends on `clk-mtk.h`, `clk-gate.h`, `clk-mux.h`, `clk-pll.h`, and `dt-bindings/clock/mt6779-clk.h`. It integrates with device-tree compatible strings, Linux CCF provider lookup, and consumers in display, camera, audio, storage, USB, UFS, modem, ADSP, and security blocks. Critical clocks include `axi_sel`, `spm_sel`, `sspm_sel`, and `apmixed_appll26m`, which are marked to avoid disabling bus/co-processor/PLL-root paths.

## Risks and test signals

The biggest risks are parent-name mismatches, wrong mux update offsets, gate polarity mistakes, and accidentally losing `CLK_IS_CRITICAL` on bus or always-on clocks. Probe error paths are sparse and do not unregister all prior allocations on every later failure. Test by booting MT6779 device trees, checking `/sys/kernel/debug/clk/clk_summary`, probing display/camera/audio/UFS/USB paths, and verifying no clk disable warning or hang occurs when unused clocks are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-apmixedsys.c

## Purpose

This MT6795 apmixedsys driver registers PLLs, PLL frequency-hopping metadata, and the `ref2usb_tx` clock, then performs a modem-domain MD1 setup sequence. It is the PLL root provider for the MT6795 clock tree and supplies main, universal, multimedia, storage, video, audio, and CPU PLLs to topckgen and subsystem consumers.

## Important APIs, types, and functions

The file defines `plls[]` using `struct mtk_pll_data`, `pllfhs[]` using `struct mtk_pllfh_data`, and the helper `clk_mt6795_apmixed_setup_md1()`. The probe uses `devm_platform_ioremap_resource()`, `mtk_alloc_clk_data()`, `fhctl_parse_dt()`, `mtk_clk_register_pllfhs()`, `mtk_clk_register_ref2usb_tx()`, and `of_clk_add_hw_provider()`. Remove reverses the provider, `ref2usb_tx`, PLLFH, and onecell allocation. The compatible is `"mediatek,mt6795-apmixedsys"`.

## Control flow, state, and persistence

Probe maps the apmixedsys register bank, allocates `CLK_APMIXED_NR_CLK`, parses FHCTL data for `"mediatek,mt6795-fhctl"`, registers PLL/FH clocks, registers `ref2usb_tx` from `REG_REF2USB`, publishes the clock provider, then clears MD1 power/isolation/clock/memory-off bits in `REG_AP_PLL_CON7`. The only persistent effects are CCF registrations and hardware register writes until reset. The MD1 writes are read-modify-write sequences, so concurrent firmware ownership would matter.

## Dependencies and integration points

Dependencies include `clk-fhctl.h`, `clk-pllfh.h`, `clk-pll.h`, `clk-mtk.h`, and `dt-bindings/clock/mediatek,mt6795-clk.h`. It feeds topckgen parent names such as `mainpll`, `univpll`, `mmpll`, `msdcpll`, `vcodecpll`, `vencpll`, `tvdpll`, `apll1`, and `apll2`. FHCTL integration lets configured PLLs use spread-spectrum or DVFS-safe frequency hopping.

## Risks and test signals

Risks include incorrect PLL PCW fields, FHCTL offsets, or MD1 setup ordering causing unstable clocks or random modem crashes. The file calls `platform_get_drvdata()` in remove, so the generic registration helpers must have stored `clk_data`. Test signals are successful boot, stable MD1/modem bring-up, USB PHY reference operation, clk summary showing all PLLs, and unload/reload cleanup if built as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-infracfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-infracfg.c

## Purpose

This MT6795 infracfg driver provides always-on infrastructure clocks, two CA53 CPU muxes, and an infracfg reset controller. It covers debug, SMI, audio, GCE, L2C SRAM, M4U, MD1, device APC, TRNG, CPUM, keypad, and related bus clocks.

## Important APIs, types, and functions

The central data is `infra_gates[]`, `cpu_muxes[]`, `infra_ao_rst_ofs[]`, `infra_ao_idx_map[]`, and `clk_rst_desc`. `clk_mt6795_infracfg_probe()` maps the resource, allocates `CLK_INFRA_NR_CLK`, registers resets with `mtk_register_reset_controller_with_dev()`, gates with `mtk_clk_register_gates()`, CPU muxes with `mtk_clk_register_cpumuxes()`, and publishes the onecell provider. Remove unregisters the provider, CPU muxes, gates, and allocation.

## Control flow, state, and persistence

The probe is linear with unwind labels for composite/gate failures. Gate registers use set/clear/status offsets `0x40`, `0x44`, and `0x48` with `mtk_clk_gate_ops_no_setclr`, while CPU muxes live at offset `0x00` and select between `clk26m`, `armca53pll`, `mainpll`, and `univpll`. The reset controller exposes selected reset bits from banks at `0x30` and `0x34`. State is CCF/reset registration plus hardware gate, mux, and reset register state.

## Dependencies and integration points

Dependencies include `clk-cpumux.h`, `clk-gate.h`, `clk-mtk.h`, `reset.h`, `dt-bindings/clock/mediatek,mt6795-clk.h`, and `dt-bindings/reset/mediatek,mt6795-resets.h`. The provider is bound by `"mediatek,mt6795-infracfg"` and consumed by core bus, modem, security, keypad, and multimedia subsystems.

## Risks and test signals

Risks include reset index-map mistakes, CPU mux parent mistakes, and gate polarity/register offset mismatch. Test by validating CPU frequency switching, reset lines for scpsys/PMIC wrap/MIPI/MM IOMMU, and clock summary entries for all `infra_*` clocks after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-infracfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-mfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-mfg.c

## Purpose

This small MT6795 MFG clock driver registers GPU/manufacturing subsystem gates. It provides bus AXI, memory, 3D engine, and 26 MHz gates for the `"mediatek,mt6795-mfgcfg"` clock provider.

## Important APIs, types, and functions

The driver defines `mfg_cg_regs`, `GATE_MFG()`, `mfg_clks[]`, `mfg_desc`, and `of_match_clk_mt6795_mfg[]`. It uses the generic `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()` platform-driver callbacks with `struct mtk_clk_desc`.

## Control flow, state, and persistence

The generic probe maps the clock controller, allocates onecell data sized from `mfg_desc`, registers the four gates, and adds an OF clock provider. Gate operations use set/clear registers at `0x4` and `0x8` and status at `0x0` with normal set/clear semantics. The only state is common-clock registration and hardware gate bits until reset.

## Dependencies and integration points

Dependencies are `clk-gate.h`, `clk-mtk.h`, Linux platform device support, and MT6795 clock bindings. The MFG gates depend on topckgen parents `axi_mfg_in_sel`, `mem_mfg_in_sel`, `mfg_sel`, and `clk26m`. GPU and power-domain code consume these clocks during MFG power-up.

## Risks and test signals

Risks are limited but include wrong parent names, wrong gate shifts, and enabling GPU clocks before MFG power domains are ready. Test with GPU probe/runtime PM, `clk_summary`, and suspend/resume transitions that gate and ungate the MFG domain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-mfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-mm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-mm.c

## Purpose

This MT6795 MMSYS driver registers multimedia and display gates. It covers SMI, MDP, display overlays/RDMA/WDMA/color/AAL/gamma/UFOE/split/merge/OD, display PWM, DSI, DPI, and related multimedia clocks.

## Important APIs, types, and functions

The important definitions are `mm0_cg_regs`, `mm1_cg_regs`, `GATE_MM0()`, `GATE_MM1()`, `mm_gates[]`, and `mm_desc`. Unlike most OF-matched files, it binds through a `platform_device_id` table named `"clk-mt6795-mm"` and uses `mtk_clk_pdev_probe()`/`mtk_clk_pdev_remove()`.

## Control flow, state, and persistence

The platform-device probe receives `mm_desc` through `driver_data`, registers the two gate banks, and publishes clocks. MM0 uses offsets `0x104/0x108/0x100`; MM1 uses `0x114/0x118/0x110`. All gates use set/clear semantics. State is hardware gate state and clock-provider registration.

## Dependencies and integration points

Dependencies are MT6795 clock bindings and the MediaTek gate/simple platform helper code. Parent clocks are mainly `mm_sel`, with display pixel paths also using `pwm_sel`, `dsi0_dig`, `dsi1_dig`, and `dpi0_sel`. The file integrates with display, DRM, MDP, SMI/LARB, DSI, DPI, and display PWM consumers.

## Risks and test signals

Risks include shifted display gates causing blank panels, incorrect platform-device binding, and parent mismatch with topckgen. Test with DRM modeset, MDP pipeline use, SMI/LARB activity, DSI/DPI panels, and suspend/resume clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-pericfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-pericfg.c

## Purpose

This MT6795 pericfg driver exposes peripheral gates, UART source muxes, and a simple reset controller. It supplies clocks for NFI, thermal, PWM, USB, DMA, MSDC, IRDA, UART, I2C, AUXADC, SPI, and the peripheral bus.

## Important APIs, types, and functions

Important data includes `peri_cg_regs`, `peri_clks[]`, `peri_gates[]`, `peri_rst_ofs[]`, `peri_idx_map[]`, `clk_rst_desc`, and `mt6795_peri_clk_lock`. `clk_mt6795_pericfg_probe()` registers resets, gates, composites, and the OF provider; remove reverses composites and gates.

## Control flow, state, and persistence

Probe maps the resource, allocates `CLK_PERI_NR_CLK`, registers reset bank `0x0`, registers gates at set/clear/status offsets `0x8/0x10/0x18`, registers four UART muxes at `0x40c`, and publishes the provider. The spinlock protects composite mux register updates. State is the hardware reset, gate, and mux registers and their CCF objects.

## Dependencies and integration points

Dependencies include `clk-gate.h`, `clk-mtk.h`, `reset.h`, MT6795 clock bindings, and MT6795 reset bindings. It integrates with serial, SPI, I2C, USB, PWM, MMC, NAND, thermal, DMA, and reset consumers. Topckgen parents include `axi_sel`, `usb30_sel`, `usb20_sel`, `msdc50_0_sel`, `msdc30_*_sel`, `irda_sel`, `spi_sel`, and `clk26m`.

## Risks and test signals

Risks include reset-bank map errors, UART mux selection bugs, and gate polarity mistakes. Test by probing UARTs, I2C, SPI, USB, MMC/NAND, thermal, and reset-controlled blocks; also verify `clk_summary` parent choices after changing UART source clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-pericfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-topckgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-topckgen.c

## Purpose

This MT6795 topckgen driver is the central non-PLL clock tree provider. It declares fixed clocks, fixed-factor PLL derivatives, top muxes, and audio mux/divider composites for bus, memory, multimedia, MFG, camera, UART, SPI, USB, MSDC, audio, PMIC, SCP, MJC, DPI, IRDA, CCI400, and display-related paths.

## Important APIs, types, and functions

Important objects include many `*_parents` arrays, `fixed_clks[]`, `top_divs[]`, `top_muxes[]`, `top_aud_divs[]`, and `topck_desc`. The custom macros `TOP_MUX_GATE_NOSR()` and `TOP_MUX_GATE()` wrap `MUX_GATE_CLR_SET_UPD_FLAGS()` to express clear/set/update muxes. The platform driver uses `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()` for `"mediatek,mt6795-topckgen"`.

## Control flow, state, and persistence

Generic simple probe consumes `topck_desc`: it registers fixed clocks, fixed factors, muxes under `mt6795_top_clk_lock`, audio composites, and the OF provider. Muxes use `CLK_CFG_*` registers from `0x40` through `0xb0`; audio dividers use `0x120` through `0x12c`. Critical flags are applied to AXI, memory, DDRPHYCFG, and CCI400-related paths. Hardware state persists until reset.

## Dependencies and integration points

Dependencies are `clk-gate.h`, `clk-mtk.h`, `clk-mux.h`, and MT6795 bindings. It consumes PLL names from apmixedsys and provides parent clocks to infracfg, pericfg, MMSYS, MFG, VDEC, VENC, audio, display, USB, storage, and camera consumers. Dummy-rate fixed clocks represent external or product-specific rates that are intentionally not modeled.

## Risks and test signals

Risks include parent-order mistakes, missing `CLK_SET_RATE_PARENT` where rate propagation is required, incorrect critical flags, and divider/mux register overlap. Test with full boot, clock summary parent/rate validation, display DPI/DSI, audio I2S, MMC, USB, camera/display pipelines, and idle clock disabling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-topckgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-vdecsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-vdecsys.c

## Purpose

This MT6795 VDEC system driver registers the video decoder engine and LARB gates. It is a small subsystem provider for `"mediatek,mt6795-vdecsys"`.

## Important APIs, types, and functions

The file defines `vdec0_cg_regs`, `vdec1_cg_regs`, `GATE_VDEC()`, `vdec_clks[]`, and `vdec_desc`. It relies on `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()` through a normal OF-matched platform driver.

## Control flow, state, and persistence

Generic probe registers two inverted set/clear gates: `vdec_cken` on the `vdec_sel` parent and `vdec_larb_cken` on the `mm_sel` parent. VDEC0 uses offsets `0x0/0x4/0x0`; VDEC1 uses `0x8/0xc/0x8`. Inverted gate semantics mean the register bit polarity is opposite a normal set/clear gate. State is the hardware gate value and clock-provider registration.

## Dependencies and integration points

Dependencies are MT6795 bindings and MediaTek gate/simple helpers. It integrates with the VDEC codec driver, MMSYS/SMI/LARB paths, and topckgen parent clocks.

## Risks and test signals

Risks include inverted gate polarity mistakes and missing LARB clock enable during decode DMA. Test with video decode workloads, runtime PM, SMI/LARB access, and `clk_summary` gate transitions while the decoder is active and idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-vdecsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-vencsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-vencsys.c

## Purpose

This MT6795 VENC system driver registers video encoder, JPEG encoder/decoder, and LARB gates. It provides the `"mediatek,mt6795-vencsys"` clock provider for media codecs.

## Important APIs, types, and functions

Key definitions are `venc_cg_regs`, `GATE_VENC()`, `venc_clks[]`, and `venc_desc`. Binding and registration use `of_match_clk_mt6795_vencsys[]`, `mtk_clk_simple_probe()`, and `mtk_clk_simple_remove()`.

## Control flow, state, and persistence

Generic simple probe registers four inverted set/clear gates using offsets `0x4/0x8/0x0`, with shifts 0, 4, 8, and 12. Parents are `venc_sel` for codec engines and `venc_sel` for the LARB gate. Hardware gate state persists until reset or runtime clock operations change it.

## Dependencies and integration points

The file depends on MT6795 clock bindings and MediaTek gate/simple helpers. It integrates with V4L2 codec drivers, JPEG blocks, SMI/LARB, and the topckgen `venc_sel` parent.

## Risks and test signals

Risks are gate polarity and shift mistakes, plus the module description says "vdecsys" even though the driver is VENC. Test with video encode/JPEG workloads, runtime PM, and clock summary transitions for all four gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-vencsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-img.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-img.c

## Purpose

This MT6797 imgsys driver registers image subsystem gates for FDVT, DPE, DIP, and LARB6. It provides the `"mediatek,mt6797-imgsys"` clock domain for camera/imaging blocks.

## Important APIs, types, and functions

Important definitions are `img_cg_regs`, `GATE_IMG()`, `img_clks[]`, `img_desc`, and the OF match table. The driver is descriptor-only and uses `mtk_clk_simple_probe()`/`mtk_clk_simple_remove()`.

## Control flow, state, and persistence

The generic probe registers four normal set/clear gates at offsets `0x4/0x8/0x0`, all parented by `mm_sel`. The gate shifts are 11, 10, 6, and 0. Hardware gate state and the CCF provider are the only lasting state.

## Dependencies and integration points

Dependencies are `clk-mtk.h`, `clk-gate.h`, and `dt-bindings/clock/mt6797-clk.h`. It integrates with image processing, face detection, depth/dual-pixel processing, DIP, and SMI LARB6 consumers.

## Risks and test signals

Risks include shifted gate IDs and lack of image pipeline clocking under runtime PM. Test camera/imaging pipelines, LARB6 DMA, and gate toggling in `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-mm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-mm.c

## Purpose

This MT6797 multimedia clock driver registers MMSYS gates for SMI, MDP, display, DSI, DPI, MJC/LARB4, and supporting fake-engine clocks. It supplies display and media pipelines.

## Important APIs, types, and functions

The file defines `mm0_cg_regs`, `mm1_cg_regs`, `GATE_MM0()`, `GATE_MM1()`, `mm_clks[]`, and `mm_desc`. Binding is via platform device id `"clk-mt6797-mm"` and generic `mtk_clk_pdev_probe()`/`mtk_clk_pdev_remove()`.

## Control flow, state, and persistence

MM0 gates use offsets `0x104/0x108/0x100`; MM1 gates use `0x114/0x118/0x110`. The platform-device probe registers the descriptor from `driver_data` and creates the clock provider. Gates are normal set/clear. State persists in hardware register bits and in CCF registrations.

## Dependencies and integration points

Dependencies are MT6797 clock bindings plus MediaTek gate/platform helpers. Parent clocks include `mm_sel`, `dpi0_sel`, `mjc_sel`, and `clk26m`. Consumers include DRM display, MDP, DSI/DPI, SMI/LARB, and multimedia runtime-PM users.

## Risks and test signals

Risks include platform-device binding mismatch, display gate shifts, and missing LARB/MJC clocks for memory transactions. Test with display scanout, DSI/DPI interfaces, MDP operations, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-vdec.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-vdec.c

## Purpose

This MT6797 VDEC driver registers video decoder gates: decoder engine, active, cken, and LARB1. It provides clocks for `"mediatek,mt6797-vdecsys"`.

## Important APIs, types, and functions

Important data includes two gate-register banks, `GATE_VDEC0()`, `GATE_VDEC1()`, `vdec_clks[]`, and `vdec_desc`. The platform driver uses `mtk_clk_simple_probe()`/`remove`.

## Control flow, state, and persistence

Generic probe registers three inverted gates on `vdec0_cg_regs` at shifts 8, 4, and 0, plus one inverted LARB gate on `vdec1_cg_regs` at shift 0. Parents are `vdec_sel` and `mm_sel`. State is CCF registration and hardware gate bits.

## Dependencies and integration points

Dependencies are MT6797 clock bindings and MediaTek gate helpers. It integrates with video decoder runtime PM, V4L2 codec stack, and SMI/LARB1 memory paths.

## Risks and test signals

Risks include inverted gate misuse, missing `vdec_active`, and LARB clock dependencies. Test video decode, power-domain cycling, and clock enable/disable traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-venc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-venc.c

## Purpose

This MT6797 VENC driver registers four inverted video encoder subsystem gates under `"mediatek,mt6797-vencsys"`.

## Important APIs, types, and functions

Key definitions are `venc_cg_regs`, `GATE_VENC()`, `venc_clks[]`, `venc_desc`, and the OF platform driver. Generic MediaTek simple probe/remove perform registration.

## Control flow, state, and persistence

The driver registers gates at shifts 0, 4, 8, and 12 using offsets `0x4/0x8/0x0`. `venc_0` is parented by `mm_sel`; the remaining gates use `venc_sel`. Hardware gate state persists until reset or CCF operations change it.

## Dependencies and integration points

It depends on MT6797 bindings and gate helpers. Consumers are video encode/JPEG blocks and associated media runtime-PM code.

## Risks and test signals

Risks are wrong gate polarity/parent selection and failure to enable `mm_sel` for the LARB-like path. Test video encode, JPEG paths, runtime PM, and clk summary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797.c

## Purpose

This is the main MT6797 clock driver for topckgen, infracfg, and apmixedsys. It registers fixed PLL-derived factors, top muxes, infrastructure gates/factors, and PLLs for the SoC. It also has an early infracfg provider path so early boot consumers can defer safely until the full platform driver registers gates.

## Important APIs, types, and functions

Important data includes `top_fixed_divs[]`, many parent arrays, `top_muxes[]`, `infra_clks[]`, `infra_fixed_divs[]`, global `infra_clk_data`, and `plls[]`. Entry points are `mtk_topckgen_init()`, `mtk_infrasys_init_early()`, `mtk_infrasys_init()`, `mtk_apmixedsys_init()`, `clk_mt6797_probe()`, and `clk_mt6797_init()`. The early hook uses `CLK_OF_DECLARE_DRIVER()` for `"mediatek,mt6797-infracfg"`.

## Control flow, state, and persistence

The `arch_initcall` registers one platform driver whose match data selects the init routine for topckgen, infracfg, or apmixedsys. Topckgen maps MMIO, allocates `CLK_TOP_NR`, registers factors and composites, then publishes a provider. Early infracfg allocates global onecell data, fills entries with `ERR_PTR(-EPROBE_DEFER)`, registers `clk13m`, and publishes the provider. Full infracfg replaces defers with `-ENOENT`, registers gates/factors, and adds the provider. APMIXED registers PLLs. State is global CCF provider data and hardware register state.

## Dependencies and integration points

Dependencies include `clk-gate.h`, `clk-mtk.h`, `clk-pll.h`, OF platform support, and `dt-bindings/clock/mt6797-clk.h`. Critical infrastructure gates `infra_dramc_f26m` and `infra_dramc_b_f26m` protect DRAM clocks, and `ddrphycfg_sel` is critical to avoid boot hangs. Consumers include core buses, storage, USB, display, media, audio, PMIC, security, and modem interfaces.

## Risks and test signals

Risks include early-provider lifetime issues, duplicate `of_clk_add_hw_provider()` for infracfg, missing critical flags, and lack of unregister/error cleanup. Test early boot without probe deferrals, DRAM stability, full clock summary, media/storage/USB/audio devices, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-apmixedsys.c

## Purpose

This MT7622 apmixedsys driver registers router SoC PLLs and a critical `main_core_en` gate. PLLs include ARM, main, universal, Ethernet, audio, TRG, and SGMII sources.

## Important APIs, types, and functions

The file defines `PLL_xtal()`, `PLL()`, `plls[]`, `apmixed_cg_regs`, `apmixed_clks[]`, `clk_mt7622_apmixed_probe()`, and `clk_mt7622_apmixed_remove()`. It uses `mtk_devm_alloc_clk_data()`, `mtk_clk_register_plls()`, `mtk_clk_register_gates()`, and `of_clk_add_hw_provider()`.

## Control flow, state, and persistence

Probe maps MMIO, allocates `CLK_APMIXED_NR_CLK`, registers PLLs, registers the critical inverted no-setclr `main_core_en` gate, and publishes the provider. Failure unwinds gates and PLLs. Remove deletes the provider and unregisters gates and PLLs. State is hardware PLL/gate programming and CCF registration.

## Dependencies and integration points

Dependencies include `clk-pll.h`, `clk-gate.h`, `clk-mtk.h`, and `dt-bindings/clock/mt7622-clk.h`. PLL parent names default to `clkxtal`. Topckgen and Ethernet/HIF/audio consumers depend on PLL names such as `mainpll`, `univ2pll`, `eth1pll`, `eth2pll`, `aud1pll`, `aud2pll`, and `sgmipll`.

## Risks and test signals

Risks include wrong reset-bar bit, critical gate polarity, and PLL parent-name mismatch. Test boot clock summary, Ethernet/SGMII rates, audio PLL users, CPU frequency path, and module removal if configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-aud.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-aud.c

## Purpose

This MT7622 audio clock driver registers audsys gates and populates child platform devices below the audio node. It covers AFE, HDMI/SPDIF/APLL, I2S input/output, ASRC, A1/A2 system, memory ASRC, and playback/capture data-path gates.

## Important APIs, types, and functions

Data includes four gate-register banks `audio0_cg_regs` through `audio3_cg_regs`, `audio_clks[]`, and `audio_desc`. The custom `clk_mt7622_aud_probe()` wraps `mtk_clk_simple_probe()` and then calls `devm_of_platform_populate()`. Remove depopulates children and calls `mtk_clk_simple_remove()`.

## Control flow, state, and persistence

Probe first registers the clock provider from `audio_desc`. If child population fails, it removes the clocks. Gate operations use no-setclr registers, with offsets `0x0`, `0x10`, `0x14`, and `0x634`. State is clock-provider registration, child platform-device population, and hardware gate bits.

## Dependencies and integration points

Dependencies include OF platform helpers, `clk-mtk.h`, `clk-gate.h`, and MT7622 bindings. Parent clocks include `rtc`, `apll1_ck_sel`, `a1sys_hp_sel`, `a2sys_hp_sel`, `asm_h_sel`, `intdir_sel`, and `aud_mux1_sel`. It integrates with ASoC and audio front-end child devices.

## Risks and test signals

Risks include no-setclr polarity errors, child-device ordering problems, and audio-parent mismatches. Test ASoC probe, I2S playback/capture, SPDIF/HDMI audio, ASRC use, child device population, and runtime PM gate transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-aud.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-eth.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-eth.c

## Purpose

This MT7622 Ethernet clock driver registers ethsys gates, sgmiisys gates, and an ethsys reset controller. It supports HSDMA, Ethernet switch/GMAC paths, and SGMII reference/feedback clocks.

## Important APIs, types, and functions

Important data includes `eth_cg_regs`, `sgmii_cg_regs`, `eth_clks[]`, `sgmii_clks[]`, `clk_rst_desc`, `eth_desc`, and `sgmii_desc`. The OF table maps `"mediatek,mt7622-ethsys"` and `"mediatek,mt7622-sgmiisys"` to the appropriate descriptor for `mtk_clk_simple_probe()`.

## Control flow, state, and persistence

Generic probe registers either ethsys or sgmiisys based on match data. Ethsys also exposes a simple reset bank at `0x34`. Gates use inverted no-setclr semantics with status/set/clear all at `0x30` or `0xe4`. State is hardware gate/reset state and provider registration.

## Dependencies and integration points

Dependencies are MT7622 bindings, `clk-gate.h`, `clk-mtk.h`, and reset support via descriptor. Topckgen parents include `eth_sel`, `eth_500m`, `txclk_src_pre`, `ssusb_tx250m`, `ssusb_eq_rx250m`, `ssusb_cdr_ref`, and `ssusb_cdr_fb`. Consumers include Ethernet MAC, switch, HSDMA, and SGMII PHY glue.

## Risks and test signals

Risks include inverted gate polarity and reset bank misbinding. Test Ethernet link up, switch traffic, SGMII link negotiation, HSDMA, and reset-controller users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-hif.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-hif.c

## Purpose

This MT7622 HIF driver registers PCIe, SATA, and SSUSB subsystem gates plus a reset controller for HIF blocks.

## Important APIs, types, and functions

It defines `pcie_cg_regs`, `ssusb_cg_regs`, `ssusb_clks[]`, `pcie_clks[]`, shared `clk_rst_desc`, `ssusb_desc`, and `pcie_desc`. The OF table maps `"mediatek,mt7622-pciesys"` and `"mediatek,mt7622-ssusbsys"` to descriptors used by `mtk_clk_simple_probe()`.

## Control flow, state, and persistence

Generic probe registers the matched gate set and reset bank at `0x34`. All gates use inverted no-setclr operations against offset `0x30`. State is clock/reset hardware state and CCF/reset provider registration.

## Dependencies and integration points

Dependencies include MT7622 clock bindings, MediaTek gate helpers, and reset descriptors. Parent clocks come from topckgen fixed/factor/mux outputs such as `to_u2_phy`, `to_usb3_ref`, `to_usb3_sys`, `axi_sel`, `hif_sel`, PCIe MAC/PIPE, SATA ASIC/RBC, and `univpll2_d4`. Consumers are PCIe, SATA, and xHCI/USB PHY drivers.

## Risks and test signals

Risks include wrong gate polarity, shared reset bank assumptions, and parent-rate mismatches for PCIe/SATA reference paths. Test PCIe enumeration on both ports, SATA link, USB2/USB3 operation, and reset control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-hif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-infracfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-infracfg.c

## Purpose

This MT7622 infracfg driver registers core infrastructure gates, one CPU mux, and a simple reset controller. It supplies clocks for debug, TRNG, audio, IRRX, APXGPT, and PMIC paths.

## Important APIs, types, and functions

Important definitions are `infra_cg_regs`, `infra_mux1_parents`, `cpu_muxes[]`, `infra_clks[]`, `infrasys_rst_ofs[]`, and `clk_rst_desc`. `clk_mt7622_infracfg_probe()` performs explicit reset, gate, CPU-mux, and provider registration with unwind labels; remove unregisters provider, CPU muxes, gates, and data.

## Control flow, state, and persistence

Probe maps the resource, allocates `CLK_INFRA_NR_CLK`, registers reset bank `0x30`, registers set/clear gates at offsets `0x40/0x44/0x48`, registers `infra_mux1_sel` at offset `0x0`, and publishes the OF provider. State is hardware gate/mux/reset bits and CCF/reset objects.

## Dependencies and integration points

Dependencies include `clk-cpumux.h`, `clk-gate.h`, `clk-mtk.h`, `reset.h`, and MT7622 bindings. Parent clocks include `clkxtal`, `armpll`, `main_core_en`, `axi_sel`, `aud_intbus_sel`, `irrx_sel`, `f10m_ref_sel`, and `pmicspi_sel`. It integrates with CPU clocking, PMIC, timers, audio, and reset consumers.

## Risks and test signals

Risks include CPU mux parent ordering, reset-controller registration failure, and missing gate unwind. Test CPU mux switching, TRNG/timer/PMIC/audio consumers, and reset lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-infracfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622.c

## Purpose

This MT7622 top/peripheral clock driver registers topckgen clocks and pericfg gates/muxes/resets. It provides central fixed clocks, PLL factors, top gates, adjustable audio dividers, top muxes, peripheral gates, and a peribus mux.

## Important APIs, types, and functions

Important data includes parent arrays for AXI, memory, Ethernet, flash, audio, USB, and peripheral paths; `top_fixed_clks[]`, `top_divs[]`, `top_clks[]`, `top_adj_divs[]`, `peri_clks[]`, `top_muxes[]`, `peri_muxes[]`, `clk_rst_desc`, `topck_desc`, and `peri_desc`. The OF table maps `"mediatek,mt7622-topckgen"` and `"mediatek,mt7622-pericfg"` to descriptors for `mtk_clk_simple_probe()`.

## Control flow, state, and persistence

The generic probe registers either the full top descriptor or pericfg descriptor. Topckgen includes fixed clocks for USB/PCIe/SATA/SGMII references, many PLL factors, no-setclr top gates, adjustable dividers, and composite muxes under `mt7622_clk_lock`. Pericfg registers set/clear peripheral gates, one peribus mux, and a two-bank simple reset controller. State is hardware clock/reset state and CCF provider state.

## Dependencies and integration points

Dependencies are `clk-cpumux.h`, `clk-gate.h`, `clk-mtk.h`, MT7622 bindings, and Linux clock consumer helpers. It integrates with apmixed PLLs, infracfg, Ethernet, HIF, audio, serial, SPI, flash/NFI, MMC, USB, and reset consumers. Critical top muxes include AXI, memory, and DDRPHYCFG.

## Risks and test signals

Risks include top/peri descriptor mismatches, parent-order errors, critical flag loss, and reset-bank offset mistakes. Test boot, Ethernet/HIF/audio/peripheral devices, flash and MMC, peribus mux rate, and idle-clock disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7629-eth.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7629-eth.c

## Purpose

This MT7629 Ethernet driver registers ethsys and two SGMII system clock providers. It also registers an ethsys reset controller.

## Important APIs, types, and functions

Important definitions are `eth_clks[]`, a two-dimensional `sgmii_clks[2][4]`, `clk_mt7629_ethsys_init()`, `clk_mt7629_sgmiisys_init()`, `clk_mt7629_eth_probe()`, and `clk_rst_desc`. The platform driver is built in with `builtin_platform_driver()`.

## Control flow, state, and persistence

Probe dispatches to a match-data init function. Ethsys allocates `CLK_ETH_NR_CLK`, registers inverted no-setclr gates, publishes the provider, and registers reset bank `0x34`. Sgmiisys allocates `CLK_SGMII_NR_CLK` and uses a static `id` to pick the first or second SGMII gate array before publishing the provider. State includes the static SGMII instance counter, hardware gates, reset provider, and CCF provider registrations.

## Dependencies and integration points

Dependencies are MT7629 bindings and MediaTek gate/reset helpers. Parents include `eth2pll`, `txclk_src_pre`, `eth_500m`, and USB-derived SGMII reference clocks. Consumers are Ethernet FE/GMAC, switch, and two SGMII PHY instances.

## Risks and test signals

The static `id++` makes SGMII assignment depend on probe order and has no bound check. Other risks are inverted gate polarity and ignoring reset registration errors. Test both SGMII instances in either DT order, Ethernet traffic, reset users, and built-in early boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7629-eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7629-hif.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7629-hif.c

## Purpose

This MT7629 HIF driver registers PCIe and SSUSB gate providers plus a simple reset bank for high-speed I/O.

## Important APIs, types, and functions

Key objects are `pcie_cg_regs`, `ssusb_cg_regs`, `ssusb_clks[]`, `pcie_clks[]`, `clk_rst_desc`, `ssusb_desc`, and `pcie_desc`. The OF table selects descriptors for `"mediatek,mt7629-pciesys"` and `"mediatek,mt7629-ssusbsys"`.

## Control flow, state, and persistence

Generic simple probe registers matched inverted no-setclr gates at offset `0x30` and a reset bank at `0x34`. The CCF provider and reset controller remain registered until driver removal; hardware gate state persists until reset.

## Dependencies and integration points

Dependencies are MT7629 bindings, `clk-gate.h`, and `clk-mtk.h`. Parent clocks include USB PHY/reference paths, `to_usb3_sys`, `to_usb3_mcu`, `to_usb3_dma`, top AXI/AHB factors, PCIe MAC and PIPE clocks. Consumers are USB3/xHCI and PCIe port drivers.

## Risks and test signals

Risks include wrong module description text, parent-name mismatches with topckgen, and reset-bank assumptions shared between PCIe and USB. Test PCIe enumeration, USB host operation, and reset lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7629-hif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7629.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7629.c

## Purpose

This is the combined MT7629 clock driver for apmixedsys, infracfg, topckgen, and pericfg. It registers PLLs, fixed clocks, factors, muxes, infra/peri gates, CPU muxes, and a peribus mux for a networking SoC.

## Important APIs, types, and functions

Important data includes `plls[]`, `apmixed_clks[]`, `infra_clks[]`, `top_fixed_clks[]`, `top_divs[]`, `peri_clks[]`, `infra_muxes[]`, `top_muxes[]`, and `peri_muxes[]`. Init functions are `mtk_topckgen_init()`, `mtk_infrasys_init()`, `mtk_pericfg_init()`, and `mtk_apmixedsys_init()`, selected by `clk_mt7629_probe()` from OF match data.

## Control flow, state, and persistence

The `arch_initcall` registers a platform driver for four compatible strings. Topckgen maps MMIO, registers fixed clocks/factors/composites, then explicitly prepares and enables AXI, memory, and DDRPHYCFG muxes before publishing the provider. Infracfg registers gates and CPU muxes. Pericfg registers gates and the peribus mux, publishes provider, and enables UART0. APMIXED registers PLLs/gates and enables ARMPLL plus `main_core_en`. State includes enabled critical clocks, CCF providers, and hardware registers.

## Dependencies and integration points

Dependencies include `clk-cpumux.h`, `clk-gate.h`, `clk-mtk.h`, `clk-pll.h`, and MT7629 clock bindings. It feeds Ethernet, SGMII, HIF/PCIe/USB, flash, MMC, crypto, serial, SPI, and peripheral consumers.

## Risks and test signals

Risks include explicit `clk_prepare_enable()` calls without cleanup, critical bus clocks not marked through flags, match-data dispatcher errors, and sparse error unwinding. Test boot, clock summary, Ethernet/SGMII, PCIe/USB, flash/MMC, UART console, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7629.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-apmixed.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-apmixed.c

## Purpose

This MT7981 apmixedsys driver registers eight PLLs for CPU, networking, multimedia, SGMII, WED MCU, memory, and audio. It is a built-in PLL root provider for router-class MT7981 systems.

## Important APIs, types, and functions

The file defines `PLL_xtal()`, `PLL()`, `plls[]`, `clk_mt7981_apmixed_probe()`, and `of_match_clk_mt7981_apmixed[]`. It uses `mtk_alloc_clk_data()`, `mtk_clk_register_plls()`, and `of_clk_add_hw_provider()`.

## Control flow, state, and persistence

Probe allocates onecell data sized to `ARRAY_SIZE(plls)`, registers PLLs, and publishes the provider. On provider failure it frees the clock data, but there is no PLL unregister path in that error branch. The driver is registered by `builtin_platform_driver()`. State is PLL hardware configuration and CCF provider registration.

## Dependencies and integration points

Dependencies are `clk-pll.h`, `clk-mux.h`, `clk-gate.h`, `clk-mtk.h`, MT7981 bindings, and `clkxtal` as parent. Topckgen uses PLL names such as `net1pll`, `net2pll`, `mmpll`, `mpll`, `sgmpll`, `wedmcupll`, and `apll2`.

## Risks and test signals

Risks include PCW field mistakes, array-size clock data depending on dense IDs, and missing unregister on provider failure. Test boot clock summary, topckgen parent rates, Ethernet/WED paths, and audio PLL users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-apmixed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-eth.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-eth.c

## Purpose

This MT7981 Ethernet clock driver registers ethsys and two SGMII system providers. It supplies FE, GP, WOCPU, and SGMII TX/RX/CDR gates.

## Important APIs, types, and functions

Key data includes `sgmii0_clks[]`, `sgmii1_clks[]`, `eth_clks[]`, and descriptors `eth_desc`, `sgmii0_desc`, and `sgmii1_desc`. The OF match table maps `"mediatek,mt7981-ethsys"`, `"mediatek,mt7981-sgmiisys_0"`, and `"mediatek,mt7981-sgmiisys_1"` to `mtk_clk_simple_probe()`.

## Control flow, state, and persistence

Generic probe registers the descriptor selected by compatible string. Eth gates use inverted no-setclr operations at offset `0x30`; SGMII gates use offset `0xe4`. State is hardware gate bits and CCF provider registration.

## Dependencies and integration points

Dependencies include `clk-mtk.h`, `clk-gate.h`, and `dt-bindings/clock/mediatek,mt7981-clk.h`. Parent clocks are topckgen outputs like `netsys_2x`, `sgm_325m`, `netsys_wed_mcu`, `usb_tx250m`, `usb_eq_rx250m`, `usb_ln0`, and `usb_cdr`. Consumers include MediaTek Ethernet, SGMII PHY glue, and WED offload firmware/CPU paths.

## Risks and test signals

Risks include parent-name drift between topckgen and ethsys, inverted gate polarity mistakes, and WOCPU clock dependency failures. Test Ethernet traffic, SGMII0/1 links, WED offload, and clock summary gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-infracfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-infracfg.c

## Purpose

This MT7981 infracfg driver registers infrastructure factor, mux, and gate clocks for low-speed peripherals, storage, USB, PCIe, audio, DMA, security, and debug paths.

## Important APIs, types, and functions

Important definitions include `infra_divs[]`, parent arrays for UART/SPI/PWM/PCIe muxes, `infra_muxes[]`, three gate-register banks, `infra_clks[]`, and `infracfg_desc`. The driver is descriptor-based with `mtk_clk_simple_probe()`/`remove`.

## Control flow, state, and persistence

The simple probe registers one fixed factor `infra_66m_mck`, muxes protected by `mt7981_clk_lock`, and gates across INFRA0-2. Muxes use clear/set/update offsets such as `0x18/0x10/0x14` and `0x28/0x20/0x24`. Gates use normal set/clear banks at `0x40`, `0x50`, and `0x60`. State is CCF provider registration and hardware mux/gate bits.

## Dependencies and integration points

Dependencies are `clk-mtk.h`, `clk-gate.h`, `clk-mux.h`, and MT7981 bindings. Parent clocks come from topckgen, including `sysaxi`, `csw_f26m_sel`, `uart_sel`, `spi_sel`, `spim_mst_sel`, `pwm_sel`, `pextp_tl_ck_sel`, storage, USB, audio, and RTC paths. Consumers include UART/SPI/I2C/PWM, eMMC/NAND, USB, PCIe, audio, security, and DMA drivers.

## Risks and test signals

Risks include mux parent mismatch, update-bit omissions, and gate shifts for storage/USB/PCIe. Test serial/SPI/I2C/PWM, eMMC/NAND, PCIe, USB, audio, and clock summary parent selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-infracfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-topckgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-topckgen.c

## Purpose

This MT7981 topckgen driver builds the main fixed-factor and mux clock tree for networking, storage, peripheral, audio, USB, PCIe, DRAM, AXI/APB, and WED paths.

## Important APIs, types, and functions

Important data includes `top_divs[]`, many `__initconst` parent arrays, `top_muxes[]`, one audio divider composite in `top_aud_divs[]`, and `topck_desc`. The platform driver binds `"mediatek,mt7981-topckgen"` to `mtk_clk_simple_probe()`.

## Control flow, state, and persistence

Simple probe registers fixed factors, muxes under `mt7981_clk_lock`, one composite audio divider, and the OF provider. Muxes use clear/set/update register triplets from `0x000` through `0x080`, with update bits at `0x1c0`/`0x1c4`. Critical flags protect `csw_f26m_sel`, `dramc_sel`, `dramc_md32_sel`, `sysaxi_sel`, `sysapb_sel`, and `sgm_reg_sel`. Hardware state persists until reset or CCF operations.

## Dependencies and integration points

Dependencies are `clk-mtk.h`, `clk-gate.h`, `clk-mux.h`, and MT7981 bindings. It consumes PLLs from apmixed and supplies parents to infracfg, ethsys/SGMII, PCIe, USB, eMMC/NAND, SPI/I2C/UART/PWM, WED MCU, and audio blocks.

## Risks and test signals

Risks include critical clock flag removal, update-bit mistakes, and parent-name mismatch with infracfg/eth. Test boot stability, Ethernet/WED, storage, PCIe/USB, peripheral clocks, audio, and `clk_summary` rate/parent checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-topckgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-apmixed.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-apmixed.c

## Purpose

This MT7986 apmixedsys driver registers eight PLLs similar to MT7981: ARM, NET2, MM, SGM, WEDMCU, NET1, MPLL, and APLL2. It is a built-in PLL provider.

## Important APIs, types, and functions

Important elements are `PLL_xtal()`, `PLL()`, `plls[]`, `clk_mt7986_apmixed_probe()`, and the compatible `"mediatek,mt7986-apmixedsys"`. It uses `mtk_alloc_clk_data()`, `mtk_clk_register_plls()`, and `of_clk_add_hw_provider()`.

## Control flow, state, and persistence

Probe allocates clock data sized by the PLL array, registers all PLLs, and publishes the OF provider. On provider failure it frees the data but does not unregister PLLs. State is CCF registration and PLL hardware control until reset.

## Dependencies and integration points

Dependencies include MT7986 clock bindings, `clk-pll.h`, `clk-mtk.h`, and the `clkxtal` parent. Topckgen consumes these PLLs for networking, memory, multimedia, WED, SGMII, and audio-derived clocks.

## Risks and test signals

Risks are array-size/ID assumptions, PLL field mistakes, and missing cleanup on provider failure. Test boot, topckgen rates, Ethernet/WED throughput, SGMII, and audio users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-apmixed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-eth.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-eth.c

## Purpose

This MT7986 Ethernet driver registers ethsys plus SGMII0 and SGMII1 gate providers. It supplies FE, GP, WOCPU0/1, and SGMII reference gates.

## Important APIs, types, and functions

Important data includes `sgmii0_clks[]`, `sgmii1_clks[]`, `eth_clks[]`, and descriptors for each compatible. It uses `mtk_clk_simple_probe()`/`remove` for `"mediatek,mt7986-ethsys"`, `"mediatek,mt7986-sgmiisys_0"`, and `"mediatek,mt7986-sgmiisys_1"`.

## Control flow, state, and persistence

Generic probe registers the matched descriptor. SGMII gates use inverted no-setclr at `0xe4`; eth gates use inverted no-setclr at `0x30`. State is gate hardware state and provider registration.

## Dependencies and integration points

Dependencies are MT7986 bindings and MediaTek gate helpers. Parent names refer to topckgen muxes such as `netsys_2x_sel`, `sgm_325m_sel`, `netsys_mcu_sel`, and `top_xtal`. Consumers are Ethernet MAC/switch, WED offload CPUs, and SGMII PHY glue.

## Risks and test signals

Risks include parent-name mismatch, inverted gate polarity, and missing WOCPU clocks for offload. Test Ethernet traffic, SGMII0/1 links, WED offload, and clock summary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-infracfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-infracfg.c

## Purpose

This MT7986 infracfg driver registers infrastructure factor, mux, and gate clocks for peripherals, storage, USB, PCIe, audio, EIP97, TRNG, DMA, and security/debug paths.

## Important APIs, types, and functions

Important definitions include `infra_divs[]`, parent arrays for UART/SPI/PWM/PCIe, `infra_muxes[]`, gate banks `infra0_cg_regs` through `infra2_cg_regs`, `infra_clks[]`, and `infra_desc`. It is descriptor-based via `mtk_clk_simple_probe()`.

## Control flow, state, and persistence

Simple probe registers `infra_sysaxi_d2`, muxes under `mt7986_clk_lock`, gates across three banks, and the OF provider. Muxes use register triplets at `0x18/0x10/0x14` and `0x28/0x20/0x24`; gates use normal set/clear banks at `0x40`, `0x50`, and `0x60`. State is hardware mux/gate settings and CCF provider data.

## Dependencies and integration points

Dependencies include MT7986 clock bindings, `clk-mux.h`, `clk-gate.h`, and `clk-mtk.h`. Parent clocks come from MT7986 topckgen, including `sysaxi_sel`, `csw_f26m_sel`, `eip_b_sel`, `u2u3_sys_sel`, `u2u3_sel`, `pextp_tl_ck_sel`, and storage/audio/peripheral parents. Consumers include UART/SPI/I2C/PWM, eMMC/NAND, USB, PCIe, EIP97 crypto, audio, and DMA.

## Risks and test signals

Risks include mux parent mismatch, update-bit mistakes, and gate shifts for storage/USB/PCIe/security. Test all low-speed buses, storage, PCIe, USB, crypto, TRNG, audio, and `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-infracfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-topckgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-topckgen.c

## Purpose

This MT7986 topckgen driver provides fixed clocks, fixed factors, and muxes for storage, SPI/I2C/UART/PWM, PCIe, eMMC, DRAM, AXI/APB, debug, networking, SGMII, audio, USB, and AP2CNN host paths.

## Important APIs, types, and functions

Important objects are `top_fixed_clks[]`, `top_divs[]`, parent arrays, `top_muxes[]`, and `topck_desc`. The driver uses `mtk_clk_simple_probe()` for `"mediatek,mt7986-topckgen"`.

## Control flow, state, and persistence

Simple probe registers fixed clocks `top_xtal` and `top_jtag`, fixed factors, muxes under `mt7986_clk_lock`, and the OF provider. Muxes use clear/set/update register triplets from `0x000` through `0x090` with update bits in `0x1c0`/`0x1c4`. Critical flags protect DRAM, DRAMC MD32, SYSAXI, SYSAPB, SGM register, and F26M selections. State is hardware mux settings and CCF registration.

## Dependencies and integration points

Dependencies are MT7986 bindings and MediaTek mux/gate helpers. It consumes apmixed PLLs and supplies parent clocks to infracfg, Ethernet/SGMII, USB, PCIe, eMMC/NAND, SPI/I2C/UART/PWM, WED, audio, and crypto.

## Risks and test signals

Risks include critical-clock flag loss, parent naming drift with infracfg/eth, and wrong update bits. Test boot, storage, network/WED, USB/PCIe, peripheral buses, and clock summary rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-topckgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-apmixed.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-apmixed.c

## Purpose

This MT7988 apmixedsys driver registers a larger PLL set for networking, memory, multimedia, audio, WED MCU, SGMII/USXGMII, CPU, CCI, and MSDC. It is a built-in PLL provider for MT7988.

## Important APIs, types, and functions

Important definitions are `MT7988_PCW_CHG_BIT`, the `PLL()` macro, `plls[]`, `clk_mt7988_apmixed_probe()`, and compatible `"mediatek,mt7988-apmixedsys"`. The driver uses `mtk_clk_register_plls()`, `mtk_clk_unregister_plls()`, and `of_clk_add_hw_provider()`.

## Control flow, state, and persistence

Probe allocates onecell data sized by the PLL array, registers PLLs, publishes the provider, and unwinds PLLs/data on failure. PLL definitions include reset-bar masks, PCW change registers, optional tuner fields for APLL2, parent `"clkxtal"`, and `MT7988_PCW_CHG_BIT`. State is PLL hardware programming and CCF registration.

## Dependencies and integration points

Dependencies include MT7988 clock bindings, `clk-pll.h`, and MediaTek clock helpers. Topckgen and subsystem drivers consume names such as `netsyspll`, `mpll`, `mmpll`, `apll2`, `net1pll`, `net2pll`, `wedmcupll`, `sgmpll`, `arm_b`, `ccipll2_b`, `usxgmiipll`, and `msdcpll`.

## Risks and test signals

Risks include PCW change-bit mistakes, reset-bar bit shifts, and PLL ID density assumptions. Test topckgen rates, CPU/CCI clocks, Ethernet/USXGMII, eMMC/MSDC, audio, and cleanup on provider failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-apmixed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-eth.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-eth.c

## Purpose

This MT7988 Ethernet driver registers ethdma, SGMII0, SGMII1, and ethwarp clock providers, plus an ethwarp reset controller. It covers XGP/GP/FE/ESW/crypto gates and WOCPU gates for Ethernet offload.

## Important APIs, types, and functions

Important data includes `ethdma_clks[]`, `sgmii0_clks[]`, `sgmii1_clks[]`, `ethwarp_clks[]`, `ethwarp_rst_desc`, and descriptors `ethdma_desc`, `sgmii0_desc`, `sgmii1_desc`, and `ethwarp_desc`. The OF table handles `"mediatek,mt7988-ethsys"`, `"mediatek,mt7988-sgmiisys0"`, `"mediatek,mt7988-sgmiisys1"`, and `"mediatek,mt7988-ethwarp"`.

## Control flow, state, and persistence

Generic simple probe registers the descriptor selected by compatible. Ethdma gates use inverted no-setclr register `0x30`, SGMII gates use `0xe4`, and ethwarp gates use `0x14`. Ethwarp exposes reset offset `0x8` with index map `MT7988_ETHWARP_RST_SWITCH -> bit 9`. State is gate/reset hardware state and provider registration.

## Dependencies and integration points

Dependencies include `clk-mtk.h`, `clk-gate.h`, `reset.h`, MT7988 clock bindings, and reset bindings. Parent clocks include `netsys_2x_sel`, `netsys_gsw_sel`, `eip197_sel`, `netsys_mcu_sel`, and `top_xtal`. Consumers are Ethernet DMA/switch, SGMII PHY glue, crypto offload, and WED/WOCPU firmware paths.

## Risks and test signals

Risks include wrong reset mapping, parent-name mismatch with topckgen, and inverted gate polarity. Test XGMAC/SGMII links, Ethernet switch traffic, crypto offload, WED/WOCPU boot, and reset-controller operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-infracfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-infracfg.c

## Purpose

This MT7988 infracfg driver registers infrastructure muxes, gates, and reset lines for UART/SPI/PWM, PCIe, USB, audio, storage, DMA, debug, DRAM, security, and low-speed peripheral paths.

## Important APIs, types, and functions

Important definitions include reset offsets `MT7988_INFRA_RST0_SET_OFFSET` and `MT7988_INFRA_RST1_SET_OFFSET`, `infra_muxes[]`, four gate-register banks, `infra_clks[]`, `infra_rst_desc`, and `infra_desc`. It uses `mtk_clk_simple_probe()`/`remove` for `"mediatek,mt7988-infracfg"`.

## Control flow, state, and persistence

Simple probe registers muxes under `mt7988_clk_lock`, gates across INFRA0-3, and a set/clear reset controller. Muxes select UART, SPI, PWM, and four PCIe TL outputs using register triplets at `0x18/0x10/0x14` and `0x28/0x20/0x24`. Gates use normal set/clear operations across offsets `0x10`, `0x40`, `0x50`, and `0x60`. Reset mapping exposes PEXTP MAC and thermal controller resets. State is hardware mux/gate/reset state and provider registration.

## Dependencies and integration points

Dependencies include `clk-mtk.h`, `clk-gate.h`, `clk-mux.h`, MT7988 clock bindings, and MT7988 reset bindings. Parent clocks come from MT7988 topckgen outputs such as `csw_infra_f26m_sel`, `uart_sel`, `spi_sel`, `spim_mst_sel`, `sysaxi_sel`, `pwm_sel`, `pextp_tl*_sel`, `aud_l_sel`, `a1sys_sel`, `usb_*_sel`, `emmc_*_sel`, and `top_xtal`. Consumers include serial/SPI/PWM, USB, PCIe ports 0-3, storage, audio, DMA, JTAG/debug, and reset users.

## Risks and test signals

Risks include numerous PCIe/USB gate shifts, critical flags on DRAM/debug/NFI/SPI/RTC/USB frame counters, reset index-map errors, and parent-name drift. Test all PCIe ports, USB ports, UART/SPI/PWM, storage, audio, thermal reset, debug/JTAG, and `clk_summary` after idle clock pruning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-infracfg.c -->
