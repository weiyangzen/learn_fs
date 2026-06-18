<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-syslinux.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-syslinux.h

## Purpose
Declares the syslinux bootloader backend type.

## Important APIs and Types
Defines type/cast/check macros, opaque `OstreeBootloaderSyslinux`, type getter, and `_ostree_bootloader_syslinux_new()`.

## Control Flow
No runtime control flow in the header.

## State and Persistence
Implementation state is a referenced sysroot; persistent state is generated syslinux config.

## Dependencies and Integration Points
Includes `ostree-bootloader.h` and participates in the generic bootloader interface.

## Risks
Constructor is internal and assumes sysroot state is initialized enough for query/write.

## Test Signals
Type registration and constructor tests validate the declaration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-syslinux.h -->
