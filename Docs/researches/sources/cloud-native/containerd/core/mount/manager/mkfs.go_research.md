<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/mkfs.go -->
# sources/cloud-native/containerd/core/mount/manager/mkfs.go

Purpose: built-in mount transformer that creates and formats a writable filesystem image file before subsequent mounts use it.

Important APIs/types/functions: `mkfs` holds allowed `os.Root` instances; `(*mkfs).Transform` consumes `X-containerd.mkfs.size`, `.fs`, and `.uuid` options; `createWritableImage` runs the selected mkfs binary. Supported filesystems are `ext2`, `ext3`, `ext4`, and `xfs`; default is `ext4`.

Control flow: transform chooses an allowed root by source prefix, strips mkfs options, parses size with `go-units.RAMInBytes`, validates filesystem type, creates/truncates the image file when absent, appends uuid-specific arguments, and runs `mkfs.<fs>`. If the file already exists it currently only leaves a TODO for magic checking and returns the mount unchanged except for consumed options.

State and persistence: creates a file under an allowed root, truncates it to the requested size, and formats it using external system tools. The returned mount no longer contains internal mkfs options.

Dependencies and integration points: called from `manager.go` for `mkfs/<type>` transform prefixes; used before loopback or other mounts that need an initialized image. Depends on `os.Root`, external `mkfs.ext*`/`mkfs.xfs`, `errdefs`, and logging.

Risks: external binaries are resolved from PATH at transform time; existing files are not validated for filesystem type/uuid/size; prefix root matching can be ambiguous; xfs/ext format behavior depends on installed tools and permissions. A missing `mkfs.size` fails activation.

Test signals: root integration tests indirectly exercise formatted ext4 image flows through loopback setup, but this file lacks direct unit tests for option parsing, unsupported fs, existing file handling, and external command failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/mkfs.go -->
