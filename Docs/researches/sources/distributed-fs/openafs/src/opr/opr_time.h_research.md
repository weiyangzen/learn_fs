# sources/distributed-fs/openafs/src/opr/opr_time.h

Purpose: inline utility API for `struct afs_time64`, a signed 64-bit timestamp/duration in 100ns ticks.

Important APIs/types/functions: defines tick conversion constants and representable bounds. Provides compare helpers (`opr_time64_cmp`, relational/equality wrappers), checked addition, conversions from ticks, seconds, microseconds, and timeval-like sec/usec pairs, conversions back to ticks/seconds, uint32 wrapping conversion, and userland `opr_time64_now_safe`/`opr_time64_now`.

Control flow: checked constructors validate range before multiplying to ticks. `opr_time64_add_safe` checks overflow based on operand signs. `opr_time64_now_safe` reads `gettimeofday` and converts to ticks; on impossible `gettimeofday` failure it aborts.

State and persistence: pure value operations; no persistent state.

Dependencies/integration: requires `struct afs_time64` typedef from OpenAFS headers, `afs/opr.h`, and either kernel includes or userland time/errno headers. Installed as `opr/time.h`.

Risks and test signals: unchecked constructors assert on invalid input and should not be used with untrusted data. Microsecond value is not normalized in `fromTimeval_safe`; very large usec can overflow independently. Unit tests should cover bounds, overflow, negative values, and wrapping.
