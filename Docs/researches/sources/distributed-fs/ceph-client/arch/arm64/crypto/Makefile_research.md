# sources/distributed-fs/ceph-client/arch/arm64/crypto/Makefile

## Purpose
This Makefile maps arm64 crypto Kconfig options to kernel objects and sub-object composition.

## APIs, Types, And Functions
It declares `obj-$(CONFIG_...)` targets for SM4 CE cipher, SM4 CE block, SM4 CE CCM/GCM, SM4 NEON, GHASH CE, AES CE CCM, AES CE block, AES NEON block, and AES NEON bit-sliced implementations. Composite variables such as `aes-ce-ccm-y := aes-ce-ccm-glue.o aes-ce-ccm-core.o` define module internals.

## Control Flow, State, And Persistence
Kbuild evaluates selected config symbols and compiles linked objects accordingly. There is no runtime state in the Makefile; the persistent result is built-in objects or loadable modules.

## Dependencies And Integration
The Makefile depends on the Kconfig options in the same directory and on matching `.c`/`.S` source files. It integrates C glue with assembly cores, including wrappers `aes-glue-ce.o` and `aes-glue-neon.o` that include the shared `aes-glue.c`.

## Risks And Test Signals
Risks include object composition mismatches, missing assembly cores, or config names diverging from Kconfig. Test with arm64 `allmodconfig`, module load tests, and crypto manager selftests for the registered algorithms.
