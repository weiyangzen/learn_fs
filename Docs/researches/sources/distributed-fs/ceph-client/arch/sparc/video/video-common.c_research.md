# sources/distributed-fs/ceph-client/arch/sparc/video/video-common.c

Purpose: identifies whether a SPARC video device is the firmware-selected primary console device.

Important APIs/functions: exports `video_is_primary_device(struct device *dev)`.

Control flow: if the user set console explicitly on the command line, the function returns false. Otherwise it compares the device's OF node with global `of_console_device` and returns true on a match.

State and persistence: no owned state; reads `console_set_on_cmdline` and `of_console_device`.

Dependencies and integration points: used by SPARC framebuffer/video drivers to decide primary device behavior. Depends on Open Firmware device nodes and console core state.

Risks: incorrect primary detection can select the wrong framebuffer as console or override an explicit user console choice.

Test signals: boot with and without `console=`, multiple framebuffer devices, firmware console node matching, and module users of the exported symbol.
