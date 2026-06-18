# sources/distributed-fs/ceph-client/tools/perf/tests/hists_common.h

## Purpose
Declares the shared constants and helpers for perf histogram tests that operate on a synthetic machine with known pids, maps, IPs, and symbols.

## Important APIs, Types, and Functions
- Defines fake pids: `FAKE_PID_PERF1`, `FAKE_PID_PERF2`, and `FAKE_PID_BASH`.
- Defines fake map bases and length for perf, bash, libc, and kernel.
- Defines symbol offsets/length and derived fake IPs for all symbols used by histogram sample tables.
- Declares `setup_fake_machine(struct machines *machines)`, `print_hists_in(struct hists *hists)`, and `print_hists_out(struct hists *hists)`.

## Control Flow
This header has no executable control flow. Its embedded comment documents the expected synthetic process/DSO/symbol matrix that `setup_fake_machine()` implements.

## State and Persistence
No state is stored by the header. It establishes compile-time constants shared by multiple `.c` tests.

## Dependencies and Integration Points
Forward-declares `struct machine` and `struct machines`; consumers rely on perf histogram and machine headers for full types. It is included by the histogram tests and the shared implementation file.

## Risks and Edge Cases
- If a fake IP macro no longer matches the symbol ranges created in `hists_common.c`, downstream resolution tests will fail or validate the wrong entry.
- The header documents only one synthetic fixture shape; adding new histogram tests should preserve these constants or clearly extend them.

## Test Signals
No direct suite. Correctness is signaled by successful compilation and by downstream histogram tests resolving the declared fake IPs to the intended symbols.
