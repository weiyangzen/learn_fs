<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vphn.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vphn.h

Purpose: Defines virtual processor home-node associativity buffer sizing and hcall entry point for pSeries NUMA placement updates.

Important APIs/types/functions: `VPHN_REGISTER_COUNT`, `VPHN_ASSOC_BUFSIZE`, `VPHN_FLAG_VCPU`, `VPHN_FLAG_PCPU`, and `hcall_vphn()`.

Control flow: NUMA/topology code calls `hcall_vphn(cpu, flags, associativity)` to fill an associativity array, with flags choosing guest vCPU or host CPU associativity.

State and persistence: No state is owned; output is a caller-provided big-endian associativity buffer derived from hypervisor state.

Dependencies and integration points: Integrates with PowerPC hcall implementation and pSeries topology/NUMA update code.

Risks: Buffer sizing includes an initial length cell; off-by-one handling can truncate topology information. Endianness and flag selection must match PAPR.

Test signals: pSeries NUMA boot and hotplug tests, dynamic LPAR topology updates, and hcall failure-path coverage.

Source read size: 24 lines, 802 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vphn.h -->
