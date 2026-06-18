<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00460_evcnt_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00460_evcnt_memmap_package.h

Purpose: Register map for a small FPGA event counter block used by Cobalt input/output paths.

Important APIs/types: `struct m00460_evcnt_regmap` exposes `control` and `count`. Masks define enable and clear bits.

Control flow: Capture start and DMA start clear/enable the counter. Stop disables it. Log-status can read related counts from other blocks.

State/persistence: Counter value is hardware runtime state, reset by clear bit or hardware reset.

Dependencies/integration: Used through `COBALT_CVI_EVCNT()` in V4L2 streaming setup and stop paths.

Risks: Counter semantics depend on FPGA event source; missed clear/enable ordering can produce stale diagnostics.

Test signals: Counter increments during streaming, resets on stream start, and disables on stream stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00460_evcnt_memmap_package.h -->
