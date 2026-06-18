# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace.c

## Purpose

`aspeed-hace.c` is the parent platform driver for the Aspeed Hash and Crypto Engine. It owns the shared HACE register block, clock, IRQ, coherent DMA buffers, crypto-engine queues, and tasklets used by the separate hash and symmetric-cipher implementation files. It supports AST2500 (`aspeed,ast2500-hace`) and AST2600 (`aspeed,ast2600-hace`) and conditionally registers hash and crypto algorithms depending on Kconfig.

## Important APIs, Types, And Functions

`aspeed_hace_probe()` and `aspeed_hace_remove()` are the platform lifecycle. `aspeed_hace_irq()` clears `ASPEED_HACE_STS` and schedules the hash or crypto done tasklet based on `HACE_HASH_ISR` and `HACE_CRYPTO_ISR`. `aspeed_hace_hash_done_task()` and `aspeed_hace_crypto_done_task()` call the current engine resume callback. `aspeed_hace_register()` and `aspeed_hace_unregister()` dispatch to the hash and skcipher registration helpers declared in `aspeed-hace.h`.

## Control Flow

Probe allocates `struct aspeed_hace_dev`, records the hardware version from OF match data, maps resource 0, requests IRQ 0, gets and enables the device clock, allocates and starts two crypto-engine instances, initializes tasklets, allocates a hash source buffer, a cipher context buffer, a cipher source buffer, and on AST2600 a cipher destination SG buffer, then registers algorithms. Remove unregisters algorithms, exits the engines, kills tasklets, and disables the clock.

## State And Persistence Behavior

The driver keeps one persistent device object with MMIO base, clock, IRQ, hardware version, two crypto-engine handles, and per-engine state. DMA buffers are coherent and device-managed, so their lifetime is the platform device lifetime. Busy state lives in the per-engine flags and is checked by the ISR before scheduling a completion tasklet. Hardware status is acknowledged by writing back the value read from `ASPEED_HACE_STS`.

## Dependencies And Integration Points

It integrates with platform/OF probing, `devm_platform_get_and_ioremap_resource()`, IRQ/tasklet APIs, the common clock framework, DMA coherent allocation, the Linux crypto engine, and compile-time feature symbols `CONFIG_CRYPTO_DEV_ASPEED_HACE_HASH` and `CONFIG_CRYPTO_DEV_ASPEED_HACE_CRYPTO`. The child implementation files rely on its buffers and `version` field to choose AST2500 versus AST2600 behavior.

## Risks And Test Signals

Risks include error unwind calling `crypto_engine_exit()` on an unallocated second engine, algorithm registration failures not causing probe failure, interrupts arriving after unregister but before tasklet kill, missing reset of stale hardware state on probe, and fixed coherent buffer sizes constraining large SG descriptors. Test by probing both compatibles, enabling hash-only/crypto-only/both Kconfig variants, running crypto selftests, checking remove/unbind paths, injecting allocation/IRQ/clock failures, and verifying no "no active requests" warnings under load.
