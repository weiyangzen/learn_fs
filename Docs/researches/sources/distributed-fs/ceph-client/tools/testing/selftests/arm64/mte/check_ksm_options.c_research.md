<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_ksm_options.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_ksm_options.c

Purpose: verifies that tagged MTE pages are not merged by Kernel Samepage Merging under MADV_MERGEABLE.

Important APIs and functions: `read_sysfs`, `write_sysfs`, `mte_ksm_setup`, `mte_ksm_restore`, `mte_ksm_scan`, and `check_madvise_options`.

Control flow: main performs MTE setup, reads page size, installs SIGBUS/SIGSEGV handlers, plans four tests, mutates KSM sysfs knobs to speed scanning, runs private/shared mmap checks under sync and async modes, restores KSM and MTE settings, and reports counts.

State and persistence: mutates `/sys/kernel/mm/ksm/*` values for merge behavior, scan timing, run state, max sharing, and pages-to-scan. Allocates tagged pages and calls `madvise(MADV_MERGEABLE)`.

Dependencies and integration: requires KSM sysfs, MTE utilities, permissions to write KSM knobs, and page scan progress.

Risks: `mte_ksm_setup` writes `max_page_sharing` using `ksm_sysfs[3]` before it is read from sysfs, likely setting it relative to zero rather than preserving original. The pass condition around `pages_shared`/`pages_sharing` is subtle and can be affected by unrelated KSM activity. Restoration happens only at normal end.

Test signals: four kselftest cases; diagnostics report missing KSM config, sysfs parse/write issues, or madvise failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_ksm_options.c -->
