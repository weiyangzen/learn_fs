# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cap_helpers.c

Purpose: toggles effective Linux capabilities in selftests without requiring libcap development headers.

Important APIs and functions: declares libc `capget`/`capset` manually; `cap_enable_effective(caps, old_caps)` ORs requested bits into effective sets; `cap_disable_effective(caps, old_caps)` clears requested bits. Both can return previous effective mask.

Control flow: read current capability sets, optionally save old mask, fast-return if requested state already holds, modify two 32-bit effective words, and call `capset`.

State and persistence: modifies process effective capability state. `old_caps` lets callers restore externally but no automatic guard is provided.

Dependencies and integration points: uses Linux capability UAPI structs from `cap_helpers.h` and errno negation for error returns.

Risks: only effective set changes, not permitted/inheritable; callers must restore caps carefully; capability operations may fail under user namespaces or insufficient privileges.

Test signals: tests can assert zero return and use saved masks to verify/restore effective capability bits.
