# sources/distributed-fs/juicefs/pkg/meta/utils_darwin.go

## Purpose
`utils_darwin.go` defines Darwin-specific errno, flock, and xattr constants for metadata code.

## Important APIs, Types, and Functions
It exports `ENOATTR`, `F_UNLCK`, `F_RDLCK`, `F_WRLCK`, `XattrCreateOrReplace`, `XattrCreate`, and `XattrReplace`.

## Control Flow and State
There is no runtime control flow. The file maps package-level constants to `syscall` and `golang.org/x/sys/unix` values selected by the Darwin build.

## State and Persistence Behavior
No state is stored. These constants affect how metadata operations interpret platform lock and extended attribute flags.

## Dependencies and Integration Points
It integrates with lock code, xattr create/replace handling in `tkv.go`, and portable metadata APIs. It depends on Go's `syscall` package and `x/sys/unix`.

## Risks and Test Signals
Risks are mostly portability regressions if Darwin constants diverge from kernel/FUSE expectations. Platform-specific xattr and locking tests on macOS are the best signal.
