# Research Group subset-b-009496

This grouped report covers Linux syzkaller report-parser fixtures under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/701 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/701

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/701`. It records expected title `KMSAN: uninit-value in btrfs_bin_search`; type `KMSAN-UNINIT-VALUE`; alternate title(s) `bad-access in btrfs_bin_search`. The raw log targets Btrfs filesystem and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `KMSAN: uninit-value in btrfs_bin_search`, type `KMSAN-UNINIT-VALUE`, frame `none`, alternate titles `bad-access in btrfs_bin_search`, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `btrfs_bin_search`
- `btrfs_search_slot`
- `btrfs_insert_empty_items`
- `btrfs_create_new_inode`
- `btrfs_create_common`
- `btrfs_create`
- `path_openat`
- `do_filp_open`
- `do_sys_openat2`
- `__ia32_compat_sys_open`
- `__do_fast_syscall_32`
- `do_fast_syscall_32`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `KMSAN: uninit-value in btrfs_bin_search` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 50 lines and about 2745 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: KMSAN: uninit-value in btrfs_bin_search+0x74c/0xb30

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Btrfs filesystem functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/701 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/702 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/702

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/702`. It records expected title `KMSAN: uninit-value in post_read_mst_fixup`; type `KMSAN-UNINIT-VALUE`; alternate title(s) `bad-access in post_read_mst_fixup`. The raw log targets NTFS filesystem and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `KMSAN: uninit-value in post_read_mst_fixup`, type `KMSAN-UNINIT-VALUE`, frame `none`, alternate titles `bad-access in post_read_mst_fixup`, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `post_read_mst_fixup`
- `ntfs_end_buffer_async_read`
- `end_bio_bh_io_sync`
- `bio_endio`
- `submit_bio_noacct`
- `submit_bio`
- `submit_bh_wbc`
- `submit_bh`
- `ntfs_read_folio`
- `filemap_read_folio`
- `do_read_cache_folio`
- `read_cache_page`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `KMSAN: uninit-value in post_read_mst_fixup` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 62 lines and about 3300 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: KMSAN: uninit-value in post_read_mst_fixup+0xab8/0xb70

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: NTFS filesystem functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/702 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/703 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/703

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/703`. It records expected title `KMSAN: uninit-value in nilfs_add_checksums_on_logs`; type `KMSAN-UNINIT-VALUE`; alternate title(s) `bad-access in nilfs_add_checksums_on_logs`. The raw log targets NILFS filesystem and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `KMSAN: uninit-value in nilfs_add_checksums_on_logs`, type `KMSAN-UNINIT-VALUE`, frame `none`, alternate titles `bad-access in nilfs_add_checksums_on_logs`, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `crc32_le_base`
- `nilfs_add_checksums_on_logs`
- `nilfs_segctor_do_construct`
- `nilfs_segctor_construct`
- `nilfs_segctor_thread`
- `kthread`
- `ret_from_fork`
- `__alloc_pages`
- `alloc_pages`
- `folio_alloc`
- `filemap_alloc_folio`
- `__filemap_get_folio`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `KMSAN: uninit-value in nilfs_add_checksums_on_logs` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 44 lines and about 2450 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: KMSAN: uninit-value in crc32_le_base+0x43c/0xd80

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: NILFS filesystem functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/703 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/704 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/704

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/704`. It records expected title `KASAN: slab-use-after-free Read in btrfs_evict_inode`; type `KASAN-USE-AFTER-FREE-READ`; primary frame `btrfs_evict_inode`; alternate title(s) `bad-access in btrfs_evict_inode`; flags `PANICKED=Y`. The raw log targets Btrfs filesystem and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `KASAN: slab-use-after-free Read in btrfs_evict_inode`, type `KASAN-USE-AFTER-FREE-READ`, frame `btrfs_evict_inode`, alternate titles `bad-access in btrfs_evict_inode`, and flags `PANICKED`. The principal kernel/user-space symbols visible to the parser are:

- `dump_stack_lvl`
- `irq_work_queue`
- `nf_tcp_handle_invalid`
- `panic`
- `_printk`
- `print_report`
- `__virt_addr_valid`
- `__phys_addr`
- `xas_start`
- `kasan_report`
- `xas_find`
- `find_lock_entries`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `KASAN: slab-use-after-free Read in btrfs_evict_inode` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 227 lines and about 13903 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: KASAN: slab-use-after-free in xas_start+0x1ef/0x7b0
- Kernel panic - not syncing: KASAN: panic_on_warn set ...

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Btrfs filesystem functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/704 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/705 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/705

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/705`. It records expected title `go runtime error`; type `DoS`; flags `SUPPRESSED=Y`. The raw log targets Linux crash-report parsing and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `go runtime error`, type `DoS`, frame `none`, alternate titles none, and flags `SUPPRESSED`. The principal kernel/user-space symbols visible to the parser are:

- `runtime/panic.go:1047`
- `runtime/mcache.go:236`
- `runtime/malloc.go:1053`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `go runtime error` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 16 lines and about 547 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- fatal error: out of memory

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/705 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/706 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/706

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/706`. It records no expected crash title. This is a deliberately mangled syslog-style ALSA fatal-error stream with no expected parsed crash header, useful for checking that repeated driver error text and broken prefixes do not become a report. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the negative parser path where `Reporter.Parse` should return no crash report, or at least should not synthesize a title from warning-like noise: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `none`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness loads the file, finds no `TITLE:` oracle in the header block, and then feeds the remaining log to the Linux reporter. The relevant control flow is `findFirstOops` scanning each prefixed line against `linuxOopses` and the ignore expressions; a successful result here would be a regression because the fixture is intended to stay below report threshold. The log contains 7 lines and about 475 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- Sep 23 02:31[ 69.295771][ T2742] ALSA: seq fatal error: cannot create timer (-22)
- :17 syzkaller ke[ 69.303665][ T2742] ALSA: seq fatal error: cannot create timer (-22)
- rn.err kernel: [[ 69.311910][ T2742] ALSA: seq fatal error: cannot create timer (-22)
- 68.938106][ T[ 69.319571][ T2742] ALSA: seq fatal error: cannot create timer (-22)
- 2742] ALSA: seq [ 69.327618][ T2742] ALSA: seq fatal error: cannot create timer (-22)
- fatal error: cannot create timer (-22)

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses negative matching and noisy warning suppression with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/706 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/707 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/707

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/707`. It records expected title `go runtime error`; type `DoS`. The raw log targets Linux crash-report parsing and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `go runtime error`, type `DoS`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `go runtime error` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 7 lines and about 110 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- fatal error: runtimer: bad p

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/707 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/708 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/708

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/708`. It records expected title `KMSAN: kernel-infoleak in filemap_read`; type `KMSAN-INFO-LEAK`; alternate title(s) `bad-access in filemap_read`. The raw log targets MM/page-cache and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `KMSAN: kernel-infoleak in filemap_read`, type `KMSAN-INFO-LEAK`, frame `none`, alternate titles `bad-access in filemap_read`, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `_copy_to_iter`
- `copy_page_to_iter`
- `filemap_read`
- `blkdev_read_iter`
- `vfs_read`
- `ksys_read`
- `__x64_sys_read`
- `do_syscall_64`
- `entry_SYSCALL_64_after_hwframe`
- `shmem_file_read_iter`
- `do_iter_read`
- `vfs_iter_read`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `KMSAN: kernel-infoleak in filemap_read` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 89 lines and about 4612 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: KMSAN: kernel-infoleak in _copy_to_iter+0x376/0x1c60

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: MM/page-cache functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/708 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/709 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/709

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/709`. It records expected title `KMSAN: uninit-value in tipc_nl_node_reset_link_stats`; type `KMSAN-UNINIT-VALUE`; alternate title(s) `bad-access in tipc_nl_node_reset_link_stats`. The raw log targets TIPC networking and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `KMSAN: uninit-value in tipc_nl_node_reset_link_stats`, type `KMSAN-UNINIT-VALUE`, frame `none`, alternate titles `bad-access in tipc_nl_node_reset_link_stats`, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `strstr`
- `tipc_nl_node_reset_link_stats`
- `genl_rcv_msg`
- `netlink_rcv_skb`
- `genl_rcv`
- `netlink_unicast`
- `netlink_sendmsg`
- `____sys_sendmsg`
- `___sys_sendmsg`
- `__x64_sys_sendmsg`
- `do_syscall_64`
- `entry_SYSCALL_64_after_hwframe`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `KMSAN: uninit-value in tipc_nl_node_reset_link_stats` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 34 lines and about 1830 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: KMSAN: uninit-value in strstr+0xb8/0x2f0

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: TIPC networking functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/709 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/71 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/71

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/71`. It records expected title `INFO: task hung in blkdev_put`; type `HANG`; alternate title(s) `hang in blkdev_put`. The raw log targets block device teardown and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `INFO: task hung in blkdev_put`, type `HANG`, frame `none`, alternate titles `hang in blkdev_put`, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `__schedule`
- `schedule`
- `schedule_preempt_disabled`
- `mutex_lock_nested`
- `blkdev_put`
- `mutex_lock_killable_nested`
- `locks_remove_file`
- `fsnotify`
- `blkdev_close`
- `__fput`
- `____fput`
- `task_work_run`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `INFO: task hung in blkdev_put` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 34 lines and about 2038 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- INFO: task syz-executor2:14507 blocked for more than 120 seconds.

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: block device teardown functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/71 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/710 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/710

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/710`. It records no expected crash title. This boot-log fragment contains CPU vulnerability and mitigation warnings without a syzkaller crash oracle, so it exercises ignore handling for informational boot warnings. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the negative parser path where `Reporter.Parse` should return no crash report, or at least should not synthesize a title from warning-like noise: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `none`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness loads the file, finds no `TITLE:` oracle in the header block, and then feeds the remaining log to the Linux reporter. The relevant control flow is `findFirstOops` scanning each prefixed line against `linuxOopses` and the ignore expressions; a successful result here would be a regression because the fixture is intended to stay below report threshold. The log contains 27 lines and about 1522 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- Speculative Return Stack Overflow: IBPB-extending microcode not applied!
- Speculative Return Stack Overflow: WARNING: See https://kernel.org/doc/html/latest/admin-guide/hw-vuln/srso.html for mitigation options.
- Speculative Return Stack Overflow: WARNING: kernel not compiled with CPU_SRSO.
- Speculative Return Stack Overflow: Vulnerable: No microcode

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses negative matching and noisy warning suppression with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/710 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/711 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/711

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/711`. It records expected title `WARNING in hci_conn_del`; type `WARNING`; flags `PANICKED=Y`. The raw log targets Bluetooth HCI and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `WARNING in hci_conn_del`, type `WARNING`, frame `none`, alternate titles none, and flags `PANICKED`. The principal kernel/user-space symbols visible to the parser are:

- `ida_free`
- `__warn`
- `report_bug`
- `handle_bug`
- `exc_invalid_op`
- `asm_exc_invalid_op`
- `__warn_printk`
- `__pfx_ida_free`
- `__pfx___mutex_unlock_slowpath`
- `hci_conn_unlink`
- `hci_conn_del`
- `hci_conn_hash_flush`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `WARNING in hci_conn_del` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 107 lines and about 6559 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- WARNING: CPU: 0 PID: 23686 at lib/idr.c:525 ida_free+0x370/0x420
- Kernel panic - not syncing: kernel: panic_on_warn set ...

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Bluetooth HCI functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/711 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/712 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/712

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/712`. It records no expected crash title. This truncated deprecated mount-option warning starts with a separator and warning text but has no expected title, exercising partial-line and ignore behavior. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the negative parser path where `Reporter.Parse` should return no crash report, or at least should not synthesize a title from warning-like noise: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `none`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness loads the file, finds no `TITLE:` oracle in the header block, and then feeds the remaining log to the Linux reporter. The relevant control flow is `findFirstOops` scanning each prefixed line against `linuxOopses` and the ignore expressions; a successful result here would be a regression because the fixture is intended to stay below report threshold. The log contains 3 lines and about 150 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- WARNING: the mand mount option is being deprecat

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses negative matching and noisy warning suppression with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/712 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/713 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/713

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/713`. It records expected title `kernel BUG in bch2_fs_recovery`; type `BUG`; primary frame `bch2_fs_recovery`. The raw log targets bcachefs recovery and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `kernel BUG in bch2_fs_recovery`, type `BUG`, frame `bch2_fs_recovery`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `__phys_addr`
- `__die_body`
- `die`
- `do_trap`
- `do_error_trap`
- `bch2_fs_recovery`
- `__pfx_do_error_trap`
- `handle_invalid_op`
- `exc_invalid_op`
- `asm_exc_invalid_op`
- `kfree`
- `mark_lock`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `kernel BUG in bch2_fs_recovery` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 89 lines and about 5630 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- kernel BUG at arch/x86/mm/physaddr.c:23!

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: bcachefs recovery functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/713 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/714 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/714

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/714`. It records expected title `WARNING in ext4_fileattr_get`; type `WARNING`; flags `PANICKED=Y`. The raw log targets Ext4 ioctl/mount and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `WARNING in ext4_fileattr_get`, type `WARNING`, frame `none`, alternate titles none, and flags `PANICKED`. The principal kernel/user-space symbols visible to the parser are:

- `show_stack`
- `dump_stack_lvl`
- `dump_stack`
- `panic`
- `print_tainted`
- `__warn`
- `warn_slowpath_fmt`
- `__fortify_report`
- `__fortify_panic`
- `ext4_fileattr_get`
- `ext4_ioctl`
- `sys_ioctl`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `WARNING in ext4_fileattr_get` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 41 lines and about 2952 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- WARNING: CPU: 0 PID: 3004 at lib/string_helpers.c:1029 __fortify_report+0x6c/0x74
- Kernel panic - not syncing: kernel: panic_on_warn set ...

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Ext4 ioctl/mount functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/714 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/715 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/715

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/715`. It records expected title `WARNING in kvm_put_kvm`; type `WARNING`; flags `PANICKED=Y`. The raw log targets KVM virtualization and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `WARNING in kvm_put_kvm`, type `WARNING`, frame `none`, alternate titles none, and flags `PANICKED`. The principal kernel/user-space symbols visible to the parser are:

- `cleanup_srcu_struct`
- `show_regs`
- `__warn`
- `report_bug`
- `handle_bug`
- `exc_invalid_op`
- `asm_exc_invalid_op`
- `kvm_put_kvm`
- `__pfx_kvm_vm_release`
- `kvm_vm_release`
- `__fput`
- `_raw_spin_unlock_irq`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `WARNING in kvm_put_kvm` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 99 lines and about 6940 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- WARNING: CPU: 0 PID: 11919 at kernel/rcu/srcutree.c:653 cleanup_srcu_struct+0x37c/0x520
- Kernel panic - not syncing: kernel: panic_on_warn set ...

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: KVM virtualization functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/715 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/716 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/716

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/716`. It records expected title `SYZFAIL: SIGSEGV`; type `SYZ_FAILURE`. The raw log targets Linux crash-report parsing and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `SYZFAIL: SIGSEGV`, type `SYZ_FAILURE`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `SYZFAIL: SIGSEGV` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 5 lines and about 142 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- SYZFAIL: SIGSEGV

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/716 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/717 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/717

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/717`. It records expected title `SYZFAIL: SIGBUS`; type `SYZ_FAILURE`; flags `SUPPRESSED=Y`. The raw log targets Linux crash-report parsing and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `SYZFAIL: SIGBUS`, type `SYZ_FAILURE`, frame `none`, alternate titles none, and flags `SUPPRESSED`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `SYZFAIL: SIGBUS` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 6 lines and about 154 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- SYZFAIL: SIGBUS

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/717 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/718 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/718

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/718`. It records expected title `INFO: rcu detected stall in corrupted`; type `HANG`; alternate title(s) `stall in corrupted`; flags `CORRUPTED=Y`, `EXECUTOR=proc=0, id=104`. The raw log targets RCU scheduler/stall detection and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `INFO: rcu detected stall in corrupted`, type `HANG`, frame `none`, alternate titles `stall in corrupted`, and flags `CORRUPTED, EXECUTOR`. The principal kernel/user-space symbols visible to the parser are:

- `__schedule`
- `__kasan_check_write`
- `__mod_timer`
- `__pfx___schedule`
- `__pfx___try_to_del_timer_sync`
- `schedule`
- `schedule_timeout`
- `__pfx__raw_spin_unlock_irqrestore`
- `__pfx_schedule_timeout`
- `__pfx_process_timeout`
- `prepare_to_swait_event`
- `rcu_gp_fqs_loop`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `INFO: rcu detected stall in corrupted` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 111 lines and about 7031 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:
- rcu: (detected by 1, t=10002 jiffies, g=4241, q=1639 ncpus=2)
- rcu: All QSes seen, last rcu_preempt kthread activity 9998 (4294951926-4294941928), jiffies_till_next_fqs=1, root ->qsmask 0x0
- rcu: rcu_preempt kthread starved for 9998 jiffies! g4241 f0x2 RCU_GP_WAIT_FQS(5) ->state=0x0 ->cpu=0
- rcu: Unless rcu_preempt kthread gets sufficient CPU time, OOM is now expected behavior.
- rcu: RCU grace-period kthread stack dump:
- rcu: Stack dump where RCU GP kthread last ran:

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: RCU scheduler/stall detection functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/718 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/719 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/719

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/719`. It records expected title `INFO: rcu detected stall in corrupted`; type `HANG`; alternate title(s) `stall in corrupted`; flags `CORRUPTED=Y`, `EXECUTOR=proc=2, id=4572`. The raw log targets RCU scheduler/stall detection and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `INFO: rcu detected stall in corrupted`, type `HANG`, frame `none`, alternate titles `stall in corrupted`, and flags `CORRUPTED, EXECUTOR`. The principal kernel/user-space symbols visible to the parser are:

- `__schedule`
- `swake_up_one_online`
- `__kasan_check_write`
- `irqentry_exit`
- `sysvec_reschedule_ipi`
- `__pfx___schedule`
- `page_table_check_set`
- `preempt_schedule`
- `preempt_schedule_common`
- `__pfx_preempt_schedule`
- `__page_table_check_ptes_set`
- `preempt_schedule_thunk`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `INFO: rcu detected stall in corrupted` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 232 lines and about 14140 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:
- rcu: Tasks blocked on level-0 rcu_node (CPUs 0-1): P30749/1:b..l P22934/1:b..l
- rcu: (detected by 0, t=10002 jiffies, g=56441, q=553 ncpus=2)
- rcu: rcu_preempt kthread starved for 10015 jiffies! g56441 f0x0 RCU_GP_WAIT_FQS(5) ->state=0x0 ->cpu=0
- rcu: Unless rcu_preempt kthread gets sufficient CPU time, OOM is now expected behavior.
- rcu: RCU grace-period kthread stack dump:
- rcu: Stack dump where RCU GP kthread last ran:

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: RCU scheduler/stall detection functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/719 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/72 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/72

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/72`. It records expected title `INFO: task hung in rtnl_lock`; type `HANG`; alternate title(s) `hang in rtnl_lock`. The raw log targets network rtnl locking and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `INFO: task hung in rtnl_lock`, type `HANG`, frame `none`, alternate titles `hang in rtnl_lock`, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `schedule`
- `schedule_preempt_disabled`
- `mutex_lock_nested`
- `rtnl_lock`
- `ieee80211_unregister_hw`
- `ret_from_fork`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `INFO: task hung in rtnl_lock` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 19 lines and about 1063 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- INFO: task kworker/0:1:764 blocked for more than 120 seconds.

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: network rtnl locking functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/72 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/720 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/720

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/720`. It records expected title `INFO: rcu detected stall in corrupted`; type `HANG`; alternate title(s) `stall in corrupted`; flags `CORRUPTED=Y`, `EXECUTOR=proc=2, id=737`. The raw log targets RCU scheduler/stall detection and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `INFO: rcu detected stall in corrupted`, type `HANG`, frame `none`, alternate titles `stall in corrupted`, and flags `CORRUPTED, EXECUTOR`. The principal kernel/user-space symbols visible to the parser are:

- `__schedule`
- `__kasan_check_write`
- `_raw_spin_lock_irqsave`
- `__pfx___schedule`
- `prb_read_valid`
- `__pfx_prb_read_valid`
- `preempt_schedule`
- `preempt_schedule_common`
- `__pfx_preempt_schedule`
- `console_trylock`
- `__pfx_console_trylock`
- `preempt_schedule_thunk`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `INFO: rcu detected stall in corrupted` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 215 lines and about 12628 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:
- rcu: Tasks blocked on level-0 rcu_node (CPUs 0-1): P9294/1:b..l
- rcu: (detected by 1, t=10002 jiffies, g=13073, q=1262 ncpus=2)
- rcu: rcu_preempt kthread starved for 10005 jiffies! g13073 f0x0 RCU_GP_WAIT_FQS(5) ->state=0x0 ->cpu=0
- rcu: Unless rcu_preempt kthread gets sufficient CPU time, OOM is now expected behavior.
- rcu: RCU grace-period kthread stack dump:
- rcu: Stack dump where RCU GP kthread last ran:

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: RCU scheduler/stall detection functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/720 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/721 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/721

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/721`. It records expected title `KASAN: use-after-free Read in ila_nf_input`; type `KASAN-USE-AFTER-FREE-READ`; alternate title(s) `bad-access in ila_nf_input`; flags `PANICKED=Y`, `EXECUTOR=proc=4, id=2288`. The raw log targets ILA network transform and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `KASAN: use-after-free Read in ila_nf_input`, type `KASAN-USE-AFTER-FREE-READ`, frame `none`, alternate titles `bad-access in ila_nf_input`, and flags `PANICKED, EXECUTOR`. The principal kernel/user-space symbols visible to the parser are:

- `dump_stack_lvl`
- `__pfx_dump_stack_lvl`
- `__pfx__printk`
- `_printk`
- `__virt_addr_valid`
- `print_report`
- `__phys_addr`
- `rhashtable_lookup_fast`
- `kasan_report`
- `__pfx_ila_cmpfn`
- `__pfx_rhashtable_lookup_fast`
- `ila_nf_input`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `KASAN: use-after-free Read in ila_nf_input` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 320 lines and about 20047 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: KASAN: use-after-free in rhashtable_lookup_fast+0x77a/0x9b0
- Kernel panic - not syncing: KASAN: panic_on_warn set ...

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: ILA network transform functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/721 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/722 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/722

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/722`. It records no expected crash title. This XFS unknown-parameter line embeds boot text inside a quoted mount parameter and should not be treated as a kernel boot crash. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the negative parser path where `Reporter.Parse` should return no crash report, or at least should not synthesize a title from warning-like noise: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `none`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness loads the file, finds no `TITLE:` oracle in the header block, and then feeds the remaining log to the Linux reporter. The relevant control flow is `findFirstOops` scanning each prefixed line against `linuxOopses` and the ignore expressions; a successful result here would be a regression because the fixture is intended to stay below report threshold. The log contains 2 lines and about 273 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- No oops-class line is expected; the fixture is dominated by ignorable or truncated console output.

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses negative matching and noisy warning suppression with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/722 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/723 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/723

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/723`. It records no expected crash title. This FUSE unknown-parameter line embeds decompressor and boot text in a quoted parameter and checks that the parser does not fire on quoted noise. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the negative parser path where `Reporter.Parse` should return no crash report, or at least should not synthesize a title from warning-like noise: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `none`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness loads the file, finds no `TITLE:` oracle in the header block, and then feeds the remaining log to the Linux reporter. The relevant control flow is `findFirstOops` scanning each prefixed line against `linuxOopses` and the ignore expressions; a successful result here would be a regression because the fixture is intended to stay below report threshold. The log contains 2 lines and about 997 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- No oops-class line is expected; the fixture is dominated by ignorable or truncated console output.

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses negative matching and noisy warning suppression with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/723 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/724 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/724

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/724`. It records no expected crash title. This early boot banner and command line have no crash header; it is a negative fixture for normal startup output. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the negative parser path where `Reporter.Parse` should return no crash report, or at least should not synthesize a title from warning-like noise: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `none`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness loads the file, finds no `TITLE:` oracle in the header block, and then feeds the remaining log to the Linux reporter. The relevant control flow is `findFirstOops` scanning each prefixed line against `linuxOopses` and the ignore expressions; a successful result here would be a regression because the fixture is intended to stay below report threshold. The log contains 6 lines and about 476 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- No oops-class line is expected; the fixture is dominated by ignorable or truncated console output.

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses negative matching and noisy warning suppression with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/724 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/725 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/725

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/725`. It records expected title `BUG: Bad page state in __get_metapage`. The raw log targets MM/page-cache and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `BUG: Bad page state in __get_metapage`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `post_alloc_hook`
- `get_page_from_freelist`
- `__alloc_pages_noprof`
- `alloc_pages_mpol_noprof`
- `folio_alloc_noprof`
- `filemap_alloc_folio_noprof`
- `__filemap_get_folio`
- `pagecache_get_page`
- `__get_metapage`
- `diNewExt`
- `diAllocAG`
- `diAlloc`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `BUG: Bad page state in __get_metapage` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 91 lines and about 5743 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: Bad page state in process syz-executor209 pfn:7deea

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: MM/page-cache functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/725 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/726 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/726

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/726`. It records expected title `BUG: Bad page state in bpf_test_run_xdp_live`; flags `EXECUTOR=proc=3, id=584`. The raw log targets BPF/XDP and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `BUG: Bad page state in bpf_test_run_xdp_live`, type `none`, frame `none`, alternate titles none, and flags `EXECUTOR`. The principal kernel/user-space symbols visible to the parser are:

- `post_alloc_hook`
- `get_page_from_freelist`
- `__alloc_pages_noprof`
- `alloc_pages_bulk_noprof`
- `__page_pool_alloc_pages_slow`
- `page_pool_alloc_pages`
- `bpf_test_run_xdp_live`
- `bpf_prog_test_run_xdp`
- `bpf_prog_test_run`
- `__sys_bpf`
- `__x64_sys_bpf`
- `do_syscall_64`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `BUG: Bad page state in bpf_test_run_xdp_live` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 102 lines and about 6460 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: Bad page state in process syz.3.584 pfn:7071f
- SYZFAIL: failed to recv rpc

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: BPF/XDP functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/726 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/727 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/727

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/727`. It records expected title `BUG: Bad page state in corrupted`; flags `CORRUPTED=Y`. The raw log targets Linux crash-report parsing and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `BUG: Bad page state in corrupted`, type `none`, frame `none`, alternate titles none, and flags `CORRUPTED`. The principal kernel/user-space symbols visible to the parser are:

- `dump_backtrace`
- `show_stack`
- `dump_stack_lvl`
- `dump_stack`
- `bad_page`
- `free_page_is_bad_report`
- `free_unref_page_prepare`
- `free_unref_page`
- `__folio_put`
- `extract_iter_to_sg`
- `hash_sendmsg`
- `____sys_sendmsg`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `BUG: Bad page state in corrupted` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 36 lines and about 2116 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: Bad page state in process syz-executor.0 pfn:1b317b

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/727 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/728 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/728

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/728`. It records no expected crash title. This EXT4 mount warning block is expected to be ignored even though it contains warning language. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the negative parser path where `Reporter.Parse` should return no crash report, or at least should not synthesize a title from warning-like noise: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `none`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness loads the file, finds no `TITLE:` oracle in the header block, and then feeds the remaining log to the Linux reporter. The relevant control flow is `findFirstOops` scanning each prefixed line against `linuxOopses` and the ignore expressions; a successful result here would be a regression because the fixture is intended to stay below report threshold. The log contains 6 lines and about 221 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- No oops-class line is expected; the fixture is dominated by ignorable or truncated console output.

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses negative matching and noisy warning suppression with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/728 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/729 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/729

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/729`. It records expected title `BUG: Bad page state in xdp_test_run_batch`; flags `EXECUTOR=proc=2, id=1806`. The raw log targets BPF/XDP and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `BUG: Bad page state in xdp_test_run_batch`, type `none`, frame `none`, alternate titles none, and flags `EXECUTOR`. The principal kernel/user-space symbols visible to the parser are:

- `__set_page_owner`
- `post_alloc_hook`
- `get_page_from_freelist`
- `__alloc_pages_noprof`
- `alloc_pages_bulk_noprof`
- `__page_pool_alloc_pages_slow`
- `page_pool_alloc_netmem`
- `page_pool_alloc_pages`
- `xdp_test_run_batch.constprop.0`
- `bpf_test_run_xdp_live`
- `bpf_prog_test_run_xdp`
- `__sys_bpf`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `BUG: Bad page state in xdp_test_run_batch` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 64 lines and about 4265 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: Bad page state in process syz.2.1806 pfn:ab652

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: BPF/XDP functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/729 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/73 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/73

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/73`. It records expected title `INFO: task hung in set_current_rng`; type `HANG`; alternate title(s) `hang in set_current_rng`. The raw log targets hardware RNG/USB and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `INFO: task hung in set_current_rng`, type `HANG`, frame `none`, alternate titles `hang in set_current_rng`, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `__schedule`
- `schedule`
- `schedule_timeout`
- `mark_held_locks`
- `_raw_spin_unlock_irq`
- `trace_hardirqs_on_caller`
- `wait_for_completion`
- `wake_up_q`
- `kthread_stop`
- `set_current_rng`
- `hwrng_unregister`
- `chaoskey_disconnect`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `INFO: task hung in set_current_rng` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 24 lines and about 1080 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- INFO: task syz-executor0:5676 blocked for more than 120 seconds.

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: hardware RNG/USB functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/73 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/730 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/730

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/730`. It records expected title `WARNING in udf_rmdir`; type `WARNING`; primary frame `udf_rmdir`; flags `PANICKED=Y`. The raw log targets UDF filesystem and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `WARNING in udf_rmdir`, type `WARNING`, frame `udf_rmdir`, alternate titles none, and flags `PANICKED`. The principal kernel/user-space symbols visible to the parser are:

- `drop_nlink`
- `__warn`
- `report_bug`
- `handle_bug`
- `exc_invalid_op`
- `asm_exc_invalid_op`
- `udf_rmdir`
- `__pfx_udf_rmdir`
- `down_write`
- `__pfx_down_write`
- `do_raw_spin_unlock`
- `bpf_lsm_inode_rmdir`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `WARNING in udf_rmdir` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 117 lines and about 7725 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- WARNING: CPU: 1 PID: 5830 at fs/inode.c:336 drop_nlink+0xc4/0x110
- Kernel panic - not syncing: kernel: panic_on_warn set ...

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: UDF filesystem functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/730 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/731 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/731

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/731`. It records no expected crash title. This syslog-uppercase noise stream contains netlink, IPVS, capability, USB, and Bluetooth warnings but no expected report title. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the negative parser path where `Reporter.Parse` should return no crash report, or at least should not synthesize a title from warning-like noise: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `none`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness loads the file, finds no `TITLE:` oracle in the header block, and then feeds the remaining log to the Linux reporter. The relevant control flow is `findFirstOops` scanning each prefixed line against `linuxOopses` and the ignore expressions; a successful result here would be a regression because the fixture is intended to stay below report threshold. The log contains 22 lines and about 2212 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- CAPABILITY: WARNING: `SYZ.2.309' USES DEPRECATED V2 CAPABILITIES IN A WAY THAT MAY BE INSECURE

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses negative matching and noisy warning suppression with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/731 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/732 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/732

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/732`. It records no expected crash title. This daemon/syslog interleaving includes an uppercase kernel wireless-extension warning and many libudev errors; it checks noise filtering across mixed prefixes. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the negative parser path where `Reporter.Parse` should return no crash report, or at least should not synthesize a title from warning-like noise: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `none`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness loads the file, finds no `TITLE:` oracle in the header block, and then feeds the remaining log to the Linux reporter. The relevant control flow is `findFirstOops` scanning each prefixed line against `linuxOopses` and the ignore expressions; a successful result here would be a regression because the fixture is intended to stay below report threshold. The log contains 22 lines and about 1837 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- WARNING: `SYZ.1.261' USES WIRELESS EXTENSIONS WHICH WILL STOP WORKING FOR WI-FI 7 HARDWARE; USE NL80211

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses negative matching and noisy warning suppression with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/732 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/733 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/733

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/733`. It records expected title `WARNING: refcount bug in hdm_disconnect`; type `REFCOUNT_WARNING`; flags `PANICKED=Y`. The raw log targets USB MOST/HDM driver and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `WARNING: refcount bug in hdm_disconnect`, type `REFCOUNT_WARNING`, frame `none`, alternate titles none, and flags `PANICKED`. The principal kernel/user-space symbols visible to the parser are:

- `show_stack`
- `dump_stack_lvl`
- `dump_stack`
- `panic`
- `get_taint`
- `__warn`
- `warn_slowpath_fmt`
- `refcount_warn_saturate`
- `kobject_put`
- `put_device`
- `hdm_disconnect`
- `usb_unbind_interface`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `WARNING: refcount bug in hdm_disconnect` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 72 lines and about 5519 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- WARNING: CPU: 1 PID: 46 at lib/refcount.c:28 refcount_warn_saturate+0x13c/0x174
- Kernel panic - not syncing: kernel: panic_on_warn set ...

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: USB MOST/HDM driver functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/733 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/734 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/734

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/734`. It records expected title `BUG: unable to handle kernel paging request in vgic_mmio_write_invlpi`; type `MEMORY_SAFETY_BUG`; primary frame `vgic_mmio_write_invlpi`; alternate title(s) `bad-access in vgic_mmio_write_invlpi`; flags `PANICKED=Y`, `EXECUTOR=proc=2, id=929`. The raw log targets KVM virtualization and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `BUG: unable to handle kernel paging request in vgic_mmio_write_invlpi`, type `MEMORY_SAFETY_BUG`, frame `vgic_mmio_write_invlpi`, alternate titles `bad-access in vgic_mmio_write_invlpi`, and flags `PANICKED, EXECUTOR`. The principal kernel/user-space symbols visible to the parser are:

- `__hwasan_check_x0_67043363`
- `vgic_get_irq`
- `vgic_mmio_write_invlpi`
- `dispatch_mmio_write`
- `__kvm_io_bus_write`
- `kvm_io_bus_write`
- `io_mem_abort`
- `kvm_handle_guest_abort`
- `handle_exit`
- `kvm_arch_vcpu_ioctl_run`
- `kvm_vcpu_ioctl`
- `__arm64_sys_ioctl`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `BUG: unable to handle kernel paging request in vgic_mmio_write_invlpi` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 64 lines and about 3938 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- KASAN: probably user-memory-access in range [0x0000000000001370-0x000000000000137f]
- Internal error: Oops: 0000000096000005 [#1] PREEMPT SMP
- Kernel panic - not syncing: Oops: Fatal exception

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: KVM virtualization functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/734 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/735 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/735

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/735`. It records no expected crash title. This user-space BTF verifier dump is tagged with [U] and should remain user diagnostic output rather than a kernel crash report. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the negative parser path where `Reporter.Parse` should return no crash report, or at least should not synthesize a title from warning-like noise: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `none`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness loads the file, finds no `TITLE:` oracle in the header block, and then feeds the remaining log to the Linux reporter. The relevant control flow is `findFirstOops` scanning each prefixed line against `linuxOopses` and the ignore expressions; a successful result here would be a regression because the fixture is intended to stay below report threshold. The log contains 44 lines and about 1435 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- INVALID BTF_INFO:72000001

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses negative matching and noisy warning suppression with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/735 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/736 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/736

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/736`. It records expected title `BUG: unable to handle kernel paging request in process_srcu`; type `MEMORY_SAFETY_BUG`; primary frame `process_srcu`; alternate title(s) `bad-access in process_srcu`; flags `PANICKED=Y`. The raw log targets KVM virtualization and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `BUG: unable to handle kernel paging request in process_srcu`, type `MEMORY_SAFETY_BUG`, frame `process_srcu`, alternate titles `bad-access in process_srcu`, and flags `PANICKED`. The principal kernel/user-space symbols visible to the parser are:

- `do_raw_spin_lock`
- `__die_body`
- `page_fault_oops`
- `__pfx_page_fault_oops`
- `lock_release`
- `is_prefetch`
- `kvm_sched_clock_read`
- `sched_clock`
- `sched_clock_cpu`
- `__pfx_is_prefetch`
- `__pfx_sched_clock_cpu`
- `__bad_area_nosemaphore`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `BUG: unable to handle kernel paging request in process_srcu` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 99 lines and about 6408 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: unable to handle page fault for address: ffffffff9175c704
- Oops: Oops: 0000 [#1] PREEMPT SMP KASAN PTI
- Kernel panic - not syncing: Fatal exception

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: KVM virtualization functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/736 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/737 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/737

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/737`. It records expected title `KASAN: slab-use-after-free Read in mptcp_pm_del_add_timer`; type `KASAN-USE-AFTER-FREE-READ`; primary frame `mptcp_pm_del_add_timer`; alternate title(s) `bad-access in mptcp_pm_del_add_timer`; flags `PANICKED=Y`. The raw log targets MPTCP networking and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `KASAN: slab-use-after-free Read in mptcp_pm_del_add_timer`, type `KASAN-USE-AFTER-FREE-READ`, frame `mptcp_pm_del_add_timer`, alternate titles `bad-access in mptcp_pm_del_add_timer`, and flags `PANICKED`. The principal kernel/user-space symbols visible to the parser are:

- `dump_stack_lvl`
- `print_report`
- `__virt_addr_valid`
- `__phys_addr`
- `kasan_report`
- `lock_timer_base`
- `__try_to_del_timer_sync`
- `__pfx___try_to_del_timer_sync`
- `__timer_delete_sync`
- `sk_stop_timer_sync`
- `mptcp_pm_del_add_timer`
- `mptcp_incoming_options`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `KASAN: slab-use-after-free Read in mptcp_pm_del_add_timer` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 302 lines and about 16930 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: KASAN: slab-use-after-free in lock_timer_base+0x1d9/0x220
- SYZFAIL: failed to recv rpc
- Kernel panic - not syncing: KASAN: panic_on_warn set ...

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: MPTCP networking functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/737 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/738 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/738

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/738`. It records expected title `general protection fault in mremap`; type `DoS`; primary frame `mremap`; alternate title(s) `bad-access in __se_sys_mremap`, `bad-access in mremap`, `bad-access in sys_mremap`, `general protection fault in __se_sys_mremap`, `general protection fault in sys_mremap`; flags `PANICKED=Y`. The raw log targets memory management syscall and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `general protection fault in mremap`, type `DoS`, frame `mremap`, alternate titles `bad-access in __se_sys_mremap`, `bad-access in mremap`, `bad-access in sys_mremap`, `general protection fault in __se_sys_mremap`, `general protection fault in sys_mremap`, and flags `PANICKED`. The principal kernel/user-space symbols visible to the parser are:

- `__se_sys_mremap`
- `__pfx___se_sys_mremap`
- `_raw_spin_lock_irq`
- `__pfx__raw_spin_lock_irq`
- `_raw_spin_unlock_irq`
- `lockdep_hardirqs_on`
- `ptrace_notify`
- `__x64_sys_mremap`
- `do_syscall_64`
- `clear_bhb_loop`
- `entry_SYSCALL_64_after_hwframe`
- `0x7f56a8c90369`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `general protection fault in mremap` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 67 lines and about 5007 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- Oops: general protection fault, probably for non-canonical address 0xdffffc0000000004: 0000 [#1] SMP KASAN PTI
- KASAN: null-ptr-deref in range [0x0000000000000020-0x0000000000000027]
- Kernel panic - not syncing: Fatal exception

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: memory management syscall functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/738 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/739 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/739

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/739`. It records no expected crash title. This XFS filesystem warning says to run repair but has no expected crash header; it validates warning filtering for filesystem maintenance messages. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the negative parser path where `Reporter.Parse` should return no crash report, or at least should not synthesize a title from warning-like noise: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `none`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness loads the file, finds no `TITLE:` oracle in the header block, and then feeds the remaining log to the Linux reporter. The relevant control flow is `findFirstOops` scanning each prefixed line against `linuxOopses` and the ignore expressions; a successful result here would be a regression because the fixture is intended to stay below report threshold. The log contains 9 lines and about 617 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- XFS (loop4): WARNING: Reset corrupted AGFL on AG 0. 1 blocks leaked. Please unmount and run xfs_repair.

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses negative matching and noisy warning suppression with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/739 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/74 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/74

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/74`. It records expected title `INFO: task hung in copy_net_ns`; type `HANG`; alternate title(s) `hang in copy_net_ns`. The raw log targets network namespace creation and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `INFO: task hung in copy_net_ns`, type `HANG`, frame `none`, alternate titles `hang in copy_net_ns`, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `schedule`
- `schedule_preempt_disabled`
- `mutex_lock_nested`
- `copy_net_ns`
- `___slab_alloc`
- `mutex_lock_killable_nested`
- `__slab_alloc`
- `rcu_read_lock_sched_held`
- `kmem_cache_alloc`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `INFO: task hung in copy_net_ns` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 25 lines and about 1527 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- INFO: task syz-executor0:6102 blocked for more than 120 seconds.

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: network namespace creation functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/74 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/740 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/740

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/740`. It records expected title `KASAN: slab-use-after-free Read in chrdev_open`; type `KASAN-USE-AFTER-FREE-READ`; alternate title(s) `bad-access in chrdev_open`. The raw log targets character device open and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `KASAN: slab-use-after-free Read in chrdev_open`, type `KASAN-USE-AFTER-FREE-READ`, frame `none`, alternate titles `bad-access in chrdev_open`, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `dump_stack_lvl`
- `print_report`
- `kasan_report`
- `__list_add_valid_or_report`
- `chrdev_open`
- `do_dentry_open`
- `vfs_open`
- `path_openat`
- `do_filp_open`
- `do_sys_openat2`
- `do_sys_open`
- `__x64_sys_openat`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `KASAN: slab-use-after-free Read in chrdev_open` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 152 lines and about 5802 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- BUG: KASAN: slab-use-after-free in __list_add_valid_or_report+0x16a/0x1a0

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: character device open functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/740 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/741 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/741

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/741`. It records expected title `kernel BUG in f2fs_sync_node_pages`; type `BUG`; flags `PANICKED=Y`. The raw log targets RCU scheduler/stall detection and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `kernel BUG in f2fs_sync_node_pages`, type `BUG`, frame `none`, alternate titles none, and flags `PANICKED`. The principal kernel/user-space symbols visible to the parser are:

- `folio_unlock`
- `f2fs_sync_node_pages`
- `__pfx_f2fs_sync_node_pages`
- `__percpu_counter_sum`
- `rcu_is_watching`
- `blk_start_plug`
- `f2fs_write_node_pages`
- `__pfx_f2fs_write_node_pages`
- `unwind_next_frame`
- `do_writepages`
- `reacquire_held_locks`
- `writeback_sb_inodes`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `kernel BUG in f2fs_sync_node_pages` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 89 lines and about 5993 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- kernel BUG at mm/filemap.c:1498!
- Oops: invalid opcode: 0000 [#1] SMP KASAN PTI
- Kernel panic - not syncing: Fatal exception

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: RCU scheduler/stall detection functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/741 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/742 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/742

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/742`. It records expected title `kernel BUG in netfs_perform_write`; type `BUG`; flags `PANICKED=Y`, `EXECUTOR=proc=0, id=886`. The raw log targets netfs/v9fs write path and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `kernel BUG in netfs_perform_write`, type `BUG`, frame `none`, alternate titles none, and flags `PANICKED, EXECUTOR`. The principal kernel/user-space symbols visible to the parser are:

- `folio_unlock`
- `die`
- `do_trap`
- `do_error_trap`
- `handle_invalid_op`
- `exc_invalid_op`
- `asm_exc_invalid_op`
- `netfs_perform_write`
- `__pfx_netfs_perform_write`
- `inode_needs_update_time.part.0`
- `netfs_file_write_iter`
- `v9fs_file_write_iter`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `kernel BUG in netfs_perform_write` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 79 lines and about 5647 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- kernel BUG at mm/filemap.c:1499!
- Oops: invalid opcode: 0000 [#1] PREEMPT SMP KASAN NOPTI
- Kernel panic - not syncing: Fatal exception

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: netfs/v9fs write path functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/742 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/743 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/743

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/743`. It records expected title `WARNING in __ieee80211_beacon_get`; type `WARNING`; flags `PANICKED=Y`, `EXECUTOR=proc=9, id=803`. The raw log targets RCU scheduler/stall detection and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `WARNING in __ieee80211_beacon_get`, type `WARNING`, frame `none`, alternate titles none, and flags `PANICKED, EXECUTOR`. The principal kernel/user-space symbols visible to the parser are:

- `__ieee80211_beacon_get`
- `ieee80211_beacon_get_tim`
- `__pfx_ieee80211_beacon_get_tim`
- `mac80211_hwsim_beacon_tx`
- `ieee80211_iterate_active_interfaces_atomic`
- `__iterate_interfaces`
- `__pfx_mac80211_hwsim_beacon_tx`
- `mac80211_hwsim_beacon`
- `__pfx_mac80211_hwsim_beacon`
- `__hrtimer_run_queues`
- `__pfx___hrtimer_run_queues`
- `read_tsc`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `WARNING in __ieee80211_beacon_get` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 225 lines and about 14690 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- WARNING: net/mac80211/tx.c:5024 at __ieee80211_beacon_get+0x125d/0x1630, CPU#1: syz.9.803/11907
- Kernel panic - not syncing: kernel: panic_on_warn set ...

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: RCU scheduler/stall detection functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/743 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/744 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/744

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/744`. It records expected title `WARNING in dbAdjTree`; type `WARNING`; flags `PANICKED=Y`. The raw log targets JFS filesystem and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `WARNING in dbAdjTree`, type `WARNING`, frame `none`, alternate titles none, and flags `PANICKED`. The principal kernel/user-space symbols visible to the parser are:

- `dbAdjTree`
- `__pfx_lock_metapage`
- `dbJoin`
- `do_read_cache_folio`
- `dbFreeBits`
- `dbFree`
- `txFreeMap`
- `txUpdateMap`
- `jfs_lazycommit`
- `__pfx_jfs_lazycommit`
- `__pfx_default_wake_function`
- `__kthread_parkme`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `WARNING in dbAdjTree` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 113 lines and about 7069 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- WARNING: fs/jfs/jfs_dmap.c:2867 at dbAdjTree+0x454/0x4e0, CPU#0: jfsCommit/112
- Kernel panic - not syncing: kernel: panic_on_warn set ...

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: JFS filesystem functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/744 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/745 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/745

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/745`. It records expected title `WARNING in v9fs_fid_get_acl`; type `WARNING`. The raw log targets 9p/V9FS and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `WARNING in v9fs_fid_get_acl`, type `WARNING`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `__alloc_frozen_pages_noprof`
- `__warn`
- `report_bug`
- `handle_bug`
- `exc_invalid_op`
- `asm_exc_invalid_op`
- `kfree`
- `__pfx___alloc_frozen_pages_noprof`
- `v9fs_fid_xattr_get`
- `__alloc_pages_noprof`
- `___kmalloc_large_node`
- `__kmalloc_large_node_noprof`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `WARNING in v9fs_fid_get_acl` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 67 lines and about 4556 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- WARNING: CPU: 0 PID: 5830 at mm/page_alloc.c:4728 __alloc_frozen_pages_noprof+0x3c5/0x710

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: 9p/V9FS functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/745 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/746 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/746

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/746`. It records expected title `WARNING in drm_mode_create_lease_ioctl`; type `WARNING`. The raw log targets DRM ioctl and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `WARNING in drm_mode_create_lease_ioctl`, type `WARNING`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `__alloc_frozen_pages_noprof`
- `__warn`
- `report_bug`
- `handle_bug`
- `exc_invalid_op`
- `asm_exc_invalid_op`
- `drm_mode_create_lease_ioctl`
- `count_memcg_events_mm.constprop.0`
- `__pfx_lock_release`
- `find_held_lock`
- `__pfx___alloc_frozen_pages_noprof`
- `__pfx___up_read`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `WARNING in drm_mode_create_lease_ioctl` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 72 lines and about 4982 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- WARNING: CPU: 0 PID: 5936 at mm/page_alloc.c:4715 __alloc_frozen_pages_noprof+0x1f66/0x2470

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: DRM ioctl functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/746 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/747 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/747

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/747`. It records expected title `possible deadlock in fakeName`; type `LOCKDEP`; flags `EXECUTOR=proc=5, id=7376`. The raw log targets Linux crash-report parsing and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `possible deadlock in fakeName`, type `LOCKDEP`, frame `none`, alternate titles none, and flags `EXECUTOR`. The principal kernel/user-space symbols visible to the parser are:

- `lock_acquire`
- `blk_alloc_queue`
- `__blk_mq_alloc_disk`
- `nbd_dev_add`
- `nbd_init`
- `do_one_initcall`
- `do_initcall_level`
- `do_initcalls`
- `kernel_init_freeable`
- `kernel_init`
- `ret_from_fork`
- `ret_from_fork_asm`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `possible deadlock in fakeName` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 171 lines and about 10163 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- WARNING: possible circular locking dependency detected

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/747 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/748 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/748

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/748`. It records expected title `attempt to subtract with overflow in <rust_binder::process::Process>::update_ref`; primary frame `<rust_binder::process::Process>::update_ref`. The raw log targets Rust Binder and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `attempt to subtract with overflow in <rust_binder::process::Process>::update_ref`, type `none`, frame `<rust_binder::process::Process>::update_ref`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `rust_helper_BUG`
- `_RNvCscSpY9Juk0HT_7___rustc17rust_begin_unwind`
- `__cfi__RNvCscSpY9Juk0HT_7___rustc17rust_begin_unwind`
- `_RNvMs0_NtCshgDM7dBCdno_11rust_binder4nodeNtB5_4Node22update_refcount_locked`
- `__cfi__RNvXs1b_NtCs9jEwPDbx20M_4core3fmtRNtNtNtB8_5panic10panic_info9PanicInfoNtB6_7Display3fmtCs43vyB533jt3_6kernel`
- `__cfi__RNvMs0_NtCshgDM7dBCdno_11rust_binder4nodeNtB5_4Node22update_refcount_locked`
- `__kasan_check_write`
- `_raw_spin_lock`
- `__cfi__raw_spin_lock`
- `_RNvNtCs9jEwPDbx20M_4core9panicking9panic_fmt`
- `__cfi__RNvNtCs9jEwPDbx20M_4core9panicking9panic_fmt`
- `_RNvNtNtCs9jEwPDbx20M_4core9panicking11panic_const24panic_const_sub_overflow`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `attempt to subtract with overflow in <rust_binder::process::Process>::update_ref` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 142 lines and about 11576 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- rust_kernel: panicked at drivers/android/binder/node.rs:877:13:
- kernel BUG at rust/helpers/bug.c:7!
- Oops: invalid opcode: 0000 [#1] PREEMPT SMP KASAN PTI

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Rust Binder functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/748 -->
