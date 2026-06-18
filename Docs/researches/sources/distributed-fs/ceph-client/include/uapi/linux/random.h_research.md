<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/random.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/random.h

Purpose: defines the random-number generator userspace ABI for `/dev/random` ioctls, `getrandom(2)` flags, entropy pool injection, and vDSO/vgetrandom opaque-state allocation parameters.

Important APIs and types: ioctls include `RNDGETENTCNT`, `RNDADDTOENTCNT`, removed legacy `RNDGETPOOL`, `RNDADDENTROPY`, `RNDZAPENTCNT`, `RNDCLEARPOOL`, and `RNDRESEEDCRNG`. `struct rand_pool_info` carries entropy count, buffer size, and flexible input buffer. `GRND_NONBLOCK`, `GRND_RANDOM`, and `GRND_INSECURE` define `getrandom()` flags. `struct vgetrandom_opaque_params` describes opaque state size and mmap parameters.

Control flow: userspace reads random devices or calls `getrandom()`, optionally nonblocking or insecure. Privileged users can adjust entropy accounting, inject entropy, clear/reseed CRNG, or allocate vgetrandom state according to kernel-provided parameters.

State and persistence: RNG state is kernel CRNG/entropy-pool runtime state. Seed state may be initialized from boot and persistent seed files managed by userspace, but this header only defines the ABI.

Dependencies and integration points: depends on Linux types, ioctl, and IRQ number headers. Integrates with random core, libc, systemd/random-seed, cryptographic consumers, init systems, and vDSO getrandom support.

Risks and test signals: risks include entropy overclaiming, privileged ioctl misuse, blocking/nonblocking surprises, insecure flag misuse, and vgetrandom mmap parameter compatibility. Test early-boot getrandom behavior, entropy ioctls with/without privilege, reseed paths, invalid `rand_pool_info` lengths, and vgetrandom state allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/random.h -->
