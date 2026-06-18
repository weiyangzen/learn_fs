# sources/distributed-fs/ceph-client/arch/parisc/kernel/kexec_file.c

## Purpose

`kexec_file.c` provides `kexec_file_load` support for PA-RISC ELF kernels. It loads an ELF vmlinux image, converts segment addresses to physical addresses, adds optional initrd and command-line buffers, and registers the loader in the architecture loader list.

## Important APIs, Types, And Functions

`elf_load()` is the loader implementation used by `kexec_elf_ops`. It uses generic helpers `kexec_build_elf_info()`, `kexec_elf_load()`, and `kexec_add_buffer()`. `kexec_file_loaders[]` advertises `kexec_elf_ops` as the supported file loader.

## Control Flow

`elf_load()` builds ELF metadata from the kernel buffer, asks the generic ELF loader to place loadable segments, sets `image->start` to the physical entry address, and converts each segment `mem` value with `__pa()`. If an initrd is supplied, it appends it as a page-aligned buffer and records `image->arch.initrd_start` and `image->arch.initrd_end`. If a command line is supplied, it adds an aligned buffer below the kernel load address but above `PAGE0->mem_free + PAGE_SIZE`, then records `image->arch.cmdline`.

The function returns `NULL` regardless of success or failure; the generic kexec file loader tracks errors through the `ret` path before `out`.

## State And Persistence Behavior

The file mutates `struct kimage`: `start`, segment physical addresses, and PA-RISC arch fields for initrd and command line. No persistent storage is used.

## Dependencies And Integration Points

It depends on generic ELF kexec support, libfdt/of headers included for common kexec-file infrastructure, page alignment, physical-address conversion, and page-zero free-memory boundaries. The values it fills are consumed later by `machine_kexec()`.

## Risks

Address conversion must match what `machine_kexec()` and the relocation stub expect. The command-line placement constraints assume `PAGE0->mem_free` is a safe lower bound and `kernel_load_addr` is a safe upper bound. Returning `NULL` means reviewers must inspect generic API expectations carefully when changing error handling.

## Test Signals

Signals include `kexec_file_load` accepting valid PA-RISC ELF kernels, rejecting malformed ELFs through generic helpers, preserving initrd and command-line addresses into the second kernel, and no segment-address mismatch in `machine_kexec()` debug output.
