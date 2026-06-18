# sources/control-plane/ceph-csi/e2e/ceph.go

Purpose: e2e helper for parsing and comparing Ceph cluster versions.

Important APIs/types/functions: predefined major-version sentinels `CephVersionSquid`, `Tentacle`, and `Umbrella`; `cephVersion` fields and accessors; `String`; `UnmarshalJSON`; `GreaterEquals`; `getCephVersion`.

Control flow: `getCephVersion` runs `ceph --format=json version` in the toolbox pod, unmarshals the `version` string into `cephVersion`, and tests can gate behavior with `GreaterEquals`.

State and persistence behavior: no persistence; state is parsed version data returned to tests.

Dependencies and integration points: depends on e2e framework, `execCommandInToolBoxPod`, `rookNamespace`, Ceph CLI JSON output, and Go JSON unmarshalling.

Risks: parser assumes strings beginning `ceph version` with at least five space-separated parts and release at index 4. Future Ceph format changes can break tests.

Test signals: direct unit tests in `ceph_test.go` cover parse errors and comparisons.
