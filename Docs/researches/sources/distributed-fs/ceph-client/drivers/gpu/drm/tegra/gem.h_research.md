# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gem.h

Purpose: declares Tegra GEM buffer object types, tiling metadata, conversion helpers, and public GEM/PRIME/mmap APIs.

Important APIs/types: `struct tegra_bo` embeds `drm_gem_object` and `host1x_bo` and stores flags, sg table, IOVA, CPU mapping, imported dma-buf, DRM MM node, pages, mapped size, and tiling. `enum tegra_bo_tiling_mode` and `enum tegra_bo_sector_layout` describe pitch/tiled/block layouts and Tegra-vs-GPU sector layout. Inline `to_tegra_bo()` and `host1x_to_tegra_bo()` are used throughout display and submit code.

Control flow and state: the header documents four memory-source/mapping combinations and the fields valid for each. That table is the practical contract for `gem.c`, display plane pinning, and host1x submission.

Dependencies/integration: includes host1x and DRM GEM headers and exports functions used by framebuffer, fbdev, plane, and driver IOCTL paths.

Risks: consumers must not assume every BO has both `pages` and `vaddr`; the allocation mode controls valid fields. `TEGRA_BO_BOTTOM_UP` is a Tegra-local flag interpreted by framebuffer/display code.

Test signals: build coverage plus tests crossing all four allocation/import modes are the meaningful validation.
