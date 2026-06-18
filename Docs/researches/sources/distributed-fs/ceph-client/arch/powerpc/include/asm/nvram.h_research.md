<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nvram.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nvram.h

## Purpose
This header declares PowerPC NVRAM partition metadata and access APIs, including persistent OS error/oops log support and PowerMac XPRAM access.

## Important APIs, Types, And Functions
It defines `OOPS_HDR_VERSION`, `struct err_log_info`, `struct nvram_os_partition`, packed `struct oops_log_info`, `oops_log_partition`, pseries `rtas_log_partition`, error-log read/write/clear APIs, `pSeries_nvram_init()`, `mmio_nvram_init()`, partition scan/create/remove/find/size APIs, PowerMac `pmac_get_partition()`, `pmac_xpram_read()`, `pmac_xpram_write()`, `nvram_init_os_partition()`, `nvram_init_oops_partition()`, `nvram_read_partition()`, and `nvram_write_os_partition()`.

## Control Flow
Platform initialization scans partitions, creates or initializes OS partitions, and later error/oops paths read or write partition payloads with error type and sequence metadata.

## State And Persistence Behavior
NVRAM contents persist across reboot. `nvram_os_partition` records desired and actual partition sizes and offsets. Oops headers include version, report length, and timestamp to distinguish formats.

## Dependencies And Integration Points
It depends on Linux types, errno/list support, UAPI NVRAM definitions, pseries RTAS, MMIO NVRAM, and PowerMac partition/XPRAM code.

## Risks And Edge Cases
Persistent storage is small and partition sizes may be below requested sizes. Endianness and packed oops headers must match readers across boots. Removing partitions must honor exception lists.

## Test Signals
Validate pseries and MMIO NVRAM init, create/find/remove partitions, write/read oops and RTAS logs across reboot, and test PowerMac XPRAM byte access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nvram.h -->
