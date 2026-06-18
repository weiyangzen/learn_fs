# sources/distributed-fs/ceph-client/arch/m68k/amiga/platform.c

Purpose: Amiga platform-device registration for buses and onboard devices discovered by earlier hardware detection.

Important initcalls are `amiga_init_bus()` under `CONFIG_ZORRO` and `amiga_init_devices()`. It defines Zorro II/III memory resources, SCSI/IDE/RTC resources, and Gayle IDE platform data for A1200 and A4000 styles. Helper `z_dev_present()` scans Zorro autoconfig ROMs for board IDs.

Control flow: the Zorro bus is registered as `amiga-zorro` at `subsys_initcall` if the machine is Amiga and Zorro exists. Device init registers platform devices for video, audio, floppy, A3000/A4000 SCSI, Gayle IDE variants, keyboard, mouse, serial, parallel, and RTC chips depending on `AMIGAHW_PRESENT()` bits and Zorro card presence.

State is not long-lived in this file beyond registered `platform_device` objects and their attached resources/platform data. Resource arrays are `__initconst` where possible.

Dependencies include hardware presence state from `config.c`, Zorro autoconfig data, platform bus APIs, Gayle IDE data types, and downstream platform drivers. Integration exposes legacy Amiga hardware to normal Linux driver binding instead of direct arch probing.

Risks and test signals: resource base/size errors bind drivers to wrong registers; early return on one failed registration can suppress later devices. Test with Amiga configs covering A1200 IDE, A4000 IDE, SCSI, Zorro II/III, and RTC, checking platform devices under sysfs and driver probe logs.
