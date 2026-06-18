# sources/distributed-fs/juicefs/pkg/meta/utils_windows.go

## Purpose
`utils_windows.go` provides Windows-compatible metadata constants for xattrs and locks where POSIX constants are not natively available.

## Important APIs, Types, and Functions
It exports `ENOATTR`, synthetic `F_UNLCK`/`F_RDLCK`/`F_WRLCK`, and synthetic xattr create/replace constants.

## Control Flow and State
There is no runtime flow. The file defines constants selected by Windows builds.

## State and Persistence Behavior
No state is stored. The constants allow shared lock/xattr metadata logic to compile and use stable symbolic values on Windows.

## Dependencies and Integration Points
It depends only on `syscall` for `ENODATA`. It integrates with the same lock and xattr code paths as Unix platforms but maps to package-defined values rather than OS flock constants.

## Risks and Test Signals
Risks include semantic mismatch between synthetic constants and Windows/FUSE behavior, and returning `ENODATA` where callers expect another Windows error. Windows-specific lock and xattr API tests are needed for confidence.
