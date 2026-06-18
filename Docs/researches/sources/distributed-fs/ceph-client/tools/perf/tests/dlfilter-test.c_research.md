# sources/distributed-fs/ceph-client/tools/perf/tests/dlfilter-test.c

Purpose: `dlfilter-test.c` tests perf script's dlfilter C API by synthesizing a perf.data stream and running versioned test filter shared objects against it.

Important APIs and state: `struct test_data` carries the synthetic machine, file descriptors, generated C/program/perf.data paths, symbol addresses, and selected dlfilter name/description. Helpers write attr, comm, mmap, and sample records; compile a small C program; locate symbols with `nm`; and run `perf script --dlfilter`.

Control flow: each API version test locates the dlfilter shared object, verifies its description, requires gcc, writes and compiles a program with `foo` and `bar`, resolves their addresses, creates a pipe-mode perf.data file with attr/comm/mmap/sample events, optionally dumps it under high verbosity, then runs `perf script` with dlfilter arguments for multiple early/normal modes. Version 0 and 2 are tested.

State and persistence: temporary C, executable, and perf.data files are created under `/tmp` and removed unless verbosity is high. The machine and fd are cleaned up.

Dependencies, integration, risks, and tests: it depends on gcc, perf executable discovery, dlfilter test shared objects, symbol tools, synthetic event helpers, and filesystem permissions. Risks include shell command quoting limits, missing gcc/filter artifacts, and environment-sensitive paths. Test signals are successful filter description lookup and all `perf script --dlfilter` invocations returning zero.
