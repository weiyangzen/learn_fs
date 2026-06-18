# sources/distributed-fs/openafs/src/auth/cellconfig.p.h

## Purpose
`cellconfig.p.h` is the template for generated `cellconfig.h`. It declares OpenAFS cell configuration structures, security-option flags, key APIs, auth connection APIs, superuser checks, realm checks, net restriction parsers, and well-known service constants.

## Important APIs, types, and functions
Key data types include `struct afsconf_cell`, `struct afsconf_cellalias`, `struct afsconf_entry`, `struct afsconf_aliasentry`, `afsconf_secflags`, `struct afsconf_dir`, `struct afsconf_typedKeyList`, and `afsconf_keyType` (`afsconf_rxkad`, `afsconf_rxgk`, `afsconf_rxkad_krb5`). Function declarations cover service/cell lookup, open/close/reload, key get/add/delete/enumeration, typed-key reference management, client/server RX security object selection, user/superuser management, realm matching, and netrestrict parsing.

## Control flow
No executable control flow exists, but the declarations define the control surface implemented across `cellconfig.c`, `keys.c`, `authcon.c`, `userok.c`, `realms.c`, and `netrestrict.c`.

## State and persistence
`struct afsconf_dir` is the central in-memory persistent configuration handle. Its fields mirror source files and runtime settings: config path, cell name, CellServDB path, cells, key list, timestamps, aliases, security flags, local realms, and exclusions. Key APIs persist to server key files through implementation modules.

## Dependencies and integration points
The header includes socket types, rx opaque buffers, opr queues, and rxgk key types. It is used broadly by OpenAFS clients, servers, tools, and authentication code. Generated error definitions from `acfg_errors.et` are combined with this template.

## Risks
The structures expose internal linked-list fields and fixed-size arrays, so ABI compatibility and direct field access constrain future changes. Security flag combinations can be invalid or meaningful only for certain mechanisms, requiring implementation-side validation. Generated-header workflow means this template, not generated `cellconfig.h`, is the maintainable source.

## Test signals
ABI checks for public structs, generated header regeneration, typed-key lifecycle tests, security flag matrix tests through `authcon.c`, userok and realm integration tests, and service constant consistency with `cellconfig.c` service table.
