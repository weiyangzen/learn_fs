# sources/distributed-fs/ceph-client/include/drm/amd/isp.h

Purpose: declares AMD ISP platform data and buffer allocation/free helpers shared between AMD GPU/ISP components.

Important APIs, types, and flow: `struct isp_platform_data` passes an AMD device pointer, ASIC type, and base RMMIO size to ISP platform code. User-buffer helpers import/allocate around a DMA-BUF-like object and return an opaque buffer object plus GPU address. Kernel-buffer helpers allocate/free device-accessible memory and return opaque object, GPU address, and CPU mapping.

State and persistence: buffer state is represented by opaque `buf_obj` handles managed by implementation code. Allocations are runtime-only and must be released with the matching free helper.

Dependencies and integration: depends on Linux device and resource-size types, AMD ASIC typing, DMA-BUF/GPU memory management implementation, and DRM AMD drivers.

Risks and test signals: risks include mismatched alloc/free paths, stale GPU addresses, CPU mapping lifetime, and imported user-buffer pinning. Signals include ISP probe tests, user buffer import/free tests, kernel buffer allocation/free leak checks, IOMMU/DMA mapping tests, and ASIC-type dispatch coverage.
