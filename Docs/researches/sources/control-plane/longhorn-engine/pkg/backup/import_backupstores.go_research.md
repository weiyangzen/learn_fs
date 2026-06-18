<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backup/import_backupstores.go -->
## sources/control-plane/longhorn-engine/pkg/backup/import_backupstores.go

Purpose: blank-import registry file for Longhorn backupstore drivers.

Important APIs/types/functions: imports Azure, CIFS, NFS, S3, and VFS backupstore packages for side-effect registration.

Control flow, state, and persistence: no functions. Import side effects register supported backup target backends in the backupstore package.

Dependencies and integration points: required by backup create/restore paths so URLs for those stores resolve.

Risks: removing or build-tag excluding this file can silently remove backup target support. Blank imports make support implicit.

Test signals: backupstore URL integration tests for each provider validate this file indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backup/import_backupstores.go -->
