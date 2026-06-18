# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_asm.c

## Purpose
Implements helper routines for encoding and modifying NFP microengine instructions and software register operands, plus ECC generation for ustore instructions. It supports code generation/patching used by NFP BPF/offload logic elsewhere in the driver.

## Important APIs, Types, and Functions
- `cmd_tgt_act[]` maps abstract command target operations to token/target-command encodings.
- `br_get_offset()`, `br_set_offset()`, and `br_add_offset()` read and modify branch offsets spanning low/high address fields.
- `immed_get_value()`, `immed_set_value()`, and `immed_add_value()` decode and adjust immediate instruction operands when encoding constraints allow.
- `swreg_to_unrestricted()` and `swreg_to_restricted()` convert software register handles into hardware operand encodings, tracking operand swaps, A/B destination, write-both, immediate-8, and LM extension bits.
- `nfp_ustore_check_valid_no_ecc()` validates instruction width before ECC; `nfp_ustore_calc_ecc_insn()` appends ECC parity bits.

## Control Flow
Instruction builders call these helpers while emitting or relocating NFP instructions. Operand conversion validates incompatible register combinations, may swap A/B operands to satisfy hardware register-bank constraints, and returns populated encoding structs. ECC calculation iterates fixed polynomial masks and appends seven parity bits above the 45-bit instruction payload.

## State and Persistence Behavior
No mutable global state except the constant command map and ECC polynomial table. Functions operate on caller-provided instruction words and output structs. Generated instruction streams may later be loaded to firmware/hardware, but this file does not persist them.

## Dependencies and Integration Points
Depends on `nfp_asm.h`, Linux bitfield helpers, bitops, and logging. Integrated with JIT/offload code that emits NFP microcode, especially BPF-related components.

## Risks
Encoding errors can generate invalid microcode. Some error cases log and return zero encodings instead of propagating errno from lower helpers, so callers must validate top-level returns. Immediate modification only supports non-inverted, unshifted, full-width immediates.

## Test Signals
Unit-style encode/decode tests for branch offsets, immediates, each software register type, LM modes, restricted/unrestricted operand conflicts, and ECC parity vectors. Negative tests should verify invalid immediates/registers return errors or emit expected diagnostics.
