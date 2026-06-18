# sources/distributed-fs/ceph-client/include/linux/elfnote-lto.h

Purpose: emits a Linux ELF note indicating whether the kernel was built with LTO.

Important APIs/types/functions: `LINUX_ELFNOTE_LTO_INFO` and `BUILD_LTO_INFO`, which expands to an `ELFNOTE32("Linux", ..., 1|0)` depending on `CONFIG_LTO`.

Control flow: build/assembly code includes the macro to place a note in the kernel image; external tools can inspect the PT_NOTE data.

State/persistence: build metadata persists in the linked ELF image. No runtime state.

Dependencies/integration: `linux/elfnote.h`, linker note sections, `CONFIG_LTO`, and tooling reading vmlinux notes.

Risks/test signals: risks are missing note emission in build paths, wrong value under mixed LTO configs, and section alignment issues inherited from elfnote macros. Test with LTO on/off builds and `readelf -n` validation.
