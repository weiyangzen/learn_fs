<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sparsemem.h

Purpose: Defines the maximum physical memory address width for MIPS sparsemem support.

Important APIs/types/functions: `MAX_PHYSMEM_BITS` set to 48.

Control flow: Memory model code uses the constant at compile time to size sparsemem section addressing.

State and persistence: No runtime state; it constrains memory model limits.

Dependencies and integration points: Included by Linux sparsemem/mm configuration code for MIPS.

Risks: Changing the bit width changes memory hotplug/sparsemem sizing assumptions and can break high-physical-address platforms.

Test signals: MIPS sparsemem builds, boot on high-memory/NUMA systems, and memory hotplug coverage are relevant.

Source read size: 18 lines, 486 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sparsemem.h -->
