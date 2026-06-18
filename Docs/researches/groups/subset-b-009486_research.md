# Research: subset-b-009486

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/275 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/275

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in smp_call_function` and the expected crash type is `HANG`. RCU scheduler stall while a syz executor closes a KVM vCPU and the interrupted frame is `smp_call_function_single`, with VMX vCPU teardown below it.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in smp_call_function`; alternate titles are `INFO: rcu detected stall in smp_call_function_single`, `stall in smp_call_function`, `stall in smp_call_function_single`; extra parsed flags are none. The body is 49 lines and 2711 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: RCU stall detector, APIC timer interrupt, KVM/VMX vCPU load and destroy path, file close/task work exit.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/275 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/276 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/276

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in __cleanup_mnt` and the expected crash type is `HANG`. RCU stall during mount cleanup: the stack starts in `fuse_abort_conn` and unwinds through FUSE superblock teardown to `cleanup_mnt` and `__cleanup_mnt`.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in __cleanup_mnt`; alternate titles are `stall in __cleanup_mnt`; extra parsed flags are none. The body is 48 lines and 2672 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: FUSE unmount, VFS superblock shutdown, task-work cleanup on syscall exit.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/276 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/277 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/277

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in ext4_file_write_iter` and the expected crash type is `HANG`. Self-detected RCU stall in the ext4 write path while process accounting writes dirty pages through `ext4_file_write_iter` during exit.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in ext4_file_write_iter`; alternate titles are `stall in ext4_file_write_iter`; extra parsed flags are none. The body is 56 lines and 3076 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: ext4 buffered writeback, dirty-page throttling, accounting file writes, signal/exit syscall path.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/277 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/278 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/278

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in sys_futex` and the expected crash type is `HANG`. RCU grace-period kthread starvation followed by a CPU backtrace in futex wait; the title aliases old `sys_futex` and modern `__x64_sys_futex` naming.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in sys_futex`; alternate titles are `INFO: rcu detected stall in __x64_sys_futex`, `stall in __x64_sys_futex`, `stall in sys_futex`; extra parsed flags are none. The body is 63 lines and 3413 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: RCU GP kthread diagnostics, futex wait scheduling, syscall wrapper title normalization.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/278 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/279 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/279

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in kvm_vcpu_ioctl` and the expected crash type is `HANG`. RCU-preempt stall in `kvm_vcpu_ioctl` where the guest run path handles an EPT violation, emulates instructions, and locks KVM MMU state.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in kvm_vcpu_ioctl`; alternate titles are `stall in kvm_vcpu_ioctl`; extra parsed flags are none. The body is 49 lines and 2730 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: KVM ioctl run path, VMX exit handling, MMU page fault emulation, spinlock acquisition.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/279 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/28 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/28

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `possible deadlock in tty_buffer_flush` and the expected crash type is `LOCKDEP`. Lockdep circular dependency fixture for `tty_buffer_flush`: buffer locking conflicts with `termios_rwsem` while n_tty signal handling is already holding a tty semaphore.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `possible deadlock in tty_buffer_flush`; alternate titles are none; extra parsed flags are `CORRUPTED: Y`. The body is 14 lines and 704 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: tty buffer flushing, n_tty termios locking, lockdep circular dependency output; marked corrupted.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/28 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/280 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/280

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in kvm_vcpu_ioctl` and the expected crash type is `HANG`. Another KVM `kvm_vcpu_ioctl` RCU stall, this time around guest segment access and instruction fetch/decode via `vmx_read_guest_seg_ar`.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in kvm_vcpu_ioctl`; alternate titles are `stall in kvm_vcpu_ioctl`; extra parsed flags are none. The body is 51 lines and 2832 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: VMX segment helpers, x86 instruction decoder, KVM MMU page fault and ioctl execution.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/280 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/281 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/281

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in kvm_vcpu_ioctl` and the expected crash type is `HANG`. KVM `kvm_vcpu_ioctl` stall with an x86 divide-error trap during emulated `idiv`, exercising parser handling of trap frames inside virtualization stacks.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in kvm_vcpu_ioctl`; alternate titles are `stall in kvm_vcpu_ioctl`; extra parsed flags are none. The body is 57 lines and 3276 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: do_error_trap/divide_error, x86 emulator, KVM MMU/EPT handling, ioctl syscall exit.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/281 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/282 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/282

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in kvm_vcpu_ioctl` and the expected crash type is `HANG`. KVM `kvm_vcpu_ioctl` stall after an unrelated overlayfs message; the useful report starts at the RCU-preempt stall and resolves through `vmx_handle_exit` to ioctl.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in kvm_vcpu_ioctl`; alternate titles are `stall in kvm_vcpu_ioctl`; extra parsed flags are none. The body is 45 lines and 2565 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: noise before report, KVM VMX exit handling, ioctl syscall wrappers, RCU stall extraction.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/282 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/283 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/283

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in snd_pcm_oss_release` and the expected crash type is `HANG`. RCU self-detected stall in ALSA OSS PCM release/sync/write code while `snd_pcm_oss_release` unwinds through OSS write and sync helpers.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in snd_pcm_oss_release`; alternate titles are `stall in snd_pcm_oss_release`; extra parsed flags are none. The body is 57 lines and 3101 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: ALSA PCM OSS compatibility layer, hrtimer interrupt RCU reporting, release-side synchronization.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/283 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/284 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/284

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in llcp_sock_sendmsg` and the expected crash type is `HANG`. RCU stall in NFC LLCP send path where the visible interrupted code is printk/console unlock before the report names `llcp_sock_sendmsg`.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in llcp_sock_sendmsg`; alternate titles are `stall in llcp_sock_sendmsg`; extra parsed flags are none. The body is 53 lines and 2905 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: NFC LLCP socket send, console/printk recursion noise, RCU self-stall stack selection.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/284 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/285 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/285

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in sctp_generate_heartbeat_event` and the expected crash type is `HANG`. SCTP heartbeat timer stall with an RCU kthread-starved prelude and softirq context, expected to title on `sctp_generate_heartbeat_event`.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in sctp_generate_heartbeat_event`; alternate titles are `stall in sctp_generate_heartbeat_event`; extra parsed flags are none. The body is 66 lines and 3361 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: SCTP association heartbeat timer, ksoftirqd, RCU kthread starvation diagnostics.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/285 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/286 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/286

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in sctp_generate_heartbeat_event` and the expected crash type is `HANG`. Longer SCTP heartbeat RCU stall variant that repeats starvation/task-dump material and still normalizes to `sctp_generate_heartbeat_event`.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in sctp_generate_heartbeat_event`; alternate titles are `stall in sctp_generate_heartbeat_event`; extra parsed flags are none. The body is 92 lines and 4951 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: SCTP timer callback, RCU self-stall diagnostics, noisy repeated stack material.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/286 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/287 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/287

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in br_handle_frame` and the expected crash type is `HANG`. Network receive-side RCU stall in bridge ingress processing, titled on `br_handle_frame` after softirq/NAPI-style stack frames.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in br_handle_frame`; alternate titles are `stall in br_handle_frame`; extra parsed flags are none. The body is 55 lines and 3571 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: Linux bridge receive path, packet softirq processing, RCU stall frame extraction.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/287 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/288 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/288

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `BUG: soft lockup in smp_call_function` and the expected crash type is `HANG`. Soft lockup fixture in `smp_call_function_single` with alternates for the generic `smp_call_function` title and stall aliases.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `BUG: soft lockup in smp_call_function`; alternate titles are `BUG: soft lockup in smp_call_function_single`, `stall in smp_call_function`, `stall in smp_call_function_single`; extra parsed flags are none. The body is 93 lines and 5694 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: watchdog soft-lockup parser, SMP call-function path, KVM/CPU rendezvous style stack frames.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/288 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/289 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/289

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in ext4_filemap_fault` and the expected crash type is `HANG`. RCU stall in ext4 fault handling where the selected frame is `ext4_filemap_fault`, covering page fault/mmap filesystem paths.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in ext4_filemap_fault`; alternate titles are `stall in ext4_filemap_fault`; extra parsed flags are none. The body is 43 lines and 2804 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: ext4 mmap fault path, page-fault handling, RCU stall title selection.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/289 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/29 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/29

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `possible deadlock in tun_queue_purge` and the expected crash type is `LOCKDEP`. Lockdep IRQ lock inversion fixture for TUN cleanup: `tun_queue_purge` changes `consumer_lock` state and lockdep reports an interrupt-ordering problem.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `possible deadlock in tun_queue_purge`; alternate titles are none; extra parsed flags are `CORRUPTED: Y`. The body is 10 lines and 508 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: TUN device queue purge, lockdep irq inversion output, corrupted lock graph marker.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/29 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/290 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/290

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in ipv6_rcv` and the expected crash type is `HANG`. IPv6 receive-path RCU stall titled on `ipv6_rcv`, useful for network interrupt/softirq parser coverage.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in ipv6_rcv`; alternate titles are `stall in ipv6_rcv`; extra parsed flags are none. The body is 49 lines and 3064 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: IPv6 ingress, network softirq path, RCU stall stack scanning.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/290 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/291 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/291

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in rmdir` and the expected crash type is `HANG`. RCU stall on directory removal, with alternates for `rmdir` and historical `SyS_rmdir` syscall names.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in rmdir`; alternate titles are `INFO: rcu detected stall in SyS_rmdir`, `stall in SyS_rmdir`, `stall in rmdir`; extra parsed flags are none. The body is 34 lines and 2042 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: VFS rmdir syscall path, syscall naming compatibility, RCU stall extraction.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/291 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/292 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/292

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in smp_call_function` and the expected crash type is `HANG`. RCU stall in `smp_call_function_single` similar to 275 but from a distinct log shape, preserving both full and shortened alternate titles.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in smp_call_function`; alternate titles are `INFO: rcu detected stall in smp_call_function_single`, `stall in smp_call_function`, `stall in smp_call_function_single`; extra parsed flags are none. The body is 50 lines and 3313 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: SMP call-function synchronization, RCU scheduler stall, alternate title generation.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/292 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/293 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/293

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in perf_mmap` and the expected crash type is `HANG`. RCU stall in `perf_mmap`, exercising perf event mmap stack parsing and title extraction from an mmap syscall path.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in perf_mmap`; alternate titles are `stall in perf_mmap`; extra parsed flags are none. The body is 52 lines and 2814 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: perf_event mmap, VM area setup, RCU stall report selection.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/293 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/294 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/294

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in lo_ioctl` and the expected crash type is `HANG`. RCU stall in loop-device ioctl handling, with compat ioctl frames ending at `lo_ioctl`/`lo_compat_ioctl`.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in lo_ioctl`; alternate titles are `stall in lo_ioctl`; extra parsed flags are none. The body is 46 lines and 2578 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: loop block-device ioctl, 32-bit compat syscall path, RCU stall parsing.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/294 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/295 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/295

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in rtnl_newlink` and the expected crash type is `HANG`. RTNL newlink RCU stall during GRE/IP tunnel device creation and sysfs/kobject registration.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in rtnl_newlink`; alternate titles are `stall in rtnl_newlink`; extra parsed flags are none. The body is 60 lines and 3883 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: rtnetlink `RTM_NEWLINK`, netdevice registration, kernfs/sysfs kobject creation, GRE tunnel setup.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/295 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/296 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/296

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `BUG: soft lockup in mount` and the expected crash type is `HANG`. NMI watchdog soft lockup in compat mount: `change_mnt_propagation`, `umount_tree`, and `compat_SyS_mount` are the important frames.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `BUG: soft lockup in mount`; alternate titles are `BUG: soft lockup in compat_SyS_mount`, `stall in compat_SyS_mount`, `stall in mount`; extra parsed flags are none. The body is 40 lines and 2681 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: mount namespace propagation, recursive mount attach/graft, 32-bit compat mount syscall.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/296 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/297 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/297

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `BUG: soft lockup in smp_call_function` and the expected crash type is `HANG`. Soft lockup in `smp_call_function_single` from a memory-sanitizer instrumented kernel while closing a block device and invalidating buffer-head LRUs.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `BUG: soft lockup in smp_call_function`; alternate titles are `BUG: soft lockup in smp_call_function_single`, `stall in smp_call_function`, `stall in smp_call_function_single`; extra parsed flags are none. The body is 43 lines and 2528 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: MSAN instrumentation frames, SMP call-function, block device close, task work exit.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/297 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/298 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/298

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in rtnl_newlink` and the expected crash type is `HANG`. Second RTNL newlink RCU stall variant, this one emphasizing sysfs file creation and netdevice kobject registration from a compat sendmsg.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in rtnl_newlink`; alternate titles are `stall in rtnl_newlink`; extra parsed flags are none. The body is 60 lines and 3884 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: rtnetlink newlink, sysfs file creation, netdevice queue kobjects, compat netlink sendmsg.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/298 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/299 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/299

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in sched_ttwu_pending` and the expected crash type is `HANG`. RCU scheduler stall on idle CPU wakeup processing, titled on `sched_ttwu_pending` in the secondary CPU startup/idle path.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in sched_ttwu_pending`; alternate titles are `stall in sched_ttwu_pending`; extra parsed flags are none. The body is 26 lines and 1740 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: scheduler wakeup queue handling, CPU startup idle loop, RCU stall on swapper task.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/299 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/3 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/3

Purpose: negative Linux reporter fixture for syzkaller. It verifies that an RCU informational line without a complete state dump is ignored rather than promoted to a crash report.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, there is intentionally no `TITLE:` header, so no crash should be parsed; alternate titles are none; extra parsed flags are none. The body is 2 lines and 58 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: RCU informational line without stack dump; parser false-positive suppression.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: `ContainsCrash` must be false and `Reporter.Parse` must return nil even though the log contains the phrase `INFO: Stall`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/3 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/30 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/30

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `possible deadlock in tun_device_event` and the expected crash type is `LOCKDEP`. Lockdep SOFTIRQ-safe to SOFTIRQ-unsafe order fixture for TUN device event handling and `consumer_lock` acquisition.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `possible deadlock in tun_device_event`; alternate titles are none; extra parsed flags are `CORRUPTED: Y`. The body is 10 lines and 523 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: TUN notifier path, lockdep softirq safety classes, corrupted lock output.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/30 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/300 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/300

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in smp_call_function` and the expected crash type is `HANG`. RCU stall in `smp_call_function_single` from vmap teardown: TLB shootdown and `vfree` occur while a socket release path unwinds.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in smp_call_function`; alternate titles are `INFO: rcu detected stall in smp_call_function_single`, `stall in smp_call_function`, `stall in smp_call_function_single`; extra parsed flags are none. The body is 48 lines and 3126 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: SMP TLB shootdown, vmap/vunmap cleanup, socket release task-work path.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/300 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/306 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/306

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `KASAN: global-out-of-bounds Read in __aa_lookupn_ns` and the expected crash type is `KASAN-READ`. KASAN global out-of-bounds read in AppArmor namespace lookup: `memcmp`/`strnstr` feeds `__aa_lookupn_ns`, later followed by panic-on-warn noise.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `KASAN: global-out-of-bounds Read in __aa_lookupn_ns`; alternate titles are `bad-access in __aa_lookupn_ns`; extra parsed flags are `PANICKED: Y`. The body is 346 lines and 17949 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: KASAN report parsing, AppArmor profile label parsing, fault-injection noise, panic flag handling.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/306 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/307 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/307

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `KASAN: stack-out-of-bounds Read in do_ip_vs_set_ctl` and the expected crash type is `KASAN-READ`. KASAN stack out-of-bounds read in IPVS setsockopt: string formatting reads past stack storage while `do_ip_vs_set_ctl` emits diagnostics.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `KASAN: stack-out-of-bounds Read in do_ip_vs_set_ctl`; alternate titles are `bad-access in do_ip_vs_set_ctl`; extra parsed flags are none. The body is 64 lines and 4032 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: KASAN stack redzone report, IPVS sockopt control path, `setsockopt` syscall integration.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/307 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/308 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/308

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `general protection fault in __aa_lookupn_ns` and the expected crash type is `DoS`. General protection fault in AppArmor `__aa_lookupn_ns`, with interleaved syzkaller program logs and kobject noise before the AppArmor stack.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `general protection fault in __aa_lookupn_ns`; alternate titles are `bad-access in __aa_lookupn_ns`; extra parsed flags are none. The body is 152 lines and 9019 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: GPF parser, AppArmor profile lookup, noisy executor-program interleaving, bad-access alternate title.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/308 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/309 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/309

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `memory leak in sget` and the expected crash type is `LEAK`. kmemleak-style memory leak report where allocation flows through `sget_userns`/`sget` during debugfs/component initialization.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `memory leak in sget`; alternate titles are none; extra parsed flags are none. The body is 26 lines and 1171 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: leak detector output, VFS superblock allocation, debugfs mount initialization.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/309 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/31 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/31

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `possible deadlock in audit_receive` and the expected crash type is `LOCKDEP`. Lockdep recursive locking fixture for audit: `kauditd` attempts to reacquire `audit_cmd_mutex` in `audit_receive`.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `possible deadlock in audit_receive`; alternate titles are none; extra parsed flags are `CORRUPTED: Y`. The body is 10 lines and 444 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: audit netlink receive path, recursive mutex lockdep output, corrupted lock report.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/31 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/310 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/310

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `memory leak in __kernfs_new_node` and the expected crash type is `LEAK`. Memory leak in `__kernfs_new_node` triggered by TUN netdevice registration and sysfs group/file creation.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `memory leak in __kernfs_new_node`; alternate titles are none; extra parsed flags are none. The body is 26 lines and 1259 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: kmemleak output, kernfs/sysfs IDR allocation, TUN ioctl netdevice creation.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/310 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/311 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/311

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `memory leak in gfs2_sys_fs_add` and the expected crash type is `LEAK`. Memory leak in GFS2 sysfs registration: object naming via `kobject_set_name_vargs` leads into `gfs2_sys_fs_add` while mounting GFS2.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `memory leak in gfs2_sys_fs_add`; alternate titles are none; extra parsed flags are none. The body is 26 lines and 1197 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: kmemleak output, GFS2 mount/fill_super, kobject naming and sysfs registration.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/311 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/312 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/312

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `memory leak in map_create` and the expected crash type is `LEAK`. Memory leak in BPF map creation: per-CPU allocator frames lead through `htab_map_alloc` into `map_create` from the `bpf` syscall.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `memory leak in map_create`; alternate titles are none; extra parsed flags are none. The body is 21 lines and 928 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: kmemleak output, BPF hash map allocation, percpu allocator, `__x64_sys_bpf`.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/312 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/313 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/313

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `PANIC: double fault in kvm_async_pf_task_wait` and the expected crash type is `DoS`. Double-fault panic in `kvm_async_pf_task_wait`, covering fatal fault parsing with KVM asynchronous page-fault wait context.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `PANIC: double fault in kvm_async_pf_task_wait`; alternate titles are none; extra parsed flags are `PANICKED: Y`. The body is 52 lines and 3073 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: x86 double fault handler, KVM async page-fault wait, panic report extraction.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/313 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/314 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/314

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `PANIC: double fault in compat_sock_ioctl` and the expected crash type is `DoS`. Double-fault panic in `compat_sock_ioctl`, including a compat networking ioctl stack and machine-halted panic marker.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `PANIC: double fault in compat_sock_ioctl`; alternate titles are none; extra parsed flags are `CORRUPTED: Y`, `PANICKED: Y`. The body is 44 lines and 2891 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: x86 double fault, compat socket ioctl, net device ioctl path, panic flag handling.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/314 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/315 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/315

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `PANIC: double fault in corrupted` and the expected crash type is `DoS`. Early boot double fault whose visible RIP is `trace_hardirqs_off_thunk`; expected title uses `corrupted` because the stack is unreliable.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `PANIC: double fault in corrupted`; alternate titles are none; extra parsed flags are `CORRUPTED: Y`, `PANICKED: Y`. The body is 47 lines and 3164 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: early boot panic, corrupted-stack classification, double-fault handling, placeholder pointer output.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/315 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/316 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/316

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `kernel panic: corrupted stack end in sys_socket` and the expected crash type is `DoS`. ARM64 corrupted stack-end panic inside scheduler while creating a socket; alternates normalize `sys_socket` and `__arm64_sys_socket` plus stack-overflow names.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `kernel panic: corrupted stack end in sys_socket`; alternate titles are `kernel panic: corrupted stack end in __arm64_sys_socket`, `stack-overflow in __arm64_sys_socket`, `stack-overflow in sys_socket`; extra parsed flags are `PANICKED: Y`. The body is 29 lines and 1234 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: arm64 syscall wrapper naming, scheduler stack-end detection, socket allocation/security hooks.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/316 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/317 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/317

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `unexpected kernel reboot` and the expected crash type is `REBOOT`. Unexpected kernel reboot fixture: a fresh SeaBIOS and full Linux boot log appears after prior machine state, with no ordinary oops stack.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `unexpected kernel reboot`; alternate titles are none; extra parsed flags are none. The body is 1140 lines and 74312 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: reboot detection, boot banner parsing, SeaBIOS/Linux boot transition, long benign boot-log noise.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/317 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/318 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/318

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `INFO: rcu detected stall in kvm_vm_compat_ioctl` and the expected crash type is `HANG`. Older-format RCU stall in `kvm_vm_compat_ioctl` using bracketed symbol addresses and `compat_SyS_ioctl`/sysenter frames.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `INFO: rcu detected stall in kvm_vm_compat_ioctl`; alternate titles are `stall in kvm_vm_compat_ioctl`; extra parsed flags are none. The body is 31 lines and 2050 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: legacy stack format, KVM VM compat ioctl, KAISER/BTI sysenter path, RCU stall parsing.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/318 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/32 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/32

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `possible deadlock in serial8250_console_write` and the expected crash type is `LOCKDEP`. Lockdep circular dependency in 8250 console write: `swapper/2` tries to acquire `port_lock_key` in `serial8250_console_write`.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `possible deadlock in serial8250_console_write`; alternate titles are none; extra parsed flags are `CORRUPTED: Y`. The body is 11 lines and 502 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: serial console locking, lockdep circular dependency report, corrupted lock graph marker.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/32 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/320 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/320

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `kernel panic: stack is corrupted in udp4_lib_lookup2` and the expected crash type is `DoS`. Stack-protector panic naming `udp4_lib_lookup2`, with only a compact panic header and reboot delay line after the call trace marker.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `kernel panic: stack is corrupted in udp4_lib_lookup2`; alternate titles are none; extra parsed flags are `PANICKED: Y`. The body is 10 lines and 495 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: stack canary panic, IPv4 UDP lookup, minimal panic report extraction.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/320 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/321 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/321

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `kernel panic: stack is corrupted in br_dev_xmit` and the expected crash type is `DoS`. Stack-protector panic in bridge transmit `br_dev_xmit`, preceded by a bridge self-source packet warning and followed by GRE/IP tunnel xmit frames.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `kernel panic: stack is corrupted in br_dev_xmit`; alternate titles are none; extra parsed flags are `PANICKED: Y`. The body is 115 lines and 5695 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: bridge transmit path, GRE tunnel packet loop, stack canary panic, networking call chain.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/321 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/322 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/322

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `kernel panic: stack is corrupted in ip6_xmit` and the expected crash type is `DoS`. Stack-protector panic where the raw panic address is resolved to `ip6_xmit` in the expected title; stack includes L2TP/PPPoL2TP send frames.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `kernel panic: stack is corrupted in ip6_xmit`; alternate titles are none; extra parsed flags are `PANICKED: Y`. The body is 50 lines and 3039 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: IPv6 transmit, L2TP PPP sendmsg, stack canary panic with symbol resolution.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/322 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/323 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/323

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `general protection fault in corrupted` and the expected crash type is `DoS`. Corrupted general-protection/double-fault cascade with repeated `vmalloc_fault` entries; expected bad-access title falls back to `corrupted`.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `general protection fault in corrupted`; alternate titles are `bad-access in corrupted`; extra parsed flags are `CORRUPTED: Y`, `PANICKED: Y`. The body is 126 lines and 9385 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: interrupt-time GPF, repeated fault cascade, corrupted/panicked classification, ebtables noise.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/323 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/324 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/324

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `BUG: unable to handle kernel paging request in lookup_object` and the expected crash type is `MEMORY_SAFETY_BUG`. Kernel paging request in `lookup_object` during kmemleak scan, with a concurrent double fault in UDP6 lookup and panic markers.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `BUG: unable to handle kernel paging request in lookup_object`; alternate titles are `bad-access in lookup_object`; extra parsed flags are `CORRUPTED: Y`, `PANICKED: Y`. The body is 170 lines and 12334 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: kmemleak object lookup, page fault report, double-fault interleaving, memory-safety type classification.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/324 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/325 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/325

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `PANIC: double fault in __udp6_lib_lookup` and the expected crash type is `DoS`. Double-fault panic in `__udp6_lib_lookup`; the log includes a reboot/SeaBIOS tail after machine halt.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `PANIC: double fault in __udp6_lib_lookup`; alternate titles are none; extra parsed flags are `CORRUPTED: Y`, `PANICKED: Y`. The body is 57 lines and 3286 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: IPv6 UDP lookup, x86 double fault, panic extraction before reboot banner.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/325 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/326 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/326

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `PANIC: double fault in corrupted` and the expected crash type is `DoS`. Corrupted double-fault/page-fault cascade around `__udp6_lib_lookup` and repeated `vmalloc_fault` reports, expected to title as corrupted.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `PANIC: double fault in corrupted`; alternate titles are none; extra parsed flags are `CORRUPTED: Y`, `PANICKED: Y`. The body is 99 lines and 7408 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: double fault plus page fault interleaving, UDP6 lookup, repeated interrupt fault reports.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/326 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/327 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/327

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `PANIC: double fault in corrupted` and the expected crash type is `DoS`. Very short corrupted double-fault followed immediately by SeaBIOS boot text, validating detection when the crash line and reboot banner are adjacent.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `PANIC: double fault in corrupted`; alternate titles are none; extra parsed flags are `CORRUPTED: Y`. The body is 23 lines and 812 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: double fault prefix, reboot banner boundary, corrupted non-panicked expectation.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/327 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/328 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/328

Purpose: Linux reporter fixture for syzkaller; expected parsed title is `kernel panic: stack is corrupted in ktime_get` and the expected crash type is `DoS`. Stack-protector panic in `ktime_get` with a compact panic header and reboot delay.

Important APIs, types, and functions: this is data consumed by the syzkaller `pkg/report` test harness rather than executable Go code. `report_test.go` reads this file with `parseReport`, strips carriage returns, parses `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, and related headers, then compares the expected values with `Reporter.Parse`, `ContainsCrash`, and `ParseFrom`. The fixture exercises the Linux reporter implementation in `linux.go`, generic `Report` fields from `report.go`, and crash type mapping through `crash.TitleToType`.

Control flow: the test runner enumerates `pkg/report/testdata/linux/report`, constructs a Linux reporter, loads this fixture, separates the leading expectation headers from the console log at the first blank line, and parses the remaining log bytes. For this file, expected parsed title is `kernel panic: stack is corrupted in ktime_get`; alternate titles are none; extra parsed flags are `PANICKED: Y`. The body is 10 lines and 481 bytes, so the parser sees the complete diagnostic shape rather than a sampled stack.

State and persistence behavior: the fixture is static testdata. It persists no runtime state, but it encodes expected parser state in header fields and the raw kernel-console transcript. The relevant transient parser state is the detected title, alternate titles, crash type, corrupted/panicked flags, report byte range, skip position, and executor metadata when present.

Dependencies and integration points: timekeeping function stack canary failure, minimal panic extraction, panic flag handling.. At repository level, the integration point is `TestParse` in `pkg/report/report_test.go`, with Linux-specific matching rules and oops tables in `pkg/report/linux.go`; syzkaller managers depend on the same parsing path to turn VM console output into deduplicated crash reports.

Risks and edge cases: this fixture can regress if Linux symbol names, syscall wrapper names, sanitizer wording, lockdep formatting, or reboot banners are matched too narrowly. The parser also has to ignore unrelated noise before, after, or inside the diagnostic, avoid over-preferring helper frames such as timer/RCU/watchdog functions, and preserve the expected corrupted or panicked classification when the stack is unreliable.

Test signals: the header values drive the expected parse result, the raw log must produce a non-empty `Report.Report`, and the parsed start/end positions must allow `ParseFrom` to rediscover the same report while skipping it after the report end.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/328 -->
