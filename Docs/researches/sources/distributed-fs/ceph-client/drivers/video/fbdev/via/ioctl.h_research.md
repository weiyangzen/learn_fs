<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/ioctl.h

Purpose: Public/driver-private definition of the legacy viafb ioctl ABI. It assigns numeric command values, userspace-facing structures, device bit constants, LCD operation constants, and prototypes for the ioctl helper functions.

Important APIs/types/functions: Command constants include `VIAFB_GET_INFO_SIZE`, `VIAFB_GET_INFO`, `VIAFB_HOTPLUG`, output on/off commands, device/support/connect queries, gamma table commands, panel position/size commands, and `VIAFB_GET_CHIP_INFO`. Data structures include `struct device_t`, `struct viafb_ioctl_info`, `struct viafb_ioctl_mode`, `struct viafb_ioctl_samm`, `struct viafb_driver_version`, `struct viafb_ioctl_lcd_attribute`, `struct viafb_ioctl_setting`, `_UTFunctionCaps`, `_POSITIONVALUE`, and `_panel_size_pos_info`. Prototypes expose `viafb_ioctl_get_viafb_info()` and `viafb_ioctl_hotplug()`.

Control flow and state: This header has no executable flow. It defines the binary layout used by `viafb_ioctl()` to copy state between kernel and userspace. The ABI stores active devices, SAMM state, primary device, LCD panel/mode attributes, resolutions, refresh rates, bpp values, and framebuffer split sizes.

Dependencies and integration points: It is included by `viafbdev.h` and is part of the fbdev ioctl surface. It conditionally defines `__user` for non-kernel parsing contexts, suggesting the header may have historically been used by userspace tools. Risks are ABI brittleness: command numbers are raw constants instead of `_IO*` encodings, many structures use fixed-width-but-not-always-explicit fields and bitfields, several commands in `viafbdev.c` are stubs, and the file itself labels the interface unstable. Test signals are 32/64-bit userspace compatibility checks, ioctl fuzzing for each command's copy length, and regression tests around gamma, SAMM, hotplug, and device state serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/ioctl.h -->
