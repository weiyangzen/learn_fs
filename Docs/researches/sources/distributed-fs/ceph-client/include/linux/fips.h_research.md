# sources/distributed-fs/ceph-client/include/linux/fips.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fips.h` declares the kernel FIPS mode flag and helper. The source was read as a complete 18-line file for this report.

## Important APIs, Types, and Functions

It declares external `fips_enabled` and inline `fips_fail_notify()` returning `fips_enabled`.

## Control Flow

Cryptographic or compliance-sensitive code can call `fips_fail_notify()` to determine whether a failure should trigger FIPS-mode behavior. Actual notification/control is elsewhere.

## State and Persistence Behavior

The only referenced state is global `fips_enabled`, typically initialized from boot/config policy. The header does not store or persist it.

## Dependencies and Integration Points

It integrates with crypto, integrity, and boot parameter code that gates behavior in FIPS mode.

## Risks and Edge Cases

The helper currently mirrors `fips_enabled`; callers expecting richer notification semantics must rely on external implementation/policy.

## Test Signals

FIPS boot parameter tests, crypto selftest failure behavior, and build coverage for code paths using `fips_fail_notify()`.
