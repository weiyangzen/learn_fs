# Research: subset-b-005849

This grouped report covers Linux kernel compatibility headers under `sources/distributed-fs/ceph-client/include/linux`. Each section preserves the source path and is bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compaction.h -->
## sources/distributed-fs/ceph-client/include/linux/compaction.h

Purpose: This header declares the memory compaction policy and external interfaces used by the page allocator, kcompactd, NUMA node registration, and fragmentation reporting. It is a coordination contract for `CONFIG_COMPACTION` builds rather than an implementation file.

Important APIs, types, and functions: `enum compact_priority` orders direct-compaction effort from full synchronous through asynchronous. `enum compact_result` encodes the allocator-visible result states, including skipped, deferred, continued, complete, contended, and success. `compact_gap(order)` computes the extra order-0 free page reserve needed above a watermark so the free scanner has target pages while isolating migration pages. `current_is_kcompactd()` checks `PF_KCOMPACTD`. Under `CONFIG_COMPACTION`, the header exports fragmentation queries (`extfrag_for_order`, `fragmentation_index`), direct compaction (`try_to_compact_pages`), suitability checks, deferral reset, kcompactd lifecycle, and wakeup hooks. NUMA sysfs registration is separately gated by `CONFIG_SYSFS` and `CONFIG_NUMA`.

Control flow: Callers first ask suitability helpers whether compaction is worthwhile for a zone, allocation order, and watermark. The allocation path then calls `try_to_compact_pages()`, interpreting `compact_result` to retry allocation, continue reclaim, or give up. Background compaction is driven by `wakeup_kcompactd()`, while node hotplug invokes `kcompactd_run()` and `kcompactd_stop()`.

State and persistence: The header exposes no persistent storage, but its APIs manipulate per-zone and per-node compaction state in mm code: deferred compaction, isolation suitability, fragmentation measurements, and kcompactd thread state. Stub definitions under disabled configs deliberately preserve buildability while making compaction unavailable.

Dependencies and integration points: It depends on mm types such as `struct zone`, `pg_data_t`, `gfp_t`, `struct page`, `struct alloc_context`, and `struct node`, and it is coupled to trace state because `enum compact_result` comments require matching `include/trace/events/compaction.h`.

Risks and test signals: Risks include mismatched result enum trace decoding, incorrect suitability logic causing allocation latency or failures, and improper kcompactd wakeups. Test signals are high-order allocation stress, fragmentation-index checks, NUMA node hotplug, tracepoint result names, and builds with `CONFIG_COMPACTION` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compat.h -->
## sources/distributed-fs/ceph-client/include/linux/compat.h

Purpose: This header defines the generic 32-bit compatibility syscall ABI used when a kernel serves tasks with narrower userspace types. It maps compat user structures, syscall wrapper macros, signal conversions, pointer conversion, and a large set of `compat_sys_*` prototypes.

Important APIs, types, and functions: `COMPAT_SYSCALL_DEFINE0..6` and `COMPAT_SYSCALL_DEFINEx` declare compat syscall entry points, error-injection metadata, sign-extension stubs, and `__do_compat_sys*` bodies. Major ABI structures include `compat_iovec`, `compat_stack_t`, `compat_sigset_t`, `compat_sigaction`, `compat_siginfo_t`, `compat_rlimit`, `compat_flock`, `compat_flock64`, `compat_rusage`, `compat_dirent`, `compat_sigevent_t`, `compat_ifreq`, robust-list types, and `compat_keyctl_kdf_params`. Conversion helpers include `copy_siginfo_to_external32`, `copy_siginfo_from_user32`, `copy_siginfo_to_user32`, `get_compat_sigevent`, `get_compat_sigset`, `put_compat_sigset`, unsafe signal-set accessors, `compat_restore_altstack`, `__compat_save_altstack`, `compat_get_bitmap`, `compat_put_bitmap`, `compat_ptr`, and `ptr_to_compat`.

Control flow: The syscall macro path aliases the public `compat_sys*` function to a sign-extension wrapper. The wrapper coerces user ABI-sized parameters to kernel argument types, calls the inline `__do_compat_sys*` implementation, and emits compile-time argument checks. Signal set helpers choose endian-specific packing paths; big-endian 64-bit kernels split native signal words into compat words, while little-endian paths can copy the compact representation directly.

State and persistence: The header itself stores no long-lived state. It defines serialized userspace layouts and conversion functions that read or write task state such as alternate stacks, signal masks, robust-list heads, rlimits, and syscall arguments. The state persistence risk is ABI stability: structure sizes, packing, and endian order are externally visible.

Dependencies and integration points: It depends on architecture-provided `asm/compat.h`, `asm/siginfo.h`, `asm/signal.h`, optional `asm/syscall_wrapper.h`, and generic usercopy, signal, filesystem, networking, aio, and time headers. It integrates with syscall tables, audit-visible syscall numbers, signal delivery, ptrace, epoll, file operations, IPC, networking, exec, kexec, and time32/time64 variants.

Risks and test signals: Primary risks are ABI layout drift, sign-extension mistakes, endian mishandling, unsafe usercopy faults, and calling `compat_sys_*` directly from kernel code instead of `kcompat_*` wrappers. Test signals include 32-bit userspace syscall suites on 64-bit kernels, signal delivery and siginfo tests, big-endian compat builds, x32 paths, time64/time32 transition coverage, and fault-injection of user pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler-clang.h -->
## sources/distributed-fs/ceph-client/include/linux/compiler-clang.h

Purpose: This compiler-specific header normalizes Clang behavior for the kernel after `compiler_types.h` has been included. It defines sanitizer attributes, diagnostic pragmas, inline assembly constraints, and feature compatibility macros.

Important APIs, types, and functions: It redefines `__cleanup(func)` with `__maybe_unused` to avoid older Clang unused-variable warnings for cleanup-only variables. It sets `KASAN_ABI_VERSION` to 5. It maps old `__has_feature` sanitizer results to GCC-style `__SANITIZE_ADDRESS__`, `__SANITIZE_HWADDRESS__`, and `__SANITIZE_THREAD__`. It defines `__no_sanitize_address`, `__no_sanitize_thread`, `__no_sanitize_undefined`, `__no_sanitize_memory`, `__no_kmsan_checks`, `__no_sanitize_coverage`, `__no_kstack_erase`, and optionally `__noscs`. Diagnostic helpers include `__diag_clang`, severity names, `_Pragma` wrappers, and `__diag_ignore_all`. Assembly constraint defaults are restricted to avoid known Clang `"g"` and `"rm"` constraint problems. `CC_HAS_TYPEOF_UNQUAL` models Clang support for `__typeof_unqual__`.

Control flow: This file is included only on Clang builds through `compiler_types.h`; it has no runtime control flow. Preprocessor decisions derive from Clang feature probes and kernel config. Sanitizer feature probes progressively refine attributes used by later headers and code.

State and persistence: No runtime state is stored. Persistent behavior is compile-time ABI and instrumentation selection: sanitizer attributes determine whether code is instrumented, KASAN ABI selection affects instrumentation compatibility, and assembly constraints affect generated code.

Dependencies and integration points: It depends on `__has_feature`, `__has_attribute`, Clang version macros, `CONFIG_ARCH_USE_BUILTIN_BSWAP`, sanitizer configs, `CONFIG_KCOV`, shadow call stack, and downstream compiler macros in `compiler_types.h` and `compiler.h`.

Risks and test signals: Risks include hiding sanitizer instrumentation where needed, failing to disable it in low-level paths, incorrect feature emulation for newer/older Clang, and bad inline-asm constraints producing invalid code. Test signals are allmodconfig builds under supported Clang versions, sanitizer boot tests, KCOV/KMSAN/KASAN builds, shadow-call-stack builds, and compile tests for cleanup variables and inline assembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler-clang.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler-context-analysis.h -->
## sources/distributed-fs/ceph-client/include/linux/compiler-context-analysis.h

Purpose: This header provides optional Clang thread-safety style annotations for kernel "context locks". It lets kernel code express lock/context requirements in attributes that can be statically checked when `WARN_CONTEXT_ANALYSIS` is enabled, while compiling to no-ops otherwise.

Important APIs, types, and functions: Internal attributes include `__ctx_lock_type`, `__acquires_ctx_lock`, `__try_acquires_ctx_lock`, `__releases_ctx_lock`, `__requires_ctx_lock`, `__excludes_ctx_lock`, `__assumes_ctx_lock`, and shared variants. Public-facing helpers include `__guarded_by`, `__pt_guarded_by`, `context_lock_struct`, `disable_context_analysis`, `enable_context_analysis`, `__no_context_analysis`, `context_unsafe`, `__context_unsafe`, `context_unsafe_alias`, `token_context_lock`, `token_context_lock_instance`, `__must_hold`, `__must_not_hold`, `__acquires`, `__cond_acquires`, `__releases`, `__cond_releases`, `__acquire`, `__release`, and shared-lock counterparts. Return-value helpers `__acquire_ret` and `__acquire_shared_ret` acquire a context based on `__ret`.

Control flow: In analysis-enabled builds, macros expand to Clang capability attributes and no-op helper functions with acquire/release annotations. Conditional acquire and release macros encode return-value-dependent ownership, using inverted acquisition to model conditional release because Clang lacks a native conditional-release attribute. In ordinary builds, all attributes and helper calls disappear or return the passed result.

State and persistence: No runtime state is created; even the helper functions are empty. The persistent effect is on static analysis state: capabilities are acquired, released, or assumed in the compiler's model. `token_context_lock()` declares abstract extern lock tokens intentionally not backed by objects.

Dependencies and integration points: It integrates with `compiler_types.h`, diagnostic suppression macros, Clang thread-safety attributes, sparse/genksyms guards, and lock-like kernel APIs that annotate caller requirements.

Risks and test signals: Risks include annotations diverging from real locking, overusing `context_unsafe()` to hide bugs, incorrectly modeling conditional returns, and alias switches that require explicit `context_unsafe_alias()`. Test signals are `WARN_CONTEXT_ANALYSIS` builds, negative compile tests for missing locks, no-warning builds when the config is disabled, and review of all `__context_unsafe()` comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler-context-analysis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler-gcc.h -->
## sources/distributed-fs/ceph-client/include/linux/compiler-gcc.h

Purpose: This GCC-specific header normalizes compiler behavior and capabilities for kernel builds after `compiler_types.h` has selected GCC. It defines version-dependent ABI, sanitizer, diagnostic, inline-assembly, and plugin-related macros.

Important APIs, types, and functions: `GCC_VERSION` encodes major/minor/patch. `RELOC_HIDE(ptr, off)` hides pointer arithmetic from GCC optimizers using empty asm. `__latent_entropy` is enabled for the GCC latent entropy plugin. `barrier_before_unreachable()` works around GCC stack-allocation issues before unreachable markers. Builtin byte-swap macros are exposed when configured. `KASAN_ABI_VERSION` is 5 for GCC 7+ and 4 for older GCC. The header defines `__noscs`, `__no_sanitize_address`, `__no_sanitize_thread`, `__no_sanitize_undefined`, `__no_sanitize_coverage`, `__no_sanitize_memory`, `__no_kmsan_checks`, diagnostic pragmas, `__diag_ignore_all`, and `CC_HAS_TYPEOF_UNQUAL`.

Control flow: There is no runtime flow. Compile-time gates select attributes from GCC version, sanitizer predefines, Kconfig, and `__has_attribute`. The `RELOC_HIDE` expression does execute as inline assembly in generated code contexts, returning a pointer adjusted by `off` while hiding provenance from optimizer assumptions.

State and persistence: The file stores no state. It affects generated code persistence through KASAN ABI version, sanitizer exclusion attributes, randomization/plugin attributes, and optimizer barriers.

Dependencies and integration points: It depends on GCC predefined macros, GCC plugin macros, sanitizer predefines, `CONFIG_ARCH_USE_BUILTIN_BSWAP`, `CONFIG_SHADOW_CALL_STACK`, `CONFIG_KCOV`, and the shared compiler attribute layer.

Risks and test signals: Risks include wrong version feature assumptions, missing sanitizer suppressions in low-level code, optimizer miscompilation when `RELOC_HIDE` is removed or changed, and plugin attribute drift. Test signals are GCC matrix builds, KASAN/KCSAN/KCOV combinations, builds with GCC plugins and randstruct, PPC or other architecture tests sensitive to pointer provenance, and warning-pragmas smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler-version.h -->
## sources/distributed-fs/ceph-client/include/linux/compiler-version.h

Purpose: This generated-inclusion header forces broad rebuilds when compiler or tree-wide compiler-affecting inputs change. It is intentionally included by the build system, not directly by source files.

Important APIs, types, and functions: It defines `__LINUX_COMPILER_VERSION_H` and carries references to dependency-triggering config strings and generated headers. Optional includes are `generated/gcc-plugins.h` under `GCC_PLUGINS`, `generated/randstruct_hash.h` under `RANDSTRUCT`, and `generated/integer-wrap.h` under `INTEGER_WRAP`.

Control flow: There is no runtime flow. The important flow is build dependency discovery: fixdep scans the string `CONFIG_CC_VERSION_TEXT` and adds a dependency on the corresponding generated config file. Optional includes force rebuilds when GCC plugin behavior, randstruct seed, or Clang integer-wrap sanitizer state changes.

State and persistence: It stores no kernel runtime state. Its persistent effect is build-cache invalidation across translation units so compiler-related ABI, layout, instrumentation, and plugin behavior remain consistent.

Dependencies and integration points: It integrates with Kbuild, fixdep, Kconfig compiler version text, GCC plugin generation, randstruct hashing, and integer wrapping sanitizer metadata.

Risks and test signals: Direct inclusion is rejected by the guard. Risks include stale object files after compiler upgrade or changed plugin seed if these dependency hooks fail. Test signals are incremental builds after compiler version changes, randstruct seed changes, GCC plugin changes, and integer-wrap config updates; expected behavior is tree-wide recompilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler-version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler.h -->
## sources/distributed-fs/ceph-client/include/linux/compiler.h

Purpose: This is the shared kernel compiler abstraction layer used by C code. It defines branch prediction and profiling hooks, barriers, unreachable markers, symbol retention, data-race annotations, compile-time type checks, constant-expression helpers, and pointer offset helpers.

Important APIs, types, and functions: Branch APIs include `likely`, `unlikely`, `likely_notrace`, `unlikely_notrace`, and `ftrace_likely_update()` when branch profiling is active. `barrier()` and `barrier_data(ptr)` prevent compiler reordering or dead-store elimination. `unreachable()`, `KENTRY(sym)`, `RELOC_HIDE`, `absolute_pointer`, `OPTIMIZER_HIDE_VAR`, `__UNIQUE_ID`, `data_race(expr)`, `__BUILD_BUG_ON_ZERO_MSG`, array/string validation helpers, `TYPEOF_UNQUAL`, `KCFI_REFERENCE`, `offset_to_ptr`, `__ADDRESSABLE`, `__is_constexpr`, `is_signed_type`, `is_unsigned_type`, `statically_true`, `const_true`, and `prevent_tail_call_optimization()` are key exports.

Control flow: In branch profiling builds, `likely()` and `unlikely()` allocate static profiling records in special sections and call `ftrace_likely_update()` around the evaluated condition. `data_race()` disables KCSAN and context analysis around a single expression and restores both after evaluation. `offset_to_ptr()` turns a 32-bit relative offset stored at an address into an absolute pointer.

State and persistence: Runtime state appears only through instrumentation records placed in sections such as `_ftrace_annotated_branch`, `_ftrace_branch`, `___kentry+sym`, or `.discard.addressable`. Most macros are compile-time or codegen controls. `data_race()` temporarily changes current-task sanitizer state.

Dependencies and integration points: It includes `compiler_types.h` and `asm/rwonce.h`, integrates with ftrace, KCSAN, context analysis, objtool jump-table annotations, KCFI, linker scripts, and architecture memory-barrier definitions.

Risks and test signals: Risks include evaluating macro arguments more than intended, weakening memory/compiler barriers, hiding real data races, or losing symbols needed by assembly/linker discovery. Test signals include branch-profiling boots, KCSAN reports, objtool validation, KCFI builds, compile-time assertion failures, and all-compiler build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler_attributes.h -->
## sources/distributed-fs/ceph-client/include/linux/compiler_attributes.h

Purpose: This header provides compiler-agnostic names for common GNU/Clang attributes. It is deliberately sorted and mostly unconditional, with optional attributes guarded by `__has_attribute`.

Important APIs, types, and functions: It defines attribute wrappers such as `__alias`, `__aligned`, `__aligned_largest`, `__alloc_size__`, `__always_inline`, `__assume_aligned`, `__cleanup`, `__attribute_const__`, `__copy`, `__diagnose_as`, `__deprecated` as intentionally empty, `__designated_init`, `__compiletime_error`, `__visible`, `__printf`, `__scanf`, `__gnu_inline`, `__malloc`, `__mode`, `__no_caller_saved_registers`, `__noclone`, `fallthrough`, `__flatten`, `noinline`, `__nonstring`, `__no_profile`, `__noreturn`, `__no_stack_protector`, `__overloadable`, `__packed`, `__pass_dynamic_object_size`, `__pass_object_size`, `__pure`, `__section`, `__uninitialized`, `__always_unused`, `__maybe_unused`, `__used`, `__always_used`, `__must_check`, `__compiletime_warning`, `__disable_sanitizer_instrumentation`, `__weak`, and `__fix_address`.

Control flow: There is no runtime flow. Compile-time feature detection decides whether optional wrappers emit attributes or disappear. Later headers combine these primitives into config-sensitive attributes.

State and persistence: No state is stored. The persistent effects are ABI layout (`__packed`, `__aligned`), section placement, symbol retention, diagnostics, warning enforcement, call convention restrictions, and sanitizer instrumentation behavior.

Dependencies and integration points: It is included by `compiler_types.h` under `__KERNEL__`, then consumed throughout the kernel by subsystems declaring structures, callbacks, printf-like functions, allocation APIs, noinline paths, and linker-section objects.

Risks and test signals: Risks include applying attributes to the wrong entity, depending on attributes that are empty on one compiler, marking ERR_PTR-returning functions as aligned, or losing format/no-return diagnostics. Test signals include GCC and Clang builds, W=1/W=2 warning checks, sparse builds, ABI-sensitive struct layout tests, and negative tests for compile-time error/warning wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler_attributes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler_types.h -->
## sources/distributed-fs/ceph-client/include/linux/compiler_types.h

Purpose: This is the central compiler type and attribute plumbing header. It defines address-space annotations, BTF tags, inline semantics, sanitizer-aware inlining, randomization annotations, object-size helpers, compile-time assertions, diagnostics, and compiler selection.

Important APIs, types, and functions: Early macros include fallback `__has_builtin`, `__PASTE`, and pre-C23 `auto` as `__auto_type`. Sparse address spaces define `__user`, `__iomem`, `__percpu`, `__rcu`, `__force`, `__nocast`, `__private`, and pointer check stubs. Kernel attributes include `__function_aligned`, `__cold`, `__preserve_most`, `__retain`, compiler-specific includes, `struct ftrace_branch_data`, `struct ftrace_likely_data`, `notrace`, `__naked`, the kernel `inline` definition, `noinline_for_stack`, sanitizer helpers (`__no_kasan_or_inline`, `__no_kcsan`, `__no_sanitize_or_inline`), `__data_racy`, `__assume`, `__counted_by`, `__counted_by_ptr`, endian-specific counted-by wrappers, `at_least`, `noinstr`, and `__cpuidle`. Later helpers include randstruct annotations, `__nocfi`, `__alloc_size`, `__realloc_size`, `__struct_size`, `__member_size`, `__annotated`, `__flex_counter`, `asm_goto_output`, assembly constraint defaults, `asm_inline`, `__same_type`, scalar type unqualification/sign conversion, `compiletime_assert`, `compiletime_assert_atomic_type`, and diagnostic push/pop/ignore wrappers.

Control flow: This header branches heavily at compile time over sparse, bindgen, Kconfig, compiler identity, sanitizer predefines, and architecture config. Runtime code is only created indirectly by macros such as instrumentation records or noinline/noinstr sections; otherwise it controls generated code shape.

State and persistence: Persistent effects include BTF annotation, struct randomization, counted flexible-array metadata, ftrace branch records, sanitizer exclusion, CFI exclusions, retained sections, and atomicity assertions. It defines the type-level contract for user, I/O, per-CPU, and RCU pointers.

Dependencies and integration points: It integrates with `compiler-context-analysis.h`, `compiler_attributes.h`, `compiler-clang.h` or `compiler-gcc.h`, optional `asm/compiler.h`, BTF, sparse, randstruct, CFI, KASAN/KCSAN/KMSAN/KCOV, FORTIFY, UBSAN bounds, objtool noinstr validation, and build warning controls.

Risks and test signals: Risks include inconsistent attributes across translation units, invalid inline semantics with tracing, sanitizer instrumentation leaking into noinstr paths, counted-by compiler bugs, and address-space annotations being bypassed with `__force`. Test signals are sparse, bindgen, BTF, randstruct, CFI, sanitizer, allmodconfig, and objtool noinstr test builds across GCC and Clang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/compiler_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/completion.h -->
## sources/distributed-fs/ceph-client/include/linux/completion.h

Purpose: This header declares the kernel completion synchronization primitive: a one-shot or reusable event object used to block tasks until another context signals completion.

Important APIs, types, and functions: `struct completion` contains a `done` counter and an `swait_queue_head`. Initializers include `COMPLETION_INITIALIZER`, `DECLARE_COMPLETION`, `DECLARE_COMPLETION_ONSTACK`, and lockdep-aware map variants. `init_completion()` initializes dynamically allocated completions, and `reinit_completion()` resets only `done` for reuse. Wait APIs include `wait_for_completion`, `_io`, `_interruptible`, `_killable`, `_state`, timeout variants, `try_wait_for_completion`, and `completion_done`. Signal APIs include `complete`, `complete_on_current_cpu`, and `complete_all`.

Control flow: Waiters enqueue on the simple wait queue when `done` is zero. Signallers increment or saturate `done` and wake waiters. `complete_all()` wakes all waiters and leaves the object in a completed state until `reinit_completion()` resets it. On-stack completion macros use runtime initialization under lockdep.

State and persistence: Completion state is entirely in `done` and the wait queue. It is in-memory synchronization state and is not persistent across object lifetime. Reinitialization intentionally keeps the wait queue intact, so it must not be used while unknown waiters remain.

Dependencies and integration points: It depends on `linux/swait.h`, scheduler wait/wake implementation, lockdep annotations, and callers throughout drivers, filesystems, and async kernel flows.

Risks and test signals: Risks include reinitializing while waiters are active, missing `complete()` on error paths, assuming `completion_done()` is a strong synchronization check, and using a normal initializer for stack objects under lockdep. Test signals are timeout tests, interruptible wait tests, `complete_all()` reuse tests, lockdep runs, and teardown paths that verify no blocked waiters remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/completion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/component.h -->
## sources/distributed-fs/ceph-client/include/linux/component.h

Purpose: This header declares the component framework used by aggregate drivers that bind only after a set of component devices is present. It is common in graphics/display pipelines and other multi-device drivers.

Important APIs, types, and functions: `struct component_ops` supplies component `bind` and `unbind` callbacks. Components register through `component_add()` or `component_add_typed()` and unregister through `component_del()`. Aggregate drivers provide `struct component_master_ops` with `bind` and `unbind`, register using `component_master_add_with_match()`, and unregister with `component_master_del()`. Match construction uses `component_match_add_release()`, `component_match_add_typed()`, and the convenience `component_match_add()`. Compare helpers include `component_compare_of`, `component_release_of`, `component_compare_dev`, and `component_compare_dev_name`. `component_bind_all()` and `component_unbind_all()` bind/unbind all matched components for a parent.

Control flow: Components register independently. An aggregate driver builds a match list and registers a master. When every required component matches, the framework calls the master `bind`, which typically allocates aggregate state, calls `component_bind_all()`, and registers the combined subsystem interface. Unregistration of the master or any component triggers master `unbind` and component unbinding.

State and persistence: Framework state is maintained in private match/component lists outside the header. Driver private aggregate state must be manually allocated and freed because its lifetime does not align with a single device; the comments explicitly warn against devm-managed aggregate resources in master bind/unbind.

Dependencies and integration points: It depends on `struct device`, OF/device matching, devm release actions for match lists, and subsystem-specific aggregate registration code.

Risks and test signals: Risks include resource lifetime leaks, partial bind rollback failures, mismatched typed vs untyped components, and unbind ordering bugs. Test signals include deferred-probe scenarios, component hot-unplug, failed component bind injection, repeated module load/unload, and aggregate driver cleanup verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/component.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/configfs.h -->
## sources/distributed-fs/ceph-client/include/linux/configfs.h

Purpose: This header defines the in-kernel configfs object model, allowing userspace to instantiate and configure kernel objects through a filesystem hierarchy.

Important APIs, types, and functions: Core types are `struct config_item`, `struct config_item_type`, `struct config_group`, `struct configfs_attribute`, `struct configfs_bin_attribute`, `struct configfs_item_operations`, `struct configfs_group_operations`, and `struct configfs_subsystem`. Item APIs include `config_item_set_name`, `config_item_name`, `config_item_init_type_name`, `config_item_get`, `config_item_get_unless_zero`, and `config_item_put`. Group APIs include `config_group_init`, `config_group_init_type_name`, `to_config_group`, `config_group_get`, `config_group_put`, `config_group_find_item`, and `configfs_add_default_group`. Attribute macros create read/write, read-only, write-only, and binary attributes. Registration APIs cover subsystems, groups, default groups, default removal, and dependency pinning.

Control flow: A subsystem registers a root `config_group`. Userspace mkdir operations call group `make_group` or `make_item`; rmdir/drop operations call `drop_item` and item release paths after reference counts drain. Attribute reads/writes call the configured `show`, `store`, `read`, or `write` callbacks. Links are controlled by `allow_link` and `drop_link`.

State and persistence: Runtime state is embodied by config items, krefs, dentries, group child lists, default group lists, and subsystem mutexes. Configfs state persists while objects are referenced from the filesystem and kernel users; it is not durable storage. Dependency APIs pin target items to prevent removal during dependent operations.

Dependencies and integration points: It depends on krefs, dentries, lists, mutexes, modules, VFS/configfs core, and caller-defined object lifecycles. It is often used by storage, target, USB gadget, and subsystem configuration code.

Risks and test signals: Risks are reference-count leaks, destructor misuse, calling dependency APIs from forbidden contexts, exposing writable attributes without validation, default group cleanup races, and using too-short names beyond `CONFIGFS_ITEM_NAME_LEN` expectations. Test signals include mount/unmount, mkdir/rmdir/link/unlink stress, attribute fuzzing, module unload under open files, and lockdep around subsystem mutexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/configfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/connector.h -->
## sources/distributed-fs/ceph-client/include/linux/connector.h

Purpose: This header declares the connector core interface, a netlink-based mechanism for in-kernel producers/consumers to exchange structured messages with userspace or registered callbacks.

Important APIs, types, and functions: `struct cn_queue_dev` represents a callback queue device with refcount, queue list/lock, name, and netlink socket. `struct cn_callback_id` combines a symbolic name with `struct cb_id`. `struct cn_callback_entry` stores callback list membership, refcount, device, ID, callback function, sequence, and group. `struct cn_dev` captures connector device ID, sequence, groups, socket, and queue device. Public APIs include `cn_add_callback`, `cn_del_callback`, `cn_netlink_send_mult`, `cn_netlink_send`, queue add/delete/release, queue allocation/free, and `cn_cb_equal`.

Control flow: Kernel users register callbacks by unique connector IDs. Incoming netlink messages are matched to callback entries, invoking the callback with `struct cn_msg` and netlink sender credentials. Outgoing messages use `cn_netlink_send()` or `_mult()` to deliver by port ID or multicast group; if both destination fields are zero, the core finds the group associated with the message ID.

State and persistence: Connector runtime state includes registered callback entries, queue lists, sequence counters, multicast group assignments, netlink sockets, and refcounts. State lasts until callbacks and queues are explicitly removed.

Dependencies and integration points: It depends on `linux/refcount.h`, lists, workqueues, netlink sockets, `netlink_filter_fn`, and UAPI connector message definitions. Integration points are kernel subsystems that need low-volume event/control messages over netlink.

Risks and test signals: Risks include callback ID collisions, silent send failure under memory pressure, use-after-free if callback refs are mishandled, group routing mistakes, and softirq-context allocation constraints. Test signals include registering duplicate IDs, netlink listener absence returning `-ESRCH`, filtered multicast delivery, module unload while callbacks are active, and memory pressure send tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/connector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/console.h -->
## sources/distributed-fs/ceph-client/include/linux/console.h

Purpose: This header declares virtual console switch operations, printk console descriptors, console registration and locking APIs, and the newer non-blocking console (nbcon) ownership contract.

Important APIs, types, and functions: `struct consw` contains virtual terminal rendering callbacks such as startup, init/deinit, clear, putc/putcs, cursor, scroll, switch, blank, font set/get/default, resize, palette, scroll delta, origin, screen save, attribute build, and invert region. `enum cons_flags` defines console state such as `CON_ENABLED`, `CON_BOOT`, `CON_SUSPENDED`, `CON_NBCON`, and `CON_NBCON_ATOMIC_UNSAFE`. nbcon types include `struct nbcon_state`, `enum nbcon_prio`, `struct nbcon_context`, and `struct nbcon_write_context`. `struct console` includes legacy write/read/device callbacks, setup/exit/match, sequence/dropped counters, list node, nbcon callbacks (`write_atomic`, `write_thread`, `device_lock`, `device_unlock`), nbcon atomic state, sequence, previous sequence, buffers, kthread, rcuwait, and IRQ work. Public APIs include console list locking/SRCU, registration, unregister, suspend/resume, panic flush, preferred console selection, braille registration, sysfs notification, and nbcon unsafe/takeover helpers.

Control flow: Console drivers register `struct console` instances, are added to a global hlist, and are iterated either under `console_list_lock()` or SRCU. Printk decides usability with `console_is_usable()` by checking enabled/suspended state, callback availability, nbcon atomic safety, unsafe takeover policy, and CPU online status. nbcon write callbacks run only after ownership is acquired; atomic writers must mark unsafe hardware regions and back out if ownership is lost. Threaded writers run in task context under device lock plus nbcon ownership.

State and persistence: Persistent runtime state includes console flags, sequence numbers, dropped counts, registration list membership, nbcon atomic ownership, per-console buffers, printer kthreads, and SRCU/list synchronization. Flag reads/writes use `READ_ONCE`/`WRITE_ONCE` under the correct locks.

Dependencies and integration points: It integrates with printk ringbuffer, tty, VT console switching, lockdep, SRCU, IRQ work, CPU hotplug, braille, sysfs, panic/oops paths, and architecture early consoles.

Risks and test signals: Risks include writing flags without list lock, iterating without SRCU/list lock, using nbcon callbacks after ownership loss, unsafe atomic takeover freezing hardware, missing migration disable in `device_lock`, and printing on offline CPUs without `CON_ANYTIME`. Test signals include lockdep, panic/oops console output, CPU hotplug, console suspend/resume, nbcon threaded and atomic paths, and repeated register/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/console.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/console_struct.h -->
## sources/distributed-fs/ceph-client/include/linux/console_struct.h

Purpose: This header defines virtual console data structures used by the VT layer, excluding implementation details in `vt.c`.

Important APIs, types, and functions: `enum vc_intensity` encodes half-bright, normal, and bold intensity. `struct vc_state` captures cursor position, color, charset selection, intensity, italic, underline, blink, and reverse flags. `struct vc_font` describes glyph width, height, count, and bitmap data; helpers `vc_font_pitch()` and `vc_font_size()` operate on it. `struct vc_data` is the main virtual console state, including tty port, saved/current states, dimensions, screen buffer addresses, scroll region, driver switch pointer, colors, cursor fields, font state, escape-parser fields, VT switching state, wait queues, mode flags, UTF-8 decoding, tab bitmap, palette, translation table, bell timing, foreground display pointer, Unicode mapping, and saved screen copies. `struct vc` wraps `vc_data` plus SAK work. Cursor encoding macros define shape, colors, and mode changes.

Control flow: The VT core mutates `vc_data` as bytes are parsed, screen regions scroll, console drivers render characters, fonts or palettes change, and VT switching saves/restores state. Low-level drivers are expected to populate fields marked by comments and may update origin fields for fast scrolling.

State and persistence: This header is almost entirely state layout. `vc_screenbuf`, Unicode lines, font pointers, palette, cursor state, escape parser state, and saved screen buffers persist for each virtual console until console teardown. `vc_cons[MAX_NR_CONSOLES]` is the global virtual console array.

Dependencies and integration points: It depends on VT UAPI definitions, wait queues, workqueues, tty ports, bitmaps, Unicode page dictionaries, `struct consw`, and console translation code.

Risks and test signals: Risks include corrupt screen-buffer pointer arithmetic, inconsistent character/attribute cell sizing, font pitch miscalculation, UTF-8 parser state corruption, and races in VT switching or SAK work. Test signals include VT switching, font load/ioctl tests, scrollback, Unicode rendering, tab stops, palette changes, and lockdep around console locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/console_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/consolemap.h -->
## sources/distributed-fs/ceph-client/include/linux/consolemap.h

Purpose: This header declares character translation helpers between VT console glyph maps, Unicode, and 8-bit encodings.

Important APIs, types, and functions: `enum translation_map` names `LAT1_MAP`, `GRAF_MAP`, `IBMPC_MAP`, and `USER_MAP`. Under `CONFIG_CONSOLE_TRANSLATIONS`, it exports `inverse_translate`, `set_translate`, `conv_uni_to_pc`, `conv_8bit_to_uni`, `conv_uni_to_8bit`, `console_map_init`, `ucs_is_double_width`, `ucs_is_zero_width`, `ucs_recompose`, and `ucs_get_fallback`. Disabled builds provide inline fallbacks that mostly return the glyph/input, reject code points above 0xff for PC glyph conversion, and report no width/recomposition/fallback metadata.

Control flow: The VT layer calls translation helpers while rendering or interpreting console bytes. The enabled path consults translation maps and Unicode tables; disabled paths bypass conversion.

State and persistence: Translation tables and user maps are implemented elsewhere. This header exposes no state directly, but `set_translate()` can return or install a per-VC translation table.

Dependencies and integration points: It depends on `struct vc_data`, `linux/types.h`, VT rendering, selection, and consolemap implementation.

Risks and test signals: Risks include incorrect glyph-to-Unicode mapping, missing double-width or zero-width handling, broken combining recomposition, and behavior divergence when translations are disabled. Test signals include Unicode console rendering, 8-bit charset tests, user map ioctls, width/fallback table tests, and builds with `CONFIG_CONSOLE_TRANSLATIONS=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/consolemap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/const.h -->
## sources/distributed-fs/ceph-client/include/linux/const.h

Purpose: This wrapper exposes VDSO constant macros through the normal Linux include path.

Important APIs, types, and functions: The file only includes `<vdso/const.h>` behind `_LINUX_CONST_H`.

Control flow: There is no runtime or compile-time decision beyond the include guard.

State and persistence: No state is declared. Any constant behavior is inherited from the VDSO header.

Dependencies and integration points: It integrates kernel code with VDSO-safe constant expression definitions, allowing shared constant macros to be reused.

Risks and test signals: Risks are limited to include-path breakage or VDSO constant macro changes. Test signals are compile coverage for kernel and VDSO consumers and ensuring the wrapper remains side-effect free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/const.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/container.h -->
## sources/distributed-fs/ceph-client/include/linux/container.h

Purpose: This header defines the container bus device wrapper used by the base power/container subsystem.

Important APIs, types, and functions: It declares `extern const struct bus_type container_subsys`. `struct container_dev` embeds `struct device dev` and optional `offline(struct container_dev *)` callback. `to_container_dev(struct device *dev)` converts an embedded device pointer to the enclosing container device using `container_of`.

Control flow: Drivers or subsystem code use `to_container_dev()` after receiving a generic `struct device`. The `offline` callback, when present, is invoked by implementation code to offline a container.

State and persistence: State is the embedded `struct device` plus callback pointer; lifetime follows device-model registration. No state is stored in this header.

Dependencies and integration points: It depends on `linux/device.h`, the driver core bus model, and `drivers/base/power/container.c`.

Risks and test signals: Risks include applying `to_container_dev()` to a non-container device, stale callback pointers after unregister, and incorrect offline handling. Test signals include container bus registration, device hotplug, offline callback error propagation, and driver-core lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/container.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/container_of.h -->
## sources/distributed-fs/ceph-client/include/linux/container_of.h

Purpose: This header provides the canonical kernel macros to recover an enclosing structure from a pointer to one of its members.

Important APIs, types, and functions: `typeof_member(T, m)` obtains the type of a member. `container_of(ptr, type, member)` checks that the pointer type matches the member type or is void, then subtracts `offsetof(type, member)` from the member pointer. `container_of_const(ptr, type, member)` wraps `container_of()` with `_Generic` to preserve `const` qualification.

Control flow: The macros expand inline at compile time. `container_of()` creates a temporary `void *__mptr`, performs a static type assertion, and returns the calculated enclosing pointer. `container_of_const()` selects const or non-const return type based on the pointer expression.

State and persistence: No state is stored. The macro is pointer arithmetic over in-memory object layout and depends on the member truly being embedded in the target structure.

Dependencies and integration points: It depends on `build_bug.h`, `stddef.h`, `offsetof`, `static_assert`, and `__same_type`. It is used across almost every subsystem for embedded object models.

Risks and test signals: Risks include losing constness with plain `container_of`, passing a pointer not actually embedded in the claimed type, or using stale member pointers after object lifetime ends. Test signals are compile-time type mismatch failures, const-correctness warnings, KASAN use-after-free reports, and migration of new code to `container_of_const()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/container_of.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/context_tracking.h -->
## sources/distributed-fs/ceph-client/include/linux/context_tracking.h

Purpose: This header declares context tracking transitions for user, guest, exception, idle, IRQ warning, and RCU watching state. It supports nohz/RCU/vtime accounting around extended quiescent states.

Important APIs, types, and functions: User tracking exports `ct_cpu_track_user`, `__ct_user_enter`, `__ct_user_exit`, `ct_user_enter`, `ct_user_exit`, `user_enter_callable`, and `user_exit_callable`. Inline wrappers `user_enter`, `user_exit`, `user_enter_irqoff`, and `user_exit_irqoff` gate calls on `context_tracking_enabled()`. `exception_enter()` and `exception_exit()` transition out of non-kernel state for exceptions unless off-stack tracking is enabled. Guest helpers enter/exit `CT_STATE_GUEST`. Idle tracking declares `ct_idle_enter`, `ct_idle_exit`, `rcu_is_watching_curr_cpu`, `ct_state_inc`, `warn_rcu_enter`, and `warn_rcu_exit`.

Control flow: Architecture entry/exit code calls the wrappers on transitions between kernel, user, guest, idle, IRQ, and exception contexts. The wrappers avoid overhead when context tracking is disabled. Warning helpers temporarily make RCU appear watching while reporting recursive RCU-not-watching conditions.

State and persistence: State lives in per-CPU `context_tracking` from `context_tracking_state.h`, including active flag, recursion, atomic state, and nesting counters. Updates are per-CPU and generally require interrupts/preemption constraints appropriate to the path.

Dependencies and integration points: It depends on scheduler state, vtime, instrumentation controls, `asm/ptrace.h`, RCU dynticks, nohz full, KVM guest transitions, exception entry code, and idle/IRQ tracking.

Risks and test signals: Risks include missing entry/exit pairs, calling IRQ-off variants with interrupts enabled, corrupting RCU watching bits, and recursion during warning paths. Test signals include nohz full workloads, RCU stall tests, KVM guest entry/exit, idle loop tests, context tracking selftests, and lockdep/RCU debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/context_tracking.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/context_tracking_irq.h -->
## sources/distributed-fs/ceph-client/include/linux/context_tracking_irq.h

Purpose: This small header declares IRQ and NMI context-tracking hooks.

Important APIs, types, and functions: Under `CONFIG_CONTEXT_TRACKING_IDLE`, it declares `ct_irq_enter`, `ct_irq_exit`, `ct_irq_enter_irqson`, `ct_irq_exit_irqson`, `ct_nmi_enter`, and `ct_nmi_exit`. Disabled builds provide no-op inline stubs.

Control flow: Low-level IRQ/NMI entry code calls enter hooks before handling an interrupt and exit hooks afterward. The `_irqson` variants are for contexts where interrupts are enabled. NMI hooks track nesting separately from regular IRQs.

State and persistence: The hooks update per-CPU context tracking nesting/state in implementation files; this header stores no state.

Dependencies and integration points: It integrates with architecture IRQ/NMI entry code, RCU idle tracking, and `context_tracking_state.h`.

Risks and test signals: Risks include unbalanced enter/exit pairs, using the wrong IRQ-enabled variant, and nesting counter corruption in NMI paths. Test signals are IRQ storm tests, NMI watchdog paths, RCU idle debug, lockdep entry instrumentation, and disabled-config compile tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/context_tracking_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/context_tracking_state.h -->
## sources/distributed-fs/ceph-client/include/linux/context_tracking_state.h

Purpose: This header defines the per-CPU context tracking data layout, state encoding, and inline readers used by RCU, nohz, and entry code.

Important APIs, types, and functions: `CT_NESTING_IRQ_NONIDLE` distinguishes IRQ vs task idle transitions. `enum ctx_state` defines disabled, kernel, idle, user, guest, and max values. `struct context_tracking` contains `active` and `recursion` for user tracking, atomic `state` for context/RCU watching bits, and idle/NMI nesting counters. Bit layout macros define `CT_STATE_WIDTH`, `CT_RCU_WATCHING_WIDTH`, masks, start/end positions, and `CT_RCU_WATCHING`. Readers include `__ct_state`, `ct_rcu_watching`, `ct_rcu_watching_cpu`, `ct_rcu_watching_cpu_acquire`, `ct_nesting`, `ct_nesting_cpu`, `ct_nmi_nesting`, `ct_nmi_nesting_cpu`, `context_tracking_enabled`, `context_tracking_enabled_cpu`, `context_tracking_enabled_this_cpu`, and `ct_state`.

Control flow: Callers sample per-CPU state using raw or acquire atomics depending on ordering needs. `ct_state()` disables preemption while reading current CPU state. Static key `context_tracking_key` eliminates overhead when user tracking is off.

State and persistence: The persistent runtime state is per-CPU `struct context_tracking`. Its atomic `state` packs low bits for context state and higher bits for RCU watching generation/counter state. Idle and NMI nesting fields track transition depth.

Dependencies and integration points: It depends on percpu APIs, static keys, bit macros, atomics, RCU dynticks torture sizing, and IRQ tracking declarations.

Risks and test signals: Risks include bitfield width mistakes, missing acquire ordering when observing remote CPUs, reading current CPU state with preemption enabled, and static-key mismatch with per-CPU active flags. Test signals include compile-time static assertions, RCU torture, nohz full, CPU hotplug, preemption debug, and remote CPU watching checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/context_tracking_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cookie.h -->
## sources/distributed-fs/ceph-client/include/linux/cookie.h

Purpose: This header defines a fast monotonically unique-ish cookie generator with per-CPU batching and recursion handling.

Important APIs, types, and functions: `struct pcpu_gen_cookie` stores per-CPU nesting and last value, aligned to 16 bytes. `struct gen_cookie` stores a per-CPU local pointer plus atomic forward and reverse counters. `COOKIE_LOCAL_BATCH` is 4096. `DEFINE_COOKIE(name)` creates per-CPU local storage and a `struct gen_cookie`. `gen_cookie_next(struct gen_cookie *gc)` returns the next cookie.

Control flow: On non-recursive calls, `gen_cookie_next()` increments local nesting, uses the per-CPU cached `last`, and periodically reserves a forward batch from `forward_last` on SMP when the local low bits reach a batch boundary. Recursive calls avoid corrupting the local forward stream by decrementing `reverse_last` atomically and returning negative/reverse-space values. Nesting is decremented before return.

State and persistence: State is in per-CPU `last`/`nesting` and two global atomic64 counters. Cookies persist only as values handed to callers; generator state persists for the lifetime of the static `gen_cookie` object.

Dependencies and integration points: It depends on local atomics, percpu storage, `atomic64_t`, `likely/unlikely`, and `CONFIG_SMP`.

Risks and test signals: Risks include recursion returning values from a different range than callers expect, overflow after long runtimes, per-CPU batch misuse on CPU hotplug, and assuming strict global monotonicity across CPUs. Test signals include concurrent generation stress, recursive generation tests, SMP and UP builds, uniqueness checks, and wraparound reasoning in long-duration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cookie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cordic.h -->
## sources/distributed-fs/ceph-client/include/linux/cordic.h

Purpose: This header declares a fixed-point CORDIC helper for computing sine/cosine-like I/Q coordinates without floating point.

Important APIs, types, and functions: Constants include `CORDIC_ANGLE_GEN`, `CORDIC_PRECISION_SHIFT` at 16, and `CORDIC_NUM_ITER`. `CORDIC_FIXED(X)` converts an integer to fixed point, while `CORDIC_FLOAT(X)` rounds fixed point back toward integer representation. `struct cordic_iq` holds signed 32-bit in-phase (`i`) and quadrature (`q`) coordinates. `cordic_calc_iq(s32 theta)` computes I/Q for an angle in degrees.

Control flow: Implementation code normalizes input angle to the supported range and iteratively applies CORDIC rotations for `CORDIC_NUM_ITER` steps. The header exposes the fixed-point scaling contract.

State and persistence: No state is stored. Results are pure values derived from the input angle.

Dependencies and integration points: It depends on `linux/types.h` and is used by drivers needing trigonometric values in kernel space, especially wireless/radio code where floating point is unavailable.

Risks and test signals: Risks include fixed-point overflow, rounding surprises in `CORDIC_FLOAT`, angle normalization errors outside -180..180 degrees, and precision regressions from constant changes. Test signals include known-angle checks for 0, 90, 180, -90 degrees; out-of-range angle normalization; and comparison against high-precision reference values within expected error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cordic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/coreboot.h -->
## sources/distributed-fs/ceph-client/include/linux/coreboot.h

Purpose: This header defines coreboot table structures and helpers used by Linux drivers to consume firmware-provided coreboot metadata.

Important APIs, types, and functions: `cb_u64` is a 4-byte-aligned 64-bit type matching table layout. Tags include `CB_TAG_FRAMEBUFFER` and `LB_TAG_CBMEM_ENTRY`. Structures include `coreboot_table_entry`, `lb_cbmem_ref`, `lb_cbmem_entry`, and `lb_framebuffer`. Framebuffer orientation constants cover normal, bottom-up, left-up, and right-up. `LB_FRAMEBUFFER_HAS_LFB(fb)` and `LB_FRAMEBUFFER_HAS_ORIENTATION(fb)` use `offsetofend` to check whether a variable-sized framebuffer table is large enough to include fields.

Control flow: Consumers parse coreboot table entries by tag and size, then cast to the matching structure only after checking size for optional fields. Framebuffer consumers use the helper macros before reading linear framebuffer or orientation data.

State and persistence: The header maps firmware table bytes; it declares no mutable state. The persistent data is firmware-provided memory made available during boot/platform probing.

Dependencies and integration points: It depends on compiler alignment attributes, `stddef.h`, types, coreboot table scanning, framebuffer/simplefb setup, and platform drivers for CBMEM.

Risks and test signals: Risks include unaligned 64-bit access, reading optional fields when `size` is too small, tag mismatch, and endian/layout assumptions. Test signals include booting on coreboot hardware, fuzzing/truncating table entries, framebuffer orientation tests, and alignment-sensitive architecture builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/coreboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/coredump.h -->
## sources/distributed-fs/ceph-client/include/linux/coredump.h

Purpose: This header declares coredump parameters and helper functions used to emit process core files safely and consistently.

Important APIs, types, and functions: Under `CONFIG_COREDUMP`, `struct core_vma_metadata` stores VMA start/end, flags, dump size, page offset, and backing file. `struct coredump_params` tracks signal info, output file, limit, mm flags, CPU, written byte count, file position, deferred skip amount, VMA count/data size, VMA metadata array, and pid. Helpers include `dump_skip_to`, `dump_skip`, `dump_emit`, `dump_align`, `dump_user_range`, and `vfs_coredump`. `core_file_note_size_limit` bounds note size. Logging macros `coredump_report` and `coredump_report_failure` add TGID and comm to ratelimited printk output. `validate_coredump_safety()` exists when sysctl support is present.

Control flow: Signal/exit code invokes `vfs_coredump()`, which fills `coredump_params` and format-specific dumpers use only the dump helpers to advance, align, skip, and emit file data. Logging macros report policy or write failures. Disabled builds stub out coredump behavior.

State and persistence: Coredump state persists during dump generation in `coredump_params` and output file contents. It serializes memory and VMA metadata to storage subject to resource limits.

Dependencies and integration points: It depends on mm, fs, signal info, current task identity, printk, sysctl, ELF/binfmt coredump implementations, and filesystem write paths.

Risks and test signals: Risks include exceeding dump limits, leaking sensitive mappings, incorrect skip/position accounting, partial writes, and unsafe coredump sysctl combinations. Test signals include coredump generation for sparse VMAs, file-backed mappings, RLIMIT_CORE, huge processes, failing filesystems, disabled config, and sysctl safety validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/coresight-pmu.h -->
## sources/distributed-fs/ceph-client/include/linux/coresight-pmu.h

Purpose: This header defines CoreSight ETM PMU naming and trace-ID encoding used by perf AUX hardware ID records.

Important APIs, types, and functions: `CORESIGHT_ETM_PMU_NAME` names the PMU as `cs_etm`. `CORESIGHT_LEGACY_CPU_TRACE_ID(cpu)` computes the historical per-CPU trace ID. AUX hardware ID masks include trace ID, sink ID, minor version, and major version fields. Version constants define major 0 and minor 1.

Control flow: Perf/CoreSight code packs and unpacks `PERF_RECORD_AUX_OUTPUT_HW_ID` payloads using the masks. Compatibility code may use the legacy CPU-to-trace-ID calculation for older kernels or tools.

State and persistence: Encoded AUX records persist in perf data files. The header stores no state but defines file-format interpretation bits.

Dependencies and integration points: It depends on bit mask helpers and integrates with perf tooling, CoreSight ETM drivers, sysfs sink IDs, and trace decoders.

Risks and test signals: Risks include breaking perf data compatibility, overlapping mask fields, wrong version interpretation, and legacy trace-ID mismatch. Test signals include perf record/report with CoreSight ETM, older-tool compatibility, sink ID decoding, and bitfield unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/coresight-pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/coresight-stm.h -->
## sources/distributed-fs/ceph-client/include/linux/coresight-stm.h

Purpose: This header is a kernel include wrapper for the CoreSight STM UAPI definitions.

Important APIs, types, and functions: It includes `<uapi/linux/coresight-stm.h>` and defines only its include guard.

Control flow: There is no control flow.

State and persistence: No state is declared in this wrapper; STM user/kernel ABI details live in the UAPI header.

Dependencies and integration points: It bridges in-kernel CoreSight STM users with the exported UAPI definitions.

Risks and test signals: Risks are limited to include ordering or UAPI drift. Test signals are CoreSight STM builds and user ABI compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/coresight-stm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/coresight.h -->
## sources/distributed-fs/ceph-client/include/linux/coresight.h

Purpose: This header defines the CoreSight framework's device model, topology descriptions, operation callbacks, register access helpers, mode arbitration, and registration APIs.

Important APIs, types, and functions: It defines CoreSight ID register offsets and unlock constants, `coresight_bustype`, device type/subtype enums, `union coresight_dev_subtype`, `struct coresight_platform_data`, `struct csdev_access`, `CSDEV_ACCESS_IOMEM`, `struct coresight_desc`, `struct coresight_connection`, `struct coresight_sysfs_link`, `struct coresight_trace_id_map`, `struct coresight_device`, `struct coresight_dev_list`, `struct coresight_path`, and `enum cs_mode`. Ops structures cover sinks, links, sources, helpers, panic sync, and the aggregate `struct coresight_ops`. Inline accessors include 32-bit and 64-bit relaxed/non-relaxed reads/writes, pair reads/writes, CID/PID extraction, source/sink predicates, and mode helpers `coresight_take_mode`, `coresight_get_mode`, and `coresight_set_mode`. Registration/control APIs include `coresight_register`, `coresight_unregister`, sysfs enable/disable, timeout helpers, claim/disclaim APIs, device naming, context-loss query, access wrappers, CPU/static trace ID lookup, platform data parsing, connection add/find helpers, driver init/remove, ETM trace ID, and clock enable lookup.

Control flow: Drivers provide a `coresight_desc` with type, subtype, ops, platform topology, and access method. The framework registers a `coresight_device`, builds sysfs connection links, arbitrates mode between disabled/sysfs/perf with atomic acquire/release operations, enables paths source-to-sink through source/link/sink/helper callbacks, and performs register I/O through either memory-mapped accessors or supplied read/write callbacks.

State and persistence: Persistent runtime state includes topology connection arrays, sysfs links, atomic mode, refcount, orphan flag, sink activation/default sink, trace ID maps with per-CPU atomics and spinlock, feature/config lists, active config context, and device model state.

Dependencies and integration points: It depends on AMBA, platform devices, clocks, perf events, sched, device/fwnode topology, MMIO, sysfs, CoreSight config frameworks, and ETM/trace sink drivers.

Risks and test signals: Risks include mode races between sysfs and perf, refcount access outside required locks, orphan topology links, incorrect relaxed vs ordered MMIO, 64-bit access on 32-bit builds, trace ID collisions, and duplicated claim declarations. Test signals include CoreSight topology probing, perf sessions, sysfs enable/disable, concurrent perf/sysfs attempts, hotplug/unbind, timeout paths, trace ID allocation, and lockdep around framework mutexes/spinlocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/coresight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/count_zeros.h -->
## sources/distributed-fs/ceph-client/include/linux/count_zeros.h

Purpose: This header provides small helpers to count leading and trailing zero bits in an `unsigned long`.

Important APIs, types, and functions: `count_leading_zeros(unsigned long x)` returns the number of zero bits from the most significant bit toward the least significant bit, using `fls()` for 32-bit longs and `fls64()` otherwise. `count_trailing_zeros(unsigned long x)` returns `__ffs(x)` for nonzero values or `BITS_PER_LONG` for zero.

Control flow: Both functions branch only on word size or zero input. The zero case is explicitly defined for both functions as `BITS_PER_LONG`.

State and persistence: No state is stored; functions are pure bit operations.

Dependencies and integration points: It depends on architecture bitops for `fls`, `fls64`, `__ffs`, and `BITS_PER_LONG`. It is useful in algorithms needing normalized bit positions without duplicating zero handling.

Risks and test signals: Risks include architecture bitops with undefined zero behavior, accidental type widening, and confusion between 32-bit and 64-bit long widths. Test signals include values 0, 1, MSB-only, all ones, and randomized comparisons against compiler builtins on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/count_zeros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/counter.h -->
## sources/distributed-fs/ceph-client/include/linux/counter.h

Purpose: This header defines the kernel Counter subsystem driver interface for devices that expose counts, signals, synapses, component extensions, and event streams through a character device/UAPI.

Important APIs, types, and functions: `enum counter_comp_type` classifies component data such as integers, booleans, signal levels, functions, synapse actions, enums, count modes, polarity, and arrays. `struct counter_comp` describes an extension with name, type, private data, and unions of read/write callbacks for device/count/signal scopes and scalar/array types. `struct counter_signal`, `struct counter_synapse`, and `struct counter_count` model the hardware graph. `struct counter_event_node` stores watched events and component lists. `struct counter_ops` declares driver callbacks for signal, count, function, action, event configuration, and watch validation. `struct counter_device` stores public driver descriptors plus internal device, cdev, event lists/locks, kfifo, wait queue, and ops-existence mutex. Lifecycle APIs include `counter_alloc`, `counter_put`, `counter_add`, `counter_unregister`, `devm_counter_alloc`, `devm_counter_add`, `counter_priv`, and `counter_push_event`. Numerous `COUNTER_COMP_*` and `DEFINE_COUNTER_*` macros initialize common extensions, enum availability, and arrays.

Control flow: A driver allocates a `counter_device`, fills signals/counts/extensions and ops, then calls `counter_add()` or devm equivalent. Userspace reads/writes component attributes or configures watches through subsystem code that dispatches to the matching callback union member. Driver hardware events call `counter_push_event()`, enqueueing a UAPI event and waking blocking readers. Event configuration uses current and next event lists protected by spinlocks/mutexes.

State and persistence: State persists in the registered device model object, cdev, arrays supplied by the driver, event watch lists, event kfifo, wait queue, and locks. Hardware count state lives in the device and is exposed through callbacks; extension `priv` pointers can reference static availability metadata.

Dependencies and integration points: It depends on UAPI counter definitions, cdev/device core, kfifo, wait queues, locks, and driver-specific hardware implementations.

Risks and test signals: Risks include mismatching `counter_comp_type` with the wrong callback union member, stale driver arrays after registration, missing `ops_exist_lock` protection during removal, event FIFO overflow, invalid watch acceptance, and macro-created components with NULL writes where users expect writability. Test signals include counter character device reads/writes, event watch configuration, blocking event reads, device removal during I/O, devm cleanup, enum/array component validation, and UAPI ABI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/counter.h -->
