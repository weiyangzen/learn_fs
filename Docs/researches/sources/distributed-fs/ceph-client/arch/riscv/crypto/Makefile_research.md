<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/Makefile

## Purpose
Builds RISC-V vector crypto AES and SM4 objects selected by Kconfig.

## Important APIs, Types, And Functions
Defines `aes-riscv64.o` from glue plus three AES assembly files and `sm4-riscv64.o` from glue plus the SM4 assembly file.

## Control Flow
Kbuild evaluates `CONFIG_CRYPTO_AES_RISCV64` and `CONFIG_CRYPTO_SM4_RISCV64`, then links the listed composite objects.

## State And Persistence
State is build graph composition for crypto modules or built-ins.

## Dependencies And Integration Points
Depends on the arch/riscv Kbuild including `crypto/`, the crypto Kconfig symbols, and object names matching source files.

## Risks And Edge Cases
Missing an assembly object leaves declared glue symbols unresolved. Including objects without the right config can fail on unsupported assemblers.

## Test Signals
Signals are clean `M=arch/riscv/crypto` builds and `modinfo`/link output containing the expected composite objects.

Source read size: 8 lines, 323 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/Makefile -->
