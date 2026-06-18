<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb_common_linux.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/smb_common_linux.go

Purpose: Provides Linux build-tagged SMB mount helpers, including a credential-file workaround for passwords that contain characters unsafe for direct CIFS mount option parsing.

Important APIs/functions: `NeedsCredentialsOption` detects the sensitive option shape `username=...`, `password=...` where password contains `"`, backtick, or comma. `Mount` writes sensitive options to a temporary `/tmp/*.smb.credentials` file and passes `credentials=<file>` when needed, otherwise delegates to `MountSensitive`. `CleanupSMBMountPoint`, `CleanupMountPoint`, `preparePublishPath`, `prepareStagePath`, and `Mkdir` provide Linux implementations for shared node code.

Control flow: The temp credentials file is created, written one option per line, closed and removed through a deferred cleanup, then passed as the sole sensitive mount option. Normal mounts flow directly to mount-utils.

State and persistence behavior: The only persistent side effect is target directory creation via `os.Mkdir`; credential files are transient and removed after `Mount` returns. Cleanup delegates to mount-utils and may remove mount directories.

Dependencies and integration points: Integrates with `nodeserver.go` sensitive option construction and `ContainsSpecialCharacter`. It depends on `/tmp` availability and Linux CIFS support for `credentials=`.

Risks: `NeedsCredentialsOption` intentionally relies on a narrow sensitive option layout; if node code changes the slice shape, special-character protection can silently stop applying. Temporary credential files exist briefly on disk and depend on default `os.CreateTemp` permissions.

Test signals: `smb_common_linux_test.go` directly covers positive and negative credential detection, including quote, backtick, and comma passwords. Node staging tests cover special password flow through failed fake mounts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb_common_linux.go -->
