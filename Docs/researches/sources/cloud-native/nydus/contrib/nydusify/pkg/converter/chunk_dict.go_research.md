# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/chunk_dict.go

Purpose: parses chunk dictionary command arguments used by converter options.

Important APIs and flow: valid formats currently contain only `bootstrap`; valid sources are `registry` and `local`. `ParseChunkDictArgs` splits the string on colon, requires at least three parts, validates format and source, and rejoins all remaining parts as the ref so registry tags and local paths containing colons are preserved. `ChunkDictOpt` stores raw args and an insecure flag.

State and persistence: none.

Dependencies and integration: feeds converter/chunk dictionary setup by separating format, source type, and reference/path.

Risks and test signals: simple split syntax cannot escape colons in the first two fields, but preserves them in refs. Error messages include accepted values.
