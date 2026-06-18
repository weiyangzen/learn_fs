# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/Makefile

## Purpose
This Makefile defines the object composition for Keem Bay OCS crypto drivers.

## Important APIs, Types, And Functions
- `keembay-ocs-aes.o` is built from `keembay-ocs-aes-core.o` and `ocs-aes.o`.
- `keembay-ocs-ecc.o` is built as a single-object module.
- `keembay-ocs-hcu.o` is built from `keembay-ocs-hcu-core.o` and `ocs-hcu.o`.

## Control Flow
Kbuild includes each module based on its Kconfig symbol. The core files implement Crypto API/platform-driver glue, while `ocs-aes.o` and `ocs-hcu.o` provide lower-level register/DMA primitives.

## State And Persistence
No runtime state is stored here.

## Dependencies And Integration Points
This file is coupled to `Kconfig` and the source file names in the same directory.

## Risks
Low risk. Build failures will occur if object names drift from source names.

## Test Signals
Build each Keem Bay crypto option as module and built-in, verifying multi-object modules link correctly.
