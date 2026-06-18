# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/Makefile

This Makefile wires the MT8192 ALSA SoC audio platform objects into the kernel build. It defines the multi-object platform driver `snd-soc-mt8192-afe-y`, combining the AFE platform, clock, GPIO, ADDA, common control, I2S, PCM, and TDM DAI implementation objects into `snd-soc-mt8192-afe.o`. It also conditionally builds the board machine driver `mt8192-mt6359-rt1015-rt5682.o`.

Important build targets are `snd-soc-mt8192-afe-y`, `obj-$(CONFIG_SND_SOC_MT8192)`, and `obj-$(CONFIG_SND_SOC_MT8192_MT6359_RT1015_RT5682)`. The platform object list is the link-time integration point for the helper symbols used by `mt8192-afe-pcm.c`. There is no runtime state or persistence here.

Main dependencies are matching source filenames and Kconfig symbols. A stale object list would omit a DAI family or create unresolved symbols. Test signals are kernel builds with the platform and machine configs enabled, plus successful module load/probe of the `mediatek,mt8192-audio` platform device.
