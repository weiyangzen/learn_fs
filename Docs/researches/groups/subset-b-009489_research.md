# subset-b-009489 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/406 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/406

Purpose: Linux reporter parse fixture for syzkaller. It encodes the expected title `WARNING: refcount bug in hci_register_dev`, type `REFCOUNT_WARNING`, corrupted flag `N`, and panic signal `Y`. The raw body covers Bluetooth HCI virtual device registration hitting `refcount_t: increment on 0` through kobject/device registration, so the reporter must classify a refcount warning rather than a generic warning.

Important APIs, types, and functions: this is static testdata for `pkg/report/report_test.go`, not executable Go code. It exercises `Reporter.ContainsCrash`, `Reporter.Parse`, `Reporter.ParseFrom`, Linux oops matchers in `linux.go`, generic `Report` fields, and `crash.TitleToType`. Key stack signals include `refcount_inc_checked`, `kobject_get`, `kobject_add_internal`, `device_add`, `hci_register_dev`, `__vhci_create_device`, and `vhci_write`.

Control flow: the test harness reads expectation headers, feeds the remaining 72 log lines to the Linux reporter, and expects the title/type/panic fields to match. The call path begins with a userspace `write`, enters `vhci_write`, registers an HCI device, and panics because `panic_on_warn` follows the refcount warning.

State and persistence behavior: all persistent state is textual fixture data. Runtime state is transient parser state: selected oops, title, type, offsets, report bytes, and panic/corruption flags. No external mutation occurs.

Dependencies, integration points, risks, and test signals: the fixture protects syzkaller crash deduplication for Bluetooth/kobject refcount warnings. Risks are over-normalizing the title to `refcount_inc_checked` or losing the subsystem frame. Passing tests require crash detection, `REFCOUNT_WARNING`, panicked `Y`, non-corrupted `N`, and stable `ParseFrom` behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/406 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/407 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/407

Purpose: Linux reporter parse fixture for syzkaller. It encodes `WARNING: kobject bug in netdev_register_kobject`, type `WARNING`, corrupted `N`, panicked `Y`. The log covers a kobject duplicate/name warning during network device registration and validates that syzkaller reports the netdev registration site rather than only the kobject helper.

Important APIs, types, and functions: this static fixture is consumed by `pkg/report/report_test.go` via the Linux reporter path. Relevant parser APIs are `ContainsCrash`, `Parse`, `ParseFrom`, Linux warning/oops recognizers, and crash type mapping. Stack signals include `kobject_add_internal.cold.13`, `kobject_add`, `device_add`, `netdev_register_kobject`, `register_netdevice`, and netlink/USB execution context later in the trace.

Control flow: after headers, 88 log lines are parsed. The kernel warns in `lib/kobject.c`, escalates to panic due to `panic_on_warn`, and unwinds through network device registration. The reporter must use the header expectation and stack extraction rules to produce the netdev-specific title.

State and persistence behavior: the only persistent state is the fixture. Parser state includes matching offsets, selected frame, crash type, and panic flag; there is no I/O beyond reading the testdata.

Dependencies, integration points, risks, and test signals: this integrates the Linux kobject warning regexes with network-device deduplication. The main risk is choosing `kobject_add_internal` as the title frame, which would collapse unrelated kobject warnings. Passing tests require type `WARNING`, panic `Y`, non-corrupted output, and exact title preservation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/407 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/408 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/408

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING: refcount bug in input_register_device`, type `REFCOUNT_WARNING`, corrupted `N`, panicked `Y`. The log covers input device registration hitting `refcount_inc` on zero through kobject parent acquisition.

Important APIs, types, and functions: this file is static Linux report testdata. It exercises syzkaller report parsing APIs and Linux refcount warning title extraction. Important stack frames include `refcount_inc`, `kobject_get`, `get_device_parent.isra.27`, `device_add`, and `input_register_device`.

Control flow: the test reads the headers, parses 80 log lines, sees the warning at `lib/refcount.c:153`, and verifies the title points at the input registration operation. The kernel path is an input-device add path ending in a panic after warning.

State and persistence behavior: expected parser output is persisted in the text headers. Runtime state is limited to parser match state, report slices, selected frame, and flags.

Dependencies, integration points, risks, and test signals: this protects refcount-warning classification for input subsystem crashes used by syzkaller dashboard grouping. Risks include mapping the title to `refcount_inc` or `device_add` instead of `input_register_device`. Test success requires the refcount crash type, panicked flag, non-corruption, and stable crash boundary extraction.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/408 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/409 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/409

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING: ODEBUG bug in usbhid_disconnect`, type `WARNING`, corrupted `N`, panicked `Y`. The raw log is a debugobjects report for freeing an active `timer_list` with hint `hid_retry_timeout` during USB HID disconnect.

Important APIs, types, and functions: the fixture exercises Linux ODEBUG warning parsing. Relevant syzkaller APIs are the standard report test harness and Linux warning recognizers. Important frames include `debug_print_object`, `debug_check_no_obj_freed`, `__free_pages_ok`, and `usbhid_disconnect`.

Control flow: the parser sees an `ODEBUG: free active` line, the subsequent `WARNING`, and a panic-on-warn stack. It must attribute the report to `usbhid_disconnect`, not the generic debugobjects or memory-freeing helpers.

State and persistence behavior: static headers persist title/type/panic expectations. Parser state records the selected crash span and frame but no external state is changed.

Dependencies, integration points, risks, and test signals: this integrates debugobjects warnings with USB HID teardown grouping. The risk is treating the hint `hid_retry_timeout` as the primary title or losing disconnect context. Passing tests require a warning type, panic `Y`, non-corrupted report, and the expected ODEBUG title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/409 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/41 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/41

Purpose: Linux reporter parse fixture for syzkaller. It expects `UBSAN: undefined-behaviour in ip_idents_reserve`, type `UBSAN`, corrupted `N`, panicked `N`. The log covers an arithmetic overflow detected by UBSAN in the IPv4 IP ID reservation path.

Important APIs, types, and functions: this static fixture targets UBSAN report recognition in the Linux reporter. Relevant frames include `dump_stack`, `ubsan_epilogue`, `handle_overflow`, `__ubsan_handle_add_overflow`, `ip_idents_reserve`, and `__ip_select_ident`.

Control flow: the harness parses the fixture headers and 18 log lines, then expects the UBSAN title extractor to skip generic UBSAN helpers and select `ip_idents_reserve`. No panic path is present.

State and persistence behavior: state is confined to fixture text and transient parse results. The parser must preserve the non-panicked result and keep the report non-corrupted.

Dependencies, integration points, risks, and test signals: this protects syzkaller grouping for UBSAN undefined behavior in networking code. Risks include collapsing all overflow reports into `__ubsan_handle_add_overflow` or requiring a panic. Success is title equality, `UBSAN` type, and no panic flag.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/41 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/410 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/410

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Read in hiddev_read`, alternate `bad-access in hiddev_read`, type `KASAN-USE-AFTER-FREE-READ`, corrupted `N`, panicked `N`. The body covers a KASAN read UAF surfaced while HID device userspace reads are finishing wait/lock handling.

Important APIs, types, and functions: this fixture exercises KASAN parsing, access-mode classification, alternate title creation, and frame selection. Key frames include `__lock_acquire`, `kasan_report`, `finish_wait`, `hiddev_read`, `__vfs_read`, and `vfs_read`.

Control flow: 153 log lines are fed to the reporter. The KASAN report first names a lockdep/internal access, but the expected title is the higher-level HID read site. The parser must extract read direction and UAF type while retaining the subsystem frame.

State and persistence behavior: the fixture stores expected fields; runtime state is report-byte boundaries, KASAN metadata, selected frame, and alternate title.

Dependencies, integration points, risks, and test signals: this protects KASAN crash deduplication for HID char-device read paths. Risks include selecting `__lock_acquire` or losing the `Read` access direction. Passing tests require exact title, bad-access alternate, UAF-read type, and non-panicked/non-corrupted flags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/410 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/411 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/411

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING in r871xu_dev_remove`, type `WARNING`, corrupted `N`, panicked `Y`. The raw report is a network-core unregister warning reached during Realtek USB wireless device removal.

Important APIs, types, and functions: the fixture exercises warning parsing and subsystem frame extraction. Significant frames include `rollback_registered_many.cold`, `rollback_registered`, `unregister_netdevice_queue`, `unregister_netdev`, and `r871xu_dev_remove`.

Control flow: the test feeds 77 log lines. A warning at `net/core/dev.c` panics; stack extraction must walk past generic unregister helpers to the driver removal function.

State and persistence behavior: only fixture headers and raw console text persist. Runtime parser state is transient and determines title/type/panic/corruption.

Dependencies, integration points, risks, and test signals: this integrates Linux warning handling with USB network driver teardown reports. The risk is grouping under `rollback_registered_many` instead of the driver function. Passing tests require the expected title, warning type, panic flag, and no corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/411 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/412 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/412

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING in default_device_exit_batch`, type `WARNING`, corrupted `N`, panicked `Y`. The body covers network namespace cleanup warning during default device exit batching.

Important APIs, types, and functions: this fixture tests Linux warning stack extraction. Key frames include `rollback_registered_many`, `unregister_netdevice_many`, `default_device_exit_batch`, `ops_exit_list.isra.5`, and `cleanup_net`.

Control flow: 108 log lines are parsed after headers. The warning is emitted in network-core unregister code and escalates via panic-on-warn, while the expected title points to namespace cleanup's `default_device_exit_batch`.

State and persistence behavior: all state is fixture text plus transient parser fields. There is no persistence beyond the source file.

Dependencies, integration points, risks, and test signals: this supports syzkaller grouping for net namespace teardown warnings. Risks are overfitting to the warning source line or selecting generic cleanup helpers. Passing tests require type `WARNING`, panicked `Y`, non-corrupted `N`, and the expected title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/412 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/413 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/413

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Read in iowarrior_disconnect`, alternate `bad-access in iowarrior_disconnect`, type `KASAN-USE-AFTER-FREE-READ`, corrupted `N`, panicked `N`. The log covers an IOWarrior USB disconnect path racing with mutex/list state.

Important APIs, types, and functions: this tests KASAN read UAF title extraction. Relevant frames include `__list_del_entry_valid`, `mutex_remove_waiter`, `__mutex_lock`, `iowarrior_disconnect`, `usb_unbind_interface`, and driver core removal helpers.

Control flow: 111 log lines are parsed. Although the low-level invalid access is in list/mutex helpers, the reporter must attribute the crash to the USB driver disconnect function and generate the bad-access alternate.

State and persistence behavior: expected parser output is stored in headers. Runtime state includes selected KASAN metadata, title frame, and report span.

Dependencies, integration points, risks, and test signals: this protects KASAN grouping for USB driver disconnect races. Risks include selecting `__list_del_entry_valid` as the title. Passing tests require exact title, alternate, UAF-read type, no panic, and no corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/413 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/414 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/414

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Write in iowarrior_disconnect`, alternate `bad-access in iowarrior_disconnect`, type `KASAN-USE-AFTER-FREE-WRITE`, corrupted `N`, panicked `N`. The body is a write UAF in USB URB teardown during IOWarrior disconnect.

Important APIs, types, and functions: this fixture exercises KASAN write classification and USB disconnect frame selection. Important frames include `usb_kill_urb`, `check_memory_region`, `iowarrior_disconnect`, `usb_unbind_interface`, `device_release_driver_internal`, and `device_del`.

Control flow: the parser consumes 109 log lines, recognizes the KASAN UAF report, infers write access, and attributes it to `iowarrior_disconnect` rather than `usb_kill_urb`.

State and persistence behavior: the file persists headers and console text. Runtime parser state is temporary report metadata and flags.

Dependencies, integration points, risks, and test signals: this pairs with report 413 and checks read/write distinctions for the same disconnect path. The key risk is losing access direction or over-grouping under USB core helpers. Passing tests require UAF-write type and the exact title/alternate.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/414 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/415 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/415

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING: ODEBUG bug in netdev_freemem`, type `WARNING`, corrupted `N`, panicked `Y`. The report is a debugobjects active `timer_list` warning with hint `delayed_work_timer_fn` during network device memory freeing.

Important APIs, types, and functions: this tests ODEBUG warning recognition and network-device teardown title selection. Stack signals include `debug_check_no_obj_freed`, `kfree`, `kvfree`, `netdev_freemem`, `free_netdev`, and `usbnet_disconnect`.

Control flow: 51 log lines are parsed. The warning is generated by debugobjects while freeing memory; the parser must keep the netdev free context and panic flag.

State and persistence behavior: static headers store expected parser state; parsing itself mutates only in-memory report fields.

Dependencies, integration points, risks, and test signals: this protects syzkaller grouping for delayed-work timer lifetime bugs in net devices. Risks are choosing the timer hint or memory allocator as the title. Passing tests require warning type, panic `Y`, non-corruption, and `netdev_freemem` in the title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/415 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/416 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/416

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Write in video_unregister_device`, alternate `bad-access in video_unregister_device`, type `KASAN-USE-AFTER-FREE-WRITE`, corrupted `N`, panicked `N`. The log covers video device unregister after USBVision lifetime corruption.

Important APIs, types, and functions: this static fixture exercises KASAN write UAF parsing. Important frames include `kobject_del`, `device_del`, `device_unregister`, `video_unregister_device`, `usbvision_unregister_video`, and `usbvision_release`.

Control flow: 108 log lines are parsed. KASAN reports a write in kobject/device deletion, and the title extractor must select the media subsystem unregister site.

State and persistence behavior: expected state is in headers; runtime parsing is temporary and read-only.

Dependencies, integration points, risks, and test signals: this integrates KASAN parsing with V4L/media driver teardown deduplication. Risks are grouping under `kobject_del` or `device_del` instead of `video_unregister_device`. Passing tests require UAF-write classification, bad-access alternate, and no panic/corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/416 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/417 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/417

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Read in usbvision_release`, alternate `bad-access in usbvision_release`, type `KASAN-USE-AFTER-FREE-READ`, corrupted `N`, panicked `N`. The body covers sysfs file removal after USBVision device release.

Important APIs, types, and functions: this fixture targets KASAN read UAF extraction. Key frames include `sysfs_remove_file_ns`, `device_remove_file`, `usbvision_release`, `usbvision_radio_close.cold`, `v4l2_release`, `__fput`, and `task_work_run`.

Control flow: the harness parses 103 log lines, recognizes KASAN UAF-read metadata, and selects `usbvision_release` as the meaningful frame above sysfs/device helpers.

State and persistence behavior: only the fixture persists; parser fields are in-memory.

Dependencies, integration points, risks, and test signals: this protects media/USB release crash grouping. Risks include selecting sysfs helpers or losing release context. Passing tests require exact title, alternate, UAF-read type, no panic, and no corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/417 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/418 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/418

Purpose: Linux reporter parse fixture for syzkaller. It expects `general protection fault in hdm_disconnect`, alternate `bad-access in hdm_disconnect`, type `DoS`, corrupted `N`, panicked `Y`. The log covers a GPF during MOST HDM USB disconnect.

Important APIs, types, and functions: this static report tests non-KASAN bad-access title extraction. Significant frames include `device_unregister`, `hdm_disconnect`, `usb_unbind_interface`, `device_release_driver_internal`, `usb_disconnect`, `hub_event`, and worker thread helpers.

Control flow: 60 log lines are parsed. The exception is fatal and escalates to panic, and the reporter must classify it as DoS while generating the bad-access alternate.

State and persistence behavior: fixture text holds expected state. Runtime state is selected oops, frame, flags, and report boundaries.

Dependencies, integration points, risks, and test signals: this supports syzkaller grouping for USB disconnect GPFs. Risks include selecting `device_unregister` or `usb_unbind_interface` instead of `hdm_disconnect`. Passing tests require the GPF title, DoS type, alternate, and panic flag.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/418 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/419 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/419

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in ld_usb_write`, alternate `hang in ld_usb_write`, type `HANG`, corrupted `N`, panicked `Y`. The body is a hung task in USB control-message write for the LD USB driver.

Important APIs, types, and functions: this tests hung-task parsing and stack filtering. Key frames include `schedule`, `wait_for_completion_timeout`, `usb_start_wait_urb`, `usb_control_msg`, `ld_usb_write`, `__vfs_write`, `vfs_write`, and syscall write frames.

Control flow: 115 log lines contain the blocked task and lock debug data. The parser must skip scheduler/wait helpers and select the device write operation; panic is set because the hung task triggers panic in this fixture.

State and persistence behavior: fixture headers persist expected parser output; runtime state is transient crash matching and flag extraction.

Dependencies, integration points, risks, and test signals: this protects hang classification for USB write paths. Risks are selecting `wait_for_completion_timeout` or generic VFS/syscall frames. Passing tests require HANG type, panic `Y`, title/alternate equality, and non-corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/419 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/42 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/42

Purpose: Linux reporter parse fixture for syzkaller. It expects `UBSAN: undefined-behaviour in corrupted`, type `UBSAN`, corrupted `Y`, panicked `N`. This is an intentionally tiny corrupted UBSAN fixture.

Important APIs, types, and functions: the file exercises the Linux reporter's ability to return a crash with a corrupted title when stack/function data is insufficient. It still uses the normal `ContainsCrash`, `Parse`, and `ParseFrom` test path, but no meaningful stack functions are present.

Control flow: after headers, only two log lines remain. The parser must detect UBSAN undefined-behaviour syntax but mark the extracted function as corrupted instead of inventing a frame.

State and persistence behavior: the fixture persists the corruption expectation in `CORRUPTED: Y`; runtime parser state is temporary.

Dependencies, integration points, risks, and test signals: this protects negative/partial-report handling. Risks include treating missing stack context as a parser failure or misclassifying corruption as a clean report. Passing tests require UBSAN type, title ending in `corrupted`, corrupted `Y`, and no panic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/42 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/420 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/420

Purpose: Linux reporter parse fixture for syzkaller. This file has no expectation headers and acts as a negative/no-crash fixture. Its five body lines must not produce a parsed crash.

Important APIs, types, and functions: it still runs through the same report test harness, especially `ContainsCrash` and `Parse`, but expected title/type are empty. No stack frames or crash-specific functions are present.

Control flow: the harness reads the file, finds no `TITLE:` header, and expects the Linux reporter not to report a crash from the remaining text. This validates that incidental console text does not trigger an oops matcher.

State and persistence behavior: the fixture stores absence of expectations as its state. Parser runtime state should remain empty or no-crash.

Dependencies, integration points, risks, and test signals: this protects false-positive resistance in syzkaller's Linux report parser. The risk is broadening regexes so ordinary lines become a crash. Passing tests require `ContainsCrash` false and no non-empty parsed report/title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/420 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/421 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/421

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: rcu detected stall in sys_exit_group`, alternates for `__x64_sys_exit_group` and stall wording, type `HANG`, corrupted `N`, panicked `N`. The log covers an RCU preempt self-detected stall with NMI backtraces and network softirq activity.

Important APIs, types, and functions: this tests RCU stall title extraction and alternate generation. Key frames include `rcu_gp_kthread`, `hhf_dequeue`, `__qdisc_run`, bridge forwarding, IGMP timer paths, `_raw_write_unlock_irq`, `do_exit`, `do_group_exit`, and `__x64_sys_exit_group`.

Control flow: 261 log lines are parsed. The reporter must recognize the RCU stall headline, inspect NMI/user task stacks, and choose the syscall exit path as the title while preserving alternates.

State and persistence behavior: expected alternates are persisted in headers; runtime state is crash span, stack scanning state, and flags.

Dependencies, integration points, risks, and test signals: this protects hang grouping for RCU stall reports with noisy multi-CPU stacks. Risks include selecting softirq bridge frames or RCU kthread helpers. Passing tests require HANG type, all alternates, no panic, and no corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/421 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/422 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/422

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Read in hso_probe`, alternate `bad-access in hso_probe`, type `KASAN-USE-AFTER-FREE-READ`, corrupted `N`, panicked `N`. The body covers HSO USB serial probing and tty device unregister/destruction lifetime issues.

Important APIs, types, and functions: this tests KASAN read UAF parsing in probe paths. Significant frames include `__mutex_lock`, `device_del`, `device_destroy`, `tty_unregister_device`, `hso_probe.cold`, `usb_probe_interface`, and `really_probe`.

Control flow: 173 log lines are parsed. The report names a low-level mutex access, but the expected title is the driver probe function where teardown/probe sequencing is meaningful.

State and persistence behavior: fixture headers are persistent; parser state is transient KASAN metadata, selected frame, and flags.

Dependencies, integration points, risks, and test signals: this protects USB serial probe crash grouping. Risks include selecting `__mutex_lock` or tty core helpers. Passing tests require exact title, bad-access alternate, UAF-read type, and no panic/corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/422 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/423 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/423

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Read in mcba_usb_disconnect`, alternate `bad-access in mcba_usb_disconnect`, type `KASAN-USE-AFTER-FREE-READ`, corrupted `N`, panicked `N`. The report covers CAN MCBA USB disconnect while anchored URBs and locks are being torn down.

Important APIs, types, and functions: this tests KASAN read UAF extraction and USB driver frame selection. Key frames include `__lock_acquire`, `usb_kill_anchored_urbs`, `mcba_usb_disconnect`, `usb_unbind_interface`, and `device_release_driver_internal`.

Control flow: 95 log lines are parsed. The parser must skip lockdep internals and assign the crash to the MCBA USB disconnect callback.

State and persistence behavior: fixture text persists expected fields; parser runtime state is temporary.

Dependencies, integration points, risks, and test signals: this protects CAN/USB disconnect grouping and bad-access alternate generation. Risks include title drift to `__lock_acquire` or USB core helpers. Passing tests require UAF-read type, expected title/alternate, no panic, and no corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/423 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/424 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/424

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Read in chaoskey_disconnect`, alternate `bad-access in chaoskey_disconnect`, type `KASAN-USE-AFTER-FREE-READ`, corrupted `N`, panicked `N`. The report covers hardware RNG unregister and kthread stopping during ChaosKey USB disconnect.

Important APIs, types, and functions: this tests KASAN UAF-read parsing around refcount helpers. Key frames include `refcount_inc_not_zero_checked`, `refcount_inc_checked`, `kthread_stop`, `hwrng_unregister`, `chaoskey_disconnect`, and `usb_unbind_interface`.

Control flow: 89 log lines are parsed. The crash begins at refcount/KASAN helpers, but the title must identify the USB disconnect callback.

State and persistence behavior: expected parser output is stored in headers. Runtime state is transient KASAN and frame-selection metadata.

Dependencies, integration points, risks, and test signals: this protects syzkaller grouping for hardware RNG USB teardown. Risks include misclassifying as a refcount warning instead of KASAN UAF or selecting `hwrng_unregister`. Passing tests require UAF-read type, exact title/alternate, and no panic/corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/424 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/425 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/425

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING in pvr2_i2c_core_done`, type `WARNING`, corrupted `N`, panicked `Y`. The body covers sysfs group removal warning during PVR2 I2C adapter teardown.

Important APIs, types, and functions: this tests warning extraction in media/I2C teardown. Frames include `sysfs_remove_group`, `dpm_sysfs_remove`, `device_del`, `device_unregister`, `i2c_del_adapter`, and `pvr2_i2c_core_done`.

Control flow: 62 log lines are parsed. The warning originates in sysfs but should be attributed to the PVR2 I2C cleanup path; panic-on-warn sets the panicked flag.

State and persistence behavior: headers persist parser expectations; runtime state is read-only and temporary.

Dependencies, integration points, risks, and test signals: this protects deduplication for media USB/I2C cleanup warnings. Risks are title selection from sysfs/device helpers. Passing tests require warning type, panic `Y`, non-corrupted state, and the PVR2 cleanup title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/425 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/426 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/426

Purpose: Linux reporter parse fixture for syzkaller. It also expects `WARNING in pvr2_i2c_core_done`, type `WARNING`, corrupted `N`, panicked `Y`. This companion fixture covers a similar sysfs group removal warning through an I2C client unregister path.

Important APIs, types, and functions: relevant frames include `sysfs_remove_group`, `dpm_sysfs_remove`, `device_del`, `device_unregister`, `__unregister_client`, `i2c_del_adapter`, and `pvr2_i2c_core_done`.

Control flow: 62 log lines are parsed. The parser must normalize a slightly different call chain to the same PVR2 cleanup title, preserving deduplication across teardown variants.

State and persistence behavior: persistent state is textual fixture data; parser state is temporary title/type/flag selection.

Dependencies, integration points, risks, and test signals: this pairs with report 425 to protect stable grouping despite variant stack tails. Risks include splitting the same bug by selecting `__unregister_client` in one fixture. Passing tests require the same expected warning title and panic behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/426 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/427 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/427

Purpose: Linux reporter parse fixture for syzkaller. It expects `KCSAN: data-race in find_next_bit / rcu_report_exp_cpu_mult`, type `KCSAN-DATARACE`, frame `find_next_bit`, corrupted `N`, panicked `N`. The report covers a race between RCU expedited CPU selection and reporting.

Important APIs, types, and functions: this tests KCSAN data-race parsing, dual-frame title generation, and `FRAME:` handling. Key frames include `find_next_bit`, `sync_rcu_exp_select_node_cpus`, `wait_rcu_exp_gp`, `rcu_report_exp_cpu_mult`, `rcu_report_exp_rdp`, and `rcu_exp_handler`.

Control flow: 32 log lines are parsed. The reporter must combine both racing functions into the title and preserve `find_next_bit` as the primary frame.

State and persistence behavior: the `FRAME:` header adds expected parser state beyond title/type. Runtime state is KCSAN report metadata and selected frame.

Dependencies, integration points, risks, and test signals: this protects KCSAN race grouping for RCU internals. Risks are dropping the second racing function or ignoring the frame header. Passing tests require KCSAN-DATARACE type, exact combined title, and frame equality.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/427 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/428 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/428

Purpose: Linux reporter parse fixture for syzkaller. It expects `KCSAN: data-race in e1000_clean_rx_irq`, type `KCSAN-DATARACE`, frame `e1000_clean_rx_irq`, corrupted `N`, panicked `N`. The log covers a KCSAN report in the Intel e1000 receive interrupt path.

Important APIs, types, and functions: this tests single-frame KCSAN title extraction. Key frames include `e1000_clean_rx_irq`, `e1000_clean`, `net_rx_action`, `__do_softirq`, `irq_exit`, and idle tail frames.

Control flow: 23 log lines are parsed. The reporter must select the driver receive-clean function as both title frame and `FRAME` value.

State and persistence behavior: expected frame/type/title are stored in headers; runtime parser state is temporary.

Dependencies, integration points, risks, and test signals: this protects KCSAN grouping for network driver interrupt handling. Risks are selecting generic softirq frames or failing without a second racing stack. Passing tests require exact data-race title and frame.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/428 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/429 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/429

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING: ODEBUG bug in blk_mq_unregister_disk`, type `WARNING`, corrupted `N`, panicked `Y`. The report is a debugobjects warning during block multiqueue disk unregister.

Important APIs, types, and functions: this tests ODEBUG warning parsing in block-device teardown. Frames include `debug_print_object`, `debug_object_init`, `init_timer_key`, `kobject_release`, `kobject_put`, and `blk_mq_unregister_disk`.

Control flow: 78 log lines are parsed. Debugobjects emits the warning; panic-on-warn follows; stack selection must identify the block MQ unregister operation.

State and persistence behavior: expected output is persisted in headers. Parser state is in-memory only.

Dependencies, integration points, risks, and test signals: this protects block-layer crash grouping for timer/debugobject lifetime bugs. Risks include choosing kobject or timer helpers. Passing tests require exact ODEBUG title, warning type, panic `Y`, and no corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/429 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/43 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/43

Purpose: Linux reporter parse fixture for syzkaller. It expects `kernel BUG in corrupted`, type `BUG`, corrupted `Y`, panicked `N`. The file is intentionally minimal and lacks enough stack context for a reliable function.

Important APIs, types, and functions: this exercises BUG detection and corruption marking in the Linux reporter. There are no meaningful crash frames beyond incidental architecture text.

Control flow: after headers, four body lines are parsed. The parser should detect a kernel BUG but mark the title function as corrupted rather than manufacturing a stack frame.

State and persistence behavior: `CORRUPTED: Y` is the key persistent expectation. Runtime parser state remains local to the test.

Dependencies, integration points, risks, and test signals: this guards partial-report behavior. Risks are false negatives for truncated BUG reports or false confidence with a clean title. Passing tests require BUG type, corrupted title, and no panic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/43 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/430 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/430

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in i2c_transfer`, alternate `hang in i2c_transfer`, type `HANG`, corrupted `N`, panicked `N`. The log contains many blocked syz-executor tasks in I2C read/ioctl paths.

Important APIs, types, and functions: this tests hung-task parsing and frame selection in I2C. Key frames include `i2c_transfer`, `i2c_transfer_buffer_flags`, `i2cdev_read`, `aspeed_i2c_master_xfer`, `i2c_smbus_xfer`, `i2cdev_ioctl_smbus`, and syscall read/ioctl frames.

Control flow: 268 log lines are parsed. The first blocked task stack selects `i2c_transfer`; subsequent blocked stacks are related noise and must not change the title.

State and persistence behavior: fixture headers persist expected title/type. Parser runtime state includes first-crash boundary and hang frame selection.

Dependencies, integration points, risks, and test signals: this protects hang grouping for I2C adapter lock/wait issues. Risks include choosing later SMBus ioctl stacks or generic rt-mutex helpers. Passing tests require HANG type, exact title/alternate, no panic, and no corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/430 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/431 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/431

Purpose: Linux reporter parse fixture for syzkaller. It expects `BUG: unable to handle kernel paging request in partition_sched_domains_locked`, alternate `bad-access in partition_sched_domains_locked`, type `MEMORY_SAFETY_BUG`, corrupted `N`, panicked `N`. The report covers a scheduler/cpuset domain rebuild fault.

Important APIs, types, and functions: this tests page-fault/oops parsing and bad-access alternate generation. Key frames include `rebuild_sched_domains_locked`, `update_flag`, `cpuset_css_offline`, `css_killed_work_fn`, `process_one_work`, and `worker_thread`.

Control flow: 39 log lines are parsed. The faulting context is cpuset offline work; the reporter must derive a memory-safety bug title from scheduler partitioning rather than worker helpers.

State and persistence behavior: expected fields persist in headers; parser state is transient.

Dependencies, integration points, risks, and test signals: this protects crash grouping for scheduler/cgroup teardown faults. Risks include selecting workqueue frames or missing bad-access alternate. Passing tests require memory-safety type, title/alternate equality, and non-panicked/non-corrupted flags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/431 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/432 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/432

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in synchronize_rcu`, alternates for `synchronize_rcu_expedited`, type `HANG`, corrupted `N`, panicked `Y`. The log covers network namespace tunnel cleanup blocked in expedited RCU synchronization.

Important APIs, types, and functions: this tests hung-task parsing where generic synchronization APIs are intentionally the title. Frames include `synchronize_rcu_expedited`, `synchronize_net`, `rollback_registered_many`, `unregister_netdevice_many`, `ip_tunnel_delete_nets`, `ipip_exit_batch_net`, and `cleanup_net`.

Control flow: 316 log lines include a blocked cleanup worker and lock debug output. The parser must normalize expedited and non-expedited RCU hang alternates while preserving panic-on-hung-task.

State and persistence behavior: headers persist multiple alternates and panic flag. Runtime state is hang detection and selected frame metadata.

Dependencies, integration points, risks, and test signals: this protects RCU hang grouping in network teardown. Risks include choosing tunnel-specific frames when the expected dedup key is synchronization. Passing tests require all alternates, HANG type, panic `Y`, and no corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/432 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/433 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/433

Purpose: Linux reporter parse fixture for syzkaller. It expects the same `INFO: task hung in synchronize_rcu` title and expedited alternates, type `HANG`, corrupted `N`, panicked `Y`. This variant is a packet socket bind path blocked in `synchronize_net`.

Important APIs, types, and functions: key frames include `synchronize_rcu_expedited`, `synchronize_net`, `__unregister_prot_hook`, `packet_do_bind`, `packet_bind`, `__sys_bind`, and `__x64_sys_bind`.

Control flow: 50 log lines are parsed. The parser must keep the synchronization hang title, not specialize to packet bind, while producing the same alternates as related RCU fixtures.

State and persistence behavior: fixture headers store expected fields; parsing is read-only and transient.

Dependencies, integration points, risks, and test signals: this protects stable deduplication across different callers blocked on expedited RCU. Risks are splitting by packet socket frames. Passing tests require HANG type, panic flag, exact alternates, and non-corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/433 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/434 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/434

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in synchronize_rcu` with expedited alternates, type `HANG`, corrupted `N`, panicked `Y`. The stack is packet socket release and file close waiting in `synchronize_net`.

Important APIs, types, and functions: relevant frames include `synchronize_rcu_expedited`, `synchronize_net`, `packet_release`, `__sock_release`, `sock_close`, `__fput`, `task_work_run`, and signal/exit handling.

Control flow: 81 log lines are parsed. The hang is detected in a task-exit close path, but expected normalization remains the RCU synchronization function.

State and persistence behavior: static headers persist title/alternates; parser state is local.

Dependencies, integration points, risks, and test signals: this protects deduplication of packet release RCU hangs with other synchronization stalls. Risks include selecting `packet_release` or file close frames. Passing tests require HANG type, panic `Y`, alternates, and clean corruption state.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/434 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/435 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/435

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in synchronize_rcu`, alternates for `__synchronize_srcu` and hang wording, type `HANG`, corrupted `N`, panicked `Y`. The body covers fsnotify mark destruction blocked in SRCU synchronization.

Important APIs, types, and functions: this tests hung-task handling for SRCU/RCU naming variants. Frames include `wait_for_completion`, `__synchronize_srcu`, `synchronize_srcu`, `fsnotify_mark_destroy_workfn`, `process_one_work`, and worker thread helpers.

Control flow: 128 log lines are parsed. The reporter must generate alternates that include the SRCU internal function while normalizing the primary title to `synchronize_rcu`.

State and persistence behavior: expected alternates and panic flag are stored in headers. Runtime state is transient hang parsing.

Dependencies, integration points, risks, and test signals: this protects hang grouping for fsnotify SRCU cleanup. Risks include losing the SRCU alternate or selecting worker helpers. Passing tests require the primary/alternate set, HANG type, panic `Y`, and non-corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/435 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/436 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/436

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in rtnl_lock`, alternate `hang in rtnl_lock`, type `HANG`, corrupted `N`, panicked `Y`. The log covers IPv6 address configuration work blocked acquiring RTNL.

Important APIs, types, and functions: key frames include `__mutex_lock`, `mutex_lock_nested`, `rtnl_lock`, `addrconf_verify_work`, `process_one_work`, and `worker_thread`.

Control flow: 132 log lines are parsed. Scheduler and mutex helpers must be skipped until the RTNL lock acquisition is selected; panic is set by the hung-task configuration.

State and persistence behavior: fixture headers persist expected title/type/panic. Runtime parser state is temporary.

Dependencies, integration points, risks, and test signals: this protects network configuration hang grouping. Risks include selecting `__mutex_lock` or workqueue frames. Passing tests require exact RTNL hang title/alternate, HANG type, panic `Y`, and non-corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/436 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/437 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/437

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in synchronize_rcu` with expedited alternates, type `HANG`, corrupted `N`, panicked `Y`. The stack is nfnetlink network namespace exit waiting in `synchronize_net`.

Important APIs, types, and functions: frames include `synchronize_rcu_expedited`, `synchronize_net`, `nfnetlink_net_exit_batch`, `ops_exit_list.isra.0`, `cleanup_net`, workqueue helpers, and semaphore wait paths.

Control flow: 142 log lines are parsed. The parser must normalize the netfilter cleanup hang to the RCU synchronization title and preserve alternates.

State and persistence behavior: expectation headers persist parser fields; runtime state is temporary.

Dependencies, integration points, risks, and test signals: this protects RCU hang deduplication across network namespace cleanup subsystems. Risks include title drift to `nfnetlink_net_exit_batch`. Passing tests require HANG type, panic `Y`, exact alternates, and no corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/437 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/438 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/438

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in synchronize_rcu` with expedited alternates, type `HANG`, corrupted `N`, panicked `Y`. The report covers SIT tunnel network namespace cleanup blocked in RCU synchronization.

Important APIs, types, and functions: key frames include `synchronize_rcu_expedited`, `synchronize_net`, `rollback_registered_many`, `unregister_netdevice_many`, `sit_exit_batch_net`, `ops_exit_list.isra.0`, and `cleanup_net`.

Control flow: 155 log lines are parsed. Despite tunnel-specific teardown frames, the expected dedup key remains the synchronization function and its alternates.

State and persistence behavior: fixture text persists expected outputs; parser state is in-memory.

Dependencies, integration points, risks, and test signals: this pairs with report 432 for tunnel cleanup variants. Risks include splitting IPIP/SIT cleanup by caller. Passing tests require title/alternate normalization, HANG type, panic `Y`, and no corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/438 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/439 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/439

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in synchronize_rcu` with expedited alternates, type `HANG`, corrupted `N`, panicked `Y`. The body covers filesystem/superblock shutdown and backing-device unregister blocked in expedited RCU.

Important APIs, types, and functions: key frames include `synchronize_rcu_expedited`, `bdi_unregister`, `bdi_put`, `generic_shutdown_super`, `fuse_kill_sb_anon`, `deactivate_super`, and mount cleanup helpers.

Control flow: 76 log lines are parsed. The reporter must select the synchronization hang, not the FUSE or BDI teardown callers, and preserve panic-on-hung-task.

State and persistence behavior: expected output persists in headers; runtime state is temporary parse metadata.

Dependencies, integration points, risks, and test signals: this protects cross-subsystem RCU hang grouping outside networking. Risks include caller-specific titles and lost alternates. Passing tests require all expected alternates, HANG type, panic `Y`, and non-corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/439 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/44 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/44

Purpose: Linux reporter parse fixture for syzkaller. It expects `kernel BUG in pte_list_remove`, type `BUG`, corrupted `N`, panicked `N`. The log covers a KVM/MMU page-table list removal assertion.

Important APIs, types, and functions: this tests kernel BUG title extraction from a short stack. Key frames include `pte_list_remove`, `drop_spte`, and `mmu_page_zap_pte`.

Control flow: 24 log lines are parsed. The reporter must select the first meaningful BUG frame and avoid marking the short but sufficient report as corrupted.

State and persistence behavior: fixture headers persist expected type/title; runtime parser state is transient.

Dependencies, integration points, risks, and test signals: this protects BUG grouping for KVM MMU page-table teardown. Risks include false corruption or choosing a lower helper. Passing tests require BUG type, exact title, no panic, and corrupted `N`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/44 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/440 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/440

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in rtnl_lock`, alternate `hang in rtnl_lock`, type `HANG`, corrupted `N`, panicked `Y`. The report covers TIPC network namespace exit blocked on RTNL.

Important APIs, types, and functions: this tests hung-task selection for network teardown lock contention. Key frames include `__mutex_lock`, `mutex_lock_nested`, `rtnl_lock`, `tipc_net_stop`, `tipc_exit_net`, `ops_exit_list.isra.0`, `cleanup_net`, and workqueue helpers.

Control flow: 260 log lines are parsed. The first blocked task stack identifies RTNL lock acquisition; long tail output and additional diagnostic stacks should not change the expected title.

State and persistence behavior: expected title/type/panic are stored in fixture headers; parser runtime state is temporary.

Dependencies, integration points, risks, and test signals: this pairs with report 436 to protect RTNL lock hang deduplication across IPv6 and TIPC callers. Risks include selecting caller-specific `tipc_net_stop` or generic mutex helpers. Passing tests require the RTNL hang title/alternate, HANG type, panic `Y`, and no corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/440 -->
