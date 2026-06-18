# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-52xx.c

## Purpose
Compatibility wrapper for old non-device-tree-aware U-Boot on MPC5200 systems.

## Important APIs, Types, And Control Flow
`platform_init()` copies U-Boot `bd_t` via `CUBOOT_INIT()`, initializes the embedded DTB and serial console, and installs `platform_fixups()`. The fixup updates memory, MAC address, CPU/timebase/bus clocks, finds the SoC node by devtype or compatible string, writes IPB bus frequency, translates SoC registers, reads the divider at offset `0x204`, and writes `system-frequency`.

## State, Dependencies, Risks, And Tests
State is copied board info, loader info from `cuboot_init()`, allocator state, and FDT properties. Dependencies include MPC52xx `ppcboot.h` layout, device-tree helper APIs, and MMIO accessors. Risks include DT node name/compatible mismatch, incorrect divider detection, endian of `bd_t` fields, and invalid translated SoC register. Test with MPC5200/MPC5200B DTBs, old U-Boot initrd/cmdline inputs, and FDT memory/clock/MAC validation.
