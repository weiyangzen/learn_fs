# sources/distributed-fs/ceph-client/arch/arm64/kernel/image.h

Purpose: Supplies linker-script macros for emitting little-endian arm64 Image header fields regardless of kernel endianness.

Important macros: `DATA_LE32()` endian-swaps 32-bit fields for big-endian builds. `DEFINE_IMAGE_LE64()` splits a 64-bit link-time value into little-endian lo/hi words. `__HEAD_FLAG*` encodes endianness, page size, and physical placement flags. `HEAD_SYMBOLS` emits `_kernel_size_le` and `_kernel_flags_le`.

Control flow and state: no runtime control flow. The macros determine header fields consumed by bootloaders and kexec image validation. Splitting values avoids unsuitable absolute 64-bit relocations in PIE/KASLR builds.

Dependencies and integration: included only from the linker script, depends on `<asm/image.h>`, `PAGE_SHIFT`, `_text`, `_end`, and arm64 boot protocol flag definitions. `head.S` references the generated symbols in the Image header.

Risks and test signals: risks are wrong endian encoding, wrong page-size flag, or relocation forms incompatible with PIE. Test with big-endian and little-endian builds, 4K/16K/64K page configurations, `file`/bootloader header inspection, and kexec image loader validation.
