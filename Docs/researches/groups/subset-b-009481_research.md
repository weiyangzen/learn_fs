# subset-b-009481 research

Grouped research report for syzkaller Linux report testdata fixtures under `sources/test-tools/syzkaller/pkg/report/testdata/linux`. Each section preserves the source path and is wrapped for reconciliation into the source-tree-aligned per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/4 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/4

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `security/keys/key.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `2269` bytes across `46` lines, with content hash prefix `56b07da3abc4` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `refcount_inc`, `dump_stack`, `panic`, `__warn`, `report_bug`, `do_trap`; source-path cues include `security/keys/key.c`, `lib/refcount.c`, `lib/dump_stack.c`, `kernel/panic.c`, `lib/bug.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `------------[ cut here ]------------`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `security/keys/key.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: security/keys/key.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/4 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/40 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/40

Purpose: This fixture validates Linux guilty-file extraction for a KASAN memory-safety report. The expected `FILE` header is `fs/overlayfs/namei.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `5076` bytes across `104` lines, with content hash prefix `c863f9565829` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `string`, `dump_stack`, `__asan_report_load1_noabort`, `vsnprintf`, `vscnprintf`, `vprintk_store`; source-path cues include `fs/overlayfs/namei.c`, `lib/vsprintf.c`, `lib/dump_stack.c`, `mm/kasan/report.c`, `kernel/printk/printk.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `BUG: KASAN: slab-out-of-bounds in string+0x298/0x2d0 lib/vsprintf.c:604`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `fs/overlayfs/namei.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: fs/overlayfs/namei.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/40 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/41 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/41

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `fs/overlayfs/namei.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `2883` bytes across `52` lines, with content hash prefix `640e0ad8a2bf` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__phys_addr`, `kfree`, `ovl_verify_set_fh`, `ovl_fill_super`, `mount_nodev`, `ovl_mount`; source-path cues include `fs/overlayfs/namei.c`, `arch/x86/mm/physaddr.c`, `include/linux/mm.h`, `mm/slab.c`, `fs/overlayfs/overlayfs.h`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `------------[ cut here ]------------`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `fs/overlayfs/namei.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: fs/overlayfs/namei.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/41 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/42 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/42

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `drivers/trusty/trusty.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `1492` bytes across `26` lines, with content hash prefix `23b86b101805` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `trusty_std_call32`, `dump_backtrace`, `show_stack`, `dump_stack`, `panic`, `__warn`; source-path cues include `drivers/trusty/trusty.c`, `kernel/lib/trusty/ipc.c`, `arch/arm64/kernel/traps.c`, `lib/dump_stack.c`, `kernel/panic.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `trusty: app-mgmt-test-srv2: 146: Channel wait failed: 0(4)`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `drivers/trusty/trusty.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: drivers/trusty/trusty.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/42 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/43 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/43

Purpose: This fixture validates Linux guilty-file extraction for a spinlock report. The expected `FILE` header is `net/netfilter/nf_conntrack_core.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `11678` bytes across `166` lines, with content hash prefix `ed60cd88f06b` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `nf_conntrack_locks`, `dump_stack`, `spin_dump`, `do_raw_spin_lock`, `_raw_spin_lock`, `nf_conntrack_lock`; source-path cues include `net/netfilter/nf_conntrack_core.c`, `lib/dump_stack.c`, `kernel/locking/spinlock_debug.c`, `include/linux/spinlock_api_smp.h`, `kernel/locking/spinlock.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `BUG: spinlock lockup suspected on CPU#1, kworker/u4:0/6`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/netfilter/nf_conntrack_core.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/netfilter/nf_conntrack_core.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/43 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/44 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/44

Purpose: This fixture validates Linux guilty-file extraction for a double-fault report. The expected `FILE` header is `arch/x86/kernel/traps.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `3119` bytes across `49` lines, with content hash prefix `15000fb33515` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `fixup_bad_iret`, `error_entry`, `native_irq_return_iret`; source-path cues include `arch/x86/kernel/traps.c`, `arch/x86/entry/entry_64.S`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `traps: PANIC: double fault, error_code: 0x0`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `arch/x86/kernel/traps.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: arch/x86/kernel/traps.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/44 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/45 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/45

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `drivers/input/misc/cm109.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `3011` bytes across `50` lines, with content hash prefix `131df27174ab` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `usb_submit_urb`, `cm109_submit_buzz_toggle`, `cm109_input_ev`, `input_handle_event`, `input_inject_event`, `kd_sound_helper`; source-path cues include `drivers/input/misc/cm109.c`, `drivers/usb/core/urb.c`, `drivers/input/input.c`, `drivers/tty/vt/keyboard.c`, `drivers/tty/vt/vt.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `------------[ cut here ]------------`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `drivers/input/misc/cm109.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: drivers/input/misc/cm109.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/45 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/46 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/46

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `drivers/input/misc/cm109.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `3026` bytes across `50` lines, with content hash prefix `707ff2dfb65b` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `usb_submit_urb`, `cm109_input_ev`, `input_handle_event`, `input_inject_event`, `kd_sound_helper`, `input_handler_for_each_handle`; source-path cues include `drivers/input/misc/cm109.c`, `drivers/usb/core/urb.c`, `drivers/input/input.c`, `drivers/tty/vt/keyboard.c`, `drivers/tty/vt/vt.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `------------[ cut here ]------------`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `drivers/input/misc/cm109.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: drivers/input/misc/cm109.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/46 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/47 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/47

Purpose: This fixture validates Linux guilty-file extraction for a leak detector report. The expected `FILE` header is `drivers/net/ieee802154/atusb.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `3519` bytes across `54` lines, with content hash prefix `aad3b9be5a20` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `usb_alloc_urb`, `atusb_probe`, `usb_probe_interface`, `really_probe`, `driver_probe_device`, `__device_attach_driver`; source-path cues include `drivers/net/ieee802154/atusb.c`, `include/linux/slab.h`, `drivers/usb/core/urb.c`, `drivers/usb/core/driver.c`, `drivers/base/dd.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `BUG: memory leak`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `drivers/net/ieee802154/atusb.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: drivers/net/ieee802154/atusb.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/47 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/48 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/48

Purpose: This fixture validates Linux guilty-file extraction for a leak detector report. The expected `FILE` header is `drivers/net/wireless/ath/ath9k/hif_usb.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `6467` bytes across `97` lines, with content hash prefix `27a17ca2720c` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `usb_alloc_urb`, `ath9k_hif_usb_alloc_urbs`, `ath9k_hif_usb_firmware_cb`, `request_firmware_work_func`, `process_one_work`, `worker_thread`; source-path cues include `drivers/net/wireless/ath/ath9k/hif_usb.c`, `include/linux/slab.h`, `drivers/usb/core/urb.c`, `drivers/base/firmware_loader/main.c`, `kernel/workqueue.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `BUG: memory leak`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `drivers/net/wireless/ath/ath9k/hif_usb.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: drivers/net/wireless/ath/ath9k/hif_usb.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/48 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/49 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/49

Purpose: This fixture validates Linux guilty-file extraction for a soft lockup report. The expected `FILE` header is `net/mac80211/sta_info.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `8256` bytes across `133` lines, with content hash prefix `3800a43c861f` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `asm_sysvec_irq_work`, `sysvec_apic_timer_interrupt`, `asm_call_irq_on_stack`, `__sanitizer_cov_trace_switch`, `jhash`, `__rhashtable_lookup`; source-path cues include `net/mac80211/sta_info.c`, `arch/x86/include/asm/idtentry.h`, `arch/x86/kernel/apic/apic.c`, `kernel/kcov.c`, `include/linux/jhash.h`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `watchdog: BUG: soft lockup - CPU#1 stuck for 134s! [syz-executor.3:16401]`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/mac80211/sta_info.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/mac80211/sta_info.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/49 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/5 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/5

Purpose: This fixture validates Linux guilty-file extraction for a KASAN memory-safety report. The expected `FILE` header is `fs/dcache.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `2724` bytes across `53` lines, with content hash prefix `349b28b738f9` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__d_lookup_rcu`, `lookup_fast`, `walk_component`, `path_lookupat`, `filename_lookup`, `kern_path`; source-path cues include `fs/dcache.c`, `include/linux/compiler.h`, `include/linux/seqlock.h`, `fs/namei.c`, `kernel/bpf/inode.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `kasan: GPF could be caused by NULL-ptr deref or user memory access`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `fs/dcache.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: fs/dcache.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/5 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/50 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/50

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `include/linux/spinlock.h`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `6736` bytes across `120` lines, with content hash prefix `3446d3c0e93f` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `deactivate_slab`, `__might_fault`, `rcu_core`, `show_stack`, `dump_stack`, `__lock_acquire`; source-path cues include `include/linux/spinlock.h`, `mm/slub.c`, `mm/memory.c`, `kernel/rcu/tree.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `=============================`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `include/linux/spinlock.h` after ignore-list filtering and deepest-path selection. Header summary: `FILE: include/linux/spinlock.h`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/50 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/51 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/51

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `fs/f2fs/recovery.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `7030` bytes across `145` lines, with content hash prefix `3d055e126cf0` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `kmem_cache_destroy`, `dump_backtrace`, `show_stack`, `dump_stack`, `print_address_description`, `kasan_report`; source-path cues include `fs/f2fs/recovery.c`, `mm/slab_common.c`, `arch/arm64/kernel/stacktrace.c`, `lib/dump_stack.c`, `mm/kasan/report.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `==================================================================`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `fs/f2fs/recovery.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: fs/f2fs/recovery.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/51 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/52 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/52

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `net/core/net_namespace.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `1962` bytes across `35` lines, with content hash prefix `08d382807dbc` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `cold`, `free_netdev`, `netdev_run_todo`, `default_device_exit_batch`, `ops_exit_list`, `cleanup_net`; source-path cues include `net/core/net_namespace.c`, `lib/ref_tracker.c`, `include/linux/spinlock.h`, `net/core/dev.c`, `kernel/workqueue.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `------------[ cut here ]------------`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/core/net_namespace.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/core/net_namespace.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/52 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/53 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/53

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `net/packet/af_packet.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `2780` bytes across `50` lines, with content hash prefix `8b1de0cd1cc2` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `cold`, `packet_release`, `__sock_release`, `sock_close`, `__fput`, `task_work_run`; source-path cues include `net/packet/af_packet.c`, `lib/ref_tracker.c`, `include/linux/spinlock.h`, `include/linux/netdevice.h`, `net/socket.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `------------[ cut here ]------------`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/packet/af_packet.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/packet/af_packet.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/53 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/54 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/54

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `fs/ntfs3/super.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `1870` bytes across `37` lines, with content hash prefix `92f4b4cf1784` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `writeback_single_inode`, `dump_stack_lvl`, `panic`, `__stack_chk_fail`, `write_inode_now`, `iput`; source-path cues include `fs/ntfs3/super.c`, `lib/dump_stack.c`, `kernel/panic.c`, `fs/fs-writeback.c`, `fs/inode.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `loop0: detected capacity change from 0 to 8226`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `fs/ntfs3/super.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: fs/ntfs3/super.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/54 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/55 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/55

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `fs/ntfs/super.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `4005` bytes across `82` lines, with content hash prefix `b89af7166ab3` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `evict`, `__lock_acquire`, `lock_acquire`, `_raw_spin_lock`, `iput`, `ntfs_fill_super`; source-path cues include `fs/ntfs/super.c`, `include/linux/spinlock.h`, `fs/inode.c`, `kernel/locking/lockdep.c`, `include/linux/spinlock_api_smp.h`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `loop4: detected capacity change from 0 to 264192`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `fs/ntfs/super.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: fs/ntfs/super.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/55 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/56 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/56

Purpose: This fixture validates Linux guilty-file extraction for a KASAN memory-safety report. The expected `FILE` header is `net/tipc/topsrv.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `3460` bytes across `61` lines, with content hash prefix `b5bca3833283` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `kernel_accept`, `tipc_topsrv_accept`, `process_one_work`, `worker_thread`, `kthread`, `ret_from_fork`; source-path cues include `net/tipc/topsrv.c`, `net/socket.c`, `kernel/workqueue.c`, `kernel/kthread.c`, `arch/x86/entry/entry_64.S`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `general protection fault, probably for non-canonical address 0xdffffc0000000001: 0000 [#1] PREEMPT SMP KASAN`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/tipc/topsrv.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/tipc/topsrv.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/56 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/57 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/57

Purpose: This fixture validates Linux guilty-file extraction for a leak detector report. The expected `FILE` header is `fs/jfs/jfs_metapage.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `1514` bytes across `27` lines, with content hash prefix `1105f20b4d08` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `mempool_alloc`, `__get_metapage`, `diNewExt`, `diAllocAG`, `diAlloc`, `ialloc`; source-path cues include `fs/jfs/jfs_metapage.c`, `mm/mempool.c`, `fs/jfs/jfs_imap.c`, `fs/jfs/jfs_inode.c`, `fs/jfs/namei.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `BUG: memory leak`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `fs/jfs/jfs_metapage.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: fs/jfs/jfs_metapage.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/57 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/58 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/58

Purpose: This fixture validates Linux guilty-file extraction for a RCU stall/lockdep report. The expected `FILE` header is `net/core/devlink.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `4600` bytes across `79` lines, with content hash prefix `d05e072fce07` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `sched_show_task`, `rcu_sched_clock_irq`, `update_process_times`, `tick_sched_handle`, `tick_sched_timer`, `__hrtimer_run_queues`; source-path cues include `net/core/devlink.c`, `kernel/sched/core.c`, `kernel/rcu/tree_stall.h`, `kernel/rcu/tree.c`, `kernel/time/timer.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/core/devlink.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/core/devlink.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/58 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/59 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/59

Purpose: This fixture validates Linux guilty-file extraction for a soft lockup report. The expected `FILE` header is `kernel/smp.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `3211` bytes across `56` lines, with content hash prefix `e836602706d2` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `exit_to_kernel_mode`, `el1_interrupt`, `_stext`, `____do_softirq`, `smp_call_function_many_cond`, `on_each_cpu_cond_mask`; source-path cues include `kernel/smp.c`, `arch/arm64/kernel/entry-common.c`, `arch/arm64/kernel/irq.c`, `arch/arm64/include/asm/cmpxchg.h`, `include/linux/smp.h`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `watchdog: BUG: soft lockup - CPU#1 stuck for 23s! [syz-executor.2:3705]`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `kernel/smp.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: kernel/smp.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/59 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/6 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/6

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `net/ipv6/tcp_ipv6.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `1546` bytes across `31` lines, with content hash prefix `ab554b2875be` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `tcp_v6_connect`, `dump_stack`, `print_address_description`, `kasan_report`, `__asan_report_load4_noabort`, `__inet_stream_connect`; source-path cues include `net/ipv6/tcp_ipv6.c`, `include/net/ip6_fib.h`, `lib/dump_stack.c`, `mm/kasan/report.c`, `net/ipv4/af_inet.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `==================================================================`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/ipv6/tcp_ipv6.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/ipv6/tcp_ipv6.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/6 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/60 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/60

Purpose: This fixture validates Linux guilty-file extraction for a RCU stall/lockdep report. The expected `FILE` header is `net/core/skmsg.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `4220` bytes across `81` lines, with content hash prefix `c650affa8a00` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__switch_to`, `__schedule`, `schedule`, `schedule_timeout`, `rcu_gp_fqs_loop`, `rcu_gp_kthread`; source-path cues include `net/core/skmsg.c`, `arch/arm64/kernel/process.c`, `kernel/sched/core.c`, `kernel/time/timer.c`, `kernel/rcu/tree.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `rcu: INFO: rcu_sched self-detected stall on CPU`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/core/skmsg.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/core/skmsg.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/60 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/61 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/61

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `<empty>`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `4272` bytes across `117` lines, with content hash prefix `f9ca06c858e5` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `ext4_evict_inode`, `ext4_ext_migrate`, `lock_acquire`, `percpu_down_write`, `ext4_ind_migrate`, `ext4_fileattr_set`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `======================================================`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `<empty>` after ignore-list filtering and deepest-path selection. Header summary: `FILE: `.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/61 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/62 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/62

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `fs/gfs2/lops.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `4065` bytes across `75` lines, with content hash prefix `abf36ff3f52e` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__switch_to`, `__schedule`, `schedule`, `io_schedule`, `folio_wait_bit_common`, `folio_wait_bit`; source-path cues include `fs/gfs2/lops.c`, `arch/arm64/kernel/process.c`, `kernel/sched/core.c`, `mm/filemap.c`, `include/linux/pagemap.h`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `INFO: task kworker/1:2:2221 blocked for more than 143 seconds.`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `fs/gfs2/lops.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: fs/gfs2/lops.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/62 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/63 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/63

Purpose: This fixture validates Linux guilty-file extraction for a RCU stall/lockdep report. The expected `FILE` header is `net/netfilter/x_tables.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `10255` bytes across `175` lines, with content hash prefix `fd4c709ea628` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__schedule`, `schedule`, `schedule_timeout`, `rcu_gp_fqs_loop`, `rcu_gp_kthread`, `kthread`; source-path cues include `net/netfilter/x_tables.c`, `kernel/sched/core.c`, `kernel/time/timer.c`, `kernel/rcu/tree.c`, `kernel/kthread.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `rcu: INFO: rcu_preempt self-detected stall on CPU`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/netfilter/x_tables.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/netfilter/x_tables.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/63 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/64 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/64

Purpose: This fixture validates Linux guilty-file extraction for a NULL pointer report. The expected `FILE` header is `fs/ntfs3/frecord.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `2949` bytes across `60` lines, with content hash prefix `84c3f637a0ba` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `unlock_page`, `ni_readpage_cmpr`, `ntfs_read_folio`, `filemap_read_folio`, `filemap_create_folio`, `filemap_get_pages`; source-path cues include `fs/ntfs3/frecord.c`, `include/linux/page-flags.h`, `mm/folio-compat.c`, `fs/ntfs3/inode.c`, `mm/filemap.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `Unable to handle kernel NULL pointer dereference at virtual address 0000000000000008`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `fs/ntfs3/frecord.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: fs/ntfs3/frecord.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/64 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/65 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/65

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `net/ipv4/ip_tunnel.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `48847` bytes across `644` lines, with content hash prefix `df1662b6685d` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `should_fail_ex`, `should_fail_alloc_page`, `kernel_clone`, `__alloc_pages`, `__kmalloc_large_node`, `__kmalloc_node_track_caller`; source-path cues include `net/ipv4/ip_tunnel.c`, `lib/fault-inject.c`, `mm/page_alloc.c`, `kernel/fork.c`, `include/linux/gfp.h`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `Insufficient stack space to handle exception!`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/ipv4/ip_tunnel.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/ipv4/ip_tunnel.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/65 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/66 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/66

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `net/mac80211/wep.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `5805` bytes across `101` lines, with content hash prefix `9ffac39713b5` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `crc32_lsb_pclmul_sse`, `crc32_le_arch`, `ieee80211_wep_encrypt`, `ieee80211_crypto_wep_encrypt`, `invoke_tx_handlers_late`, `ieee80211_tx_dequeue`; source-path cues include `net/mac80211/wep.c`, `arch/x86/lib/crc32-pclmul.S`, `arch/x86/lib/crc32.c`, `include/linux/crc32.h`, `net/mac80211/tx.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `BUG: unable to handle page fault for address: ffff8880bfffd000`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/mac80211/wep.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/mac80211/wep.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/66 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/7 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/7

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `net/packet/af_packet.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `2228` bytes across `38` lines, with content hash prefix `46c32a6bf0b9` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `skb_warn_bad_offload`, `dump_stack`, `panic`, `warn_slowpath_common`, `warn_slowpath_fmt`, `__skb_gso_segment`; source-path cues include `net/packet/af_packet.c`, `net/core/dev.c`, `lib/dump_stack.c`, `kernel/panic.c`, `include/linux/netdevice.h`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `------------[ cut here ]------------`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/packet/af_packet.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/packet/af_packet.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/7 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/8 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/8

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `net/ipv4/tcp_ipv4.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `2518` bytes across `49` lines, with content hash prefix `088a15d3510b` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `tcp_v4_early_demux`, `dump_stack`, `print_address_description`, `kasan_report`, `__asan_report_load8_noabort`, `ip_rcv_finish`; source-path cues include `net/ipv4/tcp_ipv4.c`, `include/net/dst.h`, `lib/dump_stack.c`, `mm/kasan/report.c`, `net/ipv4/ip_input.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `==================================================================`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/ipv4/tcp_ipv4.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/ipv4/tcp_ipv4.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/8 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/9 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/9

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `net/core/rtnetlink.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `1417` bytes across `30` lines, with content hash prefix `9d1792c19556` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `rtnl_fdb_dump`, `dump_stack`, `kmsan_report`, `__kmsan_warning_32`, `netlink_dump`, `__netlink_dump_start`; source-path cues include `net/core/rtnetlink.c`, `lib/dump_stack.c`, `mm/kmsan/kmsan.c`, `mm/kmsan/kmsan_instr.c`, `net/netlink/af_netlink.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `==================================================================`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/core/rtnetlink.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/core/rtnetlink.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/9 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty_raw/0 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty_raw/0

Purpose: This fixture validates `ReportToGuiltyFile` on an already prepared report title/body pair. The expected raw guilty target is `fs/kernfs/dir.c` for title `WARNING in kernfs_get (4)`. The source is `3932` bytes across `67` lines, with content hash prefix `2b00d2381246` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `kernfs_create_dir_ns`, `sysfs_create_dir_ns`, `kobject_add_internal`, `kobject_init_and_add`, `net_rx_queue_update_kobjects`, `netdev_register_kobject`; source-path cues include `fs/kernfs/dir.c`, `fs/sysfs/dir.c`, `lib/kobject.c`, `net/core/net-sysfs.c`, `net/core/dev.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `raw guilty-file fixture`, the key body signal begins with: `------------[ cut here ]------------`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `fs/kernfs/dir.c` after ignore-list filtering and deepest-path selection. Header summary: `TITLE: WARNING in kernfs_get (4); FILE: fs/kernfs/dir.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty_raw/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/0 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/0

Purpose: This fixture drives `TestParse` for a fault report and locks in the normalized title `BUG: unable to handle kernel paging request in corrupted` plus type `MEMORY_SAFETY_BUG`. It is a parser-regression input, not executable kernel code. The source is `911` bytes across `19` lines, with content hash prefix `bcd917c7dc2b` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__memset`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `BUG: unable to handle kernel paging request at ffff88002bde1e40`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: unable to handle kernel paging request in corrupted; ALT: bad-access in corrupted; TYPE: MEMORY_SAFETY_BUG; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, `ALT=bad-access in corrupted`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/1 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/1

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `<empty>` plus type `<default>`. It is a parser-regression input, not executable kernel code. The source is `67` bytes across `3` lines, with content hash prefix `c8aa3b9f7569` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include no stable stack function was exposed; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `BUG UNIX (Not tainted): kasan: bad access detected`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `no explicit metadata headers before the blank separator`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are no special flags, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/1 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/10 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/10

Purpose: This fixture drives `TestParse` for a fault report and locks in the normalized title `BUG: unable to handle kernel paging request in __call_rcu` plus type `MEMORY_SAFETY_BUG`. It is a parser-regression input, not executable kernel code. The source is `310` bytes across `8` lines, with content hash prefix `7a0fd3c2ceb9` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__call_rcu`; source-path cues include `kernel/rcu/tree.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `BUG: unable to handle kernel paging request at 00000000ffffff8a`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: unable to handle kernel paging request in __call_rcu; ALT: bad-access in __call_rcu; TYPE: MEMORY_SAFETY_BUG; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, `ALT=bad-access in __call_rcu`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/10 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/100 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/100

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `general protection fault in corrupted` plus type `DoS`. It is a parser-regression input, not executable kernel code. The source is `401` bytes across `11` lines, with content hash prefix `4e9caa13708e` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include no stable stack function was exposed; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `kasan: CONFIG_KASAN_INLINE enabled`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: general protection fault in corrupted; ALT: bad-access in corrupted; TYPE: DoS; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, `ALT=bad-access in corrupted`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/100 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/1000 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/1000

Purpose: This fixture drives `TestParse` for a hung task report and locks in the normalized title `INFO: task hung in read_cache_folio` plus type `HANG`. It is a parser-regression input, not executable kernel code. The source is `1917` bytes across `39` lines, with content hash prefix `9d534e0480db` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__switch_to`, `__schedule`, `schedule`, `io_schedule`, `folio_wait_bit_common`, `do_read_cache_folio`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `[   T31] INFO: t`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: INFO: task hung in read_cache_folio; ALT: hang in read_cache_folio; TYPE: HANG; FRAME: read_cache_folio`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `ALT=hang in read_cache_folio`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/1000 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/1001 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/1001

Purpose: This fixture drives `TestParse` for a hung task report and locks in the normalized title `INFO: task hung in p9_fd_close` plus type `HANG`. It is a parser-regression input, not executable kernel code. The source is `3757` bytes across `69` lines, with content hash prefix `4eadef6d3c23` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__schedule`, `__pfx___schedule`, `find_held_lock`, `schedule`, `schedule_timeout`, `__pfx_schedule_timeout`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `[   T41] INFO: task ����`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: INFO: task hung in p9_fd_close; ALT: hang in p9_fd_close; TYPE: HANG; FRAME: p9_fd_close`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `ALT=hang in p9_fd_close`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/1001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/101 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/101

Purpose: This fixture drives `TestParse` for a Linux crash report report and locks in the normalized title `BUG: unable to handle kernel` plus type `<default>`. It is a parser-regression input, not executable kernel code. The source is `545` bytes across `13` lines, with content hash prefix `5cc66cfa6c46` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include no stable stack function was exposed; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `device lo entered promiscuous mode`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: unable to handle kernel; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/101 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/102 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/102

Purpose: This fixture drives `TestParse` for a lockdep unlock-balance report and locks in the normalized title `BUG: bad unlock balance in corrupted` plus type `LOCKDEP`. It is a parser-regression input, not executable kernel code. The source is `274` bytes across `10` lines, with content hash prefix `89b8e9f418e9` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include no stable stack function was exposed; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `syz2: link speed 10 Mbps`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: bad unlock balance in corrupted; TYPE: LOCKDEP; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/102 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/103 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/103

Purpose: This fixture drives `TestParse` for a divide error report and locks in the normalized title `divide error in corrupted` plus type `DoS`. It is a parser-regression input, not executable kernel code. The source is `200` bytes across `7` lines, with content hash prefix `947282f09507` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include no stable stack function was exposed; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `netlink: 13 bytes leftover after parsing attributes in process syz-executor5'.`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: divide error in corrupted; TYPE: DoS; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/103 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/104 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/104

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `KASAN: slab-out-of-bounds in gup_huge_pmd at addr ADDR` plus type `KASAN-READ`. It is a parser-regression input, not executable kernel code. The source is `274` bytes across `7` lines, with content hash prefix `87f98986a7b9` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `gup_huge_pmd`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `==================================================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: KASAN: slab-out-of-bounds in gup_huge_pmd at addr ADDR; TYPE: KASAN-READ; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/104 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/105 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/105

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `KASAN: slab-out-of-bounds Read in ip6_fragment` plus type `KASAN-READ`. It is a parser-regression input, not executable kernel code. The source is `4267` bytes across `84` lines, with content hash prefix `f71b028fbfa0` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `ip6_fragment`, `dump_stack`, `print_address_description`, `kasan_report`, `check_memory_region`, `memcpy`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `==================================================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: KASAN: slab-out-of-bounds Read in ip6_fragment; ALT: bad-access in ip6_fragment; TYPE: KASAN-READ`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `ALT=bad-access in ip6_fragment`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/105 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/106 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/106

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `KASAN: use-after-free Read in consume_skb` plus type `KASAN-USE-AFTER-FREE-READ`. It is a parser-regression input, not executable kernel code. The source is `593` bytes across `15` lines, with content hash prefix `1d1179c55eab` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `consume_skb`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `==================================================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: KASAN: use-after-free Read in consume_skb; ALT: bad-access in consume_skb; TYPE: KASAN-USE-AFTER-FREE-READ; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, `ALT=bad-access in consume_skb`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/106 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/107 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/107

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `KASAN: slab-out-of-bounds in do_raw_write_lock at addr ADDR` plus type `KASAN-READ`. It is a parser-regression input, not executable kernel code. The source is `978` bytes across `16` lines, with content hash prefix `7cbfbcaaf379` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `dump_stack`, `do_raw_write_lock`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `FAULT_FLAG_ALLOW_RETRY missing 30`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: KASAN: slab-out-of-bounds in do_raw_write_lock at addr ADDR; TYPE: KASAN-READ; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/107 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/109 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/109

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `KASAN: stack-out-of-bounds Read in xfrm_state_find` plus type `KASAN-READ`. It is a parser-regression input, not executable kernel code. The source is `2470` bytes across `42` lines, with content hash prefix `0dc72e1e5a0e` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `xfrm_state_find`, `dump_stack`, `print_address_description`, `kasan_report`, `__asan_report_load4_noabort`, `entry_SYSENTER_compat`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `==================================================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: KASAN: stack-out-of-bounds Read in xfrm_state_find; ALT: bad-access in xfrm_state_find; TYPE: KASAN-READ`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `ALT=bad-access in xfrm_state_find`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/109 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/11 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/11

Purpose: This fixture drives `TestParse` for a fault report and locks in the normalized title `BUG: unable to handle kernel paging request in corrupted` plus type `MEMORY_SAFETY_BUG`. It is a parser-regression input, not executable kernel code. The source is `269` bytes across `8` lines, with content hash prefix `90f7198d5eb6` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include no stable stack function was exposed; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `BUG: unable to handle kernel paging request at ffffea0000f0e440`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: unable to handle kernel paging request in corrupted; ALT: bad-access in corrupted; TYPE: MEMORY_SAFETY_BUG; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, `ALT=bad-access in corrupted`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/11 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/110 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/110

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `KASAN: slab-out-of-bounds Read in sg_remove_request` plus type `KASAN-READ`. It is a parser-regression input, not executable kernel code. The source is `3246` bytes across `58` lines, with content hash prefix `f84757e4715b` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__lock_acquire`, `dump_stack`, `kasan_object_err`, `__asan_report_load8_noabort`, `lock_acquire`, `_raw_write_lock_irqsave`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `==================================================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: KASAN: slab-out-of-bounds Read in sg_remove_request; ALT: bad-access in sg_remove_request; TYPE: KASAN-READ`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `ALT=bad-access in sg_remove_request`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/110 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/111 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/111

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `KASAN: slab-out-of-bounds Read in sg_remove_request` plus type `KASAN-READ`. It is a parser-regression input, not executable kernel code. The source is `2386` bytes across `40` lines, with content hash prefix `cb03ffde23fc` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `sg_remove_request`, `dump_stack`, `kasan_object_err`, `__asan_report_load8_noabort`, `sg_finish_rem_req`, `sg_read`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `==================================================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: KASAN: slab-out-of-bounds Read in sg_remove_request; ALT: bad-access in sg_remove_request; TYPE: KASAN-READ`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `ALT=bad-access in sg_remove_request`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/111 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/112 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/112

Purpose: This fixture drives `TestParse` for a NULL pointer report and locks in the normalized title `BUG: unable to handle kernel NULL pointer dereference in process_one_work` plus type `NULL-POINTER-DEREFERENCE`. It is a parser-regression input, not executable kernel code. The source is `2181` bytes across `45` lines, with content hash prefix `3e2786847427` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `process_one_work`, `worker_thread`, `kthread`, `ret_from_fork`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `BUG: unable to handle kernel NULL pointer dereference at 0000000000000286`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: unable to handle kernel NULL pointer dereference in process_one_work; ALT: bad-access in process_one_work; TYPE: NULL-POINTER-DEREFERENCE; PANICKED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `PANICKED=Y`, `ALT=bad-access in process_one_work`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, panic detection is part of the expected result, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/112 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/113 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/113

Purpose: This fixture drives `TestParse` for a BUG report and locks in the normalized title `kernel BUG in esp6_gro_receive` plus type `BUG`. It is a parser-regression input, not executable kernel code. The source is `4294` bytes across `62` lines, with content hash prefix `b77538480118` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `skb_pull`, `esp6_gro_receive`, `SyS_writev`, `entry_SYSCALL_64_fastpath`, `max_burst`; source-path cues include `include/linux/skbuff.h`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `------------[ cut here ]------------`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: kernel BUG in esp6_gro_receive; TYPE: BUG`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are no special flags, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/113 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/114 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/114

Purpose: This fixture drives `TestParse` for a RCU stall/lockdep report and locks in the normalized title `WARNING: suspicious RCU usage` plus type `WARNING`. It is a parser-regression input, not executable kernel code. The source is `2703` bytes across `46` lines, with content hash prefix `773cea2d2991` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `kfree`, `blkcipher_walk_done`, `encrypt`, `SyS_recvmsg`, `entry_SYSCALL_64_fastpath`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `=============================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: WARNING: suspicious RCU usage; TYPE: WARNING; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/114 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/115 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/115

Purpose: This fixture drives `TestParse` for a lockdep unlock-balance report and locks in the normalized title `BUG: bad unlock balance in corrupted` plus type `LOCKDEP`. It is a parser-regression input, not executable kernel code. The source is `2260` bytes across `40` lines, with content hash prefix `02664eea9b3a` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `dump_stack`, `entry_SYSCALL_64_fastpath`, `ipmr_mfc_seq_stop`, `__fdget_pos`, `seq_read`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `binder: undelivered TRANSACTION_ERROR: 29189`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: bad unlock balance in corrupted; TYPE: LOCKDEP; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/115 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/116 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/116

Purpose: This fixture drives `TestParse` for a lockdep unlock-balance report and locks in the normalized title `BUG: bad unlock balance in ipmr_mfc_seq_stop` plus type `LOCKDEP`. It is a parser-regression input, not executable kernel code. The source is `1330` bytes across `26` lines, with content hash prefix `af479cd29127` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `ipmr_mfc_seq_stop`, `seq_read`, `dump_stack`, `entry_SYSCALL_64_fastpath`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `=====================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: bad unlock balance in ipmr_mfc_seq_stop; TYPE: LOCKDEP`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are no special flags, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/116 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/117 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/117

Purpose: This fixture drives `TestParse` for a lockdep unlock-balance report and locks in the normalized title `WARNING: bad unlock balance in ipmr_mfc_seq_stop` plus type `LOCKDEP`. It is a parser-regression input, not executable kernel code. The source is `2044` bytes across `44` lines, with content hash prefix `7394c97f0eda` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `ipmr_mfc_seq_stop`, `__fdget_pos`, `seq_lseek`, `dump_stack`, `arch_local_irq_restore`, `print_unlock_imbalance_bug`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `=====================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: WARNING: bad unlock balance in ipmr_mfc_seq_stop; TYPE: LOCKDEP`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are no special flags, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/117 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/118 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/118

Purpose: This fixture drives `TestParse` for a lockdep key report and locks in the normalized title `INFO: trying to register non-static key in tcp_fastopen_reset_cipher` plus type `<default>`. It is a parser-regression input, not executable kernel code. The source is `1731` bytes across `31` lines, with content hash prefix `5ed57543371b` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `dump_stack`, `arch_local_irq_restore`, `register_lock_class`, `__lock_acquire`, `find_held_lock`, `rcu_pm_notify`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `syzkaller login: [   16.305150] INFO: trying to register non-static key.`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: INFO: trying to register non-static key in tcp_fastopen_reset_cipher`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are no special flags, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/118 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/119 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/119

Purpose: This fixture drives `TestParse` for a lockdep key report and locks in the normalized title `INFO: trying to register non-static key in tun_flow_cleanup` plus type `<default>`. It is a parser-regression input, not executable kernel code. The source is `818` bytes across `17` lines, with content hash prefix `6e7e7da57f2c` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `dump_stack`, `register_lock_class`, `__lock_acquire`, `lock_acquire`, `_raw_spin_lock_bh`, `tun_flow_cleanup`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `==================================================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: INFO: trying to register non-static key in tun_flow_cleanup`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are no special flags, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/119 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/12 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/12

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `general protection fault in drm_legacy_newctx` plus type `DoS`. It is a parser-regression input, not executable kernel code. The source is `1320` bytes across `23` lines, with content hash prefix `3e5150456105` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `drm_legacy_newctx`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `kasan: CONFIG_KASAN_INLINE enabled`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: general protection fault in drm_legacy_newctx; ALT: bad-access in drm_legacy_newctx; TYPE: DoS; START: [ 1021.364461] general protection fault: 0000 [#1] SMP DEBUG_PAGEALLOC KASAN; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, `START=[ 1021.364461] general protection fault: 0000 [#1] SMP DEBUG_PAGEALLOC KASAN`, `ALT=bad-access in drm_legacy_newctx`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/12 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/120 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/120

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `KASAN: slab-out-of-bounds Write in __unwind_start` plus type `KASAN-WRITE`. It is a parser-regression input, not executable kernel code. The source is `2894` bytes across `53` lines, with content hash prefix `b134bc7b3d80` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__unwind_start`, `print_usage_bug`, `__lock_acquire`, `kthread`, `loop_get_status64`, `kthread_stop`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `==================================================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: KASAN: slab-out-of-bounds Write in __unwind_start; ALT: bad-access in __unwind_start; TYPE: KASAN-WRITE; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, `ALT=bad-access in __unwind_start`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/120 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/121 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/121

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `KASAN: use-after-free Write in __unwind_start` plus type `KASAN-USE-AFTER-FREE-WRITE`. It is a parser-regression input, not executable kernel code. The source is `2274` bytes across `43` lines, with content hash prefix `66f896277865` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__unwind_start`, `kthread`, `loop_get_status64`, `kthread_stop`, `ret_from_fork`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `==================================================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: KASAN: use-after-free Write in __unwind_start; ALT: bad-access in __unwind_start; TYPE: KASAN-USE-AFTER-FREE-WRITE; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, `ALT=bad-access in __unwind_start`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/121 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/122 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/122

Purpose: This fixture drives `TestParse` for a usercopy hardening report and locks in the normalized title `BUG: bad usercopy in kvm_vcpu_ioctl_set_cpuid2` plus type `BUG`. It is a parser-regression input, not executable kernel code. The source is `3354` bytes across `56` lines, with content hash prefix `f46914a7c7f6` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__check_object_size`, `lock_release`, `check_stack_object`, `check_noncircular`, `__might_sleep`, `kvm_vcpu_ioctl_set_cpuid2`; source-path cues include `mm/usercopy.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `usercopy: kernel memory overwrite attempt detected to ffff8801d21c9bd4 (kvm_vcpu) (1320 bytes)`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: bad usercopy in kvm_vcpu_ioctl_set_cpuid2; TYPE: BUG; PANICKED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `PANICKED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, panic detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/122 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/123 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/123

Purpose: This fixture drives `TestParse` for a RCU stall/lockdep report and locks in the normalized title `INFO: Freed in fasync_free_rcu age=NUM cpu=NUM pid=NUM` plus type `<default>`. It is a parser-regression input, not executable kernel code. The source is `4203` bytes across `43` lines, with content hash prefix `60ead3b724b7` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `sg_finish_rem_req`, `entry_SYSCALL_64_fastpath`, `fasync_free_rcu`, `__slab_free`, `kmem_cache_alloc`, `security_file_permission`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `==================================================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: INFO: Freed in fasync_free_rcu age=NUM cpu=NUM pid=NUM; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/123 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/124 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/124

Purpose: This fixture drives `TestParse` for a Linux crash report report and locks in the normalized title `INFO: Allocated in fasync_helper age=NUM cpu=NUM pid=NUM` plus type `<default>`. It is a parser-regression input, not executable kernel code. The source is `3014` bytes across `35` lines, with content hash prefix `f944fbeb226f` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `fasync_helper`, `native_queued_spin_lock_slowpath`, `SyS_fcntl`, `rw_verify_area`, `run_ksoftirqd`, `print_trailer`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `** 4491 printk messages dropped ** [   50.750742] INFO: Allocated in fasync_helper+0x29/0x90 age=1 cpu=1 pid=6024`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: INFO: Allocated in fasync_helper age=NUM cpu=NUM pid=NUM; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/124 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/125 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/125

Purpose: This fixture drives `TestParse` for a usercopy hardening report and locks in the normalized title `BUG: bad usercopy in sctp_getsockopt` plus type `BUG`. It is a parser-regression input, not executable kernel code. The source is `3266` bytes across `54` lines, with content hash prefix `94324c4a106c` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__check_object_size`, `lock_release`, `check_stack_object`, `__local_bh_enable_ip`, `__might_sleep`, `sctp_getsockopt`; source-path cues include `mm/usercopy.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `syzkaller login: [   55.288565] usercopy: kernel memory exposure attempt detected from ffff8801d4310630 (SCTPv6) (11 bytes)`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: bad usercopy in sctp_getsockopt; TYPE: BUG; PANICKED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `PANICKED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, panic detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/125 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/126 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/126

Purpose: This fixture drives `TestParse` for a leak detector report and locks in the normalized title `memory leak in corrupted` plus type `LEAK`. It is a parser-regression input, not executable kernel code. The source is `127` bytes across `9` lines, with content hash prefix `bf99ac43041e` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include no stable stack function was exposed; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `2018/01/09 14:28:48 BUG: memory leak`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: memory leak in corrupted; TYPE: LEAK; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/126 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/127 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/127

Purpose: This fixture drives `TestParse` for a reboot report and locks in the normalized title `unexpected kernel reboot` plus type `REBOOT`. It is a parser-regression input, not executable kernel code. The source is `2032` bytes across `38` lines, with content hash prefix `28a9b4548df2` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `extract_kernel`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `tkill(r8, 0x13)`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: unexpected kernel reboot; TYPE: REBOOT`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are no special flags, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/127 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/129 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/129

Purpose: This fixture drives `TestParse` for a Linux crash report report and locks in the normalized title `INFO: corrupted` plus type `<default>`. It is a parser-regression input, not executable kernel code. The source is `43` bytes across `5` lines, with content hash prefix `7c9d82e3b0a4` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include no stable stack function was exposed; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `INFO:`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: INFO: corrupted; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/129 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/13 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/13

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `general protection fault in logfs_init_inode` plus type `DoS`. It is a parser-regression input, not executable kernel code. The source is `797` bytes across `16` lines, with content hash prefix `d7df5c8c97e1` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `logfs_init_inode`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `kasan: GPF could be caused by NULL-ptr deref or user memory access`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: general protection fault in logfs_init_inode; ALT: bad-access in logfs_init_inode; TYPE: DoS; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, `ALT=bad-access in logfs_init_inode`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/13 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/130 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/130

Purpose: This fixture drives `TestParse` for a KASAN memory-safety report and locks in the normalized title `KASAN: use-after-free Read in aead_recvmsg` plus type `KASAN-USE-AFTER-FREE-READ`. It is a parser-regression input, not executable kernel code. The source is `7513` bytes across `126` lines, with content hash prefix `13975c13cc48` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `aead_recvmsg`, `dump_stack`, `arch_local_irq_restore`, `show_regs_print_info`, `af_alg_make_sg`, `print_address_description`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `2017/11/27 07:13:57 executing program 2:`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: KASAN: use-after-free Read in aead_recvmsg; ALT: bad-access in aead_recvmsg; TYPE: KASAN-USE-AFTER-FREE-READ; START: [   53.730124] BUG: KASAN: use-after-free in aead_recvmsg+0x1758/0x1bc0`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `START=[   53.730124] BUG: KASAN: use-after-free in aead_recvmsg+0x1758/0x1bc0`, `ALT=bad-access in aead_recvmsg`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/130 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/131 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/131

Purpose: This fixture drives `TestParse` for a LOCKDEP report and locks in the normalized title `BUG: using __this_cpu_read() in preemptible code in ipcomp_init_state` plus type `LOCKDEP`. It is a parser-regression input, not executable kernel code. The source is `3194` bytes across `50` lines, with content hash prefix `7586f80d0409` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__this_cpu_preempt_check`, `dump_stack`, `check_preemption_disabled`, `ipcomp_init_state`, `__lock_is_held`, `ipcomp4_init_state`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `syzkaller login: [   35.184476] BUG: using __this_cpu_read() in preemptible [00000000] code: syzkaller195313/3344`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: using __this_cpu_read() in preemptible code in ipcomp_init_state; TYPE: LOCKDEP`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are no special flags, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/131 -->
