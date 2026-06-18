# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-generic.c

Read completely: 622 lines.

This is the Linux SPL generic module implementation. It owns module-level initialization/finalization, hostid handling, pseudo-random byte generation, Solaris DDI conversion helpers, user/kernel copy wrappers, and block-device uevent signaling.

Key responsibilities:
- Defines/export `spl_hostid` and dummy process `p0`.
- Implements `random_get_pseudo_bytes()` using per-CPU xoshiro256++ state seeded from Linux `get_random_bytes()`.
- Implements `ddi_strtol`, `ddi_strtoll`, and `ddi_strtoull` through a macro-generated parser.
- Implements `ddi_copyin()` and `ddi_copyout()` with `FKIOCTL` kernel-buffer bypass.
- Signals `KOBJ_CHANGE` uevents for block devices.
- Reads `/etc/hostid` or the configured `spl_hostid_path`, preserving Linux hostid behavior.
- Initializes/finalizes SPL subsystems in dependency order.

Important implementation details:
- Per-CPU PRNG state avoids atomic operations; comments state it is not for cryptographic-quality callers and that callers needing stronger randomness should use `random_get_bytes()`.
- Random initialization jumps the PRNG sequence per CPU to avoid practical overlap and has a fallback if Linux returns an all-zero seed.
- Hostid reading uses only the first four bytes of the file, matching glibc/coreutils behavior.
- Initialization order is: random, kmem/vmem, TSD, proc, kstat, taskq, kmem cache, zlib, zone. Failure unwinds in reverse order.
- Module metadata registers SPL as GPL with OpenZFS version strings.

Dependencies and interactions:
- Coordinates many SPL subsystems: kmem, vmem, TSD, proc, kstat, taskq, kmem cache, zlib, and zones.
- Exported helpers are used broadly by OpenZFS Linux code.

Reliability notes:
- `ddi_strtox` overflow detection is simple and based on wraparound of the accumulating value.
- `spl_signal_kobj_evt()` has compile-time failure if the kernel no longer exposes a supported way to obtain the block-device kobject.
