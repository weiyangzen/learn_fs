# sources/distributed-fs/coda/coda-src/auth2/avice.h

Purpose: Header for Vice-side auth2 token validation helpers.

Important APIs/types: Declares `GetKeysFromToken` RPC2 auth callback and `SetServerKeys` key-configuration routine.

Control flow and state model: File servers configure current/previous server keys, then pass `GetKeysFromToken` to RPC2 request processing to authenticate token-bearing clients.

Persistence and integration: No direct persistence. Integrates Vice file-server authentication with `codatoken` and RPC2.

Risks and test signals: The interface accepts raw `RPC2_EncryptionKey` pointers; ownership and lifetime are external. Callers must decide whether open-kimono bindings are acceptable.
