# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/Makefile

## Purpose
This Makefile builds Inside Secure crypto accelerator drivers. It selects the Safexcel composite object when `CONFIG_CRYPTO_DEV_SAFEXCEL` is enabled and always descends into the `eip93/` subdirectory for its own Kconfig-controlled build.

## Important APIs, Types, And Functions
There are no runtime APIs. Kbuild variables define `crypto_safexcel.o` and its object list: `safexcel.o`, `safexcel_ring.o`, `safexcel_cipher.o`, and `safexcel_hash.o`. The `obj-y += eip93/` line includes the EIP93 subdirectory in the build traversal.

## Control Flow
Kbuild composes `crypto_safexcel.o` conditionally and visits `eip93/` unconditionally, where `eip93/Makefile` decides whether `crypto-hw-eip93.o` is built.

## State And Persistence
No runtime state exists. The file controls build graph shape only.

## Dependencies And Integration Points
It integrates two Inside Secure driver families under one directory: Safexcel and EIP93. It depends on each subdriver's Kconfig symbols and object lists.

## Risks
The unconditional `obj-y += eip93/` is safe because the subdirectory has its own config guard, but build errors in the subdirectory can still affect all builds that traverse it. Object-list drift would cause missing symbols or dead code.

## Test Signals
Build with Safexcel on/off and EIP93 on/off, both built-in and modular, and confirm modpost has no unresolved symbols and expected modules are produced.
