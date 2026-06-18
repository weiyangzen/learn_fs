<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/addrs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/addrs.h

Purpose: Defines SGI SN physical/virtual address construction macros for node address spaces, small/big windows, aliases, PROM/kernel layout, hub register access, and KLDIR-derived firmware areas.

Important APIs/types/functions: NASID helpers `NASID_GET_META`, `NASID_GET_LOCAL`, `NASID_MAKE`; node base helpers `NODE_CAC_BASE`, `NODE_IO_BASE`, `TO_NODE_*`; window helpers `RAW_NODE_SWIN_BASE`, `NODE_SWIN_ADDR`, `WIDGETID_GET`; alias and boot areas `UALIAS_*`, `LBOOT_*`, `RBOOT_*`; backdoor directory/ECC helpers; hub access `LOCAL_HUB_L/S`, `REMOTE_HUB_L/S`; KLDIR accessors `KLD_*`, `LAUNCH_ADDR`, `NMI_ADDR`, `KLCONFIG_ADDR`, `GDA_ADDR`, and `NODE_OFFSET_TO_K0/K1`.

Control flow: SN code constructs addresses by combining NASID/node offsets with architectural base segments, translates between local/remote node offsets, then uses raw 64-bit hub accessors to read/write registers. Firmware table macros derive launch/NMI/KLCONFIG/GDA locations from KLDIR entries.

State and persistence: The header maps persistent hardware and firmware state: per-node memory windows, hub registers, PROM-reserved areas, backdoor directory memory, and KLDIR entries. The access macros directly perform MMIO reads/writes.

Dependencies and integration points: Depends on Linux SMP/types, MIPS address-space macros, `asm/sn/kldir.h`, and SN0/SN1 address variants. Integrated across IP27/SN platform boot, interrupt, memory, and firmware-discovery code.

Risks: Address composition is highly architecture-specific; a wrong NASID or segment base can cause remote memory/register corruption. Hub accessors are raw and require correct ordering from callers.

Test signals: IP27/SN boot, KLDIR parsing, remote hub register access, NUMA node discovery, and memory-window mapping tests are relevant.

Source read size: 377 lines, 12909 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/addrs.h -->
