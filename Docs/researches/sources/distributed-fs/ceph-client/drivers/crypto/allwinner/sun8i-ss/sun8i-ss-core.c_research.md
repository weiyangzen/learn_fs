# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-core.c

## Purpose

`sun8i-ss-core.c` is the platform driver and registration layer for the older Allwinner Security System crypto block found on A80/A83T. It owns SoC variant capability data, flow allocation, register-level task execution, IRQ handling, runtime PM, debugfs stats, and CryptoAPI algorithm registration.

## Important APIs, Types, And Functions

Important functions are `sun8i_ss_probe()`, `sun8i_ss_remove()`, `sun8i_ss_register_algs()`, `sun8i_ss_unregister_algs()`, `allocate_flows()`, `sun8i_ss_get_engine_number()`, `sun8i_ss_run_task()`, `ss_irq_handler()`, `sun8i_ss_pm_resume()`, and `sun8i_ss_pm_suspend()`. `ss_a80_variant` supports ciphers only; `ss_a83t_variant` adds MD5/SHA1/SHA224/SHA256.

## Control Flow

Probe allocates `sun8i_ss_dev`, maps MMIO, gets clocks, IRQ, reset, allocates two flows and their helper buffers, initializes runtime PM, requests IRQ, registers supported algorithms, resumes once to read the die ID, and optionally creates debugfs. `sun8i_ss_run_task()` serializes register access with `mlock`, writes key/IV/source/destination/length registers per destination segment, starts the selected flow, and waits for the flow completion signaled by `ss_irq_handler()`.

## State And Persistence Behavior

Device state stores base, clocks, reset, mutex, flow array, round-robin atomic, variant pointer, and optional debugfs dentries. Each flow persists a crypto engine, completion, status, per-SG IV buffers, backup IV, hash pad/result buffers, and optional request count. Runtime suspend asserts reset and disables clocks; resume enables clocks, deasserts reset, and enables flow interrupts.

## Dependencies And Integration Points

It integrates with OF platform matching, common clock/reset, runtime PM, IRQs, `crypto_engine`, skcipher/hash/rng registration, DMA-capable helper buffers, and debugfs. Algorithm templates reference functions from cipher, hash, and PRNG files conditionally linked by the Makefile.

## Risks And Test Signals

Risks include register serialization blocking both flows, incomplete runtime PM unwind, optional algorithm symbols mismatching config, flow buffers sized for hash/HMAC assumptions, and timeout handling returning only `-EFAULT`. Test A80 vs A83T capability filtering, module remove with active TFMs, runtime suspend/resume, IRQ completion per flow, debugfs stats, and all optional build combinations.
