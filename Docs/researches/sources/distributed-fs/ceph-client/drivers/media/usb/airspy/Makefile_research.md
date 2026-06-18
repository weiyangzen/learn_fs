# sources/distributed-fs/ceph-client/drivers/media/usb/airspy/Makefile

Purpose: kbuild rule for the AirSpy USB SDR driver.

APIs/rules: `obj-$(CONFIG_USB_AIRSPY) += airspy.o` builds the object as module or built-in according to Kconfig.

Control flow/state: parent USB Makefile descends into this directory when `CONFIG_USB_AIRSPY` is enabled. No runtime state.

Dependencies/integration: must match the Kconfig symbol and `airspy.c` object name.

Risks/tests: symbol or file-name drift breaks the module. Test `CONFIG_USB_AIRSPY=m` and confirm generated module name `airspy`.
