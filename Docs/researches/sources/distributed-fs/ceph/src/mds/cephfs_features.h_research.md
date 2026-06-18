# sources/distributed-fs/ceph/src/mds/cephfs_features.h

Purpose: Defines CephFS feature bit constants, supported feature sets, metric feature sets, current release marker, and utility function declarations.

Important APIs/types: Macros define release and capability bits from reserved 0-4 through `CEPHFS_FEATURE_BLOCKDIFF` at max 23. `CEPHFS_FEATURES_ALL`, `CEPHFS_METRIC_FEATURES_ALL`, `CEPHFS_FEATURES_MDS_SUPPORTED`, and `CEPHFS_FEATURES_CLIENT_SUPPORTED` are aggregate initializer macros. Declared utilities convert/dump feature bitsets.

Control flow: No runtime control flow. The header comments document the required maintenance path when adding releases: update current release, add feature bit, add it to all features, and update `Server::update_required_client_features()`.

State and persistence behavior: Feature numbers are protocol state; changing values is wire-compatibility sensitive. Some historical release aliases intentionally share bit values (`MULTI_RECONNECT`/`NAUTILUS`, `DELEG_INO`/`OCTOPUS`).

Dependencies and integration points: Depends on release macros, client metric type constants, `feature_bitset_t`, and `Formatter`. Used by MDS/client feature negotiation and required-client-feature policy.

Risks: Adding bits without updating all aggregate macros can make features undiscoverable. Shared aliases must be preserved for compatibility. Feature sets gate client behavior, so incorrect support claims can break older clients.

Test signals: Compile-time static assertions in the implementation, feature negotiation tests, admin dump tests, and required-client-feature policy tests.
