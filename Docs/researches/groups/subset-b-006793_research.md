# subset-b-006793 research

Grouped research for arm64 MTE, PAUTH, signal, tagged-address, and BPF benchmark selftest sources. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_mmap_options.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_mmap_options.c

## Purpose

This MTE selftest validates tag-check behavior across anonymous mappings, file-backed mappings, `PROT_MTE` mappings created directly or via `mprotect()`, PSTATE.TCO override, address tag bits, private/shared mappings, synchronous/asynchronous fault modes, and store-only tag checking when supported. It deliberately accesses underflow and overflow guard granules around a tagged payload to verify when tag faults should and should not appear.

## Important APIs, Types, and Functions

Important local types are `enum mte_mem_check_type`, `enum mte_tag_op_type`, and `struct check_mmap_testcase`, which encode the matrix consumed by `main()`. Core helpers are `check_mte_memory()`, `check_anonymous_memory_mapping()`, `check_file_memory_mapping()`, `check_clear_prot_mte_flag()`, and `format_test_name()`. The test relies on `mte_switch_mode()`, `mte_allocate_memory()`, `mte_allocate_file_memory()`, tag insertion/clearing helpers, `mprotect()`, `mmap()` semantics, kselftest result APIs, and the global `cur_mte_cxt` fault context from `mte_common_util.c`.

## Control Flow and Data Flow

`main()` sizes boundary cases using the runtime page size, initializes MTE, installs the SIGSEGV handler, builds a testcase table, and evaluates each row. Mapping checks allocate a larger region with one granule before and after the tested range, tag the payload, perform in-range writes, then write before and after the range. Expected fault presence is compared with the testcase's tag-check setting. Store-only rows additionally load from invalidly tagged guard granules to confirm loads remain allowed. The clear-`PROT_MTE` path calls `mprotect()` without `PROT_MTE` and verifies the mapping remains tag checked.

## State and Persistence Behavior

There is no persistent state beyond temporary files in `/dev/shm`, immediately unlinked, and transient mappings. Global MTE state is saved by `mte_default_setup()` and restored at exit. Fault state is stored in `cur_mte_cxt` between an access and `mte_wait_after_trig()`. PSTATE.TCO is optionally enabled for testcases where tag checks should be suppressed.

## Dependencies and Integration Points

The file integrates with arm64 MTE kernel ABI support, `PR_SET_TAGGED_ADDR_CTRL`, `PROT_MTE`, MTE FAR/address-tag reporting, optional `PR_MTE_STORE_ONLY`, and the assembly tag helpers. It is built by the arm64 MTE selftest Makefile and depends on kselftest reporting.

## Risks and Edge Cases

Boundary sizes include subgranule, exact-granule, page-minus-one, page, and page-plus-one lengths, which catches alignment and rounding bugs. Risks include false failures if optional MTE FAR or store-only support is not detected correctly, if asynchronous faults are not drained before checking, or if temporary file creation returns zero even though callers treat only `-1` as failure. Clearing `PROT_MTE` must be ignored by the kernel for an existing MTE mapping, so this test is sensitive to ABI changes.

## Test Signals

Passing output shows all generated kselftest rows pass or skip only unsupported optional store-only/address-tag cases. Failure signals are missing guard faults when tag checks are on, unexpected guard faults when TCO or no-error mode should suppress checks, failed tag insertion on eligible mappings, or `mprotect()` allowing `PROT_MTE` to be cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_mmap_options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_prctl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_prctl.c

## Purpose

This standalone MTE ABI test verifies that `PR_GET_TAGGED_ADDR_CTRL` can be read and that `PR_SET_TAGGED_ADDR_CTRL` accepts and reports the supported MTE tag-check modes, including optional store-only checking.

## Important APIs, Types, and Functions

`set_tagged_addr_ctrl()` and `get_tagged_addr_ctrl()` wrap `prctl()` calls with kselftest diagnostics. `check_basic_read()` validates a baseline read before configuration. `set_mode_test()` gates each requested mode on `AT_HWCAP2` and `AT_HWCAP3`, sets the mask, reads it back, and compares `PR_MTE_TCF_MASK | PR_MTE_STORE_ONLY`. `struct mte_mode` defines the tested combinations.

## Control Flow and Data Flow

`main()` prints a kselftest header, sets a plan based on `mte_modes`, runs the baseline read, then loops over mode descriptors. Data flows from auxv hardware capability bits into skip decisions, from requested `mask` into `PR_SET_TAGGED_ADDR_CTRL`, and back through `PR_GET_TAGGED_ADDR_CTRL` for equality checking.

## State and Persistence Behavior

The test changes the calling process's tagged-address control state but does not preserve or restore a previous value. It has no files or heap state. The observable state is the process-local PRCTL setting and kselftest counters.

## Dependencies and Integration Points

It depends on arm64 tagged-address/MTE PRCTL constants, `AT_HWCAP2`, `AT_HWCAP3`, `HWCAP2_MTE`, and `HWCAP3_MTE_STORE_ONLY`. It intentionally decouples from the broader MTE utility library and can validate the core PRCTL ABI even without allocating MTE memory.

## Risks and Edge Cases

The test plan count uses `ARRAY_SIZE(mte_modes)` but also emits `check_basic_read()`, so consumers should check the exact kselftest framework behavior if plan accounting changes. Store-only rows must skip on systems without `HWCAP3_MTE_STORE_ONLY`. Error messages print the TCF mask but compare the combined TCF/store-only mask, so debugging store-only mismatches requires reading the expected mask.

## Test Signals

Expected results are a pass for basic read and each supported mode, skips for unsupported hardware modes, and failure if a supported mode cannot be set or is not read back exactly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_prctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_tags_inclusion.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_tags_inclusion.c

## Purpose

This MTE test verifies tag inclusion masks passed through `PR_SET_TAGGED_ADDR_CTRL`. It checks that random tag generation excludes the requested tags, includes all tags when allowed, and falls back to tag zero when all nonzero tags are excluded.

## Important APIs, Types, and Functions

The main helpers are `verify_mte_pointer_validity()`, `check_single_included_tags()`, `check_multiple_included_tags()`, `check_all_included_tags()`, and `check_none_included_tags()`. The file uses `MT_INCLUDE_VALID_TAG()`, `MT_INCLUDE_VALID_TAGS()`, `MT_INCLUDE_TAG_MASK`, `MT_EXCLUDE_TAG_MASK`, `mte_switch_mode()`, `mte_insert_tags()`, and `MT_FETCH_TAG()`.

## Control Flow and Data Flow

After `mte_default_setup()` and signal registration, `main()` runs four sync-mode tests. Each test allocates MTE memory, switches the tag inclusion mask, repeatedly inserts tags, and validates both the generated logical tag and the actual access behavior. `verify_mte_pointer_validity()` writes inside the tagged range, then for nonzero tags writes one byte past the range to ensure a precise tag fault is observed.

## State and Persistence Behavior

State is process-local MTE PRCTL configuration and a single tagged mapping per test. `cur_mte_cxt` tracks whether the expected access fault occurred. No persistent files are created.

## Dependencies and Integration Points

The test depends on arm64 MTE allocation helpers, synchronous tag fault delivery, and kselftest reporting. It complements mapping tests by focusing on GCR_EL1 tag generation policy exposed to userspace through inclusion masks.

## Risks and Edge Cases

Because random tag generation is probabilistic, loops run `MT_TAG_COUNT * 2` times to increase confidence but cannot prove distributions. The multiple-inclusion check compares tag ordering against the growing exclusion mask, so a future change in tag numbering semantics would require review. The file defines `MTE_LAST_TAG_MASK` but does not use it.

## Test Signals

Failures indicate generated tags falling in excluded masks, unexpected in-range faults, missing out-of-range tag faults, or all-excluded mode producing a nonzero tag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_tags_inclusion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_user_mem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_user_mem.c

## Purpose

This test verifies how kernel user-memory access helpers handle MTE-tagged userspace buffers during `read`, `write`, `readv`, and `writev`. It checks that invalid tags in user buffers are rejected in synchronous mode but may be accepted in asynchronous mode according to the arm64 MTE userspace ABI.

## Important APIs, Types, and Functions

`enum test_type` selects syscall families. `check_usermem_access_fault()` creates a temporary file, fills it, maps tagged memory, tags a subrange with a new allocation tag, and tries many offset/size combinations. `format_test_name()` renders kselftest names. The test uses `read()`, `write()`, `readv()`, `writev()`, `mte_set_tag_address_range()`, `mte_insert_new_tag()`, and `cur_mte_cxt`.

## Control Flow and Data Flow

`main()` initializes the page size and MTE state, then iterates over four syscall types, sync/async modes, private/shared mappings, whole-tail versus one-granule tag lengths, and page/granule tag offsets for 64 planned rows. Each row first proves a valid tagged read succeeds, mutates a selected part of the buffer to an invalid tag, then tests file and pointer offsets from 0 to 15 with sizes from 1 byte to one page.

## State and Persistence Behavior

The temporary file is unlinked after creation by the common helper and closed at test end. MTE mode is restored by `mte_restore_setup()`. Per-row memory and tag state is freed through `mte_free_memory()`.

## Dependencies and Integration Points

This is an integration test between arm64 MTE userspace tagging, kernel `copy_{to,from}_user()` paths used by file syscalls, vectored I/O, tmpfs-backed temporary files, and kselftest. It is especially relevant to filesystem and VFS paths because the kernel copies data through user pointers.

## Risks and Edge Cases

The expected length comparison in synchronous mode checks `syscall_len < len` rather than `syscall_len < size`, so a short transfer is treated as sufficient evidence of rejection. Async mode accepts full-size success. Offset loops intentionally exercise every byte alignment inside an MTE granule. Resource cleanup can be skipped on early file-fill write failure.

## Test Signals

Passing rows show no delivered SIGSEGV from kernel user access, synchronous syscalls returning short/error for invalid tags, and asynchronous syscalls completing the requested size. Any unexpected signal, valid-buffer mismatch, or wrong transfer length fails the row.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_user_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_common_util.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_common_util.c

## Purpose

This file is the shared runtime for the arm64 MTE selftests. It hides MTE setup/restore, signal handling, memory allocation, file-backed mapping preparation, tag insertion/clearing, address-tag manipulation, and PRCTL mode switching behind reusable helpers.

## Important APIs, Types, and Functions

It defines global `cur_mte_cxt`, `mtefar_support`, and `mtestonly_support`. Important exported functions include `mte_default_handler()`, `mte_register_signal()`, `mte_insert_tags()`, `mte_clear_tags()`, `mte_insert_atag()`, `mte_allocate_memory()`, `mte_allocate_memory_tag_range()`, `mte_allocate_file_memory()`, `mte_allocate_file_memory_tag_range()`, `mte_free_memory()`, `mte_switch_mode()`, `mte_default_setup()`, `mte_restore_setup()`, and `create_temp_file()`.

## Control Flow and Data Flow

`mte_default_setup()` seeds randomness, checks `HWCAP2_MTE`, records optional MTE FAR/store-only support, saves current PRCTL mode and PSTATE.TCO, and disables TCO. Allocation flows through `__mte_allocate_memory_range()`, which selects malloc, mmap with `PROT_MTE`, or mmap plus `mprotect(PROT_MTE)`, optionally tagging the requested range. The default signal handler decodes SIGSEGV/SIGBUS, compares fault address/range/code against `cur_mte_cxt`, marks valid faults, and advances PC for synchronous faults so tests continue.

## State and Persistence Behavior

The file maintains process-global current MTE mode, saved PSTATE.TCO, saved store-only mode, and current expected fault context. Mappings and temporary files are transient; temp files are created in `/dev/shm` and unlinked. `mte_restore_setup()` restores the saved PRCTL mode and TCO state.

## Dependencies and Integration Points

It depends on auxv hardware capabilities, arm64 `prctl(PR_SET_TAGGED_ADDR_CTRL)`, `PROT_MTE`, signal `SA_EXPOSE_TAGBITS`, MTE SIGSEGV si_codes, and assembly routines from `mte_helper.S`. All MTE test programs in this directory depend on this utility layer.

## Risks and Edge Cases

The signal handler exits on unexpected precise faults, making expected-context initialization critical. `create_temp_file()` returns `0` on failure even though many callers check `-1`, which is a latent reporting bug. File initialization uses an uninitialized stack buffer because content is irrelevant, but static analyzers may flag it. Malloc arithmetic uses `void *` extensions and assumes GNU C.

## Test Signals

The strongest validation is the dependent MTE tests passing in sync, async, store-only, mapping, and user-copy scenarios. Utility-specific failure signals include skipped execution without `HWCAP2_MTE`, PRCTL failures, allocation failures, invalid fault-address diagnostics, and failure to restore TCO/mode after a suite run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_common_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_common_util.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_common_util.h

## Purpose

This header declares the public MTE selftest utility interface and provides small kselftest-facing inline validators. It is the contract between individual MTE test programs, the C helper implementation, and the arm64 assembly tag helpers.

## Important APIs, Types, and Functions

The header defines `enum mte_mem_type`, `enum mte_mode`, and `struct mte_fault_cxt`. It declares all allocation, free, tag, signal, setup, restore, mode-switch, and current-context helpers. It also declares assembly entry points such as `mte_insert_random_tag()`, `mte_set_tag_address_range()`, and PSTATE.TCO helpers. Inline helpers are `evaluate_test()`, `check_allocated_memory()`, and `check_allocated_memory_range()`.

## Control Flow and Data Flow

There is no standalone control flow. Test binaries include this header, call setup, allocate/tag memory, initialize `cur_mte_cxt`, perform an access, then use the inline result helpers to convert numeric `KSFT_*` results into kselftest output.

## State and Persistence Behavior

The header exposes globals `cur_mte_cxt`, `mtefar_support`, and `mtestonly_support` but does not own storage. Its inline validators may free failed allocations, so callers must not double-free after a failed validation.

## Dependencies and Integration Points

It integrates with `mte_def.h`, kselftest, libc signal types, mmap/prctl headers, and `mte_helper.S`. It is intentionally test-local rather than a kernel ABI header.

## Risks and Edge Cases

The inline allocation validators assume tagged allocations should have a nonzero logical tag when `tags` is true. This is correct for the helper usage but would be wrong for tests intentionally allowing tag zero. The range validator always expects a tag and clears via the range-free helper on failure.

## Test Signals

Compilation of every MTE test is the primary contract check. Runtime failures in allocation validation are surfaced as kselftest failures with diagnostic messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_common_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_def.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_def.h

## Purpose

This header provides local MTE constants and tag-manipulation macros so the selftests can build against older or sanitized headers that may not expose the newest arm64 MTE ABI definitions.

## Important APIs, Types, and Functions

It defines fallback values for `SEGV_MTEAERR`, `SEGV_MTESERR`, `PROT_MTE`, `HWCAP2_MTE`, and MTE PRCTL TCF bits. It also defines tag positions, tag masks, granule size/count, address-tag positions, PSTATE.TCO bit constants, alignment helpers, and inclusion/exclusion mask macros such as `MT_FETCH_TAG()`, `MT_SET_TAG()`, `MT_CLEAR_TAGS()`, and `MTE_ALLOW_NON_ZERO_TAG`.

## Control Flow and Data Flow

There is no control flow. The macros transform pointer-sized integers, align byte counts to 16-byte MTE granules, and construct tag inclusion masks passed to PRCTL.

## State and Persistence Behavior

The header carries no runtime state. Its constants persist as part of the test source and must remain ABI-compatible with Linux arm64 MTE definitions.

## Dependencies and Integration Points

It is included by both C utilities and `mte_helper.S`. It bridges kernel ABI values, MTE architectural layout, and selftest logic.

## Risks and Edge Cases

Incorrect fallback constants would make tests fail or silently test the wrong ABI on systems with older headers. Macro arguments are not fully parenthesized in every shift expression, so callers should pass simple integer expressions. `MT_ALIGN_UP(0)` returns 0, which the assembly range loops handle.

## Test Signals

Successful compilation against varying header versions and correct runtime behavior of all MTE tests validate the constants. Failures usually appear as wrong tag extraction, wrong PRCTL masks, or unexpected signal si_codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_helper.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_helper.S

## Purpose

This arm64 assembly file implements the MTE instructions that C cannot express portably: generating logical tags, reading allocation tags, setting/clearing allocation tags across a range, and controlling PSTATE.TCO.

## Important APIs, Types, and Functions

Exported entry points are `mte_insert_random_tag`, `mte_insert_new_tag`, `mte_get_tag_address`, `mte_set_tag_address_range`, `mte_clear_tag_address_range`, `mte_enable_pstate_tco`, `mte_disable_pstate_tco`, and `mte_get_pstate_tco`. Instructions include `irg`, `gmi`, `ldg`, `stg`, `stzg`, `msr tco`, and `mrs tco`.

## Control Flow and Data Flow

Tag-range functions loop in 16-byte `MT_GRANULE_SIZE` steps until the requested range reaches zero. Pointer arguments are passed in `x0`, range in `x1`, and return values in `x0` per AAPCS64. PSTATE helpers write or extract the TCO bit directly.

## State and Persistence Behavior

The range helpers mutate allocation tags in memory and PSTATE helpers mutate process CPU state. The file has no static storage.

## Dependencies and Integration Points

It requires `.arch armv8.5-a+memtag` and constants from `mte_def.h`. The C helper layer calls these routines after validating alignment and range rounding.

## Risks and Edge Cases

Callers must provide granule-aligned pointers and granule-rounded sizes; otherwise architectural behavior or partial coverage may be wrong. TCO changes must be restored by higher-level setup/restore logic. These instructions require MTE-capable hardware.

## Test Signals

All MTE tests depend on these helpers. Specific failure patterns include inability to create nonzero tags, stale tags after clear, missing tag faults, or TCO override not suppressing faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_helper.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/Makefile

## Purpose

The PAUTH Makefile builds the arm64 pointer-authentication selftests only when the compiler can generate the required code. It creates the main `pac` test, helper objects, and the `exec_target` helper program used to observe key changes across `exec()`.

## Important APIs, Types, and Functions

The Makefile sets `CFLAGS += -mbranch-protection=pac-ret`, probes GCC support for `-march=armv8.3-a`, trusts LLVM support, and emits `TEST_GEN_PROGS`, `TEST_GEN_FILES`, and `TEST_GEN_PROGS_EXTENDED`. Custom rules compile PAC-instruction users at ARMv8.3 and the runnable test executables at ARMv8.2.

## Control Flow and Data Flow

Make evaluates compiler support, conditionally registers generated tests, includes `../../lib.mk`, then applies custom object and binary rules. `helper.o` and `pac_corruptor.o` feed into `pac`; `helper.o` also feeds into `exec_target`.

## State and Persistence Behavior

No runtime state is stored. Build outputs are kselftest artifacts in `$(OUTPUT)`.

## Dependencies and Integration Points

It depends on kselftest `lib.mk`, the selected C compiler, branch-protection support, and arm64 architecture levels. The split ARMv8.2/ARMv8.3 targeting allows unsupported hardware to run the binary and report meaningful skips rather than faulting before checks.

## Risks and Edge Cases

The support probe is compiler-sensitive. Building too much code for ARMv8.3 can turn intended runtime skip/failure paths into illegal-instruction crashes on older CPUs. Cross-compile `CC` handling preserves top-level settings unless `CC` is plain `cc`.

## Test Signals

Expected build output includes `pac`, `exec_target`, `pac_corruptor.o`, and `helper.o` when compiler support exists; unsupported compilers should skip these targets cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/exec_target.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/exec_target.c

## Purpose

`exec_target` is the worker process used by `pac.c` to sign a value after `exec()`. Its output lets the parent compare pointer-authentication keys before and after exec.

## Important APIs, Types, and Functions

`main()` reads one `size_t` from stdin, checks `AT_HWCAP`, signs the value with `keyia_sign()`, `keyib_sign()`, `keyda_sign()`, `keydb_sign()`, and optionally `keyg_sign()`, then writes `struct signatures` to stdout.

## Control Flow and Data Flow

The parent sends a value through a pipe. The child reads it, signs it with all supported keys, fills unsupported generic output with zero, and writes the binary structure back. There is no text protocol.

## State and Persistence Behavior

The program is stateless beyond process-local PAC keys created by the kernel during exec. It stores no files.

## Dependencies and Integration Points

It depends on `helper.h`, auxv `HWCAP_PACA` and `HWCAP_PACG`, stdin/stdout pipes, and the parent `exec_sign_all()` routine in `pac.c`.

## Risks and Edge Cases

The caller is expected to have checked feature support; missing `HWCAP_PACA` leaves four structure fields uninitialized before write, though the normal parent skips without PACA. Short input causes a failure exit.

## Test Signals

The parent treats nonzero exit, short read/write, or unchanged signatures across exec as failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/exec_target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/helper.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/helper.c

## Purpose

This file wraps arm64 pointer-authentication instructions in simple C-callable helpers used by PAUTH tests.

## Important APIs, Types, and Functions

Functions `keyia_sign()`, `keyib_sign()`, `keyda_sign()`, and `keydb_sign()` use `paciza`, `pacizb`, `pacdza`, and `pacdzb` with zero modifiers. `keyg_sign()` uses `pacga` with a zero modifier and returns the generated value.

## Control Flow and Data Flow

Each helper takes a `size_t`, executes one inline assembly instruction, and returns the signed or generated result. `keyg_sign()` writes into a separate destination register because generic PAC output is not an authenticated pointer.

## State and Persistence Behavior

The functions read architecture-managed PAC keys but keep no state.

## Dependencies and Integration Points

They are compiled for ARMv8.3 by the Makefile and shared by `pac.c` and `exec_target.c`.

## Risks and Edge Cases

Calling these helpers without matching hardware support can SIGILL because data/generic PAC instructions are not always in NOP space. Tests gate calls on HWCAP bits.

## Test Signals

The benchmark-style loops in `pac.c` expect the PAC fields masked by `PAC_MASK` to become nonzero and differ across keys where appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/helper.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/helper.h

## Purpose

This header defines the PAUTH helper ABI shared between the parent test, exec worker, and assembly corruptor.

## Important APIs, Types, and Functions

It defines `NKEYS`, `struct signatures`, declares `pac_corruptor()`, and declares five signing helpers for IA, IB, DA, DB, and generic keys.

## Control Flow and Data Flow

There is no control flow. The fixed field order in `struct signatures` is the binary pipe protocol between `pac.c` and `exec_target.c`.

## State and Persistence Behavior

The header owns no storage. The structure persists only in process memory or pipe payloads.

## Dependencies and Integration Points

It depends on `size_t` from `<stdlib.h>` and is consumed by all PAUTH selftest sources.

## Risks and Edge Cases

Changing field order or `NKEYS` breaks comparisons and worker protocol. The structure is not versioned or endian-neutral because parent and worker are the same local binary set.

## Test Signals

Compilation and correct parent/worker signature comparison validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/pac.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/pac.c

## Purpose

`pac.c` is the main pointer-authentication selftest. It verifies that PAC instructions are active, corrupted return authentication faults, different keys produce distinguishable signatures, exec changes keys, and context switches preserve keys.

## Important APIs, Types, and Functions

Important helpers are `sign_specific()`, `sign_all()`, `n_same()`, `n_same_single_set()`, `exec_sign_all()`, and `pac_signal_handler()`. Test cases are `corrupt_pac`, `pac_instructions_not_nop`, `pac_instructions_not_nop_generic`, `single_thread_different_keys`, `exec_changed_keys`, `context_switch_keep_keys`, and `context_switch_keep_keys_generic`.

## Control Flow and Data Flow

Feature macros gate tests with `HWCAP_PACA` and `HWCAP_PACG`. `exec_sign_all()` creates stdin/stdout pipes, pins execution to one CPU to force a useful context switch, forks, execs `exec_target`, writes a value, waits for completion, then reads back signatures. Collision-sensitive tests repeat up to `PAC_COLLISION_ATTEMPTS`.

## State and Persistence Behavior

The test changes signal handlers for SIGSEGV/SIGILL during corrupt-PAC validation and pins process affinity during exec comparisons. PAC keys are kernel-managed process/thread state. No persistent files are written.

## Dependencies and Integration Points

It uses `kselftest_harness.h`, helper functions, `pac_corruptor.S`, `exec_target`, auxv HWCAPs, pipes, fork/exec, wait, and CPU affinity APIs. It must be run from a directory where `exec_target` is executable under that name.

## Risks and Edge Cases

PAC bit width can be small, so equality checks are probabilistic and repeated. `PAC_MASK` assumes top-byte-ignore behavior and a 48-bit VA default. Pipe setup has some cleanup gaps on early failure. Generic PAC is optional and skipped independently.

## Test Signals

Expected failures include missing SIGSEGV/SIGILL for corrupted return PAC, all-zero masked PAC output, keys colliding every attempt, unchanged signatures across exec, or changed signatures after a context switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/pac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/pac_corruptor.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/pac_corruptor.S

## Purpose

This assembly helper deliberately corrupts a return-address PAC to prove authentication faults are delivered.

## Important APIs, Types, and Functions

It exports `pac_corruptor`, executes `paciasp`, flips bit 53 of `lr`, executes `autiasp`, and returns.

## Control Flow and Data Flow

The function signs the current return address, mutates a PAC bit outside the top byte, authenticates with the IA key, and attempts to return. Correct hardware/kernel behavior raises SIGSEGV or SIGILL before normal return.

## State and Persistence Behavior

It mutates only the link register and uses current PAC key state. There is no memory or persistent state.

## Dependencies and Integration Points

It is linked into `pac` and called under a temporary signal handler in `TEST(corrupt_pac)`.

## Risks and Edge Cases

The chosen bit assumes default TBI and PAC placement. If architecture or VA-size assumptions change, the corruption bit may need review.

## Test Signals

The calling test passes only if SIGSEGV or SIGILL is observed; returning normally is a failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/pac_corruptor.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/Makefile

## Purpose

This Makefile builds each arm64 signal testcase as a standalone kselftest executable linked with the common signal test framework.

## Important APIs, Types, and Functions

It discovers `testcases/*.c` except common `testcases/testcases.c`, maps them to program names, sets `TEST_GEN_PROGS`, includes `../../lib.mk`, copies generated binaries to `$(OUTPUT)`, and defines common sources/headers for every testcase.

## Control Flow and Data Flow

For each testcase source, make compiles that file with `test_signals.c`, `test_signals_utils.c`, `testcases/testcases.c`, `signals.S`, and `sve_helpers.c`. Each testcase supplies its own `struct tdescr tde`, and the common wrapper supplies `main()`.

## State and Persistence Behavior

Only build products are created. Runtime state is owned by the generated test binaries.

## Dependencies and Integration Points

It depends on arm64 kernel headers, kselftest `lib.mk`, the common framework files, and all testcase descriptors under `testcases/`.

## Risks and Edge Cases

Secondary expansion is required so `$@.c` resolves per target. Adding a testcase without a `tde` descriptor will link-fail. Copying `$(PROGS)` to `$(OUTPUT)` assumes the local build path created binaries beside sources.

## Test Signals

Successful build creates one executable per testcase listed by `TEST_GEN_PROGS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/signals.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/signals.S

## Purpose

This assembly helper fabricates an `rt_sigreturn` using caller-provided sigframe bytes, optionally misaligning the stack, so negative signal-frame validation tests can ask the kernel to restore malformed frames.

## Important APIs, Types, and Functions

It exports `fake_sigreturn(sigframe, sigframe_size, misalign_bytes)`. It calls `printf()` and `memcpy()`, stores the final fake frame address into `current->token`, then invokes syscall `__NR_rt_sigreturn`.

## Control Flow and Data Flow

The routine saves frame pointer/link register, computes aligned stack space for the fake frame plus optional misalignment, copies the supplied frame to the new stack location, records the token for sanity checks, moves SP to the fake frame, and executes `svc #0` for `rt_sigreturn`. If the syscall unexpectedly returns, it loops forever to force timeout failure.

## State and Persistence Behavior

It mutates the thread stack and `current->token`. There is no persistent storage.

## Dependencies and Integration Points

It depends on the C global `current`, `struct tdescr` layout with `token` first, libc `printf`/`memcpy`, and the arm64 `rt_sigreturn` syscall number.

## Risks and Edge Cases

The helper assumes stack alignment rules, `current->token` offset zero, and that malformed frames fail before unsafe control flow resumes. Misuse can corrupt the stack permanently within the test process.

## Test Signals

Expected negative tests terminate with the configured SIGSEGV; returning to the infinite loop indicates the kernel accepted a frame it should reject.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/signals.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/sve_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/sve_helpers.c

## Purpose

This helper enumerates supported SVE or SME vector lengths for signal-context tests.

## Important APIs, Types, and Functions

It defines global `vls[SVE_VQ_MAX]` and `nvls`, and implements `sve_fill_vls(bool use_sme, int min_vls)`. It uses `PR_SVE_SET_VL` or `PR_SME_SET_VL` and masks with the matching VL length mask.

## Control Flow and Data Flow

The function walks vector quads from `SVE_VQ_MAX` down to one, asks the kernel to set the VL, records the returned implemented VL, skips missing lengths, and stops if SME returns a larger VL than requested. It returns pass, fail, or skip based on the number of discovered VLs.

## State and Persistence Behavior

The global `vls` array and `nvls` persist for the testcase process. The current process SVE/SME VL is changed during enumeration.

## Dependencies and Integration Points

It depends on `asm/sigcontext.h`, `prctl()`, kselftest return codes, and is used by SVE/SME signal testcases.

## Risks and Edge Cases

`nvls` is not reset inside the function, so callers should invoke it once per process. SME VLs need not be consecutive or include the minimum, so the loop has special termination logic.

## Test Signals

Dependent tests skip when too few VLs are available, fail on PRCTL errors, and otherwise iterate `vls[0..nvls)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/sve_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/sve_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/sve_helpers.h

## Purpose

This header declares SVE/SME vector-length helper state and provides an inline reader for the SVCR system register.

## Important APIs, Types, and Functions

It defines `VLS_USE_SVE`, `VLS_USE_SME`, extern `vls`/`nvls`, declares `sve_fill_vls()`, and implements `get_svcr()` with an `mrs S3_3_C4_C2_2`.

## Control Flow and Data Flow

Testcases include this header to enumerate VLs and check that helper code has exited streaming/ZA state after grabbing a context.

## State and Persistence Behavior

The header owns no storage and exposes process-global vector-length arrays from `sve_helpers.c`.

## Dependencies and Integration Points

It integrates with SME/SVE signal tests and arm64 system-register access.

## Risks and Edge Cases

`get_svcr()` uses a raw sysreg encoding, so architectural renames or assembler support changes require review.

## Test Signals

SVE/SME context tests validate this header by checking expected vector lengths and zero SVCR after context capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/sve_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals.c

## Purpose

This is the common `main()` wrapper for all arm64 signal testcases. Each testcase links a global `struct tdescr tde`; this file runs setup, initialization, execution, cleanup, and result reporting around it.

## Important APIs, Types, and Functions

It defines `struct tdescr *current = &tde` and `main()`. It calls `gcs_set_state()`, `test_setup()`, `test_init()`, `test_run()`, `test_cleanup()`, and `test_result()`.

## Control Flow and Data Flow

At startup it enables GCS if hardware advertises it, prints the testcase name/description, runs framework setup and testcase initialization, triggers or directly runs the testcase, cleans up, reports the result, and exits with the kselftest result code.

## State and Persistence Behavior

`current` points at the testcase descriptor. Enabling GCS changes process shadow-stack state for the process lifetime; the program exits instead of returning to avoid GCS return complications.

## Dependencies and Integration Points

It depends on auxv HWCAPs, GCS PRCTL wrapper from `test_signals_utils.h`, and the descriptor supplied by each testcase.

## Risks and Edge Cases

If libc locked GCS state, enabling can fail and tests continue. Missing or malformed `tde` fields are asserted later in setup. Returning from `main()` is intentionally avoided.

## Test Signals

Every testcase executable starts here; pass/fail/skip behavior is centralized in `test_result()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals.h

## Purpose

This header defines the descriptor ABI used by the arm64 signal selftest framework and feature flags used to gate testcases.

## Important APIs, Types, and Functions

It defines feature bits and masks for SSBS, SVE, SME, SME FA64, SME2, and GCS. `struct tdescr` contains identity, feature requirements, signal expectations, timeout, saved/live contexts, private data, and callback hooks for setup/init/cleanup/trigger/run/result checking. It declares external `tde`.

## Control Flow and Data Flow

Testcase source files initialize `tde`. The common wrapper and utilities read that descriptor to install handlers, check features, trigger signals, call the testcase's run callback, and decide pass/fail/skip.

## State and Persistence Behavior

The descriptor is mutable runtime state: the framework fills feature support, initialization status, live context pointers, pass/result flags, and token sanity fields.

## Dependencies and Integration Points

It depends on arm64 ptrace/hwcap headers, libc signal/ucontext types, and is included by all signal framework and testcase files.

## Risks and Edge Cases

`token` must remain the first field because `signals.S` writes it by offset. Callback contracts are implicit: `run` is mandatory, some signal expectations require `sig_trig` to have fired, and `sanity_disabled` weakens fake-sigreturn safety checks.

## Test Signals

Build failures catch descriptor signature drift. Runtime assertions in `test_setup()` catch missing mandatory fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals_utils.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals_utils.c

## Purpose

This file implements the arm64 signal selftest framework: feature probing, default signal handlers, live `ucontext_t` capture, trigger routing, timeout handling, and default result reporting.

## Important APIs, Types, and Functions

Important internal helpers are `feats_to_string()`, `unblock_signal()`, `default_result()`, `handle_signal_unsupported()`, `handle_signal_trigger()`, `handle_signal_ok()`, `handle_signal_copyctx()`, `default_handler()`, `default_setup()`, and `default_trigger()`. Exported functions are `test_init()`, `test_setup()`, `test_run()`, `test_result()`, and `test_cleanup()`.

## Control Flow and Data Flow

`default_setup()` installs one SA_SIGINFO handler for most regular and RT signals, unblocks expected signals, and arms an alarm. `test_init()` reads auxv feature bits, handles required/incompatible features, runs testcase init, and marks initialization. The default handler dispatches unsupported-feature signals, trigger signals, expected success signals, and `SIGTRAP` copy-context service signals. Copy-context handling validates the kernel-provided sigframe, copies ordinary and extra context data into testcase storage, and adjusts PC past the breakpoint.

## State and Persistence Behavior

It mutates `current` descriptor fields including `triggered`, `pass`, `result`, `feats_supported`, `live_uc`, `live_uc_valid`, and `minsigstksz`. It installs process-wide signal handlers and alarms.

## Dependencies and Integration Points

It integrates with `testcases/testcases.c` validation, `fake_sigreturn()` assembly, auxv HWCAPs, arm64 signal frame layout, and kselftest result codes.

## Risks and Edge Cases

The SIGTRAP context capture intentionally uses inline `brk #666` and must avoid compiler/libc behavior incompatible with SME streaming mode. The handler copies extra contexts only after validation and fixes extra-context sizes for local use. Signal-wide handlers can turn unrelated faults into test failures, which is intended but makes diagnostics dependent on descriptor setup.

## Test Signals

Framework success is visible as descriptors receiving correct skip/pass/fail outcomes, `ASSERT_GOOD_CONTEXT()` validations succeeding, timeouts failing cleanly, and fake-sigreturn tests seeing expected SIGSEGV.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals_utils.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals_utils.h

## Purpose

This header declares the signal framework entry points and provides inline helpers for GCS state control, GCS pointer reads, feature checks, live context capture, and `fake_sigreturn()`.

## Important APIs, Types, and Functions

It declares `test_init()`, `test_setup()`, `test_cleanup()`, `test_run()`, and `test_result()`. It defines `gcs_set_state()` as a raw `prctl` syscall wrapper with zeroed unused args, `get_gcspr_el0()`, `feats_ok()`, and `get_current_context()`.

## Control Flow and Data Flow

`get_current_context()` prepares destination storage, points the descriptor at it, triggers `SIGTRAP` with `brk #666`, waits for the signal handler to copy the kernel-provided context, exits SME streaming/ZA state with `SMSTOP` if needed, and detects accidental returns into a previously restored context.

## State and Persistence Behavior

It mutates descriptor live-context fields and uses a static `seen_already` flag inside `get_current_context()` to detect unexpected successful sigreturn reuse. Raw GCS and SME instructions mutate process architectural state.

## Dependencies and Integration Points

It depends on `testcases.h` validation macros, arm64 syscall numbers, GCS PRCTL constants, inline assembly, and the default signal handler in `test_signals_utils.c`.

## Risks and Edge Cases

The context capture path deliberately avoids normal syscalls for signal delivery because they may discard SVE state. Destination size must be large enough for extra contexts. The raw GCS syscall wrapper is used because libc wrappers may not expose the newest ABI.

## Test Signals

Successful context capture returns true with `td->live_uc_valid` set; malformed contexts abort through validation diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_bad_magic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_bad_magic.c

## Purpose

This testcase builds a fake sigframe containing `KSFT_BAD_MAGIC` and expects kernel sigreturn restore to reject the unknown record with SIGSEGV.

## Important APIs, Types, and Functions

The key implementation is `fake_sigreturn_bad_magic_run()` obtains a real context, finds room for a bad header plus terminator, writes the bad magic, asserts local validation fails, and calls `fake_sigreturn()`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_bad_magic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_bad_size.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_bad_size.c

## Purpose

This testcase creates an oversized `ESR_MAGIC` record that overruns the reserved area and expects SIGSEGV on restore.

## Important APIs, Types, and Functions

The key implementation is `fake_sigreturn_bad_size_run()` first constructs a good ESR record, then inflates its 16-byte-aligned size beyond remaining reserved space. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_bad_size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_bad_size_for_magic0.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_bad_size_for_magic0.c

## Purpose

This testcase uses a terminator record with nonzero size and expects the kernel to reject it.

## Important APIs, Types, and Functions

The key implementation is `fake_sigreturn_bad_size_for_magic0_run()` writes magic zero with `HDR_SZ` size before invoking fake sigreturn. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_bad_size_for_magic0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_duplicated_fpsimd.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_duplicated_fpsimd.c

## Purpose

This testcase adds a second `FPSIMD_MAGIC` record to a real signal frame and expects SIGSEGV.

## Important APIs, Types, and Functions

The key implementation is `fake_sigreturn_duplicated_fpsimd_run()` appends a spurious `fpsimd_context` and terminator. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_duplicated_fpsimd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_misaligned_sp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_misaligned_sp.c

## Purpose

This testcase places an otherwise real sigframe at a deliberately misaligned SP and expects SIGSEGV.

## Important APIs, Types, and Functions

The key implementation is `fake_sigreturn_misaligned_run()` passes misalignment of three bytes to `fake_sigreturn()`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_misaligned_sp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_missing_fpsimd.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_missing_fpsimd.c

## Purpose

This testcase removes the mandatory FPSIMD record from a copied signal frame and expects SIGSEGV.

## Important APIs, Types, and Functions

The key implementation is `fake_sigreturn_missing_fpsimd_run()` finds `FPSIMD_MAGIC`, overwrites it with a terminator, and calls fake sigreturn. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_missing_fpsimd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_sme_change_vl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_sme_change_vl.c

## Purpose

This testcase attempts to change the streaming SVE/SME vector length in a ZA signal context and expects SIGSEGV.

## Important APIs, Types, and Functions

The key implementation is `sme_get_vls()` requires at least two SME VLs, and `fake_sigreturn_ssve_change_vl()` edits `za_context.vl` from the captured minimum toward the maximum. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_sme_change_vl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_sve_change_vl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_sve_change_vl.c

## Purpose

This testcase attempts to change SVE vector length in a signal context and expects SIGSEGV.

## Important APIs, Types, and Functions

The key implementation is `sve_get_vls()` requires at least two SVE VLs, and `fake_sigreturn_sve_change_vl()` edits `sve_context.vl` in a bare SVE record. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SVE rows skip when SVE support or enough vector lengths are unavailable.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fake_sigreturn_sve_change_vl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fpmr_siginfo.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fpmr_siginfo.c

## Purpose

This testcase checks whether `FPMR_MAGIC` appears in signal frames exactly when `HWCAP2_FPMR` is present and preserves the FPMR value.

## Important APIs, Types, and Functions

The key implementation is `fpmr_present()` reads FPMR via raw sysreg encoding, captures a context, finds `struct fpmr_context`, and compares presence/value. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/fpmr_siginfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/gcs_exception_fault.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/gcs_exception_fault.c

## Purpose

This testcase verifies an invalid Guarded Control Stack operation raises SIGSEGV with `SEGV_CPERR`.

## Important APIs, Types, and Functions

The key implementation is `gcs_op_fault_trigger()` executes `gcsss1()` below current GCSPR, and the signal handler validates the delivered context. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. GCS rows require `FEAT_GCS`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/gcs_exception_fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/gcs_frame.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/gcs_frame.c

## Purpose

This testcase validates the GCS signal-frame record, including enabled-feature bits and saved GCSPR.

## Important APIs, Types, and Functions

The key implementation is `gcs_regs()` reads shadow-stack status, predicts GCSPR after signal token placement, captures a context, locates `GCS_MAGIC`, and compares fields. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. GCS rows require `FEAT_GCS`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/gcs_frame.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/gcs_prot_none_fault.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/gcs_prot_none_fault.c

## Purpose

This testcase checks that `mprotect(PROT_NONE)` on a mapped shadow stack prevents later reads and causes SIGSEGV.

## Important APIs, Types, and Functions

The key implementation is `alloc_gcs()` uses `map_shadow_stack`; the trigger reads before and after `mprotect()` and tracks `post_mprotect`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. GCS rows require `FEAT_GCS`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/gcs_prot_none_fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/gcs_write_fault.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/gcs_write_fault.c

## Purpose

This testcase checks that ordinary writes to a GCS mapping fault.

## Important APIs, Types, and Functions

The key implementation is `alloc_gcs()` maps a shadow stack page and `gcs_write_fault_trigger()` writes through a normal pointer. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. GCS rows require `FEAT_GCS`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/gcs_write_fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_compat_toggle.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_compat_toggle.c

## Purpose

This testcase toggles `PSR_MODE32_BIT` inside a signal ucontext and expects sigreturn validation to reject it.

## Important APIs, Types, and Functions

The key implementation is `mangle_invalid_pstate_run()` validates the incoming context, flips the compat-state bit, and returns to sigreturn. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_compat_toggle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_daif_bits.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_daif_bits.c

## Purpose

This testcase sets illegal DAIF bits in `uc_mcontext.pstate` and expects SIGSEGV on sigreturn.

## Important APIs, Types, and Functions

The key implementation is `mangle_invalid_pstate_run()` ORs in `PSR_D_BIT`, `PSR_A_BIT`, `PSR_I_BIT`, and `PSR_F_BIT`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_daif_bits.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el1h.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el1h.c

## Purpose

This testcase instantiates the invalid PSTATE mode template for EL1h and expects SIGSEGV on sigreturn.

## Important APIs, Types, and Functions

The key implementation is the file includes `mangle_pstate_invalid_mode_template.h` and expands `DEFINE_TESTCASE_MANGLE_PSTATE_INVALID_MODE(1h)`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el1h.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el1t.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el1t.c

## Purpose

This testcase instantiates the invalid PSTATE mode template for EL1t and expects SIGSEGV on sigreturn.

## Important APIs, Types, and Functions

The key implementation is the file includes `mangle_pstate_invalid_mode_template.h` and expands `DEFINE_TESTCASE_MANGLE_PSTATE_INVALID_MODE(1t)`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el1t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el2h.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el2h.c

## Purpose

This testcase instantiates the invalid PSTATE mode template for EL2h and expects SIGSEGV on sigreturn.

## Important APIs, Types, and Functions

The key implementation is the file includes `mangle_pstate_invalid_mode_template.h` and expands `DEFINE_TESTCASE_MANGLE_PSTATE_INVALID_MODE(2h)`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el2h.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el2t.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el2t.c

## Purpose

This testcase instantiates the invalid PSTATE mode template for EL2t and expects SIGSEGV on sigreturn.

## Important APIs, Types, and Functions

The key implementation is the file includes `mangle_pstate_invalid_mode_template.h` and expands `DEFINE_TESTCASE_MANGLE_PSTATE_INVALID_MODE(2t)`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el2t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el3h.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el3h.c

## Purpose

This testcase instantiates the invalid PSTATE mode template for EL3h and expects SIGSEGV on sigreturn.

## Important APIs, Types, and Functions

The key implementation is the file includes `mangle_pstate_invalid_mode_template.h` and expands `DEFINE_TESTCASE_MANGLE_PSTATE_INVALID_MODE(3h)`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el3h.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el3t.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el3t.c

## Purpose

This testcase instantiates the invalid PSTATE mode template for EL3t and expects SIGSEGV on sigreturn.

## Important APIs, Types, and Functions

The key implementation is the file includes `mangle_pstate_invalid_mode_template.h` and expands `DEFINE_TESTCASE_MANGLE_PSTATE_INVALID_MODE(3t)`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_el3t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_template.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_template.h

## Purpose

This testcase provides a macro that generates invalid exception-level PSTATE mangle tests.

## Important APIs, Types, and Functions

The key implementation is `DEFINE_TESTCASE_MANGLE_PSTATE_INVALID_MODE()` creates a run function and descriptor that set `PSR_MODE_EL*` values before sigreturn. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/mangle_pstate_invalid_mode_template.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/poe_siginfo.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/poe_siginfo.c

## Purpose

This testcase checks whether `POE_MAGIC` and POR_EL0 state appear in signal frames exactly when `HWCAP2_POE` is present.

## Important APIs, Types, and Functions

The key implementation is `poe_present()` reads POR_EL0, captures a context, locates `struct poe_context`, and compares presence/value. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/poe_siginfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sme_trap_no_sm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sme_trap_no_sm.c

## Purpose

This testcase verifies an SME streaming-mode instruction traps when streaming mode is not enabled.

## Important APIs, Types, and Functions

The key implementation is `sme_trap_no_sm_trigger()` executes `SMSTART ZA` followed by an SME instruction expected to SIGILL. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sme_trap_no_sm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sme_trap_non_streaming.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sme_trap_non_streaming.c

## Purpose

This testcase verifies an instruction illegal in streaming mode traps while SME streaming mode is active on systems without FA64.

## Important APIs, Types, and Functions

The key implementation is `sme_trap_non_streaming_trigger()` enters streaming mode, executes `cnt`, then stops ZA for handler safety. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sme_trap_non_streaming.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sme_trap_za.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sme_trap_za.c

## Purpose

This testcase verifies ZA access without enabling ZA raises SIGILL.

## Important APIs, Types, and Functions

The key implementation is `sme_trap_za_trigger()` executes `ZERO ZA`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sme_trap_za.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sme_vl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sme_vl.c

## Purpose

This testcase checks that the SME vector length recorded in `ZA_MAGIC` matches `PR_SME_GET_VL`.

## Important APIs, Types, and Functions

The key implementation is `get_sme_vl()` saves current VL and `sme_vl()` captures a context and compares `za_context.vl`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sme_vl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/ssve_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/ssve_regs.c

## Purpose

This testcase validates streaming SVE signal records for every discovered SME VL.

## Important APIs, Types, and Functions

The key implementation is `setup_ssve_regs()` enters streaming mode and `do_one_sme_vl()` checks `SVE_MAGIC`, VL, `SVE_SIG_FLAG_SM`, record size, and post-capture SVCR. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent. SVE rows skip when SVE support or enough vector lengths are unavailable.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/ssve_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/ssve_za_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/ssve_za_regs.c

## Purpose

This testcase validates simultaneous streaming SVE and ZA signal records.

## Important APIs, Types, and Functions

The key implementation is `setup_regs()` enables SM and ZA, then `do_one_sme_vl()` checks SVE and ZA records, VLs, sizes, SM flag, and zero ZA data. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent. SVE rows skip when SVE support or enough vector lengths are unavailable.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/ssve_za_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sve_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sve_regs.c

## Purpose

This testcase validates SVE register signal records for every supported SVE VL.

## Important APIs, Types, and Functions

The key implementation is `setup_sve_regs()` executes RDVL to make SVE state live and `do_one_sve_vl()` checks `SVE_MAGIC`, size, and VL. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SVE rows skip when SVE support or enough vector lengths are unavailable.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sve_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sve_vl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sve_vl.c

## Purpose

This testcase checks that the SVE vector length in the signal frame matches `PR_SVE_GET_VL`.

## Important APIs, Types, and Functions

The key implementation is `get_sve_vl()` saves current VL and `sve_vl()` compares it with `sve_context.vl`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SVE rows skip when SVE support or enough vector lengths are unavailable.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/sve_vl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/testcases.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/testcases.c

## Purpose

This file validates and manipulates arm64 signal-frame reserved records for the signal selftests. It is the central parser used by both good-context assertions and fake bad-context construction.

## Important APIs, Types, and Functions

Important validators are `validate_extra_context()`, `validate_sve_context()`, `validate_za_context()`, `validate_zt_context()`, and `validate_reserved()`. `get_starting_head()` finds or reclaims room in a sigframe reserved area for negative tests.

## Control Flow and Data Flow

`validate_reserved()` walks `_aarch64_ctx` records until a terminator, checks alignment, duplicates, record sizes, optional extra-context data, SVE/ZA/ZT VL validity, mandatory FPSIMD presence, and ZT-without-ZA invalidity. Unknown magic values are reported as possible test-suite staleness rather than hard ABI knowledge.

## State and Persistence Behavior

No persistent state is kept. Validation uses local flags to track seen context record types and returns an error string through the caller.

## Dependencies and Integration Points

It depends on `asm/sigcontext.h` record definitions and is called by `ASSERT_GOOD_CONTEXT()`, `ASSERT_BAD_CONTEXT()`, and live-context capture.

## Risks and Edge Cases

The parser must evolve with new signal context magic records. Bad size or missing terminator handling is security-sensitive because negative tests mirror kernel restore parsing.

## Test Signals

Good kernel-generated contexts validate successfully; handcrafted bad fake-sigreturn frames fail validation before being passed to the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/testcases.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/testcases.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/testcases.h

## Purpose

This header defines common signal-frame test helpers, macros, context flags, and the fake sigframe structure used by arm64 signal testcases.

## Important APIs, Types, and Functions

It defines context flags (`FPSIMD_CTX`, `SVE_CTX`, `ZA_CTX`, `EXTRA_CTX`, `ZT_CTX`, `FPMR_CTX`, `GCS_CTX`), `KSFT_BAD_MAGIC`, reserved-area access macros, `ASSERT_BAD_CONTEXT()`, `ASSERT_GOOD_CONTEXT()`, `GET_RESV_NEXT_HEAD()`, `struct fake_sigframe`, `get_header()`, `get_terminator()`, `write_terminator_record()`, and `get_starting_head()`.

## Control Flow and Data Flow

Testcases use macros to locate `uc_mcontext.__reserved`, find or write context records, validate expected-good or expected-bad frames, and pass fake frames to `fake_sigreturn()`.

## State and Persistence Behavior

The header owns no state. Inline helpers operate on caller-provided `ucontext_t` or fake sigframe buffers.

## Dependencies and Integration Points

It depends on `asm/sigcontext.h`, libc signal/ucontext types, and the validator implementation in `testcases.c`.

## Risks and Edge Cases

`get_header()` trusts record sizes while walking, so callers use it on buffers already bounded by a reserved-size argument. `ASSERT_BAD_CONTEXT()` aborts if a supposedly bad context validates as good.

## Test Signals

All signal testcase builds and context assertions validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/testcases.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/tpidr2_restore.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/tpidr2_restore.c

## Purpose

This testcase verifies TPIDR2 is restored from the signal frame after a handler mutates the live register.

## Important APIs, Types, and Functions

The key implementation is `save_tpidr2()` records initial TPIDR2, `modify_tpidr2()` increments it in the handler, and `check_tpidr2()` compares post-sigreturn state. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/tpidr2_restore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/tpidr2_siginfo.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/tpidr2_siginfo.c

## Purpose

This testcase checks whether `TPIDR2_MAGIC` appears in signal frames exactly when SME is present and preserves the captured TPIDR2 value.

## Important APIs, Types, and Functions

The key implementation is `tpidr2_present()` reads TPIDR2, captures a context, locates `struct tpidr2_context`, and compares presence/value. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/tpidr2_siginfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/za_no_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/za_no_regs.c

## Purpose

This testcase checks that a ZA context exists with no register payload when ZA is disabled.

## Important APIs, Types, and Functions

The key implementation is `do_one_sme_vl()` sets each SME VL, captures a context, locates `ZA_MAGIC`, checks VL, and expects size `ZA_SIG_REGS_OFFSET`. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/za_no_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/za_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/za_regs.c

## Purpose

This testcase checks that an enabled ZA context includes register payload of the correct size and zero contents.

## Important APIs, Types, and Functions

The key implementation is `setup_za_regs()` starts ZA and `do_one_sme_vl()` validates `ZA_MAGIC`, VL, size, data, and post-capture SVCR. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/za_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/zt_no_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/zt_no_regs.c

## Purpose

This testcase verifies no ZT context is present when ZA is disabled on SME2 systems.

## Important APIs, Types, and Functions

The key implementation is `zt_no_regs_run()` captures a context and fails if `ZT_MAGIC` is found. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/zt_no_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/zt_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/zt_regs.c

## Purpose

This testcase verifies ZT context is present with register data when ZA is enabled on SME2 systems.

## Important APIs, Types, and Functions

The key implementation is `zt_regs_run()` enables ZA, captures context, validates `zt_context.nregs`, size, and zero register payload. The testcase exports `struct tdescr tde` with its name, description, expected signals, timeout, feature requirements, and callback pointers. Feature requirements and signal expectations are encoded in `tde`. SME/SME2 rows skip when required HWCAP bits are absent.

## Control Flow and Data Flow

The common framework installs handlers, checks feature requirements, then either invokes the run callback directly or calls the trigger callback. The testcase captures or mutates `ucontext_t`/sigframe state, returns to the framework, and relies on either normal pass marking or an expected fatal signal to complete.

## State and Persistence Behavior

State is process-local: descriptor flags, captured `ucontext_t` buffers, temporary fake sigframe storage, architecture registers, or transient shadow-stack mappings depending on the case. No persistent files are written.

## Dependencies and Integration Points

It links with `test_signals.c`, `test_signals_utils.c`, `signals.S`, and `testcases/testcases.c`, and uses `struct tdescr tde` as the integration point. It also depends on arm64 signal-frame ABI records from `asm/sigcontext.h`, raw sysreg or instruction encodings where used, and kselftest result handling.

## Risks and Edge Cases

The test is intentionally ABI-sensitive. Kernel changes to signal-frame record ordering, sizes, optional feature exposure, PSTATE validation, or new magic records can require updates. Negative fake-sigreturn tests must ensure locally malformed frames are malformed for the same reason the kernel is expected to reject.

## Test Signals

Passing behavior is either `td->pass` being set after context validation or delivery of the configured `sig_ok` signal. Unexpected signal codes, missing context records, wrong register values, or survival of an invalid sigreturn are failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/zt_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/tags/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/tags/Makefile

## Purpose

This Makefile builds the arm64 tagged-address syscall smoke test `tags_test`.

## Important APIs, Types, and Functions

It appends `$(KHDR_INCLUDES)` to `CFLAGS`, declares `TEST_GEN_PROGS := tags_test`, and includes `../../lib.mk`.

## Control Flow and Data Flow

Kselftest make infrastructure compiles `tags_test.c` into the generated program list and handles install/clean behavior.

## State and Persistence Behavior

Only build outputs in `$(OUTPUT)` are produced.

## Dependencies and Integration Points

It depends on kernel UAPI headers for `PR_SET_TAGGED_ADDR_CTRL` and kselftest `lib.mk`.

## Risks and Edge Cases

The file is intentionally minimal; missing kernel headers or unsupported target architecture will surface at compile time.

## Test Signals

A successful build creates the `tags_test` kselftest binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/tags/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/tags/tags_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/tags/tags_test.c

## Purpose

This small arm64 selftest verifies that a syscall can accept a tagged user pointer after enabling the tagged-address ABI.

## Important APIs, Types, and Functions

Macros `SHIFT_TAG()` and `SET_TAG()` manipulate top-byte tags. `main()` uses `prctl(PR_SET_TAGGED_ADDR_CTRL, PR_TAGGED_ADDR_ENABLE)`, allocates `struct utsname`, tags the pointer when enabled, calls `uname()`, and reports through kselftest.

## Control Flow and Data Flow

The test enables tagged addresses if possible, chooses tag `0x42` only when the enable call succeeds, overwrites the pointer's top byte, calls `uname()` with the tagged pointer, and frees the original allocation through the tagged pointer value.

## State and Persistence Behavior

Only process-local tagged-address control and heap memory are used. No files are created.

## Dependencies and Integration Points

It exercises the generic syscall user-pointer path and arm64 top-byte-ignore/tagged-address ABI without requiring full MTE memory tagging.

## Risks and Edge Cases

If tagged-address enable fails, the test uses tag zero and still verifies normal syscall behavior. Freeing a tagged pointer relies on libc/kernel ABI tolerating the top-byte value when enabled.

## Test Signals

The single planned kselftest row passes when `uname()` succeeds with the selected pointer tag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/tags/tags_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/Makefile

## Purpose

This large Makefile builds the BPF selftest suite, BPF test runners, helper libraries, generated skeletons, kernel modules, bpftool, benchmark binary, and install/clean targets.

## Important APIs, Types, and Functions

Key variables include `TEST_GEN_PROGS`, `TEST_GEN_PROGS_EXTENDED`, `TEST_GEN_FILES`, `TEST_KMODS`, `BPFOBJ`, `BPFTOOL`, `VMLINUX_BTF`, `BPF_CFLAGS`, and the `DEFINE_TEST_RUNNER`/`DEFINE_TEST_RUNNER_RULES` make macros. Custom rules generate `vmlinux.h`, compile BPF objects with clang or bpf-gcc, generate skeleton/subskeleton/light-skeleton headers, build `test_progs` flavors, build `test_maps`, `test_verifier`, XDP/XSK utilities, and link `bench`.

## Control Flow and Data Flow

Make first resolves tool paths, feature flags, CFLAGS/LDFLAGS, optional LLVM/libpcap/libcrypto support, and output directories. It builds libbpf and host/cross bpftool, dumps BTF into `vmlinux.h`, compiles BPF programs from `progs/`, generates skeleton headers with bpftool, compiles C test objects, links runners, and copies/install artifacts through kselftest rules. The benchmark target links `bench.o`, helper objects, and every `benchs/bench_*.o`.

## State and Persistence Behavior

Build state lives in `$(OUTPUT)`, scratch tool directories, generated headers, `.d` dependencies, BPF objects, skeleton headers, signed light skeleton material, and copied install subdirectories. `EXTRA_CLEAN` removes these generated artifacts.

## Dependencies and Integration Points

The Makefile integrates with kernel tools build includes, kselftest `lib.mk`, libbpf, bpftool, clang, optional bpf-gcc, LLVM disassembler support, libelf/zlib/pthread/rt, libpcap, cgroup helpers, kernel BTF, and test kernel modules.

## Risks and Edge Cases

Feature detection is sensitive to cross-build output paths, `VMLINUX_BTF` availability, clang target include paths, endian selection, and make version behavior. Skeleton generation intentionally relinks multiple times and diffs outputs to catch non-determinism. Static linking is filtered for shared urandom helper builds. Missing BTF is a hard error.

## Test Signals

Successful `make -C tools/testing/selftests/bpf` builds test runners, BPF objects, skeleton headers, bpftool, modules, docs unless skipped, and `bench`. Failures often identify missing BTF, clang/bpftool/libbpf breakage, skeleton generation drift, or helper library link issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/autoconf_helper.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/autoconf_helper.h

## Purpose

This header supplies a small compatibility bridge for generated kernel configuration. If `HAVE_GENHDR` is set it includes generated `autoconf.h`; otherwise it defines `CONFIG_HAVE_EFFICIENT_UNALIGNED_ACCESS` for common architectures.

## Important APIs, Types, and Functions

The only exported behavior is conditional preprocessing around `HAVE_GENHDR` and fallback architecture checks for x86, s390x, and aarch64.

## Control Flow and Data Flow

There is no runtime flow. Preprocessor state determines whether tests see kernel config definitions from the build tree or the fallback unaligned-access capability.

## State and Persistence Behavior

No runtime state exists.

## Dependencies and Integration Points

It is included by BPF selftest sources needing config-sensitive behavior while still being buildable outside a full generated-header environment.

## Risks and Edge Cases

The fallback covers only selected architectures and only one config symbol. Architectures with efficient unaligned access but not listed may compile conservative paths.

## Test Signals

Compilation both with and without `include/generated/autoconf.h` validates this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/autoconf_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bench.c

## Purpose

`bench.c` is the generic userspace driver for BPF benchmarks. It parses global and benchmark-specific options, chooses a registered `struct bench`, starts producer/consumer threads, samples once per second, and prints progress/final throughput summaries.

## Important APIs, Types, and Functions

Global state is `struct env env`, `const struct bench *bench`, and internal `state`. Core functions include `setup_libbpf()`, reporting helpers for hits/drops, operations, false hits, local storage, and grace-period stats, command-line parsers, `setup_timer()`, `set_thread_affinity()`, `next_cpu()`, `find_benchmark()`, `setup_benchmark()`, `collect_measurements()`, and `main()`. It declares every benchmark object linked from `benchs/`.

## Control Flow and Data Flow

`main()` discovers CPU count, parses global options, lists benchmarks if requested, selects a benchmark by name, reparses with that benchmark's argp, validates and sets it up, creates requested consumer and producer threads, starts an interval timer, then waits on a condition variable. SIGALRM drives `collect_measurements()`, which asks the active benchmark to fill `bench_res`, prints progress, and signals completion after warmup plus duration. Final reporting skips warmup samples.

## State and Persistence Behavior

Runtime state includes allocated arrays for thread IDs and per-second results, CPU affinity cursors, benchmark-specific global state in linked modules, and process signal/timer state. It writes no files.

## Dependencies and Integration Points

It depends on pthreads, argp, libbpf strict mode and print callbacks, `testing_helpers`, CPU-list parsing, kselftest BPF benchmark modules, and POSIX interval timers.

## Risks and Edge Cases

The timer handler calls benchmark measurement and printing paths from signal context, which is pragmatic for this tool but not async-signal-safe in the strict POSIX sense. Producers run infinite loops and are not joined. CPU-list validation fails late if too few CPUs are provided. Final latency calculations assume nonzero throughput.

## Test Signals

`bench -l` should list all registered benchmarks. Running a simple benchmark such as `count-local` should produce per-second progress and a final summary; BPF-backed benchmarks additionally validate skeleton load/attach and helper reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bench.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bench.h

## Purpose

This header defines the common ABI for BPF benchmark modules and the runner.

## Important APIs, Types, and Functions

Important types are `struct cpu_set`, `struct env`, `struct basic_stats`, `struct bench_res`, `struct bench`, and cacheline-aligned `struct counter`. It declares global `env` and `bench`, libbpf setup, shared reporting functions, grace-period statistics helpers, and relaxed atomic helpers `atomic_inc()`, `atomic_add()`, and `atomic_swap()`.

## Control Flow and Data Flow

Benchmark modules populate a `const struct bench` with callbacks. Producers update counters or trigger BPF programs; the runner calls `measure()` once per interval to fill `bench_res`; report helpers consume those deltas.

## State and Persistence Behavior

The header defines no storage except through external declarations. Atomic helpers operate on caller-owned counters and intentionally use relaxed ordering for throughput measurement.

## Dependencies and Integration Points

It integrates libbpf, BPF syscall wrappers, math/time/syscall headers, and all `benchs/` modules.

## Risks and Edge Cases

`bench_res` is a shared catch-all structure, so fields have benchmark-specific meanings. Relaxed atomics are correct for approximate benchmark counters but not for synchronization. The aligned `counter` type helps avoid false sharing only when arrays are allocated naturally.

## Test Signals

Successful compilation of all benchmark modules and sensible output from shared reporting functions validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bench.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bloom_filter_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bloom_filter_map.c

## Purpose

This benchmark module measures BPF bloom filter map lookup/update, bloom-assisted hashmap lookup, plain hashmap lookup, and false-positive behavior.

## Important APIs, Types, and Functions

State lives in `ctx` with skeleton, map FDs, condition variable, and population cursor. CLI args set `nr_entries`, `nr_hash_funcs`, and `value_size`. Important functions are `validate()`, `producer()`, `map_prepare_thread()`, `populate_maps()`, `check_args()`, `setup_skeleton()`, per-benchmark setup functions, and `measure()`. It exports five `struct bench` instances.

## Control Flow and Data Flow

Setup opens the skeleton, resizes maps and key/value sizes, sets bloom hash function count, loads BPF, populates maps with random values from concurrent threads, fills random lookup data, and attaches the selected BPF program. Producers repeatedly call `getpgid` to trigger attached programs. `measure()` reads per-CPU BSS stats and reports deltas for hits, drops, and false hits.

## State and Persistence Behavior

Map contents and per-CPU counters live for the benchmark process. `ctx.next_map_idx` coordinates concurrent map population; `map_done` only signals first completing thread, so all workers are expected to finish by exhausting the shared index quickly enough for this setup pattern.

## Dependencies and Integration Points

It depends on `bloom_filter_bench.skel.h`, libbpf map resizing APIs, `bpf_map_update_elem()`, `getrandom`, syscall-triggered BPF attachment, and the runner's reporting helpers.

## Risks and Edge Cases

Small `value_size` can make requested unique entries impossible, so `check_args()` rejects it. Hashmap population retries on `EEXIST`. The condition variable does not join all population threads, making `map_prepare_err` and map completeness sensitive to thread timing. False-positive percentages depend on random data and bloom parameters.

## Test Signals

Useful signals are stable hit/drop rates for lookup/update benches, false-positive percentages for `bloom-false-positive`, and setup failures for invalid map sizing, random generation, or skeleton attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bloom_filter_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_crypto.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_crypto.c

## Purpose

This benchmark measures BPF crypto helper throughput for encryption and decryption using a selected kernel crypto cipher and buffer length.

## Important APIs, Types, and Functions

CLI options are `--crypto-len` and `--crypto-cipher`. State lives in `input` and `ctx` with `crypto_bench` skeleton and selected program FD. Functions include `crypto_parse_arg()`, `crypto_validate()`, `crypto_setup()`, `crypto_encrypt_setup()`, `crypto_decrypt_setup()`, `crypto_measure()`, and `crypto_producer()`.

## Control Flow and Data Flow

Setup opens the skeleton, writes cipher/key/auth settings into BSS, creates random-ish input, sets rodata length, loads the skeleton, and runs the BPF setup program once through `bpf_prog_test_run_opts()`. Producers repeatedly run the selected encrypt or decrypt program with `.repeat = 64`; measurement atomically drains the BSS hit counter.

## State and Persistence Behavior

The crypto transform setup and counters live in the BPF program/skeleton for the benchmark process. Input buffer memory persists for producers. No files are stored.

## Dependencies and Integration Points

It depends on `crypto_bench.skel.h`, libbpf, `bpf_prog_test_run_opts()`, kernel BPF crypto kfunc/helper availability, and the kernel crypto API implementation for the requested cipher.

## Risks and Edge Cases

Argument parsing references `ctx.skel->bss->dst` before setup has opened the skeleton; this relies on compile-time type information through the skeleton pointer expression but would be fragile if rewritten. Cipher names longer than `MAX_CIPHER_LEN` are rejected, but BSS copy uses a 128-byte destination. Unsupported crypto helpers or ciphers fail during setup.

## Test Signals

Expected output is hit throughput for `crypto-encrypt` and `crypto-decrypt`; setup failures identify unsupported ciphers, invalid lengths, BPF load failure, or setup-program status errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_hashmap_full_update.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_hashmap_full_update.c

## Purpose

This benchmark measures BPF hash map update behavior when the map is already full.

## Important APIs, Types, and Functions

The module uses `bpf_hashmap_full_update_bench.skel.h`, `MAX_LOOP_NUM`, `validate()`, `producer()`, `setup()`, and `hashmap_report_final()`. It exports `bench_bpf_hashmap_full_update`.

## Control Flow and Data Flow

Setup loads and attaches the skeleton, sets BSS `nr_loops`, fills every entry in `hash_map_bench`, and producers repeatedly trigger the attached BPF program through `getpgid`. Measurement is empty during the run; final reporting reads per-CPU BSS elapsed times and computes events per second from loop count over recorded time.

## State and Persistence Behavior

The full hash map and per-CPU timing arrays live in the BPF skeleton during the process. No persistent state is written.

## Dependencies and Integration Points

It integrates the benchmark runner, libbpf skeleton generation, BPF map update syscall wrapper, and the BPF program that records per-CPU timing.

## Risks and Edge Cases

The benchmark intentionally relies on a full map, so map prefill failures would distort results but are not individually checked. No progress is printed until final reporting. The per-CPU report skips CPUs with zero time.

## Test Signals

A successful final report prints `hash_map_full_perf` events per second for CPUs that executed the benchmark.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_hashmap_full_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_hashmap_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_hashmap_lookup.c

## Purpose

This module benchmarks BPF hash map lookup throughput across configurable key size, map flags, entry count, and loop count.

## Important APIs, Types, and Functions

CLI options control `key_size`, `map_flags`, `max_entries`, `nr_entries`, and `nr_loops`. Important helpers are `validate()`, `producer()`, `patch_key()`, `setup()`, `events_from_time()`, `compute_events()`, and `hashmap_report_final()`. It exports `bench_bpf_hashmap_lookup`.

## Control Flow and Data Flow

Setup configures map dimensions and flags before load, initializes a deterministic key template for keys larger than four bytes, loads the skeleton, fills `nr_entries` keys, and attaches the benchmark program. Producers trigger via `getpgid`. The BPF side stores timing samples per CPU; final reporting converts time samples to million lookups per second and prints mean/stddev.

## State and Persistence Behavior

Map contents, key template, and per-CPU timing samples are process-local skeleton state. There is no persistent storage.

## Dependencies and Integration Points

It depends on `bpf_hashmap_lookup.skel.h`, libbpf map mutators, endian-aware key patching, and the benchmark runner's quiet/affinity modes.

## Risks and Edge Cases

`nr_entries` must not exceed `max_entries`; `nr_loops` is capped by the kernel loop bound. `ctx.skel->bss->nr_loops` is integer-divided by entries, so total work can be lower than requested. `compute_events()` scans only 32 timing samples per CPU.

## Test Signals

Expected final output prints per-CPU lookup throughput, or a single numeric quiet result when affinity pins execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_hashmap_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_loop.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_loop.c

## Purpose

This benchmark measures overhead and throughput of the `bpf_loop` helper for a configurable number of loop iterations.

## Important APIs, Types, and Functions

It uses `bpf_loop_bench.skel.h`, CLI option `--nr_loops`, and functions `validate()`, `producer()`, `measure()`, and `setup()`. It exports `bench_bpf_loop`.

## Control Flow and Data Flow

Setup opens, loads, and attaches the BPF program, then writes `args.nr_loops` into BSS. Producers trigger the program with `getpgid`. Measurement drains the BSS `hits` counter each interval and uses generic ops reporting.

## State and Persistence Behavior

Only the skeleton's BSS loop count and hit counter persist during the process. No files are written.

## Dependencies and Integration Points

It depends on libbpf skeleton load/attach, syscall-triggered BPF execution, and the runner's operations reporting.

## Risks and Edge Cases

Argument parsing does not validate negative or excessive loop counts in userspace; invalid values rely on BPF program or verifier behavior. Consumers are unsupported.

## Test Signals

Successful runs print M ops/sec and latency for `bpf-loop`; setup failures indicate skeleton or attach problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_count.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_count.c

## Purpose

This module provides pure userspace counting baselines for the benchmark framework: one contended global counter and one per-producer local counter.

## Important APIs, Types, and Functions

`count_global_ctx` contains a single aligned counter. `count_local_ctx` contains an allocated array of counters. Producer and measurement functions are `count_global_producer()`, `count_global_measure()`, `count_local_setup()`, `count_local_producer()`, and `count_local_measure()`. It exports `bench_count_global` and `bench_count_local`.

## Control Flow and Data Flow

Producers spin forever incrementing either one shared counter or their own slot. Measurement swaps counters to zero and reports deltas through the generic hits/drops reporting path.

## State and Persistence Behavior

Counters are process memory only. Local counters are allocated once based on producer count and never freed because the process exits after the run.

## Dependencies and Integration Points

It depends only on `bench.h` relaxed atomic helpers and the runner's thread management/reporting.

## Risks and Edge Cases

The global baseline measures atomic contention as much as loop overhead. The local baseline depends on producer index matching array bounds. Producers never terminate.

## Test Signals

`count-local` should scale better with producers than `count-global`; both are useful smoke tests for the runner without requiring BPF support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_count.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_htab_mem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_htab_mem.c

## Purpose

This benchmark measures hash map memory behavior and operation rate under overwrite, batch add/delete, and synchronized add/delete-on-different-CPU use cases.

## Important APIs, Types, and Functions

It defines `struct htab_mem_use_case`, global `ctx`, CLI args `value_size`, `use_case`, and `preallocated`, and functions for argument parsing, validation, barrier setup/teardown, use-case lookup, skeleton setup, add/delete producer loops, memory cgroup file reading, measurement, progress, and final reporting. It exports `bench_htab_mem`.

## Control Flow and Data Flow

Setup chooses the use case, optionally creates per-pair pthread barriers, joins a memory cgroup, opens the skeleton, sets hash value size and max entries, toggles preallocation, enables selected BPF programs by name, loads and attaches. Producers either repeatedly trigger add/overwrite work or synchronize paired add/delete threads through barriers. Measurement drains BPF operation count and reads `memory.current`; final reporting also reads `memory.peak`.

## State and Persistence Behavior

State includes the BPF hash map, cgroup membership, barrier objects, BPF BSS counters, and memory cgroup accounting. Final reporting closes the cgroup FD and cleans up the cgroup environment.

## Dependencies and Integration Points

It depends on `htab_mem_bench.skel.h`, cgroup helper APIs, libbpf map mutators, pthread barriers, cgroup v2 memory files, and syscall triggers.

## Risks and Edge Cases

`add_del_on_diff_cpu` requires an even producer count. On cgroup v1 or missing memory files, memory reads become zero. Cleanup is mainly on setup failure or final reporting, so abnormal exits can leave transient cgroup state. The preallocation flag clears `BPF_F_NO_PREALLOC`, so semantics depend on skeleton defaults.

## Test Signals

Progress should show per-producer kops/sec and memory MiB. Final output reports mean/stddev memory and peak memory for the selected use case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_htab_mem.c -->
