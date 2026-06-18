# sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce-rng.c

Purpose: exposes the SL3516 crypto engine random-number register through the Linux hwrng framework.

Important APIs and control flow: `sl3516_ce_rng_register()` fills `ce->trng` with name, quality 700, and `sl3516_ce_rng_read()`, then calls `hwrng_register()`. `sl3516_ce_rng_read()` recovers `struct sl3516_ce_dev` via `container_of()`, optionally increments debug counters, runtime-resumes the device, repeatedly reads 32-bit words from `IPSEC_RAND_NUM_REG` until at least `max` bytes are produced, then releases runtime PM and returns the byte count. `sl3516_ce_rng_unregister()` calls `hwrng_unregister()`.

State and persistence behavior: state is embedded in `struct sl3516_ce_dev` as `struct hwrng trng` plus optional counters. No seed or entropy pool state is maintained by the driver; hardware register reads are direct. The function ignores the `wait` parameter and always performs immediate register reads after powering the device.

Dependencies and integration points: depends on runtime PM from core, the MMIO base and random register offset in `sl3516-ce.h`, and the Linux `hw_random` subsystem. Core probe registers the RNG after crypto algorithms and unregisters it first during remove/unwind.

Risks and test signals: risks include writing past `max` when `max` is not a multiple of four because the loop stores full `u32` words, no status/ready check before reading the random register, quality value being asserted without health tests in this file, and PM errors needing `pm_runtime_put_noidle()` as implemented. Test signals include hwrng registration, reads with non-multiple-of-four sizes under KASAN, runtime PM enable/disable tracing, repeated reads returning requested lengths, and debug counters matching hwrng activity.
