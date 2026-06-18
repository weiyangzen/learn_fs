<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood.c

Purpose: Device-tree machine initialization for Marvell Kirkwood. It registers cpufreq/cpuidle platform devices, patches Ethernet MAC addresses from controller registers, applies an MBUS error-propagation workaround, initializes PM, and populates DT devices.

Important APIs/types/functions: Important functions are `kirkwood_cpufreq_init`, `kirkwood_cpuidle_init`, `kirkwood_dt_eth_fixup`, `kirkwood_disable_mbus_error_propagation`, and `kirkwood_dt_init`; the machine descriptor is `KIRKWOOD_DT`.

Control flow, state, and persistence: Control flow starts at `kirkwood_dt_init`, performs legacy board fixes before `of_platform_default_populate`, and then registers CPU power helpers. The Ethernet fixup dynamically allocates a `local-mac-address` DT property when firmware left it unset.

Dependencies and integration points: Important functions are `kirkwood_cpufreq_init`, `kirkwood_cpuidle_init`, `kirkwood_dt_eth_fixup`, `kirkwood_disable_mbus_error_propagation`, and `kirkwood_dt_init`; the machine descriptor is `KIRKWOOD_DT`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT, clk, of_iomap, mv643xx Ethernet register layout, MBUS bridge registers, Feroceon L2, common MVEBU helpers, and Kirkwood PM. Risks include leaked properties by design, clock/map failures skipping MAC repair, and SoC-specific register assumptions. Test boot on boards with and without DT MACs, cpufreq/cpuidle probe, MBUS workaround, and standby.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 192 lines, 4712 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood.c -->
