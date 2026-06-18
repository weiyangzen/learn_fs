# sources/distributed-fs/ceph-client/sound/soc/sti/uniperif.h

Purpose: shared STi uniperipheral hardware and driver contract header. It contains register access helpers and generated-style macros for soft reset, FIFO data, interrupt status/masks, configuration, control, I2S format, status, channel status, validity, and TDM registers, plus core state structures and common prototypes.

Important APIs and types: generic macros `GET_UNIPERIF_REG()`, `SET_UNIPERIF_REG()`, and `SET_UNIPERIF_BIT_REG()` implement read-modify-write and write-one bit operations. `enum uniperif_version`, `enum uniperif_type`, and `enum uniperif_state` describe IP capabilities and runtime state. `struct uniperif` is the central object shared by common, player, and reader code. `uni_tdm_hw` defines TDM PCM constraints. Prototypes expose player/reader init, DAI callbacks, reset, TDM slot helpers, and frame-size helpers.

Control flow and integration: C files program hardware almost entirely through macros from this header. Version-dependent macros return invalid shifts or zero masks for unsupported registers, so callers must only use them in compatible version paths. `struct uniperif` ties MMIO, IRQ, clock, state, substream, controls, IEC958 status, TDM slots, and DAI ops into one object.

State and persistence: the header defines state fields but does not manage lifetime. Runtime state lives in `state`, `substream`, `stream_settings`, `tdm_slot`, `daifmt`, `mclk`, and `clk_adj`; hardware state lives in MMIO registers modified through macros.

Dependencies: Linux regmap fields, dmaengine PCM, ALSA IEC958 and PCM types through includers, and version-specific STi hardware register semantics.

Risks: many macros perform read-modify-write without locking; callers must serialize concurrent control/trigger/IRQ paths. Several unsupported-version macros encode shift `-1`; accidental use can produce undefined bit operations or invalid MMIO offsets. `GET_UNIPERIF_CHANNEL_STA_REGN(ip)` references `n` despite not taking it as a macro parameter in one definition. `UNIPERIF_I2S_FMT_PADDING_MASK` is duplicated. The large macro surface makes static analysis harder than typed regmap fields.

Test signals: compile with sparse/W=1 to catch macro issues, run Coccinelle for negative shift uses, exercise each player/reader type and IP version path, validate TDM register programming on hardware, and use lockdep/KCSAN around control updates versus IRQ handling.
