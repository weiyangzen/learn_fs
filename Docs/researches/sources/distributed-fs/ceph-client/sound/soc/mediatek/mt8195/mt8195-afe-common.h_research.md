# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-common.h

## Purpose
This header defines the shared MT8195 AFE IDs, private state structures, DAI registration prototypes, and a helper macro for ALSA mixer enum controls. It is the central type contract between the MT8195 PCM platform driver, ADDA/ETDM/PCM DAI implementations, clock code, and machine driver.

## Important APIs, Types, and Definitions
The main DAI enum lays out one contiguous ID space. It starts with memifs (`DL2`, `DL3`, `DL6`, `DL7`, `DL8`, `DL10`, `DL11`, `UL1`, `UL2`, `UL3`, `UL4`, `UL5`, `UL6`, `UL8`, `UL9`, `UL10`), then IO DAIs (`DL_SRC`, `DPTX`, ETDM1/2 inputs, ETDM1/2/3 outputs, `PCM`, `UL_SRC1`, `UL_SRC2`). It also defines derived counts such as `MT8195_AFE_MEMIF_NUM`, `MT8195_AFE_IO_NUM`, and `MT8195_DAI_NUM`.

Other enums define top clock-gate categories, supported AFE IRQ IDs, ETDM 1x/Nx enable bit positions, and MTKAIF MISO channel indices. `struct mtk_dai_memif_irq_priv` stores per-IRQ ASYS timing selection. `struct mtkaif_param` stores MTKAIF calibration status, chosen phase/cycle for each MISO, DMIC enable state, and ADDA6-only state. `struct mt8195_afe_private` holds clock arrays, topckgen regmap, runtime-PM bypass flag, optional debugfs entries, reference counts, a spinlock for AFE control, IRQ private data, MTKAIF parameters, and DAI-private pointers.

The declared functions are `mt8195_afe_fs_timing()`, `mt8195_dai_adda_register()`, `mt8195_dai_etdm_register()`, and `mt8195_dai_pcm_register()`. `MT8195_SOC_ENUM_EXT()` wraps an ALSA external enum mixer control initializer with a device ID.

## Control Flow
There is no executable control flow. The enum ordering determines how platform code registers DAI drivers, allocates `dai_priv[]`, maps memifs to IRQs and clocks, and routes callbacks. The registration prototypes define the expected initialization sequence for ADDA, ETDM, and PCM DAI modules during platform probe.

## State and Persistence
Persistent runtime state is concentrated in `struct mt8195_afe_private`, which is attached to `mtk_base_afe->platform_priv`. Clock pointers remain for device lifetime, reference counts control shared AFE/top-clock state, `irq_priv[]` records per-IRQ timing decisions, `mtkaif_params` records calibration and mode state, and `dai_priv[]` stores per-DAI implementation state. The header itself does not allocate or persist storage.

## Dependencies and Integration Points
The file includes ALSA SoC, list, regmap, and the common MediaTek base AFE header. It integrates all MT8195 AFE subdrivers around shared ID and private-state contracts. Machine drivers can inspect `mt8195_afe_private` for clock handles and MTKAIF state, while DAI drivers use the IDs and registration prototypes to attach their components.

## Risks
Because ID ordering is used for array indexing, changing enum order can break ABI-like assumptions inside this driver family even if compilation succeeds. `dai_priv[MT8195_DAI_NUM]`, `irq_priv[MT8195_AFE_IRQ_NUM]`, and clock IDs in other headers must stay aligned with all users. Reference counters and spinlocks declared here require disciplined updates in implementation files to avoid unbalanced clocks or races. The ALSA control macro sets `.device = id`; wrong IDs can attach controls to unexpected DAIs.

## Test Signals
Good signals include successful platform probe with all DAI registration functions called, no out-of-bounds array access under KASAN, all declared memif and IO DAI names appearing in ALSA component registration, correct IRQ timing selection for supported rates, MTKAIF calibration fields updated by ADDA paths, debugfs creation when enabled, and clean runtime PM cycles without reference-count imbalance.
