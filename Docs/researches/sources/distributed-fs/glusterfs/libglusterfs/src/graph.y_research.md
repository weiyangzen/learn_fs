# sources/distributed-fs/glusterfs/libglusterfs/src/graph.y

Purpose: `graph.y` is the yacc/bison parser and constructor for GlusterFS volume files. It turns volume/type/option/subvolume syntax into a linked `glusterfs_graph_t`.

Important APIs and types: grammar rules parse one or more `VOLUME` blocks, each with a header, type line, optional option lines, optional subvolume line, and footer. Helper functions create volumes, set type, set options, link subvolumes, close volumes, report syntax-specific errors, preprocess backtick commands, create graphs, and construct graphs from `FILE *`.

Control flow and state: `glusterfs_graph_construct` creates a graph and temporary file, preprocesses backtick command substitutions, locks a static parser mutex, sets global `graphyyin` and `construct`, and calls `yyparse`. `new_volume` allocates `xlator_t`, rejects duplicate names, initializes options and volume option list, and prepends it to the graph. `volume_type` calls `xlator_set_type`; `volume_option` stores duplicated values in the current xlator dict; `volume_sub` resolves previously defined subvolumes and links parent/child; `volume_end` requires type/fops.

State and persistence: parser state is global/static (`curr`, `construct`, lexer globals) but serialized by `graph_mutex`. Backtick preprocessing executes shell commands via `popen` and writes expanded content to an unlinked temporary file.

Dependencies and integration: depends on `xlator.h`, graph utilities, logging, syscall wrappers, memory allocation, and parser tokens from `graph.l`. Constructed graphs are later prepared/activated by `graph.c`.

Risks: backtick execution is powerful and dangerous for untrusted volfiles. `volume_type` and `volume_option` return `0` even after setting `ret = -1` on some errors, which can mask failures. Static parser globals limit concurrency. Temporary-file and preprocessing allocation failures need cleanup scrutiny.

Test signals: parse valid multi-volume graphs, duplicate volumes/options, undefined/self subvolumes, missing type/subvolume/option values, backtick success/failure/unterminated cases, command-output buffer growth, parser concurrency serialization, and cleanup after parse errors.
