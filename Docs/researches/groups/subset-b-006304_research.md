<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_user.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_user.c

## Purpose
Implements the NETLINK_XFRM userspace control plane for the kernel XFRM/IPsec engine. It accepts privileged netlink requests for security associations, policies, replay/audit events, migration, default policy state, SAD/SPD information, and flush operations, and it emits multicast notifications back to key managers and monitoring processes.

## APIs, Types, and Functions
`xfrm_msg_min` and `xfrma_policy` define exported netlink message and attribute validation contracts. `xfrm_dispatch` maps XFRM message ids to handlers such as `xfrm_add_sa()`, `xfrm_del_sa()`, `xfrm_get_sa()`, `xfrm_dump_sa()`, `xfrm_add_policy()`, `xfrm_get_policy()`, `xfrm_flush_sa()`, `xfrm_flush_policy()`, `xfrm_new_ae()`, `xfrm_do_migrate()`, `xfrm_set_default()`, and SAD/SPD info accessors. Construction and conversion helpers include `verify_newsa_info()`, `verify_replay()`, `attach_aead()`, `attach_auth_trunc()`, `attach_crypt()`, `xfrm_state_construct()`, `xfrm_policy_construct()`, `copy_from_user_state()`, `copy_to_user_state_extra()`, `copy_from_user_tmpl()`, and `copy_to_user_tmpl()`. Notification builders include `build_aevent()`, `build_expire()`, `build_acquire()`, `build_polexpire()`, `build_report()`, and `build_mapping()`. Module integration is through `netlink_mgr`, `xfrm_user_net_ops`, `xfrm_user_init()`, and `xfrm_user_exit()`.

## Control Flow, State, and Persistence
Incoming packets enter through the per-netns netlink socket created by `xfrm_user_net_init()`, are serialized by `net->xfrm.xfrm_cfg_mutex`, optionally translated from compat layout, parsed against `xfrma_policy`, rejected for message-incompatible attributes, then dispatched to the relevant `doit` handler or dump callback. State changes are persisted in the core XFRM SAD/SPD tables, per-net namespace defaults and hash thresholds, SA replay state, lifetime counters, marks, interface ids, offload descriptors, and security contexts. The file itself persists only netlink sockets and registration structures; allocated temporary netlink payloads, replay buffers, templates, and copied algorithm descriptors are freed on error or handed to XFRM core objects. Notification flow is callback-driven from XFRM km events and multicasts skb messages to XFRM netlink groups.

## Dependencies and Integration
Depends on netlink, per-net namespace infrastructure, XFRM state and policy core APIs, crypto algorithm metadata, LSM security contexts, optional IPv6, compat translators, skb allocation, and CAP_NET_ADMIN enforcement. It is the bridge between iproute2/key managers and in-kernel IPsec state, and it exports the message minimum-size and attribute policy arrays for other XFRM code.

## Risks and Test Signals
High-risk areas are netlink attribute length validation, replay/ESN boundary rules, compat translation cleanup, redaction of authentication keys for unprivileged netlink dump consumers, lifecycle handling of allocated algorithm/security/offload state, and dump cursor correctness under concurrent state changes. Test signals include xfrm_user selftests via `ip xfrm`, malformed netlink fuzzing, namespace create/destroy cycles, SA and policy dump pagination, ESN replay validation, LSM context round trips, multicast notification listeners, compat syscall coverage, and module unload/reload with active net namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/Makefile -->
# sources/distributed-fs/ceph-client/rust/Makefile

## Purpose
Defines the Rust-for-Linux build graph for core Rust crates, generated C bindings, helper exports, rustdoc, doctests, unit tests, proc-macro support crates, symbol export headers, and optional inline-helper bitcode integration.

## APIs, Types, and Functions
Important targets build `core.o`, `compiler_builtins.o`, `ffi.o`, `bindings.o`, `uapi.o`, `pin_init.o`, `kernel.o`, `build_error.o`, `helpers/helpers.o`, generated binding files, generated export headers, proc-macro rlibs, rustdoc output, rust-analyzer metadata, and doctest KUnit glue. Key variables include `rustdoc_output`, `core-cfgs`, `proc_macro2-cfgs`, `syn-cfgs`, `pin_init-flags`, `bindgen_c_flags_final`, `redirect-intrinsics`, and rules such as `cmd_bindgen`, `cmd_rustc_library`, `cmd_rustdoc`, `cmd_exports`, and `rule_rustc_library`.

## Control Flow, State, and Persistence
The control flow is Kbuild-driven. Under `CONFIG_RUST`, host proc-macro crates are built first, bindgen generates Rust declarations from C helper headers, Rust crates are compiled with generated cfg files and explicit crate dependencies, C helper objects are compiled or linked as LLVM bitcode, and `nm` output is converted into generated `EXPORT_SYMBOL_RUST_GPL()` headers. Build state is persisted only in the object tree: `.o`, `.rlib`, `.rmeta`, generated Rust source, generated C export headers, rustdoc HTML, doctest C/Rust glue, and rust-analyzer JSON.

## Dependencies and Integration
Depends on Kbuild, rustc/rustdoc/clippy, bindgen/libclang, LLVM tools for inline helpers, nm/awk/sed/objcopy, generated kernel cfg files, target JSON, and standard kernel modversion/objtool rules. It integrates the Rust crates with the C kernel build, symbol versioning, docs, tests, and generated bindings.

## Risks and Test Signals
Risks include fragile flag filtering for GCC-vs-Clang bindgen, Rust version conditional logic, ABI mismatches in rustdoc/doctests, missing intrinsic redirection when new compiler builtins appear, symbol export churn, and helper inlining differences under `CONFIG_RUST_INLINE_HELPERS`. Test signals are `make LLVM=1 rustavailable`, `make rust-analyzer`, `make rustdoc`, `make rusttest`, KUnit doctest generation, modversion builds, GCC-built kernel bindgen paths, and architectures covered by `redirect-intrinsics`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/bindings/bindings_helper.h -->
# sources/distributed-fs/ceph-client/rust/bindings/bindings_helper.h

## Purpose
Provides the curated C include surface that bindgen uses to generate the Rust `bindings` crate, plus constant helper declarations for C macros and configuration-specific subsystem exposure.

## APIs, Types, and Functions
The header includes many kernel subsystem headers: ACPI, DRM, KUnit, auxiliary bus, block, clock, completion, CPU, cpumask, credentials, device core internals, DMA, file/firmware/fs, I/O, jump labels, memory management, OF/platform/PCI, PID namespaces, poll, property, PWM, refcount, regulator, scheduler, security, slab, task work, USB, wait queues, workqueues, xarray, and trace events. It defines `RUST_CONST_HELPER_*` constants for values bindgen cannot read as Rust constants, including GFP flags, page and slab alignment, block/file flags, xarray flags, vm flags, and optional GPU buddy flags. Conditional includes expose DRM panic QR and Android Binder Rust support when configured.

## Control Flow, State, and Persistence
There is no runtime control flow. During build, bindgen parses this translation unit and emits Rust declarations in `bindings_generated.rs`; the Makefile then renames helper constants by stripping `RUST_CONST_HELPER_`. Persistent outputs are generated Rust bindings under the object tree, not this source file.

## Dependencies and Integration
Depends on exact C header availability and config gates. It is integrated with `rust/Makefile`, the `bindings` crate, and Rust abstractions that rely on generated types and constants rather than handwritten FFI.

## Risks and Test Signals
Risks include exposing unstable private C layout, bindgen enum forward-reference behavior, architecture/config-specific header parse failures, constants accidentally using the wrong source expression, and the likely typo assigning `VM_MAYSHARE` from `VM_MAYEXEC`. Test signals are successful bindgen across broad configs, Rust compilation of generated constants, diff review of generated bindings after header changes, and targeted builds with DRM, Binder, GPU buddy, and security options toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/bindings/bindings_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/bindings/lib.rs -->
# sources/distributed-fs/ceph-client/rust/bindings/lib.rs

## Purpose
Defines the no-std Rust crate that imports generated bindgen output and exposes raw C kernel symbols and helper wrappers to higher-level Rust kernel code.

## APIs, Types, and Functions
`bindings_raw` includes `bindings_generated.rs`, imports helper symbols, manually defines blocklisted kernel integer aliases, and implements `Zeroable` for bindgen bitfield storage. `bindings_helper` includes `bindings_helpers_generated.rs` and rewrites helper names so generated Rust code can call `bindings::foo` while linking to `rust_helper_foo`. The crate re-exports `bindings_raw::*` and provides `compat_ptr_ioctl` as an `Option` depending on `CONFIG_COMPAT`.

## Control Flow, State, and Persistence
All state is compile-time generated source inclusion. Runtime calls are raw unsafe FFI calls into C or helper wrappers. The crate intentionally has broad lint allowances because generated code uses C naming, layout, and unsafe forms. There is no persistence beyond compiled metadata and object files.

## Dependencies and Integration
Depends on `OBJTREE` include paths, bindgen output, the `ffi` crate, `pin_init` marker traits, `cfi_encoding`, and the C helper generation rules. It is the lowest-level Rust integration point and is not meant to be used directly by modules.

## Risks and Test Signals
Risks include generated binding drift, direct user reliance on raw APIs, CFI/signature mismatches, missing `Zeroable` coverage for generated types, and configuration-dependent missing symbols. Test signals are full Rust crate builds, bindgen regeneration, clippy/rusttest libraries where enabled, and higher-level wrappers compiling without reaching into this crate directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/bindings/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/build_error.rs -->
# sources/distributed-fs/ceph-client/rust/build_error.rs

## Purpose
Provides a tiny no-std crate with a const function used by Rust build-time assertion machinery to force compile-time or link/build failures for impossible states.

## APIs, Types, and Functions
The sole API is `build_error(msg: &'static str) -> !`, exported as the C/Rust symbol `rust_build_error`, marked `cold`, `inline(never)`, and `track_caller`. It panics in const evaluation and remains a non-optimized call when a runtime build assertion is not eliminated.

## Control Flow, State, and Persistence
There is no mutable state or persistence. Control flow is deliberately terminal: any executed call panics, while intended use relies on compile-time const evaluation or optimizer elimination.

## Dependencies and Integration
Depends on the Rust core panic path and `rust/Makefile` rules that either build this object as always-needed or export `rust_build_error` under `CONFIG_RUST_BUILD_ASSERT_ALLOW`. It integrates with `build_assert!` in the kernel crate.

## Risks and Test Signals
Risks are optimizer/version behavior changes that fail to eliminate unreachable calls, runtime execution in paths assumed compile-time-only, and missing export for modules using build assertions. Test signals include Rust build assertion tests, negative compile tests, module builds with `CONFIG_RUST_BUILD_ASSERT_ALLOW`, and checking that failing assertions preserve useful caller locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/build_error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/compiler_builtins.rs -->
# sources/distributed-fs/ceph-client/rust/compiler_builtins.rs

## Purpose
Supplies a minimal in-tree substitute for Rust `compiler_builtins`, defining only redirected intrinsic symbols that the kernel wants to catch rather than use silently.

## APIs, Types, and Functions
`define_panicking_intrinsics!` emits extern C functions exported as `__rust*` symbols for float, 128-bit integer, and selected ARM EABI helper intrinsics. The intrinsic groups cover `__addsf3`, `__muldf3`, `__multi3`, `__udivti3`, ARM float compare/add/mul helpers, and ARM `__aeabi_uldivmod`.

## Control Flow, State, and Persistence
Runtime control flow should never reach these functions; if it does, they panic with a message explaining the unsupported type family. Symbol handling is coordinated with `rust/Makefile`, which redirects matching symbols from `core.o` to `__rust...` and weakens/removes conflicting builtin exports.

## Dependencies and Integration
Depends on unstable Rust compiler builtin features, no-builtins compilation, and Makefile `redirect-intrinsics`. It integrates with the kernel policy that Rust code should avoid floating point and unsupported wide arithmetic paths.

## Risks and Test Signals
Risks include missing a newly required intrinsic, architecture-specific compiler emission differences, panic paths in contexts that cannot tolerate them, and mismatch between this file and `redirect-intrinsics`. Test signals are cross-architecture Rust builds, symbol table inspection of `compiler_builtins.o`, negative tests for accidental float/128-bit use, and boot/module tests ensuring no panicking intrinsic is called.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/compiler_builtins.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/exports.c -->
# sources/distributed-fs/ceph-client/rust/exports.c

## Purpose
Bridges generated Rust symbol lists into the normal C `EXPORT_SYMBOL_GPL()` infrastructure so Rust crates and helpers can be used by loadable kernel modules.

## APIs, Types, and Functions
Defines `EXPORT_SYMBOL_RUST_GPL(sym)` and includes generated headers for core, bindings, kernel, and conditionally helper symbols. It also exports `rust_build_error` when build assertions are allowed for modules.

## Control Flow, State, and Persistence
There is no runtime behavior. The file is compiled into an object containing export records derived from generated header includes. Persistence is in module symbol tables and, when enabled, symbol version metadata.

## Dependencies and Integration
Depends on `include/linux/export.h`, generated `exports_*_generated.h` files from `rust/Makefile`, Rust v0 symbol mangling producing C-identifier-safe names, and Kbuild modversion handling. It integrates Rust-generated code with module loader symbol resolution.

## Risks and Test Signals
Risks include generated header omission, exporting too broad a Rust surface, symbol-version conflicts, helper export differences under `CONFIG_RUST_INLINE_HELPERS`, and mangling changes. Test signals are module builds using Rust APIs, `nm`/`modpost` export checks, GPL-only enforcement, and builds with helpers both inline and non-inline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/exports.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/ffi.rs -->
# sources/distributed-fs/ceph-client/rust/ffi.rs

## Purpose
Defines the kernel-specific Rust mapping of C primitive FFI types, avoiding assumptions baked into `core::ffi` where the kernel compiler flags differ from the platform default.

## APIs, Types, and Functions
The `alias!` macro defines `c_char`, signed and unsigned integer aliases, `c_long`, `c_ulong`, and long-long types, while asserting each alias has the same size as the corresponding `core::ffi` type. It re-exports `c_void` and `CStr` from core.

## Control Flow, State, and Persistence
The crate has no runtime state. All checks occur at compile time through constant assertions. The key semantic choice is mapping kernel `c_char` to `u8` because the kernel uses `-funsigned-char`.

## Dependencies and Integration
Depends on Rust `core::ffi` only for size comparisons and reusable `c_void`/`CStr`. It is consumed by generated bindings and low-level Rust wrappers wherever C ABI types appear.

## Risks and Test Signals
Risks include architectures where kernel ABI type sizes diverge from `core::ffi`, signedness mistakes for `char`, and future C type additions not represented here. Test signals are cross-architecture Rust builds, bindgen output using `ffi::` prefixes, and compile-time assertion failures on unsupported ABI combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/ffi.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/atomic.c -->
# sources/distributed-fs/ceph-client/rust/helpers/atomic.c

## Purpose
Generated Rust helper translation unit for Linux `atomic_t` and `atomic64_t` operations, exposing C inline/macro atomic APIs as callable Rust FFI symbols.

## APIs, Types, and Functions
Defines many `rust_helper_atomic_*` and `rust_helper_atomic64_*` wrappers for read/set, add/sub/inc/dec, return and fetch forms, relaxed/acquire/release variants, xchg/cmpxchg/try_cmpxchg, add/sub unless, inc/dec predicates, and bitwise and/or/xor/andnot operations where supported.

## Control Flow, State, and Persistence
Each helper directly delegates to the corresponding kernel atomic primitive and persists no state beyond modifying the pointed atomic object. Ordering semantics are inherited exactly from the wrapped primitive, so control flow is a single call-return boundary.

## Dependencies and Integration
Depends on `linux/atomic.h` and the generator `scripts/atomic/gen-rust-atomic-helpers.sh`; it is included by `helpers.c` and bindgen-generated into Rust helper declarations.

## Risks and Test Signals
Risks include generator drift from C atomic API changes, incorrect memory-order wrapper selection, architecture-specific atomic availability, and Rust callers passing invalid pointers or wrong lifetime assumptions. Test signals are regenerated diff checks, Rust atomic abstraction tests, KCSAN/lock-free stress, and architecture builds covering both 32-bit and 64-bit atomics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/atomic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/atomic_ext.c -->
# sources/distributed-fs/ceph-client/rust/helpers/atomic_ext.c

## Purpose
Adds Rust helper wrappers for small integer and pointer atomic-like operations not covered by the generated `atomic_t` helpers.

## APIs, Types, and Functions
Macro families generate `read`, `set`, `read_acquire`, `set_release`, `xchg` variants, and `try_cmpxchg` variants for `s8`, `s16`, and `const void *` pointer storage.

## Control Flow, State, and Persistence
Control flow is simple macro-expanded delegation to `READ_ONCE`, `WRITE_ONCE`, `smp_load_acquire`, `smp_store_release`, `xchg*`, and `try_cmpxchg*`. State is only the caller-provided memory location.

## Dependencies and Integration
Depends on `asm/barrier.h`, `asm/rwonce.h`, `linux/atomic.h`, and architecture support for byte/halfword/pointer exchange operations on Rust-supported architectures.

## Risks and Test Signals
Risks include unsupported atomic RMW width on a new Rust architecture, pointer constness mismatches, and callers assuming full `atomic_t` semantics for plain storage. Test signals are cross-architecture builds and Rust tests for memory-ordering-sensitive pointer/state machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/atomic_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/auxiliary.c -->
# sources/distributed-fs/ceph-client/rust/helpers/auxiliary.c

## Purpose
Exposes auxiliary bus device teardown helpers to Rust code.

## APIs, Types, and Functions
`rust_helper_auxiliary_device_uninit()` and `rust_helper_auxiliary_device_delete()` delegate to `auxiliary_device_uninit()` and `auxiliary_device_delete()`.

## Control Flow, State, and Persistence
The helpers mutate auxiliary-device lifecycle state owned by driver core; they keep no local state.

## Dependencies and Integration
Depends on `linux/auxiliary_bus.h` and Rust auxiliary-bus abstractions that need non-inline C entry points.

## Risks and Test Signals
Risks include lifecycle ordering mistakes, double uninit/delete, and mismatched Rust ownership. Test signals are Rust auxiliary-device registration/unregistration tests and driver-core leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/auxiliary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/barrier.c -->
# sources/distributed-fs/ceph-client/rust/helpers/barrier.c

## Purpose
Provides Rust-callable wrappers for global SMP memory barriers.

## APIs, Types, and Functions
Exports `rust_helper_smp_mb()`, `rust_helper_smp_wmb()`, and `rust_helper_smp_rmb()`.

## Control Flow, State, and Persistence
Each helper emits the corresponding architecture barrier and stores no state.

## Dependencies and Integration
Depends on `asm/barrier.h` and Rust synchronization primitives needing kernel barrier semantics.

## Risks and Test Signals
Risks are misuse as a substitute for acquire/release operations and architecture barrier regressions. Test signals are concurrency litmus tests, KCSAN stress, and inspection of generated assembly on supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/barrier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/binder.c -->
# sources/distributed-fs/ceph-client/rust/helpers/binder.c

## Purpose
Exposes list-LRU and task-work helpers used by Rust Android Binder support.

## APIs, Types, and Functions
APIs are `rust_helper_list_lru_count()`, `rust_helper_list_lru_walk()`, and `rust_helper_init_task_work()`.

## Control Flow, State, and Persistence
State lives in caller-provided `list_lru` and `callback_head` objects; the helpers count, walk, or initialize them through the C APIs.

## Dependencies and Integration
Depends on `linux/list_lru.h`, `linux/task_work.h`, and Binder Rust integration gated elsewhere by configuration.

## Risks and Test Signals
Risks include callback ABI mismatch for LRU isolation, walking under wrong locks, and task-work lifetime errors. Test signals are Binder Rust tests, list_lru shrinker exercise, and task-work cancellation/exit races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/binder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/bitmap.c -->
# sources/distributed-fs/ceph-client/rust/helpers/bitmap.c

## Purpose
Exports bitmap copy-and-extend behavior to Rust.

## APIs, Types, and Functions
`rust_helper_bitmap_copy_and_extend()` wraps `bitmap_copy_and_extend()`.

## Control Flow, State, and Persistence
The helper writes the destination bitmap from a source bitmap, extending/truncating according to bit counts; no local state is kept.

## Dependencies and Integration
Depends on `linux/bitmap.h` and Rust bitset/cpumask-style abstractions.

## Risks and Test Signals
Risks are caller buffer sizing and count/size confusion. Test signals include boundary bit counts, non-word-aligned sizes, and Rust-side buffer length checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/bitops.c -->
# sources/distributed-fs/ceph-client/rust/helpers/bitops.c

## Purpose
Provides Rust-callable bit manipulation and fallback find-bit helpers.

## APIs, Types, and Functions
Exports `rust_helper___set_bit()`, `rust_helper___clear_bit()`, `rust_helper_set_bit()`, `rust_helper_clear_bit()`, and conditional `_find_first_zero_bit`, `_find_next_zero_bit`, `_find_first_bit`, `_find_next_bit` wrappers when those are macros.

## Control Flow, State, and Persistence
Bit set/clear operations mutate caller-provided bitmaps; find helpers scan immutable bitmaps. Local state is absent and atomicity follows the wrapped C primitive.

## Dependencies and Integration
Depends on `linux/bitops.h` and `linux/find.h`. It integrates with bindgen because macro-only find helpers otherwise lack callable symbols.

## Risks and Test Signals
Risks include mixing atomic and non-atomic bit operations, volatile pointer expectations, and missing conditional symbols on some architectures. Test signals are Rust bitmap tests, concurrent bit operation stress, and cross-architecture builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/bitops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/blk.c -->
# sources/distributed-fs/ceph-client/rust/helpers/blk.c

## Purpose
Exposes block multiqueue request/private-data conversions to Rust drivers.

## APIs, Types, and Functions
`rust_helper_blk_mq_rq_to_pdu()` and `rust_helper_blk_mq_rq_from_pdu()` wrap the blk-mq PDU helpers.

## Control Flow, State, and Persistence
No local state is kept; conversions depend on blk-mq request allocation layout.

## Dependencies and Integration
Depends on `linux/blk-mq.h` and `linux/blkdev.h`, integrating Rust block drivers with blk-mq request-private storage.

## Risks and Test Signals
Risks are invalid PDU pointers, wrong tag-set command size, and lifetime assumptions after request completion. Test signals are Rust block queue tests and blk-mq request allocation/free stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/blk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/bug.c -->
# sources/distributed-fs/ceph-client/rust/helpers/bug.c

## Purpose
Makes kernel BUG/WARN primitives callable from Rust.

## APIs, Types, and Functions
`rust_helper_BUG()` is noreturn and delegates to `BUG()`. `rust_helper_WARN_ON()` returns whether the condition triggered `WARN_ON()`.

## Control Flow, State, and Persistence
State is limited to kernel warning/bug side effects such as logs and taint state; no local state is kept.

## Dependencies and Integration
Depends on `linux/bug.h` and Rust assertion/panic-adjacent abstractions.

## Risks and Test Signals
Risks are using `BUG()` where recoverable error handling is expected and test environments treating warnings as failures. Test signals are KUnit warning tests and build configs with BUG disabled or altered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/bug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/build_assert.c -->
# sources/distributed-fs/ceph-client/rust/helpers/build_assert.c

## Purpose
Performs C-side static assertions required by Rust allocation and binding assumptions.

## APIs, Types, and Functions
Contains a `static_assert()` requiring C `size_t` to match `uintptr_t` in size and alignment, matching Rust `usize` expectations from bindgen.

## Control Flow, State, and Persistence
There is no runtime control flow or state; failure is a compile-time build break.

## Dependencies and Integration
Depends on `linux/build_bug.h` and the bindgen assumption that `size_t` maps to Rust `usize`.

## Risks and Test Signals
Risks are porting Rust support to unusual ABIs where object-size and pointer-size types diverge. Test signals are cross-architecture allmodconfig-style builds and early compile failure on unsupported ABIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/build_assert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/build_bug.c -->
# sources/distributed-fs/ceph-client/rust/helpers/build_bug.c

## Purpose
Exposes kernel error-name formatting to Rust.

## APIs, Types, and Functions
`rust_helper_errname()` wraps `errname()` and returns a static string for an errno value when known.

## Control Flow, State, and Persistence
The helper has no local state and returns pointers owned by kernel error-name tables.

## Dependencies and Integration
Depends on `linux/errname.h` and Rust error/debug formatting paths.

## Risks and Test Signals
Risks are caller assumptions that every errno has a non-null stable name and lifetime misuse. Test signals include formatting common and unknown errno values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/build_bug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/clk.c -->
# sources/distributed-fs/ceph-client/rust/helpers/clk.c

## Purpose
Exposes clock-framework helpers to Rust, including fallback wrappers for inline-only C stubs.

## APIs, Types, and Functions
Conditionally exports `clk_get`, `clk_put`, `clk_enable`, `clk_disable`, `clk_get_rate`, `clk_set_rate`, `clk_prepare`, and `clk_unprepare` when corresponding clock framework configs are absent, and always exports optional get plus prepare-enable/disable-unprepare helpers.

## Control Flow, State, and Persistence
State is in clock framework references and enable/prepare counts; helpers only delegate and keep no local state.

## Dependencies and Integration
Depends on `linux/clk.h` and Rust device-driver abstractions that manage clocks.

## Risks and Test Signals
Risks include leaked clock references, unbalanced prepare/enable counts, optional clock error handling, and config-dependent symbol availability. Test signals are Rust driver probe/remove tests on systems with and without clock providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/completion.c -->
# sources/distributed-fs/ceph-client/rust/helpers/completion.c

## Purpose
Exposes completion initialization to Rust.

## APIs, Types, and Functions
`rust_helper_init_completion()` wraps `init_completion()`.

## Control Flow, State, and Persistence
The helper initializes caller-provided `struct completion` state and keeps no local state.

## Dependencies and Integration
Depends on `linux/completion.h` and Rust synchronization wrappers.

## Risks and Test Signals
Risks are reinitializing live completions and missing wakeup ordering. Test signals are Rust completion wait/complete KUnit tests and race stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/completion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/cpu.c -->
# sources/distributed-fs/ceph-client/rust/helpers/cpu.c

## Purpose
Exposes raw CPU id lookup to Rust.

## APIs, Types, and Functions
`rust_helper_raw_smp_processor_id()` wraps `raw_smp_processor_id()`.

## Control Flow, State, and Persistence
No local state; result depends on current execution CPU and preemption context.

## Dependencies and Integration
Depends on `linux/smp.h` and Rust per-CPU or scheduler-sensitive code.

## Risks and Test Signals
Risks are use in preemptible contexts where raw CPU id is unstable. Test signals include lockdep/preemption debug coverage and Rust per-CPU tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/cpufreq.c -->
# sources/distributed-fs/ceph-client/rust/helpers/cpufreq.c

## Purpose
Exposes cpufreq energy-model registration to Rust when CPU frequency support is enabled.

## APIs, Types, and Functions
`rust_helper_cpufreq_register_em_with_opp()` wraps `cpufreq_register_em_with_opp()` under `CONFIG_CPU_FREQ`.

## Control Flow, State, and Persistence
State is maintained by cpufreq/energy-model subsystems for the provided policy.

## Dependencies and Integration
Depends on `linux/cpufreq.h` and OPP/energy model integration.

## Risks and Test Signals
Risks are config-dependent absence and policy lifetime errors. Test signals are cpufreq-enabled Rust platform driver tests and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/cpumask.c -->
# sources/distributed-fs/ceph-client/rust/helpers/cpumask.c

## Purpose
Provides Rust-callable cpumask mutation, query, copy, allocation, and free helpers.

## APIs, Types, and Functions
Exports set/clear/test variants, `cpumask_setall`, `cpumask_empty`, `cpumask_full`, `cpumask_weight`, `cpumask_copy`, `alloc_cpumask_var`, `zalloc_cpumask_var`, and conditionally `free_cpumask_var` when cpumasks are not offstack.

## Control Flow, State, and Persistence
The helpers mutate caller-provided masks or allocate/free cpumask storage through kernel APIs. Persistent state is the caller-owned cpumask allocation.

## Dependencies and Integration
Depends on `linux/cpumask.h` and CPU topology configuration.

## Risks and Test Signals
Risks include CPU index bounds, allocation/free mismatch under `CONFIG_CPUMASK_OFFSTACK`, and races with hotplug if masks are assumed static. Test signals are cpumask Rust tests, CPU hotplug scenarios, and config matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/cpumask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/cred.c -->
# sources/distributed-fs/ceph-client/rust/helpers/cred.c

## Purpose
Exposes credential reference management to Rust.

## APIs, Types, and Functions
`rust_helper_get_cred()` and `rust_helper_put_cred()` wrap `get_cred()` and `put_cred()`.

## Control Flow, State, and Persistence
The helpers adjust refcounts on immutable credential objects and keep no local state.

## Dependencies and Integration
Depends on `linux/cred.h` and Rust security/task abstractions.

## Risks and Test Signals
Risks are refcount leaks, use-after-put, and confusing subjective vs objective credentials. Test signals are refcount leak detection and Rust task/cred wrapper tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/cred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/device.c -->
# sources/distributed-fs/ceph-client/rust/helpers/device.c

## Purpose
Exposes selected driver-core device helper APIs to Rust.

## APIs, Types, and Functions
Exports `devm_add_action`, `devm_add_action_or_reset`, `dev_get_drvdata`, `dev_set_drvdata`, and `dev_name` wrappers.

## Control Flow, State, and Persistence
State is device-managed action lists and device driver data; helpers only mutate or read the `struct device` fields managed by driver core.

## Dependencies and Integration
Depends on `linux/device.h` and Rust device/driver abstractions.

## Risks and Test Signals
Risks include drvdata type confusion, action callback lifetime, and cleanup ordering during probe failures. Test signals are Rust driver probe/remove tests and devres leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/dma-resv.c -->
# sources/distributed-fs/ceph-client/rust/helpers/dma-resv.c

## Purpose
Exposes DMA reservation object locking to Rust graphics/DMA users.

## APIs, Types, and Functions
`rust_helper_dma_resv_lock()` and `rust_helper_dma_resv_unlock()` wrap the reservation lock APIs.

## Control Flow, State, and Persistence
State is the reservation object's ww-mutex lock state; no local state is kept.

## Dependencies and Integration
Depends on `linux/dma-resv.h` and wound-wait acquire contexts.

## Risks and Test Signals
Risks are deadlocks from wrong ww context usage and unbalanced unlocks. Test signals are DRM/GEM Rust tests and lockdep ww-mutex coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/dma-resv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/dma.c -->
# sources/distributed-fs/ceph-client/rust/helpers/dma.c

## Purpose
Exposes DMA allocation, mask, mapping, and segment-size helpers to Rust device drivers.

## APIs, Types, and Functions
APIs include `dma_alloc_attrs`, `dma_free_attrs`, `dma_set_mask_and_coherent`, `dma_set_mask`, `dma_set_coherent_mask`, `dma_map_sgtable`, `dma_max_mapping_size`, and `dma_set_max_seg_size` wrappers.

## Control Flow, State, and Persistence
State is managed by DMA/IOMMU subsystems and device DMA configuration; helper calls allocate coherent memory, map scatter-gather tables, or mutate device constraints.

## Dependencies and Integration
Depends on `linux/dma-mapping.h`, device DMA masks, scatterlist tables, and architecture/IOMMU DMA ops.

## Risks and Test Signals
Risks include leaks on allocation/free mismatch, wrong DMA direction/attrs, mapping errors not propagated by Rust callers, and mask setup after allocations. Test signals are DMA API debug, IOMMU-enabled test systems, and Rust driver teardown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/drm.c -->
# sources/distributed-fs/ceph-client/rust/helpers/drm.c

## Purpose
Exposes DRM GEM and shmem-GEM helper functions to Rust graphics drivers when DRM configs are enabled.

## APIs, Types, and Functions
Under `CONFIG_DRM`, exports GEM object get/put and VMA node offset helpers; under `CONFIG_DRM_GEM_SHMEM_HELPER`, exports shmem object free, print-info, pin/unpin, sg-table retrieval, vmap/vunmap, and mmap helpers.

## Control Flow, State, and Persistence
State is in GEM object refcounts, shmem backing storage, mapping state, and VMA manager nodes. The wrappers keep no local state.

## Dependencies and Integration
Depends on DRM GEM, DRM shmem helper, VMA manager headers, and Rust DRM abstractions.

## Risks and Test Signals
Risks include config-dependent symbols, unbalanced object references, pin/vmap lifecycle bugs, and mmap offset misuse. Test signals are Rust DRM driver tests, GEM object refcount leak checks, mmap/pin/vmap stress, and builds with DRM helpers disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/drm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/err.c -->
# sources/distributed-fs/ceph-client/rust/helpers/err.c

## Purpose
Exposes Linux encoded error-pointer helpers to Rust.

## APIs, Types, and Functions
Exports wrappers for `ERR_PTR()`, `IS_ERR()`, and `PTR_ERR()`.

## Control Flow, State, and Persistence
No local state; helpers encode/decode errors in pointer values according to kernel conventions.

## Dependencies and Integration
Depends on `linux/err.h` and Rust wrappers converting C pointer-return APIs into `Result`.

## Risks and Test Signals
Risks include treating valid low-address pointers as errors, losing `__force` semantics, and accepting null separately from error pointers. Test signals are conversion tests for common errno values and raw pointer API wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/err.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/fs.c -->
# sources/distributed-fs/ceph-client/rust/helpers/fs.c

## Purpose
Exposes file reference acquisition to Rust.

## APIs, Types, and Functions
`rust_helper_get_file()` wraps `get_file()`.

## Control Flow, State, and Persistence
The helper increments the file refcount and returns the same file pointer; persistent state is the caller-owned reference.

## Dependencies and Integration
Depends on `linux/fs.h` and Rust file abstractions.

## Risks and Test Signals
Risks are leaked references and use-after-fput in wrappers. Test signals are file refcount tests and open/close stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/gpu.c -->
# sources/distributed-fs/ceph-client/rust/helpers/gpu.c

## Purpose
Exposes GPU buddy allocator block inspection helpers to Rust when GPU buddy is enabled.

## APIs, Types, and Functions
Under `CONFIG_GPU_BUDDY`, wraps `gpu_buddy_block_offset()` and `gpu_buddy_block_order()`.

## Control Flow, State, and Persistence
No local state; reads properties from caller-owned `gpu_buddy_block` objects.

## Dependencies and Integration
Depends on `linux/gpu_buddy.h` and Rust graphics memory-manager code.

## Risks and Test Signals
Risks include config-dependent availability and stale block pointers after allocator mutations. Test signals are GPU buddy allocation/free tests and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/helpers.c -->
# sources/distributed-fs/ceph-client/rust/helpers/helpers.c

## Purpose
Aggregates all Rust C helper fragments into one translation unit for bindgen and object/bitcode builds.

## APIs, Types, and Functions
Defines a bindgen-only `__rust_helper` attribute shape to expose correct C prototypes, otherwise maps helpers as exportable symbols. It includes every helper fragment from `atomic.c` through `xarray.c` in a fixed list.

## Control Flow, State, and Persistence
There is no direct runtime logic beyond the included helper functions. Build state differs depending on whether the file is parsed by bindgen, compiled into `helpers.o`, or emitted as LLVM bitcode for inline helper linking.

## Dependencies and Integration
Depends on `linux/compiler_types.h`, every included helper source, `rust/Makefile` bindgen rules, and optional `CONFIG_RUST_INLINE_HELPERS`.

## Risks and Test Signals
Risks include include-order conflicts, duplicate helper symbol names, bindgen seeing a different prototype than the compiler, and forgetting to add new helper files here. Test signals are bindgen helper generation, full Rust builds, symbol export generation, and inline/non-inline helper config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/io.c -->
# sources/distributed-fs/ceph-client/rust/helpers/io.c

## Purpose
Exposes MMIO mapping/accessors and I/O resource reservation helpers to Rust drivers.

## APIs, Types, and Functions
APIs include `ioremap`, `ioremap_np`, `iounmap`, read/write byte/word/long/quad accessors and relaxed variants, `resource_size`, `request_mem_region`, `release_mem_region`, `request_region`, `request_muxed_region`, and `release_region`; 64-bit qword accessors are config-gated.

## Control Flow, State, and Persistence
State lives in I/O mappings and resource reservation trees owned by the kernel; helpers map/unmap, read/write device registers, or reserve/release regions.

## Dependencies and Integration
Depends on `linux/io.h`, `linux/ioport.h`, architecture MMIO semantics, and Rust device resource abstractions.

## Risks and Test Signals
Risks include missing ordering around relaxed accessors, mapping leaks, wrong resource sizes, endian/device semantics, and 64-bit accessor absence. Test signals are Rust MMIO wrappers, resource conflict tests, driver probe/remove cleanup, and architecture builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/irq.c -->
# sources/distributed-fs/ceph-client/rust/helpers/irq.c

## Purpose
Exposes IRQ request registration to Rust.

## APIs, Types, and Functions
`rust_helper_request_irq()` wraps `request_irq()` with handler, flags, name, and device cookie.

## Control Flow, State, and Persistence
State is IRQ subsystem handler registration and caller-managed device cookie lifetime.

## Dependencies and Integration
Depends on `linux/interrupt.h` and Rust IRQ abstractions.

## Risks and Test Signals
Risks include handler ABI mismatch, freeing device data before `free_irq`, and interrupt context safety. Test signals are Rust interrupt driver tests and shared IRQ registration/removal stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/jump_label.c -->
# sources/distributed-fs/ceph-client/rust/helpers/jump_label.c

## Purpose
Provides a Rust helper for static key count fallback when jump labels are disabled.

## APIs, Types, and Functions
Under `!CONFIG_JUMP_LABEL`, exports `rust_helper_static_key_count()` wrapping `static_key_count()`.

## Control Flow, State, and Persistence
No local state; reads static-key state maintained by jump-label/static-key core.

## Dependencies and Integration
Depends on `linux/jump_label.h` and Rust static-branch abstractions.

## Risks and Test Signals
Risks are config-dependent behavior and stale assumptions about enabled/disabled static branches. Test signals are builds with and without `CONFIG_JUMP_LABEL` and Rust static-key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/kunit.c -->
# sources/distributed-fs/ceph-client/rust/helpers/kunit.c

## Purpose
Exposes current KUnit test lookup to Rust test code.

## APIs, Types, and Functions
`rust_helper_kunit_get_current_test()` wraps `kunit_get_current_test()`.

## Control Flow, State, and Persistence
No local state; returns the current task's KUnit test context when present.

## Dependencies and Integration
Depends on `kunit/test-bug.h` and Rust KUnit macro infrastructure.

## Risks and Test Signals
Risks are null handling outside KUnit context and task-local assumptions. Test signals are Rust KUnit tests and non-test builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/list.c -->
# sources/distributed-fs/ceph-client/rust/helpers/list.c

## Purpose
Exposes basic Linux intrusive list initialization and insertion to Rust.

## APIs, Types, and Functions
Exports `rust_helper_INIT_LIST_HEAD()` and `rust_helper_list_add_tail()`.

## Control Flow, State, and Persistence
Mutates caller-owned `list_head` links; no local state is kept.

## Dependencies and Integration
Depends on `linux/list.h` and Rust intrusive list abstractions.

## Risks and Test Signals
Risks include double insertion, missing initialization, and aliasing/lifetime errors around containing structs. Test signals are list insertion/removal KUnit tests and debug-list builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/maple_tree.c -->
# sources/distributed-fs/ceph-client/rust/helpers/maple_tree.c

## Purpose
Exposes maple tree initialization with flags to Rust.

## APIs, Types, and Functions
`rust_helper_mt_init_flags()` wraps `mt_init_flags()`.

## Control Flow, State, and Persistence
Initializes caller-owned maple tree state and persists only in that object.

## Dependencies and Integration
Depends on `linux/maple_tree.h` and Rust data structure wrappers.

## Risks and Test Signals
Risks include reinitializing non-empty trees and wrong flag selection. Test signals are Rust maple-tree wrapper tests and memory-leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/maple_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/mm.c -->
# sources/distributed-fs/ceph-client/rust/helpers/mm.c

## Purpose
Exposes memory-management reference and mmap-lock helpers to Rust.

## APIs, Types, and Functions
APIs include `mmgrab`, `mmdrop`, `mmget`, `mmget_not_zero`, `mmap_read_lock`, `mmap_read_trylock`, `mmap_read_unlock`, `vma_lookup`, and `vma_end_read`.

## Control Flow, State, and Persistence
State is in `mm_struct` reference counts and mmap/VMA lock/read-side state. Helpers keep no local state.

## Dependencies and Integration
Depends on `linux/mm.h`, `linux/sched/mm.h`, and Rust process/mm abstractions.

## Risks and Test Signals
Risks include refcount leaks, locking imbalance, VMA pointer lifetime after unlock, and task-exit races. Test signals are Rust mm wrapper tests, lockdep, and process exit/mmap stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/mutex.c -->
# sources/distributed-fs/ceph-client/rust/helpers/mutex.c

## Purpose
Exposes mutex operations and lockdep assertions to Rust.

## APIs, Types, and Functions
Exports `mutex_lock`, `mutex_trylock`, `__mutex_init`, lock-held assertion, and `mutex_destroy` wrappers.

## Control Flow, State, and Persistence
State is caller-owned mutex lock state and lockdep class metadata.

## Dependencies and Integration
Depends on `linux/mutex.h` and Rust lock abstractions.

## Risks and Test Signals
Risks include deadlocks, uninitialized locks, destroy while locked, and lock-class lifetime errors. Test signals are Rust mutex tests, lockdep, and PREEMPT_RT builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/mutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/of.c -->
# sources/distributed-fs/ceph-client/rust/helpers/of.c

## Purpose
Exposes Open Firmware fwnode type checking to Rust.

## APIs, Types, and Functions
`rust_helper_is_of_node()` wraps `is_of_node()`.

## Control Flow, State, and Persistence
No local state; reads fwnode type information.

## Dependencies and Integration
Depends on `linux/of.h` and Rust firmware-node abstractions.

## Risks and Test Signals
Risks are null/invalid fwnode pointers and ACPI-vs-OF branch mistakes. Test signals are device-tree and ACPI build/runtime coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/page.c -->
# sources/distributed-fs/ceph-client/rust/helpers/page.c

## Purpose
Exposes page allocation, temporary mapping, unmapping, and optional NUMA-node lookup to Rust.

## APIs, Types, and Functions
APIs include `alloc_pages`, `kmap_local_page`, `kunmap_local`, and conditionally `page_to_nid`.

## Control Flow, State, and Persistence
State is allocated pages and per-thread local kmap stack state owned by MM/highmem code.

## Dependencies and Integration
Depends on `linux/gfp.h`, `linux/highmem.h`, `linux/mm.h`, and Rust page abstractions.

## Risks and Test Signals
Risks include allocation leaks, highmem mapping imbalance, using local mappings after unmap or migration, and config-dependent node lookup. Test signals are Rust page allocation/fill tests and highmem/NUMA config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/pci.c -->
# sources/distributed-fs/ceph-client/rust/helpers/pci.c

## Purpose
Exposes PCI device id, BAR resource, type-check, and IRQ-vector helpers to Rust.

## APIs, Types, and Functions
Exports `pci_dev_id`, `pci_resource_start`, `pci_resource_len`, `dev_is_pci`, and under `!CONFIG_PCI_MSI` wrappers for IRQ vector allocation/free/lookup.

## Control Flow, State, and Persistence
State is PCI core device/resource/IRQ-vector state; helpers keep no local state.

## Dependencies and Integration
Depends on `linux/pci.h` and Rust PCI driver abstractions.

## Risks and Test Signals
Risks include BAR index errors, IRQ vector lifetime leaks, config-dependent MSI paths, and device pointer casting mistakes. Test signals are Rust PCI probe/remove tests, MSI and non-MSI configs, and resource validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/pid_namespace.c -->
# sources/distributed-fs/ceph-client/rust/helpers/pid_namespace.c

## Purpose
Exposes PID namespace reference helpers and safe task-to-PID-namespace acquisition to Rust.

## APIs, Types, and Functions
APIs are `get_pid_ns`, `put_pid_ns`, and `task_get_pid_ns()`, the latter using an RCU guard around `task_active_pid_ns()` and taking a reference before returning.

## Control Flow, State, and Persistence
Persistent state is PID namespace refcounts. The helper itself has transient RCU read-side state only.

## Dependencies and Integration
Depends on `linux/pid_namespace.h`, `linux/cleanup.h`, RCU, and Rust task/namespace wrappers.

## Risks and Test Signals
Risks include refcount leaks, null namespace handling, and task lifetime assumptions. Test signals are namespace creation/destruction tests, task exit races, and RCU debug coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/pid_namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/platform.c -->
# sources/distributed-fs/ceph-client/rust/helpers/platform.c

## Purpose
Exposes platform-device type checking to Rust.

## APIs, Types, and Functions
`rust_helper_dev_is_platform()` wraps `dev_is_platform()`.

## Control Flow, State, and Persistence
No local state; checks the device bus/type state.

## Dependencies and Integration
Depends on `linux/platform_device.h` and Rust platform driver abstractions.

## Risks and Test Signals
Risks are invalid device pointers and incorrect downcasting. Test signals are Rust platform driver probe tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/poll.c -->
# sources/distributed-fs/ceph-client/rust/helpers/poll.c

## Purpose
Exposes `poll_wait()` to Rust file operations.

## APIs, Types, and Functions
`rust_helper_poll_wait()` wraps `poll_wait()` for a file, waitqueue, and poll table.

## Control Flow, State, and Persistence
State is registered waitqueue entries in the poll table; no helper-local state.

## Dependencies and Integration
Depends on `linux/poll.h`, file operations, and Rust character/file abstractions.

## Risks and Test Signals
Risks include waitqueue lifetime, null poll table handling, and missed wakeups. Test signals are Rust file poll/select/epoll tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/processor.c -->
# sources/distributed-fs/ceph-client/rust/helpers/processor.c

## Purpose
Exposes CPU relax hints to Rust spin/wait loops.

## APIs, Types, and Functions
`rust_helper_cpu_relax()` wraps `cpu_relax()`.

## Control Flow, State, and Persistence
No state; emits architecture-specific pause/relax behavior.

## Dependencies and Integration
Depends on `linux/processor.h` and Rust polling primitives.

## Risks and Test Signals
Risks are busy-wait misuse and missing scheduling points. Test signals are lock-free wait-loop benchmarks and preemption latency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/processor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/property.c -->
# sources/distributed-fs/ceph-client/rust/helpers/property.c

## Purpose
Exposes firmware node reference release to Rust.

## APIs, Types, and Functions
`rust_helper_fwnode_handle_put()` wraps `fwnode_handle_put()`.

## Control Flow, State, and Persistence
State is fwnode reference counts; no local state.

## Dependencies and Integration
Depends on `linux/property.h` and Rust fwnode/property wrappers.

## Risks and Test Signals
Risks are put imbalance and using fwnodes after release. Test signals are device property wrapper tests and refcount leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/property.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/pwm.c -->
# sources/distributed-fs/ceph-client/rust/helpers/pwm.c

## Purpose
Exposes PWM chip parent and driver-data helpers to Rust PWM drivers.

## APIs, Types, and Functions
APIs are `pwmchip_parent`, `pwmchip_get_drvdata`, and `pwmchip_set_drvdata` wrappers.

## Control Flow, State, and Persistence
State is PWM chip drvdata and parent device reference owned by the PWM core/driver.

## Dependencies and Integration
Depends on `linux/pwm.h` and Rust PWM abstractions.

## Risks and Test Signals
Risks include drvdata type confusion and chip lifetime misuse. Test signals are Rust PWM chip registration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/pwm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/rbtree.c -->
# sources/distributed-fs/ceph-client/rust/helpers/rbtree.c

## Purpose
Exposes selected red-black tree operations to Rust intrusive tree code.

## APIs, Types, and Functions
Exports `rb_link_node`, `rb_first`, and `rb_last` wrappers.

## Control Flow, State, and Persistence
Mutates or reads caller-owned rb-tree nodes and roots; no local state.

## Dependencies and Integration
Depends on `linux/rbtree.h` and Rust rbtree abstractions.

## Risks and Test Signals
Risks include incorrect parent/link pointers, missing rebalancing outside this helper, and lifetime aliasing of intrusive nodes. Test signals are insertion/removal/order tests with debug assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/rbtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/rcu.c -->
# sources/distributed-fs/ceph-client/rust/helpers/rcu.c

## Purpose
Exposes RCU read-side lock and unlock to Rust.

## APIs, Types, and Functions
`rust_helper_rcu_read_lock()` and `rust_helper_rcu_read_unlock()` delegate to core RCU APIs.

## Control Flow, State, and Persistence
State is current execution context RCU nesting; helpers keep no local state.

## Dependencies and Integration
Depends on `linux/rcupdate.h` and Rust RCU guard abstractions.

## Risks and Test Signals
Risks include nesting imbalance, sleeping in non-sleepable RCU sections, and using protected pointers after unlock. Test signals are lockdep/RCU debug and Rust RCU guard tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/rcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/refcount.c -->
# sources/distributed-fs/ceph-client/rust/helpers/refcount.c

## Purpose
Exposes refcount initialization and mutation helpers to Rust.

## APIs, Types, and Functions
APIs include `REFCOUNT_INIT`, `refcount_set`, `refcount_inc`, `refcount_dec`, and `refcount_dec_and_test` wrappers.

## Control Flow, State, and Persistence
State is the caller-provided `refcount_t`; no local state.

## Dependencies and Integration
Depends on `linux/refcount.h` and Rust reference-counted wrappers.

## Risks and Test Signals
Risks include underflow, use-after-final-dec, and mixing raw and safe refcount paths. Test signals are refcount saturation/underflow tests and Rust ownership wrapper tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/refcount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/regulator.c -->
# sources/distributed-fs/ceph-client/rust/helpers/regulator.c

## Purpose
Provides Rust helper wrappers for regulator APIs when the regulator framework is not built as real callable functions.

## APIs, Types, and Functions
Under `!CONFIG_REGULATOR`, exports put/get, set/get voltage, enable/disable/is_enabled, and device-managed get-enable helpers including optional form.

## Control Flow, State, and Persistence
State is regulator references, enable counts, and voltage constraints maintained by regulator core or stubs.

## Dependencies and Integration
Depends on `linux/regulator/consumer.h` and Rust power-management driver abstractions.

## Risks and Test Signals
Risks include config-dependent stub semantics, unbalanced enable/disable, leaked references, and optional regulator error handling. Test signals are driver tests with regulator enabled/disabled and probe-failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/scatterlist.c -->
# sources/distributed-fs/ceph-client/rust/helpers/scatterlist.c

## Purpose
Exposes scatterlist DMA address/length traversal and DMA unmap helpers to Rust.

## APIs, Types, and Functions
APIs are `sg_dma_address`, `sg_dma_len`, `sg_next`, and `dma_unmap_sgtable` wrappers.

## Control Flow, State, and Persistence
State is in DMA-mapped scatter-gather tables; helper reads entries or unmaps a mapping.

## Dependencies and Integration
Depends on `linux/dma-direction.h`, scatterlist structures, and DMA mapping code.

## Risks and Test Signals
Risks include unmapping with wrong device/direction/attrs, iterating past the table, and using DMA fields before mapping. Test signals are DMA API debug and Rust scatter-gather wrapper tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/scatterlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/security.c -->
# sources/distributed-fs/ceph-client/rust/helpers/security.c

## Purpose
Exposes LSM/security hook stubs to Rust when full security hooks are not configured.

## APIs, Types, and Functions
Under `!CONFIG_SECURITY`, wraps credential secid lookup, secid-to-secctx conversion, secctx release, and Binder-specific LSM hooks for context manager, transaction, binder transfer, and file transfer.

## Control Flow, State, and Persistence
State is in security subsystem contexts and caller-managed `lsm_context` storage; helpers keep no local state.

## Dependencies and Integration
Depends on `linux/security.h`, LSM configuration, credentials, files, and Binder Rust integration.

## Risks and Test Signals
Risks include config-dependent no-op/security behavior, secctx lifetime leaks, and Binder permission checks diverging across configs. Test signals are Binder security tests, LSM-enabled/disabled builds, and secctx conversion/release coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/signal.c -->
# sources/distributed-fs/ceph-client/rust/helpers/signal.c

## Purpose
Exposes signal-pending checks to Rust.

## APIs, Types, and Functions
`rust_helper_signal_pending()` wraps `signal_pending()` for a task.

## Control Flow, State, and Persistence
No local state; reads task signal state.

## Dependencies and Integration
Depends on `linux/sched/signal.h` and Rust task/wait abstractions.

## Risks and Test Signals
Risks include stale task pointers and checking the wrong task context. Test signals are interruptible wait tests and signal delivery races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/slab.c -->
# sources/distributed-fs/ceph-client/rust/helpers/slab.c

## Purpose
Exposes aligned realloc helpers for slab and kvmalloc-backed Rust allocators.

## APIs, Types, and Functions
Exports `rust_helper_krealloc_node_align()` and `rust_helper_kvrealloc_node_align()` with `__must_check` and realloc-size annotations.

## Control Flow, State, and Persistence
State is heap allocation ownership transferred through returned pointers; no local helper state.

## Dependencies and Integration
Depends on `linux/slab.h` and Rust `Kmalloc`/`KVmalloc` allocator implementations.

## Risks and Test Signals
Risks include old-layout mismatches, losing the original pointer on allocation failure, alignment mistakes, and NUMA node misuse. Test signals are Rust allocator KUnit tests for alignment, growth/shrink, failure, and zero-size free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/slab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/spinlock.c -->
# sources/distributed-fs/ceph-client/rust/helpers/spinlock.c

## Purpose
Exposes spinlock initialization, lock/unlock, trylock, and lockdep assertion helpers to Rust.

## APIs, Types, and Functions
Exports `__spin_lock_init` wrapper with debug/PREEMPT_RT-specific initialization, plus `spin_lock`, `spin_unlock`, `spin_trylock`, and lock-held assertion.

## Control Flow, State, and Persistence
State is caller-owned spinlock and lockdep metadata; no local state.

## Dependencies and Integration
Depends on `linux/spinlock.h`, `CONFIG_DEBUG_SPINLOCK`, `CONFIG_PREEMPT_RT`, and Rust lock abstractions.

## Risks and Test Signals
Risks include sleeping/RT semantic differences, unbalanced locking, wrong lock class keys, and using raw spin assumptions on RT. Test signals are Rust spinlock tests, lockdep, and PREEMPT_RT config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/spinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/sync.c -->
# sources/distributed-fs/ceph-client/rust/helpers/sync.c

## Purpose
Exposes lockdep key registration and unregistration to Rust synchronization primitives.

## APIs, Types, and Functions
APIs are `rust_helper_lockdep_register_key()` and `rust_helper_lockdep_unregister_key()`.

## Control Flow, State, and Persistence
State is lockdep's global key registry for caller-owned `lock_class_key` objects.

## Dependencies and Integration
Depends on `linux/lockdep.h` and Rust lock-class management.

## Risks and Test Signals
Risks include unregistering keys too early, leaking registered keys, and conditional lockdep behavior. Test signals are lockdep-enabled Rust lock tests and module unload checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/task.c -->
# sources/distributed-fs/ceph-client/rust/helpers/task.c

## Purpose
Exposes current task, task reference, UID, namespace, and rescheduling helpers to Rust.

## APIs, Types, and Functions
APIs include `might_resched`, `get_current`, `get_task_struct`, `put_task_struct`, task uid/euid, optional `from_kuid`, `uid_eq`, `current_euid`, `current_user_ns`, and `task_tgid_nr_ns`.

## Control Flow, State, and Persistence
State is task refcounts and task credential/namespace data; helpers read or adjust references and keep no local state.

## Dependencies and Integration
Depends on `linux/kernel.h`, `linux/sched/task.h`, credentials, user namespaces, PID namespaces, and Rust task abstractions.

## Risks and Test Signals
Risks include task lifetime leaks, user namespace config differences, stale credential reads, and calling `might_resched` in invalid contexts. Test signals are Rust task wrapper tests, namespace config builds, and scheduler debug coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/time.c -->
# sources/distributed-fs/ceph-client/rust/helpers/time.c

## Purpose
Exposes sleep/delay and ktime helpers to Rust.

## APIs, Types, and Functions
APIs include `fsleep`, `ktime_get_real`, `ktime_get_boottime`, `ktime_get_clocktai`, `ktime_to_us`, `ktime_to_ms`, and `udelay`.

## Control Flow, State, and Persistence
No local state; reads kernel clocks or busy/sleep delays according to wrapped APIs.

## Dependencies and Integration
Depends on `linux/delay.h`, `linux/ktime.h`, `linux/timekeeping.h`, and Rust time abstractions.

## Risks and Test Signals
Risks include using busy delay for long periods, sleeping in atomic context via `fsleep`, and clock-domain confusion. Test signals are Rust time conversion tests and context-sensitive delay tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/uaccess.c -->
# sources/distributed-fs/ceph-client/rust/helpers/uaccess.c

## Purpose
Exposes user-memory copy helpers to Rust.

## APIs, Types, and Functions
Exports `copy_from_user` and `copy_to_user`; when inline copy helpers are configured, also exports `_copy_from_user` and `_copy_to_user` wrappers.

## Control Flow, State, and Persistence
State is user and kernel memory contents; helpers return uncopied byte counts and keep no local state.

## Dependencies and Integration
Depends on `linux/uaccess.h`, architecture user access rules, and Rust user-slice abstractions.

## Risks and Test Signals
Risks include partial copies, fault handling, missing access validation in callers, and sleeping/pagefault context constraints. Test signals are usercopy KUnit tests, fault injection, hardened usercopy, and Rust user-slice tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/uaccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/usb.c -->
# sources/distributed-fs/ceph-client/rust/helpers/usb.c

## Purpose
Exposes USB interface-to-device conversion to Rust.

## APIs, Types, and Functions
`rust_helper_interface_to_usbdev()` wraps `interface_to_usbdev()`.

## Control Flow, State, and Persistence
No local state; returns the USB device associated with an interface.

## Dependencies and Integration
Depends on `linux/usb.h` and Rust USB driver abstractions.

## Risks and Test Signals
Risks include interface lifetime misuse and missing device references if wrappers assume ownership. Test signals are Rust USB probe/disconnect tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/vmalloc.c -->
# sources/distributed-fs/ceph-client/rust/helpers/vmalloc.c

## Purpose
Exposes aligned vmalloc realloc for Rust virtual-memory allocators.

## APIs, Types, and Functions
`rust_helper_vrealloc_node_align()` wraps `vrealloc_node_align()`.

## Control Flow, State, and Persistence
State is vmalloc allocation ownership; no helper-local state.

## Dependencies and Integration
Depends on `linux/vmalloc.h` and Rust `Vmalloc` allocator implementation.

## Risks and Test Signals
Risks include alignment/size mismatches, pointer loss on failure, NUMA behavior assumptions, and page-iterator safety. Test signals are Rust allocator KUnit alignment tests and large allocation growth/shrink cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/vmalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/wait.c -->
# sources/distributed-fs/ceph-client/rust/helpers/wait.c

## Purpose
Exposes waitqueue-entry initialization to Rust.

## APIs, Types, and Functions
`rust_helper_init_wait()` wraps `init_wait()`.

## Control Flow, State, and Persistence
Initializes caller-owned waitqueue entry state; no local state.

## Dependencies and Integration
Depends on `linux/wait.h` and Rust waitqueue abstractions.

## Risks and Test Signals
Risks include adding uninitialized or stack-expired entries to waitqueues. Test signals are Rust waitqueue tests and wakeup race stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/workqueue.c -->
# sources/distributed-fs/ceph-client/rust/helpers/workqueue.c

## Purpose
Exposes a Rust-oriented work item initialization helper with lockdep metadata.

## APIs, Types, and Functions
`rust_helper_init_work_with_key()` initializes work data, lockdep map, list head, and function pointer using `__init_work()` and `WORK_DATA_INIT()`.

## Control Flow, State, and Persistence
State is caller-owned `work_struct` initialization and lockdep class association.

## Dependencies and Integration
Depends on `linux/workqueue.h` and Rust workqueue abstractions.

## Risks and Test Signals
Risks include reinitializing queued work, function pointer lifetime/ABI mismatch, and lock class key lifetime. Test signals are Rust workqueue queue/cancel tests and debugobjects/lockdep builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/workqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/xarray.c -->
# sources/distributed-fs/ceph-client/rust/helpers/xarray.c

## Purpose
Exposes selected xarray initialization, error, and locking helpers to Rust.

## APIs, Types, and Functions
APIs include `xa_err`, `xa_init_flags`, `xa_trylock`, `xa_lock`, and `xa_unlock` wrappers.

## Control Flow, State, and Persistence
State is caller-owned xarray flags and lock state; helper calls mutate or inspect that object.

## Dependencies and Integration
Depends on `linux/xarray.h` and Rust xarray abstractions.

## Risks and Test Signals
Risks include lock imbalance, storing error entries incorrectly, and reinitializing populated arrays. Test signals are Rust xarray insertion/removal/iteration tests and lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/helpers/xarray.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/acpi.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/acpi.rs

## Purpose
Defines Rust ACPI device-id table support used by Rust drivers to advertise ACPI match data.

## APIs, Types, and Functions
`IdTable<T>` aliases a static dynamic `device_id::IdTable<DeviceId, T>`. `DeviceId` wraps `bindings::acpi_device_id` and implements `RawDeviceId` and `RawDeviceIdIndex`. Constructors include `DeviceId::new(id, info)` and `DeviceId::new_with_data(id, data)`. The exported `acpi_device_table!` macro emits a static ACPI id table with optional match data.

## Control Flow, State, and Persistence
There is no runtime mutable state in this file. Match tables are static data emitted into the driver/module image; driver core consumes them during ACPI device matching. Raw index access returns the integer driver-data field from the generated C-compatible table entry.

## Dependencies and Integration
Depends on generated ACPI bindings, `kernel::device_id` traits, and Rust macro support. It integrates with Rust driver declarations and Linux ACPI match-table conventions.

## Risks and Test Signals
Risks include ACPI id string length/termination constraints, incorrect `driver_data` casting, table lifetime assumptions, and mismatch between Rust type data and C `kernel_ulong_t`. Test signals are Rust ACPI driver registration tests, compile-time table generation, and matching devices with and without associated data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/acpi.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/alloc.rs

## Purpose
Defines the public Rust kernel allocation module surface: allocator traits, allocation flags, NUMA node identifiers, allocation errors, and re-exports of box/vector types.

## APIs, Types, and Functions
Exports modules `allocator`, `kbox`, `kvec`, and `layout`; re-exports `Box`, `KBox`, `VBox`, `KVBox`, `Vec`, `KVec`, `VVec`, and `KVVec`. `AllocError` represents allocation failure. `Flags` wraps GFP bits and implements `BitOr`, `BitAnd`, `Not`, and `contains()`. `flags` exposes GFP constants and modifiers. `NumaNode::new()` validates node ids, while `NumaNode::NO_NODE` represents no preference. The unsafe `Allocator` trait defines `MIN_ALIGN`, `alloc()`, unsafe `realloc()`, and unsafe `free()`. `dangling_from_layout()` provides aligned dangling pointers for zero-sized allocations.

## Control Flow, State, and Persistence
Control flow centers on `Allocator::alloc()` delegating to `realloc(None, ...)` and `free()` delegating to `realloc(Some, zero-sized layout, ...)`. Persistent state is not held by this module, but trait implementers return allocations that remain valid until freed or reallocated. NUMA and GFP flags are passed through to the underlying kernel allocator.

## Dependencies and Integration
Depends on generated bindings for GFP constants and NUMA limits, Rust `Layout`/`NonNull`, and concrete implementations in `allocator.rs`. It is the foundation for all heap-owning Rust kernel containers.

## Risks and Test Signals
Risks include unsafe implementers violating allocation/lifetime guarantees, zero-sized allocation pointer misuse, GFP flags used in invalid contexts, and NUMA id validation drifting from kernel constants. Test signals are Rust allocator KUnit tests, fallible allocation paths, zero-sized types, alignment stress, and build coverage with different NUMA settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/allocator.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/alloc/allocator.rs

## Purpose
Implements the concrete Rust kernel allocators backed by `kmalloc`, `vmalloc`, and `kvmalloc`, plus a page iterator export for vmalloc allocations.

## APIs, Types, and Functions
Defines zero-sized allocator marker types `Kmalloc`, `Vmalloc`, and `KVmalloc`. `ReallocFunc` wraps C aligned realloc helpers (`krealloc_node_align`, `vrealloc_node_align`, `kvrealloc_node_align`) and centralizes pointer/size handling. `Kmalloc::aligned_layout()` pads layouts so slab alignment satisfies Rust layout requirements. `Vmalloc::to_page()` converts a vmalloc pointer to a borrowed page. Unsafe `Allocator` impls provide `MIN_ALIGN` and delegate `realloc()` to the selected C helper. The `rust_allocator` KUnit module tests alignment for all three allocators.

## Control Flow, State, and Persistence
Allocation control flow normalizes zero-size requests to aligned dangling pointers, turns zero-size reallocation into free semantics, and preserves old allocations on failure according to C realloc helper behavior. Persistent state is heap memory owned by callers; no allocator instance state exists because the marker types are ZSTs.

## Dependencies and Integration
Depends on Rust allocation traits, generated bindings for aligned realloc helpers and alignment constants, `page::BorrowedPage`, and C helpers from `slab.c`/`vmalloc.c`. It integrates with `Box`, `Vec`, and page iteration.

## Risks and Test Signals
Risks include old-layout mismatches, incorrect padding for kmalloc alignment, assuming vmalloc memory is physically contiguous, pointer validity in `to_page()`, and C helper behavior changes. Test signals are KUnit `test_alignment`, allocation failure injection, large `KVmalloc` fallback cases, page iterator tests, and zero-sized/growth/shrink coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/allocator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/allocator/iter.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/alloc/allocator/iter.rs

## Purpose
Implements iteration over the pages backing a `Vmalloc` allocation.

## APIs, Types, and Functions
`VmallocPageIter<'a>` stores a non-null page-aligned buffer pointer, byte size, current page index, and lifetime marker. It implements `Iterator<Item = page::BorrowedPage<'a>>`, `size_hint()`, unsafe constructor `new()`, `size()`, and `page_count()`.

## Control Flow, State, and Persistence
`next()` computes `index * PAGE_SIZE` with overflow checking, stops when the offset reaches the allocation size, advances the index, derives a pointer into the allocation, and converts it to a borrowed page via `Vmalloc::to_page()`. Persistent state is the iterator index and borrowed lifetime tied to the backing allocation; it does not own the allocation.

## Dependencies and Integration
Depends on `Vmalloc::to_page()`, `crate::page::PAGE_SIZE`, `BorrowedPage`, `NonNull`, and Rust iterator conventions. It integrates with `AsPageIter` for `VBox<T>`.

## Risks and Test Signals
Risks include unsafe constructor misuse with non-vmalloc or non-page-aligned pointers, backing allocation freed while iterating, overflow for enormous sizes, and last partial page handling. Test signals are iteration over zero, one, partial, and multi-page `VBox` allocations and page-fill operations through returned borrowed pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/allocator/iter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/kbox.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/alloc/kbox.rs

## Purpose
Implements the kernel's allocator-parameterized Rust `Box` type, including kmalloc/vmalloc/kvmalloc aliases, fallible construction, pinning, in-place initialization, foreign ownership transfer, and vmalloc page iteration.

## APIs, Types, and Functions
`Box<T, A>` is a transparent wrapper around `NonNull<T>` plus allocator marker. Aliases are `KBox`, `VBox`, and `KVBox`. Core APIs include unsafe `from_raw()`, `into_raw()`, `leak()`, `new()`, `new_uninit()`, `pin()`, `pin_slice()`, `into_pin()`, `drop_contents()`, and `into_inner()`. `Box<MaybeUninit<T>, A>` supports `assume_init()` and `write()`. Trait impls cover `ZeroableOption`, `Send`, `Sync`, `From<Box> for Pin<Box>`, `InPlaceWrite`, `InPlaceInit`, `ForeignOwnable` for boxed and pinned values, `Deref`, `DerefMut`, `Borrow`, `BorrowMut`, `Display`, `Debug`, `Drop`, and `AsPageIter` for `VBox<T>`.

## Control Flow, State, and Persistence
Construction allocates with allocator `A` and GFP flags, then initializes or leaves memory uninitialized. `pin_slice()` builds a vector with capacity, initializes elements in place with pin-init callbacks, then converts raw parts into a boxed slice. Drop first drops the contained value and then frees memory using `Layout::for_value`. Foreign ownership transfers raw pointers across C/Rust boundaries without dropping until reconstructed. Persistent state is the heap allocation and initialized value owned by the box; zero-sized types use dangling aligned pointers rather than real allocations.

## Dependencies and Integration
Depends on the allocator trait, `Kmalloc`/`Vmalloc`/`KVmalloc`, `Vec`, `Layout`, `MaybeUninit`, `Pin`, `pin_init` traits, `ForeignOwnable`, formatting traits, and page iteration support. It is the primary single-owner heap abstraction for Rust kernel code.

## Risks and Test Signals
Risks include unsafe `from_raw()` allocator mismatches, `assume_init()` on uninitialized memory, pinning violations through raw pointers, allocation leaks via `leak()` or `into_raw()`, incorrect unsized layout freeing, and panic/error cleanup during `pin_slice()`. Test signals are doctests, KUnit allocator tests, Miri-like reasoning for initialization, FFI round trips through `ForeignOwnable`, drop-order checks, ZST cases, trait-object coercions, and `VBox` page iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/kbox.rs -->
