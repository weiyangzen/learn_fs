# sources/distributed-fs/ceph-client/scripts/tracepoint-update.c

Purpose: `tracepoint-update.c` checks ELF objects for tracepoints that are defined but not referenced through the tracepoint verification section, warning about unused tracepoints.

Important APIs, types, and functions: it uses `elf-parse.h` and globals for `__tracepoint_check` and `__tracepoints_strings` sections. `add_string()` grows an array of string pointers. `for_each_shdr_str` iterates NUL-terminated strings in a section. `make_trace_array()` builds and sorts the checked tracepoint names. `find_event()` uses `bsearch()`. `check_tracepoints()` warns for strings not present in the checked array. `process_tracepoints()` locates sections and handles module-specific absence rules.

Control flow: `main()` accepts optional `--module`, maps each input with `elf_map(..., 1 << ET_REL)`, and processes it. For modules, absence of both sections is allowed, absence of check section with tracepoints warns but does not fail, and absence of tracepoint strings can mean only exported references. For non-modules, missing sections are fatal. Found tracepoint strings are compared against the sorted check list.

State and persistence: no file mutation despite the name. It allocates and frees a transient string-pointer array and writes warnings to stderr.

Dependencies and integration points: tied to kernel tracepoint section names and object build steps. The non-module usage text says `vmlinux`, but the mapping mask accepts `ET_REL`, so callers need to supply the expected relocatable object form.

Risks: global section pointers are not reset inside `process_tracepoints()`, which matters if processing multiple files with different section presence. String section iteration assumes well-formed NUL-terminated data. Misaligned usage expectations around ET_REL versus linked vmlinux can confuse integration.

Test signals: objects with no tracepoints, all-used tracepoints, unused tracepoints, module-only exported references, and multiple input files with different section combinations.
