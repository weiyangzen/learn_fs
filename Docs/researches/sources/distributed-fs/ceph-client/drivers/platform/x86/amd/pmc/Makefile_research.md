# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/Makefile

Purpose: this Makefile builds the AMD PMC composite object.

Important APIs, types, and functions: `amd-pmc-y` contains `pmc.o`, `pmc-quirks.o`, and `mp1_stb.o`; `amd-pmc-$(CONFIG_AMD_MP2_STB)` conditionally adds `mp2_stb.o`.

Control flow: kbuild links one module/object named `amd-pmc` when `CONFIG_AMD_PMC` is enabled, with optional MP2 STB code.

State and persistence: build-only state.

Dependencies and integration points: maps PMC Kconfig symbols to implementation files and ensures quirk and MP1 STB support are always present with PMC.

Risks: because STB and quirks are linked unconditionally into PMC, their symbols and module parameters are always present when PMC is present. Optional MP2 paths must compile out cleanly.

Test signals: build with `AMD_MP2_STB=y` and disabled; check that `stb_read_previous_boot` debugfs support appears only with MP2 STB compiled.
