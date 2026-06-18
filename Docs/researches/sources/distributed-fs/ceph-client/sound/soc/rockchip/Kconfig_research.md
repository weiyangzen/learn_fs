# sources/distributed-fs/ceph-client/sound/soc/rockchip/Kconfig

Purpose: Kconfig menu for Rockchip ASoC controller and machine drivers. It controls build availability for I2S, I2S/TDM, PDM, SAI, SPDIF, and several board-specific codec/HDMI sound cards.

Important APIs, types, and functions: Configuration symbols include `SND_SOC_ROCKCHIP_I2S`, `SND_SOC_ROCKCHIP_I2S_TDM`, `SND_SOC_ROCKCHIP_PDM`, `SND_SOC_ROCKCHIP_SAI`, `SND_SOC_ROCKCHIP_SPDIF`, `SND_SOC_ROCKCHIP_MAX98090`, `SND_SOC_ROCKCHIP_RT5645`, `SND_SOC_RK3288_HDMI_ANALOG`, and `SND_SOC_RK3399_GRU_SOUND`. Controller symbols select `SND_SOC_GENERIC_DMAENGINE_PCM`; PDM selects `RATIONAL`; SPDIF selects `SND_PCM_IEC958`. Machine symbols select their codec/controller dependencies.

Control flow: This is declarative build configuration. The menu is visible for `ARCH_ROCKCHIP` or `COMPILE_TEST` and requires `HAVE_CLK`. Selecting a board driver pulls in the needed controller and codec drivers.

State and persistence: No runtime state. The selected symbols persist only in kernel `.config` and determine objects built by the Makefile.

Dependencies and integration: Integrates Rockchip ASoC with kernel build system and codec Kconfig symbols such as MAX98090, RT5645, HDMI codec, ES8328, RT5514, DA7219, DMIC, and MAX98357A.

Risks and edge cases: Board drivers depend on I2C/GPIOLIB/SPI as needed, but real device-tree and pinctrl requirements are not expressible here. `COMPILE_TEST` can build code on non-Rockchip platforms where runtime resources are absent.

Test signals: `allyesconfig`/`COMPILE_TEST` builds should include selected objects. Enabling a machine symbol should automatically enable its controller and codec dependencies.
