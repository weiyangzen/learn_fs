<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-zipl.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-zipl.h

## Purpose
Declares the zIPL bootloader backend type.

## Important APIs and Types
Defines type/cast/check macros, opaque `OstreeBootloaderZipl`, type getter, and `_ostree_bootloader_zipl_new()`.

## Control Flow
No runtime flow in the header.

## State and Persistence
Implementation state is a sysroot reference; persistent backend state is the zipl update stamp and external zipl-installed boot state.

## Dependencies and Integration Points
Includes `ostree-bootloader.h` and integrates with the generic bootloader interface.

## Risks
Internal constructor should only be used in bootloader selection with an initialized sysroot.

## Test Signals
Type registration, constructor coverage, and interface cast checks validate the declaration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-zipl.h -->
