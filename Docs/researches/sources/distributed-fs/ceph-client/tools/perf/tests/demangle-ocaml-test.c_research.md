# sources/distributed-fs/ceph-client/tools/perf/tests/demangle-ocaml-test.c

Purpose: `demangle-ocaml-test.c` checks OCaml symbol demangling behavior.

Important APIs and state: it calls `dso__demangle_sym` on a small table containing a non-OCaml symbol and OCaml-encoded names. The suite is `"Demangle OCaml"`.

Control flow: each test case accepts either null output for non-demangled input or an exact demangled string. It reports mismatches with `pr_debug`, frees any returned buffer, and returns failure if any case differs.

State and persistence: no persistent state; allocations are freed per case.

Dependencies, integration, risks, and tests: it depends on perf's OCaml demangler and encoding rules for module separators and escaped punctuation. Risks are strict expected strings when demangler policy changes. Test signals include `main` remaining undemangled and OCaml names producing `Stdlib.array.map_154`, source-location anonymous function text, and operator decoding.
