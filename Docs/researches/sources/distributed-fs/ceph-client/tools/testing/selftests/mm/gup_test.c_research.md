# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/gup_test.c

## Purpose
`gup_test.c` is a command-line kselftest client and benchmark driver for the kernel `gup_test` debugfs interface. It exercises GUP fast, PIN fast, long-term PIN benchmarks, basic GUP/PIN tests, and page dumping.

## Important APIs, types, and functions
The program uses `struct gup_test` and ioctl command constants from `<mm/gup_test.h>`. `cmd_to_str()` formats command names. `gup_thread()` runs one ioctl sequence and reports timing for benchmark commands or completion for functional commands. `main()` parses options such as command selection, size, repeat count, pages per call, thread count, THP hints, file path, shared/private mapping, hugetlb mapping, write flag, and dump-page indices.

## Control flow
`main()` opens the requested file, opens `/sys/kernel/debug/gup_test`, maps the configured size, optionally applies `MADV_HUGEPAGE` or `MADV_NOHUGEPAGE`, faults every base page in from userspace, then starts `nthreads` identical worker threads. Each worker copies the shared `struct gup_test`, sets the current size, runs the selected ioctl, prints timing or completion under `print_mutex`, and emits a kselftest result.

## State and persistence behavior
The file creates or opens a mapping source, modifies the mapped memory to fault pages in, and may create a shared or hugetlb mapping depending on flags. Kernel-side pin/get operations are delegated to the debugfs driver. No durable state is intentionally written except the optional file backing chosen by `-f`.

## Dependencies and integration points
The test requires debugfs mounted at `/sys/kernel/debug`, `CONFIG_GUP_TEST`, and sufficient permissions to open the debugfs node. It uses pthreads, kselftest, `vm_util` page-size helpers, mmap, madvise, and kernel ioctl definitions.

## Risks and edge cases
The default maps 128 MiB, so memory pressure and hugetlb availability can affect runs. Thread output is serialized, but all threads share the same `gup_fd`. The test skips rather than fails when the debugfs interface is unavailable. Some flags are passed through to kernel internals and may only be meaningful for specific ioctl commands.

## Test signals
Each thread produces a kselftest result from the ioctl status. Benchmark commands print get/put microsecond deltas and truncated sizes; functional commands print completion and optional truncation.
