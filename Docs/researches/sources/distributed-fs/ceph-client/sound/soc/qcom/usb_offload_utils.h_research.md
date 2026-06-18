# sources/distributed-fs/ceph-client/sound/soc/qcom/usb_offload_utils.h

Purpose: declares or stubs Qualcomm USB offload jack helper APIs depending on `CONFIG_SND_SOC_QCOM_OFFLOAD_UTILS`.

Important APIs: when enabled, it declares `qcom_snd_usb_offload_jack_setup()` and `qcom_snd_usb_offload_jack_remove()`. When disabled, static inline stubs return `-ENODEV`.

Control flow and state: no state is stored. The header lets machine drivers compile regardless of offload utility availability, while making runtime support conditional.

Dependencies and integration: includes ASoC core headers for `snd_soc_pcm_runtime` and `snd_soc_jack`. Consumed by machine drivers such as `sm8250.c`.

Risks: disabled-Kconfig stubs fail at runtime for USB_RX links unless the board tolerates missing USB offload. Because stubs have the same signature, compile coverage does not prove feature availability.

Test signals: build both enabled and disabled Kconfig combinations, verify disabled builds gracefully return `-ENODEV`, and enabled builds export the symbols consumed by machine drivers.
