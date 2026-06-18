# File Research: sources/block-storage/thin-provisioning-tools/src/pack/vm.rs

This file implements the bytecode VM used to pack and unpack metadata byte streams.

Important pieces:
- `Tag` enum defines instruction opcodes for setting base values, positive/negative deltas, constants, counts, literals, and shifted u64 runs.
- Packing helpers encode counts, deltas, u64 sequences, shifted u64 sequences, and literal bytes.
- `VM` tracks current u64 base value and total emitted bytes while interpreting instructions.
- `unpack()` runs the VM until a requested byte count is emitted.

Important behavior:
- `pack_u64s()` uses `delta_list::to_delta()`.
- `pack_shifted_u64s()` splits u64s into high bits and low 24 bits for better compression.
- `ShiftedRun` recursively unpacks high and low streams, then recombines values.

Integration points:
- Used by node encoding, top-level unpack, and spindle cache unpack.

Test coverage:
- Literal packing.
- u64 sequence packing.
- Property tests for arbitrary u64 vectors.
- Property tests for shifted u64 packing.

Risks and notes:
- Several invalid opcode/width paths panic rather than return errors.
- Empty u64 vectors are not supported by `pack_u64s()` callers/tests.
