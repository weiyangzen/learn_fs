# sources/distributed-fs/ceph-client/net/rxrpc/server_key.c

Purpose: provides RxRPC server-side key type handling and server socket security-keyring configuration. It validates descriptions for `rxrpc_s` keys, delegates security-class-specific key parsing/destruction, and lets user or kernel services attach a keyring to a server socket.

Important APIs/functions: defines `key_type_rxrpc_s` with `vet_description`, `preparse`, `free_preparse`, `instantiate`, `destroy`, and `describe` hooks. `rxrpc_server_keyring()` consumes a userspace keyring name from a sockopt, `rxrpc_sock_set_security_keyring()` attaches a kernel-provided keyring before bind/connect, and `rxrpc_sock_set_manage_response()` toggles challenge-response management. Helpers `rxrpc_vet_description_s()`, `rxrpc_preparse_s()`, `rxrpc_free_preparse_s()`, `rxrpc_destroy_s()`, and `rxrpc_describe_s()` bridge to `struct rxrpc_security` callbacks.

Control flow: key descriptions must parse as `<service>:<security-class>[:...]` with service <= 65535 and security class 1..255. During preparse, the security class is looked up and stored in payload slot 1, then `preparse_server_key` handles class-specific payload material. Socket keyring setup rejects replacement, copies a NUL-terminated userspace string, requests a kernel keyring by description, and stores it in `rx->securities`.

State and persistence: the key subsystem persists instantiated keys and payloads. Socket state stores a referenced keyring in `rx->securities`; manage-response is a bit in `rx->flags`. Class-specific key payload lifetime is owned by key hooks and released through security callbacks.

Dependencies and integration: integrates Linux keyrings, RxRPC security class registry, sock locking, and exported AF_RXRPC kernel service APIs. Security modules such as RxKAD/RxGK provide the concrete server-key parser and cleanup methods.

Risks: key descriptions are parsed partly with `simple_strtoul()` and partly with `sscanf()`, so malformed descriptions must remain covered by both validation stages. Keyring attachment is intentionally one-shot and state-dependent; callers attempting setup after binding receive `-EISCONN`. Manage-response only has an effect for security classes that consult userspace.

Test signals: key-add/request tests with valid and invalid descriptions, missing security classes returning `-ENOPKG`, sockopt keyring setup with bad lengths/names, kernel keyring setup before and after bind, and challenge-response behavior for classes supporting managed responses.
