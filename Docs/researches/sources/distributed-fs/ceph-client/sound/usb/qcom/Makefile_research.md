# sources/distributed-fs/ceph-client/sound/usb/qcom/Makefile

Purpose: Kbuild glue for the Qualcomm USB audio QMI/offload module.

Important APIs, types, and functions: no C API is defined. It builds `snd-usb-audio-qmi.o` from `usb_audio_qmi_v01.o`, `qc_audio_offload.o`, and `mixer_usb_offload.o`, and links the module when `CONFIG_SND_USB_AUDIO_QMI` is enabled.

Control flow: Kbuild compiles the generated QMI encoding tables, the offload auxiliary driver/QMI server, and the mixer controls into a single module object.

State and persistence: persistent output is the kernel object/module selected by the Kconfig symbol. Runtime state is in the C files.

Dependencies and integration points: must remain aligned with Kconfig, the auxiliary device name `q6usb.qc-usb-audio-offload`, and usb-audio platform ops registration.

Risks: omitting one object would leave either QMI encoding symbols, mixer controls, or offload ops unresolved. The module is all-or-nothing; partial feature selection is not represented here.

Test signals: `make M=sound/usb/qcom` with `CONFIG_SND_USB_AUDIO_QMI=m/y` produces `snd-usb-audio-qmi`, and symbol resolution succeeds for QMI element arrays and `snd_usb_offload_create_ctl()`.
