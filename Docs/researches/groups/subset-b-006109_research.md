# subset-b-006109 research

Grouped research for Linux kernel test modules under `sources/distributed-fs/ceph-client/lib/`. Each section preserves the original source path for deterministic split into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_context-analysis.c -->
# sources/distributed-fs/ceph-client/lib/test_context-analysis.c

## Purpose

This is a compile-only coverage file for Clang/kernel context analysis annotations. It intentionally defines many small `__used` functions that exercise lock, guard, RCU, SRCU, local lock, ww_mutex, per-CPU, and seqlock patterns that should not produce false positive guarded-by or must-hold diagnostics.

## Important APIs, Types, And Functions

The file uses `context_unsafe()`, `__guarded_by`, `__pt_guarded_by`, `__rcu_guarded`, `__must_hold_shared`, `guard()`, `scoped_cond_guard()`, lockdep assertions, and many kernel lock families. `TEST_SPINLOCK_COMMON()` generates data types and functions for raw spinlocks, spinlocks, write locks, and read locks. Handwritten sections cover mutexes, seqlocks, rwsems, bit spinlocks, RCU/SRCU, local locks, local trylocks, ww_mutexes, and per-CPU spinlocks.

## Control Flow And State

There is no module init path and no runtime test runner. The state is local to synthetic data structs or per-CPU test instances, and the important behavior is whether the compiler accepts guarded accesses after the recognized locking primitive or assertion. The flow is a sequence of independent compile targets: initialize a lock, take it through normal/IRQ/BH/irqsave/try/scoped variants, access guarded fields, and release the lock.

## Dependencies And Integration Points

It depends on the kernel's sparse/Clang context analysis annotations and helper macros from locking, percpu, RCU, SRCU, rwsem, seqlock, local_lock, bit_spinlock, and ww_mutex headers. It integrates through the kernel build as a compile target rather than as a loaded module.

## Risks And Test Signals

The main risk is analysis drift: adding or renaming lock helpers can make valid code warn, while overly broad annotations can hide real unsafe access. Useful signals are clean compile results with the configured Clang analysis, warnings that point to guarded members in these synthetic functions, and coverage of generated guard helpers such as `guard(raw_spinlock_irqsave)`, `scoped_cond_guard(mutex_try)`, and `srcu_dereference()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_context-analysis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_debug_virtual.c -->
# sources/distributed-fs/ceph-client/lib/test_debug_virtual.c

## Purpose

This small module probes `CONFIG_DEBUG_VIRTUAL` behavior by deliberately calling `virt_to_phys()` on representative virtual addresses and printing the resulting physical address. It first uses `VMALLOC_START`, then a dynamically allocated `struct foo`.

## Important APIs, Types, And Functions

The key state is `static struct foo *foo`. `test_debug_virtual_init()` computes and logs physical addresses using `virt_to_phys()`, allocates `foo` with `kzalloc_obj()`, and returns `-ENOMEM` on allocation failure. `test_debug_virtual_exit()` frees the allocation.

## Control Flow And State

On module load, the test performs two conversions and logs both. Only the heap allocation persists until module unload. The module has no sysfs/debugfs interface and no recurring work.

## Dependencies And Integration Points

It includes memory, vmalloc, slab, I/O, page, and module headers. The test is meaningful on architectures that implement `CONFIG_DEBUG_VIRTUAL` checks for invalid virtual-to-physical conversions; MIPS has an additional bootinfo include.

## Risks And Test Signals

The test intentionally touches a suspicious conversion path, so useful signals are WARN splats or diagnostic output from debug virtual checks and the two `pr_info()` address lines. The only cleanup risk is leaked `foo` if init failed after allocation, which does not happen in this straight-line code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_debug_virtual.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_dynamic_debug.c -->
# sources/distributed-fs/ceph-client/lib/test_dynamic_debug.c

## Purpose

This module exercises dynamic debug class maps and class-parameter plumbing. Loading the module or reading/writing the `do_prints` module parameter triggers a predictable set of `pr_debug()` and `__pr_debug_cls()` calls.

## Important APIs, Types, And Functions

`DD_SYS_WRAP()` creates dynamic debug class parameters backed by `struct ddebug_class_param` and `param_ops_dyndbg_classes`. Four class maps are declared: disjoint numeric bits, disjoint symbolic names, numeric verbosity levels, and symbolic verbosity levels. `do_cats()` emits category-class messages, `do_levels()` emits level-class messages, and `do_prints()` runs both.

## Control Flow And State

The module stores class-enable state in per-map `bits_*` variables exposed through module parameters such as `p_disjoint_bits`, `T_disjoint_bits`, `p_level_names`, and `T_level_names`. Init logs debug messages and calls `do_prints()`. Parameter get/set callbacks call `do_prints()` again and either return a fixed status string or accept the write.

## Dependencies And Integration Points

The file integrates with the dynamic debug subsystem through `DECLARE_DYNDBG_CLASSMAP`, `__pr_debug_cls`, and the class parameter ops. Userspace drives it through module parameters under sysfs and dynamic debug control files.

## Risks And Test Signals

Class id bases must match the enum values and stay within the shared 0-30 class id space. Test signals are whether dynamic debug queries can enable exactly the expected category or verbosity messages and whether parameter reads/writes trigger the same print stream without module reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_dynamic_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_firmware.c -->
# sources/distributed-fs/ceph-client/lib/test_firmware.c

## Purpose

This module exposes a misc device named `test_firmware` with sysfs attributes for exercising the firmware loader, fallback paths, batched synchronous/asynchronous requests, platform firmware lookup, and firmware upload support. It is a test harness for firmware APIs, not a production loader.

## Important APIs, Types, And Functions

The central state is `struct test_config`, protected by `test_fw_mutex`, containing firmware name, request mode, buffer sizing, partial-read settings, uevent behavior, batched request array, selected upload name, and `test_result`. `struct test_batched_req` tracks individual request completions, loaded firmware pointers, backing buffers, kthreads, and return codes. `struct test_firmware_upload` tracks registered upload endpoints, data buffers, cancel state, and injected upload errors.

The sysfs surface includes configuration attributes (`config_name`, `config_num_requests`, `config_into_buf`, `config_buf_size`, `config_file_offset`, `config_partial`, `config_sync_direct`, `config_send_uevent`, `config_read_fw_idx`, `config_upload_name`) and triggers (`trigger_request`, `trigger_async_request`, `trigger_custom_fallback`, optional `trigger_request_platform`, `trigger_batched_requests`, `trigger_batched_requests_async`, `release_all_firmware`, `read_firmware`, `upload_register`, `upload_unregister`, `upload_read`, `test_result`). The misc read path returns the currently loaded `test_firmware` data.

## Control Flow And State

Init allocates `test_fw_config`, initializes defaults (`test-firmware.bin`, four requests, 1 KiB buffer, uevents enabled), and registers the misc device with attribute groups. Synchronous triggers release stale firmware, request a named firmware object, and store it in `test_firmware`. Async triggers use `request_firmware_nowait()`, wait on `async_fw_done`, and rely on `trigger_async_request_cb()` to publish the firmware pointer.

Batched sync requests allocate a request array, launch one kthread per request, then wait for completions while leaving firmware objects retained until explicit release. Batched async requests submit multiple `request_firmware_nowait()` calls, use completions from callbacks, and preserve results for later `read_firmware`. Upload registration creates firmware upload endpoints using `firmware_upload_register()` and `upload_test_ops`; writes are copied in 37-byte chunks and may inject failures at preparing, transferring, or programming stages.

## Dependencies And Integration Points

The module depends on firmware loader APIs (`request_firmware*`, `release_firmware`, `firmware_upload_register`), miscdevice/sysfs infrastructure, kthreads, completions, vmalloc, uaccess helpers, optional EFI embedded firmware state, and the `TEST_FIRMWARE` namespace. Userspace selftests usually drive the sysfs attributes and read the misc device.

## Risks And Test Signals

This file intentionally tests races and lifetime boundaries, including freeing the firmware name immediately after async submission. Risks include stale global completion state, retained firmware objects when `release_all_firmware` is not called, config changes while batched requests exist, and keeping `fw_upload_err_str` synchronized with firmware upload internals. Signals include sysfs return codes, `test_result`, misc-device read data, `read_firmware` contents, upload data returned by `upload_read`, and kernel logs for loaded sizes and injected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/Makefile -->
# sources/distributed-fs/ceph-client/lib/test_fortify/Makefile

## Purpose

This kbuild fragment builds every `*-*.c` fortify test source as a compile-time negative test and aggregates the logs into `test_fortify.log`.

## Important APIs, Types, And Functions

`cmd_test_fortify` invokes `test_fortify.sh` with the input source, output log, `nm`, compiler, normal C flags, and extra warning settings. Pattern rule `$(obj)/%.log` creates one log per test source. `cmd_gen_fortify_log` concatenates all per-test logs into a single summary log.

## Control Flow And State

The build disables the normal `fortify-source` warning suppression for this directory, builds test objects with `-Werror`, writes logs beside build outputs, and always builds the aggregate log. No runtime state exists.

## Dependencies And Integration Points

It depends on kbuild command tracking, `$(CONFIG_SHELL)`, `$(NM)`, `$(CC)`, the shared shell script, and the common header. It also sets `KASAN_SANITIZE := y` because some architecture configurations interact with `__NO_FORTIFY` and sanitizer flags.

## Risks And Test Signals

The rules rely on filenames encoding expected fortify warning symbols. Useful signals are per-test `.log` files beginning with `ok:` and an aggregate `test_fortify.log`; failures report missing expected compiler diagnostics or unresolved fortify symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memchr.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memchr.c

## Purpose

This compile-time fortify test verifies detection of a read overflow in `memchr()`.

## Important APIs, Control Flow, And State

The file defines `TEST` as `memchr(small, 0x7A, sizeof(small) + 1)` and includes `test_fortify.h`, whose `do_fortify_tests()` initializes shared buffers and expands `TEST`. The state is the common `small` array; the one-byte oversized length is intended to trigger the `__read_overflow` fortify path.

## Dependencies, Risks, And Test Signals

It depends on compiler object-size analysis and the shared harness. The expected signal is a build failure warning or unresolved symbol matching the filename-derived `__read_overflow`; successful compilation without that symbol is a failed test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memchr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memchr_inv.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memchr_inv.c

## Purpose

This negative build test checks fortify handling for an oversized `memchr_inv()` read from a known small object.

## Important APIs, Control Flow, And State

`TEST` expands to `memchr_inv(small, 0x7A, sizeof(small) + 1)`. The shared header initializes `small` and compiles the expression inside `do_fortify_tests()`. No runtime execution is expected; the compiler must diagnose the read size.

## Dependencies, Risks, And Test Signals

The test depends on the fortify implementation for `memchr_inv()` and compiler size knowledge for fixed arrays. The expected build artifact is a log confirming `__read_overflow` detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memchr_inv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memcmp.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memcmp.c

## Purpose

This file validates that fortify detects a source read past the end of the first argument to `memcmp()`.

## Important APIs, Control Flow, And State

`TEST` is `memcmp(small, large, sizeof(small) + 1)`. `small` has 16 bytes and `large` has 32 bytes in the common harness, so the first operand cannot legally satisfy the requested compare length.

## Dependencies, Risks, And Test Signals

It exercises the `memcmp()` fortify wrapper. The log should show `__read_overflow` detection; missing detection would indicate a regression in bidirectional object-size checking for compare operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memcmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memscan.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memscan.c

## Purpose

This test checks read-overflow diagnostics for `memscan()` over a fixed small buffer.

## Important APIs, Control Flow, And State

`TEST` expands to `memscan(small, 0x7A, sizeof(small) + 1)`. The shared header provides the initialized `small` buffer and compiles the expression inside `do_fortify_tests()`.

## Dependencies, Risks, And Test Signals

The target integration point is the fortified `memscan()` wrapper. The expected signal is detection of the filename-derived `__read_overflow`; a clean object without that symbol is a test failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow-memscan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2-memcmp.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2-memcmp.c

## Purpose

This companion `memcmp()` test validates overflow detection on the second source argument.

## Important APIs, Control Flow, And State

`TEST` is `memcmp(large, small, sizeof(small) + 1)`. The large first operand is valid for the length, while the second operand is too short, ensuring the fortify check covers both input pointers.

## Dependencies, Risks, And Test Signals

It depends on compiler-visible sizes for both arrays and the fortify `memcmp()` implementation. The expected build signal is `__read_overflow2`, matching the filename prefix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2-memcmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2-memcpy.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2-memcpy.c

## Purpose

This negative compile test checks source-side read overflow detection in `memcpy()`.

## Important APIs, Control Flow, And State

The expression is `memcpy(large, instance.buf, sizeof(large))`. The destination can hold 32 bytes, but `instance.buf` is a 16-byte field, so the read side is invalid.

## Dependencies, Risks, And Test Signals

It targets the fortified `memcpy()` wrapper and object-size detection for struct fields. The expected symbol/warning is `__read_overflow2`; lack of detection would permit copying beyond the source field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2-memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2-memmove.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2-memmove.c

## Purpose

This is the `memmove()` equivalent of the source-side fortify overflow test.

## Important APIs, Control Flow, And State

`TEST` expands to `memmove(large, instance.buf, sizeof(large))`. The source field is smaller than the copy length, while the destination is large enough, isolating read overflow behavior.

## Dependencies, Risks, And Test Signals

It depends on the `memmove()` fortify wrapper and compile-time struct field sizing. The expected output is an `ok:` log for `__read_overflow2` detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2-memmove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2_field-memcpy.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2_field-memcpy.c

## Purpose

This test checks the field-specific source-read overflow diagnostic for `memcpy()`.

## Important APIs, Control Flow, And State

`TEST` is `memcpy(large, instance.buf, sizeof(instance.buf) + 1)`. It reads one byte beyond the known struct field while writing into a large enough destination.

## Dependencies, Risks, And Test Signals

The integration point is fortify's distinction between whole-object and field-size checking. The expected warning/symbol is `__read_overflow2_field`, which catches field-local overreads even when surrounding struct storage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2_field-memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2_field-memmove.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2_field-memmove.c

## Purpose

This file validates field-specific source-overread detection in `memmove()`.

## Important APIs, Control Flow, And State

The `TEST` expression is `memmove(large, instance.buf, sizeof(instance.buf) + 1)`. The destination is intentionally large enough so the expected issue is the source field length.

## Dependencies, Risks, And Test Signals

It targets `memmove()` fortify field-size diagnostics. The expected log confirms `__read_overflow2_field`; missed detection would mean field overreads can be hidden by enclosing object size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2_field-memmove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/test_fortify.h -->
# sources/distributed-fs/ceph-client/lib/test_fortify/test_fortify.h

## Purpose

This shared header is the common harness for all fortify compile-time tests in the directory. Each small source defines a `TEST` macro before including it.

## Important APIs, Types, And Functions

It includes kernel, printk, slab, and string headers. It defines `__BUF_SMALL`, `__BUF_LARGE`, `struct fortify_object`, literal strings, shared global arrays (`small_src`, `large_src`, `small`, `large`), a global `instance`, and `size`. `do_fortify_tests()` initializes the buffers and struct field with `memset()` and then expands `TEST`.

## Control Flow And State

There is no module entry point here. The harness creates compiler-visible object sizes and initializations so each test expression is compiled in a consistent context. The global symbols are intentionally simple and fixed-size to make fortify diagnostics deterministic.

## Dependencies And Integration Points

It integrates with `test_fortify.sh` and the Makefile's per-source compile rules. The `TEST` macro contract is the extension point used by every C file in this directory.

## Risks And Test Signals

Changing buffer sizes, literal lengths, or the struct layout changes the expected overflow categories across every test. A valid signal is that each test expands to exactly one unsafe operation whose expected symbol is derivable from the source filename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/test_fortify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/test_fortify.sh -->
# sources/distributed-fs/ceph-client/lib/test_fortify/test_fortify.sh

## Purpose

This shell script is the per-test verifier for fortify compile-time failures. It compiles a given source and decides whether the expected fortify diagnostic was observed.

## Important APIs And Control Flow

The script derives `FILE`, `FUNC`, and expected symbol `WANT="__${FILE%%-*}"` from the source filename. It compiles with `-Werror`, capturing stderr to a temporary log. If compilation fails, it greps for an error mentioning the expected symbol. If compilation succeeds, it checks `nm` output for an unresolved reference to the expected symbol, which covers cases where the diagnostic is deferred.

## State, Dependencies, And Integration Points

It writes a temporary file beside the final log and removes it with a trap. It forces `LANG=C` so compiler messages use predictable punctuation. It depends on POSIX shell, the compiler, `nm`, `grep`, and the kbuild-provided argument list.

## Risks And Test Signals

The script is tightly coupled to filename conventions and compiler warning wording. It handles GCC and Clang's warning-attribute phrasing with a regex. Output beginning with `ok:` is success; output beginning with `warning:` is a test failure and includes compiler output for diagnosis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/test_fortify.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-memcpy.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-memcpy.c

## Purpose

This test validates destination write-overflow detection for `memcpy()` into a struct field.

## Important APIs, Control Flow, And State

`TEST` is `memcpy(instance.buf, large_src, sizeof(large_src))`. `instance.buf` is 16 bytes and `large_src` is 32 bytes, so the write exceeds the field destination.

## Dependencies, Risks, And Test Signals

The expected fortify symbol is `__write_overflow`. A missed diagnostic would indicate `memcpy()` can overrun a known fixed-size destination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-memmove.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-memmove.c

## Purpose

This is the `memmove()` destination-overflow equivalent for the fortify test suite.

## Important APIs, Control Flow, And State

`TEST` expands to `memmove(instance.buf, large_src, sizeof(large_src))`. The source has enough bytes, but the destination field is too small.

## Dependencies, Risks, And Test Signals

The target is the fortified `memmove()` wrapper. The build log should confirm `__write_overflow`; otherwise a known oversized move into a field escaped detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-memmove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-memset.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-memset.c

## Purpose

This negative build test checks destination-size diagnostics for `memset()`.

## Important APIs, Control Flow, And State

`TEST` is `memset(instance.buf, 0x5A, sizeof(large_src))`, writing 32 bytes into a 16-byte struct field.

## Dependencies, Risks, And Test Signals

It depends on fortified `memset()` size checking. The expected outcome is `__write_overflow` detection in the per-test log.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-memset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strcpy-lit.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strcpy-lit.c

## Purpose

This test ensures fortify catches copying an oversized string literal with `strcpy()`.

## Important APIs, Control Flow, And State

`TEST` expands to `strcpy(small, LITERAL_LARGE)`. `small` is 16 bytes and `LITERAL_LARGE` is sized for the larger buffer, making the destination overflow statically visible.

## Dependencies, Risks, And Test Signals

It checks literal-aware string fortify behavior. The expected diagnostic is `__write_overflow`; missing it would weaken common string literal overflow detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strcpy-lit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strcpy.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strcpy.c

## Purpose

This test checks `strcpy()` destination overflow when the source is a fixed large array instead of a literal at the call site.

## Important APIs, Control Flow, And State

`TEST` is `strcpy(small, large_src)`. The shared header declares `large_src` with a large literal initializer and `small` as a 16-byte destination.

## Dependencies, Risks, And Test Signals

It depends on fortified string object-size analysis for arrays. The expected result is `__write_overflow`; a clean compile would indicate a regression in non-literal `strcpy()` checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strncpy-src.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strncpy-src.c

## Purpose

This test validates `strncpy()` destination overflow when the requested copy length exceeds the destination size.

## Important APIs, Control Flow, And State

`TEST` expands to `strncpy(small, large_src, sizeof(small) + 1)`. The source is large enough, and the explicit count is one byte too large for `small`.

## Dependencies, Risks, And Test Signals

It targets fortified `strncpy()` write-size checks. The expected symbol is `__write_overflow`; the source suffix in the filename distinguishes this scenario from field-specific variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strncpy-src.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strncpy.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strncpy.c

## Purpose

This file tests `strncpy()` overflow into a struct field destination.

## Important APIs, Control Flow, And State

`TEST` is `strncpy(instance.buf, large_src, sizeof(instance.buf) + 1)`. The explicit copy count exceeds the size of `instance.buf`.

## Dependencies, Risks, And Test Signals

The test relies on fortify distinguishing the field destination from the surrounding struct. The expected output confirms `__write_overflow` detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strncpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strscpy.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strscpy.c

## Purpose

This test checks destination overflow detection for the kernel `strscpy()` helper.

## Important APIs, Control Flow, And State

`TEST` expands to `strscpy(instance.buf, large_src, sizeof(instance.buf) + 1)`. The specified destination size exceeds the actual field size by one byte.

## Dependencies, Risks, And Test Signals

It validates that `strscpy()` participates in fortify destination-size checking. The expected signal is `__write_overflow` in the compile log.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strscpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow_field-memcpy.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow_field-memcpy.c

## Purpose

This test validates field-specific destination overflow detection for `memcpy()`.

## Important APIs, Control Flow, And State

`TEST` is `memcpy(instance.buf, large, sizeof(instance.buf) + 1)`. The source can supply the bytes, but the destination field cannot receive them.

## Dependencies, Risks, And Test Signals

The expected diagnostic is `__write_overflow_field`, which is stricter than whole-object bounds. It guards against overwriting adjacent members of `struct fortify_object`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow_field-memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow_field-memmove.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow_field-memmove.c

## Purpose

This file is the `memmove()` field-destination overflow test.

## Important APIs, Control Flow, And State

`TEST` expands to `memmove(instance.buf, large, sizeof(instance.buf) + 1)`. It writes one byte past `instance.buf` while using a sufficiently large source.

## Dependencies, Risks, And Test Signals

The key expected signal is `__write_overflow_field`. If only whole-object size is considered, this overrun into neighboring struct members could be missed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow_field-memmove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow_field-memset.c -->
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow_field-memset.c

## Purpose

This negative test checks field-specific destination overflow detection for `memset()`.

## Important APIs, Control Flow, And State

`TEST` is `memset(instance.buf, 0x42, sizeof(instance.buf) + 1)`, a one-byte overrun of the struct field.

## Dependencies, Risks, And Test Signals

It targets the fortified `memset()` field-size path. The expected compile signal is `__write_overflow_field`, proving adjacent struct members are protected from constant-size overwrites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow_field-memset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fpu.h -->
# sources/distributed-fs/ceph-client/lib/test_fpu.h

## Purpose

This header declares the architecture-neutral entry point for the kernel FPU selftest implementation.

## Important APIs, Control Flow, And State

It exports only `int test_fpu(void);` behind an include guard. It has no state and no inline logic.

## Dependencies, Risks, And Test Signals

`test_fpu_glue.c` calls this function inside `kernel_fpu_begin()`/`kernel_fpu_end()`, while `test_fpu_impl.c` defines it. The main risk is declaration/definition mismatch if the implementation changes its ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fpu_glue.c -->
# sources/distributed-fs/ceph-client/lib/test_fpu_glue.c

## Purpose

This module provides the kernel-facing glue for testing floating-point operations under the kernel FPU API. Reading a debugfs file runs the numeric test under an explicit FPU critical section.

## Important APIs, Types, And Functions

`test_fpu_get()` calls `kernel_fpu_begin()`, invokes `test_fpu()`, calls `kernel_fpu_end()`, stores `1` in the debugfs value, and returns the test status. `DEFINE_DEBUGFS_ATTRIBUTE()` creates the read-only file operations. `test_fpu_init()` checks `kernel_fpu_available()`, creates `/sys/kernel/debug/selftest_helpers`, and adds `test_fpu`.

## Control Flow And State

The only persistent state is `selftest_dir`, removed on module exit. Each read of the debugfs file executes the FPU test synchronously. On success, userspace reads `1\n`; on failure, the debugfs read returns an error or the kernel may fault if FPU state handling is broken.

## Dependencies And Integration Points

It depends on debugfs, module support, `linux/fpu.h`, and the implementation declared in `test_fpu.h`. It integrates with kernel selftests through the debugfs helper path.

## Risks And Test Signals

The key risk is corrupting FPU state if begin/end pairing is broken. Test signals are debugfs file presence, read return status, returned value, and absence of kernel crashes when userspace has unusual FPU control state before the read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fpu_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fpu_impl.c -->
# sources/distributed-fs/ceph-client/lib/test_fpu_impl.c

## Purpose

This file implements the actual floating-point arithmetic check used by the FPU selftest glue.

## Important APIs, Types, And Functions

`test_fpu()` uses volatile `double` variables to prevent optimization away of arithmetic. It checks precision/rounding by adding tiny values to `4.0`, tests denormal and large intermediate values with `1e-310`, and returns `0` only if all expected comparisons are true.

## Control Flow And State

The function has no persistent state. It runs a fixed arithmetic sequence and returns `-EINVAL` on unexpected rounding or denormal handling.

## Dependencies And Integration Points

It includes errno and the local header. It must be called only from a context that has enabled kernel FPU usage, which `test_fpu_glue.c` supplies.

## Risks And Test Signals

The test assumes IEEE-like double semantics, nearest rounding, and denormal support. A return of `0` is success; `-EINVAL` indicates FPU state or compiler/runtime behavior did not match the kernel FPU contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_fpu_impl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_free_pages.c -->
# sources/distributed-fs/ceph-client/lib/test_free_pages.c

## Purpose

This module stress-tests `free_pages()` behavior when a page has a speculative reference, checking that compound and non-compound high-order page frees do not leak memory.

## Important APIs, Types, And Functions

`test_free_pages(gfp_t gfp)` loops one million times, allocates order-3 pages with `__get_free_pages()`, gets the first page, calls `get_page()`, frees the allocation with `free_pages()`, then drops the speculative reference with `put_page()`. `m_in()` runs this once with `GFP_KERNEL` and once with `GFP_KERNEL | __GFP_COMP`.

## Control Flow And State

All work happens during module init. There is no persistent state and exit is a no-op. The loop stresses reference accounting and freeing paths under repeated allocations.

## Dependencies And Integration Points

It depends on the page allocator, page reference APIs, `virt_to_page()`, and module init/exit. It integrates by being loaded manually or by kselftest infrastructure.

## Risks And Test Signals

The test is CPU and allocator intensive and does not check allocation failure before `virt_to_page()`, so it assumes the order-3 allocations succeed in the test environment. Signals are kernel logs for the three phases and external memory-leak/page-ref debug tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_free_pages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_hexdump.c -->
# sources/distributed-fs/ceph-client/lib/test_hexdump.c

## Purpose

This module validates `hex_dump_to_buffer()` formatting across row sizes, group sizes, ASCII/no-ASCII modes, endian-sensitive grouping, and truncated output buffers.

## Important APIs, Types, And Functions

It defines fixed binary input `data_b`, ASCII projection `data_a`, and expected strings for group sizes 1, 2, 4, and 8 in little- and big-endian order. `test_hexdump_prepare_test()` constructs the expected string. `test_hexdump()` compares full outputs. `test_hexdump_overflow()` checks return lengths and truncation behavior for every buffer size up to `TEST_HEXDUMP_BUF_SIZE`.

## Control Flow And State

Init picks random row sizes and lengths, runs normal formatting tests with and without ASCII, then exhaustively checks overflow behavior for all buffer lengths in both modes. It tracks `total_tests` and `failed_tests` in init-only data and returns `-EINVAL` if any mismatch occurs.

## Dependencies And Integration Points

The test depends on `hex_dump_to_buffer()`, random helpers, endian configuration, string/memory helpers, and module init. It is self-contained and reports via kernel logs.

## Risks And Test Signals

Random length choices provide variation but can make an exact failing case require the log for reproduction. Strong signals are `all N tests passed` or detailed `Result`/`Expect` mismatch lines including length, row size, group size, and buffer length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_hexdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_hmm.c -->
# sources/distributed-fs/ceph-client/lib/test_hmm.c

## Purpose

This module is a character-device HMM test driver that mirrors a process address space and simulates device private or coherent memory. It lets userspace read, write, snapshot, migrate, make exclusive, and release mirrored pages through ioctls.

## Important APIs, Types, And Functions

Major types include `struct dmirror` for per-open mirror state, `struct dmirror_device` for each simulated device, `struct dmirror_chunk` for `dev_pagemap` backed device memory, and `struct dmirror_bounce` for temporary user-copy buffers. It uses an XArray as a device page table with pointer tags for write and atomic/exclusive mappings. Important functions cover open/release, MMU interval invalidation, range faulting with `hmm_range_fault()`, read/write bounce copies, migration to device/system through `migrate_vma`, snapshot generation, device-memory fault handling, chunk allocation/removal, and ioctl dispatch.

## Control Flow And State

Module init allocates a chrdev region and creates two device-private devices, plus two coherent devices if both SPM address parameters are supplied. Opening a device allocates a `dmirror`, initializes an XArray, and registers a full-range `mmu_interval_notifier` against the caller's `mm`. Reads and writes consult the XArray, fault missing pages into the mirror, and copy data through a vmalloc bounce buffer. Migration to device allocates simulated device pages, copies system page contents, finalizes migration, and maps backing pages into the XArray. Migration back to system uses `migrate_vma_setup()`, allocates normal pages, copies data back, and erases device mappings. Release removes the interval notifier, evicts chunks back to system pages, destroys the XArray, and frees per-open state.

## State And Persistence

Persistent kernel state includes global `dmirror_devices`, per-device devmem chunk arrays, free-page/free-folio lists protected by spinlock, allocation counters, and per-open XArray mappings protected by `dmirror->mutex`. Device private pages use `zone_device_data` to point to backing system pages; coherent pages use the actual mapped page. The state persists across ioctls until file release or explicit `HMM_DMIRROR_RELEASE`.

## Dependencies And Integration Points

The file depends on HMM, MMU interval notifiers, migrate_vma, ZONE_DEVICE/dev_pagemap, memremap_pages, char devices, device model, xarray, mmap insertion, uaccess, swap/rmap, and the local UAPI header. Userspace integrates through `/dev/hmm_dmirror*`, mmap, and the ioctls defined in `test_hmm_uapi.h`.

## Risks And Test Signals

Risks include page lifetime bugs in fake device memory, missing invalidation of stale XArray entries, large-folio split/fallback corner cases, allocation-failure injection with `HMM_DMIRROR_FLAG_FAIL_ALLOC`, and cleanup ordering around chunk removal. Test signals include ioctl return codes, `cpages` and `faults`, snapshot permission bytes, successful round-trip data after migration, SIGBUS/OOM behavior on device faults, and kernel warnings from migration or page-type assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_hmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_hmm_uapi.h -->
# sources/distributed-fs/ceph-client/lib/test_hmm_uapi.h

## Purpose

This header defines the userspace ABI for the HMM mirror test driver.

## Important APIs, Types, And Functions

`struct hmm_dmirror_cmd` carries input address, user buffer pointer, page count, copied-page count, and fault count. Ioctls cover read, write, migrate to device, migrate to system, snapshot, exclusive migration, exclusive check, release, and flags. It also defines `HMM_DMIRROR_FLAG_FAIL_ALLOC`, snapshot protection/result byte values, and memory type identifiers for device-private and device-coherent modes.

## Control Flow And State

The header has no executable flow. Its fields are both input and output depending on ioctl: `addr`, `ptr`, and `npages` are inputs, while `cpages` and `faults` are updated by the driver.

## Dependencies And Integration Points

It includes Linux fixed-width types and ioctl macros and is included by both the kernel driver and userspace selftests. The ioctl numbers are part of the external contract for `/dev/hmm_dmirror*`.

## Risks And Test Signals

Changing struct layout, ioctl numbers, or enum values breaks userspace compatibility. Snapshot tests should verify every defined protection code, including local versus remote private/coherent device pages and PMD/PUD markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_hmm_uapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_ida.c -->
# sources/distributed-fs/ceph-client/lib/test_ida.c

## Purpose

This module exercises the IDA allocator API across allocation, free, destroy, maximum id, internal representation conversion, bad frees, and first-used-id queries.

## Important APIs, Types, And Functions

It uses a global `DEFINE_IDA(ida)` plus `tests_run` and `tests_passed`. `IDA_BUG_ON()` records assertions and dumps state/stack on failure. Test functions cover `ida_alloc()`, `ida_alloc_min()`, `ida_free()`, `ida_destroy()`, `ida_is_empty()`, `ida_exists()`, `ida_find_first()`, and `ida_find_first_range()`.

## Control Flow And State

`ida_checks()` runs all test groups during module init and prints the pass count. Each group leaves the IDA empty before the next group. The return convention is unusual: it returns `0` if any test failed and `-EINVAL` when all tests passed, causing a successful selftest to fail module insertion by design.

## Dependencies And Integration Points

It depends on `linux/idr.h`, module infrastructure, stack dumping, and kernel logging. It is a self-contained kernel API regression test.

## Risks And Test Signals

The intentional bad-free section emits expected "not allocated" warnings bracketed by log markers. Key signals are the final `IDA: X of X tests passed` line, any stack dump from `IDA_BUG_ON`, and the init return behavior that must be interpreted as a test harness convention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_ida.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_kho.c -->
# sources/distributed-fs/ceph-client/lib/test_kho.c

## Purpose

This module tests KHO, kexec handover, by preserving randomly generated folio data plus metadata in an FDT subtree and verifying it after a handover-enabled boot.

## Important APIs, Types, And Functions

`struct kho_test_state` tracks allocated folios, physical metadata for those folios, preserved vmalloc metadata, count of preserved folios, the FDT folio, and checksum. The save path uses `kho_preserve_folio()`, `kho_preserve_vmalloc()`, `fdt_*()` builders, and `kho_add_subtree()`. The restore path uses `kho_retrieve_subtree()`, `kho_restore_vmalloc()`, `kho_restore_folio()`, and checksum recomputation.

## Control Flow And State

On init, the module exits quietly if KHO is disabled. If the `kho_test` subtree is present, it validates compatibility, magic, metadata shape, and checksum, then reports restore success or failure. If the subtree is absent, it allocates random folios up to `max_mem`, computes a checksum, preserves metadata and folios, builds an FDT subtree containing `nr_folios`, `folios_info`, and `csum`, and registers that subtree for handover. Exit removes the subtree and unpreserves/frees all state.

## State And Persistence

This file explicitly tests persistence across kexec handover. Folio physical addresses and orders are stored as `phys | order`; vmalloc metadata is preserved through `struct kho_vmalloc`; data integrity is represented by `csum_partial()`.

## Dependencies And Integration Points

It depends on KHO APIs, libfdt, kexec handover ABI, folio allocation, vmalloc, random bytes, and checksum helpers. The `max_mem` module parameter bounds test memory consumption.

## Risks And Test Signals

Risks include excessive allocation from `max_mem`, cleanup paths that unpreserve or free partially initialized state, and FDT property layout drift. Signals are `KHO restore succeeded`, `KHO restore failed`, checksum mismatch errors, and successful save registration when no subtree exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_kho.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_kmod.c -->
# sources/distributed-fs/ceph-client/lib/test_kmod.c

## Purpose

This misc-device driver stress-tests the kernel module loader through concurrent `request_module()` calls and concurrent filesystem type lookups via `get_fs_type()`.

## Important APIs, Types, And Functions

Core types are `struct test_config`, `struct kmod_test_device_info`, and `struct kmod_test_device`. Config stores target driver, target filesystem, thread count, selected test case, and result. Per-thread info stores return values, filesystem pointers, task pointers, and module-put obligations. Device state includes miscdevice, sysfs attributes, config/trigger/thread locks, completion, and a per-thread info array.

The sysfs interface includes `trigger_config`, `config`, `reset`, `config_test_driver`, `config_test_fs`, `config_num_threads`, `config_test_case`, and `test_result`. `run_request()` dispatches either `request_module()` or `get_fs_type()` in a kthread. `try_requests()` creates all kthreads, waits for completion, and tallies results.

## Control Flow And State

`late_initcall(test_kmod_init)` registers the first `test_kmodN` misc device and optionally runs startup tests if `force_init_test` is set. A trigger locks config/trigger mutexes, starts up to `num_threads` kthreads, waits for `kthreads_done`, then records the first observed error in `test_result`. Reset rebuilds the default config and resizes the info array. Exit stops live threads, unregisters misc devices, frees config strings and arrays, and removes all registered test devices.

## Dependencies And Integration Points

It depends on kmod, module, kthread, filesystem type lookup, miscdevice/sysfs, vmalloc, and the optional `get_kmod_umh_limit()` helper. Userspace selftests drive the sysfs attributes, usually through `tools/testing/selftests/kmod/kmod.sh`.

## Risks And Test Signals

The driver deliberately stresses usermode-helper/module-loader limits and can create many concurrent threads. Risks include OOM during thread setup, stale module references if `module_put()` is missed, and interpreting positive `request_module()` statuses. Signals are `test_result`, per-thread log lines, completion of all threads, and correct cleanup on reset/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_kmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_lockup.c -->
# sources/distributed-fs/ceph-client/lib/test_lockup.c

## Purpose

This module intentionally generates lockups, stalls, sleeps, and lock contention patterns for watchdog and scheduler testing. It is controlled entirely by module parameters and returns `-EAGAIN` after a normal run so it does not remain loaded.

## Important APIs, Types, And Functions

Parameters control active wait time, cooldown, iterations, CPU fan-out, sleep state, hrtimer use, iowait accounting, lock mode, watchdog touching, `cond_resched()`, IRQ/BH/preempt/RCU locking, arbitrary lock pointers, page allocation under locks, and file-derived locks. `test_lock()` acquires configured locks or disables contexts. `test_unlock()` reverses them. `test_wait()` busy-waits for `TASK_RUNNING` or schedules in the selected sleep state. `test_lockup()` performs the configured iterations and optional page allocation/reallocation.

## Control Flow And State

Init records `main_task`, parses the `state` parameter, validates unsafe lock pointers with `get_kernel_nofault()` and optional debug magic checks, rejects combinations that would sleep in atomic context, optionally opens `file_path` to derive inode/mapping/superblock semaphores, then either runs on the current CPU or queues per-CPU work on `system_highpri_wq` for all online CPUs. It reports timing, maximum lock wait, page allocation failures, and final duration before returning `-EAGAIN` or `-EINTR`.

## State And Persistence

Persistent state is limited to module parameter globals, atomic counters, `main_task`, optional `test_file`, and per-CPU work structs during init. Any allocated pages are held only across test iterations and freed before exit from `test_lockup()`.

## Dependencies And Integration Points

It depends on scheduler, delay, CPU hotplug read locking, workqueues, watchdog APIs, MM locks, uaccess nofault helpers, files/inodes/superblocks, and module parameters. It integrates with watchdog and lockup selftests through controlled module insertion.

## Risks And Test Signals

This module can deliberately hang CPUs, disable interrupts/preemption, take arbitrary kernel locks by address, and allocate memory under locks. It has guards against invalid pointers and sleeping in atomic context, but it should only be run in controlled test environments. Signals include `START`/`FINISH` logs, per-CPU start/finish logs, max lock wait, allocation failure count, watchdog reports, RCU stall reports, and `-EAGAIN` for a completed test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_lockup.c -->
