<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hub.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hub.h

Purpose: Aggregates SN0 hub register definitions and provides small hub identity/attribute helpers.

Important APIs/types/functions: `HUB_PASSWORD`, chip/revision constants, `MAX_HUB_PATH`, included subheaders `hubpi.h`, `hubmd.h`, `hubio.h`, `hubni.h`, uncached attribute constants `UATTR_*`, and inline `get_nasid()`.

Control flow: SN0 code includes this umbrella header to access PI/MD/IIO/NI registers and to read the current hub NASID from the local network status register.

State and persistence: State is hub hardware revision, identity, and current node ID in hub registers. No software state is allocated.

Dependencies and integration points: Depends on SN0 address, processor-interface, memory-directory, I/O, and network-interface headers.

Risks: `get_nasid()` relies on local hub access being valid. Including this header brings many low-level MMIO macros into scope, increasing compile coupling.

Test signals: SN0 boot, NASID discovery, hub revision detection, and compile coverage for all hub subheaders are useful.

Source read size: 62 lines, 1428 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hub.h -->
