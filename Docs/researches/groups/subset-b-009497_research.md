# Research Group subset-b-009497

This grouped report covers syzkaller `pkg/report` parser and symbolization fixtures. Each section is delimited for reconciliation into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/749 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/749

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/749`. It records expected title `attempt to add with overflow in <ashmem_rust::Ashmem as kernel::miscdevice::MiscDevice>::mmap` and covers Rust ashmem mmap overflow panic through the Android miscdevice path. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `attempt to add with overflow in <ashmem_rust::Ashmem as kernel::miscdevice::MiscDevice>::mmap`, type `none`, frame `<ashmem_rust::Ashmem as kernel::miscdevice::MiscDevice>::mmap`, alternate titles none, flags `none`, executor `proc=0, id=595`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `_RNvCscSpY9Juk0HT_7___rustc17rust_begin_unwind`
- `__cfi__RNvCscSpY9Juk0HT_7___rustc17rust_begin_unwind`
- `kernel_text_address`
- `__cfi__RNvXs1b_NtCs9jEwPDbx20M_4core3fmtRNtNtNtB8_5panic10panic_info9PanicInfoNtB6_7Display3fmtCs43vyB533jt3_6kernel`
- `__cfi_stack_trace_consume_entry`
- `arch_stack_walk`
- `_RNvNtCs9jEwPDbx20M_4core9panicking9panic_fmt`
- `__cfi__RNvNtCs9jEwPDbx20M_4core9panicking9panic_fmt`
- `_RNvNtNtCs9jEwPDbx20M_4core9panicking11panic_const24panic_const_add_overflow`
- `__cfi__RNvNtNtCs9jEwPDbx20M_4core9panicking11panic_const24panic_const_add_overflow`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 80 total lines, 76 log lines, 0 expected report lines, and 7291 bytes. Salient log lines include:

- [   60.002464][ T2148] rust_kernel: panicked at /syzkaller/managers/ci2-android-6-12-rust/kernel/rust/kernel/page_size_compat.rs:60:5:
- [   60.041680][ T2148] Oops: invalid opcode: 0000 [#1] PREEMPT SMP KASAN PTI
- [   60.173624][ T2148]  ? __cfi__RNvXs1b_NtCs9jEwPDbx20M_4core3fmtRNtNtNtB8_5panic10panic_info9PanicInfoNtB6_7Display3fmtCs43vyB533jt3_6kernel+0x10/0x10
- [   60.189785][ T2148]  _RNvNtCs9jEwPDbx20M_4core9panicking9panic_fmt+0x84/0x90

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/749 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/75 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/75

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/75`. It records expected title `BUG: scheduling while atomic in pause` and covers atomic-sleep detection around pause/SyS_pause. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `BUG: scheduling while atomic in pause`, type `ATOMIC_SLEEP`, frame `none`, alternate titles `BUG: scheduling while atomic in SyS_pause`, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `dump_stack`
- `__schedule_bug`
- `__schedule`
- `schedule`
- `SyS_pause`
- `tracesys_phase2`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 19 total lines, 15 log lines, 0 expected report lines, and 1101 bytes. Salient log lines include:

- [  185.479466] BUG: scheduling while atomic: syz-executor0/19425/0x00000000
- [  185.486365] INFO: lockdep is turned off.

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/75 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/750 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/750

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/750`. It records expected title `KCSAN: assert: race in dequeue_entities` and covers KCSAN scheduler assertion in dequeue_entities reached from netfilter abort. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `KCSAN: assert: race in dequeue_entities`, type `KCSAN-ASSERT`, frame `dequeue_entities`, alternate titles none, flags `none`, executor `proc=2, id=327`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `dequeue_entities`
- `pick_next_task_fair`
- `__schedule`
- `schedule`
- `synchronize_rcu_expedited`
- `synchronize_rcu`
- `nf_tables_abort`
- `nfnetlink_rcv`
- `netlink_unicast`
- `netlink_sendmsg`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 33 total lines, 28 log lines, 0 expected report lines, and 1824 bytes. Salient log lines include:

- [   67.061656][ T4926] BUG: KCSAN: assert: race in dequeue_entities+0x6df/0x760

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/750 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/751 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/751

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/751`. It records expected title `KMSAN: uninit-value in alg_setkey` and covers KMSAN uninitialized crypto key material flowing through DRBG/aes_encrypt. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `KMSAN: uninit-value in alg_setkey`, type `KMSAN-UNINIT-VALUE`, frame `none`, alternate titles `bad-access in alg_setkey`, flags `none`, executor `proc=2, id=690`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `aes_encrypt`
- `aesti_encrypt`
- `cipher_crypt_one`
- `crypto_cipher_encrypt_one`
- `drbg_ctr_update`
- `drbg_seed`
- `drbg_kcapi_seed`
- `crypto_rng_reset`
- `rng_setkey`
- `alg_setkey`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 180 total lines, 175 log lines, 0 expected report lines, and 5223 bytes. Salient log lines include:

- BUG: KMSAN: uninit-value in aes_encrypt+0x1239/0x1960

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/751 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/752 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/752

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/752`. It records expected title `memory leak in lookup_or_create_module_kobject` and covers kmemleak report for module kobject allocation during USB gadget registration. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `memory leak in lookup_or_create_module_kobject`, type `LEAK`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `__kmalloc_cache_noprof`
- `lookup_or_create_module_kobject`
- `module_add_driver`
- `bus_add_driver`
- `driver_register`
- `usb_gadget_register_driver_owner`
- `raw_ioctl`
- `__x64_sys_ioctl`
- `do_syscall_64`
- `entry_SYSCALL_64_after_hwframe`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 35 total lines, 32 log lines, 0 expected report lines, and 1603 bytes. Salient log lines include:

- BUG: memory leak

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/752 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/753 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/753

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/753`. It records expected title `WARNING: ODEBUG bug in handle_softirqs` and covers debugobjects active timer warning in rose protocol softirq handling. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING: ODEBUG bug in handle_softirqs`, type `WARNING`, frame `handle_softirqs`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `rose_timer_expiry`
- `kfree`
- `call_timer_fn`
- `_raw_spin_unlock_irq`
- `lockdep_hardirqs_on`
- `__run_timer_base`
- `seqcount_lockdep_reader_access`
- `run_timer_softirq`
- `handle_softirqs`
- `__irq_exit_rcu`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 154 total lines, 150 log lines, 0 expected report lines, and 9325 bytes. Salient log lines include:

- [ 1448.582480][    C1] ODEBUG: free active (active state 0) object: ffff88807b3c4490 object type: timer_list hint: rose_t0timer_expiry+0x0/0x350
- [ 1448.582538][    C1] WARNING: lib/debugobjects.c:615 at 0x0, CPU#1: kworker/1:3/17677

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/753 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/754 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/754

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/754`. It records expected title `WARNING: refcount bug in __vma_enter_locked` and covers refcount warning while releasing userfaultfd VMAs. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING: refcount bug in __vma_enter_locked`, type `REFCOUNT_WARNING`, frame `__vma_enter_locked`, alternate titles none, flags `none`, executor `proc=3, id=20`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `__vma_enter_locked`
- `__vma_start_write`
- `vma_modify`
- `vma_modify_flags_uffd`
- `mas_find`
- `userfaultfd_release_all`
- `userfaultfd_release`
- `preempt_schedule_common`
- `preempt_schedule`
- `evm_file_release`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 68 total lines, 63 log lines, 0 expected report lines, and 4509 bytes. Salient log lines include:

- [   99.069428][ T6051] WARNING: lib/refcount.c:19 at 0x0, CPU#1: syz.3.20/6051

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/754 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/755 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/755

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/755`. It records expected title `WARNING in ext4_xattr_inode_update_ref` and covers ext4 xattr inode reference warning during inode eviction. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING in ext4_xattr_inode_update_ref`, type `WARNING`, frame `ext4_xattr_inode_update_ref`, alternate titles none, flags `none`, executor `proc=0, id=17`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `ext4_xattr_inode_iget`
- `ext4_xattr_set_entry`
- `ext4_xattr_ibody_set`
- `ext4_expand_extra_isize_ea`
- `__ext4_expand_extra_isize`
- `__ext4_mark_inode_dirty`
- `ext4_evict_inode`
- `do_raw_spin_unlock`
- `evict`
- `_raw_spin_unlock`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 76 total lines, 71 log lines, 0 expected report lines, and 4963 bytes. Salient log lines include:

- [   92.524882][ T5982] WARNING: fs/ext4/xattr.c:1058 at 0x0, CPU#0: syz.0.17/5982

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/755 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/756 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/756

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/756`. It records expected title `WARNING in ovl_stack_put` and covers overlayfs dentry/inode release warning via ovl_stack_put. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING in ovl_stack_put`, type `WARNING`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `dput`
- `ovl_stack_put`
- `ovl_destroy_inode`
- `evict`
- `_raw_spin_unlock`
- `iput`
- `__dentry_kill`
- `shrink_kill`
- `shrink_dentry_list`
- `shrink_dcache_tree`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 76 total lines, 73 log lines, 0 expected report lines, and 5197 bytes. Salient log lines include:

- [  195.364985][ T5830] WARNING: fs/dcache.c:829 at fast_dput+0x334/0x430, CPU#1: syz-executor/5830

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/756 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/757 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/757

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/757`. It records expected title `WARNING in __fput` and covers file close path warning in __fput after dentry release. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING in __fput`, type `WARNING`, frame `__fput`, alternate titles none, flags `none`, executor `proc=0, id=17`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `dput`
- `__fput`
- `task_work_run`
- `__se_sys_close_range`
- `exit_to_user_mode_loop`
- `rcu_is_watching`
- `do_syscall_64`
- `entry_SYSCALL_64_after_hwframe`
- `clear_bhb_loop`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 45 total lines, 40 log lines, 0 expected report lines, and 3143 bytes. Salient log lines include:

- [  113.532065][ T6007] WARNING: fs/dcache.c:829 at fast_dput+0x334/0x430, CPU#0: syz.0.17/6007

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/757 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/758 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/758

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/758`. It records expected title `WARNING in bfs_get_block` and covers BFS block write warning around mark_buffer_dirty/bfs_get_block. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING in bfs_get_block`, type `WARNING`, frame `none`, alternate titles none, flags `none`, executor `proc=0, id=52`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `bfs_get_block`
- `__block_write_begin_int`
- `block_write_begin`
- `bfs_write_begin`
- `generic_perform_write`
- `file_update_time_flags`
- `__generic_file_write_iter`
- `generic_file_write_iter`
- `futex_unqueue`
- `__lock_acquire`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 68 total lines, 64 log lines, 0 expected report lines, and 4524 bytes. Salient log lines include:

- [  140.728169][ T6181] WARNING: fs/buffer.c:1183 at mark_buffer_dirty+0x299/0x3f0, CPU#1: syz.0.52/6181

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/758 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/759 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/759

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/759`. It records expected title `int3 in __pmd_alloc` and covers panic-on-int3 trap in __pmd_alloc during clone/copy_page_range. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `int3 in __pmd_alloc`, type `DoS`, frame `__pmd_alloc`, alternate titles none, flags `PANICKED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `__pmd_alloc`
- `copy_page_range`
- `dup_mmap`
- `copy_process`
- `kernel_clone`
- `__do_sys_clone`
- `do_syscall_64`
- `entry_SYSCALL_64_after_hwframe`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 28 total lines, 23 log lines, 0 expected report lines, and 1686 bytes. Salient log lines include:

- [  150.665871][    C0] Oops: int3: 0000 [#1] SMP KASAN NOPTI
- [  150.666570][    C0] Kernel panic - not syncing: Fatal exception in interrupt

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. Panic detection must set `Panicked=true` without starting a second independent report at the panic line.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/759 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/76 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/76

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/76` with no `TITLE` header. It covers negative Linux boot-noise case containing a benign ssh moduli warning and ensures the Linux reporter does not treat ordinary warnings, Android boot strings, or informational diagnostics as crashes.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `none`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness still reads the file into `ParseTest`, but the missing `TITLE` is intentional. `Reporter.Parse` should scan the full log, fail to find a valid oops start, and return no report; the expected value is an empty parsed result rather than a low-confidence crash. The fixture has 2 total lines, 1 log lines, 0 expected report lines, and 77 bytes. Salient log lines include:

- [   72.159680] WARNING: /etc/ssh/moduli does not exist, using fixed modulus

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

The main risk is a false positive: broad warning or info regexes could turn benign console text into a crash.

## Test Signals

The key test signal is negative: `TestParse` should produce an empty parsed result. Any non-empty title, type, frame, report body, corruption marker, or panic flag indicates an over-broad Linux/NetBSD oops rule and would make benign logs look like actionable crashes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/76 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/77 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/77

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/77`. It records expected title `KASAN: slab-out-of-bounds in ip6_fragment at addr ADDR` and covers short corrupted KASAN slab-out-of-bounds ip6_fragment report. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `KASAN: slab-out-of-bounds in ip6_fragment at addr ADDR`, type `KASAN-READ`, frame `none`, alternate titles none, flags `CORRUPTED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 5 total lines, 1 log lines, 0 expected report lines, and 194 bytes. Salient log lines include:

- [ 1579.244514] BUG: KASAN: slab-out-of-bounds in ip6_fragment+0x1052/0x2d80 at addr ffff88004ec29b58

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/77 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/78 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/78

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/78`. It records expected title `BUG: spinlock bad magic in tcp_nuke_addr` and covers spinlock bad magic report in tcp_nuke_addr. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `BUG: spinlock bad magic in tcp_nuke_addr`, type `LOCKDEP`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `dump_stack`
- `spin_dump`
- `do_raw_spin_lock`
- `_raw_spin_lock`
- `tcp_nuke_addr`
- `security_capable`
- `devinet_ioctl`
- `inet_ifa_byprefix`
- `exit_robust_list`
- `inet_ioctl`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 32 total lines, 29 log lines, 0 expected report lines, and 2034 bytes. Salient log lines include:

- [   82.818367] BUG: spinlock bad magic on CPU#0, ^keyring*�vmnet/20513

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/78 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/79 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/79

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/79`. It records expected title `KASAN: use-after-free in do_con_write.part.NUM at addr ADDR` and covers short corrupted KASAN use-after-free in do_con_write.part.NUM. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `KASAN: use-after-free in do_con_write.part.NUM at addr ADDR`, type `KASAN-USE-AFTER-FREE-READ`, frame `none`, alternate titles none, flags `CORRUPTED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 5 total lines, 1 log lines, 0 expected report lines, and 218 bytes. Salient log lines include:

- [  374.860710] BUG: KASAN: use-after-free in do_con_write.part.23+0x1c50/0x1cb0 at addr ffff88000012c43a

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/79 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/8 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/8

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/8`. It records expected title `KASAN: use-after-free Read in snd_seq_queue_alloc` and covers KASAN snd_seq_queue_alloc use-after-free with explicit report block. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `KASAN: use-after-free Read in snd_seq_queue_alloc`, type `KASAN-USE-AFTER-FREE-READ`, frame `none`, alternate titles `bad-access in snd_seq_queue_alloc`, flags `CORRUPTED`, executor `none`, and explicit report block `yes`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 23 total lines, 10 log lines, 7 expected report lines, and 748 bytes. Salient log lines include:

- [   95.152992] BUG: KASAN: use-after-free in snd_seq_queue_alloc+0x670/0x690 at addr ffff8801d0c6b080

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`. Because the fixture has an explicit `REPORT:` block, report extraction must match the body text, not merely the header fields.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/8 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/80 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/80

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/80`. It records expected title `WARNING: kernel stack regs has bad 'bp' value` and covers kernel stack regs bad bp warning. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING: kernel stack regs has bad 'bp' value`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 3 total lines, 1 log lines, 0 expected report lines, and 175 bytes. Salient log lines include:

- [  163.314570] WARNING: kernel stack regs at ffff8801d100fea8 in syz-executor1:16059 has bad 'bp' value ffff8801d100ff28

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/80 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/81 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/81

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/81`. It records expected title `BUG: using __this_cpu_add() in preemptible code in ipcomp_init_state` and covers preemptible __this_cpu_add lockdep report in ipcomp_init_state. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `BUG: using __this_cpu_add() in preemptible code in ipcomp_init_state`, type `LOCKDEP`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `dump_stack`
- `check_preemption_disabled`
- `__this_cpu_preempt_check`
- `ipcomp_init_state`
- `__lock_is_held`
- `ipcomp4_init_state`
- `__xfrm_init_state`
- `xfrm_init_state`
- `pfkey_add`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 20 total lines, 17 log lines, 0 expected report lines, and 1312 bytes. Salient log lines include:

- [   76.825838] BUG: using __this_cpu_add() in preemptible [00000000] code: syz-executor0/10076

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/81 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/82 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/82

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/82`. It records expected title `BUG: Object already free` and covers short corrupted object-already-free report. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `BUG: Object already free`, type `DoS`, frame `none`, alternate titles none, flags `CORRUPTED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 5 total lines, 1 log lines, 0 expected report lines, and 133 bytes. Salient log lines include:

- no crash-start line is expected; this is a negative/no-title parser fixture

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/82 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/83 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/83

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/83` with no `TITLE` header. It covers negative NMI perf handler latency informational line and ensures the Linux reporter does not treat ordinary warnings, Android boot strings, or informational diagnostics as crashes.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `none`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness still reads the file into `ParseTest`, but the missing `TITLE` is intentional. `Reporter.Parse` should scan the full log, fail to find a valid oops start, and return no report; the expected value is an empty parsed result rather than a low-confidence crash. The fixture has 4 total lines, 3 log lines, 0 expected report lines, and 263 bytes. Salient log lines include:

- [   95.445015] INFO: NMI handler (perf_event_nmi_handler) took too long to run: 1.356 msecs

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

The main risk is a false positive: broad warning or info regexes could turn benign console text into a crash.

## Test Signals

The key test signal is negative: `TestParse` should produce an empty parsed result. Any non-empty title, type, frame, report body, corruption marker, or panic flag indicates an over-broad Linux/NetBSD oops rule and would make benign logs look like actionable crashes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/83 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/84 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/84

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/84`. It records expected title `general protection fault in corrupted` and covers corrupted general protection fault line with interleaved audit text. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `general protection fault in corrupted`, type `DoS`, frame `none`, alternate titles `bad-access in corrupted`, flags `CORRUPTED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 6 total lines, 1 log lines, 0 expected report lines, and 370 bytes. Salient log lines include:

- [   92.396607] general protection fault: 0000 [#1] [ 387.811073] audit: type=1326 audit(1486238739.637:135): auid=4294967295 uid=0 gid=0 ses=4294967295 pid=10020 comm="syz-executor1" exe="/root/syz-executor1" sig=31 arch=c000003e syscall=202 compat=0 ip=0x44fad9 code=0x0

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/84 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/85 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/85

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/85`. It records expected title `BUG: Bad page map` and covers corrupted bad page map report. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `BUG: Bad page map`, type `none`, frame `none`, alternate titles none, flags `CORRUPTED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 6 total lines, 3 log lines, 0 expected report lines, and 357 bytes. Salient log lines include:

- [   40.438790] BUG: Bad page map in process syz-executor6  pte:ffff8801a700ff00 pmd:1a700f067

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/85 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/86 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/86

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/86`. It records expected title `possible deadlock in tty_buffer_flush` and covers corrupted possible deadlock in tty_buffer_flush. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `possible deadlock in tty_buffer_flush`, type `LOCKDEP`, frame `none`, alternate titles none, flags `CORRUPTED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `tty_buffer_flush`
- `isig`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 15 total lines, 11 log lines, 0 expected report lines, and 774 bytes. Salient log lines include:

- [ 1722.511384] WARNING: possible circular locking dependency detected

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/86 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/87 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/87

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/87`. It records expected title `BUG: Dentry still in use in unmount` and covers corrupted dentry-still-in-use panic-on-warn unmount report. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `BUG: Dentry still in use in unmount`, type `none`, frame `none`, alternate titles `BUG: Dentry still in use [unmount of proc proc]`, flags `CORRUPTED, PANICKED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 10 total lines, 5 log lines, 0 expected report lines, and 519 bytes. Salient log lines include:

- [ 1722.511384] BUG: Dentry ffff880175978600{i=8bb9,n=lo}  still in use (1) [unmount of proc proc]
- [ 1722.511384] WARNING: CPU: 1 PID: 8922 at fs/dcache.c:1445 umount_check+0x246/0x2c0 fs/dcache.c:1436
- [ 1722.511384] Kernel panic - not syncing: panic_on_warn set ...

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`. Panic detection must set `Panicked=true` without starting a second independent report at the panic line.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/87 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/88 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/88

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/88`. It records expected title `WARNING: kernel stack frame pointer has bad value` and covers kernel stack frame pointer bad value warning. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING: kernel stack frame pointer has bad value`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 5 total lines, 3 log lines, 0 expected report lines, and 330 bytes. Salient log lines include:

- [   72.159680] WARNING: kernel stack frame pointer at ffff88003e1f7f40 in migration/1:14 has bad value ffffffff85632fb0

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/88 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/89 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/89

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/89`. It records expected title `BUG: Bad page state in corrupted` and covers corrupted bad page state report. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `BUG: Bad page state in corrupted`, type `none`, frame `none`, alternate titles none, flags `CORRUPTED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 10 total lines, 7 log lines, 0 expected report lines, and 639 bytes. Salient log lines include:

- [ 1722.511384] BUG: Bad page state in process syz-executor9  pfn:199e00

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/89 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/9 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/9

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/9`. It records expected title `BUG: unable to handle kernel paging request in skb_release_data` and covers kernel paging request in skb_release_data memory-safety report. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `BUG: unable to handle kernel paging request in skb_release_data`, type `MEMORY_SAFETY_BUG`, frame `none`, alternate titles `bad-access in skb_release_data`, flags `CORRUPTED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 7 total lines, 2 log lines, 0 expected report lines, and 272 bytes. Salient log lines include:

- [ 1019.110825] BUG: unable to handle kernel paging request at 000000010000001a

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/9 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/90 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/90

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/90`. It records expected title `kernel panic: Couldn't open N_TTY ldisc` and covers corrupted kernel panic opening N_TTY line discipline. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `kernel panic: Couldn't open N_TTY ldisc`, type `DoS`, frame `none`, alternate titles none, flags `CORRUPTED, PANICKED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 9 total lines, 4 log lines, 0 expected report lines, and 376 bytes. Salient log lines include:

- [ 1722.511384] Kernel panic - not syncing: Couldn't open N_TTY ldisc for ptm1 --- error -12.

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`. Panic detection must set `Panicked=true` without starting a second independent report at the panic line.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/90 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/91 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/91

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/91`. It records expected title `INFO: suspicious RCU usage in corrupted` and covers corrupted suspicious RCU usage report. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `INFO: suspicious RCU usage in corrupted`, type `none`, frame `none`, alternate titles none, flags `CORRUPTED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 10 total lines, 7 log lines, 0 expected report lines, and 398 bytes. Salient log lines include:

- [ 1722.511384] [ INFO: suspicious RCU usage. ]

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/91 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/92 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/92

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/92` with no `TITLE` header. It covers negative Android boot/debug log line with no crash oracle and ensures the Linux reporter does not treat ordinary warnings, Android boot strings, or informational diagnostics as crashes.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `none`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness still reads the file into `ParseTest`, but the missing `TITLE` is intentional. `Reporter.Parse` should scan the full log, fail to find a valid oops start, and return no report; the expected value is an empty parsed result rather than a low-confidence crash. The fixture has 4 total lines, 3 log lines, 0 expected report lines, and 267 bytes. Salient log lines include:

- [   38.018742]  [4:  system_server: 3344] logger: !@Boot_DEBUG: start networkManagement

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

The main risk is a false positive: broad warning or info regexes could turn benign console text into a crash.

## Test Signals

The key test signal is negative: `TestParse` should produce an empty parsed result. Any non-empty title, type, frame, report body, corruption marker, or panic flag indicates an over-broad Linux/NetBSD oops rule and would make benign logs look like actionable crashes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/92 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/93 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/93

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/93` with no `TITLE` header. It covers negative camera driver informational boot lines and ensures the Linux reporter does not treat ordinary warnings, Android boot strings, or informational diagnostics as crashes.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `none`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness still reads the file into `ParseTest`, but the missing `TITLE` is intentional. `Reporter.Parse` should scan the full log, fail to find a valid oops start, and return no report; the expected value is an empty parsed result rather than a low-confidence crash. The fixture has 4 total lines, 3 log lines, 0 expected report lines, and 260 bytes. Salient log lines include:

- [   16.761978] [syscamera][msm_companion_pll_init::526][BIN_INFO::0x0008]
- [   16.762666] [syscamera][msm_companion_pll_init::544][WAFER_INFO::0xcf80]
- [   16.763144] [syscamera][msm_companion_pll_init::594][BIN_INFO::0x0008][WAFER_INFO::0xcf80][voltage 0.775]

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

The main risk is a false positive: broad warning or info regexes could turn benign console text into a crash.

## Test Signals

The key test signal is negative: `TestParse` should produce an empty parsed result. Any non-empty title, type, frame, report body, corruption marker, or panic flag indicates an over-broad Linux/NetBSD oops rule and would make benign logs look like actionable crashes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/93 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/94 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/94

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/94`. It records expected title `BUG: workqueue lockup` and covers workqueue lockup detection line. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `BUG: workqueue lockup`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 3 total lines, 1 log lines, 0 expected report lines, and 120 bytes. Salient log lines include:

- [   72.159680] BUG: workqueue lockup - pool cpus=0 node=0 flags=0x0 nice=0 stuck for 32s!

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/94 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/95 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/95

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/95`. It records expected title `BUG: spinlock already unlocked in synchronize_sched_expedited_cpu_stop` and covers spinlock already unlocked report in synchronize_sched_expedited_cpu_stop. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `BUG: spinlock already unlocked in synchronize_sched_expedited_cpu_stop`, type `LOCKDEP`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `yes`. Representative symbols or frames visible to the parser are:

- `dump_stack`
- `spin_dump`
- `do_raw_spin_unlock`
- `_raw_spin_unlock_irqrestore`
- `__wake_up`
- `rcu_barrier_func`
- `synchronize_sched_expedited_cpu_stop`
- `cpu_stopper_thread`
- `cpu_stop_create`
- `cpu_stop_should_run`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 55 total lines, 33 log lines, 18 expected report lines, and 3351 bytes. Salient log lines include:

- [  108.620932] BUG: spinlock already unlocked on CPU#1, migration/1/12

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. Because the fixture has an explicit `REPORT:` block, report extraction must match the body text, not merely the header fields.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/95 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/96 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/96

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/96`. It records expected title `kernel panic: Fatal exception` and covers fatal exception kernel panic with corruption marker. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `kernel panic: Fatal exception`, type `DoS`, frame `none`, alternate titles none, flags `CORRUPTED, PANICKED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 15 total lines, 10 log lines, 0 expected report lines, and 797 bytes. Salient log lines include:

- [  128.792710] Kernel panic - not syncing: Fatal exception

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`. Panic detection must set `Panicked=true` without starting a second independent report at the panic line.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/96 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/97 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/97

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/97`. It records expected title `kernel panic: panic_on_warn set` and covers panic_on_warn report with stack around kasan_end_report/panic. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `kernel panic: panic_on_warn set`, type `DoS`, frame `none`, alternate titles none, flags `CORRUPTED, PANICKED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `dump_stack`
- `arch_local_irq_restore`
- `kasan_end_report`
- `lock_downgrade`
- `__internal_add_timer`
- `panic`
- `__warn`
- `add_taint`
- `kasan_report`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 26 total lines, 21 log lines, 0 expected report lines, and 1259 bytes. Salient log lines include:

- [  238.128296] Kernel panic - not syncing: panic_on_warn set ...
- [  238.177023]  panic+0x1e4/0x417

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`. Panic detection must set `Panicked=true` without starting a second independent report at the panic line.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/97 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/98 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/98

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/98`. It records expected title `WARNING: possible circular locking dependency detected` and covers corrupted circular-locking warning classified as generic WARNING. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING: possible circular locking dependency detected`, type `WARNING`, frame `none`, alternate titles none, flags `CORRUPTED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 9 total lines, 4 log lines, 0 expected report lines, and 419 bytes. Salient log lines include:

- [  308.136979] WARNING: possible circular locking dependency detected

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/98 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/99 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/99

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/99`. It records expected title `BUG: unable to handle kernel` and covers truncated corrupted unable-to-handle-kernel report. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `BUG: unable to handle kernel`, type `none`, frame `none`, alternate titles none, flags `CORRUPTED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 13 total lines, 10 log lines, 0 expected report lines, and 499 bytes. Salient log lines include:

- [ 1722.511384] BUG: unable to handle kernel

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/99 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/999 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/999

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/999`. It records expected title `WARNING in io_ring_exit_work` and covers io_uring exit worker timeout warning in io_ring_exit_work. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING in io_ring_exit_work`, type `WARNING`, frame `io_ring_exit_work`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `io_ring_exit_work`
- `process_one_work`
- `worker_thread`
- `kthread`
- `ret_from_fork_kernel`
- `ret_from_fork_kernel_asm`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 31 total lines, 27 log lines, 0 expected report lines, and 2258 bytes. Salient log lines include:

- [ 9877.700279][    C0] WARNING: [time_after(jiffies, timeout)] io_uring/io_uring.c:3026 at io_ring_exit_work+0x44c/0xbc0, CPU#0: kworker/u8:0/10040

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/999 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/symbolize/1 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/symbolize/1

## Purpose

This source file is a Linux syzkaller symbolization fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/symbolize/1`. It records expected title `possible deadlock in fakeName` and type `LOCKDEP` while also carrying a `REPORT:` oracle. The fixture verifies that the Linux reporter can parse a raw lockdep report containing the C++ symbol `_Z8fakeNameiii`, run `Reporter.Symbolize`, demangle it to `fakeName`, and keep the extracted report text aligned with the expected post-symbolization block.

## Important APIs, Types, and Functions

The important APIs and data types are `TestSymbolize`, `parseReport`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.symbolize`, `symbolizeLine`, the symbolizer cache, C++/Rust demangling, report-prefix accounting, and `ParseTest.Equal`. Expected parser fields are: title `possible deadlock in fakeName`, type `LOCKDEP`, frame `none`, alternate titles none, flags `none`, executor `proc=5, id=7376`, and explicit report block `yes`. Representative symbols or frames visible to the parser are:

- `_Z8fakeNameiii`
- `nbd_start_device`
- `lock_acquire`
- `blk_alloc_queue`
- `__blk_mq_alloc_disk`
- `nbd_dev_add`
- `nbd_init`
- `do_one_initcall`
- `do_initcall_level`
- `do_initcalls`

## Control Flow

`TestSymbolize` reads the same header/log/report format as parse tests, calls `Reporter.Parse` on the raw log, then invokes `Reporter.Symbolize`. The Linux symbolization path rewrites matching stack lines, demangles C++ names, preserves prefix offsets, and finally compares both derived headers and the `REPORT:` body against this file. The fixture has 306 total lines, 168 log lines, 133 expected report lines, and 15200 bytes. Salient log lines include:

- [  492.198599][T24950] WARNING: possible circular locking dependency detected

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux console-prefix parsing, task/cpu context detection, lockdep report extraction, `symbolizer.Symbolizer` callbacks, demangling via the Linux reporter, report-prefix length tracking, and executor extraction from `syz.5.7376`. The kernel-side text models block/NBD, generic netlink, mutex/lockdep, and syscall frames; these are dependencies only as strings consumed by parser regexes.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. Symbolization must not double-symbolize, corrupt prefix offsets, or leave `_Z8fakeNameiii` unmangled when the expected report uses `fakeName`. Because the fixture has an explicit `REPORT:` block, report extraction must match the body text, not merely the header fields.

## Test Signals

The key test signal is `TestSymbolize`: after parse and symbolization, `ParseTest.Equal` must accept the title/type/executor fields and the extracted `rep.Report` must equal the `REPORT:` oracle. A failure usually means broken demangling, dropped lockdep body lines, wrong report-prefix accounting, or accidental double symbolization.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/symbolize/1 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/0 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/0

## Purpose

This source file is a NetBSD syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/0`. It records expected title `page fault in __asan_load8` and exercises NetBSD/BSD crash extraction over a NetBSD console report. The file is persistent test data, not executable code, and its header is the oracle that `pkg/report` must reproduce from the console log body.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `ctorBSD`, the NetBSD oops tables, BSD stack extraction, optional `bsd.symbolizeLine`, and `crash.TitleToType`. Expected parser fields are: title `page fault in __asan_load8`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `__asan_load8`
- `shm_delete_mapping`
- `sys_shmat`
- `sys___syscall`
- `syscall`
- `netbsd:__asan_load8`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 1613 total lines, 1611 log lines, 0 expected report lines, and 107020 bytes. Salient log lines include:

- [ 299.8186254] fatal page fault in supervisor mode

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include the shared report test harness, NetBSD-specific oops patterns, BSD stack-line parsing, crash title normalization, optional symbolization regexes, and `targets.NetBSD` reporter construction. Kernel-side dependencies are represented as console text: NetBSD trap/panic syntax, KASAN/UBSan strings, syscall frames, register dumps, LWP tables, dump/reboot trailers, and subsystem paths such as `sysv_shm`, `pmap`, and ACPI.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/1 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/1

## Purpose

This source file is a NetBSD syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/1`. It records expected title `assert failed: pmap->pm_obj[i].uo_npages == NUM` and exercises NetBSD/BSD crash extraction over a NetBSD console report. The file is persistent test data, not executable code, and its header is the oracle that `pkg/report` must reproduce from the console log body.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `ctorBSD`, the NetBSD oops tables, BSD stack extraction, optional `bsd.symbolizeLine`, and `crash.TitleToType`. Expected parser fields are: title `assert failed: pmap->pm_obj[i].uo_npages == NUM`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `vpanic`
- `ch_voltag_convert_in`
- `pmap_destroy`
- `pmap_pp_remove`
- `uvm_anon_dispose`
- `uvm_anon_freelst`
- `amap_wipeout`
- `uvm_unmap_detach`
- `uvmspace_free`
- `exit1`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 25 total lines, 23 log lines, 0 expected report lines, and 1229 bytes. Salient log lines include:

- panic: kernel diagnostic assertion "pmap->pm_obj[i].uo_npages == 0" failed: file "/extra/netbsd-src/sys/arch/x86/x86/pmap.c", line 2368
- vpanic() at netbsd:vpanic+0x140

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include the shared report test harness, NetBSD-specific oops patterns, BSD stack-line parsing, crash title normalization, optional symbolization regexes, and `targets.NetBSD` reporter construction. Kernel-side dependencies are represented as console text: NetBSD trap/panic syntax, KASAN/UBSan strings, syscall frames, register dumps, LWP tables, dump/reboot trailers, and subsystem paths such as `sysv_shm`, `pmap`, and ACPI.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/1 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/10 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/10

## Purpose

This source file is a NetBSD syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/10`. It records expected title `UBSan: Undefined behavior` and exercises NetBSD/BSD crash extraction over a NetBSD console report. The file is persistent test data, not executable code, and its header is the oracle that `pkg/report` must reproduce from the console log body.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `ctorBSD`, the NetBSD oops tables, BSD stack extraction, optional `bsd.symbolizeLine`, and `crash.TitleToType`. Expected parser fields are: title `UBSan: Undefined behavior`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 3 total lines, 1 log lines, 0 expected report lines, and 287 bytes. Salient log lines include:

- [     1.000003] UBSan: Undefined Behavior in /media/k4iz3n/event1/kWork/src/sys/external/bsd/acpica/dist/resources/rsaddr.c:331:22, member access within misaligned address 0xffffe9b9e6b42f62 for type 'union AML_RESOURCE' which requires 4 byte alignment

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include the shared report test harness, NetBSD-specific oops patterns, BSD stack-line parsing, crash title normalization, optional symbolization regexes, and `targets.NetBSD` reporter construction. Kernel-side dependencies are represented as console text: NetBSD trap/panic syntax, KASAN/UBSan strings, syscall frames, register dumps, LWP tables, dump/reboot trailers, and subsystem paths such as `sysv_shm`, `pmap`, and ACPI.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/10 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/11 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/11

## Purpose

This source file is a NetBSD syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/11`. It records expected title `UBSan: Undefined behavior` and exercises NetBSD/BSD crash extraction over a NetBSD console report. The file is persistent test data, not executable code, and its header is the oracle that `pkg/report` must reproduce from the console log body.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `ctorBSD`, the NetBSD oops tables, BSD stack extraction, optional `bsd.symbolizeLine`, and `crash.TitleToType`. Expected parser fields are: title `UBSan: Undefined behavior`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 3 total lines, 1 log lines, 0 expected report lines, and 219 bytes. Salient log lines include:

- [     1.000003] UBSan: Undefined Behavior in /media/k4iz3n/event1/kWork/src/sys/dev/acpi/acpica/OsdHardware.c:265:17, left shift of 255 by 24 places cannot be represented in type 'int'

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include the shared report test harness, NetBSD-specific oops patterns, BSD stack-line parsing, crash title normalization, optional symbolization regexes, and `targets.NetBSD` reporter construction. Kernel-side dependencies are represented as console text: NetBSD trap/panic syntax, KASAN/UBSan strings, syscall frames, register dumps, LWP tables, dump/reboot trailers, and subsystem paths such as `sysv_shm`, `pmap`, and ACPI.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/11 -->
