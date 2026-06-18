<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-aboot.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-aboot.h

## Purpose
Declares the `OstreeBootloaderAboot` backend type.

## Important APIs and Types
Defines type/cast/check macros, opaque `OstreeBootloaderAboot`, type getter, and `_ostree_bootloader_aboot_new(OstreeSysroot*)`.

## Control Flow
No runtime flow; declarations only.

## State and Persistence
The implementation stores a referenced sysroot and uses a stamp file for deferred work.

## Dependencies and Integration Points
Includes `ostree-bootloader.h`, binding this backend to the shared bootloader interface.

## Risks
The constructor is internal and requires a valid loaded sysroot. Consumers should call through the interface after construction.

## Test Signals
Compile/type registration and construction tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-aboot.h -->
