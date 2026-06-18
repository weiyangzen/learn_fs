# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/nvdec.c

Purpose: host1x/DRM client driver for Tegra NVDEC video decoder engines, supporting Falcon firmware on Tegra210/186/194 and RISC-V bootrom firmware descriptors on Tegra234.

Important APIs/functions: `nvdec_probe()` inherits DMA mask, maps registers, gets clocks, sets max clock rate, reads optional host1x class, initializes Falcon or RISC-V boot descriptors/carveout/reset, and registers the host1x client. `nvdec_init()/exit()` attach IOMMU, request channel/syncpoint, register/unregister DRM client, manage dma parameters, and free firmware memory. Runtime resume enables clocks and boots either RISC-V or Falcon. `nvdec_load_falcon_firmware()` allocates firmware memory via DMA API or shared Tegra DRM allocator, loads/parses firmware, and maps shared-domain memory for cache maintenance. `nvdec_boot_riscv()` runs bootloader and OS descriptors through the bootrom and waits for debug info to clear.

Control flow and state: `struct nvdec` owns Falcon/RISC-V state, MMIO, DRM client, channel, clocks, reset, SoC config, and carveout base. Userspace contexts obtain the shared channel and submit through `tegra_drm_submit`.

Dependencies/integration: integrates host1x, Tegra DRM submit/memory context, Falcon/RISC-V helpers, memory controller carveout info, runtime PM, IOMMU, clocks, reset, and stream-ID programming.

Risks: firmware allocation/free paths depend on `client->group`. RISC-V boot requires DT descriptor offsets and memory-controller carveout index 1. SID programming is SoC-dependent. Exit assumes firmware memory exists after runtime paths; failed early initialization needs correct guard behavior.

Test signals: probe on all compatibles, runtime resume boot, decode job submit, memory-context negotiation, missing firmware, bad RISC-V descriptors, stream-ID/IOMMU configurations, suspend/resume under load.
