# sources/control-plane/rook/pkg/operator/ceph/object/dependents_test.go

## Purpose
`dependents_test.go` validates deletion-dependency behavior for standard and multisite CephObjectStores.

## Important APIs, Types, and Functions
`TestCephObjectStoreDependents` builds fake cluster contexts, fake Rook clientsets, mock Ceph executors, and mock RGW Admin Ops HTTP clients. It supplies pool lists and zonegroup/zone JSON for normal stores, secondary zones, and master zones. It creates `CephObjectStoreUser` CRs to test matching and non-matching user dependencies.

## Control Flow, State, and Persistence
Each subtest creates in-memory client state and invokes `CephObjectStoreDependents()`. The mocked Ceph executor returns pool lists and multisite JSON; the mocked HTTP client returns bucket arrays from the RGW admin bucket endpoint. The fake Rook clientset stores user CRs for listing.

## Dependencies and Integration Points
The tests cover interactions between pool discovery, Admin Ops bucket listing, Rook user CR listing, multisite zone master checks, and zonegroup peer detection. They also validate dependency labels used by deletion reporting.

## Risks and Test Signals
Signals include missing-pool skip behavior, no dependency for users pointing at other stores, user dependency for matching stores, secondary-zone deletion not blocked by buckets/users, master-zone bucket blocking when no peers exist, and master-zone peer blocking with an error when peer zones exist. Gaps include real RGW auth failures, malformed zonegroup JSON, and API-server errors while listing users.
