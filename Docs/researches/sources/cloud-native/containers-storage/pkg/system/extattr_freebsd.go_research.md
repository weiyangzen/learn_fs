# sources/cloud-native/containers-storage/pkg/system/extattr_freebsd.go

Purpose: implements FreeBSD extended attribute operations on symlink paths themselves.

Important APIs, types, and functions: namespace constants, `ExtattrGetLink`, `ExtattrSetLink`, and `ExtattrListLink`.

Control flow: get/list first call the FreeBSD syscall with nil buffer to get size, then allocate and call again. Missing attributes return nil, nil. Set ensures empty data is non-nil and passes the data pointer. List decodes FreeBSD's length-prefixed attribute names.

State and persistence: reads and writes filesystem extended attributes.

Dependencies and integration points: depends on `os`, `unsafe`, and `x/sys/unix`; selected on FreeBSD. Used by metadata/xattr preservation paths.

Risks and edge cases: `ExtattrSetLink` indexes `data[0]` even after setting empty data to `[]byte{}`, which is still length zero and would panic for empty input. Attribute list parsing silently stops on malformed length overrun.

Test signals: no FreeBSD extattr tests in requested files.
