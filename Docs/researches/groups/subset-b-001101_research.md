<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-topckgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-topckgen.c

Purpose: This file registers MT7988 topckgen and mcusys clocks: fixed oscillator aliases, fixed PLL-derived factors, top-level muxes for networking/storage/audio/peripheral domains, one audio divider composite, and CPU/MCU bus mux composites.

Important APIs, types, and functions: It uses `struct mtk_fixed_clk`, `struct mtk_fixed_factor`, `struct mtk_mux`, `struct mtk_composite`, `struct mtk_clk_desc`, `mtk_clk_simple_probe`, and `mtk_clk_simple_remove`. `topck_desc` exposes `top_fixed_clks`, `top_divs`, `top_muxes`, `top_aud_divs`, and `mt7988_clk_lock`; `mcusys_desc` exposes `mcu_muxes`. OF compatibles are `mediatek,mt7988-topckgen` and `mediatek,mt7988-mcusys`.

Control flow: Platform probe is entirely table-driven. The common MediaTek simple probe obtains the MMIO base from the matching OF node, allocates onecell clock data, registers fixed clocks/factors, muxes, and composites from the selected descriptor, and publishes them as an OF clock provider. Consumers then select mux parents or audio divider rates through the common clock framework.

State and persistence behavior: State is volatile kernel clock-provider state plus register bits in the topckgen/mcusys MMIO blocks. The spinlock serializes mux and composite register updates. There is no disk persistence; removal unregisters the provider and clocks.

Dependencies and integration points: The driver depends on `clk-mtk.h`, `clk-gate.h`, `clk-mux.h`, the MT7988 clock binding IDs, DT clock names such as `top_xtal`, `net1pll`, `net2pll`, `mmpll`, `apll2`, and MediaTek common clock registration helpers. It feeds Ethernet, USXGMII, PCIe, storage, UART, SPI, I2C, audio, TOPS/NPU, and CPU-bus consumers.

Risks and edge cases: Parent arrays must match hardware mux encodings exactly; wrong order silently selects bad rates. Shared mux registers require the lock. The mcusys and topckgen descriptors share one driver but expose different clock sets, so compatible-string routing is critical. Network clocks use many divided PLL paths, making regressions visible as Ethernet/PCIe/USXGMII failures.

Test signals: Boot with both compatibles present, inspect `/sys/kernel/debug/clk/clk_summary`, exercise Ethernet/USXGMII, PCIe, eMMC/SPI/NAND, UART, I2C, and audio paths, change mux parents through consumers, and unload/reload the module where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-topckgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-xfipll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-xfipll.c

Purpose: This is the MT7988 XFI PLL clock provider for USXGMII. It creates a fixed-factor PLL clock from `top_xtal`, exposes an enable gate, and applies a documented analog software workaround before registering the clocks.

Important APIs, types, and functions: `xfipll_divs` defines `xfipll_pll` as a 125/32 factor of `top_xtal`; `xfipll_clks` defines `xfipll_pll_en` using `mtk_clk_gate_ops_no_setclr_inv`; `xfipll_desc` groups both. `clk_mt7988_xfipll_probe` maps the register block with `of_iomap`, writes `RG_XFI_PLL_ANA_SWWA` to `XFI_PLL_ANA_GLB8`, unmaps it, and delegates to `mtk_clk_simple_probe`.

Control flow: The custom probe performs the analog register write first. If mapping fails it returns `-ENOMEM`; otherwise the simple MediaTek probe registers the fixed factor and gate and publishes the OF provider for `mediatek,mt7988-xfi-pll`.

State and persistence behavior: Runtime state is limited to the registered clocks and the MMIO gate bit. The workaround write changes hardware register state for the lifetime of the device until reset or later firmware/kernel writes. Removal uses `mtk_clk_simple_remove`.

Dependencies and integration points: It depends on the MT7988 clock binding, common MediaTek gate/factor helpers, OF address mapping, and consumers in the USXGMII/XFI Ethernet path.

Risks and edge cases: The workaround uses raw `of_iomap`/`iounmap`, so failure handling is deliberately minimal. The gate uses inverted no-set/clear semantics, so a wrong gate operation would invert enable state. The fixed factor assumes the expected crystal parent.

Test signals: Validate that `xfipll_pll` and `xfipll_pll_en` appear in clock summary, the analog register contains `0x02283248` after probe, USXGMII links train reliably, and probe fails cleanly if the MMIO resource is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-xfipll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8135-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8135-apmixedsys.c

Purpose: This driver registers MT8135 apmixedsys PLLs, including ARM, main, universal, multimedia, storage, TV/display, LVDS, audio, and video decoder PLLs.

Important APIs, types, and functions: The `PLL` macro fills `struct mtk_pll_data` entries with register offsets, power registers, enable masks, PCW fields, post-divider fields, tuner registers, `HAVE_RST_BAR`, and the MT8135 reset-bar mask. `clk_mt8135_apmixed_probe` allocates `CLK_APMIXED_NR_CLK` onecell data, calls `mtk_clk_register_plls`, then `of_clk_add_hw_provider`. `clk_mt8135_apmixed_remove` unregisters the provider and PLLs.

Control flow: On `mediatek,mt8135-apmixedsys` probe, the driver obtains the node, allocates clock storage, registers every PLL table entry against the apmixedsys MMIO region through common helpers, and exposes the resulting hardware clocks to DT consumers. Error paths unregister already-created PLLs.

State and persistence behavior: PLL programming and enable state live in apmixedsys registers. The driver keeps only provider metadata and clock handles in memory. There is no persistent storage; remove deletes the provider and unregisters PLLs.

Dependencies and integration points: It depends on `clk-pll.h`, `clk-mtk.h`, MT8135 clock binding IDs, and parent consumers in topckgen and subsystem gates. The PLL names form the parent namespace used by `clk-mt8135.c`.

Risks and edge cases: Incorrect register offsets or PCW bit widths can produce wrong frequencies or failed PLL lock. Some PLLs use reset-bar behavior and some do not, so flag accuracy matters. The old manual allocation path requires remove/error cleanup symmetry.

Test signals: Boot-time PLL registration, clk summary parent rates, topckgen parent selection for `mainpll`, `univpll`, `mmpll`, `msdcpll`, `audpll`, and display PLLs, probe error injection for provider registration, and module remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8135-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8135.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8135.c

Purpose: This is the main MT8135 clock controller driver for topckgen, infracfg, and pericfg. It describes fixed PLL factors, top-level mux composites, infrastructure gates, peripheral gates, a UART peripheral composite, and reset controllers.

Important APIs, types, and functions: `top_divs` derives divided clocks from apmixedsys PLLs; many parent arrays feed `top_muxes`; `infra_clks` and `peri_gates` use `mtk_gate` definitions; `peri_clks` adds a UART selector. `infra_desc`, `peri_desc`, and `topck_desc` are selected by OF compatibles `mediatek,mt8135-infracfg`, `mediatek,mt8135-pericfg`, and `mediatek,mt8135-topckgen`. Reset descriptors cover infra and peri reset banks.

Control flow: `mtk_clk_simple_probe` matches a compatible string, selects the descriptor, registers factors/composites/gates/resets under the shared `mt8135_clk_lock` where needed, and exposes an OF clock provider. Consumers access clock IDs from `dt-bindings/clock/mt8135-clk.h`.

State and persistence behavior: Clock state is hardware MMIO state in topckgen/infracfg/pericfg registers plus volatile provider registrations. Reset-controller state is also register-backed. No persistent configuration is stored by the driver.

Dependencies and integration points: The file depends on MediaTek common clock/gate helpers, `clk-pll.h` parents provided by `clk-mt8135-apmixedsys.c`, syscon/reset infrastructure, and DT bindings. It integrates with CPU/bus, display, camera, VDEC/VENC, storage, USB, UART/SPI, PMIC wrapper, and memory-subsystem consumers.

Risks and edge cases: The file is table-dense; parent array order, mux field width, gate polarity, and reset bank offsets must match the SoC manual. Several muxes select display/video PLLs, making bad parents visible as display or codec instability. Shared registers require the lock to avoid read-modify-write races.

Test signals: Check all three compatibles bind, reset controls appear, clock summary shows expected parent trees, UART/SPI/MSDC/USB/display/video consumers probe, mux switching works under load, and remove unregisters providers without leaked clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8135.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-apmixedsys.c

Purpose: This driver registers MT8167 apmixedsys PLLs and one adjustable HDMI reference divider. It supplies root PLL parents used by the MT8167 top clock generator and media/peripheral clock trees.

Important APIs, types, and functions: `PLL`/`PLL_B` define `struct mtk_pll_data` entries for ARM, main, universal, MM, APLL1/APLL2, TVD, and LVDS PLLs, with `mmpll_div_table` for MMPLL post-divider choices. `adj_divs` exposes `hdmi_ref` from `tvdpll`. `clk_mt8167_apmixed_probe` maps MMIO, allocates `MT8167_CLK_APMIXED_NR_CLK`, registers PLLs, registers dividers under `mt8167_apmixed_clk_lock`, and publishes an OF provider.

Control flow: The built-in platform driver binds `mediatek,mt8167-apmixedsys` early enough for dependent clocks. Probe uses devm MMIO/allocation, then explicit rollback for PLL/divider/provider failures.

State and persistence behavior: PLL and divider settings are volatile apmixedsys register state. The clock provider is kernel runtime state. There is no remove callback because this built-in root clock driver is not intended to unload.

Dependencies and integration points: It depends on MT8167 clock bindings, `clk-pll.h`, `clk-mtk.h`, common divider helpers, and downstream topckgen/media drivers that reference `mainpll`, `univpll`, `mmpll`, `apll1`, `apll2`, `tvdpll`, and `hdmi_ref`.

Risks and edge cases: Divider registration shares apmixed registers and requires the lock. Missing remove means failed late cleanup is limited to error paths. Wrong PLL post-divider tables or reset-bar flags can break HDMI/display/audio/storage rates.

Test signals: Confirm built-in probe ordering, PLL and `hdmi_ref` presence in clk summary, HDMI/display/audio rate derivation, error rollback with simulated provider failure, and boot of topckgen consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-aud.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-aud.c

Purpose: This small provider exposes MT8167 audsys clock gates for AFE, I2S, PCM, SPDIF, APB, and related audio blocks.

Important APIs, types, and functions: `aud_cg_regs` uses a shared set/clear/status offset pattern; `GATE_AUD` builds `struct mtk_gate` entries with MediaTek set/clear gate ops; `aud_desc` contains the gate table; the platform driver binds `mediatek,mt8167-audsys` and uses `mtk_clk_simple_probe/remove`.

Control flow: Probe is descriptor-driven: map the audsys register block, register each gate under its DT clock ID, and publish the OF provider. Audio consumers enable the relevant gates through the common clock framework.

State and persistence behavior: Gate state persists only in audsys MMIO bits while the SoC is powered. Kernel state is the registered onecell provider and gate handles. Remove unregisters them.

Dependencies and integration points: It depends on `clk-gate.h`, `clk-mtk.h`, MT8167 binding IDs, and parent clocks from topckgen such as audio bus and audio engine selectors. ALSA/SoC audio drivers are the primary consumers.

Risks and edge cases: Gate bit positions and parent names must match the audio hardware. Incorrectly gating APB or AFE can hang or mute audio paths. Runtime PM users depend on enable/disable balance.

Test signals: Audio playback/capture, I2S and SPDIF operation, clk summary gate toggling during stream start/stop, and module bind/unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-aud.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-img.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-img.c

Purpose: This file registers MT8167 image subsystem gates for the image LARB, SMI, and camera/image processing clocks.

Important APIs, types, and functions: `img_cg_regs` describes the set/clear/status offsets; `GATE_IMG` creates `struct mtk_gate` entries; `img_desc` is selected by `mediatek,mt8167-imgsys`; probe/remove use MediaTek simple helpers.

Control flow: The platform driver maps the imgsys clock-gate registers, registers all gates in `img_clks`, and exposes them as an OF provider. Camera/image consumers request gates by MT8167 binding IDs.

State and persistence behavior: State is limited to volatile gate bits and the runtime clock-provider data. There is no software persistence.

Dependencies and integration points: It depends on common MediaTek clock gate code, `dt-bindings/clock/mt8167-clk.h`, and topckgen parents for the image domain. It integrates with image sensor/camera and memory-interface drivers.

Risks and edge cases: A wrong gate bit can block memory access for the image subsystem. Since gates share one register set, polarity and set/clear semantics are important.

Test signals: Image/camera pipeline probe, LARB/SMI access with clocks enabled, clk summary transitions during runtime PM, and clean provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-mfgcfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-mfgcfg.c

Purpose: This driver exposes MT8167 GPU manufacturing-domain clock gates, primarily the GPU/MFG bus and core gate controls.

Important APIs, types, and functions: `mfg_cg_regs` defines the MFG gate register offsets; `GATE_MFG` creates gates in `mfg_clks`; `mfg_desc` is matched by `mediatek,mt8167-mfgcfg`; `mtk_clk_simple_probe/remove` handle provider lifecycle.

Control flow: On probe, the common helper registers the MFG gate table against the compatible node. GPU drivers then enable the gates through CCF before accessing the hardware.

State and persistence behavior: Only MMIO gate bits and runtime provider structures are maintained. No state survives reset or driver removal.

Dependencies and integration points: It depends on MT8167 clock IDs, common MediaTek gate helpers, and top-level MFG parent clocks selected in `clk-mt8167.c`. It integrates with the GPU and power-domain sequencing.

Risks and edge cases: GPU clocks often interact with power domains; enabling a gate while the domain is off or using the wrong parent can cause bus faults. Gate polarity must match hardware.

Test signals: GPU probe and workload execution, runtime PM suspend/resume, clock summary gate enable counts, and bind/unbind checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-mfgcfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-mm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-mm.c

Purpose: This is the MT8167 multimedia system gate provider for display, SMI/LARB, MDP, DPI/DSI, and related MM clocks.

Important APIs, types, and functions: `mm0_cg_regs` and `mm1_cg_regs` describe two gate banks; `GATE_MM0` and `GATE_MM1` populate `mm_clks`; `mm_desc` groups the gates. Unlike OF-matched simple drivers, it uses a platform device ID `clk-mt8167-mm` and `mtk_clk_pdev_probe/remove`.

Control flow: A parent platform/MFD device instantiates `clk-mt8167-mm`; the pdev probe fetches `mm_desc` from driver data, registers all MM gate clocks, and provides them to consumers.

State and persistence behavior: Gate state is volatile MM system register state. The platform-device provider data is runtime-only and removed by `mtk_clk_pdev_remove`.

Dependencies and integration points: It depends on MediaTek common pdev clock helpers, MT8167 clock IDs, topckgen MM parents, and display/media consumers. The platform-device integration means DT matching may happen in a parent syscon/MFD path rather than directly here.

Risks and edge cases: Two register banks increase the chance of bit-offset mistakes. Display and memory paths are sensitive to gating order with power domains and larb/IOMMU setup.

Test signals: Display pipeline startup, MDP operations, LARB/SMI consumers, pdev creation from the parent device, runtime PM gate toggling, and module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-vdec.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-vdec.c

Purpose: This driver registers MT8167 video decoder subsystem gates.

Important APIs, types, and functions: Two gate banks are described by `vdec0_cg_regs` and `vdec1_cg_regs`. `GATE_VDEC0_I` and `GATE_VDEC1_I` use inverted gate operations for VDEC gate bits. `vdec_desc` is selected by `mediatek,mt8167-vdecsys`.

Control flow: `mtk_clk_simple_probe` maps the VDEC register block, registers the gate clocks, and exposes the OF clock provider. Codec drivers enable the gates while decoding.

State and persistence behavior: Runtime gate enable state is held in VDEC MMIO registers; the driver stores only provider metadata. Removal unregisters the gates and provider.

Dependencies and integration points: It depends on MT8167 binding IDs, MediaTek gate helpers, top-level VDEC parent muxes, media codec drivers, and often power-domain sequencing.

Risks and edge cases: The inverted gate ops are essential; using normal polarity would disable clocks when consumers request enable. Codec hardware may hang if LARB/SMI and VDEC gates are not sequenced coherently.

Test signals: Hardware video decode, clock summary enable counts during decode, suspend/resume of the VDEC power domain, and probe/remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167.c

Purpose: This is the main MT8167 topckgen/infracfg clock driver. It defines fixed clocks, PLL factors, a large set of top-level mux composites, infrastructure muxes, adjustable dividers, and top clock gates.

Important APIs, types, and functions: `fixed_clks`, `top_divs`, `top_muxes`, `ifr_muxes`, `top_adj_divs`, and `top_clks` are grouped into `topck_desc` and `infra_desc`. Gate banks `top0` through `top5` cover clocks for audio, storage, USB, display, NAND, GPU, and peripheral functions. The platform driver matches `mediatek,mt8167-topckgen` and `mediatek,mt8167-infracfg`.

Control flow: Simple probe chooses the descriptor from OF match data. For topckgen it registers fixed clocks, factors, composites, dividers, gates, and uses `mt8167_clk_lock`; for infracfg it registers infracfg composites. Consumers use binding IDs from `mt8167-clk.h`.

State and persistence behavior: Clock selection and divider/gate state reside in SoC clock registers. Provider state is volatile. The spinlock protects shared register updates for muxes/dividers/gates.

Dependencies and integration points: It depends on PLL parent names from apmixedsys, common MediaTek clock/gate/divider helpers, OF platform binding, and syscon/MFD headers. It feeds the whole MT8167 platform: AXI/infra, DDRPHY, MFG, MSDC, USB, audio, DPI, VDEC, Ethernet, NAND, SPI, I2C, UART, PWM, and debug clocks.

Risks and edge cases: This file is highly table-driven and vulnerable to parent-order, bit-field, and gate-polarity mistakes. Shared register locking is important. `top_muxes` is marked `__initdata`, so registration must copy or consume it before init memory is discarded.

Test signals: Boot all topckgen/infracfg consumers, compare rates against the datasheet, exercise storage/audio/display/VDEC/USB/Ethernet paths, verify gate polarity in clk summary, and run suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-apmixedsys.c

Purpose: This driver registers MT8173 apmixedsys PLLs with optional FHCTL/pllfh support and a special `ref2usb_tx` clock.

Important APIs, types, and functions: `plls` describes ARMCA15, ARMCA7, main, universal, MM, MSDC, VENC, TVD, MPLL, VCODEC, APLL, LVDS, and MSDCPLL2 PLLs. `pllfhs` maps selected PLLs to frequency-hopping data parsed by `fhctl_parse_dt`. `clk_mt8173_apmixed_probe` registers PLLFH clocks, registers `ref2usb_tx`, populates `CLK_APMIXED_HDMI_REF` as a fixed `tvdpll_594m`, then adds an OF provider. Remove unregisters the provider, ref2usb, and PLLFH clocks.

Control flow: Probe finds the optional `mediatek,mt8173-fhctl` node, maps apmixedsys MMIO, allocates onecell data, parses FHCTL metadata, registers PLLs with FH backing, creates the USB reference clock, fills the HDMI reference slot, and exposes clocks.

State and persistence behavior: PLL/FH/ref2usb state is hardware register state plus volatile provider data. Remove reverses provider and clock registration. There is no disk persistence.

Dependencies and integration points: It depends on `clk-fhctl.h`, `clk-pllfh.h`, `clk-pll.h`, `clk-mtk.h`, MT8173 clock IDs, FHCTL DT, and consumers in topckgen, USB, HDMI/display, CPU, storage, video, and audio.

Risks and edge cases: FHCTL parsing is optional but must align PLL IDs with hardware FH IDs. Ref2USB has custom registration and cleanup. The synthetic HDMI reference slot must match consumers expecting `CLK_APMIXED_HDMI_REF`.

Test signals: Boot with and without FHCTL node, validate PLL rates and frequency hopping registration, USB reference operation, HDMI/display clocks, error-path cleanup, and remove/unbind behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-img.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-img.c

Purpose: This file exposes MT8173 image subsystem clock gates.

Important APIs, types, and functions: `img_cg_regs` describes the image gate register bank; `GATE_IMG` creates `img_clks`; `img_desc` is attached to `mediatek,mt8173-imgsys`. The driver uses `mtk_clk_simple_probe/remove`.

Control flow: The OF platform driver registers image gates when the imgsys node probes. Consumers then enable the LARB/SMI and image processing gates by DT clock ID.

State and persistence behavior: The only persistent-at-runtime state is MMIO gate bits and common clock framework registration. Removal unregisters provider state.

Dependencies and integration points: It depends on MT8173 clock bindings, common MediaTek gate helpers, parent clocks from topckgen, and image/camera/media drivers.

Risks and edge cases: The driver name and description mention vdecsys even though it binds imgsys, so diagnostics can be confusing. Gate bit and parent mismatches can break image DMA paths.

Test signals: Imgsys node binding, camera/image pipeline operation, LARB clock enable sequencing, clk summary gate toggles, and module unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-infracfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-infracfg.c

Purpose: This driver handles MT8173 infracfg clocks, including early fixed factors, CPU muxes, infrastructure gates, and the infracfg reset controller.

Important APIs, types, and functions: `infra_early_divs` creates `clk13m`; `cpu_muxes` expose CA53 and CA72 CPU selectors; `infra_gates` covers debug, SMI, audio, GCE, M4U, CPUM, keypad, CEC, PMIC SPI, and PMIC wrapper gates. `clk_rst_desc` registers simple reset banks. The early `CLK_OF_DECLARE_DRIVER` path runs `mt8173_infracfg_init` before the platform driver.

Control flow: Early init allocates shared `infra_clk_data`, registers early factors, and publishes an OF provider so early consumers can resolve clocks. Later platform probe reuses or allocates the same data, registers gates and CPU muxes, refreshes the provider, and registers resets. Remove unregisters CPU muxes and gates.

State and persistence behavior: A global `infra_clk_data` pointer bridges early and platform phases. Hardware gate/mux/reset bits are volatile. Provider data persists for the device lifetime.

Dependencies and integration points: It depends on `of_clk_hw_onecell_get`, MediaTek factor/gate/cpumux/reset helpers, MT8173 bindings, and early boot clock users. It feeds CPU cluster, SMI/M4U, audio, GCE, PMIC wrapper, and reset consumers.

Risks and edge cases: The two-phase init must not double-allocate or leak clock data. Provider replacement/removal ordering matters. CPU mux registration is sensitive to parent order and may affect live CPU frequency paths.

Test signals: Early boot without deferred clock failures, CPU frequency/cluster mux operation, reset-controller consumers, infracfg gate toggling, and remove cleanup after early provider registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-infracfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-mm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-mm.c

Purpose: This provider registers MT8173 multimedia gates for display, SMI/LARB, MDP, DPI/DSI, mutex, and related MM blocks.

Important APIs, types, and functions: Two register banks `mm0_cg_regs` and `mm1_cg_regs` back `mt8173_mm_clks`. `mm_desc` is supplied by platform ID `clk-mt8173-mm`, and lifecycle is handled by `mtk_clk_pdev_probe/remove`.

Control flow: A parent device creates the platform device; pdev probe registers all MM gates from `mm_desc`. Display/media drivers consume the clocks through normal CCF lookup.

State and persistence behavior: Gate bits are volatile MM register state. Provider and gate handles are runtime-only and removed on pdev remove.

Dependencies and integration points: It depends on MT8173 clock IDs, common gate helpers, pdev clock helpers, topckgen MM parents, DRM/display, MDP, and memory/LARB consumers.

Risks and edge cases: Display clock gating must coordinate with power domains and memory ports. Wrong bank/shift values can disable unrelated multimedia blocks.

Test signals: Display bring-up, MDP operation, DSI/DPI paths, LARB/SMI enable ordering, clock summary during runtime PM, and pdev unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-pericfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-pericfg.c

Purpose: This driver registers MT8173 peripheral configuration clocks and resets for UART, I2C, PWM, SPI, MSDC, NFI, USB, and related peripheral buses.

Important APIs, types, and functions: `peri0_cg_regs` and `peri1_cg_regs` back `peri_gates`. `peri_clks` adds peripheral composites such as UART clock selection. `peri_desc` includes gates, composites, `mt8173_clk_lock`, and `clk_rst_desc`. It binds `mediatek,mt8173-pericfg`.

Control flow: `mtk_clk_simple_probe` registers gates, composites, and reset controller from the descriptor and publishes an OF provider. Consumers request clocks and resets using MT8173 binding IDs.

State and persistence behavior: Gate, mux, and reset states live in pericfg registers. Provider state is runtime-only. The spinlock protects shared composite register updates.

Dependencies and integration points: It depends on MediaTek gate/composite/reset helpers, DT bindings, and topckgen parents. It supports serial, I2C, SPI, PWM, MSDC, NAND, USB, and PMIC-related drivers.

Risks and edge cases: Peripheral boot dependencies make missing clocks obvious as deferred probes. Reset descriptor offsets must align with reset bindings. Composite parent order affects UART/peripheral baud generation.

Test signals: Probe serial/I2C/SPI/MSDC/USB devices, reset assertions through reset consumers, clk summary gate toggles, mux rate validation, and driver removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-pericfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-topckgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-topckgen.c

Purpose: This is the MT8173 top clock generator driver. It declares fixed clocks, fixed PLL dividers, and a large composite mux table for system, memory, media, storage, USB, audio, display, HDMI, and peripheral source clocks.

Important APIs, types, and functions: `TOP_MUX_GATE`/`TOP_MUX_GATE_NOSR` define gated mux composites; `fixed_clks`, `top_divs`, and `top_muxes` are grouped in `topck_desc` with `mt8173_top_clk_lock`. The driver binds `mediatek,mt8173-topckgen` through `mtk_clk_simple_probe/remove`.

Control flow: Probe registers fixed clocks/factors/composites from the descriptor, protects shared register updates with the top clock lock, and publishes the OF provider. Downstream subsystem clock drivers and device drivers select parents by binding ID.

State and persistence behavior: Clock parent/gate state is volatile topckgen register state. Provider data lives until driver removal. No state is written outside hardware registers.

Dependencies and integration points: It depends on MT8173 apmixedsys PLL names, common MediaTek mux/composite helpers, and MT8173 clock bindings. It feeds AXI/memory, MM/VDEC/VENC/MFG, camera, UART/SPI/MSDC, USB, audio, SCP, HDMI/HDCP, and RTC-related consumers.

Risks and edge cases: Parent arrays are long and hardware-encoded; wrong order causes subtle rate failures. Gate/no-set-rate flag usage matters for glitch-sensitive muxes. HDMI/display clocks are particularly sensitive to fixed dummy rates and parent naming.

Test signals: Full boot clock summary, display/HDMI/audio/storage/USB/video/GPU operation, mux parent switching where supported, suspend/resume, and module unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-topckgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-vdecsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-vdecsys.c

Purpose: This file registers MT8173 video decoder subsystem gates.

Important APIs, types, and functions: `vdec0_cg_regs` and `vdec1_cg_regs` define the VDEC gate banks; `GATE_VDEC` creates `vdec_clks`; `vdec_desc` is matched by `mediatek,mt8173-vdecsys`; the driver uses `mtk_clk_simple_probe/remove`.

Control flow: The platform driver maps the VDEC clock registers, registers VDEC gates, and provides them through OF. Codec drivers enable the gates around decode work.

State and persistence behavior: Gate state is hardware register state only. Provider metadata is runtime-only and removed on unbind.

Dependencies and integration points: It depends on MT8173 clock bindings, common gate helpers, topckgen VDEC parent clocks, media codec drivers, and power domains.

Risks and edge cases: Wrong bank selection or polarity can stop decoder clocks. VDEC operation also depends on power and memory clocks outside this file.

Test signals: Hardware decode, runtime PM enable/disable sequences, clk summary gate counts, suspend/resume, and bind/unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-vdecsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-vencsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-vencsys.c

Purpose: This driver registers MT8173 video encoder gates for both the main VENC system and the VENC-LT system.

Important APIs, types, and functions: `venc_cg_regs` backs both `venc_clks` and `venclt_clks` through `GATE_VENC`. `venc_desc` and `venc_lt_desc` are selected by `mediatek,mt8173-vencsys` and `mediatek,mt8173-vencltsys`.

Control flow: Simple probe selects the descriptor by compatible string and registers the relevant gate set. Consumers see separate providers for main encoder and lightweight encoder blocks.

State and persistence behavior: Gate enable bits are volatile hardware state. Provider registrations are runtime-only.

Dependencies and integration points: It depends on MT8173 clock IDs, common gate helpers, topckgen VENC parents, encoder drivers, and media power domains.

Risks and edge cases: The same register layout is reused for two compatible strings; wrong descriptor association would expose the wrong clock IDs. Encoder gates must be sequenced with power and memory paths.

Test signals: Main and VENC-LT node binding, hardware encode workloads, clock summary gate toggles, runtime PM, and provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-vencsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-apmixedsys.c

Purpose: This built-in driver registers MT8183 apmixedsys root PLLs plus 26 MHz gates for USB, APPLL, MIPI, modem, MMSYS, UFS, memory, and LVPLL-related consumers.

Important APIs, types, and functions: `apmixed_clks` uses `GATE_APMIXED` and one `CLK_IS_CRITICAL` APPLL 26M gate. `plls` defines ARM, CCI, main, universal, MFG, MSDC, TVD, MM, APLL1, and APLL2 PLLs with min/max, PCW, reset-bar, and divider-table data. `clk_mt8183_apmixed_probe` registers PLLs, gates, and an OF provider with rollback.

Control flow: As a `builtin_platform_driver`, it probes early for `mediatek,mt8183-apmixedsys`. It maps apmixedsys, allocates onecell data, registers PLLs, then low-frequency gates, and publishes the provider.

State and persistence behavior: PLL and gate state is volatile register state. Provider data is devm-allocated; no remove callback is used for normal unload. The critical gate is intended to remain enabled.

Dependencies and integration points: It depends on MT8183 bindings, `clk-pll.h`, `clk-gate.h`, and topckgen/main clock consumers that use PLL names and 26 MHz reference gates for USB, UFS, MIPI, display, modem, and audio.

Risks and edge cases: Root clock probe ordering is important. Incorrect PLL min/max/integer bit settings can break DVFS or rate changes. Critical gate flags must be preserved to avoid disabling required references.

Test signals: Early boot without clock-provider deferrals, PLL rates in clk summary, USB/UFS/MIPI/display/audio operation, critical gate enable state, and error-path rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-audio.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-audio.c

Purpose: This driver registers MT8183 audio subsystem gates and populates child audio platform devices below the audiosys node.

Important APIs, types, and functions: `audio0_cg_regs` and `audio1_cg_regs` describe two gate banks; `audio_clks` includes AFE, 22M/24M, APLL tuners, TDM, ADC/DAC, TML, I2S1-4, and ADDA6 ADC gates. `clk_mt8183_audio_probe` calls `mtk_clk_simple_probe` then `devm_of_platform_populate`; remove depopulates children and unregisters clocks.

Control flow: Probe registers the clock provider for `mediatek,mt8183-audiosys`; if child-device population fails, it removes the clock provider. Child audio devices then bind with the clocks available.

State and persistence behavior: Gate bits live in audiosys registers. Child platform devices and provider data exist for the driver lifetime. There is no disk persistence.

Dependencies and integration points: It depends on MT8183 clock bindings, common gate helpers, OF platform population, topckgen audio parents, and ASoC audio child drivers.

Risks and edge cases: Child population makes cleanup ordering important. Audio gate enable balance affects stream start/stop and suspend. APLL tuner parents must match topckgen audio-engine muxes.

Test signals: Audiosys child devices bind, playback/capture and TDM/I2S paths work, failure injection for child population removes clocks, clk summary gate toggling, and remove depopulates children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-cam.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-cam.c

Purpose: This file exposes MT8183 camera subsystem gates.

Important APIs, types, and functions: `cam_cg_regs` defines the camera gate register bank; `GATE_CAM` builds `cam_clks`; `cam_desc` is attached to `mediatek,mt8183-camsys`; probe/remove use MediaTek simple helpers.

Control flow: The OF platform driver registers camera gates and publishes them to camera sensor, ISP, SENINF, and memory-interface consumers.

State and persistence behavior: Gate state is volatile MMIO state. Provider state is runtime-only and removed on unbind.

Dependencies and integration points: It depends on MT8183 clock IDs, common gate helpers, topckgen camera parents, camera pipelines, power domains, and larb/IOMMU paths.

Risks and edge cases: Camera pipelines often need multiple gates and memory clocks; missing one gate can produce timeouts rather than obvious probe failure. Parent/gate bit accuracy is critical.

Test signals: Camera capture, SENINF/ISP probing, runtime PM gate transitions, suspend/resume, and clock provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-cam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-img.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-img.c

Purpose: This driver registers MT8183 image subsystem gates.

Important APIs, types, and functions: `img_cg_regs`, `GATE_IMG`, `img_clks`, and `img_desc` describe the image gate provider matched by `mediatek,mt8183-imgsys`.

Control flow: `mtk_clk_simple_probe` registers all image gates and publishes the OF provider. Image/ISP/MDP-related consumers enable gates through the common clock framework.

State and persistence behavior: The gate register bits are volatile; provider data is runtime-only.

Dependencies and integration points: It depends on MT8183 clock bindings, MediaTek gate helpers, top-level image parent clocks, and image processing consumers.

Risks and edge cases: Gate bits usually protect memory-facing image blocks, so bad gating can manifest as DMA/IOMMU faults. Runtime PM must keep gates balanced.

Test signals: Image pipeline operation, clk summary gate changes during use, suspend/resume, and driver unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu0.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu0.c

Purpose: This file registers MT8183 primary IPU core clock gates.

Important APIs, types, and functions: `ipu_core0_cg_regs` defines the register bank; `GATE_IPU_CORE0` creates `ipu_core0_clks`; `ipu_core0_desc` is selected by `mediatek,mt8183-ipu_core0`; lifecycle uses `mtk_clk_simple_probe/remove`.

Control flow: Probe maps the IPU core0 gate block, registers gates, and exposes them to IPU/NPU consumers.

State and persistence behavior: Gate state is volatile hardware state and provider data is runtime-only.

Dependencies and integration points: It depends on MT8183 clock bindings, common gate helpers, topckgen IPU parent clocks, IPU power domains, and AI/vision drivers.

Risks and edge cases: Core clock gates must be coordinated with IPU connection/bus gates and power domains. Wrong polarity or shift can leave the core inaccessible.

Test signals: IPU core0 probe/workload, runtime PM sequencing with `ipu_conn`, clk summary gate toggles, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu1.c

Purpose: This file registers MT8183 secondary IPU core clock gates.

Important APIs, types, and functions: `ipu_core1_cg_regs`, `GATE_IPU_CORE1`, `ipu_core1_clks`, and `ipu_core1_desc` describe the provider matched by `mediatek,mt8183-ipu_core1`.

Control flow: The common simple probe registers the core1 gate table and publishes an OF clock provider. IPU drivers enable the gates when scheduling work on the second core.

State and persistence behavior: Gate state is MMIO-backed and volatile. Provider metadata is removed on unbind.

Dependencies and integration points: It depends on MT8183 bindings, MediaTek gate helpers, IPU bus/connection clocks, power domains, and AI/vision consumers.

Risks and edge cases: Core1 depends on shared bus and connection gates; standalone enable may be insufficient. Register shift mistakes can affect the wrong IPU clock.

Test signals: IPU core1 workload, multi-core IPU use with `ipu0` and `ipu_conn`, runtime PM, clock summary transitions, and unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu_adl.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu_adl.c

Purpose: This driver exposes the MT8183 IPU ADL clock gate.

Important APIs, types, and functions: `ipu_adl_cg_regs` defines the ADL gate bank; `GATE_IPU_ADL_I` creates inverted gate entries in `ipu_adl_clks`; `ipu_adl_desc` is matched by `mediatek,mt8183-ipu_adl`.

Control flow: Simple probe registers the ADL gate provider for consumers in the IPU subsystem.

State and persistence behavior: State is limited to volatile gate bits and CCF provider metadata.

Dependencies and integration points: It depends on MT8183 clock bindings, inverted MediaTek gate ops, top-level IPU parents, and IPU data-link/accelerator consumers.

Risks and edge cases: The inverted gate operation is significant; normal polarity would reverse enable behavior. ADL also depends on broader IPU connection clocks.

Test signals: IPU ADL consumer probe, enable/disable behavior in clk summary, IPU workload involving ADL, and provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu_adl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu_conn.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu_conn.c

Purpose: This file registers MT8183 IPU connection and bus clock gates, including APB and several AXI gate banks that connect IPU cores to the rest of the SoC.

Important APIs, types, and functions: It defines five gate-register groups: `ipu_conn_cg_regs`, `ipu_conn_apb_cg_regs`, `ipu_conn_axi_cg_regs`, `ipu_conn_axi1_cg_regs`, and `ipu_conn_axi2_cg_regs`. `ipu_conn_clks` combines normal and inverted gates through `GATE_IPU_CONN*` macros. `ipu_conn_desc` is matched by `mediatek,mt8183-ipu_conn`.

Control flow: Simple probe registers all bus/connection gates and exposes them as one OF provider. IPU core and ADL drivers depend on these clocks for bus access.

State and persistence behavior: Gate state is volatile across IPU connection MMIO registers. Provider state exists only while the driver is bound.

Dependencies and integration points: It depends on MT8183 bindings, common gate helpers, topckgen IPU parents, IPU core drivers, power domains, and memory fabric/IOMMU paths.

Risks and edge cases: Multiple banks and inverted gates make bit/polarity errors likely. Bus gates must be enabled before core access, so sequencing bugs can cause bus faults.

Test signals: IPU subsystem probe order, IPU workloads, runtime PM with core0/core1/ADL, clk summary for APB/AXI gates, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-mfgcfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-mfgcfg.c

Purpose: This driver exposes MT8183 GPU/MFG clock gates.

Important APIs, types, and functions: `mfg_cg_regs` describes the MFG register bank; `GATE_MFG` creates `mfg_clks`; `mfg_desc` is matched by `mediatek,mt8183-mfgcfg`.

Control flow: Simple probe registers MFG gates and publishes an OF provider. GPU consumers enable the gates through CCF.

State and persistence behavior: Gate enable state is volatile hardware state; provider metadata is runtime-only.

Dependencies and integration points: It depends on MT8183 clock bindings, topckgen MFG muxes, MediaTek gate helpers, GPU drivers, and power-domain sequencing.

Risks and edge cases: The MFG mux has a notifier in `clk-mt8183.c`; this gate provider must interoperate with that parent-switching behavior. Power-domain ordering matters.

Test signals: GPU probe and rendering workload, MFG mux switching under load, runtime PM, clk summary gates, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-mfgcfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-mm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-mm.c

Purpose: This pdev driver registers MT8183 multimedia gates for display, SMI/LARB, MDP, mutex, DPI, DSI, and related blocks.

Important APIs, types, and functions: `mm0_cg_regs` and `mm1_cg_regs` back `mm_clks`; `mm_desc` is attached to platform ID `clk-mt8183-mm`; lifecycle uses `mtk_clk_pdev_probe/remove`.

Control flow: A parent platform device instantiates the MM clock device, pdev probe registers all gates, and display/media consumers use the registered clock IDs.

State and persistence behavior: Gate state is volatile MM register state. Provider state is runtime-only.

Dependencies and integration points: It depends on MT8183 bindings, pdev clock helpers, common gate ops, top-level MM parents, DRM/display, MDP, SMI/LARB, and power domains.

Risks and edge cases: Multimedia clocks are tightly coupled with power domains and memory ports. Bank/shift mistakes can break unrelated display blocks.

Test signals: Display and MDP operation, LARB clock sequencing, runtime PM, clock summary gate counts, and pdev unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-vdec.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-vdec.c

Purpose: This file registers MT8183 video decoder gates.

Important APIs, types, and functions: `vdec0_cg_regs` and `vdec1_cg_regs` define two inverted gate banks; `vdec_clks` is grouped into `vdec_desc`; the provider matches `mediatek,mt8183-vdecsys`.

Control flow: Simple probe registers VDEC gates and publishes them to media codec consumers.

State and persistence behavior: Gate bits are volatile hardware state. Provider metadata is runtime-only.

Dependencies and integration points: It depends on MT8183 clock bindings, inverted MediaTek gate ops, VDEC parent clocks from topckgen, codec drivers, power domains, and memory/LARB clocks.

Risks and edge cases: Inverted gates must not be converted to normal gates. Decode failures can result from missing companion power or memory clocks rather than this provider alone.

Test signals: Hardware decode, runtime PM, clock summary enable counts, suspend/resume, and provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-venc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-venc.c

Purpose: This driver registers MT8183 video encoder gates.

Important APIs, types, and functions: `venc_cg_regs` defines the gate bank; `GATE_VENC_I` creates inverted gate entries in `venc_clks`; `venc_desc` is matched by `mediatek,mt8183-vencsys`.

Control flow: Simple probe registers the VENC gate provider; encoder drivers enable gates while encoding.

State and persistence behavior: State is MMIO gate bits plus runtime provider metadata. Remove unregisters provider state.

Dependencies and integration points: It depends on MT8183 clock IDs, inverted gate helpers, top-level VENC parents, encoder drivers, and power domains.

Risks and edge cases: Gate polarity is inverted. Encoder clocks must be sequenced with media power and memory path clocks.

Test signals: Hardware encode, runtime PM enable/disable, clk summary gate state, suspend/resume, and unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183.c

Purpose: This is the main MT8183 topckgen, infracfg, pericfg, and mcucfg clock driver. It defines fixed clocks, PLL factors, top muxes, audio composites, infrastructure/peripheral gates, MCU muxes, reset controller data, and an MFG mux notifier.

Important APIs, types, and functions: `top_fixed_clks`, `top_divs`, `top_muxes`, `top_aud_comp`, `top_clks`, `infra_clks`, `peri_clks`, and `mcu_muxes` are grouped into `topck_desc`, `infra_desc`, `peri_desc`, and `mcu_desc`. `clk_rst_desc` exposes infracfg resets. `clk_mt8183_reg_mfg_mux_notifier` registers `struct mtk_mux_nb` for MFG parent switching. Compatible strings cover `mediatek,mt8183-infracfg`, `mediatek,mt8183-mcucfg`, `mediatek,mt8183-pericfg`, and `mediatek,mt8183-topckgen`.

Control flow: `mtk_clk_simple_probe` selects the descriptor, registers its factors/muxes/composites/gates/resets, and invokes the descriptor notifier hook for topckgen. The notifier temporarily switches the MFG mux to a safe parent around parent-rate changes.

State and persistence behavior: Clock selections, gates, and reset state are volatile hardware registers. Provider data is runtime-only. `mt8183_clk_lock` protects shared mux/composite registers.

Dependencies and integration points: It depends on MT8183 apmixedsys PLLs, common MediaTek clock/mux/gate/reset helpers, DT bindings, and consumers across CPU, infra, peri, display, camera, IPU, GPU, audio, storage, USB, UFS, SCP, security, and SPM domains.

Risks and edge cases: This is a central table file; parent-order and bit-field mistakes affect many devices. The MFG notifier is critical for safe GPU mux/rate changes. Critical or bus clocks should not be inadvertently gated.

Test signals: Full SoC boot, clk summary validation, GPU DVFS/mux changes, reset-controller users, storage/audio/display/camera/IPU/USB/UFS workloads, suspend/resume, and module removal where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-apmixedsys.c

Purpose: This driver registers MT8186 apmixedsys PLLs using PLLFH/FHCTL support for CPU, CCI, main, universal, storage, MM, NNA, ADSP, MFG, TVD, and audio PLLs.

Important APIs, types, and functions: `plls` defines `struct mtk_pll_data` with MT8186 min/max and integer-bit settings. `pllfhs` maps PLL IDs to FHCTL data. `clk_mt8186_apmixed_probe` maps MMIO, allocates `CLK_APMIXED_NR_CLK`, parses optional `mediatek,mt8186-fhctl`, registers PLLFH clocks with `mtk_clk_register_pllfhs`, and publishes an OF provider. Remove unregisters provider and PLLFH clocks.

Control flow: The platform driver binds `mediatek,mt8186-apmixedsys`; probe prepares all root PLLs before topckgen and subsystem consumers rely on them. Error paths unregister PLLFH state if provider publication fails.

State and persistence behavior: PLL and FH state is hardware register state; provider data is volatile. No persistent storage is used.

Dependencies and integration points: It depends on `clk-fhctl.h`, `clk-pllfh.h`, `clk-pll.h`, MT8186 bindings, optional FHCTL DT, and root consumers in topckgen, CPU, AI, ADSP, display, storage, video, and audio domains.

Risks and edge cases: FHCTL tables must align with PLL hardware IDs and offsets. Missing or malformed FHCTL node should not prevent basic PLL registration. Root clock errors cascade into many subsystem probe failures.

Test signals: Boot with FHCTL present/absent, validate PLL rates and frequency hopping registration, CPU/AI/ADSP/display/storage workloads, error-path cleanup, and remove/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-cam.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-cam.c

Purpose: This driver registers MT8186 camera clock gates for the main camera system and two raw camera subsystems.

Important APIs, types, and functions: `cam_cg_regs` backs `cam_clks`, `cam_rawa_clks`, and `cam_rawb_clks`. Three descriptors, `cam_desc`, `cam_rawa_desc`, and `cam_rawb_desc`, are selected by compatibles `mediatek,mt8186-camsys`, `mediatek,mt8186-camsys_rawa`, and `mediatek,mt8186-camsys_rawb`.

Control flow: Simple probe registers the descriptor selected by OF match data. Each camera node exposes its own gate set to camera pipeline consumers.

State and persistence behavior: Gate bits are volatile camera subsystem registers. Provider state is runtime-only.

Dependencies and integration points: It depends on MT8186 clock IDs, common MediaTek gate helpers, topckgen camera parents, camera drivers, raw sensor paths, power domains, and memory/LARB clocks.

Risks and edge cases: Multiple compatibles share one register layout but expose different IDs; descriptor routing must be correct. Camera pipelines depend on many clocks and power domains, so partial enablement can produce capture timeouts.

Test signals: Main and raw camera node binding, capture on RAWA/RAWB paths, runtime PM gate toggling, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-cam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-img.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-img.c

Purpose: This provider registers MT8186 image subsystem clocks for imgsys1 and imgsys2.

Important APIs, types, and functions: `img_cg_regs` backs both `img1_clks` and `img2_clks`; `img1_desc` and `img2_desc` are selected by `mediatek,mt8186-imgsys1` and `mediatek,mt8186-imgsys2`.

Control flow: Simple probe picks the descriptor by compatible string, registers the image gates, and publishes the provider for image/ISP consumers.

State and persistence behavior: Gate state is volatile MMIO state; provider data is runtime-only.

Dependencies and integration points: It depends on MT8186 bindings, common gate helpers, top-level image parents, image processing drivers, power domains, and memory fabric clocks.

Risks and edge cases: Two image subsystems share code but have distinct clock IDs. A descriptor mismatch can expose the wrong clocks to a DT node.

Test signals: Both imgsys nodes bind, image processing workloads run on both domains, clk summary gate toggling, runtime PM, and unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-imp_iic_wrap.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-imp_iic_wrap.c

Purpose: This driver exposes MT8186 I2C wrapper clock gates.

Important APIs, types, and functions: `imp_iic_wrap_cg_regs` defines the gate bank; `GATE_IMP_IIC_WRAP` populates `imp_iic_wrap_clks`; `imp_iic_wrap_desc` is matched by `mediatek,mt8186-imp_iic_wrap`.

Control flow: Simple probe registers wrapper gates and publishes them for I2C wrapper consumers.

State and persistence behavior: Gate state is volatile hardware state; provider metadata is runtime-only.

Dependencies and integration points: It depends on MT8186 clock bindings, common gate helpers, topckgen I2C/AXI parents, and I2C controller/wrapper drivers.

Risks and edge cases: I2C wrapper gates affect multiple buses; a wrong gate bit can break peripheral discovery. Runtime PM ordering with infracfg clocks matters.

Test signals: Probe all I2C buses behind the wrapper, transfer traffic, observe gate enable counts, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-imp_iic_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-infra_ao.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-infra_ao.c

Purpose: This is the MT8186 always-on infrastructure clock and reset provider. It exposes many gates for PMIC, SCP, security, timers, USB, I2C, PWM, UART, DMA, SPI, MSDC, DVFS, debug, audio, modem interfaces, ADSP, flash, and related AO services.

Important APIs, types, and functions: Four gate banks `infra_ao0` through `infra_ao3` are described by `infra_ao*_cg_regs` and `GATE_INFRA_AO*` macros, with selected `CLK_IS_CRITICAL` gates. `infra_ao_rst_desc` uses MTK set/clear reset support and reset maps from `mt8186-resets.h`. `infra_ao_desc` includes gates and reset descriptor and binds `mediatek,mt8186-infracfg_ao`.

Control flow: Simple probe registers all AO gates, registers the reset controller from the descriptor, and exposes the OF provider. Consumers across many buses use these clocks during normal boot and low-power transitions.

State and persistence behavior: Gate and reset state is volatile AO register state, but many clocks are always-on in practice. Provider data is runtime-only.

Dependencies and integration points: It depends on MT8186 clock and reset bindings, common MediaTek gate/reset helpers, topckgen parents, and most peripheral/infra consumers.

Risks and edge cases: This file controls critical infrastructure clocks; accidentally gating critical SCP/SSPM/security/timer clocks can hang the system. The visible stray space before one macro definition is stylistic but compile-safe. Reset mapping must match hardware bank numbering.

Test signals: Full platform boot, UART/I2C/SPI/MSDC/USB/audio/security/modem-interface operation, reset-controller consumers, suspend/resume, critical gates remaining enabled, and clk summary inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-infra_ao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-ipe.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-ipe.c

Purpose: This driver registers MT8186 image processing engine gates.

Important APIs, types, and functions: `ipe_cg_regs` describes the IPE gate bank; `GATE_IPE` creates `ipe_clks`; `ipe_desc` is selected by `mediatek,mt8186-ipesys`.

Control flow: Simple probe registers the IPE gate provider for image-processing consumers.

State and persistence behavior: Gate state is volatile MMIO state; provider data is runtime-only.

Dependencies and integration points: It depends on MT8186 clock IDs, common gate helpers, top-level IPE/ISP parents, image processing drivers, power domains, and memory/LARB clocks.

Risks and edge cases: IPE operation depends on companion image and memory clocks; isolated gate enable is not enough. Bit-offset errors can cause image workload timeouts.

Test signals: IPE workload execution, runtime PM gate toggles, clk summary inspection, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-ipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mcu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mcu.c

Purpose: This file registers MT8186 mcusys CPU/bus mux composites for little, big, and bus clock domains.

Important APIs, types, and functions: Parent arrays select among `clk26m`, ARM PLLs, `mainpll`, and `univpll` divided parents. `mcu_muxes` defines composite muxes, and `mcu_desc` exposes them through `mediatek,mt8186-mcusys`.

Control flow: Simple probe registers the MCU mux composites and publishes a clock provider. CPU frequency and bus-clock users can then switch parents through CCF.

State and persistence behavior: Mux state is volatile mcusys register state. Provider metadata is runtime-only.

Dependencies and integration points: It depends on MT8186 bindings, MediaTek composite helpers, apmixedsys PLL parents, topckgen divided parents, CPU/cluster clock consumers, and DVFS.

Risks and edge cases: CPU mux parent order and safe switching are critical. Bad mux fields can destabilize CPU clocks. This file does not register a custom notifier, so safe switching must be handled by common mux/composite behavior and consumers.

Test signals: CPU frequency scaling, bus-clock changes, clk summary parent changes, stress workloads during DVFS, suspend/resume, and provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mdp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mdp.c

Purpose: This driver registers MT8186 Multimedia Data Path gates.

Important APIs, types, and functions: `mdp0_cg_regs` and `mdp2_cg_regs` define two gate banks; `GATE_MDP0` and `GATE_MDP2` populate `mdp_clks`; `mdp_desc` is selected by `mediatek,mt8186-mdpsys`.

Control flow: Simple probe registers MDP gates and publishes a provider for display/media data-path consumers.

State and persistence behavior: Gate state is volatile register state. Provider metadata exists only while bound.

Dependencies and integration points: It depends on MT8186 clock IDs, common gate helpers, top-level MDP parents, MDP/display drivers, power domains, and memory/LARB clocks.

Risks and edge cases: MDP paths require coordinated display, MM, and memory clocks. Wrong gate bank selection causes pipeline stalls or DMA faults.

Test signals: MDP blit/resize/composition workloads, display pipeline use, runtime PM, clock summary transitions, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mfg.c

Purpose: This file exposes MT8186 GPU/MFG subsystem gate clocks.

Important APIs, types, and functions: `mfg_cg_regs` defines the MFG gate bank; `GATE_MFG` creates `mfg_clks`; `mfg_desc` is matched by `mediatek,mt8186-mfgsys`.

Control flow: Simple probe registers MFG gates and publishes them to GPU consumers.

State and persistence behavior: Gate state is volatile register state; provider metadata is runtime-only.

Dependencies and integration points: It depends on MT8186 bindings, common gate helpers, topckgen MFG muxes, GPU drivers, power domains, and the topckgen MFG mux notifier.

Risks and edge cases: GPU clocking depends on parent switching and power sequencing. Gate mistakes can hang GPU accesses.

Test signals: GPU probe/render workloads, runtime PM, MFG mux parent changes, clk summary gates, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mm.c

Purpose: This pdev driver registers MT8186 multimedia/display gates.

Important APIs, types, and functions: `mm0_cg_regs` and `mm1_cg_regs` back `mm_clks`; `mm_desc` is associated with platform ID `clk-mt8186-mm`; lifecycle uses `mtk_clk_pdev_probe/remove`.

Control flow: A parent device instantiates the pdev, pdev probe registers all MM gate clocks, and media/display consumers use them by binding ID.

State and persistence behavior: Gate bits are volatile MM registers. Provider state is runtime-only.

Dependencies and integration points: It depends on MT8186 clock IDs, pdev clock helpers, common gate ops, top-level display/MM parents, DRM/display, MDP, SMI/LARB, and power domains.

Risks and edge cases: Multimedia clock gating requires power-domain coordination. Wrong bank/shift values can disable display-critical clocks.

Test signals: Display pipeline, MDP/MM consumers, LARB access, runtime PM, clk summary gate counts, and pdev removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-topckgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-topckgen.c

Purpose: This is the MT8186 top clock generator driver. It registers fixed clocks, PLL-derived factors, many top-level muxes, audio I2S/APLL composites, and an MFG mux notifier.

Important APIs, types, and functions: `top_fixed_clks`, `top_divs`, `top_mtk_muxes`, and `top_muxes` are grouped into `topck_desc` with `mt8186_clk_lock`. Parent arrays cover AXI, SCP, MFG, camera timers, UART/SPI/MSDC/audio/display/USB/security/VENC/ISP/VDEC/MDP/UFS/ADSP/NNA/WPE/DPI/SPMI/SPINOR domains. `clk_mt8186_reg_mfg_mux_notifier` registers a `struct mtk_mux_nb` for safe MFG parent switching.

Control flow: Simple probe selects `topck_desc` for `mediatek,mt8186-topckgen`, registers factors/muxes/composites, installs the MFG notifier, and publishes the OF provider. Consumers select parents and rates through CCF.

State and persistence behavior: Mux, divider, and composite state is volatile topckgen register state. The spinlock serializes shared updates; notifier state is devm-managed.

Dependencies and integration points: It depends on MT8186 apmixedsys PLLs, MediaTek mux/composite helpers, clock bindings, and nearly every subsystem clock consumer including CPU/GPU, camera, display, MDP, video, audio, UFS, USB, ADSP, NNA, and WPE.

Risks and edge cases: Parent-order mistakes or mux field errors have broad impact. MFG notifier behavior is critical for GPU rate changes. Many muxes use update bits and shared registers, so locking and register layout are important.

Test signals: Full boot clock summary, GPU DVFS, audio/display/camera/video/MDP/UFS/USB/ADSP/NNA/WPE workloads, mux parent changes, suspend/resume, and provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-topckgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-vdec.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-vdec.c

Purpose: This driver registers MT8186 video decoder gates across four VDEC gate banks.

Important APIs, types, and functions: `vdec0_cg_regs` through `vdec3_cg_regs` define register banks; `GATE_VDEC0` through `GATE_VDEC3` populate `vdec_clks`; `vdec_desc` is matched by `mediatek,mt8186-vdecsys`.

Control flow: Simple probe registers all VDEC gate clocks and publishes the OF provider for codec consumers.

State and persistence behavior: Gate enable state is volatile hardware state. Provider metadata is runtime-only.

Dependencies and integration points: It depends on MT8186 bindings, common gate helpers, top-level VDEC parents, video decoder drivers, power domains, and memory/LARB clocks.

Risks and edge cases: Four banks increase the risk of register/shift mismatch. Decode requires coordinated memory and power clocks outside this file.

Test signals: Hardware decode, all VDEC sub-block gate enables in clk summary, runtime PM, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-venc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-venc.c

Purpose: This file registers MT8186 video encoder gate clocks.

Important APIs, types, and functions: `venc_cg_regs` defines the gate bank; `GATE_VENC` creates `venc_clks`; `venc_desc` is matched by `mediatek,mt8186-vencsys`.

Control flow: Simple probe registers the VENC gates and publishes a clock provider for encoder consumers.

State and persistence behavior: Gate state is volatile MMIO state; provider state is runtime-only.

Dependencies and integration points: It depends on MT8186 clock bindings, common gate helpers, top-level VENC parents, encoder drivers, and power domains.

Risks and edge cases: Encoder operation also depends on MM/MDP and memory clocks. Gate bit mistakes can manifest as encode timeouts.

Test signals: Hardware encode, runtime PM gate transitions, clk summary inspection, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-wpe.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-wpe.c

Purpose: This provider registers MT8186 Warp Engine clock gates.

Important APIs, types, and functions: `wpe_cg_regs` defines the gate bank; `GATE_WPE` creates `wpe_clks`; `wpe_desc` is selected by `mediatek,mt8186-wpesys`.

Control flow: Simple probe registers WPE gates and publishes them to warp/image-processing consumers.

State and persistence behavior: Gate state is volatile hardware state; provider data is runtime-only.

Dependencies and integration points: It depends on MT8186 clock IDs, common gate helpers, top-level WPE parents, image/warp engine drivers, power domains, and memory clocks.

Risks and edge cases: WPE clocking depends on MDP/image and memory paths. A wrong parent or gate bit can produce pipeline stalls.

Test signals: WPE workload execution, runtime PM enable/disable, clk summary gate counts, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-wpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-adsp_audio26m.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-adsp_audio26m.c

Purpose: This file registers the MT8188 ADSP audio 26 MHz gate provider.

Important APIs, types, and functions: `adsp_audio26m_cg_regs` describes the gate register; `GATE_ADSP_FLAGS` creates `adsp_audio26m_clks`; `adsp_audio26m_desc` is matched by `mediatek,mt8188-adsp-audio26m`; lifecycle uses `mtk_clk_simple_probe/remove`.

Control flow: Probe registers the ADSP audio 26 MHz gate and exposes it to ADSP/audio consumers through OF.

State and persistence behavior: Gate state is volatile hardware register state. Provider state is runtime-only.

Dependencies and integration points: It depends on MT8188 clock bindings, MediaTek gate helpers, a `clk26m` parent, and ADSP/audio firmware or driver consumers.

Risks and edge cases: This is a small reference-clock provider; disabling it at the wrong time can stall ADSP audio firmware. Gate polarity and parent naming are the main correctness risks.

Test signals: ADSP audio probe/firmware boot, audio playback through ADSP path, clk summary gate state, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-adsp_audio26m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-apmixedsys.c

Purpose: This driver registers MT8188 apmixedsys root PLLs and a small PLL 26 MHz gate, providing root clocks for Ethernet, storage, display, multimedia, image, universal, ADSP, audio, and GPU domains.

Important APIs, types, and functions: `apmixed_clks` exposes `pll_ssusb26m_en`. `plls` defines ETHPLL, MSDCPLL, TVDPLL1/2, MMPLL, MAINPLL, IMGPLL, UNIVPLL, ADSPPLL, APLL1-5, and MFGPLL with MT8188 min/max, PCW, reset-bar, and fixed-post-divider data. `clk_mt8188_apmixed_probe` allocates `CLK_APMIXED_NR_CLK`, registers PLLs, registers gates, and adds an OF provider. Remove unregisters provider, gates, and PLLs.

Control flow: On `mediatek,mt8188-apmixedsys` probe, the driver maps apmixedsys registers, registers all PLLs first, adds the gate table, and exposes the clock provider. Error paths roll back gates and PLLs in reverse order.

State and persistence behavior: PLL programming and gate state live in volatile apmixedsys registers. Provider state is runtime-only and cleaned up on remove.

Dependencies and integration points: It depends on MT8188 clock bindings, `clk-pll.h`, `clk-gate.h`, common MediaTek registration helpers, and consumers in topckgen/subsystem drivers for Ethernet, USB, display, image, ADSP, audio, storage, and GPU clocks.

Risks and edge cases: Root PLL register definitions must match hardware exactly; mistakes propagate to many rates. Several PLLs use reset-bar and post-divider fields. Provider publication failure must clean up both gates and PLLs.

Test signals: Boot root clock registration, clk summary PLL rates, USB 26 MHz gate, Ethernet/storage/display/audio/GPU/ADSP workloads, error-path cleanup, and module unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-apmixedsys.c -->
