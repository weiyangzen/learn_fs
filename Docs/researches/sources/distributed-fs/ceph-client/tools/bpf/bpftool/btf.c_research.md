<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/btf.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/btf.c

Purpose: this implements the `bpftool btf` command family: listing BTF objects and dumping BTF data in raw or C header form from kernel BTF IDs, programs, maps, or files.

Important APIs/types/functions: `dump_btf_type()` formats individual BTF kinds, including int, ptr, array, struct/union, enum/enum64, fwd, func/proto, var, datasec, float, decl tags, type tags, and modifiers. `dump_btf_raw()` emits raw type records. `dump_btf_c()` uses libbpf `btf_dump` to generate `vmlinux.h`-style C, with optional stable sorting from `sort_btf_c()`. `dump_btf_kfuncs()` emits weak kfunc prototypes based on decl tags. `do_dump()` parses BTF sources and dump options. `do_show()` lists BTF objects and references from programs/maps/PIDs using hashmaps built by `build_btf_tables()`.

Control flow: `do_btf()` dispatches `show/list`, `dump`, and `help`. Dump flow first resolves the source: map/prog file descriptor, BTF ID, or one or more files. Map dumps can restrict roots to key, value, kv, or all; `root_id` can filter arbitrary root types unless other filtering was already selected. File dumps can merge multiple split BTF files with a required base BTF, automatically loading `/sys/kernel/btf/vmlinux` when sysfs module paths are used. It then loads BTF if needed, validates root IDs before emitting C boilerplate, and chooses raw or C format.

State and persistence: command state is transient. It opens kernel object FDs, loads/parses BTF objects, builds in-memory hashmaps for references, and writes output to stdout/json writer. It does not mutate kernel BTF state. The global `base_btf` from bpftool options may be used or populated for module fallback.

Dependencies and integration points: it depends on libbpf BTF APIs, kernel `bpf_btf_*`, map/prog FD parsers from `common.c`, bpftool JSON helpers, object reference tracking from other bpftool modules, and `/sys/kernel/btf/vmlinux` for common base BTF fallback. Generated C output is consumed by BPF CO-RE builds.

Risks: BTF source parsing has many combinations and error paths; invalid root IDs are checked before C output to avoid half-emitted headers. Sorting C output uses hashes and names for stability but still depends on libbpf type traversal behavior. Multiple file merge requires correct base BTF or can fail/dedup incorrectly. Kernel module BTF loaded by ID without a base triggers fallback warning and sysfs base loading. `build_btf_type_table()` frees only the failing hashmap on some errors, so callers must handle paired cleanup carefully.

Test signals: tests should cover raw and C dumps from map/prog/id/file, root filters, invalid and duplicate root IDs, map key/value/kv/all modes, JSON raw dump, JSON rejection for C dump, module BTF with and without base, multi-file merge, kfunc prototype emission, enum64/decl-tag/type-tag formatting, and list output with program/map/PID references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/btf.c -->
