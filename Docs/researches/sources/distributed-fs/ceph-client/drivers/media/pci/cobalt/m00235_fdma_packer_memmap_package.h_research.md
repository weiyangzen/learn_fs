<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00235_fdma_packer_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00235_fdma_packer_memmap_package.h

Purpose: Register map for the FPGA FDMA packer block that converts video bus pixels into DMA memory packing formats.

Important APIs/types: `struct m00235_fdma_packer_regmap` contains a single `control` register. Macros define enable, two-bit pack-format selector, and endian-format bit.

Control flow: `cobalt_enable_input()` writes the control register for YUYV, RGB24, or BGR32 capture formats before streaming.

State/persistence: The control register persists in hardware until changed or reset.

Dependencies/integration: Used by Cobalt V4L2 format setup and log-status through `COBALT_CVI_PACKER()`.

Risks: Pack-format values are encoded by shifts in the caller rather than named enum constants; mismatches with FPGA definitions would corrupt captured pixel layout.

Test signals: Capture in YUYV/RGB24/BGR32, bytesperline correctness, color channel order validation, and log-status packer control value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00235_fdma_packer_memmap_package.h -->
