# Research Group subset-b-009495

Grouped research for syzkaller Linux report-parser fixtures under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/649 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/649

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Negative Linux-console fixture: repeated user-space `traps:` general-protection-fault lines from `syz-executor229` must not be promoted to a kernel crash report.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: no `TITLE` header is present, so `Reporter.Parse` and `ContainsCrash` should treat this input as non-crashing. The first notable signal line in the body is `syzkaller login: [   36.852785][ T3615] traps: syz-executor229[3615] general protection fault ip:7feb96eb56a1 sp:20000fd0 error:0 in syz-executor2295634012[7feb96e75000+84000]`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 8 lines and 1050 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/649 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/65 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/65

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Soft-lockup fixture around `smp_call_function_single` and jump-label text patching, with panic-on-softlockup proving `Panicked` detection and alternate hang titles.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `BUG: soft lockup in smp_call_function`, type `HANG`, alternate titles `BUG: soft lockup in smp_call_function_single`, `stall in smp_call_function`, `stall in smp_call_function_single`, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[  247.938942] watchdog: BUG: soft lockup - CPU#0 stuck for 134s! [kworker/0:2:1400]`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 81 lines and 4744 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/65 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/650 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/650

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KASAN slab-out-of-bounds write where the noisy top access is `test_and_clear_bit`, but title extraction must choose the actionable frame `napi_hash_del`.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KASAN: slab-out-of-bounds Write in napi_hash_del`, type `KASAN-WRITE`, alternate titles `bad-access in napi_hash_del`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[   34.688750][ T2373] BUG: KASAN: slab-out-of-bounds in test_and_clear_bit+0x1a/0x25`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 120 lines and 7291 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/650 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/651 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/651

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KASAN user-memory-access read where `atomic_read` is the primitive and `skb_unref` is the report frame; it protects bad-access title normalization.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KASAN: user-memory-access Read in skb_unref`, type `KASAN-READ`, alternate titles `bad-access in skb_unref`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[   33.964872][ T2205] BUG: KASAN: user-memory-access in atomic_read+0x16/0x46`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 42 lines and 2609 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/651 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/652 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/652

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KASAN double-free wording from an older kernel, expected to normalize to `invalid-free in xt_free_table_info` despite the immediate `kvfree` frame.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KASAN: invalid-free in xt_free_table_info`, type `KASAN-INVALID-FREE`, alternate titles `invalid-free in xt_free_table_info`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  368.550228] BUG: KASAN: double-free in kvfree+0x36/0x60`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 78 lines and 4006 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/652 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/653 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/653

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Paired invalid-free variant using newer `BUG: KASAN: invalid-free` wording, checking that it maps to the same title and type as the double-free form.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KASAN: invalid-free in xt_free_table_info`, type `KASAN-INVALID-FREE`, alternate titles `invalid-free in xt_free_table_info`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  368.550228] BUG: KASAN: invalid-free in kvfree+0x36/0x60`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 78 lines and 4007 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/653 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/654 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/654

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Negative warning fixture: a framebuffer-driver console warning is intentionally benign and must not match the generic kernel WARNING crash detector.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: no `TITLE` header is present, so `Reporter.Parse` and `ContainsCrash` should treat this input as non-crashing. The first notable signal line in the body is `[   45.025191][ T3610] WARNING: fbcon: Driver 'vkmsdrmfb' missed to adjust virtual screen size (0x0 vs. 128x16)`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 17 lines and 931 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/654 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/655 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/655

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Lockdep nested-lock warning in `evict`, followed by kernel panic text, exercising lockdep title extraction and panic detection.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `WARNING: nested lock was not taken in evict`, type `LOCKDEP`, alternate titles none, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[ 1078.042081][ T3315] WARNING: Nested lock was not taken`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 70 lines and 4191 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/655 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/656 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/656

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Btrfs `kernel BUG at fs/btrfs/ctree.h` log where the relevant frame is `close_ctree` and the report panics after the oops.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `kernel BUG in close_ctree`, type `BUG`, alternate titles none, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[  399.860119][ T3629] kernel BUG at fs/btrfs/ctree.h:3615!`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 87 lines and 6791 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/656 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/657 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/657

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Lockdep nested-lock warning in `ntfs_fill_super` followed by a separate general-protection-fault, checking first-oops selection.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `WARNING: nested lock was not taken in ntfs_fill_super`, type `LOCKDEP`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  292.996890][T13544] WARNING: Nested lock was not taken`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 52 lines and 3848 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/657 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/658 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/658

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KASAN stack-out-of-bounds read from lockdep acquisition under `ntfs_fill_super`, including memory-state trailer parsing.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KASAN: stack-out-of-bounds Read in ntfs_fill_super`, type `KASAN-READ`, alternate titles `bad-access in ntfs_fill_super`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  474.463900][T13922] BUG: KASAN: stack-out-of-bounds in lock_acquire+0x1c3/0x3c0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 88 lines and 5582 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/658 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/659 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/659

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. ARM list-debug kernel BUG in `nilfs_sysfs_delete_device_group`, expected as memory-safety bug with panic-on-oops.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `BUG: corrupted list in nilfs_sysfs_delete_device_group`, type `MEMORY_SAFETY_BUG`, alternate titles `bad-access in nilfs_sysfs_delete_device_group`, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[  531.962869][ T3061] kernel BUG at lib/list_debug.c:64!`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 52 lines and 3205 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/659 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/66 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/66

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Corrupted dual-oops fixture: spinlock lockup and soft lockup appear together, so the expected report is marked corrupted.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `BUG: spinlock lockup suspected in corrupted`, type `LOCKDEP`, alternate titles none, `Panicked=N`, and `Corrupted=Y`. The first notable signal line in the body is `[   72.159680] BUG: spinlock lockup suspected on CPU#2, syz-executor/12636`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 6 lines and 228 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/66 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/660 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/660

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. syz-executor infrastructure failure, not a kernel oops, where dynamic executor numbers and temp-directory suffixes are sanitized in the title.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `SYZFATAL: executor NUM failed NUM times: failed to create temp dir: mkdir ./syzkaller-testdirNUM: read-only file system`, type `SYZ_FAILURE`, alternate titles `SYZFATAL`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `no crash-looking signal line`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 6 lines and 304 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/660 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/661 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/661

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Long KASAN slab-out-of-bounds read in JFS `ea_get`, including allocation history and panic-on-warn continuation.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KASAN: slab-out-of-bounds Read in ea_get`, type `KASAN-READ`, alternate titles `bad-access in ea_get`, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[   54.502667][ T3608] BUG: KASAN: slab-out-of-bounds in hex_dump_to_buffer+0xdc1/0xdf0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 265 lines and 15457 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/661 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/662 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/662

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. General-protection-fault title in `device_find_child` after earlier workqueue context, checking that the later real crash wins.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `general protection fault in device_find_child`, type `DoS`, alternate titles `bad-access in device_find_child`, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[   50.983422][ T3608] general protection fault, probably for non-canonical address 0xdffffc000000000b: 0000 [#1] PREEMPT SMP KASAN`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 127 lines and 8384 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/662 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/663 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/663

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Kernel stack overflow while recursing through rtnetlink link creation, expected as a DoS-style crash with stack-overflow alternate title.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `kernel stack overflow in rtnl_newlink`, type `DoS`, alternate titles `stack-overflow in rtnl_newlink`, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[ 1349.302950][    C1] Kernel panic - not syncing: kernel stack overflow`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 222 lines and 13053 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/663 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/664 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/664

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Reiserfs general-protection-fault in `reiserfs_readdir_inode`, with KASAN wild-memory-access context and panic detection.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `general protection fault in reiserfs_readdir_inode`, type `DoS`, alternate titles `bad-access in reiserfs_readdir_inode`, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[  464.245994][T13181] general protection fault, probably for non-canonical address 0xe0017c0000000006: 0000 [#1] PREEMPT SMP KASAN`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 61 lines and 4950 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/664 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/665 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/665

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Lockdep inconsistent-lock-state report in `ntfs_fill_super`, covering lock-class state reports without a subsequent panic.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `inconsistent lock state in ntfs_fill_super`, type `LOCKDEP`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[ 1336.869886][ T9712] WARNING: inconsistent lock state`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 98 lines and 5416 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/665 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/666 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/666

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Lockdep inconsistent-lock-state report in an io_uring softirq path, expected title frame `io_dismantle_req`.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `inconsistent lock state in io_dismantle_req`, type `LOCKDEP`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[   32.242183][    C0] WARNING: inconsistent lock state`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 69 lines and 4256 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/666 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/667 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/667

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Lockdep inconsistent-lock-state report in `__io_req_aux_free`, preserving the double-underscore frame name.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `inconsistent lock state in __io_req_aux_free`, type `LOCKDEP`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[   28.146298] WARNING: inconsistent lock state`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 82 lines and 4680 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/667 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/668 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/668

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Lockdep inconsistent-lock-state report in `io_file_data_ref_zero`, another io_uring lifecycle path.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `inconsistent lock state in io_file_data_ref_zero`, type `LOCKDEP`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[   21.093011][    C0] WARNING: inconsistent lock state`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 80 lines and 4843 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/668 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/669 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/669

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Duplicated lockdep inconsistent-lock-state block for `fs_reclaim_acquire`, validating report boundary handling when the same warning repeats.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `inconsistent lock state in fs_reclaim_acquire`, type `LOCKDEP`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  860.117823][    C1] WARNING: inconsistent lock state`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 175 lines and 10216 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/669 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/67 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/67

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Soft-lockup hang in `snd_pcm_oss_write` with panic-on-softlockup and sanitized syzkaller process names.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `BUG: soft lockup in snd_pcm_oss_write`, type `HANG`, alternate titles `stall in snd_pcm_oss_write`, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[  562.725743] watchdog: BUG: soft lockup - CPU#0 stuck for 135s! [syzkaller670324:3527]`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 176 lines and 9728 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/67 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/670 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/670

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Large KMSAN uninitialized-value report in APIC writes with many `Uninit was stored to memory at` sections before creation origin.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KMSAN: uninit-value in native_apic_mem_write`, type `KMSAN-UNINIT-VALUE`, alternate titles `bad-access in native_apic_mem_write`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  663.636461][    C1] BUG: KMSAN: uninit-value in native_apic_mem_write+0x6e/0x90`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 191 lines and 9927 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/670 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/671 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/671

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KMSAN uninitialized-value report in tty `flush_to_ldisc`, compact origin tracking from a created-uninit block.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KMSAN: uninit-value in flush_to_ldisc`, type `KMSAN-UNINIT-VALUE`, alternate titles `bad-access in flush_to_ldisc`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[ 1725.930075][   T52] BUG: KMSAN: uninit-value in flush_to_ldisc+0x95d/0xdf0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 38 lines and 2040 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/671 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/672 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/672

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KMSAN uninitialized-value report in `ext4_evict_inode`, covering filesystem eviction paths.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KMSAN: uninit-value in ext4_evict_inode`, type `KMSAN-UNINIT-VALUE`, alternate titles `bad-access in ext4_evict_inode`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  345.524532][ T3516] BUG: KMSAN: uninit-value in ext4_evict_inode+0xdd/0x26b0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 52 lines and 2768 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/672 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/673 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/673

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KMSAN uninitialized-value report in NILFS bmap lookup, preserving a deep filesystem helper as title frame.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KMSAN: uninit-value in nilfs_bmap_lookup_at_level`, type `KMSAN-UNINIT-VALUE`, alternate titles `bad-access in nilfs_bmap_lookup_at_level`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  231.723837][ T3795] BUG: KMSAN: uninit-value in nilfs_bmap_lookup_at_level+0x22e/0x4c0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 56 lines and 3039 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/673 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/674 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/674

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KMSAN uninitialized-value report in `ntfs_iget5`, with the fault reached through inode lookup.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KMSAN: uninit-value in ntfs_iget5`, type `KMSAN-UNINIT-VALUE`, alternate titles `bad-access in ntfs_iget5`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  493.527002][ T7865] BUG: KMSAN: uninit-value in ntfs_iget5+0x6cf/0x6510`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 47 lines and 2469 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/674 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/675 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/675

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Classic `kernel BUG at mm/slab.c` report where title extraction must use `sg_scsi_ioctl` rather than the allocator file location.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `kernel BUG in sg_scsi_ioctl`, type `BUG`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[ 1889.445218][T11163] kernel BUG at mm/slab.c:4339!`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 37 lines and 2824 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/675 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/676 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/676

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. ARM null-pointer dereference in GSM line discipline receive path, with ARM backtrace format and panic text.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `BUG: unable to handle kernel NULL pointer dereference in gsmld_receive_buf`, type `NULL-POINTER-DEREFERENCE`, alternate titles `bad-access in gsmld_receive_buf`, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[  794.202055][ T8604] Kernel panic - not syncing: Fatal exception`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 113 lines and 9216 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/676 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/677 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/677

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. ARM null-pointer dereference in NFC `nci_send_cmd`, testing ARM exception/backtrace parsing and panic detection.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `BUG: unable to handle kernel NULL pointer dereference in nci_send_cmd`, type `NULL-POINTER-DEREFERENCE`, alternate titles `bad-access in nci_send_cmd`, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[ 9171.724909][T26146] Kernel panic - not syncing: Fatal exception`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 152 lines and 12697 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/677 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/678 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/678

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Lockdep inconsistent-lock-state report in debugfs show path `sync_info_debugfs_show`.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `inconsistent lock state in sync_info_debugfs_show`, type `LOCKDEP`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  952.328681][T12429] WARNING: inconsistent lock state`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 82 lines and 5053 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/678 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/679 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/679

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Lockdep inconsistent-lock-state report in scheduler core balancing, retaining `sched_core_balance` as the important frame.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `inconsistent lock state in sched_core_balance`, type `LOCKDEP`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  124.809430][ T3879] WARNING: inconsistent lock state`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 92 lines and 5833 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/679 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/68 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/68

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Spinlock recursion report in `wake_up_new_task`, a lockdep-style bug without normal oops framing.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `BUG: spinlock recursion in wake_up_new_task`, type `LOCKDEP`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  213.269287] BUG: spinlock recursion on CPU#0, syz-executor7/5032`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 19 lines and 1184 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/68 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/680 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/680

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Paging-request memory-safety bug in `simple_xattr_alloc`, panic after fatal exception.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `BUG: unable to handle kernel paging request in simple_xattr_alloc`, type `MEMORY_SAFETY_BUG`, alternate titles `bad-access in simple_xattr_alloc`, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[   34.717898][ T3083] Kernel panic - not syncing: Oops: Fatal exception`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 74 lines and 4363 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/680 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/681 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/681

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KMSAN uninitialized-value report in network softirq transmit action `net_tx_action`.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KMSAN: uninit-value in net_tx_action`, type `KMSAN-UNINIT-VALUE`, alternate titles `bad-access in net_tx_action`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  142.148660][    C0] BUG: KMSAN: uninit-value in net_tx_action+0x77c/0x9a0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 30 lines and 1584 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/681 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/682 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/682

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KMSAN uninitialized-value report in mac80211 receive path `ieee80211_rx_list`.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KMSAN: uninit-value in ieee80211_rx_list`, type `KMSAN-UNINIT-VALUE`, alternate titles `bad-access in ieee80211_rx_list`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  338.587187][    C0] BUG: KMSAN: uninit-value in ieee80211_rx_list+0x1839/0x5860`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 46 lines and 2524 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/682 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/683 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/683

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Short VFS diagnostic `Close: file count is zero`, intentionally recognized as a DoS/use-after-free style report.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `VFS: Close: file count is zero (use-after-free)`, type `DoS`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `VFS: Close: file count is 0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 4 lines and 94 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/683 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/684 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/684

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Short VFS busy-inodes-after-unmount diagnostic, another terse VFS self-destruct warning fixture.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `VFS: Busy inodes after unmount (use-after-free)`, type `DoS`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `VFS: Busy inodes after unmount of %s. Self-destruct in 5 seconds.  Have a nice day...`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 5 lines and 153 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/684 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/685 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/685

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Negative VFS fixture: similar-looking text that should not be considered an error.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: no `TITLE` header is present, so `Reporter.Parse` and `ContainsCrash` should treat this input as non-crashing. The first notable signal line in the body is `VFS: some message that is not an error`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 2 lines and 40 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/685 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/686 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/686

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Generic WARNING title with colon form `zero-size vmalloc in bpf_check`, preserving the mm/vmalloc source location.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `WARNING: zero-size vmalloc in bpf_check`, type `WARNING`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `WARNING: CPU: 1 PID: 15973 at mm/vmalloc.c:3108 __vmalloc_node_range+0x1036/0x1300 mm/vmalloc.c:3108`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 44 lines and 2548 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/686 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/687 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/687

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. RCU stall report whose stack points to `devlink_nl_cmd_port_get_dumpit`, classified as a hang.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `INFO: rcu detected stall in devlink_nl_cmd_port_get_dumpit`, type `HANG`, alternate titles `stall in devlink_nl_cmd_port_get_dumpit`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[ 1946.223778][    C0] rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 112 lines and 7024 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/687 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/688 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/688

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. ARM64 RCU self-detected-stall report with multiple alternate titles for syscall wrapper and syscall names.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `INFO: rcu detected stall in sys_recvmmsg`, type `HANG`, alternate titles `INFO: rcu detected stall in __arm64_sys_recvmmsg`, `stall in __arm64_sys_recvmmsg`, `stall in sys_recvmmsg`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `syzkaller login: [  417.725670][    C1] rcu: INFO: rcu_sched self-detected stall on CPU`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 74 lines and 4021 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/688 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/689 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/689

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KMSAN kernel-infoleak in kernfs read iteration, exercising info-leak type classification.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KMSAN: kernel-infoleak in kernfs_fop_read_iter`, type `KMSAN-INFO-LEAK`, alternate titles `bad-access in kernfs_fop_read_iter`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  160.670618][ T5029] BUG: KMSAN: kernel-infoleak in _copy_to_iter+0x870/0x1fd0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 63 lines and 3414 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/689 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/69 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/69

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Hung-task report in `tty_ldisc_hangup`, with blocked getty task and hang alternate title.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `INFO: task hung in tty_ldisc_hangup`, type `HANG`, alternate titles `hang in tty_ldisc_hangup`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  843.240752] INFO: task getty:2986 blocked for more than 120 seconds.`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 22 lines and 1360 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/69 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/690 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/690

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KMSAN kernel-infoleak through skb datagram iterator, keeping `__skb_datagram_iter` as the selected frame.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KMSAN: kernel-infoleak in __skb_datagram_iter`, type `KMSAN-INFO-LEAK`, alternate titles `bad-access in __skb_datagram_iter`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[ 2104.503364][ T4311] BUG: KMSAN: kernel-infoleak in _copy_to_iter+0x870/0x1fd0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 57 lines and 3061 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/690 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/691 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/691

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Negative empty/noise fixture, present to ensure no crash is parsed from an effectively blank log.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: no `TITLE` header is present, so `Reporter.Parse` and `ContainsCrash` should treat this input as non-crashing. The first notable signal line in the body is `no crash-looking signal line`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 7 lines and 1498 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/691 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/692 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/692

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Hung-task report in `netdev_run_todo` with additional lockdep-disabled and call-trace noise.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `INFO: task hung in netdev_run_todo`, type `HANG`, alternate titles `hang in netdev_run_todo`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `INFO: task kworker/u4:6:5166 blocked for more than 143 seconds.`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 75 lines and 3755 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/692 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/693 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/693

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Null-pointer dereference title for compressed NTFS read path `ni_readpage_cmpr`.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `BUG: unable to handle kernel NULL pointer dereference in ni_readpage_cmpr`, type `NULL-POINTER-DEREFERENCE`, alternate titles `bad-access in ni_readpage_cmpr`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `no crash-looking signal line`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 60 lines and 3034 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/693 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/694 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/694

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KASAN out-of-bounds write in netdevsim trap work, with concurrent corrupted-stack panic noise.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KASAN: out-of-bounds Write in nsim_dev_trap_report_work`, type `KASAN-WRITE`, alternate titles `bad-access in nsim_dev_trap_report_work`, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `[  771.746713][T15335] BUG: KASAN: out-of-bounds in stack_trace_consume_entry+0x141/0x160`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 133 lines and 7772 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/694 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/695 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/695

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. ARM64 WARNING in `nfc_llcp_unregister_device`, where title extraction falls back to the warning frame rather than the fault helper.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `WARNING in nfc_llcp_unregister_device`, type `WARNING`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `WARNING: CPU: 0 PID: 6668 at arch/arm64/mm/fault.c:374 __do_kernel_fault+0x158/0x1c0 arch/arm64/mm/fault.c:374`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 47 lines and 2613 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/695 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/696 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/696

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. WARNING in `ext4_expand_extra_isize_ea` followed by a secondary KASAN invalid-free; the first warning remains the expected report.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `WARNING in ext4_expand_extra_isize_ea`, type `WARNING`, alternate titles none, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[   33.761985][ T5931] WARNING: CPU: 1 PID: 5931 at mm/slab_common.c:935 free_large_kmalloc+0x34/0x12c`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 99 lines and 6469 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/696 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/697 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/697

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. ARM zero-size-vmalloc warning in AF_XDP queue creation with panic-on-warn.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `WARNING: zero-size vmalloc in xskq_create`, type `WARNING`, alternate titles none, `Panicked=Y`, and `Corrupted=N`. The first notable signal line in the body is `WARNING: CPU: 1 PID: 2949 at mm/vmalloc.c:3132 __vmalloc_node_range+0x44c/0x584 mm/vmalloc.c:3132`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 45 lines and 2768 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/697 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/698 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/698

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KASAN use-after-free read in UDF sync path where the primitive is `crc_itu_t` but the selected frame is `udf_sync_fs`.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KASAN: use-after-free Read in udf_sync_fs`, type `KASAN-USE-AFTER-FREE-READ`, alternate titles `bad-access in udf_sync_fs`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[   54.516895][ T4991] BUG: KASAN: use-after-free in crc_itu_t+0x1d5/0x2a0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 95 lines and 5941 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/698 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/699 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/699

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KMSAN uninitialized-value report in fscrypt block encryption, including stored and created origin sections.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KMSAN: uninit-value in fscrypt_crypt_block`, type `KMSAN-UNINIT-VALUE`, alternate titles `bad-access in fscrypt_crypt_block`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  311.910990][ T5388] BUG: KMSAN: uninit-value in aes_encrypt+0x15cc/0x1db0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 93 lines and 5096 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/699 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/7 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/7

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Corrupted soft-lockup fixture with an explicit `REPORT:` override block used to compare the exact trimmed report body.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `BUG: soft lockup in corrupted`, type `HANG`, alternate titles `stall in corrupted`, `Panicked=N`, and `Corrupted=Y`. The first notable signal line in the body is `[  536.429346] NMI watchdog: BUG: soft lockup - CPU#1 stuck for 11s! [syz-executor7:16813]`. The file also contains an explicit `REPORT:` block, so the test compares the parser's trimmed report bytes against that block.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 20 lines and 958 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/7 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/70 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/70

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. Hung-task report in block-device iteration during `sync`, with `iterate_bdevs` as the selected hang frame.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `INFO: task hung in iterate_bdevs`, type `HANG`, alternate titles `hang in iterate_bdevs`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  615.391254] INFO: task syz-executor5:10045 blocked for more than 120 seconds.`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 34 lines and 1745 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/70 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/700 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/700

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KMSAN uninitialized-value report in virtqueue scatter-gather submission, with interleaved unrelated VLAN console noise.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KMSAN: uninit-value in virtqueue_add`, type `KMSAN-UNINIT-VALUE`, alternate titles `bad-access in virtqueue_add`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[  897.210960][ T1083] BUG: KMSAN: uninit-value in virtqueue_add+0x20e2/0x60f0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 51 lines and 2809 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/700 -->
