# sources/distributed-fs/ceph-client/security/selinux/Kconfig

## Purpose
This Kconfig fragment defines the build-time configuration surface for SELinux support in the kernel tree. It controls whether SELinux is built, whether it can be disabled at boot, whether development/permissive support is enabled, whether AVC statistics are exposed, and the sizes of internal SELinux hash/cache structures.

## Important Options
- `SECURITY_SELINUX`: top-level SELinux enable. It depends on `SECURITY_NETWORK`, `AUDIT`, `NET`, and `INET`, selects `NETWORK_SECMARK`, and defaults to off.
- `SECURITY_SELINUX_BOOTPARAM`: adds the `selinux=` boot parameter, allowing `selinux=0` to disable SELinux at boot.
- `SECURITY_SELINUX_DEVELOP`: enables development support, defaults to on, and starts permissive unless `enforcing=1` is passed.
- `SECURITY_SELINUX_AVC_STATS`: enables per-CPU AVC statistics visible through selinuxfs.
- `SECURITY_SELINUX_SIDTAB_HASH_BITS`: controls sidtab bucket count as `2^bits`, range 8..13, default 9.
- `SECURITY_SELINUX_SID2STR_CACHE_SIZE`: sizes the SID-to-context string cache, default 256, with zero disabling it.
- `SECURITY_SELINUX_AVC_HASH_BITS`: controls AVC hash buckets as `2^bits`, range 9..14, default 9.
- `SECURITY_SELINUX_DEBUG`: enables SELinux debug code and is intended for developers, often combined with dynamic debug.

## Control Flow and Build Effects
Kconfig does not execute runtime logic itself. It emits configuration symbols consumed by the SELinux Makefile and C code. `SECURITY_SELINUX` controls whether `selinux.o` is linked. The hash-size symbols compile into sidtab and AVC constants, and `SECURITY_SELINUX_AVC_STATS` toggles stats increments and exported selinuxfs data. `SECURITY_SELINUX_DEVELOP` and boot parameter options influence initialization and runtime enforcement toggles elsewhere in SELinux code.

## State and Persistence Behavior
The file defines compile-time defaults only. Resulting kernel config persists in the kernel build configuration. Runtime SELinux policy, enforcing state, AVC entries, and sidtab contents are handled by other SELinux components and by boot/runtime settings.

## Dependencies and Integration Points
SELinux is made dependent on networking and audit support, reflecting that SELinux hooks include network labeling/secmark behavior and audit logging. `NETWORK_SECMARK` is selected to support packet labeling. Dynamic debug documentation is referenced for debug output control.

## Risks and Edge Cases
- Enabling `SECURITY_SELINUX_BOOTPARAM` permits disabling SELinux via kernel command line, which is useful for distributable kernels but weakens mandatory enablement.
- `SECURITY_SELINUX_DEVELOP=y` defaults to permissive behavior unless overridden, which is appropriate for policy development but risky in production defaults.
- Too-small sidtab or AVC hash settings can increase chain lengths and lookup latency; too-large settings consume more memory.
- `SECURITY_SELINUX_AVC_STATS` adds stats overhead, small but present on hot permission paths.

## Test Signals
Validation includes Kconfig dependency resolution, builds with SELinux on/off, boot tests for `selinux=0` and `enforcing=1`, selinuxfs visibility for `/sys/fs/selinux/avc/cache_stats` and sidtab stats, and performance tests under different `*_HASH_BITS` settings.
