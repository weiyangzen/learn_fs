<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-uboot.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-uboot.h

## Purpose
Declares the U-Boot bootloader backend type.

## Important APIs and Types
Defines type/cast/check macros, opaque `OstreeBootloaderUboot`, type getter, and `_ostree_bootloader_uboot_new()`.

## Control Flow
No runtime flow; declarations only.

## State and Persistence
The implementation keeps a sysroot reference and writes bootversion-specific uEnv files.

## Dependencies and Integration Points
Includes `ostree-bootloader.h` for shared interface integration.

## Risks
Internal constructor should only be used by sysroot bootloader selection code.

## Test Signals
Compile/type checks and constructor coverage are sufficient for the header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-uboot.h -->
