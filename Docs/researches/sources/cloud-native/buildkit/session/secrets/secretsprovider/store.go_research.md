<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secretsprovider/store.go -->
# sources/cloud-native/buildkit/session/secrets/secretsprovider/store.go

Purpose: builds a file/env-backed `SecretStore` from user-provided secret sources.

Important APIs, types, and functions: `Source` includes `ID`, `FilePath`, and `Env`. `NewStore(files)` validates ids, defaults an unspecified source to environment variable when present or file path otherwise, stats file-backed secrets, rejects files larger than `MaxSecretSize`, and stores sources by id. `fileStore.GetSecret` returns env value bytes or reads the configured file.

Control flow and state: store state is an in-memory id-to-source map. File content and environment values are read at request time, except file size is checked during construction.

Dependencies and integration: used by BuildKit secret CLI/session setup and `secretsprovider.NewSecretProvider`.

Risks and test signals: file size can change after `NewStore`, so provider-level max-size enforcement is still important. Env values are not size-checked until provider response path. Duplicate ids overwrite earlier sources. Tests should cover defaulting, missing ids, missing files, env reads, file reads, duplicate behavior, and size enforcement.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secretsprovider/store.go -->
