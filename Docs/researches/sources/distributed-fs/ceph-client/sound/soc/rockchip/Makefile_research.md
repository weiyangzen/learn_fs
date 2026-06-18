# sources/distributed-fs/ceph-client/sound/soc/rockchip/Makefile

Purpose: Rockchip ASoC object mapping for Kbuild. It maps Kconfig symbols to controller and machine-driver object files.

Important APIs, types, and functions: Defines module object aggregates for `snd-soc-rockchip-i2s`, `snd-soc-rockchip-i2s-tdm`, `snd-soc-rockchip-pdm`, `snd-soc-rockchip-sai`, `snd-soc-rockchip-spdif`, `snd-soc-rockchip-max98090`, `snd-soc-rockchip-rt5645`, `snd-soc-rk3288-hdmi-analog`, and `snd-soc-rk3399-gru-sound`.

Control flow: Kbuild appends objects to `obj-$(CONFIG_...)` according to selected Kconfig symbols. Each aggregate currently contains one `.o`.

State and persistence: No runtime state; affects build outputs and module names.

Dependencies and integration: Consumes symbols declared in `Kconfig` and source files in the same directory, including files not in this work item such as `rockchip_sai.c` and `rockchip_spdif.c`.

Risks and edge cases: Missing object entries would make a Kconfig option build no code; stale entries would break builds. Module names are ABI-visible to packaging/scripts.

Test signals: `make sound/soc/rockchip/` or full kernel builds with each symbol enabled should produce the expected `.o`/module artifacts without unresolved references.
