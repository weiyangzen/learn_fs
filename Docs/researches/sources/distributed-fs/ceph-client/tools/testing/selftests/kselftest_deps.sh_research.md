# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_deps.sh

`kselftest_deps.sh` checks build-time library dependencies for kselftests. It parses Makefiles for `LDLIBS` patterns, compiles a trivial C program with each library set using a supplied compiler, reports pass/fail results, and can print a filtered target list.

Important functions are `usage()`, `main()`, `all_tests()`, `l1_test()` through `l5_test()`, `check_libs()`, and `print_results()`. It uses grep/sed/awk/find to detect static `LDLIBS`, target-specific `: LDLIBS`, `VAR_LDLIBS`, pkg-config fallbacks, and `IOURING_EXTRA_LIBS`.

Control flow requires running from the top-level `tools/testing/selftests` directory, parses optional `-p`, creates temporary source and pass/fail logs, extracts top-level `TARGETS`, builds Makefile candidate lists, optionally restricts to one test, compiles the trivial program for each library token/set, records failing targets/libs, and prints summaries. It does not modify source files.

Dependencies are bash, coreutils, grep/sed/awk/find, and a native or cross compiler. Integration is with selftest Makefile conventions and build-target selection. Risks include grep-based parsing missing complex make expressions, multiple `trap ... EXIT` assignments replacing earlier cleanup traps, and unusual `shift` behavior in option parsing. Pass signals are successful compile checks and accurate suggested targets when `-p` is requested.
