<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/snprintf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/snprintf.c

Purpose: `snprintf.c` tests `bpf_snprintf()` formatting and verifier validation. Positive coverage checks numeric, IP, symbol, pointer, string, overflow, padding, no-argument, and no-buffer formats; negative coverage checks invalid format strings are rejected at load time.

Important APIs/types/functions: `test_snprintf_positive()` loads and attaches `test_snprintf.skel.h`, sets BSS `pid`, triggers the program, and compares BSS output buffers and return values. `load_single_snprintf()` injects a candidate format into `test_snprintf_single` rodata and attempts load. `test_snprintf_negative()` asserts valid and invalid load results. `test_snprintf()` creates two subtests.

Control flow: the positive subtest opens/loads, filters by PID, attaches, triggers with `usleep(1)`, and checks all expected strings/return lengths. Symbol and hashed pointer output use prefix/minimum comparisons where exact content is kernel/compiler dependent. The negative subtest repeatedly opens a single-format skeleton, copies up to ten bytes of the requested format into rodata, loads it, and asserts whether the verifier accepts or rejects it.

State and persistence: state is in skeleton rodata/BSS buffers and return values. There are no sockets, maps beyond skeleton globals, or persistent files.

Dependencies: requires `bpf_snprintf()` helper support, symbol formatting, BPF verifier format-string validation, tracepoint attachment used by the BPF object, and libbpf skeletons `test_snprintf` and `test_snprintf_single`.

Integration points: integrates helper runtime formatting behavior with verifier-time format validation and userspace skeleton BSS observation.

Risks: expected return values include C string terminators via `sizeof()`, so edits to expected constants must preserve the helper's return convention. Symbol output depends on compiler inlining and kernel symbol formatting; the test deliberately checks only a stable prefix/minimum. Pointer hashing changes across boots, so only a prefix and expected length are checked.

Test signals: positive subtest exact matches for stable formats, prefix/minimum matches for symbol/pointer formats, and negative subtest load acceptance/rejection for valid, unterminated, too-many-specifier, invalid-specifier, non-ASCII, and non-printable format strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/snprintf.c -->
