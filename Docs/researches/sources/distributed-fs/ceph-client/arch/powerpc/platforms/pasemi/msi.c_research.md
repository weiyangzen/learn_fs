# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/msi.c

Purpose: PA Semi MPIC-backed MSI allocation and PCI controller MSI callbacks.

Important APIs and control flow: the MSI chip combines PCI MSI masking with MPIC masking/unmasking and uses MPIC EOI/type/affinity operations. `pasemi_msi_setup_msi_irqs` allocates hardware interrupts in 16-vector chunks from the MPIC MSI bitmap, creates virq mappings, associates MSI descriptors, programs vector zero, sets edge-rising type, and writes an MSI message targeting address `0xfc080000` with data `hwirq - 0x200`. Teardown clears descriptors, disposes mappings, and frees chunks. `mpic_pasemi_msi_init` validates the MPIC compatible string, initializes the allocator, saves the MPIC, and installs callbacks on all PHBs.

State, dependencies, and risks: state is global `msi_mpic`, MPIC MSI bitmap allocations, and PHB controller callbacks. Dependencies include MPIC MSI allocator, PCI MSI core, irqdomain mapping, and PA Semi MSI address/data semantics. Risks include fixed 16-vector allocation granularity, MSI-X noted as untested, callback installation over existing hooks, and teardown freeing whole chunks per descriptor. Test signals are MSI allocation/free under PCI devices, interrupt delivery at the magic address, affinity grouping, and no bitmap leaks after driver removal.
