# sources/distributed-fs/ceph-client/lib/crypto/arm/aes-cipher-core.S

## Purpose
This ARM assembly file implements scalar AES block encryption and decryption using T-tables, optimized for ARM and integrated as the ARM AES arch backend.

## Important APIs, Types, and Functions
It defines `ENTRY(__aes_arm_encrypt)` and `ENTRY(__aes_arm_decrypt)`. Macros include `__select`, `__load`, `__hround`, `fround`, `iround`, and `do_crypt`.

## Control Flow
`do_crypt` loads the round keys and input block, handles big-endian byte reversal, XORs the first round key, prefetches the selected T-table with interrupts disabled, executes paired round macros until the final round, prefetches inverse S-box data for decryption final round, restores interrupts after data-dependent lookups, and stores the result.

## State and Persistence
All state is register/stack-local during a single block operation. It reads global AES tables from `aes.c` and does not mutate persistent state.

## Dependencies and Integration Points
It depends on ARM assembler helpers, cacheline constants, AES tables, and the C wrapper in `arm/aes.h`. `Makefile` includes it in `libaes` for ARM when AES arch support is enabled.

## Risks and Test Signals
Risks include table-based cache timing leakage, interrupt disabling window length, alignment assumptions, big-endian handling, and register clobber ABI errors. Test signals include AES known-answer tests on ARM, unaligned buffer wrapper tests, and FIPS/crypto selftests.
