<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/329 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/329

## Purpose
This fixture is a syzkaller Linux report-parser oracle for repeated page faults in `bpf_prog_kallsyms_find`. The expected metadata says the parser must report `BUG: unable to handle kernel paging request in bpf_prog_kallsyms_find`, classify it as `MEMORY_SAFETY_BUG`, keep the alternative `bad-access in bpf_prog_kallsyms_find`, and set both corrupted and panicked flags.

## Important APIs, Types, And Functions
The file is test data consumed by `pkg/report` test loading, not executable code. Its API surface is the header contract: `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, followed by the raw log. The kernel signature of interest is the x86 oops with `RIP: bpf_prog_kallsyms_find+0x289/0x4a0`, repeated many times with the same faulting address and empty `Call Trace:` sections.

## Control Flow
The parser reads the metadata block, then scans the console stream from the first `BUG: unable to handle kernel paging request`. The fixture stresses first-report selection and duplicate-oops handling: many nearly identical page-fault records follow, so `findFirstOops`, title extraction, and report trimming must not drift to later duplicates or panic epilogue text.

## State And Persistence
All state is persistent expected data in the fixture. The important persisted flags are `CORRUPTED: Y` and `PANICKED: Y`, reflecting a damaged report stream and eventual panic behavior. Dynamic addresses, CPUs, PIDs, and registers are intentionally present for normalizer coverage.

## Dependencies And Integration Points
This integrates with syzkaller's Linux oops regex catalog, bad-access title normalizer, BPF symbol handling, corruption detection, and crash type mapping. It is loaded by the report parser tests through the `report` testdata directory.

## Risks
The repeated same-site oopses can cause overlong or unstable selected reports if duplicate suppression changes. The empty call traces also mean the parser must rely primarily on the RIP symbol.

## Test Signals
The stable signal is title `BUG: unable to handle kernel paging request in bpf_prog_kallsyms_find`, type `MEMORY_SAFETY_BUG`, alt `bad-access in bpf_prog_kallsyms_find`, corrupted and panicked flags set, and a selected report anchored at the first `bpf_prog_kallsyms_find` RIP.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/329 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/33 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/33

## Purpose
This compact fixture verifies lockdep parsing for an inconsistent lock state in `inet_ehash_insert`. The expected title is `inconsistent lock state in inet_ehash_insert`, type `LOCKDEP`, with `CORRUPTED: Y`.

## Important APIs, Types, And Functions
The consumed API is the report fixture header schema plus a short lockdep body. The key runtime markers are `[ INFO: inconsistent lock state ]`, the transition text `inconsistent {IN-SOFTIRQ-W} -> {SOFTIRQ-ON-W} usage`, and the lock site `inet_ehash_insert+0x240/0xad0`.

## Control Flow
Parser control flow is minimal: metadata is read, the first lockdep banner is found, and the lock site is extracted from the `at:` clause. The fixture is short enough that report-boundary logic has little surrounding noise.

## State And Persistence
The fixture persists only expected title/type/corruption metadata and the raw kernel log. The corrupted flag records that this short excerpt is not a complete, clean lockdep report.

## Dependencies And Integration Points
It depends on Linux lockdep pattern recognition, stack/site extraction from lockdep prose, and crash type mapping to `LOCKDEP`. It integrates through syzkaller's generic `TestParse` testdata loop.

## Risks
Because the body is truncated, parser changes that require a complete lockdep dependency chain would break this regression.

## Test Signals
The parser should still select `inet_ehash_insert` as the title function and classify the report as `LOCKDEP` despite the short input.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/33 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/330 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/330

## Purpose
This fixture verifies parsing of a scheduler-detected stack overflow during ext4 writeback. The expected title is `kernel panic: corrupted stack end in wb_workfn`, with alt `stack-overflow in wb_workfn`, type `DoS`, and `PANICKED: Y`.

## Important APIs, Types, And Functions
The important kernel path is `Kernel panic - not syncing: corrupted stack end detected inside scheduler`, workqueue `writeback wb_workfn`, and a stack from `__schedule` through memory reclaim and ext4 allocation/writeback: `shrink_page_list`, `ext4_mb_new_blocks`, `ext4_ext_map_blocks`, `ext4_writepages`, and `wb_workfn`.

## Control Flow
The Linux reporter must treat the panic line as the root oops, then walk the stack to the best frame for title attribution. The selected function is not the immediate scheduler frame, but the writeback worker context visible in the workqueue and lower stack.

## State And Persistence
Persistent state is the expected metadata and raw panic log. The log includes stack-depth warnings from other processes, which are transient state used to test that unrelated depth messages do not become the title.

## Dependencies And Integration Points
This depends on panic-line parsing, stack-overflow alternative title generation, workqueue context recognition, and crash type mapping to `DoS`.

## Risks
Parser ranking can accidentally choose `__schedule`, `retint_kernel`, or memory reclaim frames instead of `wb_workfn`.

## Test Signals
Stable output should keep the `wb_workfn` title and alt, mark the report panicked, and ignore unrelated `used greatest stack depth` lines as secondary noise.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/330 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/331 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/331

## Purpose
This is a second `corrupted stack end` writeback fixture for the same expected crash title as report 330. It protects parser stability across a shorter path through allocator sleep instead of interrupt preemption.

## Important APIs, Types, And Functions
Key markers are the panic line, workqueue `writeback wb_workfn`, and stack frames `schedule_timeout_uninterruptible`, `__alloc_pages_slowpath`, `ext4_mb_load_buddy_gfp`, `ext4_writepages`, `wb_writeback`, and `wb_workfn`.

## Control Flow
After headers, the parser scans the panic body, builds the report around the panic, and derives `wb_workfn` from the workqueue/writeback stack. It must normalize this variant to the same title and alternative as neighboring stack-end fixtures.

## State And Persistence
The file persists expected `DoS` and `PANICKED` state. It has no mutable state; PIDs, timestamps, and allocation state in the log are raw kernel context.

## Dependencies And Integration Points
It integrates with the Linux panic parser, scheduler stack-overflow recognizer, workqueue frame selection, and ext4/writeback symbol filtering.

## Risks
The immediate frames are scheduler and page allocator functions, so frame-priority changes can regress attribution away from `wb_workfn`.

## Test Signals
The report should parse to `kernel panic: corrupted stack end in wb_workfn` with `stack-overflow in wb_workfn` and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/331 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/332 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/332

## Purpose
This fixture covers the same corrupted-stack-end panic class on a 4.20-rc7 kernel, with an ext4 path that includes `__remove_mapping` and bitmap loading. It validates version-insensitive title extraction.

## Important APIs, Types, And Functions
Important frames include `panic`, `__schedule`, `_raw_spin_unlock_irqrestore`, `__remove_mapping`, `shrink_page_list`, `ext4_read_block_bitmap_nowait`, `ext4_mb_mark_diskspace_used`, `ext4_writepages`, and `wb_workfn`.

## Control Flow
The parser enters through the panic marker, then finds the writeback context and expected title. The body has normal call-trace structure without a separate explicit `REPORT:` block.

## State And Persistence
Expected persisted state is `TYPE: DoS`, `ALT: stack-overflow in wb_workfn`, and `PANICKED: Y`. The raw log preserves version, register, and ext4 allocator details for regression coverage.

## Dependencies And Integration Points
This depends on Linux stack-overflow title normalization and syzkaller's logic that avoids choosing allocator or filesystem helper frames over the worker function.

## Risks
The report might be misclassified as a generic panic if the `corrupted stack end detected inside scheduler` string is not recognized.

## Test Signals
Parser output must match the shared `wb_workfn` title and alt and preserve the panicked flag.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/332 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/333 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/333

## Purpose
This fixture exercises corrupted-stack-end parsing when the visible interrupted RIP is a lockdep helper, not the final writeback worker. It ensures syzkaller still reports `wb_workfn`.

## Important APIs, Types, And Functions
The raw stack starts at `lock_is_held_type`, then moves through `rcu_read_lock_held`, slab shrinkers, ext4 inode/extent write paths, and finally `wb_workfn`. The expected API contract sets title, alt, type `DoS`, and panicked state.

## Control Flow
The parser must use panic context and workqueue/stack ranking rather than the first RIP alone. It trims a long but coherent writeback/reclaim trace and assigns the stable stack-overflow alt title.

## State And Persistence
Persistent metadata is the parser oracle. Runtime state in the log includes writeback worker identity, ext4 allocation state, and panic status.

## Dependencies And Integration Points
It depends on report frame scoring, lockdep helper filtering, ext4 stack recognition, and panic handling in `pkg/report`.

## Risks
A naive first-frame title would become `lock_is_held_type`, which would hide the intended stack-overflow signature.

## Test Signals
The parsed title must remain `kernel panic: corrupted stack end in wb_workfn`, with type `DoS` and panicked flag.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/333 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/334 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/334

## Purpose
This corrupted-stack-end fixture verifies title stability in the presence of an interleaved OOM-killer line. The expected root remains writeback stack overflow in `wb_workfn`.

## Important APIs, Types, And Functions
Important frames and markers are `Kernel panic - not syncing`, workqueue `writeback wb_workfn`, interrupted RIP `__add_to_page_cache_locked`, an OOM-killer message, and ext4/writeback frames ending at `wb_workfn`.

## Control Flow
The parser scans the panic, ignores the OOM status line as noise, and derives the title from the writeback worker context. It must not treat the OOM line as a separate report.

## State And Persistence
The fixture persists panicked `DoS` metadata and raw console noise around memory pressure. No mutable state exists outside the checked-in sample.

## Dependencies And Integration Points
It integrates with panic parsing, stack-overflow alternative generation, OOM-message filtering, and workqueue-aware frame selection.

## Risks
Interleaving can cause report-boundary or title contamination if OOM messages are not recognized as incidental.

## Test Signals
The expected parser signal is unchanged `wb_workfn` title/alt with `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/334 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/335 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/335

## Purpose
This fixture verifies lockdep warning parsing when the log is known corrupted by fault injection and panic-on-warn. The expected title is `WARNING: locking bug in corrupted`, type `LOCKDEP`, with corrupted and panicked flags.

## Important APIs, Types, And Functions
The log begins with `FAULT_INJECTION: forcing a failure`, then a warning at `kernel/locking/lockdep.c:3553 lock_downgrade`. The surrounding syscall path includes tty and ioctl frames such as `__tty_buffer_request_room`, `n_tty_ioctl`, `tty_ioctl`, `ksys_ioctl`, and a user RIP.

## Control Flow
The reporter must notice the warning and lockdep context, but because corruption prevents reliable function attribution, it uses `corrupted` in the title. The panic-on-warn secondary stack is part of the selected report but should not replace the root classification.

## State And Persistence
The persisted state is `TYPE: LOCKDEP`, `CORRUPTED: Y`, and `PANICKED: Y`. Runtime state includes failslab settings and panic-on-warn behavior.

## Dependencies And Integration Points
It depends on warning parsing, lockdep bug detection, corruption heuristics, panic-on-warn detection, and noisy fault-injection filtering.

## Risks
The parser can overfit to the tty/ioctl syscall path or panic frame and lose the lockdep classification.

## Test Signals
Stable parsing means title `WARNING: locking bug in corrupted`, type `LOCKDEP`, both flags set, and no selection of `lock_downgrade` as a clean non-corrupted title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/335 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/336 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/336

## Purpose
This fixture covers debugobjects/ODEBUG warning parsing from a corrupted and panicking log. The expected title is `WARNING: ODEBUG bug in corrupted`, type `WARNING`, corrupted and panicked.

## Important APIs, Types, And Functions
The leading marker is `ODEBUG: free active ... object type: timer_list hint: delayed_work_timer_fn`, followed by `WARNING` at `lib/debugobjects.c:287 debug_print_object`. Stack context includes socket allocation/sendmsg on one side and cleanup workqueue frames such as `kobject_delayed_cleanup`, `disk_release`, and `device_release`.

## Control Flow
The parser must prefer the ODEBUG warning class over later panic frames, then mark the report corrupted because multiple interleaved stacks and fault-injection context reduce reliable attribution.

## State And Persistence
The fixture persists the expected warning type plus corrupted/panicked flags. The runtime state includes active timer debug object state and panic-on-warn transition.

## Dependencies And Integration Points
It depends on ODEBUG-specific report patterns, generic warning parsing, panic detection, and report boundary logic for interleaved traces.

## Risks
Later cleanup stack frames can look like better function names; selecting them would lose the ODEBUG regression.

## Test Signals
The expected parse is `WARNING: ODEBUG bug in corrupted` with type `WARNING`, `CORRUPTED: Y`, and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/336 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/337 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/337

## Purpose
This fixture validates direct sysrq crash panic parsing. The expected title is `kernel panic: sysrq triggered crash`, type `DoS`, with `PANICKED: Y`.

## Important APIs, Types, And Functions
Key markers are `Kernel panic - not syncing: sysrq triggered crash`, `sysrq_handle_crash`, `__handle_sysrq`, `write_sysrq_trigger`, `proc_reg_write`, `vfs_write`, and `ksys_write`. The fixture also includes an explicit cleaned `REPORT:` block.

## Control Flow
The parser reads headers, scans the raw log, and compares the selected report with the explicit `REPORT:` section. It must preserve the sysrq panic as the root report and not over-trim the user-space write path.

## State And Persistence
Persistent state includes title/type/panic metadata plus the explicit expected report body. Runtime state is a write to the sysrq trigger from a syzkaller executor.

## Dependencies And Integration Points
It integrates with panic parsing, sysrq-specific title extraction, explicit `REPORT:` comparison in testdata, and report text normalization that strips printk prefixes.

## Risks
Because sysrq is intentional, classification must remain `DoS` rather than memory-safety or warning. Changes to report-body prefix stripping can affect the explicit report comparison.

## Test Signals
The parser should output the exact sysrq panic title and the report body beginning with `Kernel panic - not syncing: sysrq triggered crash`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/337 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/338 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/338

## Purpose
This fixture verifies KASAN slab-out-of-bounds write parsing for module init code, normalizing from the immediate buggy helper to `do_one_initcall`. The expected title is `KASAN: slab-out-of-bounds Write in do_one_initcall`, alt `bad-access in do_one_initcall`, type `KASAN-WRITE`.

## Important APIs, Types, And Functions
Important markers include `BUG: KASAN: slab-out-of-bounds in kmalloc_oob_right`, `Write` access metadata, `__asan_report_store1_noabort`, `kmalloc_oob_right`, `kmalloc_tests_init`, `do_one_initcall`, `do_init_module`, `load_module`, and `__do_sys_init_module`.

## Control Flow
The parser consumes the KASAN report, recognizes a write, filters internal test-module helpers where appropriate, and chooses the stable initcall frame. It also handles allocation/free stack sections after the primary fault stack.

## State And Persistence
The fixture persists KASAN type and alt metadata. The raw log stores allocation provenance and module-loading state but no mutable repository state.

## Dependencies And Integration Points
It depends on KASAN read/write classification, bad-access alt generation, module suffix handling like `[test_kasan]`, and frame-priority logic that can select `do_one_initcall`.

## Risks
Parser changes might title the report as `kmalloc_oob_right` or `kmalloc_tests_init`, changing deduplication semantics.

## Test Signals
Expected output keeps title `KASAN: slab-out-of-bounds Write in do_one_initcall`, type `KASAN-WRITE`, and alt `bad-access in do_one_initcall`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/338 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/339 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/339

## Purpose
This fixture covers a general protection fault caused by sysrq crash handling. The expected title is `general protection fault in sysrq_handle_crash`, alt `bad-access in sysrq_handle_crash`, type `DoS`, and panicked.

## Important APIs, Types, And Functions
The stack is anchored at `RIP: sysrq_handle_crash+0x5e/0xd0`, then `__handle_sysrq`, `write_sysrq_trigger`, `proc_reg_write`, `__vfs_write`, `vfs_write`, `ksys_write`, and syscall return. It later includes `Kernel panic - not syncing: Fatal exception`.

## Control Flow
The reporter must select the initial GPF report before the fatal-exception panic, normalize the bad-access alt, and mark the crash panicked due to the later panic line.

## State And Persistence
The expected metadata is persisted in the header. Runtime state is a sysrq-trigger write that causes the kernel exception and panic.

## Dependencies And Integration Points
It depends on x86 exception parsing, bad-access alt generation, sysrq symbol handling, and panic-after-oops detection.

## Risks
If panic lines take precedence over the GPF, the title would become generic and lose the faulting function.

## Test Signals
The parser should return the GPF title in `sysrq_handle_crash` and keep `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/339 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/34 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/34

## Purpose
This short fixture verifies suspicious RCU usage detection when the report is corrupted or truncated. The expected title is `INFO: suspicious RCU usage in corrupted`.

## Important APIs, Types, And Functions
The key marker is `[ INFO: suspicious RCU usage. ]`. There are no complete stacks in this very small sample, so the parser's API contract is mostly header recognition and corrupted-title generation.

## Control Flow
The reporter reads the metadata, finds the RCU info banner, and cannot derive a reliable function. It therefore uses `corrupted` as the title function.

## State And Persistence
Persistent state is the expected title and `CORRUPTED: Y`. The fixture has no mutable state or explicit type header.

## Dependencies And Integration Points
It depends on RCU info pattern recognition and corruption heuristics in the Linux reporter.

## Risks
Requiring a full RCU splat would break this intentionally minimal regression.

## Test Signals
The stable parse is `INFO: suspicious RCU usage in corrupted` with corruption set.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/34 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/340 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/340

## Purpose
This is a KASAN slab-out-of-bounds write fixture similar to report 338, but with an interleaved CPU context line around `kfree`. It verifies robust stack parsing under mixed printk prefixes.

## Important APIs, Types, And Functions
Key markers include `BUG: KASAN: slab-out-of-bounds in memcpy`, the call chain through `kmalloc_oob_right`, `kmalloc_tests_init`, `do_one_initcall`, module load frames, and an interleaved `[ C3] kfree` line.

## Control Flow
The parser must preserve the KASAN write report, ignore the interleaved CPU-only line as noise, and still choose `do_one_initcall` for the expected title and bad-access alt.

## State And Persistence
Persistent state is title/alt/type metadata. The raw log preserves module init state, KASAN allocation metadata, and mixed context prefixes.

## Dependencies And Integration Points
It integrates with KASAN write classification, prefix stripping for `[ T...]` and `[ C...]` contexts, and frame-priority logic for module init reports.

## Risks
Interleaved lines can break stack continuity or cause false selection of `kfree`/`memcpy`.

## Test Signals
The expected output is `KASAN: slab-out-of-bounds Write in do_one_initcall`, alt `bad-access in do_one_initcall`, type `KASAN-WRITE`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/340 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/341 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/341

## Purpose
This small fixture checks a corrupted generic warning with panic-on-warn. The expected title is `WARNING in corrupted`, type `WARNING`, with corrupted and panicked flags.

## Important APIs, Types, And Functions
The visible warning is at `arch/x86/kernel/irq_64.c:61 handle_irq+0x2cb/0x3d8`, followed immediately by `Kernel panic - not syncing: panic_on_warn set ...` and a short call-trace marker.

## Control Flow
The reporter detects the warning but cannot produce a stable non-corrupted function title from the truncated context, then marks the panic state from the panic-on-warn line.

## State And Persistence
State is entirely fixture metadata plus raw log. `CORRUPTED: Y` records the incomplete report body.

## Dependencies And Integration Points
It depends on generic warning recognition, corrupted-title fallback, and panic-on-warn detection.

## Risks
If parser heuristics start trusting the visible `handle_irq` site, the expected `corrupted` title would regress.

## Test Signals
The parse should remain `WARNING in corrupted`, type `WARNING`, `CORRUPTED: Y`, `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/341 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/342 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/342

## Purpose
This is another minimal corrupted warning fixture with panic-on-warn. It protects fallback behavior for short warning excerpts.

## Important APIs, Types, And Functions
The body contains a warning line and panic-on-warn context but not enough reliable stack detail for a stable function-specific title. The expected type is `WARNING`.

## Control Flow
The parser reads the generic warning, applies corrupted fallback title logic, and sets the panicked flag from the following kernel panic line.

## State And Persistence
The persistent oracle is `TITLE: WARNING in corrupted`, `TYPE: WARNING`, `CORRUPTED: Y`, and `PANICKED: Y`.

## Dependencies And Integration Points
This depends on warning regex coverage and corrupted report heuristics in the Linux reporter.

## Risks
Small formatting changes in warning detection can make short corrupted warnings disappear or become over-attributed.

## Test Signals
Expected output is exactly `WARNING in corrupted` with type `WARNING` and both flags set.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/342 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/343 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/343

## Purpose
This large fixture verifies KASAN stack-out-of-bounds read parsing in a heavily corrupted IPv6/GUE/UDP error path. The expected title is `KASAN: stack-out-of-bounds Read in __udp6_lib_err`, alt `bad-access in __udp6_lib_err`, type `KASAN-READ`, corrupted and panicked.

## Important APIs, Types, And Functions
The initial KASAN marker is `BUG: KASAN: stack-out-of-bounds in debug_lockdep_rcu_enabled.part.0`, with repeated recursive frames through `__udp6_lib_err`, `udpv6_err`, `gue6_err_proto_handler`, and `gue6_err`. Later corruption includes list-debug failures, usercopy/slab complaints, `__list_add_valid`, futex wakeup frames, circular-locking reports, and a final fatal exception panic.

## Control Flow
The parser must select the first KASAN report, then score the meaningful stack frame as `__udp6_lib_err` rather than internal helpers or later corrupted secondary failures. It also needs to mark corruption because task names, PIDs, stack pointers, list state, and follow-on reports are visibly damaged.

## State And Persistence
The file persists all expected metadata and a long raw log with repeated recursion and secondary crashes. Runtime state includes IPv6 tunnel error recursion, corrupted task identity, damaged lists, and final panic.

## Dependencies And Integration Points
This fixture exercises KASAN access-type parsing, bad-access alt generation, repeated frame handling, corruption detection, report-boundary selection, and panic-after-report detection.

## Risks
The biggest risk is selecting a later `kernel BUG`, lockdep circular dependency, or `__list_add_valid` crash instead of the initial KASAN report. The recursive stack can also cause unstable title frame ranking.

## Test Signals
Stable parsing keeps `KASAN: stack-out-of-bounds Read in __udp6_lib_err`, type `KASAN-READ`, alt `bad-access in __udp6_lib_err`, and both corrupted and panicked flags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/343 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/344 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/344

## Purpose
This fixture covers stack guard page overflow detection in a corrupted recursive IPv6 error path. The expected title is `BUG: stack guard page was hit in corrupted`, with alt `stack-overflow in corrupted`, corrupted and panicked.

## Important APIs, Types, And Functions
The leading markers are `BUG: stack guard page was hit` and `kernel stack overflow (double-fault)`. The visible RIP is `__udp6_lib_lookup`, followed by many recursive `__udp6_lib_err`, `udplitev6_err`, and `gue6_err` frames before networking receive and ksoftirqd frames.

## Control Flow
The parser must recognize stack-guard overflow as the primary oops and fall back to `corrupted` because the recursive trace and overflow state make specific function attribution unreliable. It sets panic from `Kernel panic - not syncing: Fatal exception in interrupt`.

## State And Persistence
Persistent state is title/alt/corrupted/panicked metadata. The raw log preserves stack range, double-fault registers, softirq context, and reboot line.

## Dependencies And Integration Points
It depends on stack-guard page patterns, stack-overflow alt generation, recursive stack trimming, and interrupt panic detection.

## Risks
The parser could select `__udp6_lib_lookup` as a precise title, but the expected behavior is conservative due to corruption.

## Test Signals
Expected output keeps `BUG: stack guard page was hit in corrupted`, alt `stack-overflow in corrupted`, and both flags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/344 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/345 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/345

## Purpose
This fixture verifies warning parsing for XFRM namespace cleanup. The expected title is `WARNING in xfrm_state_fini`, type `WARNING`, with panicked flag.

## Important APIs, Types, And Functions
The key warning is at `net/xfrm/xfrm_state.c:2381 xfrm_state_fini+0x440/0x5c0`. The cleanup stack includes `xfrm_net_exit`, `ops_exit_list.isra.0`, `cleanup_net`, `process_one_work`, and worker thread frames.

## Control Flow
The parser must locate the warning after earlier setup/fault-injection noise and select the XFRM cleanup function. It also detects `panic_on_warn set` as the panicked state.

## State And Persistence
The fixture persists warning type and panic metadata. Runtime state includes network namespace teardown on the `netns` workqueue.

## Dependencies And Integration Points
It depends on warning-at-file-line parsing, symbol extraction from RIP, workqueue context handling, and panic-on-warn detection.

## Risks
Preceding allocation failure or netdevice-event traces could be mistaken for the root report.

## Test Signals
Parser output should be `WARNING in xfrm_state_fini`, `TYPE: WARNING`, `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/345 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/346 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/346

## Purpose
This is a second XFRM cleanup warning fixture for `xfrm_state_fini`, preserving parser stability across slightly different interleaving and prefix formats.

## Important APIs, Types, And Functions
The significant marker is the warning at `net/xfrm/xfrm_state.c:2381 xfrm_state_fini+0x440/0x5c0`, with stack frames `xfrm_net_exit`, `ops_exit_list.isra.0`, `cleanup_net`, and workqueue execution.

## Control Flow
The reporter scans past earlier noise, selects the warning block, derives the title from `xfrm_state_fini`, and marks panic-on-warn.

## State And Persistence
The header persists `TITLE: WARNING in xfrm_state_fini`, `TYPE: WARNING`, and `PANICKED: Y`. The body stores raw kernel timing and task context.

## Dependencies And Integration Points
It integrates with Linux warning parsing, XFRM symbol extraction, prefixed printk cleanup, and panic detection.

## Risks
The similarity to reports 345, 347, and 348 means deduplication-sensitive changes must keep identical titles for equivalent crashes.

## Test Signals
The test signal is identical warning title/type/panic metadata for this input variant.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/346 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/347 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/347

## Purpose
This fixture tests XFRM warning selection when an earlier failslab/netdevice event trace precedes the actual warning. The expected result remains `WARNING in xfrm_state_fini`.

## Important APIs, Types, And Functions
The early stack includes `__should_failslab`, `kmem_cache_alloc_trace`, `netdevice_event`, notifier calls, ioctl syscall frames, and user RIP. The later root warning is `xfrm_state_fini` on workqueue `netns cleanup_net`.

## Control Flow
The parser must not stop at the first call trace. It needs to find the warning line, attach the following XFRM cleanup stack, and mark `PANICKED: Y` from panic-on-warn.

## State And Persistence
Persistent state is warning title/type/panic metadata. Runtime state includes injected allocation failures and namespace cleanup teardown.

## Dependencies And Integration Points
It depends on root-report selection amid pre-report traces, prefixed context handling, and workqueue stack extraction.

## Risks
An overly eager parser could use `netdevice_event` or `ioctl` as the title before reaching the warning.

## Test Signals
Stable output is `WARNING in xfrm_state_fini`, type `WARNING`, panicked.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/347 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/348 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/348

## Purpose
This is another XFRM cleanup warning variant, using CPU context prefixes like `[ C1]` rather than normal task prefixes. It verifies prefix normalization.

## Important APIs, Types, And Functions
Important markers are the prelude allocation/failslab call trace and the warning at `xfrm_state_fini+0x440/0x5c0`, followed by `xfrm_net_exit`, `ops_exit_list.isra.0`, `cleanup_net`, and worker frames.

## Control Flow
The parser strips or normalizes CPU prefixes, skips pre-warning noise, selects the XFRM warning, and records the panic-on-warn state.

## State And Persistence
The fixture persists expected title/type/panic state. The raw body preserves the unusual CPU-only printk prefix format.

## Dependencies And Integration Points
It depends on printk prefix parsing, warning extraction, workqueue cleanup stack handling, and panic detection.

## Risks
Prefix changes can cause the Linux reporter to miss stack frames or report boundaries.

## Test Signals
Expected output remains `WARNING in xfrm_state_fini`, `TYPE: WARNING`, `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/348 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/349 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/349

## Purpose
This fixture validates hung-task parsing for ext4/jbd2 journal commits. The expected title is `INFO: task hung in jbd2_journal_commit_transaction`, alt `hang in jbd2_journal_commit_transaction`, type `HANG`, and panicked.

## Important APIs, Types, And Functions
The root marker is `INFO: task jbd2/sda-8:3563 blocked for more than 140 seconds`. The first stack contains `__wait_on_buffer` and `jbd2_journal_commit_transaction`; a second blocked writeback worker includes `wbt_wait`, block I/O, `ext4_writepages`, and `wb_workfn`.

## Control Flow
The parser must choose the first hung-task report and title it from the blocked task's meaningful stack, not from later writeback worker hangs. Panic is inferred from later hung-task panic/reboot context.

## State And Persistence
The fixture stores expected hang metadata and the raw multi-task blocked report. Runtime state is journal and writeback I/O waiting.

## Dependencies And Integration Points
It depends on hung-task recognizers, blocked-task stack selection, alt generation for `hang in`, and panic detection.

## Risks
Multiple blocked tasks can cause unstable title selection if ordering or stack scoring changes.

## Test Signals
The parser must preserve `jbd2_journal_commit_transaction` as the title function and classify as `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/349 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/35 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/35

## Purpose
This fixture verifies suspicious RCU usage parsing with an explicit `START:` directive. The expected title is `INFO: suspicious RCU usage in corrupted`.

## Important APIs, Types, And Functions
The important parser contract includes `START: [   37.540478] [ INFO: suspicious RCU usage. ]`, which tells the test harness where the expected report begins. The visible stack includes `vcpu_load+0x22/0x70`, but corruption prevents precise title attribution.

## Control Flow
After reading headers, the test harness uses the `START` marker to align expected report extraction. The Linux reporter detects the RCU info banner and emits the corrupted fallback title.

## State And Persistence
Persistent metadata includes title, start marker, and `CORRUPTED: Y`. The raw log is a short RCU splat excerpt.

## Dependencies And Integration Points
It depends on the testdata `START` directive, RCU warning pattern recognition, and corrupted-title fallback.

## Risks
Changes to prefix matching for `START` or RCU banners could make the fixture fail even though the raw report is small.

## Test Signals
The parser should start at the given line and produce `INFO: suspicious RCU usage in corrupted`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/35 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/350 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/350

## Purpose
This large fixture verifies soft-lockup parsing with an explicit expected `REPORT:` block. The expected title is `BUG: soft lockup in smp_call_function`, with alternatives for `smp_call_function_many` and generic stall wording, type `HANG`, panicked.

## Important APIs, Types, And Functions
The root marker is `watchdog: BUG: soft lockup - CPU#2 stuck for 136s`. The primary stack includes `smp_call_function_many`, `smp_call_function`, `on_each_cpu`, `text_poke_bp`, jump-label updates, perf tracepoint teardown, `perf_event_release_kernel`, and syscall exit. NMI backtraces for other CPUs include `process_srcu`, DRM/vkms timer paths, and execve fault handling.

## Control Flow
The parser selects the watchdog soft lockup as the root, generates several alternative titles, then the test compares the parser-selected body against the explicit `REPORT:` block. Panic state is detected from `Kernel panic - not syncing: softlockup: hung tasks`.

## State And Persistence
Persistent state includes title, three alt titles, type `HANG`, panicked flag, raw log, and explicit expected report. Runtime state includes stuck CPU, NMI backtraces, ftrace buffer content, and perf/vkms subsystem activity.

## Dependencies And Integration Points
It depends on soft-lockup recognizers, NMI backtrace inclusion, `REPORT:` handling in `report_test.go`, alt title generation for stalls, and hang classification.

## Risks
Report-boundary changes are high risk because this fixture asserts a large explicit report body. Frame scoring can also choose `smp_call_function_many`, which is allowed only as an alternative.

## Test Signals
Stable parsing keeps primary title `BUG: soft lockup in smp_call_function`, all listed alternatives, type `HANG`, panicked, and a report body beginning with the watchdog soft-lockup line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/350 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/351 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/351

## Purpose
This fixture validates lockdep informational parsing for a non-static key registration in VKMS/DRM cleanup, while another CPU panics on a lockdep warning. The expected title is `INFO: trying to register non-static key in vkms_atomic_crtc_destroy_state`.

## Important APIs, Types, And Functions
The primary marker is `INFO: trying to register non-static key.` followed by `register_lock_class` and lock acquisition frames. The meaningful subsystem path is `__flush_work`, `flush_work`, `vkms_atomic_crtc_destroy_state`, `drm_atomic_state_default_clear`, `drm_mode_setcrtc`, `drm_ioctl`, and `ksys_ioctl`. Interleaved panic-on-warn frames mention `lock_downgrade`.

## Control Flow
The reporter must treat the INFO lockdep report as primary, derive the title from the VKMS cleanup frame, and still set `PANICKED: Y` because another task triggers panic-on-warn during the same log window.

## State And Persistence
The header persists title and panicked state. The raw log includes a syzkaller reproducer fragment, DRM ioctl state, and a secondary lockdep warning/panic.

## Dependencies And Integration Points
It depends on lockdep info parsing, frame selection outside the immediate `register_lock_class` helper, interleaved task handling, and panic detection.

## Risks
The secondary `lock_downgrade` warning can steal the title if first-report/priority logic changes. The reproducer program text must be ignored as console context, not report content for title derivation.

## Test Signals
Expected output keeps the non-static-key title in `vkms_atomic_crtc_destroy_state` and marks panicked.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/351 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/352 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/352

## Purpose
This fixture validates kernel BUG parsing in the memory compaction allocator. The expected title is `kernel BUG in __isolate_free_page`, type `BUG`, panicked.

## Important APIs, Types, And Functions
The root marker is `kernel BUG at mm/page_alloc.c:3112!` with `RIP: __isolate_free_page+0x4a8/0x680`. The stack includes `compaction_alloc`, `migrate_pages`, `compact_zone`, `kcompactd_do_work`, and `kcompactd`. A later circular locking dependency report involving console locks is secondary.

## Control Flow
The parser must select the BUG/oops block first, derive the title from the RIP symbol, classify as `BUG`, and not let the following lockdep dependency report replace the root.

## State And Persistence
Persistent state is title/type/panic metadata. Runtime state includes kcompactd memory compaction, zone locks, console locks, and a following lockdep chain.

## Dependencies And Integration Points
It depends on kernel BUG pattern recognition, x86 invalid-op parsing, RIP function extraction, panic detection, and multi-report boundary handling.

## Risks
The secondary lockdep report is long and detailed, so boundary selection could mistakenly classify the fixture as lockdep rather than BUG.

## Test Signals
The stable parser result is `kernel BUG in __isolate_free_page`, `TYPE: BUG`, `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/352 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/353 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/353

## Purpose
This fixture verifies Trusty secure-world panic title extraction for an IPC channel list assertion. The expected title is `trusty: ASSERT FAILED: !list_in_list(&chan->node)`, type `DoS`, panicked.

## Important APIs, Types, And Functions
The key Trusty marker is `ASSERT FAILED at (trusty/kernel/lib/trusty/ipc.c:472): !list_in_list(&chan->node)`, followed by `trusty: HALT`, `trusty crashed`, a Linux warning at `drivers/trusty/trusty.c:215 trusty_std_call32`, and panic-on-warn. The Linux stack includes `nop_work_func`, `process_one_work`, and `worker_thread`.

## Control Flow
The parser must recognize the Trusty panic message before the Linux wrapper warning and use the secure-world assertion text as the title. It then marks panicked from Linux panic-on-warn.

## State And Persistence
The fixture persists the Trusty title, type `DoS`, and panicked flag. Runtime state is a Trusty app-management channel failure propagated through a Linux workqueue.

## Dependencies And Integration Points
It depends on Trusty-specific report patterns, multiline panic text handling, arm64 call-trace parsing, and panic-on-warn detection.

## Risks
The generic Linux `WARNING` can obscure the more specific Trusty assertion if parser priority changes.

## Test Signals
Expected output is the full `!list_in_list(&chan->node)` assertion title with `TYPE: DoS` and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/353 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/354 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/354

## Purpose
This Trusty fixture covers a reflist assertion. The expected title is `trusty: ASSERT FAILED: list_in_list(&ref->ref_node)`, type `DoS`, panicked.

## Important APIs, Types, And Functions
The root line is `DEBUG ASSERT FAILED at (trusty/kernel/include/shared/lk/reflist.h:63): list_in_list(&ref->ref_node)`, followed by Trusty halt/crash markers, Linux `trusty_std_call32` warning, and arm64 workqueue stack in `nop_work_func`.

## Control Flow
The reporter prioritizes the Trusty panic/assertion text over the Linux warning wrapper. It then records panic-on-warn from the Linux kernel panic line.

## State And Persistence
The checked-in state is expected title/type/panic metadata and raw arm64 console output. Runtime state includes Trusty secure-world halt reason and Linux workqueue notification.

## Dependencies And Integration Points
It integrates with Trusty pattern matching, assertion-text extraction, arm64 stack parsing, and generic panic handling.

## Risks
If the parser strips too much Trusty text or selects `trusty_std_call32`, deduplication loses the secure-world assertion identity.

## Test Signals
Stable parsing returns the reflist assertion title exactly and marks `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/354 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/355 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/355

## Purpose
This fixture verifies Trusty panic normalization for app start failures with dynamic numbers. The expected title is `trusty: panic: failed(-NUM) to start app NUM`.

## Important APIs, Types, And Functions
The raw log includes Trusty page-table allocation failures, `failed(-5) to allocate data segment`, `failed(-5) to load address map`, and `panic ... failed(-5) to start app 6`, followed by the Linux Trusty warning wrapper and arm64 workqueue stack.

## Control Flow
The parser must extract the Trusty panic root and normalize dynamic error/app values to `NUM`. It then handles the Linux panic-on-warn wrapper as panicked state, not as the title.

## State And Persistence
Persistent state is the normalized title, type `DoS`, and panicked flag. Runtime state includes secure-world loader memory allocation failure and Trusty halt reason.

## Dependencies And Integration Points
It depends on Trusty panic parsing, numeric normalization, multiline prefix cleanup, and panic-on-warn detection.

## Risks
The app UUID fragment and numeric error codes can produce unstable titles if normalization changes.

## Test Signals
Expected parse title is exactly `trusty: panic: failed(-NUM) to start app NUM`, type `DoS`, panicked.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/355 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/356 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/356

## Purpose
This Trusty fixture checks behavior when assertion details are split across lines, leaving the expected title as the generic `trusty: ASSERT FAILED:` with corruption and panic flags.

## Important APIs, Types, And Functions
The log shows Trusty app metadata, channel wait failure, `ASSERT FAILED at ... ipc.c:472:` on one line, the assertion expression `!list_in_list(&chan->node)` on the next, then Trusty halt/crash and Linux `trusty_std_call32` panic-on-warn stack.

## Control Flow
The parser recognizes the Trusty assertion root but cannot reliably join the split assertion text for this corrupted fixture, so it keeps the generic assertion title and marks corruption. Panic state comes from the Linux panic-on-warn line.

## State And Persistence
The header persists `TYPE: DoS`, `CORRUPTED: Y`, and `PANICKED: Y`. Runtime state includes Trusty app start/channel state and Linux workqueue notification.

## Dependencies And Integration Points
It depends on Trusty assertion parsing, multiline handling, corrupted-title fallback, arm64 call-trace parsing, and panic detection.

## Risks
Future multiline-join changes could produce a more specific title, intentionally changing this regression's expected output.

## Test Signals
The stable result is generic `trusty: ASSERT FAILED:` with type `DoS`, corrupted and panicked flags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/356 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/357 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/357

## Purpose
This fixture validates KASAN use-after-free read parsing in network ICMP error handling. The expected title is `KASAN: use-after-free Read in icmp_send`, alt `bad-access in icmp_send`, type `KASAN-USE-AFTER-FREE-READ`.

## Important APIs, Types, And Functions
The root marker is `BUG: KASAN: use-after-free in do_raw_spin_trylock`, with read size/address metadata. The meaningful stack includes `_raw_spin_trylock`, `icmp_send`, `ip_options_compile`, `ip_rcv_finish_core`, `ip_rcv`, `__netif_receive_skb`, `napi_gro_frags`, and `tun_get_user`. Network noise includes `protocol 88fb is buggy` messages.

## Control Flow
The parser must classify this as a KASAN use-after-free read, then choose `icmp_send` rather than low-level spinlock/KASAN helper frames. It should treat protocol warning lines as incidental console noise.

## State And Persistence
The fixture persists title, alt, and KASAN type. The raw log stores network receive path state, KASAN shadow/provenance sections, and syzkaller executor context.

## Dependencies And Integration Points
It depends on KASAN use-after-free subtype parsing, read/write access extraction, bad-access alt generation, networking frame selection, and report-boundary handling around interleaved protocol warnings.

## Risks
The immediate fault is in `do_raw_spin_trylock`; if frame ranking changes, the title can regress away from the network API where the bug manifests.

## Test Signals
Expected output is `KASAN: use-after-free Read in icmp_send`, alt `bad-access in icmp_send`, type `KASAN-USE-AFTER-FREE-READ`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/357 -->
