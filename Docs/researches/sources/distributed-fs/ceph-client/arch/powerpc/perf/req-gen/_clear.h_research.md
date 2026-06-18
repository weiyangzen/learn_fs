<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_clear.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_clear.h

Purpose: resets the request-generation macro layer so the same request file can be included repeatedly with different macro meanings.

Important APIs/types/functions: undefines `__field_`, `__count_`, `__array_`, and `REQUEST_`.

Control flow: generator headers include `_clear.h` before redefining the low-level macros for enum generation, struct generation, offset checks, or perf attribute generation.

State and persistence: only preprocessor state changes. There is no runtime state.

Dependencies and integration: paired with `perf.h`, `_request-begin.h`, and request description files that expand to `REQUEST_` and field macros.

Risks and test signals: missing an undef causes one generation pass to bleed into the next; undefining too much would break the wrapper macros. Test through a full kernel build of request-generated perf PMUs and by checking preprocessed output when adding new request fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_clear.h -->
