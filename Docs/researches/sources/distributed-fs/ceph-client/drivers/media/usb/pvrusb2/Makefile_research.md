<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/Makefile

Purpose: Kbuild composition for the multi-file `pvrusb2` driver.

Important APIs/types/functions: variables `obj-pvrusb2-sysfs-*`, `obj-pvrusb2-debugifc-*`, and `obj-pvrusb2-dvb-*` conditionally add optional objects. `pvrusb2-objs` lists I2C, audio, encoder, V4L2 video, EEPROM, main, hardware, control, standard, device-attribute, context, I/O, subdevice-routing, DVB/sysfs/debug objects. Include paths add tuner and DVB frontend headers.

Control flow: Kbuild folds all selected objects into one `pvrusb2.o`, then links it according to `CONFIG_VIDEO_PVRUSB2`.

State and persistence: build artifact control only.

Dependencies and integration: tightly paired with `pvrusb2/Kconfig` and with source files that reference tuner/frontend headers via the added include paths.

Risks: optional object variables use `-y` expansion, so only built-in booleans append optional objects; this matches bool suboptions but must remain aligned with Kconfig types. Missing include path updates can break frontend/tuner configuration tables.

Test signals: compile all combinations of sysfs/DVB/debug; `nm pvrusb2.o` for optional symbols; module load with digital and analog devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/Makefile -->
