## sources/distributed-fs/ceph-client/arch/arm64/include/asm/image.h

Purpose: defines the arm64 kernel Image header layout and flag encodings.

Important APIs/types/functions: defines `ARM64_IMAGE_MAGIC`, image flag shifts/masks/values for endianness, page size, and physical base, `arm64_image_flag_field`, and `struct arm64_image_header`.

Control flow: bootloaders and EFI stub read the fixed header fields to place and launch the kernel image.

State and persistence: header data is embedded in the kernel Image and consumed before normal kernel execution.

Dependencies and integration: used by boot protocol, EFI stub, decompression/image tooling, and external bootloaders.

Risks: layout changes break bootloader ABI. Test signals are image header inspection, EFI and non-EFI boot tests, big/little endian builds, and page-size variant boots.
