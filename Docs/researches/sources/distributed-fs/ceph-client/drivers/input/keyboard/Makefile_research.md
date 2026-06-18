# sources/distributed-fs/ceph-client/drivers/input/keyboard/Makefile

Purpose: maps keyboard driver Kconfig symbols to object files compiled into the kernel or modules.

Important APIs/types/functions: this is Kbuild metadata using `obj-$(CONFIG_KEYBOARD_...) += ...o` assignments. It has no functions or runtime types.

Control flow: during kernel build, Kbuild expands each enabled `CONFIG_KEYBOARD_*` symbol and includes the matching object in the directory build. The file covers the drivers declared in Kconfig, including `adc-keys.o`, `adp5520-keys.o`, `adp5585-keys.o`, `adp5588-keys.o`, `amikbd.o`, `atkbd.o`, GPIO, matrix, many I2C/MFD keypad drivers, and SoC-specific key scanners.

State and persistence: the selected build state comes from `.config`; this Makefile does not persist runtime state. It determines whether objects are built-in, modular, or omitted.

Dependencies and integration: integrates directly with `drivers/input/keyboard/Kconfig`, module names referenced in help text, and source filenames in the same directory. Object spelling is the critical contract.

Risks: missing or stale object mappings break enabled Kconfig symbols. Symbol/object naming mismatches can confuse module help text and packaging. Since this file is broad build plumbing, unrelated edits can affect many architectures.

Test signals: build with `allmodconfig`, `allyesconfig`, and targeted configs for ADC/ADP/Amiga drivers; run `scripts/checkkconfigsymbols.py` style checks; verify each source file has a corresponding Kconfig-controlled object and each referenced object exists.
