# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/libfdt.h

Purpose: primary public libfdt API header, documenting supported versions, error codes, traversal/read/write/overlay APIs, inline endian helpers, and convenience macros.

Important APIs/types/macros: version constants, `FDT_ERR_*` values, `FDT_MAX_PHANDLE`, unaligned load/store helpers `fdt16_ld`, `fdt32_ld/st`, `fdt64_ld/st`, iteration macros `fdt_for_each_subnode` and `fdt_for_each_property_offset`, header field getters/setters, read-only functions, sequential-write constructors, read-write mutators, typed property helpers, overlay APIs, and `fdt_strerror`.

Control flow/state: no standalone runtime state, but the API contract documents important state effects: sequential-write state transitions, read-write offset invalidation after inserts/deletes, and overlay non-atomic mutation.

Dependencies/integration: includes `libfdt_env.h` and `fdt.h`, exposes C ABI with `extern "C"`, and hides selected APIs from SWIG bindings. It is the single include used by DTC utilities and external consumers.

Risks: inline helpers are ABI/API surface; changing signatures or macro semantics affects all consumers. Documentation repeatedly warns that mutators can invalidate offsets and that overlay apply can damage inputs on failure.

Test signals: public-header compile coverage in C/C++, SWIG exclusions, typed helper endian output, macro iteration correctness, error-code/string synchronization, and behavior promised in comments for each API.
