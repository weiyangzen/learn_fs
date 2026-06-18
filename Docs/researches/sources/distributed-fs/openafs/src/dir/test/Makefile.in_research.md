# sources/distributed-fs/openafs/src/dir/test/Makefile.in

This Makefile builds the directory test utility `dtest`. It includes config and LWP make fragments, links `dtest.o` with `libdir.a`, `liblwp.a`, `libopr.a`, roken, and platform libraries, and defines minimal `all`, `install`, and `clean` targets.

There is no runtime state in the Makefile; build state is `dtest` and object files. Integration is the parent `src/dir` test target. Risks are that `install` only depends on `dtest` and does not stage it anywhere, and the test is built but not automatically run. Test signal is successful compilation/linking of `dtest`, which verifies the userspace callback surface required by `buffer.c`.
