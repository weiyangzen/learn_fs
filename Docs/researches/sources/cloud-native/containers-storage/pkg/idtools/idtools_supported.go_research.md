## sources/cloud-native/containers-storage/pkg/idtools/idtools_supported.go

Purpose: optional Linux+cgo+libsubid backend for subordinate ID lookup.

Important APIs/types/functions: `readSubid`, `readSubuid`, `readSubgid`, and `onceInit`.

Control flow: rejects username `ALL`, optionally resolves username to numeric UID string, initializes libsubid once, calls UID or GID range lookup by name then numeric UID fallback, converts C ranges to Go `ranges`, and frees C allocations.

State and persistence: initializes libsubid process state and reads system subordinate ID databases through the library.

Dependencies and integration points: selected by build tags `linux && cgo && libsubid`; replaces file parser backend in `idtools_unsupported.go`.

Risks: C string from `C.CString("storage")` passed to `subid_init` is not freed in the visible code; ABI compatibility handled with preprocessor aliases but still depends on libsubid availability. `ALL` is unsupported here, which affects helpers that scan all ranges.

Test signals: no selected tests target libsubid backend specifically.
