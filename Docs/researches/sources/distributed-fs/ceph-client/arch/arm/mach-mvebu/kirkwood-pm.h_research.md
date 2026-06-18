<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood-pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood-pm.h

Purpose: Small conditional header for Kirkwood PM initialization. It lets Kirkwood machine setup call PM code unconditionally while compiling to a no-op when `CONFIG_PM` is disabled.

Important APIs/types/functions: The visible API is `kirkwood_pm_init()`, either declared for the PM object or defined as an inline empty function.

Control flow, state, and persistence: There is no runtime state in the header. Its behavior is compile-time selection through Kconfig.

Dependencies and integration points: The visible API is `kirkwood_pm_init()`, either declared for the PM object or defined as an inline empty function. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: The main risk is silent loss of suspend registration when PM is disabled or the header guard/API diverges from `kirkwood-pm.c`. Test by building Kirkwood with and without `CONFIG_PM`.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 18 lines, 403 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood-pm.h -->
