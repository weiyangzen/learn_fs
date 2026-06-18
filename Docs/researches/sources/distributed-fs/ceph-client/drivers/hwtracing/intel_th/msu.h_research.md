
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/msu.h

Purpose: MSU/MSC register offsets, bit definitions, multiblock descriptor layout, and descriptor helper routines.

Important APIs/types/functions: defines MSU global and MSC0/MSC1 offsets, status/control bits (`MSC_EN`, `MSC_WRAPEN`, `MSC_MODE`, `MSC_LEN`, `MSCSTS_PLE`, interrupt bits), `struct msc_block_desc`, descriptor size constants, software/hardware tag bits, and helpers `msc_data_sz()`, `msc_total_sz()`, `msc_block_sz()`, `msc_block_wrapped()`, and `msc_block_last_written()`.

Control flow: no standalone execution. `msu.c` uses the constants to program capture and interpret hardware-written descriptors while iterating captured data.

State and persistence: describes volatile register state and in-memory/DMA block descriptor fields populated by hardware.

Dependencies and integration: included by `msu.c`; relies on Linux bit macros and page constants.

Risks: descriptor size math affects user-visible read offsets. Off-by-one or mask changes can corrupt multiblock iteration, window sizing, and wrap detection.

Test signals: compile coverage, multiblock capture validation against expected block descriptor tags, wrap/last-block handling, and pipeline-empty wait path.
