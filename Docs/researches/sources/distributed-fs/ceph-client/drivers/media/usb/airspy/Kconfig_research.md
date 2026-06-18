# sources/distributed-fs/ceph-client/drivers/media/usb/airspy/Kconfig

Purpose: Kconfig entry for the AirSpy USB SDR V4L2 driver.

APIs/entries: `config USB_AIRSPY` is tristate "AirSpy", depends on `VIDEO_DEV`, selects `VIDEOBUF2_VMALLOC`, and documents module name `airspy`.

Control flow/state: sourced by parent USB media Kconfig under SDR support; user choice persists in `.config`.

Dependencies/integration: build rule is `obj-$(CONFIG_USB_AIRSPY) += airspy.o`.

Risks/tests: missing videobuf2 selection or wrong dependency breaks build/runtime buffers. Test `CONFIG_USB_AIRSPY=m` and built-in builds.
