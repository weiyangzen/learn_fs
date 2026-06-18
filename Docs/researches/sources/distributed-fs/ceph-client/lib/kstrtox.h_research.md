# sources/distributed-fs/ceph-client/lib/kstrtox.h

Purpose: private header for `kstrtox.c` integer parsing internals.

Important declarations: `KSTRTOX_OVERFLOW` high-bit flag, `_parse_integer_fixup_radix()`, `_parse_integer_limit()`, and `_parse_integer()`.

Control flow: not executable itself; it exposes the internal parser contract used by the implementation and possible local tests.

State and persistence: no state.

Dependencies and integration: included by `lib/kstrtox.c`; relies on standard kernel integer and size types from including context.

Risks: because it is an internal header, widening its use can couple external code to low-level return encodings such as consumed-character count ORed with overflow.

Test signals: compile coverage of `kstrtox.c`; direct tests of parser internals if KUnit or lib tests expose them.
