# sources/cloud-native/containers-storage/types/idmappings.go

Purpose: defines ID mapping option structs and parses CLI-style UID/GID mapping inputs into storage `IDMappingOptions`.

Important APIs and control flow: `AutoUserNsOptions` describes automatic namespace sizing, passwd/group overrides, and additional mappings. `IDMappingOptions` controls host mapping, explicit maps, and auto-userns configuration. `ParseIDMapping` normalizes missing UID/GID and subuid/subgid inputs, defaults non-root users to a one-ID mapping when no subid data is provided, loads subid mappings via `idtools.NewIDMappings`, parses explicit `UIDMapSlice` and `GIDMapSlice`, appends both sources, and flips `HostUIDMapping`/`HostGIDMapping` to false when maps exist.

State and persistence: no persisted state; uses current process UID/GID to infer defaults for non-root execution.

Dependencies and integration: depends on `github.com/containers/storage/pkg/idtools` for parsing and `/etc/subuid`/`/etc/subgid` mapping resolution. Called by the top-level `storage.ParseIDMapping` wrapper in `utils.go`.

Risks: error messages for GID parsing include the UID slice in one format path, which could confuse diagnostics. Implicit mirroring of UID to GID and vice versa is convenient but can surprise callers who intended asymmetry.

Test signals: behavior is usually validated by user namespace and ID mapping tests in storage packages; key cases include rootless fallback, subid lookup failure, parse errors, and host-mapping flags.
