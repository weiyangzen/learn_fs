# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/dexcr.c

## Purpose
Common helper implementation for DEXCR tests and utilities.

## Important APIs, Types, and Functions
Implements `dexcr_exists()`, `pr_which_to_aspect()`, `pr_get_dexcr()`, `pr_set_dexcr()`, `pr_dexcr_aspect_supported()`, `pr_dexcr_aspect_editable()`, `hashchk_triggers()`, `get_dexcr()`, `await_child_success()`, `hashst()`, `hashchk()`, and `do_bad_hashchk()`.

## Control Flow
Helpers probe DEXCR SPR access under a SIGILL handler, wrap prctl get/set operations, read userspace/hypervisor/effective DEXCR SPR values, wait for children, and emit raw hash instructions for NPHIE/hashchk tests.

## State and Persistence
State includes temporary signal handlers/jump buffers and hardware/process DEXCR state read or modified by callers. Hash helpers mutate caller-provided memory.

## Dependencies and Integration Points
Depends on `reg.h` mfspr/mtspr macros, `dexcr.h` raw instruction encodings, prctl constants, signal handling, and `utils.h` failure helpers.

## Risks and Test Signals
Risks include longjmp from signal contexts, unsupported SPR emulation, and raw instruction encoding correctness. Test signals are skipped unsupported hardware, SIGILL behavior, and child wait assertions.
