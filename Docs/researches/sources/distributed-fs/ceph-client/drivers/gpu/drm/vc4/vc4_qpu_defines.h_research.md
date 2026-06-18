# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_qpu_defines.h

Purpose: Defines VC4 QPU instruction encoding constants: ALU opcodes, register addresses, signal values, mux/condition/pack/unpack enums, and bit masks/shifts for 64-bit QPU instructions.

Important APIs/types/functions: Key enums are `qpu_op_add`, `qpu_op_mul`, `qpu_raddr`, `qpu_waddr`, `qpu_sig_bits`, `qpu_mux`, `qpu_cond`, `qpu_pack_mul`, `qpu_pack_a`, and `qpu_unpack_r4`. Macros `QPU_MASK()` and `QPU_GET_FIELD()` plus `QPU_*_SHIFT/MASK` constants decode signals, unpack/pack, conditions, branch bits, register addresses, muxes, add/mul operations, immediates, and branch targets.

Control flow: None locally. Consumers use these constants to build/decode shader instructions and to reason about shader validation results.

State and persistence: No runtime state. The header is a stable hardware encoding contract.

Dependencies and integration points: Standalone except for standard integer types from includers. Ties into shader compiler/validator paths and debug tooling that decode QPU programs. In this subset, `vc4_validate.c` depends on prevalidated shader metadata rather than decoding QPU instructions directly, but those metadata originate from code that uses these definitions.

Risks: QPU encodings are dense and overloaded; wrong shifts or enum values can miscompile shaders or misinterpret validation. `QPU_MASK()` uses 64-bit shifts, so callers must avoid invalid high/low ranges. Some enum values alias hardware special registers and must match A/B file semantics.

Test signals: Shader validation/disassembly/compiler tests should decode and encode representative ALU, branch, signal, pack/unpack, small-immediate, and register-address instructions. Rendering tests should catch regressions in shader execution and uniform/texture access.
