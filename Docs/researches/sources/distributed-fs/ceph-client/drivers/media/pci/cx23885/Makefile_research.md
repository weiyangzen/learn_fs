# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/Makefile

Defines the cx23885 module composition. `cx23885-objs` links card setup, video, VBI, core, I2C, DVB, CX23417 encoder, ioctl, IR/input, NetUP helpers, CIMax2, f300, and ALSA into `cx23885.o`.

`obj-$(CONFIG_VIDEO_CX23885)` builds the main module and `obj-$(CONFIG_MEDIA_ALTERA_CI)` builds `altera-ci.o`. Include flags add tuner and DVB frontend header paths.

Risks are missing objects when adding features or build failures when optional dependencies move. Test signals are modular and built-in builds with and without `MEDIA_ALTERA_CI`.
