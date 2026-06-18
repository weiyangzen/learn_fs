# sources/distributed-fs/ceph-client/include/uapi/linux/nubus.h

Purpose: Publishes NuBus category, type, driver software/hardware, and ROM resource IDs for old Macintosh NuBus drivers and userspace tooling.

Important APIs/types/functions: Defines `enum nubus_category`, network/display/CPU type enums, `enum nubus_drsw`, `enum nubus_drhw`, `enum nubus_res_id`, and category-specific resource ID enums for board, vendor, network, CPU, and display resources. Constants identify display cards, SONIC Ethernet variants, CPU boards, ROM directories, MAC address records, and display mode resources.

Control flow: No executable flow. Kernel NuBus probing and drivers match ROM tuples such as category/type/DrSW/DrHW and walk resource directories using these IDs. Userspace diagnostic tools can use the same constants to decode ROM contents.

State and persistence behavior: The header describes persistent firmware ROM metadata on NuBus cards. It does not store state; matched devices and parsed ROM data live in bus/device structures at runtime.

Dependencies and integration points: Depends on `<linux/types.h>`. Integrates with m68k Macintosh NuBus bus code, framebuffer and network drivers, and historical ROM inspection tooling.

Risks: Some cards misidentify themselves, as noted by comments, so consumers must avoid over-trusting DrHW values. Numeric IDs are ABI and historical hardware documentation; reusing or renumbering them would break drivers and tooling.

Test signals: Decode known NuBus ROMs, match documented Ethernet and framebuffer tuples, verify resource directory parsing for vendor/MAC/display modes, and compile m68k NuBus drivers against the UAPI header.
