<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/Makefile

Purpose: Build glue for Nomadik. It compiles `cpu-8815.o` when `NOMADIK_8815` is selected.

Important APIs/types/functions: The file has no functions or runtime state.

Control flow, state, and persistence: It integrates Kconfig with the legacy machine descriptor implementation.

Dependencies and integration points: The file has no functions or runtime state. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are object omission if Kconfig symbols change. Test ARCH_NOMADIK builds.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 12 lines, 347 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/Makefile -->
