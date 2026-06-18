# sources/control-plane/rook/deploy/examples/object-shared-pools-test.yaml

Purpose: test-sized shared pool set for multiple RGW object stores.

Important APIs/types/functions: `CephBlockPool/rgw-root`, `rgw-meta-pool`, and `rgw-data-pool`, all with replica size 1 and RGW application metadata.

Control flow: Rook creates these pools; object stores with `sharedPools` can then use the same root/meta/data pool set.

State and persistence: object metadata and data are stored in the shared pools and therefore shared by dependent stores.

Dependencies/integration: supports `object-a.yaml` and `object-b.yaml` test scenarios.

Risks: one-replica pools are unsafe and pool sharing can blur failure domains between stores.

Test signals: pools ready and both `store-a` and `store-b` can start against them.
