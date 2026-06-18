# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_reg_addr.h

Purpose: Central register-address and bitfield-definition header for the QED driver. It gives implementation files symbolic names for BAR0/GRC block registers, memory windows, debug controls, parser/NIG/DORQ/QM/IGU/CDU/Storm registers, MCP scratch/shared memory offsets, tunnel configuration registers, PTP timestamp registers, RDMA parser registers, and many chip-specific variants.

Important APIs/types/functions: There are no functions or types; the file is a large set of `#define` constants. Important groups include context/CDU CID/TID parameter masks, BAR0 storm RAM maps, MCP scratch/public memory, NIG LLH/filter/PTP/tunnel registers, PRS parser search and light-L2/RoCE registers, DORQ doorbell/EDPM registers, IGU interrupt/status/configuration registers, QM rate-limit/WFQ/PQ registers, PGLUE error/BAR registers, debug select/shift/force registers for many blocks, and block init/soft-reset addresses.

Control flow: No runtime control flow. Consumers use these constants with `qed_rd()`, `qed_wr()`, `REG_WR16()`, GTT address macros, and bitfield helpers to program hardware.

State and persistence: The header itself stores no state. Values correspond to persistent hardware register locations and bit masks whose effects last until hardware reset or later programming.

Dependencies/integration: Included throughout QED core, storage, RDMA, PTP, LLH, debug, init, and MCP paths. Files in this work item use it for PTP NIG registers, RDMA parser/light-L2/DORQ registers, MCP TLV shared memory access, and NVMe/TCP doorbell/PQ context.

Risks: Register constants are an ABI with hardware/firmware. Wrong addresses, duplicate names, chip-family mismatches, or mask/shift drift can cause silent hardware misprogramming. Because this header is broad and untyped, invalid combinations are caught only through hardware behavior or focused tests. Some names have BB/K2/E5 suffixes while others are generic, so call sites must choose by chip helper when needed.

Test signals: Compile coverage across all QED personalities, hardware bring-up smoke tests, register read/write selftests, PTP timestamp/filter tests, RDMA/RoCE parser enable tests, tunnel and LLH filter tests, debug dump paths, and static checks for duplicate/mismatched mask/shift pairs.
