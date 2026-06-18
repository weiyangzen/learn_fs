# sources/distributed-fs/coda/coda-src/auth2/avice.c

Purpose: Server-side token validation helper used by Vice file servers to derive RPC2 handshake/session keys from Coda tokens.

Important APIs/functions: `GetKeysFromToken` and `SetServerKeys`. Static state tracks two derived auth2 keys and validity flags.

Control flow: `SetServerKeys` derives auth2 keys from one or two configured server keys. `GetKeysFromToken` allows unauthenticated open-kimono calls when `cIdent` is NULL, validates token length, tries key1 then key2 with `validate_CodaToken`, checks expiry, copies the token handshake key to `hKey`, generates a fresh server secret `sKey`, and overwrites `cIdent->SeqBody` with a host-order `SecretToken` for new-connection handling.

State and persistence: Holds derived keys in static memory only. Persistent key source is supplied by callers from server configuration.

Dependencies and integration: Depends on RPC2, `getsecret`, auth token definitions, and `codatoken`. Intended as the RPC2 authentication callback for file-server request loops.

Risks and test signals: Expires based on `endtimestamp` from token validation, but a log line references fields in `st` before all are set. Static key state is process-global. Sensitive derived keys are not wiped on replacement. Accepting NULL `cIdent` intentionally allows unauthenticated bindings, so callers must enforce operation-level policy.
