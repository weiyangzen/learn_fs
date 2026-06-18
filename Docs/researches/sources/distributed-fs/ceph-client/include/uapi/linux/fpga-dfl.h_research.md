# sources/distributed-fs/ceph-client/include/uapi/linux/fpga-dfl.h

This UAPI header defines the ioctl ABI for Intel/DFL-based FPGA devices. It covers common API version/extension checks, AFU port reset and region discovery, DMA map/unmap, eventfd-backed interrupts, and FME partial reconfiguration plus port assignment/release and error IRQs.

Important exports include `DFL_FPGA_API_VERSION`, `DFL_FPGA_MAGIC`, base ranges `DFL_FPGA_BASE`, `DFL_PORT_BASE`, `DFL_FME_BASE`, common ioctls `DFL_FPGA_GET_API_VERSION` and `DFL_FPGA_CHECK_EXTENSION`, AFU ioctls `DFL_FPGA_PORT_RESET`, `PORT_GET_INFO`, `PORT_GET_REGION_INFO`, `PORT_DMA_MAP`, `PORT_DMA_UNMAP`, port error/UINT IRQ get/set commands, and FME commands `DFL_FPGA_FME_PORT_PR`, `PORT_RELEASE`, `PORT_ASSIGN`, and FME error IRQ get/set. Key structs include `dfl_fpga_port_info`, `dfl_fpga_port_region_info`, `dfl_fpga_port_dma_map`, `dfl_fpga_port_dma_unmap`, `dfl_fpga_irq_set`, and `dfl_fpga_fme_port_pr`.

Control flow is ioctl and mmap/eventfd based: userspace opens an AFU or FME fd, checks API support, discovers regions, mmaps device regions, maps user pages for DMA to obtain IOVAs, binds eventfds to interrupts, resets ports, or asks FME to partially reconfigure a port. State lives in DFL device drivers, IOMMU mappings, FPGA manager state, port ownership, interrupt routing, and eventfd references. Persistence can include FPGA programmed image/port assignment until reset or reconfiguration.

Dependencies include `linux/types.h`, `linux/ioctl.h`, eventfd, IOMMU/DMA mapping, FPGA manager, and DFL bus drivers. Integration points include OPAE-like userspace, VFIO-inspired ABI design, hardware accelerators, and platform management tools.

Risks include DMA mapping of unpinned or misaligned memory, stale IOVA unmap bugs, eventfd lifetime mistakes, destructive resets during DMA/partial reconfiguration, ABI extension handling through `argsz`/flags, and privilege boundaries around FME controls. Test signals include DFL driver selftests, ioctl struct size/flags validation, DMA map/unmap stress, eventfd interrupt tests, partial reconfiguration failure tests, and IOMMU fault handling.
