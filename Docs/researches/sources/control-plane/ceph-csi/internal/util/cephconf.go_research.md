<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cephconf.go -->
## sources/control-plane/ceph-csi/internal/util/cephconf.go

**Purpose:** Creates a minimal `/etc/ceph/ceph.conf` and `/etc/ceph/keyring` so Ceph libraries and CLI tools have baseline configuration files.

**Important APIs and functions:** `WriteCephConfig` creates `/etc/ceph`, writes default cephx-required config if `CephConfigPath` does not exist, and calls `createKeyRingFile`. `createCephConfigRoot` and `createKeyRingFile` are small filesystem helpers. Constants define `CephConfigPath`, `cephConfigRoot`, and `keyRing`.

**Control flow, state, and persistence:** This file writes persistent host/container files under `/etc/ceph`. It preserves existing `ceph.conf` and keyring files by only creating missing paths. Permissions are `0755` for the directory and `0600` for the config; the keyring uses `os.Create` defaults.

**Dependencies and integration points:** Depends on `os`. It supports `ConnPool.Get`, which reads `CephConfigPath`, and any Ceph CLI command that expects config/keyring paths.

**Risks and test signals:** Writing under `/etc/ceph` requires permissions and can fail in restricted containers. Existing malformed files are not corrected. There are no direct tests in this subset; behavior is validated indirectly by components that need Ceph config.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cephconf.go -->
