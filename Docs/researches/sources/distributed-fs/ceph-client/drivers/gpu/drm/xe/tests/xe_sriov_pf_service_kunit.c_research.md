# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_sriov_pf_service_kunit.c

## Purpose

`xe_sriov_pf_service_kunit.c` tests PF/VF ABI version negotiation for SR-IOV PF service setup.

## Important APIs, Types, and Functions

- Setup: `pf_service_test_init()` creates a fake Tiger Lake PF, initializes SR-IOV and PF service versions, and sanity-checks base/latest versions.
- Negotiation tests: `pf_negotiate_any`, base match/newer/next/older/previous cases, and latest match/newer/next/older/previous cases.
- Suite: `pf_service_suite`.

## Control Flow

After setup, each test calls `pf_negotiate_version` with requested major/minor values and asserts success/failure plus returned negotiated version. `ANY` selects latest. Older-than-base cases fail. Newer-than-latest requests clamp to latest. Some multi-major cases include FIXME failure branches because multi-version policy is not fully modeled yet.

## State and Persistence Behavior

The fake device stores SR-IOV PF service base/latest versions. Tests read negotiation outputs but do not mutate service state after init.

## Dependencies and Integration Points

It depends on fake Xe device setup, `xe_sriov_init`, `xe_sriov_pf_service_init`, VF2PF handshake version constants, and `pf_negotiate_version`.

## Risks and Edge Cases

- Multi-major-version support is explicitly incomplete in test expectations.
- Skip paths depend on minor/major values; coverage changes as ABI versions change.
- Negotiation policy is compatibility-critical for PF/VF interoperability.

## Test Signals

Passing tests indicate base/latest versions are defined and ordered, wildcard negotiation selects latest, compatible requests succeed, unsupported older requests fail, and newer requests clamp according to current policy.
