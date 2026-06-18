# sources/cloud-native/buildkit/cache/config/config.go

Purpose: small cache configuration package defining options attached to cache refs.

Important APIs/types/functions: `RefConfig` with `Compression compression.Config` and `PreferNonDistributable bool`.

Control flow: data-only struct; no functions.

State and persistence behavior: no persistence itself. Instances are passed through cache/export paths to influence compression and distributability preferences.

Dependencies and integration points: imports BuildKit `util/compression`. Used by cache callers that need to carry layer compression policy alongside distribution preference.

Risks: because this is a shared config shape, adding fields can have broad propagation impact. Zero values mean default compression config and distributable preference.

Test signals: indirect compile and behavioral coverage in cache/export tests.
