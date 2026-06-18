# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/adi/Makefile

Purpose: this Makefile connects the Analog Devices Ethernet Kconfig symbol to the actual driver object.

Important APIs, types, and functions: the only build rule is `obj-$(CONFIG_ADIN1110) += adin1110.o`, which lets kbuild include the ADIN1110 driver when the symbol is built-in or modular.

Control flow: when `CONFIG_ADIN1110=y`, `adin1110.o` is linked into the kernel image through the networking driver build. When `CONFIG_ADIN1110=m`, kbuild emits it as a module. When unset, no object in this directory is built.

State and persistence: there is no runtime state. The persistent effect is entirely in the build graph selected by `.config`.

Dependencies and integration points: it depends on the surrounding kbuild infrastructure and the `ADIN1110` symbol declared in the same directory's Kconfig. It keeps the source-tree mapping direct: `adin1110.c` compiles to `adin1110.o`.

Risks: no conditional subdirectories or composite objects exist, so the main risks are stale symbol names or missing Kconfig inclusion from the parent directory. A rename of the C file or symbol must update this line.

Test signals: `make drivers/net/ethernet/adi/` or a full kernel build should compile `adin1110.o` only when `CONFIG_ADIN1110` is enabled, and `modinfo adin1110.ko` should expose the metadata from `adin1110.c` in modular builds.
