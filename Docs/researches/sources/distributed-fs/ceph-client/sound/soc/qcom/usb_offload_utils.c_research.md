# sources/distributed-fs/ceph-client/sound/soc/qcom/usb_offload_utils.c

Purpose: provides shared jack setup/removal helpers for Qualcomm machine drivers using Q6 USB audio offload.

Important APIs: `qcom_snd_usb_offload_jack_setup()` verifies the CPU DAI is `USB_RX`, calls `snd_soc_usb_setup_offload_jack()` on the codec component if not already set up, and marks the caller-owned setup flag. `qcom_snd_usb_offload_jack_remove()` verifies `USB_RX`, clears the codec component jack via `snd_soc_component_set_jack(NULL)`, and resets the flag. Both are exported GPL symbols.

Control flow and state: state is caller-owned through `bool *jack_setup`; the helper is idempotent for repeated setup/removal on the same runtime. It obtains CPU and codec DAIs from the runtime rather than storing global state.

Dependencies and integration: depends on Q6AFE `USB_RX`, ASoC DAI/runtime helpers, `sound/soc-usb.h`, and is used by SM8250-like machine drivers that expose USB_RX backends.

Risks: returns `-EINVAL` for non-USB_RX runtimes, so callers must dispatch correctly. If codec component offload support is absent, setup propagates the failure. The helper assumes codec DAI index 0 is the offload component.

Test signals: USB_RX BE init creates an offload jack once, exit clears it once, non-USB links do not call this helper, and plug/unplug events report through the q6usb component.
