<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/Makefile

## Purpose
`rm/Makefile` builds the 32-bit ELF real-mode image, relocation table, and final `realmode.bin` consumed by the kernel.

## Important APIs, types, and functions
Targets include `realmode.elf`, `realmode.bin`, `realmode.relocs`, generated `pasyms.h`, and `realmode.lds`. Object groups include `header.o`, `trampoline_$(BITS).o`, `stack.o`, `reboot.o`, and ACPI wakeup/video objects under `CONFIG_ACPI_SLEEP`.

## Control flow
Kbuild first extracts physical-address symbols with `nm | sed`, preprocesses the linker script, links an `elf32-i386` image with relocations, runs `arch/x86/tools/relocs --realmode`, and objcopies the binary blob.

## State and persistence behavior
It persists generated build artifacts only. The order of video objects is encoded as build state because VGA must be probed before VESA and BIOS fallback.

## Dependencies and integration points
It depends on real-mode compiler flags from the parent makefile, `arch/x86/tools/relocs`, `nm`, `ld`, `objcopy`, and boot include paths for shared 16-bit code.

## Risks and edge cases
Object order and relocation generation are high-risk: missing `pasyms.h`, wrong `BITS`, or omitted `--emit-relocs` breaks `init.c` relocation. Real-mode C flags must avoid unsupported unwind metadata.

## Test signals
Signals are successful generation of `realmode.bin`/`realmode.relocs`, no unsupported relocations from `relocs`, and resume/reboot paths using the generated blob.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/Makefile -->
