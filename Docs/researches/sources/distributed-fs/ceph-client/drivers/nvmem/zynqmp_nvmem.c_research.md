# sources/distributed-fs/ceph-client/drivers/nvmem/zynqmp_nvmem.c

Purpose: Xilinx/AMD ZynqMP firmware-backed NVMEM provider for silicon revision and eFuse/PUF user fuse access.

Important APIs/types/functions: `struct xilinx_efuse` is the DMA-shared firmware request descriptor. `zynqmp_efuse_access()` validates alignment and PUF bit restrictions, allocates coherent descriptor/data buffers, calls `zynqmp_pm_efuse_access()`, and copies read data back. `zynqmp_nvmem_read()` special-cases silicon revision through `zynqmp_pm_get_chipid()` and routes eFuse ranges to firmware. `zynqmp_nvmem_write()` permits firmware writes in eFuse ranges.

Control flow: probe registers a byte-granular NVMEM config sized to include SoC version, unused gap, and eFuse region. Reads at offset 0 return masked silicon revision; eFuse and PUF ranges call firmware; other offsets return `0xDEADBEEF`. Writes reject offsets outside eFuse/PUF ranges and otherwise call firmware with write flag.

State/persistence: eFuse writes are permanent. Driver keeps no private state beyond using `struct device` as callback context.

Dependencies/integration: OF compatible `xlnx,zynqmp-nvmem-fw`; depends on Xilinx firmware API and DMA-coherent memory allocation.

Risks: firmware error `EFUSE_NOT_ENABLED` maps to `-EOPNOTSUPP`, other firmware errors to `-EPERM`. Returning `0xDEADBEEF` for unsupported read offsets may mask bad cell definitions. PUF row bitmask restrictions are enforced only for specific offsets.

Test signals: silicon revision read size check, word alignment rejection, PUF mask rejection, firmware disabled/error paths, DMA allocation failures, and default-gap reads returning sentinel value.
