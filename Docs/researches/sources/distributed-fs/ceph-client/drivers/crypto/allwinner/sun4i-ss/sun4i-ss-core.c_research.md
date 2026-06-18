<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-core.c

## Purpose

`sun4i-ss-core.c` is the platform and algorithm registration core for the Allwinner sun4i Security System. It probes clocks, reset, MMIO, variant data, runtime PM, registers hash/cipher/RNG algorithms, and exposes optional debugfs statistics.

## Important APIs, Types, And Functions

`ss_algs[]` contains the MD5, SHA1, AES CBC/ECB, DES CBC/ECB, 3DES CBC/ECB, and optional PRNG algorithm templates. `sun4i_ss_probe()` initializes hardware resources and registers algorithms. `sun4i_ss_remove()` unregisters them. Runtime PM callbacks `sun4i_ss_pm_suspend()` and `sun4i_ss_pm_resume()` assert/deassert reset and disable/enable bus and module clocks. Variants `ss_a10_variant` and `ss_a33_variant` describe SHA1 digest endianness.

## Control Flow

Probe maps MMIO, loads match data, gets `mod` and `ahb` clocks, obtains optional reset, sets module clock rate, logs clock compliance, initializes runtime PM, temporarily resumes the device to read the die ID from `SS_CTL`, then iterates `ss_algs[]` registering each algorithm with the correct crypto API. Failure unwinds already registered algorithms and disables runtime PM.

## State And Persistence Behavior

`struct sun4i_ss_ctx` persists as platform data and holds base address, clocks, reset, spinlock, buffers, optional PRNG seed, variant, and debugfs dentries. Algorithm templates store back-pointers to the single device and optional stats.

## Dependencies And Integration Points

It depends on platform devices, OF match compatibles `allwinner,sun4i-a10-crypto` and `allwinner,sun8i-a33-crypto`, common clocks, reset controller, runtime PM, crypto API registration, debugfs, and the cipher/hash/PRNG implementation files.

## Risks And Test Signals

Risks include global algorithm templates limiting multiple device instances, clock-rate assumptions, missing debugfs cleanup, partial registration unwind errors, and SHA1 endian variant mistakes. Test probe/remove, runtime suspend/resume, crypto self-tests, A10 versus A33 SHA1 vectors, and debugfs stats under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-core.c -->
