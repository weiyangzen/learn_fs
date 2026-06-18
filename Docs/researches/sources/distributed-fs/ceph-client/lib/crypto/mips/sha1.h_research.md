# sources/distributed-fs/ceph-client/lib/crypto/mips/sha1.h

## Purpose
Provides an OCTEON-accelerated `sha1_blocks()` override for SHA-1 block processing on MIPS systems with OCTEON crypto hardware.

## Important APIs, Types, and Functions
- Defines `octeon_sha1_store_hash()`, `octeon_sha1_read_hash()`, and static `sha1_blocks()`.
- Uses `struct sha1_block_state`, `struct octeon_cop2_state`, and OCTEON crypto register helpers.

## Control Flow and State
`sha1_blocks()` checks `octeon_has_crypto()`. If unavailable, it delegates to `sha1_blocks_generic()`. Otherwise it enables COP2 crypto state, writes the current hash into hardware registers, streams each 64-byte block as eight 64-bit words, starts the hardware SHA-1 operation, reads the resulting hash state, and disables/restores crypto state. Temporary hash-tail union handling avoids leaking the unused word.

## Dependencies and Integration Points
Included by the generic SHA-1 implementation as an architecture override. Depends on `<asm/octeon/crypto.h>` and `<asm/octeon/octeon.h>`.

## Risks and Test Signals
Risks include assuming OCTEON's misaligned access behavior, hash word packing of the fifth SHA-1 word, COP2 state restore bugs, and fallback parity. Tests should compare SHA-1 vectors with and without hardware, run unaligned input buffers, multi-block streams, and preemption/state-save stress where possible.
