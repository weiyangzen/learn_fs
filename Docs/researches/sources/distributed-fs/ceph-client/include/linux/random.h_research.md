# sources/distributed-fs/ceph-client/include/linux/random.h

Purpose: declares the kernel random-number and entropy-input API, including device/input/interrupt/hardware entropy injection, byte and scalar random output, bounded uniform integer helpers, initialization readiness, VM fork notifications, CPU hotplug hooks, and `/dev/random` file operations.

Important APIs and types: entropy input functions include `add_device_randomness()`, bootloader/input/interrupt/hwgenerator variants, and `add_latent_entropy()`. Output functions include `get_random_bytes()`, `get_random_u8/u16/u32/u64()`, `get_random_long()`, `get_random_u32_below()`, `get_random_u32_above()`, and `get_random_u32_inclusive()`. Initialization APIs include `random_init_early()`, `random_init()`, `rng_is_initialized()`, `wait_for_random_bytes()`, `execute_with_initialized_rng()`, and `get_random_bytes_wait()`. Optional VMGENID and SMP hooks handle VM fork reseeding and CPU state.

Control flow: boot adds early entropy, initializes RNG state, later producers mix environmental entropy, and consumers either read immediately or wait for initialization. Bounded helpers use reciprocal multiplication with rejection to avoid modulo bias and specialize constant ceilings at compile time.

State and persistence: RNG state is global in-kernel cryptographic state plus per-CPU/backend state outside this header. It is runtime-only but may be reseeded by bootloader, devices, interrupts, hardware RNGs, and VM-generation events.

Dependencies and integration points: depends on UAPI random definitions, notifier blocks, file operations, latent entropy plugin, VMGENID, SMP hotplug, and kernel math/build assertions. It integrates crypto/security-sensitive consumers, device drivers, boot code, and character devices.

Risks and test signals: risks include use before initialization where blocking is required, zero/overflow bounds, modulo bias regressions, entropy over-crediting, VM clone reuse, and hotplug reseeding bugs. Test boot readiness, `get_random_u32_below()` boundaries and distribution, VM fork notifier paths, hardware RNG injection, CPU online/offline hooks, and `/dev/random`/`urandom` behavior.
