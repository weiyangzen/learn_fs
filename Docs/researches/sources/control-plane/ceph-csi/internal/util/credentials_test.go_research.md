<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/credentials_test.go -->
## sources/control-plane/ceph-csi/internal/util/credentials_test.go

**Purpose:** Tests migration-secret detection and conversion into normal Ceph-CSI user credential fields.

**Important APIs and functions:** `TestIsMigrationSecret` checks that a non-empty `key` marks a migration secret. `TestParseAndSetSecretMapFromMigSecret` checks default admin ID, invalid empty/missing key cases, and explicit `adminId` mapping.

**Control flow, state, and persistence:** Pure in-memory table tests with parallel subtests; no temp key files are created.

**Dependencies and integration points:** Uses `reflect.DeepEqual` and Go testing. It protects migration volume request credential compatibility.

**Risks and test signals:** Coverage does not exercise actual `NewUserCredentialsWithMigration`, key file storage, cleanup, or monitor lookup. It also does not validate behavior when unrelated fields are present in the migration secret.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/credentials_test.go -->
