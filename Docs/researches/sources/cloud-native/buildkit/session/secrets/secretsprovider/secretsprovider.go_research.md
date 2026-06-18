<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secretsprovider/secretsprovider.go -->
# sources/cloud-native/buildkit/session/secrets/secretsprovider/secretsprovider.go

Purpose: implements a session attachable server for serving secrets from a `SecretStore`.

Important APIs, types, and functions: `MaxSecretSize` is 500 KiB. `NewSecretProvider(store)` returns a session attachable. `secretProvider.Register` registers generated server. `GetSecret` loads bytes from the store, maps `secrets.ErrNotFound` to gRPC NotFound, rejects oversized secrets, and returns data. `FromMap` creates a provider from an in-memory byte map. `mapStore.GetSecret` reads from the map.

Control flow and state: provider state is the backing store. Map provider state is in-memory bytes. Every RPC fetches from the store at request time.

Dependencies and integration: uses session attachables, generated secrets server, gRPC status codes, and `secrets.SecretStore`.

Risks and test signals: oversized map secrets are rejected only at request time, while file store validates file size at setup and reads env secrets at request time. Tests should cover max-size enforcement, not-found status, and FromMap behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secretsprovider/secretsprovider.go -->
