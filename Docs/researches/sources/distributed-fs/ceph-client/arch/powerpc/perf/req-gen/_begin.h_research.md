<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_begin.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_begin.h

Purpose: starts the request-description macro environment used by generated perf request headers under `req-gen`.

Important APIs/types/functions: defines the include guard `POWERPC_PERF_REQ_GEN_H_`, imports `<linux/stringify.h>`, provides `CAT2_STR_()`, `CAT2_STR()`, and `I(...)`, then defines `REQ_GEN_PREFIX`, `REQUEST_BEGIN`, and `REQUEST_END` for sibling include names.

Control flow: request-definition headers include this file before declaring requests. The macros build string include paths such as `req-gen/_request-begin.h` and `req-gen/_request-end.h` for later use by generator-style headers.

State and persistence: no runtime state; it creates preprocessor definitions that persist until `_end.h` or `_clear.h` undefines them.

Dependencies and integration: consumed by powerpc perf request-generation headers, especially `perf.h`, and assumes the preprocessor include path can resolve `req-gen/...` fragments.

Risks and test signals: macro leakage or include-path mistakes can break generated request structures and sysfs events. Test by building hv-gpci/request users with multiple inclusions and by verifying `_end.h` cleans all definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_begin.h -->
