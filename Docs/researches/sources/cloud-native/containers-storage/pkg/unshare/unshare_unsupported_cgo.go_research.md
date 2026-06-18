# sources/cloud-native/containers-storage/pkg/unshare/unshare_unsupported_cgo.go

Purpose: cgo placeholder for platforms that have C files in the package but no usable unshare C implementation.

Important APIs/types/functions: imports C with `CPPFLAGS: -DUNSHARE_NO_CODE_AT_ALL`.

Control flow: no operational C code is compiled; the import satisfies Go's cgo package requirements.

State/persistence: none.

Dependencies/integration: selected for cgo builds outside Linux/FreeBSD.

Risks: build plumbing only; changing tags can accidentally expose Linux/FreeBSD C code to unsupported platforms.

Test signals: cgo compile tests on unsupported platforms.
