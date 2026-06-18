<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_request-end.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_request-end.h

Purpose: cleans up the per-request macro aliases and identity fields established for one request description.

Important APIs/types/functions: undefines `REQUEST`, `__field`, `__array`, `__count`, `REQUEST_NAME`, `REQUEST_NUM`, and `REQUEST_IDX_KIND`.

Control flow: included at the end of each request block so the next request can define a new name, number, and index kind without macro contamination.

State and persistence: preprocessor cleanup only.

Dependencies and integration: used with `_request-begin.h` by request description files included from `perf.h`.

Risks and test signals: missing cleanup can cause subsequent request blocks to reuse stale names or numeric IDs. Test through multi-request generated headers and preprocessed output after editing request definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_request-end.h -->
