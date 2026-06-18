<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/serio.h

Purpose: defines serio input-device ioctl, event flags, bus/controller types, and protocol/device IDs for serial input devices such as keyboards, mice, touchscreens, game controllers, and CEC adapters.

Important APIs, types, and functions: `SPIOCSTYPE` sets the serio type. Event flags include timeout, parity, frame, and out-of-band data. Bus/controller constants include XT, 8042, RS232, HIL, passthrough, and XL. Protocol IDs cover many mouse, keyboard, touchscreen, tablet, joystick, and adapter devices such as MSC, Sun, Microsoft, Wacom, eGalax, Pulse8 CEC, RainShadow CEC, FS-iA6B, and Extron.

Control flow: serio drivers report port and device protocol types to input core. Userspace or compatibility tools may set a port type through ioctl. Drivers consume event flags while decoding input bytes.

State and persistence behavior: serio port type and attached device identity live in kernel input/serio state. The header only defines ABI constants.

Dependencies and integration points: depends on const and ioctl UAPI headers. It integrates with the Linux input subsystem, i8042, serial input drivers, and device matching tables.

Risks and edge cases: protocol IDs are stable ABI. Misidentifying a device can bind the wrong input driver. Event flags may be reported asynchronously with data bytes and must be decoded with ordering preserved.

Test signals: input device probing for common serio protocols, ioctl type setting, parity/frame/timeout error injection, hotplug/unplug, and ID stability checks for userspace device databases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serio.h -->
