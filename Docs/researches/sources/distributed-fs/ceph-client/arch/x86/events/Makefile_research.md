## sources/distributed-fs/ceph-client/arch/x86/events/Makefile

Purpose: top-level Kbuild aggregation for x86 perf-event support.

Important build objects: core `core.o probe.o utils.o`, optional `rapl.o`, AMD subdirectory, `msr.o` under local APIC, Intel subdirectory, and Zhaoxin/Centaur support.

Control flow: object inclusion follows architecture perf configuration and CPU vendor options.

State/persistence: produces perf-event kernel objects and subdirectory builds.

Integration points: Kconfig options, AMD/Intel event drivers, local APIC perf interrupt support, and generic perf core.

Risks: missing object inclusion breaks PMU registration. Test signals include vendor-specific builds, perf list on boot, and local APIC enabled/disabled configurations.
