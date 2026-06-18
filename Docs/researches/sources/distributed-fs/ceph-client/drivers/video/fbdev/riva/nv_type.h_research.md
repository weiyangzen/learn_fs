# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/nv_type.h

## Purpose
`nv_type.h` centralizes legacy NVIDIA chipset constants as packed vendor/device IDs. It lets the driver compare `par->Chipset` against named `NV_CHIP_*` macros instead of scattering raw PCI IDs.

## Important APIs, types, and functions
The file exports preprocessor constants only. Important groups include RIVA 128/TNT/TNT2, GeForce/GeForce2/GeForce3/GeForce4 variants, Quadro variants, laptop/mobile IDs, integrated GeForce2/nForce IDs, and several raw `0x018*`/`0x028*` placeholders. It includes no functions or storage.

## Control flow
There is no runtime control flow in this header. At compile time, consumers such as `nv_driver.c` and `riva_hw.c` use these macros in switch/if logic for memory sizing, arbitration, two-head support, mobile flat-panel defaults, and integrated chipset handling.

## State and persistence behavior
No mutable state exists. The constants define the identity contract between PCI probing in `fbdev.c`, setup in `nv_driver.c`, and configuration in `riva_hw.c`.

## Dependencies and integration points
The macros depend on Linux PCI vendor/device ID definitions being available before or through including translation units. Integration points are direct equality checks against `(vendor << 16) | device`, especially `NV_CHIP_IGEFORCE2`, `NV_CHIP_0x01F0`, `NV_CHIP_GEFORCE2_GO`, and RIVA/TNT families.

## Risks and test signals
Risks are stale or mismatched PCI names, inconsistent aliases (`QUADRO_DCC` vs table naming), and missing newer variants. Test signals are successful compilation against current PCI ID headers and correct architecture/setup selection for every PCI ID in `rivafb_pci_tbl`.
