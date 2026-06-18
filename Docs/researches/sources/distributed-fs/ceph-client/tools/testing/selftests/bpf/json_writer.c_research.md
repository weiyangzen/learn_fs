# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/json_writer.c

Purpose: simple streaming JSON writer that manages commas, nesting, optional pretty printing, and primitive value formatting.

Important APIs and functions: `jsonw_new`, `jsonw_destroy`, `jsonw_pretty`, `jsonw_reset`, `jsonw_name`, `jsonw_printf`, `jsonw_vprintf_enquote`, object/array start/end functions, primitive writers, and field helpers. Internal helpers handle indentation, end-of-line, comma insertion, and JSON string escaping.

Control flow: writer tracks `depth` and `sep`. Starting a collection writes any needed comma, emits `{`/`[`, increments depth, and resets separator. Ending decrements depth and writes closing delimiter. Names and values manage separators so callers can stream JSON incrementally.

State and persistence: heap-allocated `json_writer` holds output file, depth, pretty flag, and separator. Destroy asserts balanced depth, writes newline, flushes, frees, and nulls caller pointer.

Dependencies and integration points: used by bpftool-derived or selftest output code needing JSON without external dependencies.

Risks: string escaping does not emit Unicode escapes for control characters beyond common C escapes; `jsonw_destroy` asserts rather than returning an error on unbalanced JSON; header declares `jsonw_float` while implementation keeps it under `#ifdef notused`.

Test signals: `#ifdef TEST` main exercises nested objects/arrays and escaping; consumers can validate emitted JSON syntax.
