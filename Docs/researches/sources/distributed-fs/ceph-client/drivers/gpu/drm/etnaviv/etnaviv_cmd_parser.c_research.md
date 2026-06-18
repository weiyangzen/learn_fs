# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_cmd_parser.c

## Purpose
Validates userspace etnaviv command streams, rejecting forbidden opcodes and writes to sensitive hardware state unless backed by expected relocations.

## Important APIs, Types, and Functions
Exports `etnaviv_validate_init` and `etnaviv_cmd_validate_one`. Internal state includes `struct etna_validation_state`, the `etnaviv_sensitive_states` table, a bitmap of sensitive state offsets, and `cmd_length` for allowed fixed-length opcodes. The `EXTRACT` macro decodes generated bitfields.

## Control Flow
Initialization populates a bitmap of sensitive state register ranges. Validation walks the command dwords, decodes opcode, computes packet length, and for LOAD_STATE checks whether the written register range intersects sensitive states. Sensitive state writes require a relocation at the matching submit offset; non-sensitive relocations are warned and skipped. Only a small allowlist of draw/NOP/stall/load-state packet types is permitted.

## State and Persistence
The sensitive-state bitmap is initialized once at module init. Per-submit validation is stateless except for advancing through the relocation array.

## Dependencies and Integration Points
Called from `etnaviv_gem_submit.c` before submission. Depends on generated command stream bitfields, relocation records from the UAPI submit path, and GPU device logging.

## Risks
Parser length bugs can under- or over-scan command buffers. Missing sensitive registers weakens isolation; overly broad ranges reject valid workloads. Relocations must be sorted consistently with command offsets for the advancing pointer logic.

## Test Signals
Submit tests with valid/invalid LOAD_STATE relocations, forbidden opcode rejection, truncated packet rejection, fuzzed command streams, and rate-limited warning coverage are key.
