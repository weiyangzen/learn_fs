<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/credentials.go -->
## sources/control-plane/ceph-csi/internal/util/credentials.go

**Purpose:** Converts Kubernetes/CSI secret maps into temporary Ceph key files and user IDs for go-ceph/CLI authentication, including legacy admin fields and migration secret formats.

**Important APIs and types:** `Credentials` holds `ID` and `KeyFile`. Constructors are `NewUserCredentials`, `NewAdminCredentials`, and `NewUserCredentialsWithMigration`. `DeleteCredentials`, `storeKey`, `newCredentialsFromSecret`, `GetMonValFromSecret`, `ParseAndSetSecretMapFromMigSecret`, and `isMigrationSecret` provide lifecycle and parsing helpers.

**Control flow, state, and persistence:** Constructors validate required map fields, write key contents to a temp file under `/tmp/csi/keys`, and return the temp path. Admin credentials prefer `userID/userKey` and fall back to deprecated `adminID/adminKey`. Migration secrets with key `key` are converted to `userKey` and `userID`, defaulting the user to `admin` unless `adminId` is set. `DeleteCredentials` removes the temp key file.

**Dependencies and integration points:** Depends on `os`, internal logging, and constants consumed by RADOS connection code. It integrates with CSI request secrets, migration volume flows, and `connPool.Get`.

**Risks and test signals:** `/tmp/csi/keys` must exist and be writable. Temp key files must be removed by callers to avoid credential residue. `newCredentialsFromSecret` indexes `secrets[keyField]` without checking presence separately, so missing and empty values share the same error. Tests cover migration secret detection and conversion only, not temp file creation, admin fallback, monitor extraction, or cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/credentials.go -->
