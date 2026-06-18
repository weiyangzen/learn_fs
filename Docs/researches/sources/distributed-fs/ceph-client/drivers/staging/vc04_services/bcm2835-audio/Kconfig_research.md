## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/Kconfig

Purpose: this Kconfig entry defines the staging ALSA driver for BCM2835 built-in audio over the VideoCore VCHIQ messaging interface.

Important definitions: `config SND_BCM2835` is tristate, depends on `(ARCH_BCM2835 || COMPILE_TEST) && SND`, selects `SND_PCM`, and selects `BCM2835_VCHIQ` when `HAS_DMA` is available. Help text states that both 3.5mm and HDMI audio are handled through firmware running on VideoCore.

Control flow and state: build-time selection controls whether the module is built and whether supporting PCM and VCHIQ symbols are selected. No runtime state exists in this file.

Dependencies and integration points: sourced only under `BCM_VIDEOCORE` by the parent Kconfig. The selected symbol drives both parent and child Makefiles.

Risks: `select BCM2835_VCHIQ if HAS_DMA` assumes VCHIQ is valid whenever DMA is present; unusual COMPILE_TEST configs may still expose missing dependencies elsewhere. The staging location implies the driver may not meet normal subsystem quality expectations.

Test signals: Kconfig resolution under Raspberry Pi, COMPILE_TEST, module, and built-in configurations; full build with ALSA disabled should keep the option unavailable.
