# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-core.S

## Purpose
Implements fast AES single-block encryption and decryption cores for PowerPC SPE SIMD instructions.

## Important APIs, Types, and Functions
- Defines `_GLOBAL(ppc_encrypt_block)` and `_GLOBAL(ppc_decrypt_block)`.
- Uses register definitions from `aes-spe-regs.h`.
- Macros `EAD`, `DAD`, `LWH`, `LWL`, `LBZ`, `LAH`, `LAL`, `LAE`, and `LAD` build T-table/S-box addresses and loads.

## Control Flow and State
Both functions are leaf block cores with no stack setup; callers must prepare registers with pre-xored input, key pointer, table pointer, and CTR round count. Encryption iterates combined table rounds using SPE loads/xors and final S-box byte assembly, then leaves output in data/word registers for caller final XOR. Decryption mirrors this with inverse table addressing and final inverse S-box loads. All working registers are documented as clobbered.

## Dependencies and Integration Points
Integrated by higher-level PowerPC AES SPE assembly/C wrappers that manage mode loops, key schedule, stack, and final stores. Depends on SPE instruction availability, PPC assembler macros, and table layout expected by `aes-spe-regs.h`.

## Risks and Test Signals
Risks include table-index side channels, caller/callee register contract mismatch, CTR round-count setup, and final round byte placement. Tests should include AES-128/192/256 encrypt/decrypt known-answer vectors through the wrapper, all supported modes using this core, build tests for SPE targets, and disassembly/register-clobber review.
