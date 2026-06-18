# sources/distributed-fs/ceph-client/sound/soc/intel/Makefile

Purpose: top-level kbuild dispatch for Intel ASoC subdirectories.

Important APIs/types/functions: includes `common/` and `boards/` when `CONFIG_SND_SOC` is enabled; includes `atom/`, `catpt/`, `keembay/`, and `avs/` based on their platform config symbols.

Control flow: kbuild recurses into enabled subdirectories and builds their objects.

State and persistence: build-time only.

Dependencies/integration: maps symbols from `intel/Kconfig` to subtrees. Boards and common support are tied to the global ASoC symbol rather than platform-specific symbols.

Risks: broad inclusion of `boards/` and `common/` under `CONFIG_SND_SOC` means those subdirectories must self-gate their objects correctly. Adding new platform directories requires matching Kconfig and Makefile entries.

Test signals: build matrix across `CONFIG_SND_SOC`, CATPT, Atom, Keembay, and AVS symbols confirming correct subdirectory recursion.
