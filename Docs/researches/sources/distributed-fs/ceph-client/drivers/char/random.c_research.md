# sources/distributed-fs/ceph-client/drivers/char/random.c

## Purpose
`random.c` implements the kernel cryptographic random number generator, `/dev/random`, `/dev/urandom`, `getrandom(2)`, exported in-kernel random APIs, entropy accumulation, entropy source ingestion, readiness waiting, and `/proc/sys/kernel/random` sysctls. It uses a BLAKE2s input pool and a ChaCha20 fast-key-erasure CRNG.

## Important APIs, Types, and Functions
- Readiness state is `crng_init` with `CRNG_EMPTY`, `CRNG_EARLY`, and `CRNG_READY`, plus static key `crng_is_ready`.
- Exported readiness APIs include `rng_is_initialized()`, `wait_for_random_bytes()`, and `execute_with_initialized_rng()`.
- `base_crng` and per-CPU `struct crng` store ChaCha keys and generations.
- `crng_reseed()`, `crng_make_state()`, `crng_fast_key_erasure()`, `_get_random_bytes()`, and `get_random_bytes_user()` generate output.
- `DEFINE_BATCHED_ENTROPY()` defines exported `get_random_u8/u16/u32/u64()`, and `__get_random_u32_below()` implements unbiased bounded values.
- Input pool functions include `mix_pool_bytes()`, `extract_entropy()`, and `_credit_init_bits()`.
- Entropy source APIs include `add_device_randomness()`, `add_hwgenerator_randomness()`, `add_bootloader_randomness()`, optional `add_vmfork_randomness()`, `add_interrupt_randomness()`, `add_input_randomness()`, `add_disk_randomness()`, and `rand_initialize_disk()`.
- User ABI includes `SYSCALL_DEFINE3(getrandom)`, `random_fops`, `urandom_fops`, `random_ioctl()`, and sysctls for `boot_id`, `uuid`, `poolsize`, `entropy_avail`, and legacy thresholds.

## Control Flow
Early boot mixes architecture randomness, latent entropy, UTS name, and command line in `random_init_early()`, crediting CPU entropy only if trusted. `random_init()` mixes timestamps, registers the PM notifier, enables readiness static key if already initialized, and reseeds when possible. Entropy events mix data into the BLAKE2s pool and may credit initialization bits. When enough bits are credited, `_credit_init_bits()` reseeds the CRNG, enables readiness, notifies waiters, updates vDSO readiness, wakes poll/read waiters, and sends fasync.

Output generation obtains or refreshes a per-CPU CRNG key from `base_crng`, uses fast key erasure, and streams ChaCha blocks. `getrandom()` blocks unless ready or `GRND_INSECURE` is set; `/dev/random` blocks until ready; `/dev/urandom` warns but serves output before readiness.

## State and Persistence
State is in-memory only: input pool hash/key, CRNG keys/generations, readiness counters, per-CPU batches, interrupt fast pools, disk/input timing states, wait queues, notifier chains, fasync state, and sysctl boot UUID. No seed file persistence is implemented here; userspace may write seed material to the devices, which mixes but does not credit entropy unless privileged ioctls are used.

## Dependencies and Integration Points
This file integrates with crypto primitives (`chacha`, `blake2s`, siphash), architecture random instructions and cycle counters, interrupts, input, block layer, VM generation ID notifiers, PM suspend/resume, vDSO getrandom data, syscalls, proc/sysctl, fasync, polling, and the memory-device registration in `mem.c`.

## Risks
- Security depends on correct entropy crediting and preserving forward secrecy via key erasure and zeroization.
- Pre-initialization `/dev/urandom` and `GRND_INSECURE` behavior remains intentionally available but warns users.
- Entropy accounting is conservative but architecture/platform trust knobs (`random.trust_cpu`, `random.trust_bootloader`) affect readiness.
- Concurrency is complex: spinlocks, local locks, per-CPU state, timers, notifiers, and hotplug hooks must keep generations coherent.
- `random_ioctl()` permits privileged entropy crediting and reseeding; misuse can affect global RNG state.

## Test Signals
Signals include boot readiness transition logs, blocking/nonblocking `getrandom()` behavior, `/dev/random` poll readiness, urandom warning ratelimiting before readiness, sysctl UUID generation, ioctl permission checks, CPU hotplug invalidating batches, PM/vmfork reseed logs, and statistical/API tests for bounded random values. Security review should focus on readiness transitions, entropy credit paths, and zeroization after extraction.
