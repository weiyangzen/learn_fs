# sources/control-plane/ceph-csi/e2e/ceph_test.go

Purpose: unit tests for the Ceph version helper used by e2e tests.

Important APIs/types/functions: `TestCephVersionUnmarshalJSON` table-tests valid Squid string, invalid prefix, too few version numbers, invalid numeric major, missing build ID, and missing release name. `TestCephVersionGreaterEquals` table-tests major/minor/patch ordering and Reef/Squid comparisons.

Control flow: tests run in parallel at both top level and subtest level, instantiate `cephVersion`, call `UnmarshalJSON` or `GreaterEquals`, and compare fields/booleans.

State and persistence behavior: no external state.

Dependencies and integration points: standard Go testing package and helpers from `ceph.go`.

Risks: typo in error text (`expecred`) is cosmetic. Tests call `UnmarshalJSON` with unquoted strings, matching the implementation's trim behavior but not exact `encoding/json` invocation shape.

Test signals: provides direct coverage for version parsing and comparison edge cases.
