# sources/distributed-fs/ceph-client/sound/soc/qcom/Kconfig

Purpose: defines Qualcomm ASoC build options for LPASS CPU/platform/HDMI/CDC DMA, board machine drivers, QDSP6 DSP stack, SoundWire helpers, and offload utilities.

Important APIs/types/functions: root `SND_SOC_QCOM` depends on `ARCH_QCOM || COMPILE_TEST`. LPASS symbols select `REGMAP_MMIO`; SoC variants select CPU/platform/HDMI/CDC pieces. Machine drivers such as `SND_SOC_APQ8016_SBC` and `SND_SOC_MSM8996` select common helpers and QDSP6 dependencies.

Control flow: Kconfig dependencies determine which platform and machine objects are compiled and which lower-level DSP/clock/codec dependencies are selected.

State and persistence: build-time configuration only.

Dependencies and integration: feeds `qcom/Makefile` and ensures APR, COMMON_CLK, I2C, SOUNDWIRE, codec, and helper selections for each board family.

Risks: complex select chains can hide missing runtime dependencies. Several machine drivers require QDSP6/APR and SoundWire; incorrect dependencies cause build or probe failures. Indentation in the QDSP6 USB block is unusual but syntactically meaningful to Kconfig.

Test signals: allmodconfig/allyesconfig, individual SoC defconfigs, dependency resolution for APR/SoundWire/I2C variants, and compile tests of LPASS-only versus QDSP6-backed cards.
