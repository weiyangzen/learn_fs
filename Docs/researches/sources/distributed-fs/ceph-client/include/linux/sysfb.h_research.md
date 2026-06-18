<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysfb.h -->
# sources/distributed-fs/ceph-client/include/linux/sysfb.h

## Purpose

`sysfb.h` declares generic system-framebuffer support, primarily for firmware-provided framebuffers on x86/EFI systems. It carries display info, DMI EFI framebuffer quirks, simplefb creation, and helpers to disable firmware framebuffers when native drivers take over.

## Important APIs, types, and functions

It defines Mac model enum IDs for EFI quirks, `struct efifb_dmi_info`, and `struct sysfb_display_info` containing `screen_info` plus optional firmware EDID. It declares global `sysfb_primary_display`. APIs include `sysfb_disable()`, `sysfb_handles_screen_info()`, EFI-specific `sysfb_apply_efi_quirks()` and `sysfb_set_efifb_fwnode()`, and simplefb helpers `sysfb_parse_mode()` and `sysfb_create_simplefb()`, with config-dependent stubs.

## Control flow

Early boot records firmware framebuffer details in `screen_info`/`sysfb_primary_display`. Sysfb code applies EFI/DMI quirks, parses mode data into `simplefb_platform_data`, creates a platform device for simplefb/simpledrm-style binding, and later native graphics drivers call `sysfb_disable()` to prevent overlapping firmware framebuffer use.

## State and persistence behavior

Primary display information persists globally after boot. Created platform devices persist in the device model until removed. EFI DMI quirks adjust screen info before device creation. Disabled sysfb state is maintained by implementation code outside this header.

## Dependencies and integration points

It depends on error pointers, simplefb platform data, `screen_info`, EDID, device and platform-device types, EFI, firmware EDID, and SYSFB/SYSFB_SIMPLEFB configs. It integrates with x86 boot graphics, EFI framebuffer, simplefb/simpledrm, and native GPU handoff.

## Risks and test signals

Risks include incorrect DMI quirks, bogus firmware mode parsing, overlapping native and firmware drivers, missing EDID, stubs returning false/`-EINVAL` in unsupported configs, and lifetime issues for fwnodes/platform devices. Tests should cover EFI framebuffer quirks, simplefb creation for common pixel formats, native driver disable handoff, no-SYSFB builds, EDID propagation, and boot on systems with invalid screen_info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysfb.h -->
