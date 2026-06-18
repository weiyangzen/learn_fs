<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/fips.c -->
# sources/distributed-fs/ceph-client/crypto/fips.c

Purpose: Provides the kernel crypto FIPS-mode switch, metadata sysctls, and a notification hook for crypto subsystem FIPS failures.

Important APIs/types/functions: `fips_enabled` is the exported global mode flag. `fips_fail_notif_chain` is an exported blocking notifier chain. `fips_enable()` parses the early `fips=` boot option. The sysctl table exposes `fips_enabled`, `fips_name`, and `fips_version` under `/proc/sys/crypto`. `fips_fail_notify()` calls the failure notifier chain.

Control flow: At early boot, `__setup("fips=", fips_enable)` sets `fips_enabled` when the option is nonzero. Module init registers the crypto sysctl table; exit unregisters it. Runtime callers invoke `fips_fail_notify()` to broadcast a FIPS module failure to registered listeners.

State and persistence behavior: `fips_enabled` is global process lifetime state set by boot parameters and exported read-only via sysctl mode `0444`. Module name/version strings are static. The notifier chain has kernel runtime registrations but no persisted state.

Dependencies and integration points: Integrates with Linux sysctl, notifier chains, `utsrelease`, and crypto code that gates behavior on `fips_enabled`, such as HMAC key length checks, KDF self-test handling, and jitterentropy panic-on-permanent-health-failure paths.

Risks: Treating `fips_enabled` as a mutable ordinary integer can produce inconsistent policy if code attempts late writes, although the exposed sysctl is read-only. Notifier callbacks run in a blocking chain and must avoid unsafe contexts. FIPS enforcement is distributed; missing checks in individual algorithms are not caught here.

Test signals: Boot with `fips=0` and `fips=1`, verify `/proc/sys/crypto/fips_enabled`, `fips_name`, and `fips_version`, trigger algorithm self-test/failure paths, and validate notifier callbacks receive `fips_fail_notify()` events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/fips.c -->
