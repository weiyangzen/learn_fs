# sources/distributed-fs/ceph-client/include/keys/asymmetric-parser.h

Source read summary: 36 lines, 1012 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/asymmetric-parser.h` declares the registration interface for asymmetric key parsers that convert raw blobs into key payloads during key instantiation.

Important APIs, types, and functions: Important exported functions or hooks: `register_asymmetric_key_parser`, `unregister_asymmetric_key_parser`. Important types: `key_preparsed_payload`, `asymmetric_key_parser`. Important constants/macros: none.

Control flow: Parser modules fill `struct asymmetric_key_parser` with an owner, name, parser callback, and linked-list node, then call register/unregister helpers so the asymmetric key type can try parsers during preparse.

State and persistence behavior: Registered parsers persist in a global kernel list while their module is loaded; individual preparsed payloads remain request-local until key instantiation succeeds or fails.

Dependencies and integration points: It is self-contained at include level. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Parser ordering, module lifetime, and preparse cleanup are the main hazards. A parser must leave no dangling payload state on failure and must not unregister while in active use.

Test signals: Load/unload parser modules, instantiate X.509/PKCS#7-like blobs through the keyring API, and cover malformed blob cleanup and duplicate parser names.
