# sources/control-plane/rook/deploy/examples/pool-builtin-mgr.yaml

Purpose: manages the built-in Ceph manager pool through a Rook `CephBlockPool` CR.

Important APIs/types/functions: `CephBlockPool/builtin-mgr` with `spec.name: .mgr`, failure domain `host`, replicated size 3, safe replica requirement, compression disabled, and mirroring disabled.

Control flow: Rook reconciles the CR against the existing or desired `.mgr` Ceph pool.

State and persistence: `.mgr` stores Ceph manager module state and metadata.

Dependencies/integration: depends on Ceph mgr expectations and enough OSDs for three replicas.

Risks: changing the manager pool can affect Ceph dashboard/modules; deleting it may disrupt manager services.

Test signals: `.mgr` pool exists with configured size and Ceph mgr remains healthy.
