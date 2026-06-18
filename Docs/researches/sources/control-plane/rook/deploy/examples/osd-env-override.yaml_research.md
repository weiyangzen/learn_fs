# sources/control-plane/rook/deploy/examples/osd-env-override.yaml

Purpose: demonstrates environment variable overrides for OSD pods through a named ConfigMap.

Important APIs/types/functions: `ConfigMap/rook-ceph-osd-env-override` in `rook-ceph` with data key `ASAN_OPTIONS`.

Control flow: the Rook operator can mount/read this ConfigMap and add configured environment variables to OSD daemons.

State and persistence: persists only config key/value data; OSD runtime behavior changes after pod reconciliation/restart.

Dependencies/integration: requires the operator logic that recognizes `rook-ceph-osd-env-override`.

Risks: arbitrary env overrides can destabilize OSDs; ASAN options are mostly for debug/test builds.

Test signals: OSD pod environment contains the key and OSD startup logs reflect the override.
