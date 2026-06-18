<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/util.c -->
## sources/distributed-fs/ceph-client/fs/proc/util.c

Purpose: provides a small procfs utility for parsing decimal path components into unsigned integers, primarily for numeric proc entries such as PIDs or file descriptors.

Important APIs and functions: exports `name_to_int(const struct qstr *qstr)`.

Control flow: `name_to_int` rejects names with leading zeroes longer than one character, rejects non-digits, checks for unsigned overflow using `(~0U - 9) / 10`, accumulates the number, and returns `~0U` as an invalid sentinel.

State and persistence behavior: stateless pure parser; it reads only the supplied qstr.

Dependencies and integration points: depends on dcache qstr definitions and proc internal callers in numeric lookup paths. The invalid sentinel must be understood by callers as "not a valid decimal name."

Risks: the sentinel collides with the maximum unsigned value, so callers must not allow that as a valid object number. Leading-zero rejection is ABI-relevant for proc numeric names. Overflow checks must run before multiply/add.

Test signals: parse `0`, normal PIDs, leading-zero strings, non-digit strings, empty-like qstrs from lookup callers, `UINT_MAX`, and overflow values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/util.c -->
