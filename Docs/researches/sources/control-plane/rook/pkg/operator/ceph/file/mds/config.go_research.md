# sources/control-plane/rook/pkg/operator/ceph/file/mds/config.go

## Purpose
This file generates MDS CephX keyrings and writes default MDS-specific options to the Ceph monitor config store. It ensures each MDS daemon has appropriate Ceph capabilities, supports key rotation, removes legacy key Secrets, and sets cache and filesystem-join config.

## Important APIs, Types, and Functions
`generateKeyring` builds user `mds.<daemonID>`, requests caps `mon allow profile mds`, `osd allow *`, and `mds allow`, optionally rotates the key, deletes the legacy Secret named by `mdsConfig.ResourceName`, and writes the rendered keyring through the keyring secret store. `setDefaultFlagsMonConfigStore` computes `mds_cache_memory_limit` from resource memory limit or request and always sets `mds_join_fs` for `mds.<id>`.

## Control Flow, State, and Persistence
Keyring generation persists Ceph auth keys in Ceph and Kubernetes Secret data through the keyring store. If `shouldRotateCephxKeys` is true, it replaces the generated/existing key with `RotateKey`. Legacy Secret deletion is best-effort: not-found is debug, other errors are warnings. Config-store updates persist in Ceph monitor config for each MDS daemon. Memory limit takes precedence over request; custom factor fields override defaults.

## Dependencies and Integration Points
The file depends on Rook's keyring secret store, Ceph monitor config store, Kubernetes Secret API, MDS resource settings, `opcontroller` namespaced logging, and the `mdsConfig` generated during deployment startup. Its Secret resource version is later applied to MDS Deployment annotations to trigger restarts on key changes.

## Risks
The rendered keyring grants broad `osd allow *` and full `mds allow`, so key leakage is high impact. Config options are applied to running daemons and can fail if Ceph rejects runtime changes; callers ignore only EPERM in the deployment path. The map iteration order for config options is not deterministic, so tests should not depend on command order. Memory calculations cast float products to integer bytes, truncating fractional results.

## Test Signals
Signals include generated keyring contents, Secret resource version changes, legacy Secret deletion behavior, key rotation path, correct `mds_cache_memory_limit` values for limits and requests, custom factor behavior, and always setting `mds_join_fs`.
