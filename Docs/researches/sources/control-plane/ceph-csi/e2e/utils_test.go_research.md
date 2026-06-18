# sources/control-plane/ceph-csi/e2e/utils_test.go

Purpose: unit tests the ceph-csi version parser used for feature gating in e2e helpers.

Important APIs and flow: `TestParseCephCSIVersion` runs parallel subtests for `canary`, `v3.16-canary`, `v3.17-canary`, release versions such as `v3.16.8`, and invalid strings. It asserts parsed major/minor values and expected error presence.

State and persistence: no external state; pure in-memory table test.

Dependencies and integration: covers `parseCephCSIVersion` in `utils.go`, including the convention that unversioned `canary` maps to `math.MaxInt` for feature gates.

Risks and test signals: useful focused signal for version parsing, but it does not test `getCephCSIVersion` output scanning or pod exec failures. It protects VAC and other feature gates from regressions in release/canary string handling.
