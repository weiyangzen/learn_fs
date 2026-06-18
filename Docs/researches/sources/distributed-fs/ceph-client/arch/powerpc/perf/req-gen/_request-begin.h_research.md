<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_request-begin.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_request-begin.h

Purpose: exposes user-facing request-description macros that stamp each field with the active request name, numeric ID, and starting-index kind.

Important APIs/types/functions: defines `REQUEST(r_contents)`, `__field()`, `__array()`, and `__count()`. These wrap lower-level `REQUEST_`, `__field_`, `__array_`, and `__count_` macros with `REQUEST_NAME`, `REQUEST_NUM`, and `REQUEST_IDX_KIND`.

Control flow: a request description sets request identity macros, includes this header, emits `REQUEST(...)` containing field declarations, then includes `_request-end.h`. Higher-level generators redefine the underscored macros before including the request file.

State and persistence: preprocessor-only state; definitions persist until `_request-end.h` or `_clear.h`.

Dependencies and integration: requires `REQUEST_NAME`, `REQUEST_NUM`, and `REQUEST_IDX_KIND` to be defined by the request file context, and requires a higher-level consumer to define the underscored expansion macros.

Risks and test signals: request identity macros are positional and easy to mismatch, producing wrong sysfs metadata or struct names. Test by adding a request and confirming enum values, struct names, offset assertions, and event attributes all reflect the same request metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_request-begin.h -->
