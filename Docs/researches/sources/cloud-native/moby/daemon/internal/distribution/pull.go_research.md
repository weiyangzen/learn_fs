# sources/cloud-native/moby/daemon/internal/distribution/pull.go

## Purpose
Provides top-level pull and tag listing orchestration across registry endpoints.

## APIs, Control Flow, and Integration
`Pull` resolves endpoints through `pullEndpoints`, constructs a v2 puller for each candidate, and logs a pull event on success. `Tags` reuses endpoint fallback to list remote tags. `validateRepoName` rejects `scratch`. `addDigestReference` adds immutable digest references without updating changed digest IDs. `pullEndpoints` trims refs, looks up pull endpoints, skips plaintext endpoints after confirmed TLS, invokes the callback, unwraps fallback errors, records last error, and translates final failures.

## State, Dependencies, and Risks
State updates reference store digest refs and emits events. Risks include endpoint fallback subtlety, `scratch` reservation, unchanged digest refs not updated if image ID differs, and TLS/plaintext skip behavior. Pull-specific error translation lives in `errors.go`.
