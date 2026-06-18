<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si4713/Makefile

Purpose: maps Si4713 Kconfig symbols to the objects built by kbuild.

Important APIs and entries: `obj-$(CONFIG_I2C_SI4713) += si4713.o`, `obj-$(CONFIG_USB_SI4713) += radio-usb-si4713.o`, and `obj-$(CONFIG_PLATFORM_SI4713) += radio-platform-si4713.o`.

Control flow: kbuild links each selected object as its own module or built-in unit according to the resolved tristate value. The USB and platform objects are wrappers around the core I2C subdevice.

State and persistence: no runtime state. The file defines build artifact shape only.

Dependencies and integration points: depends on symbols declared in the adjacent `Kconfig`. The object boundaries align with driver registration boundaries: I2C driver, USB driver, and platform driver.

Risks: new source files added to the Si4713 stack must be represented here or functionality will silently not build. Wrapper modules depend on the core module relationship expressed by Kconfig rather than Makefile ordering.

Test signals: targeted kbuilds with each symbol enabled as `m` and built-in, plus module load tests confirming dependencies resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/Makefile -->
