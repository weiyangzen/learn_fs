<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cephcmds.go -->
## sources/control-plane/ceph-csi/internal/util/cephcmds.go

**Purpose:** Provides shared Ceph command and RADOS helper operations: external command execution, pool ID/name lookup, object creation/deletion, and OSD blocklist management.

**Important APIs and functions:** `ExecuteCommandWithNSEnter`, `ExecCommand`, and `ExecCommandWithTimeout` run external commands with separated stdout/stderr and sanitized logging. `GetPoolID`, `GetPoolName`, and `GetPoolIDs` resolve pools through the global connection pool. `CreateObject` and `RemoveObject` create/delete RADOS objects with namespace support and map RADOS errors to `ErrObjectExists`/`ErrObjectNotFound`. `AddCephBlocklist` and `RemoveCephBlocklist` use go-ceph OSD admin APIs and constants `AutoBlocklistTime`/`MaxBlocklistTime`.

**Control flow, state, and persistence:** Command helpers capture buffers, run subprocesses, and log success or wrapped errors unless context is `context.TODO()`. Timeout execution uses a new background timeout context and wraps deadline exceeded. Pool and object helpers acquire pooled RADOS connections or `ClusterConnection`, open IO contexts, optionally set namespaces, and mutate Ceph pools. Blocklisting connects to the cluster, builds `osdAdmin.AddressEntry`, formats IPv4/IPv6 nonce addresses when needed, and adds/removes blocklist entries.

**Dependencies and integration points:** Depends on `os/exec`, net parsing, go-ceph `rados` and OSD admin packages, internal logging, credentials, connection pool, and secret stripping. It integrates with provisioning, fencing/unfencing, OMAP/object lifecycle, and any code needing command-line fallback.

**Risks and test signals:** Subprocess calls are sensitive to secret leakage, timeout semantics, and stderr handling. `ExecCommandWithTimeout` ignores the caller context for cancellation and always bases timeout on `context.Background`. RADOS helpers require balanced pooled connection use. Blocklist formatting must handle IPv6 brackets and nonce/range modes correctly. `cephcmds_test.go` covers timeout and stdout behavior only; cluster operations need integration coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cephcmds.go -->
