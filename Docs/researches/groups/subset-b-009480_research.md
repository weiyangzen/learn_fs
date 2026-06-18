# Research Group: subset-b-009480

This grouped report covers the exact subset-b-009480 manifest. Each source file has a separate section bounded by BEGIN/END markers for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/23 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/23

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/23`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `ASSERT FAILED: thread_resched_disable_count() > NUM`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=ASSERT FAILED: thread_resched_disable_count() > NUM.
- Notable functions observed in the report body: `crashlog_to_string`.
- Notable source locations observed in the report body: `lib/crashlog/crashlog.cpp:131`.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 39 lines and 2292 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected title `ASSERT FAILED: thread_resched_disable_count() > NUM`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: ASSERT FAILED: thread_resched_disable_count() > NUM`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/23 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/25 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/25

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/25`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `ASSERT FAILED in size_to_index_helper`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=ASSERT FAILED in size_to_index_helper.
- Notable functions observed in the report body: `platform_halt`, `_panic`, `size_to_index_helper`, `size_to_index_freeing`, `create_free_area`, `cmpct_alloc`, `malloc`, `new`.
- Notable source locations observed in the report body: `platform/pc/power.cpp:122`, `lib/debug/debug.cpp:39`, `lib/heap/cmpctmalloc/cmpctmalloc.c:290`, `lib/heap/cmpctmalloc/cmpctmalloc.c:254`, `lib/heap/cmpctmalloc/cmpctmalloc.c:303`, `lib/heap/cmpctmalloc/cmpctmalloc.c:358`, `lib/heap/cmpctmalloc/cmpctmalloc.c:943`, `lib/heap/heap_wrapper.cpp:55`.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 76 lines and 4699 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected title `ASSERT FAILED in size_to_index_helper`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: ASSERT FAILED in size_to_index_helper`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/25 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/26 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/26

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/26`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `ASSERT FAILED in VmPageListNode::~VmPageListNode`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=ASSERT FAILED in VmPageListNode::~VmPageListNode.
- Notable functions observed in the report body: `platform_halt`, `_panic`, `VmPageListNode::~VmPageListNode`, `fbl::unique_ptr::recycle`, `fbl::unique_ptr::reset`, `fbl::WAVLTree::clear`, `VmPageList::FreeAllPages`, `VmObjectPaged::~VmObjectPaged`.
- Notable source locations observed in the report body: `platform/pc/power.cpp:122`, `lib/debug/debug.cpp:40`, `vm/vm_page_list.cpp:31`, `system/ulib/fbl/include/fbl/unique_ptr.h:125`, `system/ulib/fbl/include/fbl/unique_ptr.h:65`, `system/ulib/fbl/include/fbl/intrusive_wavl_tree.h:391`, `vm/vm_page_list.cpp:170`, `system/ulib/fbl/include/fbl/ref_counted_internal.h:119`.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 31 lines and 2128 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected title `ASSERT FAILED in VmPageListNode::~VmPageListNode`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: ASSERT FAILED in VmPageListNode::~VmPageListNode`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/26 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/27 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/27

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/27`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `panic: not implemented`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=panic: not implemented, TYPE=DoS.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 24 lines and 1800 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected title `panic: not implemented`, expected type `DoS`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: not implemented`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/27 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/28 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/28

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/28`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `panic: payload too small`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=panic: payload too small, TYPE=DoS.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 32 lines and 2647 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected title `panic: payload too small`, expected type `DoS`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: payload too small`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/28 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/29 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/29

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/29`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `panic: runtime error: slice bounds out of range`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=panic: runtime error: slice bounds out of range, TYPE=DoS.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 20 lines and 1372 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected title `panic: runtime error: slice bounds out of range`, expected type `DoS`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: runtime error: slice bounds out of range`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/29 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/3 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/3

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/3`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `ASSERT FAILED: wait->magic == WAIT_QUEUE_MAGIC`.
It also carries an explicit `REPORT:` block, so the test checks the exact shortened report body after `fuchsia.Parse` symbolization, `simpleLineParser`, and Fuchsia-specific report trimming.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=ASSERT FAILED: wait->magic == WAIT_QUEUE_MAGIC.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 20 lines and 704 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 3 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected title `ASSERT FAILED: wait->magic == WAIT_QUEUE_MAGIC`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: ASSERT FAILED: wait->magic == WAIT_QUEUE_MAGIC`.
- Expected report begins with: `ZIRCON KERNEL PANIC`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/3 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/30 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/30

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/30`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `unexpected kernel reboot`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=unexpected kernel reboot, TYPE=REBOOT, START=[00000.000] 00000.00000> welcome to Zircon.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 23 lines and 1260 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.
- Unexpected reboot detection is boundary-sensitive because it keys off boot banner output rather than a conventional panic stack.

## Test Signals
- Primary signal: expected title `unexpected kernel reboot`, expected type `REBOOT`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: unexpected kernel reboot`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/30 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/4 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/4

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/4`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `recursion in interrupt handler`.
It also carries an explicit `REPORT:` block, so the test checks the exact shortened report body after `fuchsia.Parse` symbolization, `simpleLineParser`, and Fuchsia-specific report trimming.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=recursion in interrupt handler.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 17 lines and 494 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 2 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected title `recursion in interrupt handler`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: recursion in interrupt handler`.
- Expected report begins with: `recursion in interrupt handler`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/4 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/5 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/5

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/5`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `recursion in interrupt handler in fillrect16`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=recursion in interrupt handler in fillrect16.
- Notable functions observed in the report body: `fillrect16`.
- Notable source locations observed in the report body: `lib/gfx/gfx.c:289`.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 10 lines and 362 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected title `recursion in interrupt handler in fillrect16`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: recursion in interrupt handler in fillrect16`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/5 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/6 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/6

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/6`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `KERNEL PANIC in corrupted`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=KERNEL PANIC in corrupted, CORRUPTED=Y, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 53 lines and 4530 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.
- The fixture explicitly expects corruption handling, so relaxed stack validation could turn a suppressed corrupted report into a false positive.

## Test Signals
- Primary signal: expected title `KERNEL PANIC in corrupted`, expected suppression, expected corruption.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `ZIRCON KERNEL PANIC`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/6 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/7 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/7

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/7`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `double fault`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=double fault.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 22 lines and 863 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected title `double fault`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: double fault`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/7 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/8 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/8

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/8`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `fatal exception in fshost`.
It also carries an explicit `REPORT:` block, so the test checks the exact shortened report body after `fuchsia.Parse` symbolization, `simpleLineParser`, and Fuchsia-specific report trimming.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=fatal exception in fshost.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 94 lines and 7509 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 40 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected title `fatal exception in fshost`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: fatal exception in fshost`.
- Expected report begins with: `<== fatal exception: process fshost[1127] thread root-dispatcher[1246]`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/8 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/9 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/9

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/9`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `<no crash expected>`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: this input intentionally has no `TITLE:`/`FILE:` header; the paired test derives behavior from the parsed Linux crash and `.out` golden output.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 33 lines and 2946 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected no title/crash header.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `[00046.694] 01102.01116> <== fatal exception: process /tmp/syz-executor14[143530] thread initial-thread[143565]`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/9 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/0 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/0

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/0`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: runtime error: invalid memory address or nil pointer dereference`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: runtime error: invalid memory address or nil pointer dereference, TYPE=DoS.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 124 lines and 11221 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 44 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `panic: runtime error: invalid memory address or nil pointer dereference`, expected type `DoS`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: runtime error: invalid memory address or nil pointer dereference`.
- Expected report begins with: `panic: runtime error: invalid memory address or nil pointer dereference`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/1 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/1

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/1`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: MountNamespace.FindInode: path is empty`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: MountNamespace.FindInode: path is empty, TYPE=DoS.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 106 lines and 9534 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 35 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `panic: MountNamespace.FindInode: path is empty`, expected type `DoS`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: MountNamespace.FindInode: path is empty`.
- Expected report begins with: `panic: MountNamespace.FindInode: path is empty`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/1 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/10 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/10

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/10`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `FATAL ERROR: error running container: err waiting on container NAME: EOF`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=FATAL ERROR: error running container: err waiting on container NAME: EOF.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 9 lines and 785 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `FATAL ERROR: error running container: err waiting on container NAME: EOF`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: FATAL ERROR: error running container: err waiting on container NAME: EOF`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/10 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/11 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/11

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/11`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `FATAL ERROR: error getting processes for container: error executing in sandbox: EOF`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=FATAL ERROR: error getting processes for container: error executing in sandbox: EOF.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 9 lines and 573 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `FATAL ERROR: error getting processes for container: error executing in sandbox: EOF`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: FATAL ERROR: error getting processes for container: error executing in sandbox: EOF`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/11 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/12 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/12

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/12`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `SIGSEGV: segmentation violation`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=SIGSEGV: segmentation violation.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 18 lines and 1391 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `SIGSEGV: segmentation violation`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: SIGSEGV: segmentation violation`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/12 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/13 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/13

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/13`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `FATAL ERROR: error getting processes for container: error executing in sandbox: EOF`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=FATAL ERROR: error getting processes for container: error executing in sandbox: EOF, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 12 lines and 839 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `FATAL ERROR: error getting processes for container: error executing in sandbox: EOF`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: FATAL ERROR: error getting processes for container: error executing in sandbox: EOF`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/13 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/14 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/14

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/14`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: ptrace sysemu failed: no such process`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: ptrace sysemu failed: no such process, TYPE=DoS, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 17 lines and 983 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `panic: ptrace sysemu failed: no such process`, expected type `DoS`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: ptrace sysemu failed: no such process`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/14 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/15 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/15

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/15`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `Invalid request partialResult in sendfile`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=Invalid request partialResult in sendfile.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 26 lines and 2124 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `Invalid request partialResult in sendfile`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: Invalid request partialResult in sendfile`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/15 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/16 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/16

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/16`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: error mapping run data: error mapping runData: cannot allocate memory`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: error mapping run data: error mapping runData: cannot allocate memory, TYPE=DoS, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 19 lines and 1157 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `panic: error mapping run data: error mapping runData: cannot allocate memory`, expected type `DoS`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: error mapping run data: error mapping runData: cannot allocate memory`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/16 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/17 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/17

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/17`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: ptrace set fpregs (ADDR) failed: no such process`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: ptrace set fpregs (ADDR) failed: no such process, TYPE=DoS, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 17 lines and 988 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `panic: ptrace set fpregs (ADDR) failed: no such process`, expected type `DoS`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: ptrace set fpregs (ADDR) failed: no such process`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/17 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/18 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/18

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/18`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `FATAL ERROR: error waiting on pid X: error waiting on pid X in sandbox NAME failed: EOF`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=FATAL ERROR: error waiting on pid X: error waiting on pid X in sandbox NAME failed: EOF.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 6 lines and 726 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `FATAL ERROR: error waiting on pid X: error waiting on pid X in sandbox NAME failed: EOF`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: FATAL ERROR: error waiting on pid X: error waiting on pid X in sandbox NAME failed: EOF`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/18 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/19 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/19

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/19`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: ptrace set regs failed: no such process`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: ptrace set regs failed: no such process, TYPE=DoS, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 17 lines and 1051 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `panic: ptrace set regs failed: no such process`, expected type `DoS`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: ptrace set regs failed: no such process`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/19 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/2 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/2

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/2`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: ptrace set regs (&{R15:NUM R14:NUM R13:NUM R12:NUM Rbp:ADDR Rbx:ADDR R11:NUM R10:NUM R9:NUM R8:NUM Rax:NUM Rcx:AD`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: ptrace set regs (&{R15:NUM R14:NUM R13:NUM R12:NUM Rbp:ADDR Rbx:ADDR R11:NUM R10:NUM R9:NUM R8:NUM Rax:NUM Rcx:AD, TYPE=DoS, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 52 lines and 3662 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 13 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `panic: ptrace set regs (&{R15:NUM R14:NUM R13:NUM R12:NUM Rbp:ADDR Rbx:ADDR R11:NUM R10:NUM R9:NUM R8:NUM Rax:NUM Rcx:AD`, expected type `DoS`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: ptrace set regs (&{R15:NUM R14:NUM R13:NUM R12:NUM Rbp:ADDR Rbx:ADDR R11:NUM R10:NUM R9:NUM R8:NUM Rax:NUM Rcx:AD`.
- Expected report begins with: `panic: ptrace set regs (&{R15:512 R14:218 R13:219 R12:32 Rbp:139868397907264 Rbx:50432192 R11:646 R10:0 R9:0 R8:0 Rax:0 Rcx:4567363 Rdx:842350500544 Rsi:842350500848 Rdi:17 Orig_rax:202 Rip:4566688 Cs:51 Eflags:646 Rsp:8`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/20 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/20

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/20`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: error initializing first thread: resource temporarily unavailable`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: error initializing first thread: resource temporarily unavailable, TYPE=DoS, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 11 lines and 517 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `panic: error initializing first thread: resource temporarily unavailable`, expected type `DoS`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: error initializing first thread: resource temporarily unavailable`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/20 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/21 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/21

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/21`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `fatal error: newosproc`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=fatal error: newosproc, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 11 lines and 704 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `fatal error: newosproc`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: fatal error: newosproc`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/21 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/22 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/22

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/22`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: ptrace get fpregs failed: no such process`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: ptrace get fpregs failed: no such process, TYPE=DoS, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 17 lines and 998 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `panic: ptrace get fpregs failed: no such process`, expected type `DoS`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: ptrace get fpregs failed: no such process`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/22 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/23 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/23

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/23`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: ptrace get regs failed: no such process`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: ptrace get regs failed: no such process, TYPE=DoS, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 18 lines and 995 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `panic: ptrace get regs failed: no such process`, expected type `DoS`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: ptrace get regs failed: no such process`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/23 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/24 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/24

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/24`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: unable to activate mm: creating stub process: resource temporarily unavailable`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: unable to activate mm: creating stub process: resource temporarily unavailable, TYPE=DoS, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 14 lines and 560 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `panic: unable to activate mm: creating stub process: resource temporarily unavailable`, expected type `DoS`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: unable to activate mm: creating stub process: resource temporarily unavailable`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/24 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/25 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/25

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/25`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: Sentry detected stuck tasks`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: Sentry detected stuck tasks, TYPE=DoS.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 67 lines and 4774 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `panic: Sentry detected stuck tasks`, expected type `DoS`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: Sentry detected stuck tasks`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/25 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/26 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/26

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/26`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: Sentry detected stuck tasks`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: Sentry detected stuck tasks, TYPE=DoS.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 68 lines and 4874 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `panic: Sentry detected stuck tasks`, expected type `DoS`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: Sentry detected stuck tasks`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/26 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/27 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/27

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/27`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: header.ScopeForIPv6Address(IP): bad address`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: header.ScopeForIPv6Address(IP): bad address, TYPE=DoS.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 46 lines and 4262 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `panic: header.ScopeForIPv6Address(IP): bad address`, expected type `DoS`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: header.ScopeForIPv6Address(IP): bad address`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/27 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/28 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/28

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/28`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `FATAL ERROR: waiting on pid X: waiting on pid X in sandbox NAME failed: EOF`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=FATAL ERROR: waiting on pid X: waiting on pid X in sandbox NAME failed: EOF, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 38 lines and 4158 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `FATAL ERROR: waiting on pid X: waiting on pid X in sandbox NAME failed: EOF`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: FATAL ERROR: waiting on pid X: waiting on pid X in sandbox NAME failed: EOF`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/28 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/29 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/29

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/29`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `fatal error: out of memory`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=fatal error: out of memory, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 15 lines and 548 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `fatal error: out of memory`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: fatal error: out of memory`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/29 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/3 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/3

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/3`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: Decrementing non-positive ref count`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: Decrementing non-positive ref count, TYPE=DoS.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 93 lines and 7266 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 29 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `panic: Decrementing non-positive ref count`, expected type `DoS`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: Decrementing non-positive ref count`.
- Expected report begins with: `panic: Decrementing non-positive ref count`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/3 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/4 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/4

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/4`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: munmap(ADDR, NUM)) failed: invalid argument`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: munmap(ADDR, NUM)) failed: invalid argument, TYPE=DoS.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 98 lines and 8631 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 31 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `panic: munmap(ADDR, NUM)) failed: invalid argument`, expected type `DoS`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: munmap(ADDR, NUM)) failed: invalid argument`.
- Expected report begins with: `panic: munmap(2000d000, 0)) failed: invalid argument`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/4 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/5 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/5

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/5`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: invalid segment range [ADDR, ADDR)`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: invalid segment range [ADDR, ADDR), TYPE=DoS.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 54 lines and 4298 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `panic: invalid segment range [ADDR, ADDR)`, expected type `DoS`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: invalid segment range [ADDR, ADDR)`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/5 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/6 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/6

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/6`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `DATA RACE in waiter.(*Entry).Next`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=DATA RACE in waiter.(*Entry).Next.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 165 lines and 9339 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 56 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- Data-race reports require preserving both racing stacks, unlike ordinary panic truncation.

## Test Signals
- Primary signal: expected title `DATA RACE in waiter.(*Entry).Next`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `WARNING: DATA RACE`.
- Expected report begins with: `WARNING: DATA RACE`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/6 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/7 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/7

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/7`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `DATA RACE in mm.(*MemoryManager).internalMappingsLocked`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=DATA RACE in mm.(*MemoryManager).internalMappingsLocked.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 169 lines and 9605 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 56 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- Data-race reports require preserving both racing stacks, unlike ordinary panic truncation.

## Test Signals
- Primary signal: expected title `DATA RACE in mm.(*MemoryManager).internalMappingsLocked`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `WARNING: DATA RACE`.
- Expected report begins with: `WARNING: DATA RACE`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/7 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/8 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/8

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/8`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `DATA RACE in mm.(*pmaSet).Find`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=DATA RACE in mm.(*pmaSet).Find.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 170 lines and 9639 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 62 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- Data-race reports require preserving both racing stacks, unlike ordinary panic truncation.

## Test Signals
- Primary signal: expected title `DATA RACE in mm.(*pmaSet).Find`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `WARNING: DATA RACE`.
- Expected report begins with: `WARNING: DATA RACE`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/8 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/9 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/9

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/9`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `DATA RACE in kernel.(*Task).accountTaskGoroutineEnter`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=DATA RACE in kernel.(*Task).accountTaskGoroutineEnter.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 96 lines and 4935 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 24 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- Data-race reports require preserving both racing stacks, unlike ordinary panic truncation.

## Test Signals
- Primary signal: expected title `DATA RACE in kernel.(*Task).accountTaskGoroutineEnter`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `WARNING: DATA RACE`.
- Expected report begins with: `WARNING: DATA RACE`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/9 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/0.in -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/0.in

## Purpose
This fixture is a Linux opcode decompilation input for architecture `amd64`. `TestDisassemblyInReports` parses the crash, invokes `linux.decompileOpcodes`, and compares the transformed report with the sibling `.out` golden file.
The input provides a real kernel report with one or more `Code:` byte streams and a marked faulting opcode, exercising `parseOpcodes`, target-aware objdump invocation, instruction alignment, and decompiled snippet insertion.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestDisassemblyInReports`, `testDisassembly`, `linux.decompileOpcodes`, `linux.processOpcodes`, `linux.decompileWithOffset`, `DecompileOpcodes`, `objdumpParseOutput`.
- Fixture metadata: this input intentionally has no `TITLE:`/`FILE:` header; the paired test derives behavior from the parsed Linux crash and `.out` golden output.
- Notable functions observed in the report body: `at`, `__device_add_disk`, `add_disk`, `md_alloc`, `md_probe`, `blk_request_module`, `blkdev_get_no_open`, `blkdev_get_by_dev.part.0`.
- Notable source locations observed in the report body: `block/genhd.c:523`, `include/linux/genhd.h:217`, `drivers/md/md.c:5707`, `drivers/md/md.c:5738`, `block/genhd.c:660`, `fs/block_dev.c:1332`, `fs/block_dev.c:1395`, `fs/block_dev.c:1448`.
- Opcode material: 2 `Code:` line(s), with 2 marked trapping opcode marker(s).

## Control Flow
- `TestDisassemblyInReports` selects this `.in` file by architecture, builds the matching Linux reporter, parses the crash, then passes both the raw input and parsed `Report` into `decompileOpcodes`.
- `decompileOpcodes` scans all `Code:` lines, tries to parse byte streams with a `<...>` trapping byte marker, decompiles with the architecture target, aligns instructions around the faulting offset, and appends the disassembly to the bottom of the report.

## State And Persistence
- Static fixture only: 48 lines and 2963 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Linux reporter for `amd64`, target metadata from `sys/targets`, objdump-compatible decompilation helpers, and the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/0.out`. The test is skipped outside Linux hosts or when the target compiler/decompiler is marked broken.

## Risks And Edge Cases
- Opcode parsing is architecture-sensitive; byte order, Thumb mode, fault marker placement, and objdump output formatting can all change expected `.out` text.

## Test Signals
- Primary signal: parsed Linux crash plus decompiled output must match the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/0.out` byte-for-byte.
- Regression signal: `go test ./pkg/report -run TestDisassemblyInReports` on a Linux host should keep the appended decompiled instruction block stable for this architecture.

## Source-Specific Observations
- First crash/log signal: `WARNING: CPU: 0 PID: 2468 at block/genhd.c:523 __device_add_disk+0xb76/0xd10 block/genhd.c:523`.
- Architecture lane `amd64` makes this input sensitive to target-specific decompiler flags and instruction-width assumptions.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/0.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/1.in -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/1.in

## Purpose
This fixture is a Linux opcode decompilation input for architecture `amd64`. `TestDisassemblyInReports` parses the crash, invokes `linux.decompileOpcodes`, and compares the transformed report with the sibling `.out` golden file.
The input provides a real kernel report with one or more `Code:` byte streams and a marked faulting opcode, exercising `parseOpcodes`, target-aware objdump invocation, instruction alignment, and decompiled snippet insertion.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestDisassemblyInReports`, `testDisassembly`, `linux.decompileOpcodes`, `linux.processOpcodes`, `linux.decompileWithOffset`, `DecompileOpcodes`, `objdumpParseOutput`.
- Fixture metadata: this input intentionally has no `TITLE:`/`FILE:` header; the paired test derives behavior from the parsed Linux crash and `.out` golden output.
- Opcode material: 1 `Code:` line(s), with 0 marked trapping opcode marker(s).

## Control Flow
- `TestDisassemblyInReports` selects this `.in` file by architecture, builds the matching Linux reporter, parses the crash, then passes both the raw input and parsed `Report` into `decompileOpcodes`.
- `decompileOpcodes` scans all `Code:` lines, tries to parse byte streams with a `<...>` trapping byte marker, decompiles with the architecture target, aligns instructions around the faulting offset, and appends the disassembly to the bottom of the report.

## State And Persistence
- Static fixture only: 20 lines and 1176 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Linux reporter for `amd64`, target metadata from `sys/targets`, objdump-compatible decompilation helpers, and the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/1.out`. The test is skipped outside Linux hosts or when the target compiler/decompiler is marked broken.

## Risks And Edge Cases
- Opcode parsing is architecture-sensitive; byte order, Thumb mode, fault marker placement, and objdump output formatting can all change expected `.out` text.

## Test Signals
- Primary signal: parsed Linux crash plus decompiled output must match the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/1.out` byte-for-byte.
- Regression signal: `go test ./pkg/report -run TestDisassemblyInReports` on a Linux host should keep the appended decompiled instruction block stable for this architecture.

## Source-Specific Observations
- First crash/log signal: `BUG: kernel NULL pointer dereference, address: 0000000000000000`.
- Architecture lane `amd64` makes this input sensitive to target-specific decompiler flags and instruction-width assumptions.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/1.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/2.in -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/2.in

## Purpose
This fixture is a Linux opcode decompilation input for architecture `amd64`. `TestDisassemblyInReports` parses the crash, invokes `linux.decompileOpcodes`, and compares the transformed report with the sibling `.out` golden file.
The input provides a real kernel report with one or more `Code:` byte streams and a marked faulting opcode, exercising `parseOpcodes`, target-aware objdump invocation, instruction alignment, and decompiled snippet insertion.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestDisassemblyInReports`, `testDisassembly`, `linux.decompileOpcodes`, `linux.processOpcodes`, `linux.decompileWithOffset`, `DecompileOpcodes`, `objdumpParseOutput`.
- Fixture metadata: this input intentionally has no `TITLE:`/`FILE:` header; the paired test derives behavior from the parsed Linux crash and `.out` golden output.
- Notable functions observed in the report body: `context_switch`, `__schedule`, `schedule`, `schedule_timeout`, `rcu_gp_fqs_loop`, `rcu_gp_kthread`, `kthread`, `ret_from_fork`.
- Notable source locations observed in the report body: `kernel/sched/core.c:4683`, `kernel/sched/core.c:5940`, `kernel/sched/core.c:6019`, `kernel/time/timer.c:1878`, `kernel/rcu/tree.c:1996`, `kernel/rcu/tree.c:2169`, `kernel/kthread.c:319`, `arch/x86/entry/entry_64.S:295`.
- Opcode material: 4 `Code:` line(s), with 4 marked trapping opcode marker(s).

## Control Flow
- `TestDisassemblyInReports` selects this `.in` file by architecture, builds the matching Linux reporter, parses the crash, then passes both the raw input and parsed `Report` into `decompileOpcodes`.
- `decompileOpcodes` scans all `Code:` lines, tries to parse byte streams with a `<...>` trapping byte marker, decompiles with the architecture target, aligns instructions around the faulting offset, and appends the disassembly to the bottom of the report.

## State And Persistence
- Static fixture only: 164 lines and 9889 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Linux reporter for `amd64`, target metadata from `sys/targets`, objdump-compatible decompilation helpers, and the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/2.out`. The test is skipped outside Linux hosts or when the target compiler/decompiler is marked broken.

## Risks And Edge Cases
- Opcode parsing is architecture-sensitive; byte order, Thumb mode, fault marker placement, and objdump output formatting can all change expected `.out` text.

## Test Signals
- Primary signal: parsed Linux crash plus decompiled output must match the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/2.out` byte-for-byte.
- Regression signal: `go test ./pkg/report -run TestDisassemblyInReports` on a Linux host should keep the appended decompiled instruction block stable for this architecture.

## Source-Specific Observations
- First crash/log signal: `rcu: INFO: rcu_preempt self-detected stall on CPU`.
- Architecture lane `amd64` makes this input sensitive to target-specific decompiler flags and instruction-width assumptions.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/2.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/3.in -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/3.in

## Purpose
This fixture is a Linux opcode decompilation input for architecture `amd64`. `TestDisassemblyInReports` parses the crash, invokes `linux.decompileOpcodes`, and compares the transformed report with the sibling `.out` golden file.
The input provides a real kernel report with one or more `Code:` byte streams and a marked faulting opcode, exercising `parseOpcodes`, target-aware objdump invocation, instruction alignment, and decompiled snippet insertion.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestDisassemblyInReports`, `testDisassembly`, `linux.decompileOpcodes`, `linux.processOpcodes`, `linux.decompileWithOffset`, `DecompileOpcodes`, `objdumpParseOutput`.
- Fixture metadata: this input intentionally has no `TITLE:`/`FILE:` header; the paired test derives behavior from the parsed Linux crash and `.out` golden output.
- Notable functions observed in the report body: `at`, `__dump_stack`, `dump_stack_lvl`, `ccid3_first_li.cold`, `tfrc_lh_interval_add`, `tfrc_rx_handle_loss`, `ccid3_hc_rx_packet_recv`, `ccid_hc_rx_packet_recv`.
- Notable source locations observed in the report body: `net/dccp/ccids/ccid3.c:691`, `lib/dump_stack.c:88`, `lib/dump_stack.c:105`, `net/dccp/ccids/lib/loss_interval.c:157`, `net/dccp/ccids/lib/packet_history.c:328`, `net/dccp/ccids/ccid3.c:744`, `net/dccp/ccid.h:182`, `net/dccp/input.c:176`.
- Opcode material: 1 `Code:` line(s), with 1 marked trapping opcode marker(s).

## Control Flow
- `TestDisassemblyInReports` selects this `.in` file by architecture, builds the matching Linux reporter, parses the crash, then passes both the raw input and parsed `Report` into `decompileOpcodes`.
- `decompileOpcodes` scans all `Code:` lines, tries to parse byte streams with a `<...>` trapping byte marker, decompiles with the architecture target, aligns instructions around the faulting offset, and appends the disassembly to the bottom of the report.

## State And Persistence
- Static fixture only: 50 lines and 2845 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Linux reporter for `amd64`, target metadata from `sys/targets`, objdump-compatible decompilation helpers, and the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/3.out`. The test is skipped outside Linux hosts or when the target compiler/decompiler is marked broken.

## Risks And Edge Cases
- Opcode parsing is architecture-sensitive; byte order, Thumb mode, fault marker placement, and objdump output formatting can all change expected `.out` text.

## Test Signals
- Primary signal: parsed Linux crash plus decompiled output must match the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/3.out` byte-for-byte.
- Regression signal: `go test ./pkg/report -run TestDisassemblyInReports` on a Linux host should keep the appended decompiled instruction block stable for this architecture.

## Source-Specific Observations
- First crash/log signal: `BUG: stored value of X_recv is zero at net/dccp/ccids/ccid3.c:691/ccid3_first_li()`.
- Architecture lane `amd64` makes this input sensitive to target-specific decompiler flags and instruction-width assumptions.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/3.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/4.in -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/4.in

## Purpose
This fixture is a Linux opcode decompilation input for architecture `amd64`. `TestDisassemblyInReports` parses the crash, invokes `linux.decompileOpcodes`, and compares the transformed report with the sibling `.out` golden file.
The input provides a real kernel report with one or more `Code:` byte streams and a marked faulting opcode, exercising `parseOpcodes`, target-aware objdump invocation, instruction alignment, and decompiled snippet insertion.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestDisassemblyInReports`, `testDisassembly`, `linux.decompileOpcodes`, `linux.processOpcodes`, `linux.decompileWithOffset`, `DecompileOpcodes`, `objdumpParseOutput`.
- Fixture metadata: this input intentionally has no `TITLE:`/`FILE:` header; the paired test derives behavior from the parsed Linux crash and `.out` golden output.
- Notable functions observed in the report body: `snd_pcm_lib_ioctl_fifo_size`, `snd_pcm_lib_ioctl`, `snd_pcm_ops_ioctl`, `fixup_unreferenced_params`, `snd_pcm_hw_refine_old_user`, `snd_pcm_common_ioctl`, `snd_pcm_ioctl`, `vfs_ioctl`.
- Notable source locations observed in the report body: `sound/core/pcm_lib.c:1739`, `sound/core/pcm_lib.c:1764`, `sound/core/pcm_native.c:196`, `sound/core/pcm_native.c:471`, `sound/core/pcm_native.c:3700`, `sound/core/pcm_native.c:3036`, `sound/core/pcm_native.c:3073`, `fs/ioctl.c:47`.
- Opcode material: 3 `Code:` line(s), with 3 marked trapping opcode marker(s).

## Control Flow
- `TestDisassemblyInReports` selects this `.in` file by architecture, builds the matching Linux reporter, parses the crash, then passes both the raw input and parsed `Report` into `decompileOpcodes`.
- `decompileOpcodes` scans all `Code:` lines, tries to parse byte streams with a `<...>` trapping byte marker, decompiles with the architecture target, aligns instructions around the faulting offset, and appends the disassembly to the bottom of the report.

## State And Persistence
- Static fixture only: 55 lines and 3630 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Linux reporter for `amd64`, target metadata from `sys/targets`, objdump-compatible decompilation helpers, and the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/4.out`. The test is skipped outside Linux hosts or when the target compiler/decompiler is marked broken.

## Risks And Edge Cases
- Opcode parsing is architecture-sensitive; byte order, Thumb mode, fault marker placement, and objdump output formatting can all change expected `.out` text.

## Test Signals
- Primary signal: parsed Linux crash plus decompiled output must match the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/4.out` byte-for-byte.
- Regression signal: `go test ./pkg/report -run TestDisassemblyInReports` on a Linux host should keep the appended decompiled instruction block stable for this architecture.

## Source-Specific Observations
- First crash/log signal: `divide error: 0000 [#1] PREEMPT SMP KASAN`.
- Architecture lane `amd64` makes this input sensitive to target-specific decompiler flags and instruction-width assumptions.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/amd64/4.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm/0.in -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm/0.in

## Purpose
This fixture is a Linux opcode decompilation input for architecture `arm`. `TestDisassemblyInReports` parses the crash, invokes `linux.decompileOpcodes`, and compares the transformed report with the sibling `.out` golden file.
The input provides a real kernel report with one or more `Code:` byte streams and a marked faulting opcode, exercising `parseOpcodes`, target-aware objdump invocation, instruction alignment, and decompiled snippet insertion.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestDisassemblyInReports`, `testDisassembly`, `linux.decompileOpcodes`, `linux.processOpcodes`, `linux.decompileWithOffset`, `DecompileOpcodes`, `objdumpParseOutput`.
- Fixture metadata: this input intentionally has no `TITLE:`/`FILE:` header; the paired test derives behavior from the parsed Linux crash and `.out` golden output.
- Notable functions observed in the report body: `__raw_writel`, `bitfill_aligned`, `sys_fillrect`, `drm_fb_helper_sys_fillrect`, `drm_fbdev_fb_fillrect`, `bit_clear_margins`, `fbcon_clear_margins`, `fbcon_switch`.
- Notable source locations observed in the report body: `arch/arm/include/asm/io.h:95`, `drivers/video/fbdev/core/cfbfillrect.c:65`, `drivers/video/fbdev/core/cfbfillrect.c:35`, `drivers/video/fbdev/core/cfbfillrect.c:62`, `drivers/video/fbdev/core/sysfillrect.c:291`, `drivers/gpu/drm/drm_fb_helper.c:764`, `drivers/gpu/drm/drm_fb_helper.c:2258`, `drivers/video/fbdev/core/bitblit.c:232`.
- Opcode material: 1 `Code:` line(s), with 0 marked trapping opcode marker(s).

## Control Flow
- `TestDisassemblyInReports` selects this `.in` file by architecture, builds the matching Linux reporter, parses the crash, then passes both the raw input and parsed `Report` into `decompileOpcodes`.
- `decompileOpcodes` scans all `Code:` lines, tries to parse byte streams with a `<...>` trapping byte marker, decompiles with the architecture target, aligns instructions around the faulting offset, and appends the disassembly to the bottom of the report.

## State And Persistence
- Static fixture only: 108 lines and 7487 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Linux reporter for `arm`, target metadata from `sys/targets`, objdump-compatible decompilation helpers, and the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm/0.out`. The test is skipped outside Linux hosts or when the target compiler/decompiler is marked broken.

## Risks And Edge Cases
- Opcode parsing is architecture-sensitive; byte order, Thumb mode, fault marker placement, and objdump output formatting can all change expected `.out` text.

## Test Signals
- Primary signal: parsed Linux crash plus decompiled output must match the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm/0.out` byte-for-byte.
- Regression signal: `go test ./pkg/report -run TestDisassemblyInReports` on a Linux host should keep the appended decompiled instruction block stable for this architecture.

## Source-Specific Observations
- First crash/log signal: `Internal error: Oops: a07 [#1] PREEMPT SMP ARM`.
- Architecture lane `arm` makes this input sensitive to target-specific decompiler flags and instruction-width assumptions.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm/0.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm64/0.in -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm64/0.in

## Purpose
This fixture is a Linux opcode decompilation input for architecture `arm64`. `TestDisassemblyInReports` parses the crash, invokes `linux.decompileOpcodes`, and compares the transformed report with the sibling `.out` golden file.
The input provides a real kernel report with one or more `Code:` byte streams and a marked faulting opcode, exercising `parseOpcodes`, target-aware objdump invocation, instruction alignment, and decompiled snippet insertion.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestDisassemblyInReports`, `testDisassembly`, `linux.decompileOpcodes`, `linux.processOpcodes`, `linux.decompileWithOffset`, `DecompileOpcodes`, `objdumpParseOutput`.
- Fixture metadata: this input intentionally has no `TITLE:`/`FILE:` header; the paired test derives behavior from the parsed Linux crash and `.out` golden output.
- Notable functions observed in the report body: `at`, `free_image_page`, `free_list_of_pages`, `memory_bm_free`, `free_basic_memory_bitmaps`, `snapshot_release`, `__fput`, `____fput`.
- Notable source locations observed in the report body: `kernel/power/snapshot.c:257`, `kernel/power/snapshot.c:253`, `kernel/power/snapshot.c:274`, `kernel/power/snapshot.c:726`, `kernel/power/snapshot.c:1173`, `kernel/power/user.c:120`, `fs/file_table.c:280`, `fs/file_table.c:313`.
- Opcode material: 1 `Code:` line(s), with 0 marked trapping opcode marker(s).

## Control Flow
- `TestDisassemblyInReports` selects this `.in` file by architecture, builds the matching Linux reporter, parses the crash, then passes both the raw input and parsed `Report` into `decompileOpcodes`.
- `decompileOpcodes` scans all `Code:` lines, tries to parse byte streams with a `<...>` trapping byte marker, decompiles with the architecture target, aligns instructions around the faulting offset, and appends the disassembly to the bottom of the report.

## State And Persistence
- Static fixture only: 42 lines and 2001 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Linux reporter for `arm64`, target metadata from `sys/targets`, objdump-compatible decompilation helpers, and the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm64/0.out`. The test is skipped outside Linux hosts or when the target compiler/decompiler is marked broken.

## Risks And Edge Cases
- Opcode parsing is architecture-sensitive; byte order, Thumb mode, fault marker placement, and objdump output formatting can all change expected `.out` text.

## Test Signals
- Primary signal: parsed Linux crash plus decompiled output must match the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm64/0.out` byte-for-byte.
- Regression signal: `go test ./pkg/report -run TestDisassemblyInReports` on a Linux host should keep the appended decompiled instruction block stable for this architecture.

## Source-Specific Observations
- First crash/log signal: `kernel BUG at kernel/power/snapshot.c:257!`.
- Architecture lane `arm64` makes this input sensitive to target-specific decompiler flags and instruction-width assumptions.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm64/0.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm64/1.in -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm64/1.in

## Purpose
This fixture is a Linux opcode decompilation input for architecture `arm64`. `TestDisassemblyInReports` parses the crash, invokes `linux.decompileOpcodes`, and compares the transformed report with the sibling `.out` golden file.
The input provides a real kernel report with one or more `Code:` byte streams and a marked faulting opcode, exercising `parseOpcodes`, target-aware objdump invocation, instruction alignment, and decompiled snippet insertion.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestDisassemblyInReports`, `testDisassembly`, `linux.decompileOpcodes`, `linux.processOpcodes`, `linux.decompileWithOffset`, `DecompileOpcodes`, `objdumpParseOutput`.
- Fixture metadata: this input intentionally has no `TITLE:`/`FILE:` header; the paired test derives behavior from the parsed Linux crash and `.out` golden output.
- Notable functions observed in the report body: `__raw_writeb`, `_outb`, `logic_outb`, `io_serial_out`, `serial_out`, `serial8250_set_THRI`, `__start_tx`, `serial8250_start_tx`.
- Notable source locations observed in the report body: `arch/arm64/include/asm/io.h:27`, `include/asm-generic/io.h:501`, `lib/logic_pio.c:302`, `drivers/tty/serial/8250/8250_port.c:453`, `drivers/tty/serial/8250/8250.h:120`, `drivers/tty/serial/8250/8250.h:140`, `drivers/tty/serial/8250/8250_port.c:1561`, `drivers/tty/serial/8250/8250_port.c:1660`.
- Opcode material: 1 `Code:` line(s), with 0 marked trapping opcode marker(s).

## Control Flow
- `TestDisassemblyInReports` selects this `.in` file by architecture, builds the matching Linux reporter, parses the crash, then passes both the raw input and parsed `Report` into `decompileOpcodes`.
- `decompileOpcodes` scans all `Code:` lines, tries to parse byte streams with a `<...>` trapping byte marker, decompiles with the architecture target, aligns instructions around the faulting offset, and appends the disassembly to the bottom of the report.

## State And Persistence
- Static fixture only: 49 lines and 2702 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Linux reporter for `arm64`, target metadata from `sys/targets`, objdump-compatible decompilation helpers, and the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm64/1.out`. The test is skipped outside Linux hosts or when the target compiler/decompiler is marked broken.

## Risks And Edge Cases
- Opcode parsing is architecture-sensitive; byte order, Thumb mode, fault marker placement, and objdump output formatting can all change expected `.out` text.

## Test Signals
- Primary signal: parsed Linux crash plus decompiled output must match the sibling golden file `sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm64/1.out` byte-for-byte.
- Regression signal: `go test ./pkg/report -run TestDisassemblyInReports` on a Linux host should keep the appended decompiled instruction block stable for this architecture.

## Source-Specific Observations
- First crash/log signal: `Internal error: synchronous external abort: 96000050 [#1] PREEMPT SMP`.
- Architecture lane `arm64` makes this input sensitive to target-specific decompiler flags and instruction-width assumptions.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/decompile/arm64/1.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/0 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/0

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/ipv6/ip6_output.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/ipv6/ip6_output.c.
- Notable functions observed in the report body: `ip6_send_skb`, `__dump_stack`, `dump_stack`, `print_address_description`, `kasan_report_error`, `kasan_report`, `__asan_report_load8_noabort`, `ip6_push_pending_frames`.
- Notable source locations observed in the report body: `net/ipv6/ip6_output.c:1748`, `lib/dump_stack.c:16`, `lib/dump_stack.c:52`, `mm/kasan/report.c:252`, `mm/kasan/report.c:351`, `mm/kasan/report.c:408`, `mm/kasan/report.c:429`, `net/ipv6/ip6_output.c:1763`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 32 lines and 1603 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/ipv6/ip6_output.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: KASAN: use-after-free in ip6_send_skb+0x2f5/0x330 net/ipv6/ip6_output.c:1748`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/ipv6/ip6_output.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/1 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/1

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/ipv6/ip6_output.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/ipv6/ip6_output.c.
- Notable functions observed in the report body: `at`, `__lock_acquire`, `__dump_stack`, `dump_stack`, `panic`, `__warn`, `report_bug`, `fixup_bug`.
- Notable source locations observed in the report body: `kernel/locking/lockdep.c:3344`, `lib/dump_stack.c:16`, `lib/dump_stack.c:52`, `kernel/panic.c:180`, `kernel/panic.c:541`, `lib/bug.c:183`, `arch/x86/kernel/traps.c:190`, `arch/x86/kernel/traps.c:224`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 59 lines and 2991 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/ipv6/ip6_output.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `WARNING: CPU: 2 PID: 24023 at kernel/locking/lockdep.c:3344 __lock_acquire+0x10e5/0x3690 kernel/locking/lockdep.c:3344`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/ipv6/ip6_output.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/1 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/10 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/10

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `fs/nsfs.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=fs/nsfs.c.
- Notable functions observed in the report body: `__read_once_size`, `atomic_read`, `virt_spin_lock`, `queued_spin_lock_slowpath`, `__dump_stack`, `dump_stack`, `kasan_object_err`, `print_address_description`.
- Notable source locations observed in the report body: `include/linux/compiler.h:254`, `arch/x86/include/asm/atomic.h:26`, `arch/x86/include/asm/qspinlock.h:62`, `kernel/locking/qspinlock.c:421`, `lib/dump_stack.c:16`, `lib/dump_stack.c:52`, `mm/kasan/report.c:164`, `mm/kasan/report.c:202`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 36 lines and 1994 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `fs/nsfs.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: KASAN: use-after-free in __read_once_size include/linux/compiler.h:254 [inline] at addr ffff88004f0f1938`.
- The expected blamed subsystem prefix is `fs`; competing frames should not outrank `fs/nsfs.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/10 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/11 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/11

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `virt/kvm/eventfd.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=virt/kvm/eventfd.c.
- Notable functions observed in the report body: `__list_del`, `list_del`, `irq_bypass_unregister_consumer`, `irqfd_shutdown`, `process_one_work`, `worker_thread`, `kthread`, `ret_from_fork`.
- Notable source locations observed in the report body: `include/linux/list.h:89`, `include/linux/list.h:107`, `virt/lib/irqbypass.c:258`, `arch/x86/kvm/../../../virt/kvm/eventfd.c:145`, `kernel/workqueue.c:2096`, `kernel/workqueue.c:2230`, `kernel/kthread.c:209`, `arch/x86/entry/entry_64.S:433`.
- Opcode material: 1 `Code:` line(s), with 1 marked trapping opcode marker(s).

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 48 lines and 2815 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `virt/kvm/eventfd.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `FILE: virt/kvm/eventfd.c`.
- The expected blamed subsystem prefix is `virt`; competing frames should not outrank `virt/kvm/eventfd.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/11 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/12 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/12

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/llc/llc_sap.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/llc/llc_sap.c.
- Notable functions observed in the report body: `skb_set_owner_r`, `__sock_queue_rcv_skb`, `sock_queue_rcv_skb`, `llc_sap_state_process`, `llc_sap_rcv`, `llc_sap_handler`, `llc_rcv`, `__netif_receive_skb_core`.
- Notable source locations observed in the report body: `include/linux/skbuff.h:2389`, `net/core/sock.c:425`, `net/core/sock.c:451`, `net/llc/llc_sap.c:220`, `net/llc/llc_sap.c:294`, `net/llc/llc_sap.c:434`, `net/llc/llc_input.c:208`, `net/core/dev.c:4190`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 54 lines and 2549 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/llc/llc_sap.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `kernel BUG at ./include/linux/skbuff.h:2389!`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/llc/llc_sap.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/12 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/13 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/13

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/dccp/ipv6.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/dccp/ipv6.c.
- Notable functions observed in the report body: `skb_pfmemalloc`, `skb_clone`, `__dump_stack`, `dump_stack`, `kasan_object_err`, `print_address_description`, `kasan_report_error`, `kasan_report.part.1`.
- Notable source locations observed in the report body: `include/linux/skbuff.h:829`, `net/core/skbuff.c:1029`, `lib/dump_stack.c:15`, `lib/dump_stack.c:51`, `mm/kasan/report.c:162`, `mm/kasan/report.c:200`, `mm/kasan/report.c:289`, `mm/kasan/report.c:311`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 63 lines and 3174 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/dccp/ipv6.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: KASAN: use-after-free in skb_pfmemalloc include/linux/skbuff.h:829 [inline] at addr ffff88003b910d8c`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/dccp/ipv6.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/13 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/14 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/14

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `fs/timerfd.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=fs/timerfd.c.
- Notable functions observed in the report body: `__list_add_rcu`, `list_add_rcu`, `timerfd_setup_cancel`, `do_timerfd_settime`, `__dump_stack`, `dump_stack`, `kasan_object_err`, `print_address_description`.
- Notable source locations observed in the report body: `include/linux/rculist.h:57`, `include/linux/rculist.h:78`, `fs/timerfd.c:141`, `fs/timerfd.c:446`, `lib/dump_stack.c:15`, `lib/dump_stack.c:51`, `mm/kasan/report.c:162`, `mm/kasan/report.c:200`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 26 lines and 1449 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `fs/timerfd.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: KASAN: use-after-free in __list_add_rcu include/linux/rculist.h:57 [inline] at addr ffff8801c5b6c110`.
- The expected blamed subsystem prefix is `fs`; competing frames should not outrank `fs/timerfd.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/14 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/15 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/15

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `fs/pnode.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=fs/pnode.c.
- Notable functions observed in the report body: `apic_timer_interrupt`, `__do_softirq`, `invoke_softirq`, `irq_exit`, `next_group`, `x90`, `x8c4`, `x1a0`.
- Notable source locations observed in the report body: `arch/x86/entry/entry_64.S:710`, `kernel/softirq.c:344`, `kernel/softirq.c:395`, `kernel/softirq.c:436`, `fs/pnode.c:172`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 9 lines and 679 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `fs/pnode.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: soft lockup - CPU#1 stuck for 22s! [syz-executor2:7067]`.
- The expected blamed subsystem prefix is `fs`; competing frames should not outrank `fs/pnode.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/15 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/16 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/16

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `ipc/util.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=ipc/util.c.
- Notable functions observed in the report body: `at`, `__vunmap`, `__dump_stack`, `dump_stack`, `__panic`, `panic_saved_regs`, `warn_slowpath_common`, `warn_slowpath_fmt`.
- Notable source locations observed in the report body: `mm/vmalloc.c:1473`, `mm/vmalloc.c:1472`, `lib/dump_stack.c:15`, `lib/dump_stack.c:51`, `kernel/panic.c:179`, `kernel/panic.c:280`, `kernel/panic.c:642`, `kernel/panic.c:658`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 18 lines and 890 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `ipc/util.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `WARNING: CPU: 1 PID: 7733 at mm/vmalloc.c:1473 __vunmap+0x1ca/0x300 mm/vmalloc.c:1472()`.
- The expected blamed subsystem prefix is `ipc`; competing frames should not outrank `ipc/util.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/16 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/17 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/17

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/netfilter/x_tables.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/netfilter/x_tables.c.
- Notable functions observed in the report body: `__dump_stack`, `dump_stack`, `warn_alloc`, `__vmalloc_area_node_memcg`, `__vmalloc_node_range_memcg`, `__vmalloc_node_memcg`, `__vmalloc_node_memcg_flags`, `vmalloc`.
- Notable source locations observed in the report body: `lib/dump_stack.c:15`, `lib/dump_stack.c:51`, `mm/page_alloc.c:2850`, `mm/vmalloc.c:1647`, `mm/vmalloc.c:1690`, `mm/vmalloc.c:1751`, `mm/vmalloc.c:1788`, `mm/vmalloc.c:1803`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 17 lines and 978 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/netfilter/x_tables.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `FILE: net/netfilter/x_tables.c`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/netfilter/x_tables.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/17 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/18 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/18

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `crypto/blkcipher.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=crypto/blkcipher.c.
- Notable functions observed in the report body: `virt_to_cache`, `kfree`, `blkcipher_walk_done`, `x250`, `xde0`.
- Notable source locations observed in the report body: `mm/slab.c:400`, `mm/slab.c:3802`, `crypto/blkcipher.c:139`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 29 lines and 1383 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `crypto/blkcipher.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: unable to handle kernel NULL pointer dereference at 0000000000000074`.
- The expected blamed subsystem prefix is `crypto`; competing frames should not outrank `crypto/blkcipher.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/18 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/19 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/19

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `crypto/af_alg.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=crypto/af_alg.c.
- Notable functions observed in the report body: `at`, `lock_sock`, `af_alg_wait_for_data`, `__do_page_fault`, `slab_alloc`, `__do_kmalloc`, `__kmalloc`, `kfree`.
- Notable source locations observed in the report body: `arch/x86/mm/fault.c:1372`, `include/net/sock.h:1465`, `crypto/af_alg.c:768`, `arch/x86/mm/fault.c:1358`, `mm/slab.c:3378`, `mm/slab.c:3709`, `mm/slab.c:3720`, `mm/slab.c:3800`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 36 lines and 2296 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `crypto/af_alg.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: sleeping function called from invalid context at arch/x86/mm/fault.c:1372`.
- The expected blamed subsystem prefix is `crypto`; competing frames should not outrank `crypto/af_alg.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/19 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/2 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/2

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `kernel/bpf/hashtab.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=kernel/bpf/hashtab.c.
- Notable functions observed in the report body: `pcpu_addr_to_page`, `pcpu_chunk_addr_search`, `free_percpu`, `htab_free_elems`, `prealloc_destroy`, `htab_map_free`, `bpf_map_free_deferred`, `process_one_work`.
- Notable source locations observed in the report body: `mm/percpu-vm.c:358`, `mm/percpu.c:852`, `mm/percpu.c:1264`, `kernel/bpf/hashtab.c:112`, `kernel/bpf/hashtab.c:191`, `kernel/bpf/hashtab.c:1093`, `kernel/bpf/syscall.c:124`, `kernel/workqueue.c:2097`.
- Opcode material: 1 `Code:` line(s), with 1 marked trapping opcode marker(s).

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 43 lines and 2241 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `kernel/bpf/hashtab.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `FILE: kernel/bpf/hashtab.c`.
- The expected blamed subsystem prefix is `kernel`; competing frames should not outrank `kernel/bpf/hashtab.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/20 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/20

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `driver/foo/lib/foo.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=driver/foo/lib/foo.c.
- Notable functions observed in the report body: `at`, `__lock_acquire`, `x3690`.
- Notable source locations observed in the report body: `kernel/locking/lockdep.c:3344`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 4 lines and 171 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `driver/foo/lib/foo.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `WARNING: CPU: 2 PID: 24023 at kernel/locking/lockdep.c:3344 __lock_acquire+0x10e5/0x3690 kernel/locking/lockdep.c:3344`.
- The expected blamed subsystem prefix is `driver`; competing frames should not outrank `driver/foo/lib/foo.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/20 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/21 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/21

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `fs/block_dev.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=fs/block_dev.c.
- Notable functions observed in the report body: `context_switch`, `__schedule`, `schedule`, `io_schedule`, `wait_on_page_bit_common`, `__lock_page`, `lock_page`, `truncate_inode_pages_range`.
- Notable source locations observed in the report body: `kernel/sched/core.c:2800`, `kernel/sched/core.c:3376`, `kernel/sched/core.c:3435`, `kernel/sched/core.c:5043`, `mm/filemap.c:1099`, `mm/filemap.c:1272`, `include/linux/pagemap.h:483`, `mm/truncate.c:452`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 32 lines and 1482 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `fs/block_dev.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `FILE: fs/block_dev.c`.
- The expected blamed subsystem prefix is `fs`; competing frames should not outrank `fs/block_dev.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/21 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/22 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/22

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `fs/block_dev.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=fs/block_dev.c.
- Notable functions observed in the report body: `context_switch`, `__schedule`, `schedule`, `schedule_preempt_disabled`, `__mutex_lock_common`, `__mutex_lock`, `mutex_lock_nested`, `blkdev_put`.
- Notable source locations observed in the report body: `kernel/sched/core.c:2800`, `kernel/sched/core.c:3376`, `kernel/sched/core.c:3435`, `kernel/sched/core.c:3493`, `kernel/locking/mutex.c:833`, `kernel/locking/mutex.c:893`, `kernel/locking/mutex.c:908`, `fs/block_dev.c:1793`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 16 lines and 723 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `fs/block_dev.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `FILE: fs/block_dev.c`.
- The expected blamed subsystem prefix is `fs`; competing frames should not outrank `fs/block_dev.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/22 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/23 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/23

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `crypto/af_alg.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=crypto/af_alg.c.
- Notable functions observed in the report body: `context_switch`, `__schedule`, `schedule`, `__lock_sock`, `lock_sock_nested`, `lock_sock`, `af_alg_sendmsg`, `aead_sendmsg`.
- Notable source locations observed in the report body: `kernel/sched/core.c:2799`, `kernel/sched/core.c:3375`, `kernel/sched/core.c:3434`, `net/core/sock.c:2240`, `net/core/sock.c:2764`, `include/net/sock.h:1461`, `crypto/af_alg.c:858`, `crypto/algif_aead.c:76`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 16 lines and 687 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `crypto/af_alg.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `FILE: crypto/af_alg.c`.
- The expected blamed subsystem prefix is `crypto`; competing frames should not outrank `crypto/af_alg.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/23 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/24 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/24

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `crypto/algif_aead.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=crypto/algif_aead.c.
- Notable functions observed in the report body: `context_switch`, `__schedule`, `schedule`, `schedule_timeout`, `do_wait_for_common`, `__wait_for_common`, `wait_for_common`, `wait_for_completion`.
- Notable source locations observed in the report body: `kernel/sched/core.c:2800`, `kernel/sched/core.c:3376`, `kernel/sched/core.c:3435`, `kernel/time/timer.c:1776`, `kernel/sched/completion.c:91`, `kernel/sched/completion.c:112`, `kernel/sched/completion.c:123`, `kernel/sched/completion.c:144`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 17 lines and 810 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `crypto/algif_aead.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `FILE: crypto/algif_aead.c`.
- The expected blamed subsystem prefix is `crypto`; competing frames should not outrank `crypto/algif_aead.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/24 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/25 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/25

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/xfrm/xfrm_ipcomp.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/xfrm/xfrm_ipcomp.c.
- Notable functions observed in the report body: `__this_cpu_preempt_check`, `__dump_stack`, `dump_stack`, `check_preemption_disabled`, `ipcomp_alloc_tfms`, `ipcomp_init_state`, `ipcomp4_init_state`, `__xfrm_init_state`.
- Notable source locations observed in the report body: `lib/smp_processor_id.c:62`, `lib/dump_stack.c:15`, `lib/dump_stack.c:51`, `lib/smp_processor_id.c:46`, `net/xfrm/xfrm_ipcomp.c:286`, `net/xfrm/xfrm_ipcomp.c:363`, `net/ipv4/ipcomp.c:137`, `net/xfrm/xfrm_state.c:2096`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 30 lines and 1970 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/xfrm/xfrm_ipcomp.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: using __this_cpu_read() in preemptible [00000000] code: syzkaller157688/3312`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/xfrm/xfrm_ipcomp.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/25 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/26 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/26

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/xfrm/xfrm_policy.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/xfrm/xfrm_policy.c.
- Notable functions observed in the report body: `sched_show_task`, `print_other_cpu_stall`, `check_cpu_stall.isra.61`, `__rcu_pending`, `rcu_pending`, `rcu_check_callbacks`, `update_process_times`, `tick_sched_handle`.
- Notable source locations observed in the report body: `kernel/sched/core.c:5198`, `kernel/rcu/tree.c:1564`, `kernel/rcu/tree.c:1682`, `kernel/rcu/tree.c:3440`, `kernel/rcu/tree.c:3502`, `kernel/rcu/tree.c:2842`, `kernel/time/timer.c:1630`, `kernel/time/tick-sched.c:162`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 93 lines and 4927 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/xfrm/xfrm_policy.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `INFO: rcu_sched detected stalls on CPUs/tasks:`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/xfrm/xfrm_policy.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/26 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/27 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/27

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `sound/core/oss/mulaw.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=sound/core/oss/mulaw.c.
- Notable functions observed in the report body: `sched_show_task`, `print_other_cpu_stall`, `check_cpu_stall.isra.61`, `__rcu_pending`, `rcu_pending`, `rcu_check_callbacks`, `update_process_times`, `tick_sched_handle`.
- Notable source locations observed in the report body: `kernel/sched/core.c:5198`, `kernel/rcu/tree.c:1564`, `kernel/rcu/tree.c:1682`, `kernel/rcu/tree.c:3440`, `kernel/rcu/tree.c:3502`, `kernel/rcu/tree.c:2842`, `kernel/time/timer.c:1628`, `kernel/time/tick-sched.c:162`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 56 lines and 3070 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `sound/core/oss/mulaw.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `INFO: rcu_sched detected stalls on CPUs/tasks:`.
- The expected blamed subsystem prefix is `sound`; competing frames should not outrank `sound/core/oss/mulaw.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/27 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/28 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/28

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/strparser/strparser.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/strparser/strparser.c.
- Notable functions observed in the report body: `constant_test_bit`, `work_is_static_object`, `__dump_stack`, `dump_stack`, `print_address_description`, `kasan_report_error`, `kasan_report`, `__asan_report_load8_noabort`.
- Notable source locations observed in the report body: `arch/x86/include/asm/bitops.h:325`, `kernel/workqueue.c:443`, `lib/dump_stack.c:17`, `lib/dump_stack.c:53`, `mm/kasan/report.c:252`, `mm/kasan/report.c:351`, `mm/kasan/report.c:409`, `mm/kasan/report.c:430`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 96 lines and 4506 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/strparser/strparser.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: KASAN: use-after-free in constant_test_bit arch/x86/include/asm/bitops.h:325 [inline]`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/strparser/strparser.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/28 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/29 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/29

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `drivers/vhost/vhost.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=drivers/vhost/vhost.c.
- Notable functions observed in the report body: `__list_add_valid`, `__dump_stack`, `dump_stack`, `print_address_description`, `kasan_report_error`, `kasan_report`, `__asan_report_load8_noabort`, `__list_add`.
- Notable source locations observed in the report body: `lib/list_debug.c:23`, `lib/dump_stack.c:17`, `lib/dump_stack.c:53`, `mm/kasan/report.c:252`, `mm/kasan/report.c:351`, `mm/kasan/report.c:409`, `mm/kasan/report.c:430`, `include/linux/list.h:60`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 97 lines and 4542 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `drivers/vhost/vhost.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: KASAN: use-after-free in __list_add_valid+0xb1/0xd0 lib/list_debug.c:23`.
- The expected blamed subsystem prefix is `drivers`; competing frames should not outrank `drivers/vhost/vhost.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/29 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/3 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/3

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `kernel/bpf/arraymap.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=kernel/bpf/arraymap.c.
- Notable functions observed in the report body: `css_put`, `cgroup_put`, `cgroup_fd_array_put_ptr`, `fd_array_map_delete_elem`, `bpf_fd_array_map_clear`, `cgroup_fd_array_free`, `bpf_map_free_deferred`, `process_one_work`.
- Notable source locations observed in the report body: `include/linux/cgroup.h:354`, `include/linux/cgroup.h:373`, `kernel/bpf/arraymap.c:535`, `kernel/bpf/arraymap.c:374`, `kernel/bpf/arraymap.c:410`, `kernel/bpf/arraymap.c:540`, `kernel/bpf/syscall.c:124`, `kernel/workqueue.c:2097`.
- Opcode material: 1 `Code:` line(s), with 1 marked trapping opcode marker(s).

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 43 lines and 2297 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `kernel/bpf/arraymap.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `FILE: kernel/bpf/arraymap.c`.
- The expected blamed subsystem prefix is `kernel`; competing frames should not outrank `kernel/bpf/arraymap.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/3 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/30 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/30

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/ipv4/netfilter/ipt_CLUSTERIP.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/ipv4/netfilter/ipt_CLUSTERIP.c.
- Notable functions observed in the report body: `at`, `proc_register`, `__dump_stack`, `dump_stack`, `panic`, `__warn`, `report_bug`, `fixup_bug.part.11`.
- Notable source locations observed in the report body: `fs/proc/generic.c:330`, `fs/proc/generic.c:329`, `lib/dump_stack.c:17`, `lib/dump_stack.c:53`, `kernel/panic.c:183`, `kernel/panic.c:547`, `lib/bug.c:184`, `arch/x86/kernel/traps.c:178`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 51 lines and 2742 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/ipv4/netfilter/ipt_CLUSTERIP.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `WARNING: CPU: 1 PID: 4074 at fs/proc/generic.c:330 proc_register+0x2a4/0x370 fs/proc/generic.c:329`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/ipv4/netfilter/ipt_CLUSTERIP.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/30 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/31 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/31

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/bridge/br_if.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/bridge/br_if.c.
- Notable functions observed in the report body: `at`, `kobject_add_internal`, `__dump_stack`, `dump_stack`, `panic`, `__warn`, `report_bug`, `fixup_bug`.
- Notable source locations observed in the report body: `lib/kobject.c:244`, `lib/kobject.c:242`, `lib/dump_stack.c:16`, `lib/dump_stack.c:52`, `kernel/panic.c:181`, `kernel/panic.c:542`, `lib/bug.c:183`, `arch/x86/kernel/traps.c:178`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 58 lines and 2945 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/bridge/br_if.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `WARNING: CPU: 1 PID: 3485 at lib/kobject.c:244 kobject_add_internal+0x3f6/0xbc0 lib/kobject.c:242`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/bridge/br_if.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/31 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/32 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/32

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/tipc/name_table.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/tipc/name_table.c.
- Notable functions observed in the report body: `at`, `__list_del_entry_valid`, `__list_del_entry`, `list_del_init`, `tipc_nametbl_unsubscribe`, `tipc_subscrb_subscrp_delete`, `tipc_subscrb_delete`, `tipc_subscrb_release_cb`.
- Notable source locations observed in the report body: `lib/list_debug.c:53`, `lib/list_debug.c:51`, `include/linux/list.h:117`, `include/linux/list.h:159`, `net/tipc/name_table.c:851`, `net/tipc/subscr.c:208`, `net/tipc/subscr.c:238`, `net/tipc/subscr.c:316`.
- Opcode material: 1 `Code:` line(s), with 1 marked trapping opcode marker(s).

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 57 lines and 3103 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/tipc/name_table.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `kernel BUG at lib/list_debug.c:53!`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/tipc/name_table.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/32 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/33 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/33

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `kernel/bpf/cpumap.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=kernel/bpf/cpumap.c.
- Notable functions observed in the report body: `at`, `kvmalloc_node`, `__dump_stack`, `dump_stack`, `panic`, `__warn`, `report_bug`, `fixup_bug.part.11`.
- Notable source locations observed in the report body: `mm/util.c:403`, `lib/dump_stack.c:17`, `lib/dump_stack.c:53`, `kernel/panic.c:183`, `kernel/panic.c:547`, `lib/bug.c:184`, `arch/x86/kernel/traps.c:178`, `arch/x86/kernel/traps.c:247`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 45 lines and 2694 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `kernel/bpf/cpumap.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `WARNING: CPU: 1 PID: 4183 at mm/util.c:403 kvmalloc_node+0xc3/0xd0 mm/util.c:403`.
- The expected blamed subsystem prefix is `kernel`; competing frames should not outrank `kernel/bpf/cpumap.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/33 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/34 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/34

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/ipv6/route.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/ipv6/route.c.
- Notable functions observed in the report body: `rt6_mtu_change_route`, `__dump_stack`, `dump_stack`, `kmsan_report`, `__msan_warning_32`, `fib6_clean_node`, `fib6_walk_continue`, `fib6_walk`.
- Notable source locations observed in the report body: `net/ipv6/route.c:3822`, `lib/dump_stack.c:17`, `lib/dump_stack.c:53`, `mm/kmsan/kmsan.c:1093`, `mm/kmsan/kmsan_instr.c:676`, `net/ipv6/ip6_fib.c:1918`, `net/ipv6/ip6_fib.c:1844`, `net/ipv6/ip6_fib.c:1892`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 87 lines and 4368 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/ipv6/route.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: KMSAN: use of uninitialized memory in rt6_mtu_change_route+0x4d8/0xa70 net/ipv6/route.c:3822`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/ipv6/route.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/34 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/35 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/35

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `arch/x86/kernel/dumpstack.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=arch/x86/kernel/dumpstack.c.
- Notable functions observed in the report body: `show_trace_log_lvl`, `__dump_stack`, `dump_stack`, `kmsan_report`, `__msan_warning_32`, `show_stack`, `warn_alloc`, `__vmalloc_node_range`.
- Notable source locations observed in the report body: `arch/x86/kernel/dumpstack.c:203`, `lib/dump_stack.c:17`, `lib/dump_stack.c:53`, `mm/kmsan/kmsan.c:1093`, `mm/kmsan/kmsan_instr.c:676`, `arch/x86/kernel/dumpstack.c:236`, `mm/page_alloc.c:3317`, `mm/vmalloc.c:1775`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 78 lines and 4149 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.
- The expected path is in a generic or architecture area, so skip-list changes can easily redirect blame to a caller subsystem.

## Test Signals
- Primary signal: expected guilty file `arch/x86/kernel/dumpstack.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: KMSAN: use of uninitialized memory in show_trace_log_lvl+0xda4/0x1030 arch/x86/kernel/dumpstack.c:203`.
- The expected blamed subsystem prefix is `arch`; competing frames should not outrank `arch/x86/kernel/dumpstack.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/35 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/36 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/36

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `sound/core/oss/pcm_oss.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=sound/core/oss/pcm_oss.c.
- Notable functions observed in the report body: `__dump_stack`, `dump_stack`, `nmi_cpu_backtrace.cold.4`, `nmi_trigger_cpumask_backtrace`, `arch_trigger_cpumask_backtrace`, `trigger_single_cpu_backtrace`, `rcu_dump_cpu_stacks`, `print_cpu_stall`.
- Notable source locations observed in the report body: `lib/dump_stack.c:77`, `lib/dump_stack.c:113`, `lib/nmi_backtrace.c:103`, `lib/nmi_backtrace.c:62`, `arch/x86/kernel/apic/hw_nmi.c:38`, `include/linux/nmi.h:156`, `kernel/rcu/tree.c:1376`, `kernel/rcu/tree.c:1525`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 63 lines and 3459 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `sound/core/oss/pcm_oss.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `INFO: rcu_sched self-detected stall on CPU`.
- The expected blamed subsystem prefix is `sound`; competing frames should not outrank `sound/core/oss/pcm_oss.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/36 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/37 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/37

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `fs/xattr.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=fs/xattr.c.
- Notable functions observed in the report body: `at`, `kmalloc_slab`, `__dump_stack`, `dump_stack`, `panic`, `__warn.cold.8`, `report_bug`, `fixup_bug`.
- Notable source locations observed in the report body: `mm/slab_common.c:1031`, `lib/dump_stack.c:77`, `lib/dump_stack.c:113`, `kernel/panic.c:184`, `kernel/panic.c:536`, `lib/bug.c:186`, `arch/x86/kernel/traps.c:178`, `arch/x86/kernel/traps.c:296`.
- Opcode material: 2 `Code:` line(s), with 2 marked trapping opcode marker(s).

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 53 lines and 2853 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `fs/xattr.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `WARNING: CPU: 0 PID: 4406 at mm/slab_common.c:1031 kmalloc_slab+0x56/0x70 mm/slab_common.c:1031`.
- The expected blamed subsystem prefix is `fs`; competing frames should not outrank `fs/xattr.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/37 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/38 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/38

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `sound/core/seq/seq_clientmgr.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=sound/core/seq/seq_clientmgr.c.
- Notable functions observed in the report body: `__dump_stack`, `dump_stack`, `nmi_cpu_backtrace.cold.3`, `nmi_trigger_cpumask_backtrace`, `arch_trigger_cpumask_backtrace`, `trigger_single_cpu_backtrace`, `rcu_dump_cpu_stacks`, `print_cpu_stall.cold.78`.
- Notable source locations observed in the report body: `lib/dump_stack.c:77`, `lib/dump_stack.c:113`, `lib/nmi_backtrace.c:101`, `lib/nmi_backtrace.c:62`, `arch/x86/kernel/apic/hw_nmi.c:38`, `include/linux/nmi.h:162`, `kernel/rcu/tree.c:1340`, `kernel/rcu/tree.c:1478`.
- Opcode material: 2 `Code:` line(s), with 2 marked trapping opcode marker(s).

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 61 lines and 3564 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `sound/core/seq/seq_clientmgr.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `rcu: INFO: rcu_sched self-detected stall on CPU`.
- The expected blamed subsystem prefix is `sound`; competing frames should not outrank `sound/core/seq/seq_clientmgr.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/38 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/39 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/39

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `security/apparmor/policy_ns.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=security/apparmor/policy_ns.c.
- Notable functions observed in the report body: `sock_common_setsockopt`, `__sys_setsockopt`, `__do_sys_setsockopt`, `__se_sys_setsockopt`, `__x64_sys_setsockopt`, `do_syscall_64`, `memcmp`, `__dump_stack`.
- Notable source locations observed in the report body: `net/core/sock.c:3038`, `net/socket.c:1902`, `net/socket.c:1913`, `net/socket.c:1910`, `arch/x86/entry/common.c:290`, `lib/string.c:861`, `lib/dump_stack.c:77`, `lib/dump_stack.c:113`.
- Opcode material: 2 `Code:` line(s), with 2 marked trapping opcode marker(s).

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 77 lines and 4254 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `security/apparmor/policy_ns.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: KASAN: global-out-of-bounds in memcmp+0xe3/0x160 lib/string.c:861`.
- The expected blamed subsystem prefix is `security`; competing frames should not outrank `security/apparmor/policy_ns.c`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/39 -->
