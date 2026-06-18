# sources/cloud-native/containers-storage/pkg/unshare/unshare_gccgo.go

Purpose: gccgo-specific cgo hook ensuring the C constructor for Linux unshare is linked.

Important APIs/types/functions: imports C constructor and defines exported `AlwaysFalse` used in `init`.

Control flow: the ordinary C constructor calls `_containers_unshare`; additionally, `init` contains an unreachable reference to `C.init()` behind `AlwaysFalse` so gccgo links the symbol despite optimizer behavior.

State/persistence: same early constructor side effects as `unshare_cgo.go` when environment requests unshare.

Dependencies/integration: selected for `linux && cgo && gccgo`; works around a gccgo linker issue noted in comments.

Risks: subtle build-toolchain compatibility file; removing the dead-looking reference can break gccgo builds.

Test signals: gccgo build/namespace smoke tests are the key signal.
