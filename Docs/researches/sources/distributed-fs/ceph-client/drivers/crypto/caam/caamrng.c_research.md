<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamrng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamrng.c

Purpose: registers CAAM as a Linux `hwrng` provider named `rng-caam`, using CAAM job-ring descriptors to fetch 16-byte RNG chunks and an async FIFO for nonblocking reads.

Important APIs and control flow: `caam_rng_init()` checks RNG presence, opens a devres group, allocates `caam_rng_ctx`, and registers `devm_hwrng_register()`. `caam_init()` allocates sync/async descriptors, a kfifo sized to DMA cache alignment, initializes work, allocates a JR, and pre-fills the async FIFO. `caam_read()` either performs a synchronous `caam_rng_read_one()` when `wait` is true or drains the FIFO and schedules `caam_rng_worker()` when empty. `caam_rng_read_one()` maps the destination, builds an RNG descriptor, enqueues it, waits for completion, unmaps, and returns either an error or 16 bytes. `caam_cleanup()` flushes work, frees JR reference, and frees the FIFO.

State and persistence behavior: per-hwrng state tracks the JR device, controller device, two reusable descriptors, work item, and FIFO. Device-managed allocation binds most lifetime to the controller, while `cleanup` releases ring/FIFO resources when hwrng unregisters. RNG entropy/state itself persists in hardware state handles instantiated by `ctrl.c`.

Dependencies and integration points: depends on Linux `hw_random`, kfifo DMA helpers, workqueues, CAAM descriptors, JR enqueue/free, and `caam_jr_strstatus()`. It is registered once by `jr.c` when the first job ring appears and cleaned up on JR removal/suspend.

Risks and test signals: `caam_rng_read_one()` ignores caller `len` and always requests 16 bytes, so buffers must be at least that large; no completion timeout exists; async fill silently drops errors; devres group cleanup must run on all registration failures. Test signals include `/dev/hwrng` reads in wait and non-wait paths, FIFO refill scheduling, suspend/remove cleanup without JR leaks, optional RNG self-test under `CONFIG_CRYPTO_DEV_FSL_CAAM_RNG_TEST`, and no registration when RNG block count is zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamrng.c -->
