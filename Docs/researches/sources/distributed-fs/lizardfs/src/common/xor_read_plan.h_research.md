# sources/distributed-fs/lizardfs/src/common/xor_read_plan.h

Purpose: defines `XorReadPlan`, the `SliceReadPlan` specialization that post-processes reads for XOR-coded chunk slices and reconstructs one missing requested part from parity/peer data.

Important APIs/types/functions: `class XorReadPlan : public SliceReadPlan`; nested `RecoverParity` functor for building parity blocks by copying the first data part and XORing the remaining parts with `blockXor`; override `postProcessRead(uint8_t *buffer, const PartsContainer &available_parts) const`.

Control flow: `postProcessRead` first delegates to `SliceReadPlan::postProcessRead`, records available slice parts in a bitset, then finds the first requested part not present in `available_parts`. If all requested parts were read directly it returns the concatenated requested size. Otherwise it computes the missing output offset and XORs every available read operation into that missing region, copying the first available source and zero-padding short reads before applying later XORs.

State and persistence: no persistent state of its own; it relies on inherited `requested_parts`, `read_operations`, `buffer_part_size`, and debug buffer bounds. Recovery mutates only the caller-provided buffer.

Dependencies and integration: depends on `common/block_xor.h`, `common/read_plan.h`, and `common/slice_read_plan.h`; used by slice read planning for XOR goals to turn a plan that reads parity/other parts into the requested client buffer layout.

Risks: recovery assumes exactly one requested part is missing and enough compatible parts were planned; debug-only assertions guard buffer ranges but release builds depend on planner correctness. `RecoverParity` copies whole `MFSBLOCKSIZE` blocks and assumes part/block counts match the source layout.

Test signals: directly exercised by `xor_read_plan_unittest.cc`, which verifies unrecoverable configurations and successful reads from direct and parity-recovered XOR parts.
