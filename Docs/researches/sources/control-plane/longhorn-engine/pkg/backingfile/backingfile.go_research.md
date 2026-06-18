<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backingfile/backingfile.go -->
## sources/control-plane/longhorn-engine/pkg/backingfile/backingfile.go

Purpose: opens and describes optional backing image files for backup/snapshot operations.

Important APIs/types/functions: `BackingFile` records physical size, virtual size, sector size, path, and `types.DiffDisk`. `OpenBackingFile` resolves the path, uses qemu-img metadata to detect format, opens qcow2 through `qcow.Open` or raw through sparse direct I/O, validates size alignment, and returns a populated descriptor.

Control flow and state: empty path returns nil. Unsupported image formats fail. The backing file is opened read-only for raw files; qcow handling is delegated. Persistent state remains in the backing file.

Dependencies and integration points: depends on `go-common-libs/backingimage`, `sparse-tools/sparse`, Longhorn `qcow`, util path resolution, and disk sector constants. Used by backup creation to include backing image data in delta backup operations.

Risks: qemu-img availability and backing file path resolution are environmental dependencies. Direct I/O requires sector alignment; misaligned files fail. Only raw and qcow2 are supported.

Test signals: backing image tests should cover empty path, raw/qcow2 open, unsupported formats, and misaligned size.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backingfile/backingfile.go -->
