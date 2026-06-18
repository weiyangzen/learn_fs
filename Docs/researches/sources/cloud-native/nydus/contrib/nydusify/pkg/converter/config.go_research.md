# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/config.go

Purpose: converts `converter.Opt` into string driver configuration for the Harbor acceleration-service converter.

Important APIs and flow: `getConfig` returns a map with workdir, builder path, backend type/config/force-push, chunk dictionary ref, Docker/OCI/manifest/referrer booleans, prefetch patterns, compressor, fs version/alignment/chunk size, batch size, and cache ref/version/max records. Boolean and unsigned values are formatted as strings.

State and persistence: none.

Dependencies and integration: consumed by `converter.New(converter.WithDriver("nydus", getConfig(opt)))` in `Convert`.

Risks and test signals: stringly typed config means misspelled keys or invalid values are only caught by the downstream driver. Adding fields to `Opt` requires updating this mapping.
