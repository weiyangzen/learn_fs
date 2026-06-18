# sources/control-plane/rook/pkg/operator/ceph/object/bucket/provisioner_test.go

## Purpose
`provisioner_test.go` validates key helper behavior in the RGW bucket provisioner: endpoint/domain resolution, quantity parsing, user quota reconciliation, bucket quota reconciliation, and parsing/allow-listing of OBC additional config.

## Important APIs, Types, and Functions
The suite tests `populateDomainAndPort`, `quanityToInt64`, `setUserQuota`, `setBucketQuota`, and `additionalConfigSpecFromMap`. It creates `Provisioner` instances with fake Rook and Kubernetes clients, fake CephObjectStore and Service resources, and go-ceph Admin Ops clients backed by `object.MockClient`. `numberOfCallsWithValue()` checks query-string fragments in recorded Admin Ops calls.

## Control Flow, State, and Persistence
Endpoint tests first fail missing/invalid endpoints, then accept `192.168.0.1:80`, then resolve a CephObjectStore service hostname when no StorageClass endpoint is provided. Quota tests mock Admin Ops `GET` responses for user or bucket quota state, call the setter, and verify whether a `PUT` was issued with expected query parameters. Additional config tests toggle `ROOK_OBC_ALLOW_ADDITIONAL_CONFIG_FIELDS` and `opcontroller.SetObcAllowAdditionalConfigFields()` to assert which keys are allowed and how values are parsed.

## Dependencies and Integration Points
The tests exercise go-ceph Admin Ops query encoding, Kubernetes `resource.ParseQuantity`, Rook object-store service endpoint logic, StorageClass parameter conventions, operator additional-config allow-list state, and AWS pointer helpers for expected int64 values.

## Risks
The file intentionally focuses on helper units and does not cover S3 policy/lifecycle APIs or the full provision/grant/delete/revoke flows. It uses global environment/operator allow-list state and resets it in most advanced-field subtests; this should not be parallelized casually. The test name and function are misspelled as `Quanity`, matching production code, which can make searchability worse but preserves current API names.

## Test Signals
Strong signals include quota no-op when live state already matches, disabling quotas when no config is provided, enabling and updating max object/size quotas, rejecting invalid quantities, resolving object store service hostnames, and enforcing additional config fields as disallowed by default except the baseline max quota keys when enabled.
