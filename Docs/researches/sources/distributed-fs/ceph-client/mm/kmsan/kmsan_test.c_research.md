# sources/distributed-fs/ceph-client/mm/kmsan/kmsan_test.c

## Purpose
`kmsan_test.c` is the KUnit test suite for KMSAN. It intentionally creates initialized, uninitialized, copied, freed, vmapped, percpu, and stack-origin data flows, then verifies whether KMSAN reports or suppresses reports as expected.

## Important APIs, Types, And Functions
The suite uses a console tracepoint probe (`probe_console()`) to capture `BUG: KMSAN:` report headers into the `observed` state. `struct expect_report` describes expected error type and symbol. Helpers `report_available()`, `report_reset()`, and `report_matches()` compare captured output against expected report headers. Test cases cover kmalloc/kzalloc, stack variables, parameters, `kmsan_check_memory()`, vmap/vmalloc, UAF for slab and pages, percpu propagation, printk, memcpy alignment, origin gaps, memset variants, guarded buffers, long origin chains, stack depot, explicit unpoisoning, and `copy_from_kernel_nofault()`.

## Control Flow
Suite init registers the console tracepoint and disables `panic_on_kmsan`. Each test resets observed report state, performs operations intended to create or avoid poisoned metadata, and asserts `report_matches()`. Tests that expect multiple reports call `report_reset()` between checks. Suite exit unregisters the tracepoint, synchronizes tracepoint removal, and restores the original panic setting.

## State And Persistence
Persistent test state is the static `observed` capture buffer protected by a spinlock, plus saved `orig_panic_on_kmsan`. Individual tests allocate transient slab, page, vmalloc, vmap, and stack objects and free/unmap them where needed. The suite mutates global `panic_on_kmsan` for the duration of the tests to keep expected reports from panicking the kernel.

## Dependencies And Integration Points
It depends on KUnit, KMSAN public and private APIs, printk tracepoints, stack depot, slab/page/vmalloc/vmap allocation, percpu variables, `copy_from_kernel_nofault()`, and compiler KMSAN instrumentation enabled specifically for this object by the Makefile.

## Risks
Report matching is string/symbol based and strips offsets, so symbol naming or report formatting changes can break tests. The console tracepoint captures the first matching report and then ignores further output until reset, which keeps tests deterministic but can hide extra unexpected reports within a single test. Tests deliberately use uninitialized variables, so build flags must suppress compiler diagnostics without optimizing away the flows.

## Test Signals
This file is itself the primary test signal for KMSAN. Passing cases indicate correct poisoning/unpoisoning, origin propagation, UAF tagging, report formatting, metadata mapping for vmalloc/vmap/pages, and behavior of compiler-inserted hooks. Failures identify specific runtime contracts because each case has a narrow expected report/no-report outcome.
