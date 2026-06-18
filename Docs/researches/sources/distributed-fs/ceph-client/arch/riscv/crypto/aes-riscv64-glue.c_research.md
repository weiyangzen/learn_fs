<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-glue.c -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-glue.c

## Purpose
Registers Linux skcipher AES algorithms backed by RISC-V vector crypto assembly.

## Important APIs, Types, And Functions
Declares assembly entry points for ECB, CBC, CBC-CTS, CTR32, and XTS. C helpers include `riscv64_aes_setkey`, mode-specific encrypt/decrypt functions, `struct riscv64_aes_xts_ctx`, algorithm arrays, and module init/exit registration.

## Control Flow
Setkey uses generic AES expansion. Each request walks scatterlists with `skcipher_walk_virt`, brackets vector assembly with `kernel_vector_begin/end`, handles partial tails for CTR, and ensures CTS/XTS tail blocks are contiguous when ciphertext stealing is needed. Module init checks Zvkned, Zvbb, Zvkg, Zvkb, and VLEN before registering mode groups.

## State And Persistence
Persistent state is per-tfm AES context, XTS tweak key, algorithm registration, and request IV updates. Vector state is borrowed only inside kernel vector sections.

## Dependencies And Integration Points
Integrated with Linux crypto skcipher API, scatterwalk, generic AES library, XTS helpers, RISC-V vector state management, and runtime ISA detection.

## Risks And Edge Cases
Tail handling around CTR overflow and CTS/XTS scatterlist boundaries is subtle. Missing vector bracketing can corrupt task vector state. Runtime extension checks must match the assembly used by each registered algorithm.

## Test Signals
Signals are crypto self-tests for ecb/cbc/cts/ctr/xts, scatterlist fragmentation tests, in-place operation, partial final CTR blocks, counter overflow boundaries, and module load on supported versus unsupported CPUs.

Source read size: 566 lines, 17100 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-glue.c -->
