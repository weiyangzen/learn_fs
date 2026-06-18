<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/Makefile

Purpose: build glue for Intel AVS machine driver modules.

Important APIs, types, and functions: defines per-module object variables such as `snd-soc-avs-da7219-y := da7219.o` and maps Kconfig symbols to module objects through `obj-$(CONFIG_SND_SOC_INTEL_AVS_MACH_*)`.

Control flow: Kbuild includes each module object only when its corresponding Kconfig symbol is enabled. Each source currently builds as a single-object module with the `snd-soc-avs-*` module name.

State and persistence: no runtime state. The persistent output is kernel objects/modules named according to the Makefile variables.

Dependencies and integration points: must stay aligned with `boards/Kconfig`, platform driver names inside each `.c` file, and platform devices registered by `board_selection.c`.

Risks: adding a board only in `Kconfig` or only in this Makefile silently prevents the expected module from building. Case sensitivity matters for `MAX98357A` Kconfig versus `snd-soc-avs-max98357a` object naming.

Test signals: `make M=sound/soc/intel/avs/boards` builds the expected modules, and enabled configs produce matching `snd-soc-avs-*.ko` artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/Makefile -->
