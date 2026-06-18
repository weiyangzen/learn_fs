# sources/cloud-native/containers-storage/pkg/system/lchflags_bsd.go

Purpose: exposes FreeBSD file flag constants and `lchflags` syscall wrapper.

Important APIs, types, and functions: `UF_*` and `SF_*` constants plus `Lchflags`.

Control flow: converts path to a C-style byte pointer, invokes `SYS_LCHFLAGS` with the flag value, and returns syscall errno if nonzero.

State and persistence: mutates filesystem flags on a path without following symlinks.

Dependencies and integration points: depends on `unsafe` and `x/sys/unix`; selected on FreeBSD. Used by archive/metadata restoration paths needing BSD flags.

Risks and edge cases: requires permissions for system flags. Only FreeBSD build tag is present; other BSDs may need different support. Path conversion errors are returned.

Test signals: no direct tests in requested files.
