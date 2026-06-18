# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6usb.c

Purpose: provides the QDSP6 USB backend DAI for Qualcomm USB audio offload. It bridges ASoC DAI setup, `sound/soc-usb` offload discovery, jack reporting, an auxiliary device for QC USB offload, and Q6AFE USB device parameter programming.

Important functions and types: `struct q6usb_port_data` stores the auxiliary device, USB config, `snd_soc_usb` port, optional jack, offload private data, mutex, and connected USB device list. `q6usb_hw_params()` validates the selected USB device format and sends card/PCM indexes to the DSP via `afe_port_send_usb_dev_param()`. `q6usb_update_offload_route()` reports card or PCM route IDs. `q6usb_alsa_connection_cb()` maintains the active device list and jack state.

Control flow: platform probe reads `qcom,usb-audio-intr-idx`, optionally derives SID from `iommus`, records the IOMMU domain, and registers a component plus `USB_RX_BE` DAI. Component probe adds the auxiliary device, allocates an ASoC USB port, installs connection and route callbacks, and registers the port. DAPM traversal maps enabled USB mixer paths back to the active FE PCM ID.

State and persistence: connected devices are tracked in an in-memory list; the newest connected playback device is selected for offload. Jack state and stream selection vanish on disconnect/remove.

Dependencies and integration: depends on q6afe, q6dsp LPASS ports, auxiliary bus, IOMMU APIs, ASoC USB helpers, DAPM routes, and `qcom,q6usb` DT nodes.

Risks: route selection uses the last connected USB playback device and DAPM graph name assumptions (`MultiMedia*`, `USB Mixer`). Mutex coverage protects list operations, but callback ordering between USB core and ASoC component removal is a key edge.

Test signals: USB headset plug/unplug jack events, `snd_soc_usb_find_supported_format()` success for supported PCM params, DSP parameter send success, and route controls exposing the correct card/PCM indexes.
