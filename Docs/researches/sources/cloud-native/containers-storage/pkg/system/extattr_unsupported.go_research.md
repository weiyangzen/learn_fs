# sources/cloud-native/containers-storage/pkg/system/extattr_unsupported.go

Purpose: provides unsupported stubs for FreeBSD-style extattr functions on non-FreeBSD platforms.

Important APIs, types, and functions: zero namespace constants, `ExtattrGetLink`, `ExtattrSetLink`, and `ExtattrListLink`.

Control flow: each function immediately returns `ErrNotSupportedPlatform`.

State and persistence: no filesystem mutation or read occurs.

Dependencies and integration points: selected for `!freebsd`; uses the shared unsupported sentinel. This keeps cross-platform callers compiling.

Risks and edge cases: namespace constants are zero and should not be used for real extattr work on unsupported platforms. Callers must handle unsupported errors.

Test signals: no direct tests in requested files.
