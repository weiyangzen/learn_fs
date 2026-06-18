# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-sse.h

Purpose: declares the SSE dynamic-code generator descriptor used by `ec-code.c` when `USE_EC_DYNAMIC_SSE` is compiled in.

Important API: `extern ec_code_gen_t ec_code_gen_sse;` exposes the backend descriptor. Consumers use it through the generic `ec_code_gen_t` vtable rather than calling SSE helpers directly.

Control flow and integration: `ec-code.c` places `&ec_code_gen_sse` in `ec_code_gen_table` behind AVX and before x64 depending on compile-time flags. `ec_code_detect()` validates CPU flags and returns this descriptor; `ec_code_build_dynamic()` then calls its callbacks to emit executable code.

State behavior: no mutable state is declared in the header. Runtime state lives in `ec_code_t`, `ec_code_builder_t`, and generated code chunks. Risks are mostly build-configuration risks: the header must only be included when the implementation is compiled, and the symbol must match the descriptor name. Test signals include builds with `USE_EC_DYNAMIC_SSE` toggled, CPU-detection tests for `"sse"`, and fallback checks when SSE generation fails.
