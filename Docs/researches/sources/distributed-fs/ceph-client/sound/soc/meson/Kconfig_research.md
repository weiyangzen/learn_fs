# sources/distributed-fs/ceph-client/sound/soc/meson/Kconfig

Purpose: Declares the Amlogic Meson ASoC Kconfig menu and the symbols controlling AIU, AXG FIFO, TDM, SPDIF, PDM, card utilities, codec glue, GX/AXG sound cards, G12A routing controls, and the T9015 DAC.

Important entries: `SND_MESON_AIU` enables the older Meson8/GX Audio Input Unit and selects codec glue plus IEC958 support. `SND_MESON_AXG_FIFO` is a hidden common symbol selected by `SND_MESON_AXG_FRDDR` and `SND_MESON_AXG_TODDR`. `SND_MESON_AXG_TDM_FORMATTER` and `SND_MESON_AXG_TDM_INTERFACE` are hidden common TDM layers selected by `SND_MESON_AXG_TDMIN` and `SND_MESON_AXG_TDMOUT`. `SND_MESON_AXG_SOUND_CARD` and `SND_MESON_GX_SOUND_CARD` select or imply the needed frontend/backend drivers. `SND_MESON_AXG_SPDIFOUT`, `SND_MESON_AXG_SPDIFIN`, `SND_MESON_AXG_PDM`, `SND_MESON_G12A_TOACODEC`, `SND_MESON_G12A_TOHDMITX`, and `SND_SOC_MESON_T9015` expose individual endpoint/control choices.

Control flow: Kconfig evaluation is gated by `ARCH_MESON` or `COMPILE_TEST && COMMON_CLK`. Selected symbols pull in required helper modules, while `imply` suggests platform companions without forcing them.

State and persistence: User selections persist in the kernel `.config` and decide which objects from the Meson Makefile build into the kernel or modules.

Dependencies and integration points: Integrates with the parent ALSA SoC Kconfig tree, Common Clock framework, REGMAP MMIO, reset drivers, HDMI codec support, DRM Meson HDMI availability, and dynamic minor support.

Risks: Hidden common symbols rely on all public drivers selecting the right helper. `imply` does not guarantee dependencies are present, so runtime card topologies can still miss optional codecs or routing controls. Menu dependency on `COMMON_CLK` for compile testing is important because most drivers depend heavily on clock APIs.

Test signals: `allyesconfig`/`allmodconfig` compile coverage, menu visibility on Meson and COMPILE_TEST builds, module dependency checks, and build tests for minimal selections such as only SPDIFIN, only PDM, or only AIU.
