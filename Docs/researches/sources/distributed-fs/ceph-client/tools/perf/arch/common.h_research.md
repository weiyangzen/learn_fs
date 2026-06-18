# sources/distributed-fs/ceph-client/tools/perf/arch/common.h

Purpose: Common perf architecture helpers for locating cross-architecture binutils and identifying address-space behavior.

Important APIs/types/functions: `perf_env__lookup_objdump`, `perf_env__single_address_space`, `ARCH_PERF_COMMON_H`, `perf_env`.

Control flow: Maps perf environment architecture names to objdump triplet candidates, honors cross-compile environment variables, searches PATH, and reports whether an env has a single address space.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf env metadata, libc PATH handling, and installed binutils naming conventions.

Risks: Triplet lists can become stale and path lookup allocates/parses environment strings.

Test signals: Lookup objdump for native and cross perf.data environments; test missing PATH and unsupported arch names.

Source coverage: researched from the complete local file (13 lines, 291 bytes).
