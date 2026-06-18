## `sources/distributed-fs/ceph-client/drivers/pinctrl/spear/Makefile`

Purpose: Kbuild object list for SPEAr pinctrl drivers.

Important APIs/types/functions: `obj-y += pinctrl-spear.o` builds the common SPEAr helper whenever this directory is included. Conditional objects include `pinctrl-plgpio.o`, `pinctrl-spear3xx.o`, and SoC files for SPEAr300/310/320/1310/1340 according to Kconfig symbols.

Control flow: no runtime flow. Build inclusion is controlled by `CONFIG_PINCTRL_SPEAR_*` symbols.

State and persistence: no runtime state; it affects the kernel image contents.

Dependencies and integration: ties Kconfig to source files in this directory. Because common `pinctrl-spear.o` is unconditional within the directory, directory-level inclusion must already be constrained by higher-level Makefiles/Kconfig. Risks include stale object entries if SoC files are removed, unconditional common object build without matching platform data in unusual build combinations, and limited compile-test if the directory is not entered. Test signals include SPEAr platform builds and verifying each selected SoC symbol pulls exactly its common prerequisites.
