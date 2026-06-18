# sources/control-plane/rook/tests/external-cluster/external-config.ini

Purpose: this INI-style fixture supplies external-cluster configuration keys used by Rook external cluster tests or scripts. It enumerates expected configuration knobs for Ceph conf/keyring paths, cluster names, namespaces, RGW, monitoring, CephFS, RBD, topology, and upgrade behavior.

Important APIs/types/functions: no code APIs exist. The `[Configurations]` section is the contract. Notable non-empty defaults include `rbd-data-pool-name = replicapoolconfig` and `rados-namespace = radosnamespace2`; all other keys are intentionally present but blank.

Control flow: parsing is performed by external scripts/tests. This file is static data and defines which options are available to callers.

State and persistence behavior: state is persisted as a test fixture. It does not mutate at runtime unless a test harness writes over it.

Dependencies and integration points: integrates with external cluster resource generation paths that expect exact key names such as `cephfs-filesystem-name`, `rgw-endpoint`, `topology-failure-domain-label`, and `upgrade`.

Risks: blank values rely on parser defaults, so tests may silently change behavior if defaults change elsewhere. Typos or stale option names are hard to detect without end-to-end external-cluster tests. The fixture encodes specific pool and namespace names that may collide if reused outside an isolated test.

Test signals: useful tests verify the parser accepts this complete key set, honors the non-empty RBD pool and rados namespace values, and rejects or surfaces missing required external-cluster parameters.
