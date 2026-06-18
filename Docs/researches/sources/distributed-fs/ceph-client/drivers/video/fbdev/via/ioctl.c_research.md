<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/ioctl.c

Purpose: Implements two helper routines behind the legacy VIA fbdev ioctl interface: driver/chip identity reporting and a simple DVI-vs-CRT hotplug policy.

Important APIs/types/functions: `viafb_ioctl_get_viafb_info(u_long arg)` fills `struct viafb_ioctl_info` with `VIAID`, `PCI_VIA_VENDOR_ID`, a chipset-specific device ID derived from `viaparinfo->chip_info->gfx_chip_name`, and the viafb major/minor version before copying it to userspace. `viafb_ioctl_hotplug(int hres, int vres, int bpp)` senses DVI through `viafb_dvi_sense()`, prefers DVI over CRT when a TMDS transmitter exists, mutates `viafb_DVI_ON`, `viafb_CRT_ON`, `viafb_LCD_ON`, `viafb_DeviceStatus`, and calls `viafb_set_iga_path()`.

Control flow and state: The info path is straight-line except for the chipset switch and `copy_to_user` failure handling. The hotplug path first checks for a real TMDS transmitter, then promotes attached DVI if current status is not DVI, otherwise falls back to CRT when no DVI status is active. The `hres`, `vres`, and `bpp` parameters are unused, so hotplug does not validate the current mode against detected output.

Dependencies and integration points: Included via `global.h` and called from `viafb_ioctl()` in `viafbdev.c`. It depends on global `viaparinfo`, TMDS detection helpers, userspace copy helpers, and the IOCTL constants/types in `ioctl.h`. Risks include an unstable ABI warning from the caller, unsynchronized global output-state mutation, unhandled newer chip names in the device-id switch, no LCD hotplug policy, and limited failure reporting from I2C sense paths. Test signals are ioctl userspace probes for `VIAFB_GET_INFO` and `VIAFB_HOTPLUG`, DVI attach/detach exercises, and validating that `viafb_set_iga_path()` reprograms expected output routing after status changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/ioctl.c -->
