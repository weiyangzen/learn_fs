# sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/error-gen-mem-types.h

## Purpose
This header declares memory accounting IDs for the error-gen debug translator.

## Important APIs, Types, And Functions
It defines enum `gf_error_gen_mem_types_` with `gf_error_gen_mt_eg_t` for private error-gen state and `gf_error_gen_mt_end` as the registration limit.

## Control Flow
There is no runtime control flow. The implementation should use these IDs during memory-accounting initialization and private-state allocation.

## State And Persistence Behavior
It only labels heap allocations for diagnostics and persists no data.

## Dependencies And Integration Points
It includes `<glusterfs/mem-types.h>` and follows the translator-local numbering convention beginning at `gf_common_mt_end + 1`.

## Risks
Forgetting to use this type in allocations weakens memory diagnostics. Reordering enum values should be avoided for consistency with accounting output.

## Test Signals
Build coverage and memory-accounting dumps for error-gen should show allocations under the expected type.
