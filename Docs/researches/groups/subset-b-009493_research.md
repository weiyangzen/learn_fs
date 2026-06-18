# subset-b-009493 Research

Grouped research for syzkaller Linux report parser fixtures. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/559 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/559

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `possible deadlock in test_clear_page_writeback`, expected type `LOCKDEP`, and parser behavior for a lockdep/locking diagnostic using x86/GCE syzkaller console format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises lockdep/deadlock recognizers, lock-class text normalization, and stack-frame selection from nested dependency reports. Parser-relevant local signals: key stack symbols include `lock_acquire`, `_raw_spin_lock_irqsave`, `test_clear_page_writeback`, `end_page_writeback`, `ext4_finish_bio`, `ext4_end_bio`, `bio_endio`, `blk_update_request`. First non-header signal: `[  904.288838] =====================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 366 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `possible deadlock in test_clear_page_writeback`, type `LOCKDEP`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/559 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/56 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/56

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `BUG: sleeping function called from invalid context in corrupted`, expected type `ATOMIC_SLEEP`, and parser behavior for a atomic-sleep context diagnostic using standard Linux printk/oops format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction. It belongs to a compact cluster of intentionally corrupted or truncated fixtures where generic crash words appear but the expected title must degrade to `corrupted`.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises atomic-sleep recognizers, invalid-context wording, and conservative corrupted-title handling for very short reports. Parser-relevant local signals: expected corrupted flag is `Y`. First non-header signal: `[ 1722.511384] BUG: sleeping function called from invalid context at include/linux/wait.h:1095`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 6 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture is corrupted or truncated, the parser must stay conservative and avoid inventing a precise frame from unreliable text. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `BUG: sleeping function called from invalid context in corrupted`, type `ATOMIC_SLEEP`, alternate titles `none`, corrupted `Y`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/56 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/560 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/560

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `possible deadlock in test_clear_page_writeback`, expected type `LOCKDEP`, and parser behavior for a lockdep/locking diagnostic using x86/GCE syzkaller console format, RCU stall multi-line report. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises lockdep/deadlock recognizers, lock-class text normalization, and stack-frame selection from nested dependency reports. Parser-relevant local signals: key stack symbols include `_raw_spin_lock_irqsave`, `test_clear_page_writeback`, `end_page_writeback`, `ext4_finish_bio`, `ext4_end_bio`, `bio_endio`, `blk_update_request`, `scsi_end_request`. First non-header signal: `[   26.449922] =====================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 282 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `possible deadlock in test_clear_page_writeback`, type `LOCKDEP`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/560 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/561 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/561

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `possible deadlock in cgroup_rstat_updated`, expected type `LOCKDEP`, and parser behavior for a lockdep/locking diagnostic using ARM backtrace format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises lockdep/deadlock recognizers, lock-class text normalization, and stack-frame selection from nested dependency reports. Parser-relevant local signals: key stack symbols include `lock_acquire.part.0`, `lock_acquire`, `_raw_spin_lock_irqsave`, `cgroup_rstat_updated`, `cgroup_base_stat_cputime_account_end`, `__cgroup_account_cputime_field`, `task_group_account_field`, `account_system_index_time`. First non-header signal: `[  594.649298][ T5097] =====================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 346 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `possible deadlock in cgroup_rstat_updated`, type `LOCKDEP`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/561 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/562 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/562

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `WARNING in vkms_vblank_simulate`, expected type `WARNING`, and parser behavior for a kernel WARNING/oops diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises warning recognizers, panic-on-warn detection when present, and guilty-frame selection from the warning call trace rather than generic allocator or IRQ helpers. Parser-relevant local signals: key stack symbols include `vkms_get_vblank_timestamp`, `__run_hrtimer`, `hrtimer_interrupt`, `sync_rcu_exp_select_node_cpus`, `__sysvec_apic_timer_interrupt`, `asm_call_irq_on_stack`, `sysvec_apic_timer_interrupt`, `asm_sysvec_apic_timer_interrupt`; expected panicked flag is `Y`. First non-header signal: `[  201.134276][    C1] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 151 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `WARNING in vkms_vblank_simulate`, type `WARNING`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/562 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/563 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/563

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `WARNING in bpf_warn_invalid_xdp_action`, expected type `WARNING`, and parser behavior for a kernel WARNING/oops diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises warning recognizers, panic-on-warn detection when present, and guilty-frame selection from the warning call trace rather than generic allocator or IRQ helpers. Parser-relevant local signals: key stack symbols include `netif_receive_generic_xdp`, `__netif_receive_skb_core`, `__netif_receive_skb`, `process_backlog`, `napi_poll`, `net_rx_action`, `__do_softirq`, `asm_call_irq_on_stack`; expected panicked flag is `Y`. First non-header signal: `[  459.035879][    C1] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 128 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `WARNING in bpf_warn_invalid_xdp_action`, type `WARNING`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/563 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/564 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/564

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `WARNING in squashfs_read_table`, expected type `WARNING`, and parser behavior for a kernel WARNING/oops diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises warning recognizers, panic-on-warn detection when present, and guilty-frame selection from the warning call trace rather than generic allocator or IRQ helpers. Parser-relevant local signals: key stack symbols include `alloc_pages_current`, `kmalloc_order`, `kmalloc_order_trace`, `__kmalloc`, `squashfs_read_table`, `squashfs_read_xattr_id_table`, `squashfs_fill_super`, `get_tree_bdev`; expected panicked flag is `Y`. First non-header signal: `[  549.217031][T11106] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 96 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `WARNING in squashfs_read_table`, type `WARNING`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/564 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/565 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/565

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `BUG: using __this_cpu_read() in preemptible code in __bad_area_nosemaphore`, expected type `LOCKDEP`, and parser behavior for a lockdep/locking diagnostic using x86/GCE syzkaller console format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises lockdep/deadlock recognizers, lock-class text normalization, and stack-frame selection from nested dependency reports. Parser-relevant local signals: key stack symbols include `dump_stack`, `check_preemption_disabled`, `lockdep_hardirqs_on_prepare`, `trace_hardirqs_on`, `__bad_area_nosemaphore`, `do_user_addr_fault`, `exc_page_fault`, `asm_exc_page_fault`. First non-header signal: `[  127.573471][ T9951] BUG: using __this_cpu_read() in preemptible [00000000] code: syz-executor.0/9951`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 47 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `BUG: using __this_cpu_read() in preemptible code in __bad_area_nosemaphore`, type `LOCKDEP`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/565 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/566 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/566

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `WARNING in ip6_neigh_lookup`, expected type `WARNING`, and parser behavior for a kernel WARNING/oops diagnostic using ARM backtrace format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises warning recognizers, panic-on-warn detection when present, and guilty-frame selection from the warning call trace rather than generic allocator or IRQ helpers. Parser-relevant local signals: key stack symbols include `dump_backtrace`, `show_stack`, `dump_stack`, `panic`, `__warn`, `warn_slowpath_fmt`, `__local_bh_enable_ip`, `ip6_neigh_lookup`; expected panicked flag is `Y`. First non-header signal: `[ 1471.274677][    C1] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 164 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `WARNING in ip6_neigh_lookup`, type `WARNING`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/566 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/567 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/567

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `BUG: unable to handle kernel NULL pointer dereference in vhci_shutdown_connection`, expected type `NULL-POINTER-DEREFERENCE`, and parser behavior for a architecture fault/oops diagnostic using ARM backtrace format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises architecture fault/oops recognizers, bad-access alternate title generation, and stack-frame extraction from the architecture-specific register dump. Parser-relevant local signals: key stack symbols include `kthread_stop`, `vhci_shutdown_connection`, `event_handler`, `process_one_work`, `worker_thread`, `kthread`, `dump_backtrace`, `show_stack`; alternate title(s): `bad-access in vhci_shutdown_connection`; expected panicked flag is `Y`. First non-header signal: `[  775.896747][ T5109] 8<--- cut here ---`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 109 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `BUG: unable to handle kernel NULL pointer dereference in vhci_shutdown_connection`, type `NULL-POINTER-DEREFERENCE`, alternate titles `bad-access in vhci_shutdown_connection`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/567 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/568 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/568

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KASAN: invalid-access Read in io_submit_sqes`, expected type `KASAN-READ`, and parser behavior for a KASAN memory-safety diagnostic using arm64 oops/unwinder format, tagged-address KASAN format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KASAN title/type mapping, access-direction extraction, tagged-address text handling, and frame selection across report and call-trace lines. Parser-relevant local signals: key stack symbols include `dump_backtrace`, `show_stack`, `dump_stack`, `print_address_description`, `kasan_report`, `__do_kernel_fault`, `do_tag_check_fault`, `do_mem_abort`; alternate title(s): `bad-access in io_submit_sqes`. First non-header signal: `[ 1344.478322][ T6700] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 80 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KASAN: invalid-access Read in io_submit_sqes`, type `KASAN-READ`, alternate titles `bad-access in io_submit_sqes`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/568 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/569 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/569

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KASAN: invalid-access Read in enqueue_timer`, expected type `KASAN-READ`, and parser behavior for a KASAN memory-safety diagnostic using tagged-address KASAN format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KASAN title/type mapping, access-direction extraction, tagged-address text handling, and frame selection across report and call-trace lines. Parser-relevant local signals: key stack symbols include `dump_backtrace`, `show_stack`, `dump_stack`, `print_address_description`, `kasan_report`, `__do_kernel_fault`, `do_tag_check_fault`, `do_mem_abort`; alternate title(s): `bad-access in enqueue_timer`. First non-header signal: `[ 1039.654796][    C0] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 55 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KASAN: invalid-access Read in enqueue_timer`, type `KASAN-READ`, alternate titles `bad-access in enqueue_timer`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/569 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/57 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/57

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `INFO: rcu detected stall in corrupted`, expected type `HANG`, and parser behavior for a RCU stall/hang diagnostic using x86/GCE syzkaller console format, RCU stall multi-line report. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction. It belongs to a compact cluster of intentionally corrupted or truncated fixtures where generic crash words appear but the expected title must degrade to `corrupted`.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises RCU stall/hang recognizers, corrupted-report handling when expected, NMI backtrace parsing, and title fallback to the active function when reliable. Parser-relevant local signals: key stack symbols include `wait_for_xmitr`, `serial8250_console_putchar`, `uart_console_write`, `serial8250_console_write`, `check_noncircular`, `hrtimer_interrupt`, `local_apic_timer_interrupt`, `smp_apic_timer_interrupt`; alternate title(s): `stall in corrupted`; expected corrupted flag is `Y`. First non-header signal: `[  277.780013] INFO: rcu_sched self-detected stall on CPU`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 51 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture is corrupted or truncated, the parser must stay conservative and avoid inventing a precise frame from unreliable text. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `INFO: rcu detected stall in corrupted`, type `HANG`, alternate titles `stall in corrupted`, corrupted `Y`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/57 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/570 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/570

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KASAN: invalid-access Read in bond_ipsec_del_sa`, expected type `KASAN-READ`, and parser behavior for a KASAN memory-safety diagnostic using arm64 oops/unwinder format, tagged-address KASAN format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KASAN title/type mapping, access-direction extraction, tagged-address text handling, and frame selection across report and call-trace lines. Parser-relevant local signals: key stack symbols include `dump_backtrace`, `show_stack`, `dump_stack`, `print_address_description`, `kasan_report`, `__do_kernel_fault`, `do_tag_check_fault`, `do_mem_abort`; alternate title(s): `bad-access in bond_ipsec_del_sa`. First non-header signal: `[  678.660041][ T2885] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 99 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KASAN: invalid-access Read in bond_ipsec_del_sa`, type `KASAN-READ`, alternate titles `bad-access in bond_ipsec_del_sa`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/570 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/571 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/571

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KASAN: invalid-access Read in __run_timers`, expected type `KASAN-READ`, and parser behavior for a KASAN memory-safety diagnostic using arm64 oops/unwinder format, tagged-address KASAN format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KASAN title/type mapping, access-direction extraction, tagged-address text handling, and frame selection across report and call-trace lines. Parser-relevant local signals: key stack symbols include `dump_backtrace`, `show_stack`, `dump_stack`, `print_address_description`, `kasan_report`, `__do_kernel_fault`, `do_tag_check_fault`, `do_mem_abort`; alternate title(s): `bad-access in __run_timers`. First non-header signal: `[  931.917437][    C0] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 122 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KASAN: invalid-access Read in __run_timers`, type `KASAN-READ`, alternate titles `bad-access in __run_timers`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/571 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/572 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/572

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KASAN: invalid-access Read in l2cap_sock_teardown_cb`, expected type `KASAN-READ`, and parser behavior for a KASAN memory-safety diagnostic using arm64 oops/unwinder format, tagged-address KASAN format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KASAN title/type mapping, access-direction extraction, tagged-address text handling, and frame selection across report and call-trace lines. Parser-relevant local signals: key stack symbols include `dump_backtrace`, `show_stack`, `dump_stack`, `print_address_description`, `kasan_report`, `__do_kernel_fault`, `do_tag_check_fault`, `do_mem_abort`; alternate title(s): `bad-access in l2cap_sock_teardown_cb`. First non-header signal: `[ 5825.407853][ T9802] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 96 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KASAN: invalid-access Read in l2cap_sock_teardown_cb`, type `KASAN-READ`, alternate titles `bad-access in l2cap_sock_teardown_cb`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/572 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/573 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/573

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KASAN: invalid-access Read in firmware_fallback_sysfs`, expected type `KASAN-READ`, and parser behavior for a KASAN memory-safety diagnostic using arm64 oops/unwinder format, tagged-address KASAN format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KASAN title/type mapping, access-direction extraction, tagged-address text handling, and frame selection across report and call-trace lines. Parser-relevant local signals: key stack symbols include `dump_backtrace`, `show_stack`, `dump_stack`, `print_address_description`, `kasan_report`, `__do_kernel_fault`, `do_tag_check_fault`, `do_mem_abort`; alternate title(s): `bad-access in firmware_fallback_sysfs`. First non-header signal: `[ 4452.860624][T17139] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 124 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KASAN: invalid-access Read in firmware_fallback_sysfs`, type `KASAN-READ`, alternate titles `bad-access in firmware_fallback_sysfs`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/573 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/574 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/574

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `WARNING in smk_write_syslog`, expected type `WARNING`, and parser behavior for a kernel WARNING/oops diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises warning recognizers, panic-on-warn detection when present, and guilty-frame selection from the warning call trace rather than generic allocator or IRQ helpers. Parser-relevant local signals: key stack symbols include `kmalloc_order`, `kmalloc_order_trace`, `__kmalloc_track_caller`, `memdup_user_nul`, `smk_write_syslog`, `vfs_write`, `ksys_write`, `do_syscall_64`; expected panicked flag is `Y`. First non-header signal: `[  192.620756][T13366] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 79 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `WARNING in smk_write_syslog`, type `WARNING`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/574 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/575 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/575

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `WARNING in rds_rdma_extra_size`, expected type `WARNING`, and parser behavior for a kernel WARNING/oops diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises warning recognizers, panic-on-warn detection when present, and guilty-frame selection from the warning call trace rather than generic allocator or IRQ helpers. Parser-relevant local signals: key stack symbols include `kmalloc_order`, `kmalloc_order_trace`, `__kmalloc`, `kmalloc_array`, `rds_rdma_extra_size`, `rds_sendmsg`, `____sys_sendmsg`, `__sys_sendmsg`; expected panicked flag is `Y`. First non-header signal: `[  284.876768][T15540] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 79 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `WARNING in rds_rdma_extra_size`, type `WARNING`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/575 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/576 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/576

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in rmap_walk_file`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `rmap_walk`, `page_mkclean`, `clear_page_dirty_for_io`, `mpage_submit_page`, `mpage_process_page_bufs`, `mpage_prepare_extent_to_map`, `ext4_writepages`, `do_writepages`; expected panicked flag is `Y`. First non-header signal: `[ 1802.485653][T28126] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 59 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in rmap_walk_file`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/576 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/577 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/577

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in truncate_inode_partial_page`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `shmem_undo_range`, `shmem_setattr`, `notify_change`, `do_truncate`, `vfs_truncate`, `do_sys_truncate.part.0`, `__x64_sys_truncate`, `do_syscall_64`; expected panicked flag is `Y`. First non-header signal: `[  413.263409][T16632] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 58 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in truncate_inode_partial_page`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/577 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/578 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/578

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in free_netdev`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `__rtnl_newlink`, `rtnl_newlink`, `rtnetlink_rcv_msg`, `netlink_rcv_skb`, `netlink_unicast`, `netlink_sendmsg`, `sock_sendmsg`, `____sys_sendmsg`; expected panicked flag is `Y`. First non-header signal: `[  429.970583][T14786] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 61 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in free_netdev`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/578 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/579 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/579

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in reserve_bootmem_region`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `memblock_free_all`, `dmar_table_detect`, `clkdev_alloc`, `reset_all_zones_managed_pages`, `__sanitizer_cov_trace_const_cmp4`, `swiotlb_init_with_tbl`, `mem_init`, `mm_init`. First non-header signal: `[    0.834244][    T0] kernel BUG at include/linux/page-flags.h:356!`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 35 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in reserve_bootmem_region`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/579 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/58 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/58

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `INFO: rcu detected stall in corrupted`, expected type `HANG`, and parser behavior for a RCU stall/hang diagnostic using RCU stall multi-line report. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction. It belongs to a compact cluster of intentionally corrupted or truncated fixtures where generic crash words appear but the expected title must degrade to `corrupted`.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises RCU stall/hang recognizers, corrupted-report handling when expected, NMI backtrace parsing, and title fallback to the active function when reliable. Parser-relevant local signals: alternate title(s): `stall in corrupted`; expected corrupted flag is `Y`. First non-header signal: `[ 1722.511384] INFO: rcu_preempt detected stalls on CPUs/tasks: { 2} (detected by 0, t=65008 jiffies, g=48068, c=48067, q=7339)`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 6 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture is corrupted or truncated, the parser must stay conservative and avoid inventing a precise frame from unreliable text. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `INFO: rcu detected stall in corrupted`, type `HANG`, alternate titles `stall in corrupted`, corrupted `Y`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/58 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/580 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/580

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in do_journal_end`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `do_journal_end`, `reiserfs_sync_fs`, `sync_filesystem`, `generic_shutdown_super`, `kill_block_super`, `deactivate_locked_super`, `deactivate_super`, `cleanup_mnt`; expected panicked flag is `Y`. First non-header signal: `[  805.123956][ T8558] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 61 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in do_journal_end`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/580 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/581 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/581

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in pfkey_send_acquire`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format, skbuff panic preamble. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `skb_put.cold`, `pfkey_send_acquire`, `km_query`, `xfrm_state_find`, `xfrm_tmpl_resolve`, `xfrm_resolve_and_create_bundle`, `xfrm_lookup_with_ifid`, `xfrm_lookup_route`. First non-header signal: `[  280.626490][T13868] skbuff: skb_over_panic: text:ffffffff87ca4a76 len:232 put:72 head:ffff88801115a800 data:ffff88801115a800 tail:0xe8 end:0xc0 dev:<NULL>`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 52 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in pfkey_send_acquire`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/581 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/582 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/582

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in ipgre_header`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format, skbuff panic preamble. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `skb_push`, `ipgre_header`, `pppoe_sendmsg`, `sock_sendmsg`, `sock_write_iter`, `do_iter_readv_writev`, `do_iter_write`, `vfs_writev`. First non-header signal: `[   34.354336] skbuff: skb_under_panic: text:000000000470095b len:82 put:24 head:00000000f453c8df data:000000007cc2256c tail:0x3a end:0xc0 dev:gre0`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 46 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in ipgre_header`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/582 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/583 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/583

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in sctp_packet_transmit`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer, skbuff panic preamble. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `skb_put`, `sctp_packet_transmit`, `sctp_outq_flush`, `sctp_outq_uncork`, `sctp_do_sm`, `sctp_assoc_bh_rcv`, `sctp_inq_push`, `sctp_backlog_rcv`; expected panicked flag is `Y`. First non-header signal: `[  486.883962] skbuff: skb_over_panic: text:ffffffff847fe683 len:213316 put:213008 head:ffff8801c2fd3340 data:ffff8801c2fd33f8 tail:0x341fc end:0x7ec0 dev:<NULL>`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 61 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in sctp_packet_transmit`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/583 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/584 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/584

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in xt_rateest_tg_checkentry`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer, fortify buffer-overflow preamble. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `xt_rateest_tg_checkentry`, `xt_rateest_net_init`, `mutex_lock_io_nested`, `xt_find_target`, `xt_check_target`, `textify_hooks.constprop.0`, `find_check_entry.constprop.0`, `compat_get_entries`; expected panicked flag is `Y`. First non-header signal: `[   70.516302][ T8713] detected buffer overflow in strlen`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 93 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in xt_rateest_tg_checkentry`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/584 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/585 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/585

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in ucma_join_ip_multicast`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `ucma_join_ip_multicast`, `ucma_write`, `__vfs_write`, `vfs_write`, `SyS_write`, `do_syscall_64`, `entry_SYSCALL_64_after_hwframe`. First non-header signal: `[   24.127473] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 41 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in ucma_join_ip_multicast`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/585 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/586 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/586

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in do_ip_vs_set_ctl`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format, fortify buffer-overflow preamble. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `do_ip_vs_set_ctl`, `nf_setsockopt`, `ip_setsockopt`, `udp_setsockopt`, `ipv6_setsockopt`, `tcp_setsockopt`, `sock_common_setsockopt`, `__sys_setsockopt`. First non-header signal: `[ 1392.954057] detected buffer overflow in strlen`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 46 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in do_ip_vs_set_ctl`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/586 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/587 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/587

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in btree_readpage_end_io_hook`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `btree_readpage_end_io_hook.cold`, `end_bio_extent_readpage`, `bio_endio`, `end_workqueue_fn`, `btrfs_work_helper`, `process_one_work`, `worker_thread`, `kthread`. First non-header signal: `[   61.075073][   T26] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 34 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in btree_readpage_end_io_hook`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/587 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/588 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/588

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `INFO: rcu detected stall in io_sq_thread`, expected type `HANG`, and parser behavior for a RCU stall/hang diagnostic using x86/GCE syzkaller console format, RCU stall multi-line report. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises RCU stall/hang recognizers, corrupted-report handling when expected, NMI backtrace parsing, and title fallback to the active function when reliable. Parser-relevant local signals: key stack symbols include `dump_stack`, `lapic_can_unplug_cpu`, `nmi_cpu_backtrace.cold`, `nmi_trigger_cpumask_backtrace`, `arch_trigger_cpumask_backtrace`, `rcu_dump_cpu_stacks`, `find_next_bit`, `rcu_sched_clock_irq.cold`; alternate title(s): `stall in io_sq_thread`. First non-header signal: `[  589.079232] rcu: INFO: rcu_sched self-detected stall on CPU`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 51 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `INFO: rcu detected stall in io_sq_thread`, type `HANG`, alternate titles `stall in io_sq_thread`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/588 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/589 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/589

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `WARNING in macvlan_broadcast`, expected type `WARNING`, and parser behavior for a kernel WARNING/oops diagnostic using ARM backtrace format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises warning recognizers, panic-on-warn detection when present, and guilty-frame selection from the warning call trace rather than generic allocator or IRQ helpers. Parser-relevant local signals: key stack symbols include `dump_backtrace`, `show_stack`, `dump_stack`, `panic`, `__warn`, `warn_slowpath_fmt`, `__seqprop_assert.constprop.0`, `macvlan_broadcast`; expected panicked flag is `Y`. First non-header signal: `[   92.038906][   T19] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 95 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `WARNING in macvlan_broadcast`, type `WARNING`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/589 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/59 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/59

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `INFO: rcu detected stall in corrupted`, expected type `HANG`, and parser behavior for a RCU stall/hang diagnostic using RCU stall multi-line report. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction. It belongs to a compact cluster of intentionally corrupted or truncated fixtures where generic crash words appear but the expected title must degrade to `corrupted`.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises RCU stall/hang recognizers, corrupted-report handling when expected, NMI backtrace parsing, and title fallback to the active function when reliable. Parser-relevant local signals: alternate title(s): `stall in corrupted`; expected corrupted flag is `Y`. First non-header signal: `[  317.168127] INFO: rcu_sched detected stalls on CPUs/tasks: { 0} (detected by 1, t=2179 jiffies, g=740, c=739, q=1)`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 6 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture is corrupted or truncated, the parser must stay conservative and avoid inventing a precise frame from unreliable text. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `INFO: rcu detected stall in corrupted`, type `HANG`, alternate titles `stall in corrupted`, corrupted `Y`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/59 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/590 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/590

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KFENCE: use-after-free read in find_uprobe`, expected type `KFENCE-USE-AFTER-FREE-READ`, and parser behavior for a KFENCE memory-safety diagnostic using x86/GCE syzkaller console format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KFENCE-specific title/type mapping, allocation/free stack parsing, and frame selection that must skip generic helpers when a more meaningful object-use frame is present. Parser-relevant local signals: key stack symbols include `memcpy`, `find_uprobe`, `uprobe_apply`, `uprobe_perf_close`, `trace_uprobe_register`, `perf_uprobe_destroy`, `_free_event`, `perf_event_release_kernel`; alternate title(s): `bad-access in find_uprobe`. First non-header signal: `[  221.211609][ T9991] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 93 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KFENCE: use-after-free read in find_uprobe`, type `KFENCE-USE-AFTER-FREE-READ`, alternate titles `bad-access in find_uprobe`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/590 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/591 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/591

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KFENCE: out-of-bounds read in test_out_of_bounds_read`, expected type `KFENCE-READ`, and parser behavior for a KFENCE memory-safety diagnostic using KUnit/KFENCE self-test stack format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KFENCE-specific title/type mapping, allocation/free stack parsing, and frame selection that must skip generic helpers when a more meaningful object-use frame is present. Parser-relevant local signals: key stack symbols include `test_out_of_bounds_read`, `kunit_try_run_case`, `kunit_generic_run_threadfn_adapter`, `kthread`, `ret_from_fork`, `test_alloc`, `test_out_of_bounds_write`, `preempt_count_add`; alternate title(s): `bad-access in test_out_of_bounds_read`. First non-header signal: `[    3.317089] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 49 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KFENCE: out-of-bounds read in test_out_of_bounds_read`, type `KFENCE-READ`, alternate titles `bad-access in test_out_of_bounds_read`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/591 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/592 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/592

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KFENCE: out-of-bounds write in test_out_of_bounds_write`, expected type `KFENCE-WRITE`, and parser behavior for a KFENCE memory-safety diagnostic using KUnit/KFENCE self-test stack format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KFENCE-specific title/type mapping, allocation/free stack parsing, and frame selection that must skip generic helpers when a more meaningful object-use frame is present. Parser-relevant local signals: key stack symbols include `test_out_of_bounds_write`, `kunit_try_run_case`, `kunit_generic_run_threadfn_adapter`, `kthread`, `ret_from_fork`, `test_alloc`, `test_use_after_free_read`, `preempt_count_add`; alternate title(s): `bad-access in test_out_of_bounds_write`. First non-header signal: `[    3.980910] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 50 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KFENCE: out-of-bounds write in test_out_of_bounds_write`, type `KFENCE-WRITE`, alternate titles `bad-access in test_out_of_bounds_write`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/592 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/593 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/593

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KFENCE: use-after-free read in test_use_after_free_read`, expected type `KFENCE-USE-AFTER-FREE-READ`, and parser behavior for a KFENCE memory-safety diagnostic using KUnit/KFENCE self-test stack format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KFENCE-specific title/type mapping, allocation/free stack parsing, and frame selection that must skip generic helpers when a more meaningful object-use frame is present. Parser-relevant local signals: key stack symbols include `test_use_after_free_read`, `kunit_try_run_case`, `kunit_generic_run_threadfn_adapter`, `kthread`, `ret_from_fork`, `test_alloc`, `test_double_free`, `preempt_count_add`; alternate title(s): `bad-access in test_use_after_free_read`. First non-header signal: `[    4.252938] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 58 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KFENCE: use-after-free read in test_use_after_free_read`, type `KFENCE-USE-AFTER-FREE-READ`, alternate titles `bad-access in test_use_after_free_read`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/593 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/594 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/594

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KFENCE: invalid free in test_double_free`, expected type `KFENCE-INVALID-FREE`, and parser behavior for a KFENCE memory-safety diagnostic using KUnit/KFENCE self-test stack format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KFENCE-specific title/type mapping, allocation/free stack parsing, and frame selection that must skip generic helpers when a more meaningful object-use frame is present. Parser-relevant local signals: key stack symbols include `test_double_free`, `kunit_try_run_case`, `kunit_generic_run_threadfn_adapter`, `kthread`, `ret_from_fork`, `test_alloc`; alternate title(s): `invalid-free in test_double_free`. First non-header signal: `[    4.524933] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 32 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KFENCE: invalid free in test_double_free`, type `KFENCE-INVALID-FREE`, alternate titles `invalid-free in test_double_free`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/594 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/595 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/595

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KFENCE: invalid free in test_invalid_addr_free`, expected type `KFENCE-INVALID-FREE`, and parser behavior for a KFENCE memory-safety diagnostic using KUnit/KFENCE self-test stack format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KFENCE-specific title/type mapping, allocation/free stack parsing, and frame selection that must skip generic helpers when a more meaningful object-use frame is present. Parser-relevant local signals: key stack symbols include `test_invalid_addr_free`, `kunit_try_run_case`, `kunit_generic_run_threadfn_adapter`, `kthread`, `ret_from_fork`, `test_alloc`; alternate title(s): `invalid-free in test_invalid_addr_free`. First non-header signal: `[    4.764967] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 25 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KFENCE: invalid free in test_invalid_addr_free`, type `KFENCE-INVALID-FREE`, alternate titles `invalid-free in test_invalid_addr_free`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/595 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/596 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/596

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KFENCE: memory corruption in test_corruption`, expected type `KFENCE-MEMORY-CORRUPTION`, and parser behavior for a KFENCE memory-safety diagnostic using KUnit/KFENCE self-test stack format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KFENCE-specific title/type mapping, allocation/free stack parsing, and frame selection that must skip generic helpers when a more meaningful object-use frame is present. Parser-relevant local signals: key stack symbols include `test_corruption`, `kunit_try_run_case`, `kunit_generic_run_threadfn_adapter`, `kthread`, `ret_from_fork`, `test_alloc`. First non-header signal: `[    4.996949] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 24 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KFENCE: memory corruption in test_corruption`, type `KFENCE-MEMORY-CORRUPTION`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/596 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/597 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/597

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KFENCE: memory corruption in kunit_try_run_case`, expected type `KFENCE-MEMORY-CORRUPTION`, and parser behavior for a KFENCE memory-safety diagnostic using KUnit/KFENCE self-test stack format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KFENCE-specific title/type mapping, allocation/free stack parsing, and frame selection that must skip generic helpers when a more meaningful object-use frame is present. Parser-relevant local signals: key stack symbols include `test_kmalloc_aligned_oob_write`, `kunit_try_run_case`, `kunit_generic_run_threadfn_adapter`, `kthread`, `ret_from_fork`, `test_alloc`. First non-header signal: `[   10.396949] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 24 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KFENCE: memory corruption in kunit_try_run_case`, type `KFENCE-MEMORY-CORRUPTION`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/597 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/598 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/598

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KFENCE: invalid read in test_invalid_access`, expected type `KFENCE-READ`, and parser behavior for a KFENCE memory-safety diagnostic using KUnit/KFENCE self-test stack format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KFENCE-specific title/type mapping, allocation/free stack parsing, and frame selection that must skip generic helpers when a more meaningful object-use frame is present. Parser-relevant local signals: key stack symbols include `test_invalid_access`, `kunit_try_run_case`, `kunit_generic_run_threadfn_adapter`, `kthread`, `ret_from_fork`, `report_matches.part.0`, `preempt_count_add`, `_raw_spin_lock_irqsave`; alternate title(s): `bad-access in test_invalid_access`. First non-header signal: `[   10.613348] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 41 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KFENCE: invalid read in test_invalid_access`, type `KFENCE-READ`, alternate titles `bad-access in test_invalid_access`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/598 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/599 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/599

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `KFENCE: memory corruption in do_check_common`, expected type `KFENCE-MEMORY-CORRUPTION`, and parser behavior for a KFENCE memory-safety diagnostic using x86/GCE syzkaller console format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises KFENCE-specific title/type mapping, allocation/free stack parsing, and frame selection that must skip generic helpers when a more meaningful object-use frame is present. Parser-relevant local signals: key stack symbols include `krealloc`, `do_check_common`, `bpf_check`, `bpf_prog_load`, `__do_sys_bpf`, `do_syscall_64`, `entry_SYSCALL_64_after_hwframe`. First non-header signal: `[   98.860898][ T9916] ==================================================================`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 27 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `KFENCE: memory corruption in do_check_common`, type `KFENCE-MEMORY-CORRUPTION`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/599 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/6 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/6

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `WARNING: foo`, expected type `WARNING`, and parser behavior for a kernel WARNING/oops diagnostic using standard Linux printk/oops format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises warning recognizers, panic-on-warn detection when present, and guilty-frame selection from the warning call trace rather than generic allocator or IRQ helpers. Parser-relevant local signals: contains an explicit `REPORT:` block for exact extracted-body comparison. First non-header signal: `<6>[   85.501187] WARNING: foo`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 14 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. The explicit report body makes whitespace and prefix stripping regressions visible.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `WARNING: foo`, type `WARNING`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `yes`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/6 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/60 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/60

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `INFO: rcu detected stall in corrupted`, expected type `HANG`, and parser behavior for a RCU stall/hang diagnostic using RCU stall multi-line report. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction. It belongs to a compact cluster of intentionally corrupted or truncated fixtures where generic crash words appear but the expected title must degrade to `corrupted`.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises RCU stall/hang recognizers, corrupted-report handling when expected, NMI backtrace parsing, and title fallback to the active function when reliable. Parser-relevant local signals: key stack symbols include `something`; alternate title(s): `stall in corrupted`; expected corrupted flag is `Y`. First non-header signal: `[   50.583499] something`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 8 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture is corrupted or truncated, the parser must stay conservative and avoid inventing a precise frame from unreliable text. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `INFO: rcu detected stall in corrupted`, type `HANG`, alternate titles `stall in corrupted`, corrupted `Y`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/60 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/600 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/600

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `general protection fault in nl802154_add_llsec_key`, expected type `DoS`, and parser behavior for a KASAN memory-safety diagnostic using standard Linux printk/oops format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises architecture fault/oops recognizers, bad-access alternate title generation, and stack-frame extraction from the architecture-specific register dump. Parser-relevant local signals: key stack symbols include `genl_family_rcv_msg_doit`, `genl_rcv_msg`, `netlink_rcv_skb`, `genl_rcv`, `netlink_unicast`, `netlink_sendmsg`, `sock_sendmsg`, `____sys_sendmsg`; alternate title(s): `bad-access in nl802154_add_llsec_key`. First non-header signal: `[   65.899519][ T6734] general protection fault, probably for non-canonical address 0xdffffc0000000000: 0000 [#1] SMP KASAN`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 46 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `general protection fault in nl802154_add_llsec_key`, type `DoS`, alternate titles `bad-access in nl802154_add_llsec_key`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/600 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/601 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/601

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `SYZFAIL: negative running`, expected type `SYZ_FAILURE`, and parser behavior for a syzkaller executor failure diagnostic using standard Linux printk/oops format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises syzkaller executor failure parsing rather than kernel oops parsing, including the `SYZFAIL:` title namespace and crash type mapping. Parser-relevant local signals: no alternate flags beyond the header; the raw console body is the parser input. First non-header signal: `2021/02/21 12:37:19 executor 5 failed 11 times:`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 27 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `SYZFAIL: negative running`, type `SYZ_FAILURE`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/601 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/602 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/602

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `BUG: unable to handle kernel paging request in vmx_vcpu_run`, expected type `MEMORY_SAFETY_BUG`, and parser behavior for a architecture fault/oops diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises architecture fault/oops recognizers, bad-access alternate title generation, and stack-frame extraction from the architecture-specific register dump. Parser-relevant local signals: key stack symbols include `intel_pmu_pebs_disable`, `vmx_vcpu_run`, `asm_sysvec_apic_timer_interrupt`, `vmx_set_host_fs_gs`, `vmx_prepare_switch_to_guest`, `__fpregs_load_activate`, `vcpu_enter_guest`, `irqentry_exit`; alternate title(s): `bad-access in vmx_vcpu_run`; expected panicked flag is `Y`. First non-header signal: `[   67.921889][T10420] Not enough msr switch entries. Can't add msr abd1e896`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 98 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `BUG: unable to handle kernel paging request in vmx_vcpu_run`, type `MEMORY_SAFETY_BUG`, alternate titles `bad-access in vmx_vcpu_run`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/602 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/603 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/603

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `(no crash expected)`, expected type `UnknownType/no TYPE header`, and parser behavior for a negative/no-crash console fixture using standard Linux printk/oops format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction. This is intentionally a no-crash fixture: it contains alarming words such as panic/status/warn in driver logs, but no expected `TITLE` header.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises the negative path: `ContainsCrash` must ignore noisy subsystem messages and `Parse` must return no report. Parser-relevant local signals: no alternate flags beyond the header; the raw console body is the parser input. First non-header signal: `[    3.576566] [drm:sde_dbg_init:3432] evtlog_status: enable:0, panic:1, dump:2`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return false, `Parse` must not produce a report, and `ParseFrom` must remain consistent with the no-crash result. The raw log has 4 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture is negative, any returned report is a false positive; the parser must distinguish ordinary driver status text from real oops signatures. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `(no crash expected)`, type `UnknownType/no TYPE header`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must return no crash for this noisy non-oops console text, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/603 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/604 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/604

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `Internal error in el0_svc_naked`, expected type `DoS`, and parser behavior for a architecture fault/oops diagnostic using arm64 oops/unwinder format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction. The leading comments document that `LR` names `SyS_darby`, but the parser should not use LR because it is often duplicated or misleading outside the call trace.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises architecture fault/oops recognizers, bad-access alternate title generation, and stack-frame extraction from the architecture-specific register dump. Parser-relevant local signals: key stack symbols include `el0_svc_naked`; alternate title(s): `bad-access in el0_svc_naked`; fixture comment: Note: there is SyS_darby in LR, it looks more relevant, but for some reason it's not present in the call trace. We don't parse LR because usually it's either wrong or duplicated in call trace, also not present on other arches. This looks like a bug in the arm64 kernel unwinder.. First non-header signal: `[   28.231851] Internal error: Oops - SP/PC alignment exception: 8a000000 [#1] PREEMPT SMP`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 64 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `Internal error in el0_svc_naked`, type `DoS`, alternate titles `bad-access in el0_svc_naked`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/604 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/605 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/605

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `(no crash expected)`, expected type `UnknownType/no TYPE header`, and parser behavior for a negative/no-crash console fixture using standard Linux printk/oops format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction. This is intentionally a no-crash fixture: it contains alarming words such as panic/status/warn in driver logs, but no expected `TITLE` header.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises the negative path: `ContainsCrash` must ignore noisy subsystem messages and `Parse` must return no report. Parser-relevant local signals: no alternate flags beyond the header; the raw console body is the parser input. First non-header signal: `[    3.906407] CAM_INFO: CAM-ISP: cam_isp_dev_probe: 122 Camera ISP probe complete`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return false, `Parse` must not produce a report, and `ParseFrom` must remain consistent with the no-crash result. The raw log has 11 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture is negative, any returned report is a false positive; the parser must distinguish ordinary driver status text from real oops signatures. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `(no crash expected)`, type `UnknownType/no TYPE header`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must return no crash for this noisy non-oops console text, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/605 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/606 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/606

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `WARNING in kvm_wait`, expected type `WARNING`, and parser behavior for a kernel WARNING/oops diagnostic using x86/GCE syzkaller console format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises warning recognizers, panic-on-warn detection when present, and guilty-frame selection from the warning call trace rather than generic allocator or IRQ helpers. Parser-relevant local signals: key stack symbols include `raw_local_irq_restore`, `kvm_wait`, `__pv_queued_spin_lock_slowpath`, `do_raw_spin_lock`, `lock_sock_nested`, `tcp_sendmsg`, `inet_sendmsg`, `sock_sendmsg`. First non-header signal: `[   60.014572][ T4392] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 44 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `WARNING in kvm_wait`, type `WARNING`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/606 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/607 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/607

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `BUG: unable to handle kernel access to user memory in schedule_tail`, expected type `UnknownType/no TYPE header`, and parser behavior for a architecture fault/oops diagnostic using RISC-V register/oops format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises architecture fault/oops recognizers, bad-access alternate title generation, and stack-frame extraction from the architecture-specific register dump. Parser-relevant local signals: alternate title(s): `bad-access in schedule_tail`. First non-header signal: `[  472.619615][ T5233] Unable to handle kernel access to user memory without uaccess routines at virtual address 000000000cc6b0d0`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 28 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `BUG: unable to handle kernel access to user memory in schedule_tail`, type `UnknownType/no TYPE header`, alternate titles `bad-access in schedule_tail`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/607 -->
