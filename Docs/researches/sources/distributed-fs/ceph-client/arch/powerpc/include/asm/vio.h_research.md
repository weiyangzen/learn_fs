<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vio.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vio.h

Purpose: Declares IBM PowerPC Virtual I/O bus objects, driver registration, CMO accounting, and PFO hypercall plumbing.

Important APIs/types/functions: VIO attribute names, `h_vio_signal()`, IRQ mode constants, `struct vio_pfo_op`, `enum vio_dev_family`, `struct vio_dev`, `struct vio_driver`, `vio_register_driver()`, device/driver unregister functions, CMO helpers, `vio_h_cop_sync()`, `vio_register_device_node()`, `vio_get_attribute()`, and pSeries interrupt helpers.

Control flow: VIO drivers register a `vio_driver`, match OF-backed `vio_dev` instances, request DMA entitlement through `get_desired_dma`, and use hcalls or bus helpers for PFO operations and interrupt enable/disable.

State and persistence: Persistent state lives in each `vio_dev`: identity, unit/resource IDs, IRQ, DMA entitlement/allocated counters, failure count, family, and embedded device object.

Dependencies and integration points: Depends on Linux driver core, DMA/scatterlist APIs, module device tables, and PowerPC hcalls. Integrated by pSeries virtual Ethernet, SCSI, crypto, and platform-facility drivers.

Risks: CMO accounting must match DMA usage or allocation can fail under constrained memory. Hypercall parameters are logical real addresses, so bad translation or length signs can corrupt firmware operations.

Test signals: pSeries VIO device probe/remove, DMA entitlement update tests, virtual Ethernet/storage I/O, PFO hcall error-path testing, and non-pSeries compile stubs.

Source read size: 163 lines, 4649 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vio.h -->
