<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/agent.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/agent.h

Purpose: Provides macros for accessing a hub agent's NIC/micro-LAN register on SGI SN systems.

Important APIs/types/functions: `HUB_NIC_ADDR(cpuid)`, `SET_HUB_NIC`, `SET_MY_HUB_NIC`, `GET_HUB_NIC`, and `GET_MY_HUB_NIC`.

Control flow: Code maps a CPU ID to NASID through `cputonasid`, computes the hub NIC register offset, and reads/writes it through `REMOTE_HUB_L/S` or local wrappers.

State and persistence: State is the hub NIC/micro-LAN register used for board identity and management interactions. The macros directly mutate/read hardware registers.

Dependencies and integration points: Includes SN address and architecture headers and SN0/SN1 hub variants. Depends on CPU-to-NASID mapping being initialized.

Risks: Using these macros before CPU/NASID maps are valid, or against the wrong CPU ID, targets the wrong hub. MMIO ordering and serialization are caller responsibilities.

Test signals: SN boot inventory discovery, NIC read/write diagnostics, and multi-node CPU mapping validation are useful signals.

Source read size: 45 lines, 1133 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/agent.h -->
