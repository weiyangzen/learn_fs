# sources/distributed-fs/ceph-client/arch/powerpc/kexec/elf_64.c

## Purpose
Implements the 64-bit PowerPC ELF kernel loader for the `kexec_file_load` syscall.

## Important APIs, Types, And Functions
Defines static `elf64_load` and exports `kexec_elf64_ops` with `.probe = kexec_elf_probe` and `.load = elf64_load`.

## Control Flow
The loader parses ELF metadata, adjusts buffer placement for crash kernels, loads kernel segments, loads purgatory, adds crashdump segments and dm-crypt keys for kdump, prepends `elfcorehdr=` to the kdump command line, loads initrd if present, allocates and prepares an FDT with extra room, applies PowerPC FDT updates, optionally packs the FDT, adds it as a segment, stores it for cleanup, and initializes purgatory symbols with kernel/FDT addresses and slave code.

## State And Persistence
Mutates `struct kimage` segment arrays and architecture fields including `image->arch.fdt`, `elf_load_addr`, backup/elf headers via helpers, and purgatory symbol storage. Allocated FDT and command-line buffers are freed on cleanup or error.

## Dependencies And Integration Points
Depends on generic ELF kexec loading, purgatory loading, crashdump segment helpers, dm-crypt crash key loading, reserved memory range discovery, Open Firmware FDT setup, and `setup_new_fdt_ppc64`.

## Risks And Edge Cases
Kdump buffer ranges must stay within crashkernel/RMA constraints. FDT ownership is transferred only after segment addition; error paths must free correctly. Crash hotplug may require leaving FDT unpacked. Slave code assumes the first ELF program header contains the first 0x100 bytes.

## Test Signals
`kexec_file_load` tests with ELF kernels, initrd and no-initrd, kdump images, dm-crypt key capture, FDT inspection, error injection for segment placement, and cleanup leak checks are useful.
