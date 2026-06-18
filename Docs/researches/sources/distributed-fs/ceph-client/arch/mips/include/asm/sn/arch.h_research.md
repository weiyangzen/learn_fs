<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/arch.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/arch.h

Purpose: Defines common SGI SN architecture identity helpers and invalid sentinel values.

Important APIs/types/functions: `cputonasid(cpu)`, `cputoslice(cpu)`, and invalid sentinels `INVALID_NASID`, `INVALID_PNODEID`, `INVALID_MODULE`, `INVALID_PARTID`.

Control flow: Callers index `sn_cpu_info` to convert Linux CPU numbers into SN NASID/slice coordinates used for hub access and interrupt routing.

State and persistence: The header reads `sn_cpu_info` but does not define it. The state is platform CPU topology discovered during boot.

Dependencies and integration points: Depends on `asm/sn/types.h` and SN0 architecture constants. Integrated by nearly all SN platform code needing CPU-to-node translation.

Risks: Macros assume `sn_cpu_info` is populated and CPU indices are valid. Invalid sentinels are typed casts and must not be confused with valid signed IDs.

Test signals: SN CPU discovery, NUMA topology reporting, and SMP boot on IP27 are the key signals.

Source read size: 28 lines, 762 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/arch.h -->
