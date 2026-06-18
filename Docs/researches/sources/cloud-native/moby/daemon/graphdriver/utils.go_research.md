# sources/cloud-native/moby/daemon/graphdriver/utils.go

Purpose: shared parser for graphdriver storage option strings.

Important APIs and control flow: `ParseStorageOptKeyValue` splits an option on the first `=`, returns an error when no separator exists, and trims surrounding whitespace from key and value while preserving additional `=` characters in the value.

State, dependencies, and risks: no state and only standard library dependencies. It is used by multiple drivers to parse daemon/global and per-layer storage options. It does not reject empty keys or values after trimming, so caller-specific validation must handle those. Tests cover missing separators, whitespace trimming, and values containing additional equals signs.
