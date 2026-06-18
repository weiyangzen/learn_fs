<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mxs/Makefile

Purpose: Build glue for Freescale MXS machine support. It compiles suspend support when PM is enabled and the DT machine file when `ARCH_MXS` is selected.

Important APIs/types/functions: Targets are `pm.o` and `mach-mxs.o`.

Control flow, state, and persistence: No runtime state exists; the file only controls object inclusion.

Dependencies and integration points: Targets are `pm.o` and `mach-mxs.o`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are simple Kconfig/object mismatches. Test MXS builds with PM on and off.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 3 lines, 102 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/Makefile -->
