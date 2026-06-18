# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/crypto.h

Purpose: Cavium Octeon COP2 crypto instruction interface for MD5, SHA1, SHA256, and SHA512 acceleration.

Important APIs/types/functions: `OCTEON_CR_OPCODE_PRIORITY` is `300`. Externs `octeon_crypto_enable()` and `octeon_crypto_disable()` save/restore COP2 crypto state around use. Macros write/read hash dwords, block dwords, and start hash operations using `dmtc2`/`dmfc2` with fixed COP2 opcodes. MD5 uses big-endian conversion for hash/block writes; SHA1/SHA256 starts write raw values; SHA512 has separate hash/block opcode ranges. The file contains duplicated SHA1/SHA256/SHA512 macro definitions with identical bodies.

Control flow, state, and persistence: Callers enable COP2 crypto, load state/block words through macros, trigger the final operation, read hash output, and disable/restore state. Persistent state is in COP2 crypto registers and saved `octeon_cop2_state`.

Dependencies and integration: Depends on scheduler state, byte-order helpers, `mipsregs.h`, and Octeon crypto drivers.

Risks and test signals: Opcode constants, endian conversions, and duplicate macro definitions are risk points. Test known-answer vectors for MD5/SHA1/SHA256/SHA512, context switches during crypto use, preemption/interrupt safety, and big/little-endian builds.
