# sources/distributed-fs/ceph-client/security/integrity/platform_certs/load_ipl_s390.c

Purpose: Loads certificates from the s390 IPL report into the platform trusted keyring during late init.

Important APIs/types/functions: `load_ipl_certs()` walks `ipl_cert_list_addr`/`ipl_cert_list_size` from architecture boot data and calls `add_to_platform_keyring("IPL:db", ptr, len)` for each length-prefixed certificate.

Control flow: If no IPL certificate list address is present, it exits successfully. Otherwise it converts the physical address with `__va()`, iterates until the end pointer, reads an unsigned length, advances to certificate data, imports it, and advances by length.

State and persistence: No local persistent state. Imported certs persist in the platform keyring.

Dependencies and integration: s390 boot data, integrity platform keyring, and late initcall ordering after keyring initialization.

Risks and test signals: Risks include trusting malformed firmware length fields and lack of explicit bounds checks for each entry. Platform tests should cover empty list, single/multiple certs, and corrupted length data if fixture support exists.
