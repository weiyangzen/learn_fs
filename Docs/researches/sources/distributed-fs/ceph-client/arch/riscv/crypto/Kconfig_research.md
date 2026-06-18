<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/Kconfig

## Purpose
Adds RISC-V accelerated AES and SM4 crypto algorithm configuration options.

## Important APIs, Types, And Functions
`CRYPTO_AES_RISCV64` enables AES ECB/CBC/CTS/CTR/XTS using Zvkned plus Zvbb/Zvkb/Zvkg where needed. `CRYPTO_SM4_RISCV64` enables SM4 using Zvksed and Zvkb. Both require 64-bit RISC-V, vector crypto toolchain support, and efficient vector unaligned access.

## Control Flow
Kconfig exposes module/built-in options; selected symbols cause the crypto Makefile to build the glue and vector assembly objects.

## State And Persistence
State is build configuration and module availability. Runtime registration still checks actual CPU ISA and VLEN.

## Dependencies And Integration Points
Integrated with Linux crypto API symbols, RISC-V vector crypto toolchain probes, and the arch/riscv crypto Makefile.

## Risks And Edge Cases
Enabling with insufficient runtime hardware results in module init `-ENODEV`; wrong dependencies could compile assembly the toolchain cannot parse or register algorithms on unsupported CPUs.

## Test Signals
Signals are config visibility, successful module builds, runtime registration only when ISA extensions and VLEN are present, and crypto self-tests for AES/SM4.

Source read size: 38 lines, 1190 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/Kconfig -->
