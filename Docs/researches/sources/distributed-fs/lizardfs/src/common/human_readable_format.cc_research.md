# sources/distributed-fs/lizardfs/src/common/human_readable_format.cc

Purpose: implements formatting helpers for byte counts, IP addresses, timestamps, and transfer rates.

Important APIs/types/functions: internal `convertToHumanReadableFormat`, public `convertToSi`, `convertToIec`, `ipToString`, `timeToString`, and `bpsToString`.

Control flow: byte formatting chooses exponent by logarithms, adjusts near-boundary values, emits one decimal for values below 10 and zero decimals otherwise, and uses SI or IEC suffixes. IP formatting shifts a host-order `uint32_t` into dotted decimal. Time formatting uses `strftime(localtime(...))`. `bpsToString` asserts positive microseconds and formats `(bytes * 1e6 / usec)` as IEC bytes per second.

State and persistence: no state; formatting only.

Dependencies and integration: depends on `<cmath>`, `<iomanip>`, `<sstream>`, `massert`, and the header declarations. Used in CLI/admin/status output.

Risks: `localtime` uses static storage and is not thread-safe on many platforms. Floating conversion from `uint64_t` can lose precision at high values but output is intentionally approximate. `bpsToString` mixes floating result into a `uint64_t`-typed formatter through implicit conversion.

Test signals: `human_readable_format_unittest.cc` covers SI and IEC boundary outputs extensively.
