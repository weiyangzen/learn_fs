# sources/distributed-fs/ceph-client/drivers/video/fbdev/efifb.c

## Purpose
`efifb.c` is the EFI/UEFI firmware framebuffer driver. It maps firmware-provided linear framebuffer memory, exposes truecolor fbdev, arbitrates aperture ownership, and optionally restores BGRT boot graphics.

## APIs And Control Flow
`struct efifb_par` stores pseudo palette and mapped base/size. `efifb_probe()` copies `screen_info`, validates EFI origin/base/stride, applies options, computes remap size, optionally reserves memory, chooses mapping attributes from EFI memory descriptors, maps with WC/UC/WT/WB, initializes var/fix fields and rotation hint, allocates cmap, acquires the aperture, and registers fbdev. `efifb_setcolreg()` updates pseudo palette; `efifb_destroy()` unmaps/releases resources.

## State, Dependencies, Integration, Risks
Global state includes `use_bgrt`, `request_mem_succeeded`, and `mem_flags`; per-device state lives in `efifb_par` and copied `screen_info`. Dependencies include sysfb, EFI memory-map helpers, BGRT ACPI, aperture helpers, and DRM panel orientation quirks. Risks include global reservation/mapping flags in a theoretically multi-device path, cleanup size mismatch scrutiny, and BGRT BMP parsing edge cases. Tests should cover 64-bit bases, missing stride, memory attributes, DRM takeover, BGRT invalid data, and sysfs attributes.
