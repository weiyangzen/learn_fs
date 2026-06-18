## sources/cloud-native/containers-storage/pkg/idtools/idtools_unsupported.go

Purpose: default subordinate ID backend when libsubid-specific backend is not selected.

Important APIs/types/functions: `readSubuid` and `readSubgid`.

Control flow: delegates to `parseSubidFile` for `/etc/subuid` and `/etc/subgid`.

State and persistence: reads system files only.

Dependencies and integration points: active for most non-`linux+cgo+libsubid` builds, including Linux without libsubid. Used by `NewIDMappings` and user range helpers.

Risks: depends on direct file readability and parser behavior; no NSS/libsubid integration in this path.

Test signals: `idtools_unix_test.go` covers `parseSubidFile` with a synthetic file, not the hard-coded system file paths.
