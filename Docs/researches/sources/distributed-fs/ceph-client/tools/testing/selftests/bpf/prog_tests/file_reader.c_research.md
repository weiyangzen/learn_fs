# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/file_reader.c

## Purpose
Tests BPF file-reading behavior on executable file contents, including successful reads and expected page-fault handling, plus generated negative verifier/load cases.

## Important APIs, types, and functions
Uses `file_reader.skel.h`, `file_reader_fail.skel.h`, `dladdr()` to get executable base, `/proc/self/exe`, `madvise(MADV_PAGEOUT)`, skeleton autoload selection by program name, and BSS buffers. `initialize_file_contents()` reads 256 KiB from the executable and pages out a 512 KiB range around the executable mapping.

## Control flow and state
`run_test()` initializes file contents, opens the skeleton, autoloads only the requested program, copies expected bytes into BSS `user_buf`, sets current PID, loads/attaches, opens `/proc/self/exe` to trigger, and asserts BSS `err == 0` and `run_success == 1`. Top-level runs two positive subtests and `RUN_TESTS(file_reader_fail)`. State includes global `file_contents`, user pointer string, paged-out executable mapping range, and skeleton BSS.

## Dependencies and integration points
Depends on executable mapping introspection through libdl, procfs, page-out support, generated file reader programs, and BPF file read helper/kfunc support. Integrated as `test_file_reader()`.

## Risks and test signals
Risks include executables smaller than 256 KiB, `MADV_PAGEOUT` behavior, and address alignment assumptions. Passing signals are full executable read, successful page-out calls, trigger open, zero BSS error, success flag set, and generated negative tests failing as expected.
