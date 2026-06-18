# sources/distributed-fs/ceph-client/drivers/media/usb/Kconfig

Purpose: top-level Kconfig menu for USB media adapters.

APIs/entries: `menuconfig MEDIA_USB_SUPPORT` appears under `USB && MEDIA_SUPPORT`. Nested conditional `source` lines include webcam, analog TV, analog/digital TV, digital TV USB, mixed webcam/TV, and SDR USB driver Kconfigs.

Control flow/state: Kconfig visibility depends on media feature symbols such as camera, analog TV, digital TV, I2C, and SDR support. Choices persist in `.config`.

Dependencies/integration: must stay aligned with `drivers/media/usb/Makefile`. AirSpy is sourced under `MEDIA_SDR_SUPPORT`.

Risks/tests: missing sources hide drivers; bad guards expose invalid dependencies. Test Kconfig parsing and menu visibility across USB/media feature matrices.
