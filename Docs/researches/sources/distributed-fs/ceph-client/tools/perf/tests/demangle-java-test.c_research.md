# sources/distributed-fs/ceph-client/tools/perf/tests/demangle-java-test.c

Purpose: `demangle-java-test.c` verifies perf's Java symbol demangler for JVM descriptor-style method names.

Important APIs and state: the test calls `dso__demangle_sym(NULL, 0, mangled)` over a table of mangled and expected strings. It uses `pr_debug` for mismatches and registers `"Demangle Java"`.

Control flow: each case demangles a Java-like method descriptor, checks for non-null output, compares against the expected dotted class/method/signature form, frees the buffer, and accumulates failure state.

State and persistence: all state is local; returned demangled strings are freed.

Dependencies, integration, risks, and tests: it depends on perf's symbol demangler dispatch recognizing Java names. Risks are expected-output drift as demangling behavior is improved or descriptor coverage expands. Test signals are exact matches for StringLatin1, ZipUtils, regex, AbstractStringBuilder, and constructor descriptors.
