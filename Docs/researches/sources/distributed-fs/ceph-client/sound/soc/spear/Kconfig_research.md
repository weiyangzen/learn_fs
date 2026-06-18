# sources/distributed-fs/ceph-client/sound/soc/spear/Kconfig

Purpose: Kconfig menu for ST SPEAr ASoC support.

Important APIs/types: `SND_SPEAR_SOC` selects generic DMAEngine PCM and builds the shared PCM platform helper. `SND_SPEAR_SPDIF_OUT` and `SND_SPEAR_SPDIF_IN` are tristate symbols for the S/PDIF playback and capture interfaces.

Control flow/state: no runtime state. Symbols are minimal and likely selected by board/platform configuration rather than exposing detailed prompts here.

Dependencies/integration: supports legacy SPEAr platform-data based audio drivers.

Risks/test signals: build configurations should ensure S/PDIF drivers select or depend on `SND_SPEAR_SOC` where the shared PCM helper symbol is required.
