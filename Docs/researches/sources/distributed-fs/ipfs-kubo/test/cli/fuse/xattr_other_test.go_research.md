# sources/distributed-fs/ipfs-kubo/test/cli/fuse/xattr_other_test.go

Purpose: non-Linux stub for the FUSE xattr helper.

Important APIs/functions: build tag `!linux`, `getXattr(_, _ string)`, `runtime.GOOS`, and formatted error creation.

Control flow: any call returns an error stating xattr is unsupported on the current OS. In practice, the xattr subtest in `fuse_test.go` skips unless `runtime.GOOS == "linux"`.

State/persistence: none.

Dependencies/integration: keeps the `fuse` package compiling on Darwin/FreeBSD without importing Linux-only syscall APIs.

Risks/test signals: intentionally no behavioral xattr coverage off Linux; platform-specific xattr support on other OSes is not exercised by these tests.
