# sources/distributed-fs/ceph-client/tools/bpf/resolve_btfids/Makefile

Purpose: Builds the host-side `resolve_btfids` tool and its private libbpf/libsubcmd dependencies in the kernel tools build environment.

Important APIs, types, and functions: Defines `srctree`, `OUTPUT`, host tool variables, `HOST_OVERRIDES`, `BPFOBJ`, `SUBCMDOBJ`, `BINARY`, and `BINARY_IN`. Targets include `all`, `prepare`, libsubcmd/libbpf builds, object build through `tools/build/Makefile.include`, final link, `clean`, and `tags`.

Control flow: `all` builds `$(BINARY)`. `prepare` builds dependency archives and installs headers into output-local include directories. `$(BINARY_IN)` invokes the tools build system for `resolve_btfids`. Final link uses `HOSTCC`, `KBUILD_HOSTLDFLAGS`, optional `EXTRA_LDFLAGS`, libbpf, libsubcmd, libelf, and zlib.

State and persistence: Writes generated objects, static archives, installed headers, and binary under `OUTPUT`, defaulting to `tools/bpf/resolve_btfids/`. `clean` removes these outputs.

Dependencies and integration points: Integrates with `tools/scripts/Makefile.include`, `Makefile.arch`, `tools/build`, `tools/lib/bpf`, and `tools/lib/subcmd`. Uses `pkg-config` for libelf/zlib flags with fallbacks.

Risks: Static libelf fallback includes `-lzstd`, which assumes availability. Host/cross overrides intentionally clear target cross flags; incorrect environment can still mix host and target flags. `clean_objects` is computed at parse time, so stale outputs created after parse are handled by wildcard expansion only on invocation.

Test signals: `make -C tools/bpf/resolve_btfids`, static and dynamic libelf builds, `OUTPUT=` out-of-tree builds, `V=1`, and `make clean`.
