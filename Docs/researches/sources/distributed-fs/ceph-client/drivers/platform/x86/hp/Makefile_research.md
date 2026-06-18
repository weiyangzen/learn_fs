# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/Makefile

Purpose: maps HP x86 platform Kconfig symbols to build objects in `drivers/platform/x86/hp`.

Important APIs/types/functions: build entries compile `hp_accel.o`, `hp-wmi.o`, `tc1100-wmi.o`, and descend into `hp-bioscfg/` when `CONFIG_HP_BIOSCFG` is enabled.

Control flow: there is no runtime behavior. Kbuild evaluates `obj-$(CONFIG_...)` lines to select objects or subdirectories.

State and persistence: no runtime state. The file participates in reproducible build graph generation based on `.config`.

Dependencies and integration: this is the folder-level Kbuild integration point for the HP drivers whose feature gates are declared in the adjacent `Kconfig`.

Risks and test signals: if object names diverge from module names or symbols, modular builds fail. Build tests should include HP symbols as modules and built-in. `hp-bioscfg/` owns its internal object composition, so this file should only point at the subdirectory.
