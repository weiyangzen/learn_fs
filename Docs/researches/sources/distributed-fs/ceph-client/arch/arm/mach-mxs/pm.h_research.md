<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mxs/pm.h

Purpose: Header for MXS PM initialization. It exposes `mxs_pm_init()` when PM is enabled and an inline no-op otherwise.

Important APIs/types/functions: There are no types or runtime data; compile-time `CONFIG_PM` controls behavior.

Control flow, state, and persistence: The header integrates with the MXS machine descriptor's `.init_late` hook.

Dependencies and integration points: There are no types or runtime data; compile-time `CONFIG_PM` controls behavior. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are silent no-op behavior in non-PM builds and declaration mismatch with `pm.c`. Test compile coverage with `CONFIG_PM=y/n`.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 15 lines, 240 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/pm.h -->
