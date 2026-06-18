# sources/control-plane/ceph-csi/internal/nvmeof/nodeserver/security.go

Purpose: Provides node-side DH-CHAP authentication setup for `nvme connect` requests by retrieving or creating keys through the same KMS/DEKStore scheme as the controller.

Important APIs/types/functions: `getOrInitSecurityKeys` lazily initializes a `SecurityKeyManager`. `setupDHCHAPAuth` attaches `HostDhchapKey` and optional `SubsystemDhchapKey` to a `nvmeof.ConnectRequest`.

Control flow: The node initializes security keys using the requested KMS ID and CSI secrets. If the KMS needs an external DEKStore, it creates user credentials, resolves the RBD volume by volume ID, wraps it in `NewRBDVolumeDEKStore`, and attaches it. It then calls DH-CHAP get-or-create helpers using the node server's node ID, subsystem NQN, and connect host NQN. Bidirectional mode retrieves the subsystem key too.

State and persistence behavior: Cacheable KMS managers are stored on the `NodeServer`; metadata KMS requires a volume-specific DEKStore per call. Keys are persisted via the configured KMS/DEKStore, commonly RBD image metadata for metadata KMS.

Dependencies and integration points: Depends on `nvmeof` crypto/DH-CHAP, RBD volume resolution via `GenVolFromVolID`, user credential migration helper, CSI secrets, and the connection info built in `nodeserver.go`.

Risks: Same cache scoping concern as controller security: cached manager is not keyed by KMS ID or secret material. Because node can create keys if missing, node and controller key-generation races are possible if gateway AddHost and node connect overlap with missing metadata. Metadata KMS path requires valid RBD credentials on node.

Test signals: No direct tests. Behavior requires integration coverage with KMS, RBD metadata, and `nvme connect`.
