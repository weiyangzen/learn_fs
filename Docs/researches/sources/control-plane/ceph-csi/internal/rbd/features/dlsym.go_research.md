# sources/control-plane/ceph-csi/internal/rbd/features/dlsym.go

## Purpose
Provides a small cgo helper for dynamic symbol detection in already loaded native libraries. It lets Ceph-CSI decide whether optional librbd functions are available at runtime.

## Important APIs, Types, And Functions
`dlsym(symbol string) error` converts the symbol to a C string, clears `dlerror`, calls `dlsym(nil, symbol)`, reads `dlerror`, and returns nil only when lookup succeeds.

## Control Flow
The helper checks the global process symbol table rather than opening a specific library handle. It frees the allocated C string with `C.free` and wraps any dynamic-loader message in a Go error.

## State And Persistence
No persistent state is stored. It observes process-loaded shared libraries and their exported symbols.

## Dependencies And Integration Points
Depends on cgo, `libdl`, and unsafe pointer conversion. `features.go` calls this after forcing librbd to load so it can gate group snapshot and snapshot-diff capabilities.

## Risks And Test Signals
Risks include platform/linker differences, cgo availability, and interpreting non-undefined-symbol `dlerror` values. It is indirectly exercised by `features_test.go`, which calls feature detection against the test runtime’s librbd.
