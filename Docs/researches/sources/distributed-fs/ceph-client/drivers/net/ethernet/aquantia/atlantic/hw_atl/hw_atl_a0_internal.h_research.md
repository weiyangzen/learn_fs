<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0_internal.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0_internal.h

Purpose: defines A0-specific constants for MTU, ring counts, descriptor sizes, descriptor bit masks, MPI registers, buffer sizes, RSS packing, TC limits, firmware semaphore IDs, RX writeback bits, and descriptor count bounds.

Important APIs/types: constants include `HW_ATL_A0_MTU_JUMBO`, ring and descriptor sizing, MAC filter slot range, interrupt mask/error vector, TX descriptor control masks, MPI address/speed masks, TX/RX buffer sizes, RSS table properties, TC/RSS max, firmware expected version, and min/max RXD/TXD macros.

Control flow: `hw_atl_a0.c` uses these constants to build capability records, pack TX descriptors, parse RX writebacks, program RSS, map filters, size buffers, and validate descriptor limits.

State and persistence: no runtime state; it is compile-time hardware contract data.

Dependencies and integration: includes `aq_common` for common constants and alignment macros. It is private to A0 hardware code.

Risks: incorrect masks or sizes directly corrupt MMIO/descriptor programming; min/max descriptor macros must stay compatible with generic ring allocation and hardware multiples. Test signals include descriptor programming, RSS table packing, MTU boundary tests, ring size validation, and A0 hardware smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0_internal.h -->
