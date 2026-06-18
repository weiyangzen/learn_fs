# sources/distributed-fs/ceph-client/tools/include/tools/endian.h

## Purpose
Defines little-endian host conversion macros for tools when system headers do not already provide `htole*` and `le*toh`.

## Important APIs, Types, and Functions
Exports fallback `htole16/32/64` and `le16toh/le32toh/le64toh`. On little-endian hosts these are identity macros; on other hosts they map to `__bswap_16/32/64`.

## Control Flow, State, and Persistence
All behavior is compile-time conditional on `__BYTE_ORDER == __LITTLE_ENDIAN`. There is no runtime state.

## Dependencies and Integration
Depends on `<byteswap.h>` and libc byte-order macros. It integrates with tools reading Linux binary formats that are explicitly little-endian.

## Risks and Test Signals
Risks include relying on libc-specific `__BYTE_ORDER` names, macro double evaluation if arguments have side effects, and missing big-endian build coverage. Test signals are compile checks on little- and big-endian targets and known-value conversion tests.
