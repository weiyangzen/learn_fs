<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-grub2.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-grub2.h

## Purpose
Declares the GRUB2 bootloader backend and its config-generation helper.

## Important APIs and Types
Defines `OSTREE_TYPE_BOOTLOADER_GRUB2`, cast/check macros, opaque `OstreeBootloaderGrub2`, type getter, `_ostree_bootloader_grub2_new()`, and `_ostree_bootloader_grub2_generate_config()`.

## Control Flow
No implementation flow; the header exposes the constructor and generator entry point used by private command glue.

## State and Persistence
The backend implementation owns sysroot and detected config path state. The generator writes GRUB text to a supplied target fd.

## Dependencies and Integration Points
Includes `ostree-bootloader.h`. `_ostree_bootloader_grub2_generate_config()` is exported internally through `ostree_cmd__private__()` for the command-side generator.

## Risks
Callers of the generator must provide the environment expected by the implementation. The backend should be consumed through the shared interface except for the generator hook.

## Test Signals
Compile/link coverage and generator invocation through the private vtable validate this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-grub2.h -->
