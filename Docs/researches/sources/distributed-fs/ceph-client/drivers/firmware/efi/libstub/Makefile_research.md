# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/Makefile

Purpose: builds the EFI boot stub as freestanding, relocation-safe code for multiple architectures, with special compiler flags, object-copy rewriting, architecture object selection, and zboot support.

Important APIs/types/functions: assembles `lib-y` from generic stub helpers, architecture stubs, string/intrinsics, libfdt objects, zboot decompressors, unaccepted-memory helpers, and selected support code. It defines `KBUILD_CFLAGS`, architecture cflags, `STUBCOPY_FLAGS-*`, `STUBCOPY_RELOC-*`, and the `%.stub.o` objcopy verification rule.

Control flow: no runtime flow. Build flow removes tracing, stack protector, fortify, struct randomization, SCS, CFI, and LTO from stub builds, compiles objects as PIC/PIE as needed, imports selected `lib/` C files, prefixes/renames sections for ARM/ARM64/RISC-V/LoongArch, and checks for forbidden absolute relocations before producing `.stub.o` objects.

State and persistence behavior: build artifacts only.

Dependencies and integration points: tightly coupled to architecture image formats, EFI stub C code, libfdt, zlib/zstd decompression, binutils `objcopy`/`objdump`, and kernel linker scripts.

Risks and test signals: EFI stub code runs before normal kernel runtime support, so accidental instrumentation, absolute relocations, or wrong section flags can break boot. Test signals include successful PE/COFF boot images for each architecture, relocation check failures when absolute references appear, and zboot decompression builds for enabled algorithms.
