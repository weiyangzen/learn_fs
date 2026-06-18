# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/usbdevfs_ioctl.sh

Purpose: Generates USBDEVFS ioctl command names.

Important APIs/types/functions: It parses `USBDEVFS_*` definitions in `usbdevice_fs.h` and emits `static const char *usbdevfs_ioctl_cmds[]`. It also emits a disabled `#if 0` block for 32-bit variants.

Control flow: The main regex handles `_IO`, `_IOR`, `_IOW`, `_IOWR`, and `_IOC`-style macros with type `U`, filters `USBDEVFS_*32` commands, sorts entries, and prints them. A second pass emits the disabled 32-bit table.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `ioctl__scnprintf_usbdevfs_cmd` in `ioctl.c`, selected when fd major is USB device major.

Risks: USBDEVFS shares ioctl type letter `U` with ALSA control, so consumer fd classification is required. Disabled 32-bit table means compat-specific names may not be used.

Test signals: Regenerate and trace common USBDEVFS ioctls on a USB device fd; verify ALSA control fds still use `SNDRV_CTL_*`.
