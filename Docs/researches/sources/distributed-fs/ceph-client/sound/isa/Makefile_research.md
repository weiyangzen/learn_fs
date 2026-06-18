## sources/distributed-fs/ceph-client/sound/isa/Makefile

Purpose: maps top-level ISA ALSA Kconfig symbols to module objects and descends into ISA card-family subdirectories.

Important APIs, types, and functions: object lists `snd-adlib-y`, `snd-als100-y`, `snd-azt2320-y`, `snd-cmi8328-y`, `snd-cmi8330-y`, `snd-es18xx-y`, `snd-opl3sa2-y`, `snd-sc6000-y`, `snd-sscape-y`, and `obj-$(CONFIG_...)` entries plus unconditional `obj-$(CONFIG_SND)` subdirectory traversal.

Control flow: selected simple ISA drivers build from one C object each. When ALSA is enabled, subdirectories for AD1816A, AD1848, CS423x, ES1688, Galaxy, GUS, MSND, OPTi9xx, SB, Wavefront, and WSS are visited, where their own Makefiles gate objects by card configs.

State and persistence: no runtime state; it encodes build composition.

Dependencies and integration points: follows Kconfig definitions in the same directory and lower-level Makefiles. It ties module names from help text to generated `snd-*` objects.

Risks: unconditional subdirectory traversal under `CONFIG_SND` relies on child Makefiles to avoid building disabled cards. Adding a top-level card requires updating both Kconfig and this Makefile. Line continuation must remain syntactically correct.

Test signals: targeted module builds for every top-level ISA symbol, `make M=sound/isa`, and checking that disabled child directories produce no unintended objects.
