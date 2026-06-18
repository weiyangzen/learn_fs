# sources/distributed-fs/ceph-client/security/apparmor/Kconfig

## Purpose
This Kconfig file controls whether the AppArmor Linux Security Module is built and which optional policy introspection, hashing, raw binary export, paranoid policy-load verification, debug, and KUnit test features are compiled. It is the top-level build-time contract that determines which code paths in this directory are present, especially `crypto.c` and raw policy export support in `apparmorfs.c`.

## Important symbols
- `SECURITY_APPARMOR` depends on `SECURITY` and `NET`, selects `AUDIT`, `SECURITY_PATH`, `SECURITYFS`, and `SECURITY_NETWORK`, and gates the main `apparmor.o` object.
- `SECURITY_APPARMOR_DEBUG`, `SECURITY_APPARMOR_DEBUG_ASSERTS`, and `SECURITY_APPARMOR_DEBUG_MESSAGES` control assertion and diagnostic behavior around `AA_BUG`, `AA_DEBUG`, and the `apparmor.debug` boot/module parameter.
- `SECURITY_APPARMOR_INTROSPECT_POLICY` enables policy introspection through apparmorfs and is a prerequisite for hash and export features.
- `SECURITY_APPARMOR_HASH` selects `CRYPTO_LIB_SHA256` and compiles hash support used by `crypto.c` and hash files in apparmorfs.
- `SECURITY_APPARMOR_EXPORT_BINARY` selects zstd compression/decompression and enables raw binary policy export and related apparmorfs symlinks/files.
- `SECURITY_APPARMOR_PARANOID_LOAD` defaults to full policy verification during load.
- `SECURITY_APPARMOR_KUNIT_TEST` builds the policy unpack KUnit test object.

## Control flow and integration
The options flow into `Makefile` object selection and into `#ifdef CONFIG_SECURITY_APPARMOR_HASH` / `#ifdef CONFIG_SECURITY_APPARMOR_EXPORT_BINARY` conditionals. Enabling AppArmor also requires securityfs and path/network LSM hooks, matching the code's reliance on `/sys/kernel/security/apparmor`, path names, sockets, and kernel audit.

## State and persistence
Kconfig choices are persisted in the kernel build configuration. Runtime state such as loaded profiles, namespace revisions, profile hashes, and raw policy data only exists if the corresponding features are compiled and then enabled at runtime through globals such as `aa_g_hash_policy` and `aa_g_export_binary`.

## Dependencies
The file depends on kernel security, networking, audit, securityfs, crypto SHA-256, zstd, and KUnit subsystems. A mismatch between selected options and code expectations changes exported apparmorfs features and can affect userspace tooling compatibility.

## Risks
Disabling paranoid load verification or policy hashing/export can improve memory or load-time behavior but reduces diagnosability and integrity checking. Introspection and raw export increase memory use because policy data and hashes may be retained. Debug asserts can expose latent kernel warnings in production-like environments if enabled.

## Test signals
Build matrices should cover `SECURITY_APPARMOR=y`, hash on/off, export binary on/off, paranoid load on/off, and `SECURITY_APPARMOR_KUNIT_TEST`. Runtime smoke tests should check expected feature files in securityfs and that policy load/replace/remove behavior matches compiled options.
