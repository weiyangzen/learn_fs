## sources/distributed-fs/ceph-client/drivers/dma/amd/qdma/qdma-comm-regs.c

### Purpose
`qdma-comm-regs.c` provides the default AMD QDMA register offset and bit-field tables used by the QDMA core. It centralizes common hardware register layout data for context, queue, interrupt, and error programming.

### Important APIs, Types, And Functions
The file defines two constant arrays: `qdma_regos_default[QDMA_REGO_MAX]` of `struct qdma_reg` entries and `qdma_regfs_default[QDMA_REGF_MAX]` of `struct qdma_reg_field` entries. It uses `QDMA_REGO()` and `QDMA_REGF()` macros and enumerators declared in `qdma.h`.

### Control Flow, State, And Persistence
There is no executable control flow. The arrays are read-only driver data describing offsets and word counts for context data/cmd/mask, H2C/C2H MM controls, queue count, ring size, producer/consumer indices, function ID, and error registers, plus bit ranges for queue context, interrupt context, command fields, queue count, and error interrupt fields.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies are `qdma.h` enum ordering and field extraction helpers in the QDMA core. Risks include table index drift when enum values change, incorrect bit positions silently corrupting hardware contexts, and lack of per-IP-version differentiation if newer hardware layouts diverge. Test signals include QDMA probe reading expected queue count/function ID, context programming round trips, interrupt vector programming, error interrupt arming, and compile-time array bounds coverage through `QDMA_REGO_MAX` and `QDMA_REGF_MAX`.
