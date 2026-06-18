# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-cdc-dma.c

Purpose: implements LPASS codec DMA DAI operations for RXTX/VA CDC DMA paths used by newer Qualcomm audio macros.

Important APIs/types/functions: key helpers include `__lpass_get_dmactl_handle`, `__lpass_get_codec_dma_intf_type`, `__lpass_platform_codec_intf_init`, and DAI ops `lpass_cdc_dma_daiops_startup`, `shutdown`, `hw_params`, and `trigger`. Exports `asoc_qcom_lpass_cdc_dma_dai_ops`.

Control flow: startup enables codec memory clocks/resources for the selected DMA interface. hw_params initializes the correct RXTX or VA DMA interface register field, programs DMA control fields through variant regmap fields, and configures channel/format-related interface selection. Trigger enables or disables DMA based on ALSA trigger commands. Shutdown drops clocks/resources.

State and persistence: per-stream DMA control handles are resolved from `struct lpass_data` and variant mappings. Codec memory clock state persists while streams are active.

Dependencies and integration: depends on LPASS register macros, `is_cdc_dma_port`, variant DMA field definitions, codec memory clocks parsed by `lpass-cpu.c`, and LPASS platform PCM code.

Risks: DAI ID to interface mapping is critical and easy to break as bindings grow. Clock/resource enablement must stay balanced across startup failures and trigger errors. CDC DMA register maps differ between RXTX and VA regions.

Test signals: startup/hw_params/trigger for RX, TX, and VA CDC DMA ports, interface register programming, codec memory clock rates/enables, and DMA capture/playback with period interrupts.
