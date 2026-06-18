# sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-glue-ce.c

## Purpose
This wrapper builds the shared AES skcipher glue as the ARMv8 Crypto Extensions implementation.

## APIs, Types, And Functions
It defines `USE_V8_CRYPTO_EXTENSIONS` and includes `aes-glue.c`. That macro switches the shared implementation to CE mode, setting `MODE` to `ce`, priority to 300, using `ce_aes_*` assembly/core routines, and enabling CPU feature match registration.

## Control Flow, State, And Persistence
All control flow is inherited from `aes-glue.c`. This wrapper has no state, but its compile-time macro changes algorithm names, driver names, priority, function bindings, and module init gating.

## Dependencies And Integration
It depends on `aes-glue.c` and the CE backend symbols linked into `aes-ce-blk.o`. Kbuild uses it for `CONFIG_CRYPTO_AES_ARM64_CE_BLK`.

## Risks And Test Signals
Risks are compile-time macro drift or missing CE symbols. Test by building `aes-ce-blk`, checking registered drivers such as `ecb-aes-ce`, and running AES skcipher selftests on an AES-capable arm64 CPU.
