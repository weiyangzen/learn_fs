# sources/distributed-fs/ceph-client/drivers/accel/ethosu/Kconfig

Purpose: adds the build-time configuration option for the Arm Ethos-U DRM accel driver.

Important entries: `config DRM_ACCEL_ETHOSU` is a tristate option named `ARM Ethos-U NPU` depending on `DRM_ACCEL`, `OF`, and `HAS_IOMEM`, and selecting `DRM_SCHED`, `DMA_SHARED_BUFFER`, and `GENERIC_ALLOCATOR`.

Control flow: kernel configuration enables or disables compilation of the Ethos-U platform accel driver and its support for DRM scheduler, dma-buf sharing, and SRAM gen-pool allocation.

State and persistence: no runtime state; affects build configuration and module availability.

Dependencies: DRM accel core, device tree, MMIO, scheduler, dma-buf, and generic allocator support.

Risks: missing selected dependencies would break build/link. The OF dependency means non-device-tree platforms cannot select it directly.

Test signals: `allyesconfig`, module and built-in builds, dependency-disabled configs, and device-tree platform probe with `arm,ethos-u65`/`arm,ethos-u85` compatible strings.
