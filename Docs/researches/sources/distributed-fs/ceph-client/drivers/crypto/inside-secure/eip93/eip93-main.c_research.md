# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-main.c

## Purpose
Implements the EIP93 platform driver: device probing, descriptor ring allocation, hardware initialization, interrupt handling, result dispatch, and crypto algorithm registration.

## Important APIs, Types, and Functions
Core routines include `eip93_register_algs()`, `eip93_unregister_algs()`, `eip93_handle_result_descriptor()`, `eip93_irq_handler()`, `eip93_initialize()`, `eip93_desc_init()`, `eip93_cleanup()`, `eip93_crypto_probe()`, and `eip93_crypto_remove()`. It exposes inline IRQ helpers `eip93_irq_enable()`, `eip93_irq_disable()`, and `eip93_irq_clear()`.

The static `eip93_algs[]` array collects templates from AES, DES, AEAD, and hash files.

## Control Flow
Probe allocates `struct eip93_device`, maps MMIO, requests the IRQ, allocates and initializes one command ring and one result ring, initializes tasklet/spinlocks/IDR, reads hardware option bits, resets/configures the packet engine, enables RDR threshold interrupts, and registers supported algorithms. Removal unregisters algorithms and disables/cleans hardware.

At runtime, the IRQ handler detects RDR threshold interrupts, disables that interrupt, and schedules a tasklet. The tasklet drains result descriptors. It waits until hardware marks descriptor ownership and length ready, acknowledges RD count, stops at `EIP93_DESC_LAST`, resolves the async request through the 16-bit IDR, parses hardware errors, and calls the result handler matching `EIP93_DESC_SKCIPHER`, `EIP93_DESC_AEAD`, or `EIP93_DESC_HASH`.

## State and Persistence
Maintains MMIO base, IRQ, rings, tasklet, spinlocks, and an IDR mapping descriptor user IDs to active crypto requests. Ring memory is DMA coherent and device-managed. No persistent storage is used.

## Dependencies and Integration Points
Depends on platform device/OF infrastructure, Linux crypto registration APIs, EIP93 register definitions, and algorithm templates from sibling EIP93 files. Device tree compatibles include several `inside-secure,safexcel-eip93*` variants.

## Risks
The result drain loop busy-waits for descriptor ownership bits with no timeout. IDR lookup/removal assumes a valid ID stored by submitters. The driver uses 32-bit DMA addresses in descriptors and casts coherent base DMA to `u32`, so it depends on suitable DMA addressing. Requesting a threaded IRQ with only a primary handler and `IRQF_ONESHOT` is unusual but functional if supported. Algorithm template globals are mutated with the device pointer during registration.

## Test Signals
Probe/remove on each compatible, interrupt storm and ring saturation tests, crypto self-tests under concurrent requests, IDR exhaustion behavior, DMA mask/address tests on 64-bit systems, and hardware error injection for auth/pad/ext errors.
