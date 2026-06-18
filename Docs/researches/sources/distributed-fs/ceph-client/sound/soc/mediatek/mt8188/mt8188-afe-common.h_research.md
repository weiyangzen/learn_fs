# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-common.h

Purpose: Provides shared MT8188 ASoC identifiers and private state for the AFE platform and sub-DAI registration files. It is the central cross-file contract for memif IDs, backend IO DAI IDs, IRQ IDs, top clock-gate IDs, MTKAIF calibration data, per-IRQ timing state, and per-DAI private pointers.

Important APIs and types: The main DAI enum lays out all DAI IDs from memory interfaces (`DL2`, `DL3`, `DL6`, `DL7`, `DL8`, `DL10`, `DL11`, `UL1`, `UL2`, `UL3`, `UL4`, `UL5`, `UL6`, `UL8`, `UL9`, `UL10`) through backend IO (`DL_SRC`, `DMIC_IN`, `DPTX`, eTDM IN/OUT, `PCM`, `UL_SRC`). The IRQ enum defines MCU and ASYS IRQ slots used by `irq_data` in `mt8188-afe-pcm.c`. The eTDM timing enum defines special FS selectors used when memif IRQs are synchronized to eTDM domains. `struct mt8188_afe_private` stores clock arrays, clock lookups, optional `topckgen`, runtime-PM bypass state, a spinlock, per-IRQ timing selections, MTKAIF params, and `dai_priv[]`.

Control flow and integration: Platform probe allocates `struct mt8188_afe_private` and then each DAI registration function allocates its own state into `dai_priv[id]`. ADDA reads and writes `mtkaif_params`. PCM controls update `irq_priv[]` and memif private state. eTDM, DMIC, ADDA, and PCMIF all retrieve their private state through this common array. The file declares the registration functions invoked from the platform DAI registration callback table.

State and persistence: This header defines memory layout only. Runtime state persists in the allocated `mt8188_afe_private` for the lifetime of the platform device. The enum numeric values are persistent internal IDs and must match memif/IRQ data tables, DAPM route naming assumptions, and DAI driver IDs.

Dependencies: Includes Linux list/regmap, ALSA SoC headers, and common MediaTek base AFE definitions. The `MT8188_SOC_ENUM_EXT` macro wraps ALSA mixer control initialization while storing a DAI or IRQ ID in `.device`, which several custom control handlers use to find state.

Risks: Any enum insertion can break table indexing in `memif_data`, `irq_data`, `mt8188_afe_memif_const_irqs`, and `dai_priv`. `dai_priv` is a `void *` array, so wrong IDs become runtime type confusion rather than compile-time failures. The macro stores IDs in ALSA control `.device`; handlers depend on that field remaining untouched.

Test signals: Build with all mt8188 sub-drivers catches missing declarations. Probe should allocate every private object before controls are used. ALSA control tests for memif timing, DMIC gain, ADDA DMIC switch, and eTDM settings exercise the shared private state paths.
