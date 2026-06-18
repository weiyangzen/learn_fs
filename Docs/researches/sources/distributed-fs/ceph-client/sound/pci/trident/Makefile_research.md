# sources/distributed-fs/ceph-client/sound/pci/trident/Makefile

## Purpose
This Makefile defines the ALSA Trident module composition. It builds one module, `snd-trident`, from the PCI wrapper, shared hardware engine, and TLB memory allocator.

## Important APIs, types, and functions
There are no C APIs here. The key build variables are `snd-trident-y := trident.o trident_main.o trident_memory.o` and `obj-$(CONFIG_SND_TRIDENT) += snd-trident.o`. The first line defines the objects linked into the composite module; the second connects the module to the kernel configuration symbol.

## Control flow
Kbuild compiles `trident.c`, `trident_main.c`, and `trident_memory.c`, then links them into `snd-trident.o` when `CONFIG_SND_TRIDENT` is enabled as built-in or module. `trident.c` provides module metadata and PCI registration. `trident_main.c` provides most exported and internal device logic. `trident_memory.c` provides TLB allocation helpers referenced by the main implementation.

## State and persistence behavior
The Makefile has no runtime state. It controls whether the runtime state defined in the C files is present in the built kernel/module.

## Dependencies and integration points
The file depends on Linux Kbuild composite-object conventions and the `CONFIG_SND_TRIDENT` Kconfig symbol defined elsewhere. It establishes that all three source files must remain ABI-compatible within one module, including exported symbols used by other Trident-related ALSA components.

## Risks and test signals
Risks are build integration risks: removing one object would leave unresolved references such as `snd_trident_create()` or `snd_trident_alloc_pages()`, and adding objects without updating this file would omit functionality. Test signals are `make M=sound/pci/trident` or full kernel/module builds with `CONFIG_SND_TRIDENT=m/y`, plus `modinfo snd-trident` showing a single module built from these objects.
