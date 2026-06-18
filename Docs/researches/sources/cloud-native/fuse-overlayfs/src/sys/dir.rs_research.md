# sources/cloud-native/fuse-overlayfs/src/sys/dir.rs

## Purpose
`sys/dir.rs` wraps libc `DIR*` iteration behind a small Rust API used by overlay directory merging and cleanup paths.

## Important APIs, Types, And Functions
`RawDirEntry` carries entry name bytes, inode number, and `d_type`. `DirStream` owns a `*mut libc::DIR`. `DirStream::from_fd` consumes an `OwnedFd` with `fdopendir`; `DirStream::from_raw_fd` duplicates a borrowed fd first; `next_entry` wraps `readdir`; `Drop` closes the stream with `closedir`. An unsafe `Send` impl is justified by exclusive `&mut self` iteration.

## Control Flow
Callers open a directory fd, construct a `DirStream`, loop on `next_entry`, and use returned raw names/types for merge or deletion decisions. End of directory returns `None`; syscall failure during `readdir` is not separately surfaced.

## State And Persistence
The only state is the owned DIR pointer and the fd consumed by `fdopendir`. No persistent data is written. `from_raw_fd` avoids stealing caller ownership by duping the fd.

## Dependencies And Integration Points
`overlay.rs` uses `DirStream` for loading layer directories and emptying upper directories before rename-over-dir. Datasource implementations can also expose it through `opendir`. It depends on libc and the project `FsError`/`FsResult` error wrapper.

## Risks
`readdir` errors are indistinguishable from end-of-directory. `d_type` can be `DT_UNKNOWN`, so callers must stat when type matters. The unsafe `Send` contract relies on higher-level locking or exclusive ownership; sharing a `DirStream` concurrently would be invalid.

## Test Signals
Unit tests create temporary directories and verify normal listing includes `.`/`..` and files/subdirs, and an empty directory only lists `.`/`..`.
