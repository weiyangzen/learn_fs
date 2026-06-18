<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/types.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/types.h

Purpose: Defines SGI SN-specific scalar identifier types used across topology, partition, module, and hardware graph code.

Important APIs/types/functions: `cpuid_t`, `nasid_t`, `partid_t`, `moduleid_t`, and `vertex_hdl_t`.

Control flow: These typedefs are used to make SN topology and inventory code explicit about CPU, node, partition, module, and hardware graph handles.

State and persistence: No state is stored; the file standardizes type widths and signedness.

Dependencies and integration points: Depends on Linux types for `dev_t`. Included by SN architecture, KLCONFIG, launch, and kernel-vars headers.

Risks: Changing signedness or width breaks sentinel values and firmware structure layout.

Test signals: Build coverage and struct-layout checks in SN headers are sufficient.

Source read size: 25 lines, 687 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/types.h -->
