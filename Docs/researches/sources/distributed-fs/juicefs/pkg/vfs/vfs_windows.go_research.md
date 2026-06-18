# sources/distributed-fs/juicefs/pkg/vfs/vfs_windows.go

## Purpose
This Windows-specific file supplies the minimal platform replacements needed by the shared VFS code: Windows-compatible `O_ACCMODE` and `F_UNLCK` constants plus `ChFlags` for setting inode flags through metadata.

## Important APIs, Types, and Functions
`O_ACCMODE` is derived from WinFsp cgofuse's `fuse.O_ACCMODE`. `F_UNLCK` is set to `0x01`. `ChFlags` rejects internal special nodes, checks setattr permission when required, and calls `Meta.SetAttr` with `meta.SetAttrFlag`.

## Control Flow and State
`ChFlags` constructs an attr with only `Flags` populated. If the context enforces permission checks, it first asks metadata to validate the flag change. It then persists the new flag value with `SetAttr`. No local VFS state is updated here; state persistence is entirely in the metadata layer.

## Dependencies and Integration Points
The file depends on `github.com/winfsp/cgofuse/fuse` for Windows open-flag semantics and on JuiceFS `meta` for flag mutation. It is selected only for Windows builds and complements the Unix-only `SetAttr`, lock, statfs, access, and ioctl implementation.

## Risks and Edge Cases
The implementation only handles flag changes and leaves other platform-specific operations to other files. Internal nodes are protected with `EPERM`. The hard-coded unlock constant must stay compatible with WinFsp/cgofuse lock semantics used elsewhere.

## Test Signals
No Windows-specific test appears in this target set. Shared VFS tests cover cross-platform code paths, but `ChFlags` needs Windows or build-tag-specific coverage to validate permission behavior and WinFsp constant compatibility.
