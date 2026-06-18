# Research: subset-b-006528

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-mt6359-rt1015-rt5682.c -->
## sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-mt6359-rt1015-rt5682.c

### Purpose
This file is the MT8192 ASoC machine driver for boards combining the MT8192 AFE, MT6359 codec, RT1015 or RT1015P speaker path, and RT5682 or RT5682S headset codec. It binds a platform sound card through `mtk_soundcard_common_probe`, publishes frontend and backend DAI links, wires board-specific DAPM widgets/routes/controls, and handles jack registration plus codec-specific clock programming.

### Important APIs, Types, and Functions
The exported module surface is the `platform_driver` named `mt8192_mt6359`, with OF matches for `mediatek,mt8192_mt6359_rt1015_rt5682`, `mediatek,mt8192_mt6359_rt1015p_rt5682`, and `mediatek,mt8192_mt6359_rt1015p_rt5682s`. The main data objects are two `snd_soc_card` definitions, `mt8192_mt6359_rt1015_rt5682_card` and `mt8192_mt6359_rt1015p_rt5682x_card`, both sharing `mt8192_mt6359_dai_links`.

Key callbacks include `mt8192_rt1015_i2s_hw_params()` for RT1015 PLL/sysclk setup, `mt8192_rt5682x_i2s_hw_params()` for RT5682 TDM slot and PLL/sysclk setup, `mt8192_mt6359_init()` for MTKAIF protocol setup and calibration, `mt8192_rt5682_init()` for I2S8/I2S9 clock sharing and headset jack setup, `mt8192_mt6359_hdmi_init()` for HDMI jack setup, `mt8192_i2s_hw_params_fixup()` for forcing BE I2S format to `S24_LE`, and `mt8192_mt6359_soc_card_probe()` for card-specific probe adjustments.

### Control Flow
At module load, the platform driver registers with the common MediaTek sound-card probe. OF match data selects one of three `mtk_soundcard_pdata` structures, each pointing to the matching card definition, jack count, PCM constraints, and `soc_probe`. During probe, legacy DTs are optionally parsed by `mt8192_mt6359_legacy_probe()`: it resolves `mediatek,hdmi-codec`, `speaker-codecs`, and `headset-codec`, rewrites relevant BE codec components for `I2S3`, `I2S8`, `I2S9`, enables TDM if HDMI exists, and attaches RT1015 ops when the codec DAI name matches `rt1015-aif`.

Runtime PCM setup flows through DPCM links. FE links expose playback/capture endpoints such as `Playback_1`, `Capture_1`, and `Playback_HDMI`; BE links bind hardware DAIs such as `Primary Codec`, `ADDA_CH34`, `I2S0` through `I2S9`, `PCM 1`, `PCM 2`, `CONNSYS_I2S`, and `TDM`. BE hw-param fixups normalize I2S sample format, and codec-specific ops program PLL/sysclk on RT1015 or RT5682 paths.

The MTKAIF calibration path in `mt8192_mt6359_mtkaif_calibration()` powers the AFE runtime, requests ADDA GPIOs, enables codec calibration mode, selects protocol/test mode with `regmap_update_bits()`, sweeps phases 0..42, polls `CKSYS_AUD_TOP_MON` until three channel monitors complete, records the previous cycle before a transition as the chosen phase, programs the codec with the chosen phases, then disables FIFO/calibration/GPIOs and drops runtime PM.

### State and Persistence
State is mostly kernel runtime state, not persistent storage. Card state lives in static `snd_soc_card`, `snd_soc_dai_link`, DAPM widget/route/control, codec-conf, and pdata structures. Per-device mutable state is held in `mt8192_afe_private`, notably `mtkaif_protocol`, `mtkaif_calibration_num_phase`, `mtkaif_chosen_phase[]`, and `mtkaif_phase_cycle[]`. Jack state is stored in the common card data `jacks[]` array. Runtime PM state is acquired during calibration and released before returning.

### Dependencies and Integration Points
This driver depends on ALSA SoC core APIs, MediaTek common AFE/soundcard helpers, MT8192 AFE clock/GPIO/common definitions, MT6359 codec helpers, and RT1015/RT5682 codec DAI controls. DT integration is central: compatible strings select pdata, child codec nodes fill BE links in legacy mode, and optional HDMI controls whether TDM is ignored. The DAI names used here must match the MT8192 AFE platform driver and codec drivers.

### Risks
The calibration loop polls up to 10000 iterations without sleeping; incorrect clock/GPIO/power sequencing can return bad phases or waste CPU during probe. `mt8192_mt6359_mtkaif_calibration()` always returns 0 even after `mtkaif_calib_ok` becomes false, so failures are logged but may not fail card probe. Legacy DT rewriting assumes codec child nodes and DAI names are consistent; missing nodes fail probe except HDMI. BE link sharing for I2S8/I2S9 must match the AFE implementation or headset clocks may be wrong.

### Test Signals
Useful validation includes successful platform probe for all three compatible strings, ALSA card enumeration with all FE/BE links, headset jack button reporting for play/pause, voice command, volume up, and volume down, HDMI jack creation when `mediatek,hdmi-codec` is present, playback through RT1015/RT1015P and headset paths at constrained rates, capture at listed capture rates/channels, clean suspend poweroff and restore resume, and dmesg absence of `failed to set pll`, `failed to set sysclk`, `test fail`, or DAI-link codec parse errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-mt6359-rt1015-rt5682.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-reg.h -->
## sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-reg.h

### Purpose
This header is the MT8192 AFE register map and bitfield definition layer. It provides symbolic register offsets, shifts, masks, shifted masks, and small register-value enums used by the MT8192 platform, DAI, clock, memory-interface, IRQ, ASRC, MTKAIF, TDM, HDMI, and security code.

### Important APIs, Types, and Definitions
The only C type is the anonymous enum defining `MT8192_MEMIF_PBUF_SIZE_*` values. The rest of the file is preprocessor definitions. Important groups include top-level enable and monitor bits for `AFE_DAC_CON0` and `AFE_DAC_MON`; I2S control fields for `AFE_I2S_CON`, `AFE_I2S_CON1` through `AFE_I2S_CON9`, and `AFE_CONNSYS_I2S_CON`; PCM fields for `PCM_INTF_CON1`, `PCM_INTF_CON2`, and `PCM2_INTF_CON`; ADDA and MTKAIF fields for `AFE_ADDA_*`, `AFE_AUD_PAD_TOP`, `AFE_ADDA_MTKAIF_*`, and `AFE_ADDA6_MTKAIF_*`; memif control fields for DL, VUL, AWB, DAI, MOD_DAI, HDMI, and pbuf format registers; IRQ control/count/status fields for `AFE_IRQ_MCU_*`; ASRC and sinegen fields; and security mask register offsets.

The register-offset section maps symbolic names such as `AFE_DAC_CON0`, `AFE_CONN*`, `AFE_DL*_BASE`, `AFE_VUL*_CUR`, `AFE_IRQ_MCU_CON*`, `AFE_APLL*_TUNER_CFG`, `AFE_TDM_CON*`, `GENERAL_ASRC_*`, and `AFE_SECURE_MASK_*` to byte offsets. `AFE_MAX_REGISTER` is set to `AFE_SECURE_MASK_TINY_CONN7`, and `AFE_IRQ_STATUS_BITS`, `AFE_IRQ_CNT_SHIFT`, and `AFE_IRQ_CNT_MASK` summarize IRQ status/count handling.

### Control Flow
There is no executable control flow. Consumers use these definitions in `regmap_update_bits()`, `regmap_read()`, regmap range/default tables, DAI configuration helpers, interrupt handlers, and PCM/memif setup paths. The naming convention usually provides a raw shift, unshifted mask, and pre-shifted mask, letting callers either compose values manually or use update helpers with explicit masks.

### State and Persistence
This file owns no runtime state. It defines the layout of hardware state in the AFE register block. Runtime state persists only in the hardware registers accessed by other driver files, for example enable bits in `AFE_DAC_CON0`, buffer addresses/cursors for memifs, IRQ counters and clears, MTKAIF protocol/delay/fifo controls, and secure-domain masks.

### Dependencies and Integration Points
The header is included by MT8192 AFE implementation files that need stable names for hardware registers. It must agree with the SoC datasheet, the regmap maximum register, and any debugfs/regcache/default-register tables. It also underpins machine-driver calibration code that touches `AFE_AUD_PAD_TOP` and MTKAIF registers, and PCM/DAI code that configures I2S, PCM, TDM, HDMI, ASRC, and memif paths.

### Risks
The main risks are silent hardware misconfiguration from incorrect offsets, shifts, or masks. Because many names are repeated across similar I2S or memif blocks, copy/paste mistakes can be hard to detect at compile time. Some generic macro names, such as `INV_LRCK_SFT`, appear in multiple register sections and could collide semantically if used without register context. A wrong `AFE_MAX_REGISTER` may make regmap reject valid accesses or allow invalid ones. IRQ masks and clear bits are especially sensitive because stale interrupts can cause underruns or missed period notifications.

### Test Signals
Compile coverage catches missing macro names but not most numeric mistakes. Runtime signals include successful probe with no regmap range errors, working playback and capture on every memif/DAI using these offsets, stable interrupt delivery and period elapsed callbacks, correct I2S/PCM/TDM clock and format behavior across sample rates, successful MTKAIF calibration, no unexpected secure access faults, and register dumps matching expected bit transitions during stream start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/Makefile -->
## sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/Makefile

### Purpose
This Makefile wires the MT8195 ALSA SoC platform and machine drivers into the kernel build. It defines the objects that make up the MT8195 AFE platform module and conditionally builds the MT8195 MT6359 machine driver.

### Important APIs, Types, and Build Targets
The composite object `snd-soc-mt8195-afe-y` consists of `mt8195-audsys-clk.o`, `mt8195-afe-clk.o`, `mt8195-afe-pcm.o`, `mt8195-dai-adda.o`, `mt8195-dai-etdm.o`, and `mt8195-dai-pcm.o`. `obj-$(CONFIG_SND_SOC_MT8195)` includes `snd-soc-mt8195-afe.o`, while `obj-$(CONFIG_SND_SOC_MT8195_MT6359)` includes `mt8195-mt6359.o`.

### Control Flow
There is no runtime control flow. Build control flow is Kbuild-driven: enabling `CONFIG_SND_SOC_MT8195` compiles and links the platform driver aggregate, and enabling `CONFIG_SND_SOC_MT8195_MT6359` compiles the machine driver. The order in `snd-soc-mt8195-afe-y` determines the link order inside the aggregate object but not probe order, which remains platform/driver-core controlled.

### State and Persistence
The file has no runtime state. Its persistent effect is the kernel build graph: object inclusion controls whether MT8195 AFE and machine-driver code is present in the built kernel or module.

### Dependencies and Integration Points
This file integrates the MT8195 source directory with the parent ALSA SoC Kbuild tree and Kconfig symbols. The platform object depends on the clock, PCM, ADDA, ETDM, and PCM DAI sources all building together. The machine driver is separately gated so board support can be included only when the MT6359 card driver is selected.

### Risks
Omitting an object from `snd-soc-mt8195-afe-y` can produce unresolved symbols or missing DAI registration at runtime. Adding a new DAI/source file without updating this Makefile leaves code unbuilt. Misaligned Kconfig dependencies can compile the machine driver without the platform support it expects or omit the machine driver on boards that require it.

### Test Signals
Build tests should cover `CONFIG_SND_SOC_MT8195=y/m` and `CONFIG_SND_SOC_MT8195_MT6359=y/m`. Useful signals are clean compile/link output, presence of `snd-soc-mt8195-afe` symbols or module, successful registration of ADDA/ETDM/PCM DAIs, and MT8195 MT6359 machine-driver probe when the machine config is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-clk.c -->
## sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-clk.c

### Purpose
This file implements MT8195 AFE clock acquisition, generic clock helpers, APLL tuner setup, register-access clock sequencing, main AFE clock sequencing, and top clock-gate control. It is the clock-control backend used by MT8195 PCM and DAI drivers.

### Important APIs, Types, and Functions
The public functions are `mt8195_afe_get_mclk_source_clk_id()`, `mt8195_afe_get_mclk_source_rate()`, `mt8195_afe_get_default_mclk_source_by_rate()`, `mt8195_afe_init_clock()`, `mt8195_afe_enable_clk()`, `mt8195_afe_disable_clk()`, `mt8195_afe_prepare_clk()`, `mt8195_afe_unprepare_clk()`, `mt8195_afe_enable_clk_atomic()`, `mt8195_afe_disable_clk_atomic()`, `mt8195_afe_set_clk_rate()`, `mt8195_afe_set_clk_parent()`, `mt8195_afe_enable_main_clock()`, `mt8195_afe_disable_main_clock()`, `mt8195_afe_enable_reg_rw_clk()`, and `mt8195_afe_disable_reg_rw_clk()`. Only `mt8195_afe_enable_clk()` and `mt8195_afe_disable_clk()` are explicitly exported with `EXPORT_SYMBOL_GPL`.

The main private data type is `struct mt8195_afe_tuner_cfg`, which stores tuner register addresses, shifts, masks, defaults, a spinlock, and a reference count for each audio PLL tuner. The `aud_clks[]` table maps `enum MT8195_CLK_*` IDs to DT/CCF clock names.

### Control Flow
`mt8195_afe_init_clock()` registers audsys clocks, allocates `afe_priv->clk`, resolves every clock name with `devm_clk_get()`, and initializes the five tuner configs. MCLK helpers map user-facing MCK selections to clock IDs and choose APLL1 for 8 kHz-family rates and APLL2 otherwise.

Generic clock wrappers guard NULL clock pointers, call CCF APIs, and return/log errors. Non-atomic helpers use `clk_prepare_enable()` or `clk_disable_unprepare()`, while atomic helpers use `clk_enable()` or `clk_disable()` for contexts where preparation is already handled.

APLL tuner enable first writes default divider/reference/upper-bound values, enables tuner-related clocks for PLL1 or PLL2, then increments the tuner refcount under `ctrl_lock` and sets the tuner enable bit only on the first user. Disable decrements under the same lock, clears the tuner enable bit at zero, clamps negative counts back to zero, and disables the tuner clocks.

`mt8195_afe_enable_reg_rw_clk()` enables the infra, bus, 26 MHz, AFE, and A1SYS clocks needed for register access. Its disable counterpart turns them off in reverse order. `mt8195_afe_enable_main_clock()` enables timing-system clocks, sets top CG bits, turns on `AFE_DAC_CON0` bit 0, and enables APLL1/APLL2 tuners. Disable runs the reverse sequence.

### State and Persistence
Mutable state lives in `mt8195_afe_private->clk` and in the static tuner config array. Tuner `ref_cnt` and `ctrl_lock` manage shared use across stream paths. Hardware state is persisted in clock framework enables and AFE registers such as APLL tuner config registers, `ASYS_TOP_CON`, and `AFE_DAC_CON0`. The file does not store state on disk.

### Dependencies and Integration Points
The file depends on Linux CCF (`clk_*`), regmap, `mt8195-afe-common.h`, `mt8195-afe-clk.h`, `mt8195-reg.h`, and `mt8195-audsys-clk.h`. It is called from the MT8195 PCM runtime PM paths, ADDA/ETDM/PCM DAI setup, and machine-driver MCLK configuration. Clock names in `aud_clks[]` must match the SoC clock providers and device tree.

### Risks
Several loops ignore return values from individual enable/disable calls, so partial clock failures can be hidden in aggregate sequencing. APLL tuner disable decrements before checking underflow and always disables tuner clocks even if the refcount was already zero, which can unbalance CCF enables if callers mismatch enable/disable. `get_top_cg_*()` returns zero for invalid types, leading to harmless-looking writes to register 0 with mask 0, but invalid callers would not receive an error. Missing DT clocks fail probe during init.

### Test Signals
Validation should include probe with every clock resolved, runtime resume/suspend cycling with no unbalanced clock warnings, stream start/stop across ADDA, ETDM, PCM, HDMI/DPTX, and memif paths, sample-rate changes that select APLL1 vs APLL2 correctly, debug register checks showing AFE on/timing CG/tuner bits set and cleared, and fault injection for missing clocks or failed `clk_set_parent()`/`clk_set_rate()` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-clk.h -->
## sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-clk.h

### Purpose
This header defines the MT8195 AFE clock ID namespace and declares the clock-control functions implemented by `mt8195-afe-clk.c`. It is the common interface used by MT8195 PCM, DAI, and machine-driver code to acquire, enable, disable, prepare, parent, and rate-control AFE-related clocks.

### Important APIs, Types, and Definitions
The first enum defines `MT8195_CLK_*` IDs for the 26 MHz crystal, APLL roots, APLL dividers, top muxes, infrastructure/audio clock gates, ADSP audio DSP clock, AFE master clock, APLL tuners, DAC/ADC/hires clocks, I2S/TDM/HDMI/ASRC clocks, A1SYS/A2SYS/PCMIF clocks, and individual memif gates. The second enum defines MCLK source selectors such as `MT8195_MCK_SEL_26M`, `MT8195_MCK_SEL_APLL1`, and `MT8195_MCK_SEL_APLL2`, with placeholders for APLL3-5 and HDMI RX APLL. The third enum defines tuner IDs `MT8195_AUD_PLL1` through `MT8195_AUD_PLL5`.

Function declarations cover MCLK source mapping/rate/default choice, clock initialization, generic enable/disable/prepare/unprepare helpers, atomic enable/disable helpers, clock rate and parent updates, main clock sequencing, and register-read/write clock sequencing.

### Control Flow
There is no implementation control flow in the header. It constrains caller control flow by separating initialization (`mt8195_afe_init_clock()`), generic one-clock operations, atomic vs sleepable clock operations, register-access clock gates, and main AFE clock bring-up/tear-down.

### State and Persistence
The header itself holds no state. Its enum values index `mt8195_afe_private->clk`, so ordering is state-significant: any mismatch between enum order and the implementation clock-name table would route callers to the wrong clock. MCLK and tuner IDs are also persisted indirectly in DAI private data and runtime configuration code.

### Dependencies and Integration Points
It forward-declares `struct mtk_base_afe` and uses `struct clk` pointers in prototypes. It integrates with MT8195 AFE implementation files, DAI drivers, machine drivers, and Linux CCF. It must stay synchronized with `mt8195-afe-clk.c` and with device-tree clock bindings/names.

### Risks
Adding, removing, or reordering enum values without updating `aud_clks[]` and all clock users can silently misconfigure hardware. The MCLK selector enum advertises APLL3-5/HDMIRX choices, but the current implementation only maps 26M/APLL1/APLL2; callers using unsupported selectors receive errors or zero rates. Atomic helpers require callers to prepare clocks elsewhere.

### Test Signals
Compile tests should catch missing declarations and enum names. Runtime signals include correct clock lookup for every enum index, successful DAI paths that rely on memif/ETDM/ADDA clock IDs, expected MCLK parent/rate selection for 8 kHz-family and 44.1 kHz-family rates, and no CCF warnings about unprepared atomic clock enables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-common.h -->
## sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-common.h

### Purpose
This header defines the shared MT8195 AFE IDs, private state structures, DAI registration prototypes, and a helper macro for ALSA mixer enum controls. It is the central type contract between the MT8195 PCM platform driver, ADDA/ETDM/PCM DAI implementations, clock code, and machine driver.

### Important APIs, Types, and Definitions
The main DAI enum lays out one contiguous ID space. It starts with memifs (`DL2`, `DL3`, `DL6`, `DL7`, `DL8`, `DL10`, `DL11`, `UL1`, `UL2`, `UL3`, `UL4`, `UL5`, `UL6`, `UL8`, `UL9`, `UL10`), then IO DAIs (`DL_SRC`, `DPTX`, ETDM1/2 inputs, ETDM1/2/3 outputs, `PCM`, `UL_SRC1`, `UL_SRC2`). It also defines derived counts such as `MT8195_AFE_MEMIF_NUM`, `MT8195_AFE_IO_NUM`, and `MT8195_DAI_NUM`.

Other enums define top clock-gate categories, supported AFE IRQ IDs, ETDM 1x/Nx enable bit positions, and MTKAIF MISO channel indices. `struct mtk_dai_memif_irq_priv` stores per-IRQ ASYS timing selection. `struct mtkaif_param` stores MTKAIF calibration status, chosen phase/cycle for each MISO, DMIC enable state, and ADDA6-only state. `struct mt8195_afe_private` holds clock arrays, topckgen regmap, runtime-PM bypass flag, optional debugfs entries, reference counts, a spinlock for AFE control, IRQ private data, MTKAIF parameters, and DAI-private pointers.

The declared functions are `mt8195_afe_fs_timing()`, `mt8195_dai_adda_register()`, `mt8195_dai_etdm_register()`, and `mt8195_dai_pcm_register()`. `MT8195_SOC_ENUM_EXT()` wraps an ALSA external enum mixer control initializer with a device ID.

### Control Flow
There is no executable control flow. The enum ordering determines how platform code registers DAI drivers, allocates `dai_priv[]`, maps memifs to IRQs and clocks, and routes callbacks. The registration prototypes define the expected initialization sequence for ADDA, ETDM, and PCM DAI modules during platform probe.

### State and Persistence
Persistent runtime state is concentrated in `struct mt8195_afe_private`, which is attached to `mtk_base_afe->platform_priv`. Clock pointers remain for device lifetime, reference counts control shared AFE/top-clock state, `irq_priv[]` records per-IRQ timing decisions, `mtkaif_params` records calibration and mode state, and `dai_priv[]` stores per-DAI implementation state. The header itself does not allocate or persist storage.

### Dependencies and Integration Points
The file includes ALSA SoC, list, regmap, and the common MediaTek base AFE header. It integrates all MT8195 AFE subdrivers around shared ID and private-state contracts. Machine drivers can inspect `mt8195_afe_private` for clock handles and MTKAIF state, while DAI drivers use the IDs and registration prototypes to attach their components.

### Risks
Because ID ordering is used for array indexing, changing enum order can break ABI-like assumptions inside this driver family even if compilation succeeds. `dai_priv[MT8195_DAI_NUM]`, `irq_priv[MT8195_AFE_IRQ_NUM]`, and clock IDs in other headers must stay aligned with all users. Reference counters and spinlocks declared here require disciplined updates in implementation files to avoid unbalanced clocks or races. The ALSA control macro sets `.device = id`; wrong IDs can attach controls to unexpected DAIs.

### Test Signals
Good signals include successful platform probe with all DAI registration functions called, no out-of-bounds array access under KASAN, all declared memif and IO DAI names appearing in ALSA component registration, correct IRQ timing selection for supported rates, MTKAIF calibration fields updated by ADDA paths, debugfs creation when enabled, and clean runtime PM cycles without reference-count imbalance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-common.h -->
