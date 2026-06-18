# sources/distributed-fs/ceph-client/drivers/crypto/amlogic/amlogic-gxl-core.c

## Purpose

`amlogic-gxl-core.c` is the platform driver and CryptoAPI registration layer for the Amlogic GXL crypto offloader. It manages MMIO, clock enablement, flow engines, IRQ completion, algorithm templates, debugfs, and probe/remove.

## Important APIs, Types, And Functions

Important functions are `meson_crypto_probe()`, `meson_crypto_remove()`, `meson_allocate_chanlist()`, `meson_free_chanlist()`, `meson_register_algs()`, `meson_unregister_algs()`, `meson_irq_handler()`, and `meson_debugfs_show()`. `mc_algs[]` registers `cbc(aes)` and `ecb(aes)` as crypto-engine skcipher algorithms.

## Control Flow

Probe allocates `meson_dev`, maps resource 0, gets and enables `blkmv` clock, obtains two IRQs, requests both with a shared handler, allocates two flow engines and coherent descriptor lists, registers algorithms, and creates optional debugfs stats. The IRQ handler identifies the flow by IRQ number, reads the flow status register, clears it, marks completion, and wakes the waiting crypto-engine worker. Remove removes debugfs, unregisters algorithms, frees flow engines/descriptors, and disables the clock.

## State And Persistence Behavior

Persistent state includes MMIO base, bus clock, device pointer, flow list, round-robin atomic, IRQ array, and optional debugfs dentry. Each flow persists a crypto engine, completion, status, descriptor list physical/virtual addresses, and optional request counter. Hardware state is not saved across suspend because no PM hooks are defined.

## Dependencies And Integration Points

It integrates with platform/OF matching for `amlogic,gxl-crypto`, common clock, IRQs, coherent DMA, `crypto_engine`, internal skcipher registration, and debugfs.

## Risks And Test Signals

Risks include no reset/runtime-PM handling, per-flow IRQ/register mapping mistakes, failure unwind ordering, algorithm template global state across multiple devices, and status clearing semantics. Test probe/remove, both flows, IRQ routing, clock gating, debugfs stats, multi-device assumptions, and CryptoAPI selftests on GXL hardware.
