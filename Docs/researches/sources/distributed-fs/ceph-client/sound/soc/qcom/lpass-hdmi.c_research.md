# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-hdmi.c

Purpose: implements LPASS HDMI/DisplayPort DAI operations for configuring HDMI audio metadata, channel status, stream format, and RDMA start/stop.

Important APIs/types/functions: key DAI ops are `lpass_hdmi_daiops_hw_params`, `lpass_hdmi_daiops_prepare`, and `lpass_hdmi_daiops_trigger`, exported as `asoc_qcom_lpass_hdmi_dai_ops`.

Control flow: hw_params configures HDMI TX control reset/legacy bits, stream enable and metadata fields, channel allocation/status/user bits, parity calculation, and DMA channel metadata based on PCM params. Prepare primes HDMI/DP metadata before stream start. Trigger enables or disables the HDMI RDMA path on START/RESUME/PAUSE_RELEASE and STOP/SUSPEND/PAUSE_PUSH.

State and persistence: HDMI-specific regmap fields allocated in `lpass-cpu.c` are stored in `struct lpass_data` and persist across stream operations. Runtime register state includes channel status, user bits, metadata, stream enable, and DMA control.

Dependencies and integration: depends on LPASS HDMI register field setup from `lpass_hdmi_init_bitfields`, LPASS platform DMA allocation, ASoC DAI framework, and DP/HDMI machine-driver routes.

Risks: channel-status metadata must match PCM parameters or sinks may reject audio. HDMI register fields are variant-specific; missing field allocation causes runtime failures. Trigger must synchronize with RDMA setup/teardown to avoid underruns.

Test signals: HDMI/DP playback at supported sample rates/formats/channels, sink channel-status validation, RDMA trigger start/stop, suspend/resume, and jack/ELD integration in machine drivers.
