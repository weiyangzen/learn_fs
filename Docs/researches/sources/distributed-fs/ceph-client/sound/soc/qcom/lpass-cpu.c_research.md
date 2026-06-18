# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-cpu.c

Purpose: implements the generic Qualcomm LPASS CPU DAI driver and platform probe support for MI2S, HDMI, and CDC DMA-capable variants.

Important APIs/types/functions: DAI ops are exported as `asoc_qcom_lpass_cpu_dai_ops` and `_ops2`. Major helpers include `lpass_cpu_init_i2sctl_bitfields`, MI2S startup/shutdown/hw_params/prepare/trigger, regmap access filters for CPU/HDMI/RXTX/VA maps, `lpass_hdmi_init_bitfields`, OF SD-line parsing, CDC clock parsing, `asoc_qcom_lpass_cpu_platform_probe`, remove, and shutdown.

Control flow: probe rejects devices where `qcom,adsp` owns audio resources, allocates `lpass_data`, loads variant data, parses child DAI nodes for HDMI/CDC enablement and MI2S SD-line masks, maps LPASS MMIO regions, initializes regmaps, runs variant init, obtains MI2S clocks, allocates I2SCTL regmap fields, initializes HDMI fields if needed, registers CPU DAIs, and registers the LPASS platform. Runtime MI2S startup prepares OSR/BIT clocks; hw_params programs bit width, SD-line mode, mono/stereo, and bit clock rate; prepare/trigger manage LRCLK/BCLK and speaker/mic enable fields.

State and persistence: `struct lpass_data` persists variant pointers, regmaps, regmap fields, clocks, SD-line modes, HDMI/CDC flags, prepared-clock booleans, and DMA maps. Register caches are flat regmap caches with volatile current pointer/IRQ status registers.

Dependencies and integration: central integration point for `lpass.h`, LPASS register macros, SoC variant drivers, LPASS platform PCM, HDMI/CDC DAI ops, DT child nodes, and common clock/regmap frameworks.

Risks: complex clock balancing between prepare, trigger, shutdown, and suspend paths; shared BCLK use requires careful enable counts. OF SD-line parsing defaults to 8-channel compatibility and can mask DT omissions. Regmap readable/writeable filters must match variant register ranges exactly. Probe mutates variant DAI channel limits for quad modes, which can affect static variant data.

Test signals: probe for APQ8016/SC variants with and without HDMI/CDC nodes, MI2S playback/capture for 1/2/4/6/8 channels, SD-line DT validation, clock enable-count tests across pause/suspend/resume, regmap access warnings, and platform PCM DMA operation.
