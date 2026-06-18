# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-x64.h

Purpose: declares the scalar x64 dynamic-code generator descriptor.

Important API: `extern ec_code_gen_t ec_code_gen_x64;` is consumed by `ec-code.c` when `USE_EC_DYNAMIC_X64` is enabled. The descriptor supplies generic callbacks for `ec_code_build_dynamic()`.

Control flow and integration: x64 is a fallback dynamic generator in `ec_code_gen_table`, generally after wider AVX/SSE backends. CPU detection can select it even without feature flags because its implementation requires only x86-64 baseline integer operations.

State behavior: this header declares no state. Generated functions are managed by `ec_code_t` and released through `ec_code_release()`. Risks are symbol/configuration mismatches and accidental inclusion on non-x64 builds if compile guards are wrong. Test signals include builds with only x64 dynamic support, explicit `cpu-extensions=x64`, and parity output comparison to the portable C backend.
