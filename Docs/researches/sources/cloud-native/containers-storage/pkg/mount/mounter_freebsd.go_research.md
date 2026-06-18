# sources/cloud-native/containers-storage/pkg/mount/mounter_freebsd.go

Purpose: implements FreeBSD mount operations using `nmount` through cgo.

Important APIs, types, and functions: `allocateIOVecs` and platform `mount`.

Control flow: the function builds a key/value iovec list starting with `fspath`. Data options are split into names and values; a `bind` data option switches to `nullfs` with `target=device`, otherwise it uses the requested filesystem type and `from=device`. It calls `C.nmount` and converts errno to a Go error string.

State and persistence: mutates the FreeBSD mount table. Allocated C strings are freed with defers after the syscall.

Dependencies and integration points: depends on cgo FreeBSD mount headers, `fmt`, `strings`, and `unsafe`. Used by high-level `Mount` on `freebsd && cgo`.

Risks and edge cases: data option parsing assumes `key=value`; options without values still append an empty value. cgo is required. Error wrapping does not use `mountError`, unlike Linux.

Test signals: no FreeBSD tests in the requested set; correctness depends on platform integration.
