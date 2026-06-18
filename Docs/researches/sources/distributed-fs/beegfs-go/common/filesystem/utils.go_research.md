<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/utils.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/utils.go

Purpose: user-facing file type formatting helper.

Important APIs/types/functions: `FileTypeToString`.

Control flow: checks directory and regular file first, then mode type bits for symlink, pipe, socket, device/char device, irregular, and unknown fallback.

State and persistence: none.

Dependencies and integration points: depends on `os.FileMode`; useful for CLI/reporting code that should not expose Go's compact file-mode type strings directly.

Risks: ordering matters for device/char-device interpretation. Unknown types return `fmt.Sprintf` with raw mode type.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/utils.go -->
