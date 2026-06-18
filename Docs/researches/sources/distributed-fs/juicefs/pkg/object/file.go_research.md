# sources/distributed-fs/juicefs/pkg/object/file.go


Purpose: implements local filesystem storage registered as `file`.

Important APIs and flow: `filestore` maps object keys to paths under `root`. `Head` uses `Lstat`, follows symlinks for target metadata, and returns `file` metadata. `Get` opens files and returns empty readers for directories or out-of-range offsets; ranged reads use `SectionReaderCloser`. `Put` creates directories for slash keys, otherwise writes to a temp file from `TmpFilePath` and renames atomically unless `PutInplace` is set. `Copy` streams through `Get`/`Put`; `Delete` ignores missing paths. `readDirSorted` filters non-regular files, handles symlinks based on `followLink`, and sorts entries. `List` implements delimiter `/` listing and may include the directory itself.

State and persistence: persistent state is the local directory tree. Temporary `.jfs.*.tmp.*` files exist during non-inplace writes. Symlinks are supported through `Symlink` and `Readlink`.

Dependencies and integration: uses platform-specific `getOwnerGroup` and `Chtimes`, shared `file` type, `bufPool`, `TryCFR`, `PutInplace`, `FileSystem`, and `SupportSymlink`.

Risks: path construction differs depending on whether root ends with `/`; callers must understand leading slash behavior. Global `PutInplace` weakens atomic write semantics. `TryCFR` currently uses `io.Copy` rather than explicit copy-file-range here. Permission errors during list are skipped.

Test signals: `TestDisk`, `TestDisk2`, and `TestListAllWithDelimiterDeepStart` exercise object and filesystem behavior.
