# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-amigaone.c

## Purpose
Old U-Boot compatibility wrapper for AmigaOne.

## Important APIs, Types, And Control Flow
`platform_init()` copies board info using `CUBOOT_INIT()`, initializes the embedded DTB, starts serial console, and installs `platform_fixups()`. The fixup writes memory and CPU/timebase/bus clocks from U-Boot board info.

## State, Dependencies, Risks, And Tests
State is copied `bd_t`, loader metadata, allocator state, and FDT memory/clock properties. Dependencies include AmigaOne-compatible `ppcboot.h` fields and serial console availability. Risks include sparse fixups that do not correct MAC or bus child clocks, and old firmware board-info inaccuracies. Test with `cuImage.amigaone`, DT memory/clock validation, and serial output before kernel entry.
