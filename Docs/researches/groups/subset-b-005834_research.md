<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/resource.h -->
# sources/distributed-fs/ceph-client/include/kunit/resource.h

## Purpose
`resource.h` defines KUnit's test-managed resource API. It lets tests attach allocations, named handles, and deferred cleanup actions to `struct kunit` so resources are released when a test ends or aborts.

## Important APIs, types, and functions
The central type is `struct kunit_resource`, which stores `data`, an optional `name`, a user-supplied `free` callback, a `kref`, a list node, and a `should_kfree` ownership flag. Public entry points include `kunit_add_resource()`, `kunit_add_named_resource()`, `kunit_alloc_resource()`, `kunit_alloc_and_get_resource()`, `kunit_find_resource()`, `kunit_find_named_resource()`, `kunit_destroy_resource()`, `kunit_remove_resource()`, and the reference helpers `kunit_get_resource()` / `kunit_put_resource()`. Deferred action helpers are exposed through `kunit_action_t`, `KUNIT_DEFINE_ACTION_WRAPPER()`, `kunit_add_action()`, `kunit_add_action_or_reset()`, `kunit_remove_action()`, and `kunit_release_action()`.

## Control flow
Resources are initialized through `__kunit_add_resource()`, inserted into `test->resources`, then found by reverse list scan under `test->lock`. Matches gain a reference before the lock is dropped. `kunit_put_resource()` calls `kref_put()`, which runs `kunit_release_resource()` when the last reference disappears. Named addition first checks for duplicate names and returns `-EEXIST`.

## State and persistence behavior
Resource state lives in the running `struct kunit` only. The list holds one reference, callers may hold more, and teardown or explicit destruction removes the list reference. `should_kfree` distinguishes KUnit-allocated `struct kunit_resource` objects from caller-owned ones.

## Dependencies and integration points
This header depends on `kunit/test.h`, `kref`, `list_head`, `spinlock`, and slab allocation. It underpins `kunit_kmalloc*`, action-based cleanup, and helper headers such as `kunit/skbuff.h`.

## Risks and test signals
Risks include leaking resources when references are not put, double cleanup if caller-owned resources set `should_kfree`, duplicate named resources, and lock/refcount races around lookup and destruction. Test signals are KUnit selftests for allocation cleanup, named lookup, deferred action LIFO ordering, duplicate-name rejection, forced `kunit_add_action_or_reset()` failure, and concurrent lookup/removal stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/run-in-irq-context.h -->
# sources/distributed-fs/ceph-client/include/kunit/run-in-irq-context.h

## Purpose
`run-in-irq-context.h` provides a KUnit helper for repeatedly running a test callback in task, softirq, and hardirq contexts. It is aimed at validating fallback paths that only execute when interrupt context or FPU/vector availability changes kernel behavior.

## Important APIs, types, and functions
`struct kunit_irq_test_state` stores the callback, caller state, failure flags for each context, atomic call counters, an adaptive `ktime_t` interval, a hard hrtimer, and a BH work item. `kunit_run_irq_test()` is the public inline helper. Internal callbacks are `kunit_irq_test_timer_func()` for hardirq context and `kunit_irq_test_bh_work_func()` for softirq context.

## Control flow
`kunit_run_irq_test()` initializes an on-stack hard hrtimer and BH work item, starts the timer, and loops in task context until `max_iterations` and at least one call from each context are observed, or one second elapses. The hrtimer callback asserts hardirq context, runs the test callback, forwards itself, and queues BH work. The BH worker asserts softirq context and runs the same callback.

## State and persistence behavior
All state is on the stack for one invocation and is cancelled/flushed before return. Atomic counters coordinate observations across contexts; boolean failure flags are sampled after all asynchronous work is drained.

## Dependencies and integration points
The header integrates KUnit assertions with `hrtimer`, `system_bh_wq`, `jiffies`, atomic counters, and interrupt-context predicates. Crypto and architecture KUnit tests can use it to exercise irq/FPU edge cases.

## Risks and test signals
Risks include callback code that is not reentrant, sleeps in interrupt context, or assumes only one caller. Very slow systems may hit the one-second timeout; the timer interval self-adjusts after repeated hardirq-only progress. Test signals are positive hardirq and softirq counters, failure flags remaining false, timer cancellation without pending work, and architecture tests that intentionally force fallback code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/run-in-irq-context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/skbuff.h -->
# sources/distributed-fs/ceph-client/include/kunit/skbuff.h

## Purpose
`skbuff.h` adds KUnit-managed `struct sk_buff` allocation and release helpers for network tests.

## Important APIs, types, and functions
`kunit_action_kfree_skb()` is the cleanup adapter passed to KUnit deferred actions. `kunit_zalloc_skb()` allocates an skb with `alloc_skb()`, pads/zeroes the requested length with `skb_pad()`, and registers automatic cleanup with `kunit_add_action_or_reset()`. `kunit_kfree_skb()` releases an skb early by invoking `kunit_release_action()`.

## Control flow
Allocation returns `NULL` if `alloc_skb()` fails, if padding fails, or if action registration fails. When action registration fails, `kunit_add_action_or_reset()` runs the cleanup action immediately, preventing a leak. Early free calls are no-ops for `NULL` and otherwise execute and remove the matching deferred action.

## State and persistence behavior
The skb itself is normal network-stack state, but its lifetime is recorded in the test's KUnit resource/action list. No persistent state is stored in the header.

## Dependencies and integration points
This helper depends on `kunit/resource.h` and `<linux/skbuff.h>`. It integrates KUnit cleanup semantics with networking tests that allocate packets, avoiding manual teardown paths when assertions abort.

## Risks and test signals
Risks include assuming `kunit_zalloc_skb()` initializes more than the padded data area, using the skb after `kunit_kfree_skb()`, and registering the same skb through another cleanup path. Test signals are skb allocation tests that abort early and still free memory, explicit early free tests, and fault-injection tests for allocation/action registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/skbuff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/static_stub.h -->
# sources/distributed-fs/ceph-client/include/kunit/static_stub.h

## Purpose
`static_stub.h` implements KUnit's static function redirection API. It lets a function opt into test-time replacement by placing a redirect macro at the start of the real function.

## Important APIs, types, and functions
`KUNIT_STATIC_STUB_REDIRECT(real_fn_name, args...)` is the prologue macro used by code under test. `kunit_activate_static_stub()` type-checks and registers a replacement through `__kunit_activate_static_stub()`. `kunit_deactivate_static_stub()` removes a replacement. When `CONFIG_KUNIT` is disabled, the redirect macro compiles to an empty statement and the activation APIs disappear.

## Control flow
The redirect macro obtains the current KUnit test with `kunit_get_current_test()`. Outside a KUnit context, it falls through to the real implementation. Inside a test, it asks `kunit_hooks.get_static_stub_address()` for a replacement keyed by the test and real function address; if present, it returns the replacement's result immediately.

## State and persistence behavior
Redirection state is per-test and maintained by the KUnit core, not in this header. It should be activated for a specific test and deactivated or allowed to be cleaned with test resources.

## Dependencies and integration points
The header integrates with `kunit/test-bug.h` hooks, current-task KUnit context, compiler `typecheck_fn()`, and branch prediction macros. It is an opt-in testing seam for static functions without exporting symbols globally.

## Risks and test signals
Risks include missing the prologue in the real function, mismatched replacement signatures, recursive replacement calls, and unexpected behavior if production code runs under an active KUnit test context. Test signals include replacement success, fallthrough outside KUnit, type-check compile failures for wrong signatures, and deactivation restoring the real function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/static_stub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/test-bug.h -->
# sources/distributed-fs/ceph-client/include/kunit/test-bug.h

## Purpose
`test-bug.h` exposes low-overhead hooks that let ordinary kernel code detect and fail the currently running KUnit test, without depending on the full test framework when KUnit is disabled.

## Important APIs, types, and functions
When `CONFIG_KUNIT` is enabled, the header declares the `kunit_running` static key and `kunit_hooks`, containing `fail_current_test()` and `get_static_stub_address()` callbacks. `kunit_get_current_test()` returns `current->kunit_test` only when the static key says tests are running. `kunit_fail_current_test(fmt, ...)` reports a failure through the hooks. Without KUnit, these APIs compile to `NULL`/no-op behavior.

## Control flow
Both helper paths first check `static_branch_unlikely(&kunit_running)`. This keeps production code cheap when no KUnit test is executing. The failure macro passes `__FILE__`, `__LINE__`, and the formatted message to the KUnit hook table.

## State and persistence behavior
The only persistent state declared here is the global static key and hook table, populated by KUnit core code. Per-test identity lives on `current->kunit_test`.

## Dependencies and integration points
This header integrates scheduler task state, jump labels, static stubs, and failure reporting. It is included by static-stub support and by code that wants to convert internal bug checks into KUnit failures during tests.

## Risks and test signals
Risks include assuming `kunit_running` means every task has a current test, using the fail macro outside a task-associated test, and hook table misuse during module load/unload. Test signals include no-op behavior without KUnit, current-test detection only in the test task, and accurate file/line failure reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/test-bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/test.h -->
# sources/distributed-fs/ceph-client/include/kunit/test.h

## Purpose
`test.h` is the main KUnit public API. It defines test cases, suites, running test state, suite registration, test-managed allocation helpers, logging, skip/fail mechanics, expectations, assertions, and parameterized-test helpers.

## Important APIs, types, and functions
Core types include `enum kunit_status`, `enum kunit_speed`, `struct kunit_attributes`, `struct kunit_case`, `struct kunit_suite`, `struct kunit_suite_set`, `struct kunit_params`, and `struct kunit`. Registration macros include `KUNIT_CASE*`, `kunit_test_suites()`, `kunit_test_suite()`, and init-section variants. Runtime APIs include `kunit_init_test()`, `kunit_run_tests()`, suite filtering/listing helpers, `kunit_cleanup()`, `kunit_kmalloc_array()`, `kunit_kfree()`, `kunit_kstrdup_const()`, `kunit_vm_mmap()`, `kunit_mark_skipped()`, and `kunit_skip()`. Assertion families include `KUNIT_EXPECT_*` and `KUNIT_ASSERT_*` for booleans, integers, pointers, strings, memory, NULL, and error pointers.

## Control flow
Suites are registered by placing pointers in dedicated ELF sections. The executor filters and runs suites, invoking optional suite init/exit and per-test init/exit. Expectations record failures and continue; assertions route through `__kunit_do_failed_assertion()` and then abort via `__kunit_abort()` / `kunit_try_catch_throw()`. Parameter generators lazily provide values and descriptions for repeated case execution.

## State and persistence behavior
`struct kunit` owns per-case mutable state: status, resources, logs, parameter value/index, last-seen location, parent context, and private fixture data. `struct kunit_suite` stores suite-wide status comments, debugfs/log pointers, and init status. Test-managed allocations persist until cleanup unless released early.

## Dependencies and integration points
The API depends on KUnit assertion definitions, try/catch, list/spinlock/slab/string helpers, module infrastructure, static keys, and linker sections. It integrates with debugfs logging, TAP-style output, module load/unload, boot-time built-in test execution, and memory mapping helpers.

## Risks and test signals
Risks include side effects in assertion expressions, continuing after failed expectations when code required an assertion, parameter arrays with stale lifetime, resources touched from multiple threads without cleanup synchronization, and linker-section registration mistakes. Test signals include KUnit selftests, compile coverage of assertion macro type handling, suite filtering/listing behavior, skip output, resource cleanup after aborts, and parameterized test enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/try-catch.h -->
# sources/distributed-fs/ceph-client/include/kunit/try-catch.h

## Purpose
`try-catch.h` declares KUnit's generic abort/recovery primitive used to implement assertions and controlled test bailouts.

## Important APIs, types, and functions
`kunit_try_catch_func_t` is a `void (*)(void *)` callback type. `struct kunit_try_catch` stores the owning `struct kunit`, a `try_result` errno-style result, `try` and `catch` callbacks, a timeout, and caller context. `kunit_try_catch_run()` executes a try/catch pair. `kunit_try_catch_throw()` is `__noreturn` and aborts the try path. `kunit_try_catch_get_result()` returns the recorded result.

## Control flow
KUnit code sets up the structure, runs the try callback, and lets assertions or skips call `kunit_try_catch_throw()` to stop execution. The catch callback then handles the abort path and records the result. The implementation is architecture-independent at the interface level.

## State and persistence behavior
State is per active try/catch invocation and embedded in `struct kunit`. `try_result` is the durable outcome after execution; callback context remains caller-owned.

## Dependencies and integration points
The header depends only on basic kernel types and a forward `struct kunit`. `kunit/test.h` embeds it in `struct kunit` and uses it for `KUNIT_ASSERT_*`, `KUNIT_FAIL_AND_ABORT`, and `kunit_skip()`.

## Risks and test signals
Risks include throwing without a valid active try/catch, catch paths that assume fully initialized fixture state, and timeout behavior differing across architectures. Test signals include assertions aborting exactly one test case, expectations not aborting, skip reporting, and correct `try_result` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/try-catch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/visibility.h -->
# sources/distributed-fs/ceph-client/include/kunit/visibility.h

## Purpose
`visibility.h` provides macros for symbols that should be private in production builds but visible/exported for KUnit builds.

## Important APIs, types, and functions
`VISIBLE_IF_KUNIT` expands to nothing when `CONFIG_KUNIT` is enabled and to `static` otherwise. `EXPORT_SYMBOL_IF_KUNIT(symbol)` exports into the `EXPORTED_FOR_KUNIT_TESTING` namespace only with KUnit enabled; otherwise it emits nothing.

## Control flow
There is no runtime control flow. The macros alter linkage and module export tables at compile time.

## State and persistence behavior
No runtime state is created. The persistent effect is the presence or absence of exported symbols and symbol visibility in the built kernel/module.

## Dependencies and integration points
The header relies on Kconfig state and `EXPORT_SYMBOL_NS()` being available from included kernel headers in users. KUnit test modules must import `EXPORTED_FOR_KUNIT_TESTING` when using the exported symbols.

## Risks and test signals
Risks include accidentally exposing production-only ABI when KUnit is enabled, tests depending on internals too strongly, and missing namespace imports. Test signals are build tests with KUnit on/off, module namespace checks, and confirming non-KUnit builds keep helper symbols static/unexported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/visibility.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_arch_timer.h -->
# sources/distributed-fs/ceph-client/include/kvm/arm_arch_timer.h

## Purpose
`arm_arch_timer.h` declares ARM/arm64 KVM architectural timer state, timer register accessors, VM/VCPU lifecycle hooks, and helpers for mapping virtual and physical guest timers to emulated or direct hardware paths.

## Important APIs, types, and functions
Important enums are `kvm_arch_timers` and `kvm_arch_timer_regs`. Key structs are `arch_timer_offset`, `arch_timer_vm_data`, `arch_timer_context`, `timer_map`, and `arch_timer_cpu`. APIs include `kvm_timer_hyp_init()`, `kvm_timer_enable()`, VCPU init/reset/load/put/terminate functions, user attribute accessors, `kvm_phys_timer_read()`, `kvm_arm_timer_read_sysreg()`, `kvm_arm_timer_write_sysreg()`, trace helpers, and CPU hotplug callbacks.

## Control flow
KVM initializes VM-wide offsets and PPIs, initializes each VCPU's timer contexts, loads timer state when a VCPU enters the guest, puts it on exit, and uses background hrtimers for non-running guests. `get_timer_map()` selects direct versus emulated timer contexts. Sysreg helpers read/write CNT/CVAL/TVAL/CTL/VOFF state.

## State and persistence behavior
VM timer state includes virtual/physical offsets and PPI numbers. VCPU state includes per-timer hrtimers, fractional nanosecond accounting, loaded flags, IRQ output level, and host timer IRQ. Offsets can be VM-wide or per-VCPU, and `timer_set_offset()` writes only VM-backed offsets.

## Dependencies and integration points
The header depends on hrtimers, clocksource logic, GICv5 IRQ encoding, static keys, CPU capability helpers, and `struct kvm_vcpu` architecture fields. It integrates with VGIC interrupt injection, userspace KVM device attributes, tracing, hyp initialization, and CPU hotplug.

## Risks and test signals
Risks include stale loaded state across VCPU switches, incorrect offset handling on broken CNTVOFF or ECV/CNTPOFF systems, wrong PPI encoding for GICv5, and timer IRQ level drift. Test signals include KVM timer selftests, migration/user attribute tests, nested timer synchronization, CPU hotplug testing, and guest clock/interrupt accuracy checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_arch_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_hypercalls.h -->
# sources/distributed-fs/ceph-client/include/kvm/arm_hypercalls.h

## Purpose
`arm_hypercalls.h` declares ARM KVM handling for SMCCC firmware/hypervisor calls and exposes helpers for decoding call registers and managing firmware register attributes.

## Important APIs, types, and functions
`kvm_smccc_call_handler()` is the main call dispatch entry. Inline helpers `smccc_get_function()`, `smccc_get_arg1()`, `smccc_get_arg2()`, `smccc_get_arg3()`, and `smccc_set_retval()` read/write guest registers x0-x3 through KVM emulation helpers. Lifecycle and userspace APIs include `kvm_arm_init_hypercalls()`, `kvm_arm_teardown_hypercalls()`, firmware one-reg enumeration/copy/get/set functions, and VM SMCCC device attribute set/has helpers.

## Control flow
When a guest traps an SMCCC call, the handler reads x0 for the function ID and x1-x3 for arguments, dispatches internally, and writes return values back to x0-x3. VM initialization configures available hypercall features and teardown releases any VM-owned state.

## State and persistence behavior
State is VM-scoped hypercall capability/configuration maintained in `struct kvm`; this header only declares access. Firmware register state is exposed through the KVM one-reg/userspace attribute interfaces for migration and configuration.

## Dependencies and integration points
The file depends on `asm/kvm_emulate.h`, `struct kvm_vcpu`, userspace pointers, `struct kvm_one_reg`, and KVM device attributes. It integrates with PSCI, SMCCC feature discovery, guest firmware ABI emulation, and migration tooling.

## Risks and test signals
Risks include clobbering the wrong guest registers, misreporting SMCCC feature availability, incomplete one-reg migration state, and ABI mismatches between userspace and KVM. Test signals include SMCCC/PSCI guest tests, KVM one-reg enumeration round trips, migration compatibility tests, and negative attribute validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_hypercalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_pmu.h -->
# sources/distributed-fs/ceph-client/include/kvm/arm_pmu.h

## Purpose
`arm_pmu.h` defines ARM PMUv3 virtualization interfaces for KVM VCPUs and supplies no-op stubs when hardware perf events or KVM PMU support are disabled.

## Important APIs, types, and functions
With support enabled, it defines `KVM_ARMV8_PMU_MAX_COUNTERS`, `struct kvm_pmc`, `struct kvm_pmu_events`, `struct kvm_pmu`, and `struct arm_pmu_entry`. APIs cover support detection, counter read/write, implemented/access masks, PMCEID, VCPU init/destroy, counter reprogramming, hwstate flush/sync, run notification, software increment, PMCR handling, event type setup, PMU reload, KVM device attributes, PMUv3 enablement, host/guest PMU state restore, PMU version/counter limits, event type masking, default PMU selection, and nested transition.

## Control flow
VCPU PMU state is initialized during VCPU setup, programmed before guest entry, synced/flushed around runs, and restored between host and guest contexts. `kvm_pmu_update_vcpu_events()` copies per-CPU PMU event masks with interrupts disabled on non-VHE systems.

## State and persistence behavior
`struct kvm_pmu` stores perf-event-backed counters, overflow irq work, event masks, IRQ number/level, and created state. Counter values and device attributes are part of VCPU/VM migration-visible state.

## Dependencies and integration points
The header integrates KVM, Linux perf events, ARM PMUv3 definitions, IRQ work, VCPU feature bits, and KVM device attribute plumbing. Stub definitions return false, zero, `-ENXIO`, or `-ENODEV` so callers can compile unconditionally.

## Risks and test signals
Risks include host/guest PMU state leaks, incorrect counter accessibility masks, IRQ level mismatches, unsupported builds silently taking stubs, and nested virtualization transitions losing hyp counters. Test signals include KVM PMU selftests, perf event lifecycle tests, migration of PMU state, IRQ overflow tests, and builds with PMU support disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_psci.h -->
# sources/distributed-fs/ceph-client/include/kvm/arm_psci.h

## Purpose
`arm_psci.h` declares ARM KVM's PSCI version constants and PSCI call entry point.

## Important APIs, types, and functions
The header maps KVM PSCI version constants from `PSCI_VERSION()` for versions 0.1 through 1.3 and defines `KVM_ARM_PSCI_LATEST`. `kvm_psci_version()` selects the guest-visible version for a VCPU. `kvm_psci_call()` handles trapped PSCI calls.

## Control flow
`kvm_psci_version()` returns PSCI 0.1 unless the VCPU has `KVM_ARM_VCPU_PSCI_0_2`; for v0.2-capable VCPUs, it returns a userspace-configured VM PSCI version if present, otherwise the latest supported version. The call handler is implemented elsewhere and uses this version decision when emulating firmware functions.

## State and persistence behavior
PSCI version state is VM-scoped through `vcpu->kvm->arch.psci_version`, with VCPU feature flags controlling the legacy v0.1 path. The version is migration/user-configuration relevant.

## Dependencies and integration points
The header depends on KVM host structures and UAPI PSCI definitions. It integrates with SMCCC/hypercall dispatch, guest CPU on/off/reset behavior, and userspace VM configuration.

## Risks and test signals
Risks include exposing a newer PSCI version than userspace intended, mishandling legacy v0.1 guests, and migration incompatibility if configured version is lost. Test signals include PSCI feature/version guest tests, CPU hotplug/reset tests, and migration of `arch.psci_version`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_psci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_vgic.h -->
# sources/distributed-fs/ceph-client/include/kvm/arm_vgic.h

## Purpose
`arm_vgic.h` defines ARM KVM's virtual GIC data model and APIs for GICv2, GICv3, GICv4 forwarding, and GICv5 support. It is the shared contract between KVM core, VGIC MMIO devices, ITS/LPI handling, VCPU world-switch state, and in-kernel interrupt injection.

## Important APIs, types, and functions
The header defines INTID limits and classification helpers for SGI/PPI/SPI/LPI, including GICv5 hardware IRQ encoding helpers. Key types include `vgic_global`, `irq_ops`, `vgic_irq`, `vgic_io_device`, `vgic_its`, `vgic_redist_region`, `vgic_v5_vm`, `vgic_dist`, `vgic_v2_cpu_if`, `vgic_v3_cpu_if`, `vgic_v5_cpu_if`, `vgic_v5_ppi_caps`, and `vgic_cpu`. APIs cover creation/destruction, VCPU init/destroy, resource mapping, hyp init, IRQ injection, IRQ owner/ops setup, physical IRQ mapping, load/put, hwstate sync/flush, SGI dispatch, default routing, GICv4 forwarding, GICv5 PPI finalization, nested-state checks, and CPU hotplug.

## Control flow
VM setup chooses a VGIC model, initializes distributor/redistributor/ITS state, maps MMIO iodev regions, and initializes per-VCPU private interrupts and CPU interface state. Guest MMIO and sysreg paths mutate `vgic_irq` and distributor state under locks. Before guest entry KVM loads CPU interface state; on exit it syncs or flushes hardware state and handles pending/active lists.

## State and persistence behavior
Persistent VM state includes distributor addresses, enabled/ready flags, SPI/LPI arrays, ITS tables, GICv4 VM data, GICv5 PPI masks, implementation revision, and routing properties. Per-VCPU state includes private IRQs, AP lists, redistributor mapping, pending table address, priority/id-bit caches, and CPU interface registers. Many fields are migration-visible.

## Dependencies and integration points
The header depends on KVM MMIO iodev support, xarrays, mutexes, raw spinlocks, static keys, irqchip GICv4/GICv5 definitions, and KVM userspace device attributes. It integrates with irq routing, in-kernel devices, ITS emulation, physical interrupt forwarding, nested virtualization, CPU hotplug, and timer/PMU PPIs.

## Risks and test signals
Risks include INTID classification errors across GIC versions, AP-list races, wrong LPI translation-cache invalidation, mismatched migration ABI revision, physical IRQ forwarding leaks, and GICv5 PPI mask inconsistencies. Test signals include KVM VGIC selftests, irq routing/injection tests, ITS/MSI tests, migration save/restore, nested VGIC tests, CPU hotplug, and GICv2/v3/v5 configuration builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_vgic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/iodev.h -->
# sources/distributed-fs/ceph-client/include/kvm/iodev.h

## Purpose
`iodev.h` defines KVM's small polymorphic interface for memory-mapped or port I/O devices attached to a VM address space.

## Important APIs, types, and functions
`struct kvm_io_device_ops` contains optional `read`, `write`, and `destructor` callbacks. `struct kvm_io_device` stores the ops table. `kvm_iodevice_init()` assigns operations. `kvm_iodevice_read()` and `kvm_iodevice_write()` dispatch to callbacks or return `-EOPNOTSUPP`.

## Control flow
KVM bus code locates a registered iodev under `slots_lock`, then invokes read/write. A callback returning zero means the transaction was handled; nonzero lets the bus continue to another device. The inline wrappers only handle callback presence and dispatch.

## State and persistence behavior
The only state in the base object is the ops pointer. Device-specific state is carried by embedding `struct kvm_io_device` in a larger structure, such as VGIC MMIO device objects.

## Dependencies and integration points
The header depends on KVM types, `gpa_t`, errno values, and `struct kvm_vcpu`. It integrates with VM bus registration, VGIC/IOAPIC/PIT-style in-kernel devices, and MMIO emulation.

## Risks and test signals
Risks include registering partially initialized ops, callbacks that mishandle length/endian behavior, destructor lifetime bugs, and relying on `-EOPNOTSUPP` semantics incorrectly. Test signals include MMIO read/write routing tests, fallback-to-next-device behavior, and device unregister/destructor tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/iodev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/8250_pci.h -->
# sources/distributed-fs/ceph-client/include/linux/8250_pci.h

## Purpose
`8250_pci.h` declares the PCI-facing configuration contract for 8250 serial adapters.

## Important APIs, types, and functions
Flag macros encode BAR selection (`FL_BASE*`, `FL_GET_BASE()`), successive BAR mode (`FL_BASE_BARS`), IRQ suppression (`FL_NOIRQ`), and BAR-size port count capping (`FL_REGION_SZ_CAP`). `struct pciserial_board` describes port count, base baud, UART register offset/shift, first offset, and flags. Lifecycle APIs are `pciserial_init_ports()`, `pciserial_remove_ports()`, `pciserial_suspend_ports()`, and `pciserial_resume_ports()`.

## Control flow
The 8250 PCI driver passes a `pci_dev` and board description into init, which discovers and registers serial ports. Remove/suspend/resume operate on the opaque `serial_private` returned at init.

## State and persistence behavior
Persistent state lives in `struct serial_private` and serial-core registrations, not in the header. The board description is static driver data.

## Dependencies and integration points
It integrates PCI enumeration with the 8250 serial core and power management. Consumers need `struct pci_dev` and serial-private definitions from implementation files.

## Risks and test signals
Risks include wrong BAR selection, incorrect UART stride/offset, IRQ misconfiguration, and suspend/resume mismatches. Test signals include PCI serial probe/remove, multi-port cards, no-IRQ boards, BAR-size constrained boards, and system suspend/resume tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/8250_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acct.h -->
# sources/distributed-fs/ceph-client/include/linux/acct.h

## Purpose
`acct.h` provides kernel-side BSD process accounting definitions, version selection, lifecycle hooks, and time conversion helpers.

## Important APIs, types, and functions
When `CONFIG_BSD_PROCESS_ACCT` is enabled, it declares `acct_collect()`, `acct_process()`, and `acct_exit_ns()`. Otherwise they are no-op macros. It selects `ACCT_VERSION`, `AHZ`, and `acct_t` based on `CONFIG_BSD_PROCESS_ACCT_V3` and `CONFIG_M68K`. Inline helpers `jiffies_to_AHZ()` and `nsec_to_AHZ()` convert kernel time units into accounting ticks.

## Control flow
Accounting-enabled kernels collect exit data, write process records, and clean namespace accounting state through the declared hooks. Conversion helpers choose exact arithmetic paths where possible and use scaled division otherwise.

## State and persistence behavior
The header declares hooks for persistent accounting logs and namespace accounting state, but does not store state itself. The accounting record format is persistent ABI and depends on `ACCT_VERSION`.

## Dependencies and integration points
It includes UAPI accounting layouts and `linux/jiffies.h`, and integrates process exit, pid namespaces, and user tools that parse accounting records.

## Risks and test signals
Risks include record-format incompatibility, time conversion overflow/precision loss, and disabled-config stubs hiding accounting calls. Test signals include accton/process-exit tests, namespace teardown, record parser compatibility, and conversion tests for HZ/AHZ combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi.h

## Purpose
`linux/acpi.h` is the main Linux ACPI interface header. It bridges ACPICA types with Linux devices, firmware nodes, table parsing, interrupt routing, resources, DMA/IOMMU setup, power management, hotplug, properties, platform matching, topology, and ACPI-disabled stubs.

## Important APIs, types, and functions
Major surfaces include companion helpers (`ACPI_COMPANION`, `ACPI_HANDLE`, `has_acpi_companion()`), IRQ model enums, table parsing APIs, debugger ops, CPU/NUMA mapping, GSI/IOAPIC/PCI IRQ helpers, WMI calls, video/backlight flags, thermal trip helpers, resource conversion (`acpi_dev_get_resources()` and friends), `_OSC` context/capability macros, matching/enumeration helpers, GTDT, GPIO/property APIs, probe-table macros, SPCR/watchdog helpers, IRQ affinity, PPTT topology helpers, FFH/PCC init, device notification, sleep/PM hooks, and ACPI logging macros. The non-`CONFIG_ACPI` half provides stubs returning `NULL`, false, zero, or `-ENODEV`.

## Control flow
ACPI boot code initializes tables, parses subtables, configures interrupt domains, maps CPUs/NUMA nodes, and enumerates devices. Driver probe paths use companion/fwnode helpers, resources, DMA/IOMMU configuration, and property APIs. Power paths call ACPI PM attach/suspend/resume hooks. `_OSC` helpers negotiate platform capability ownership.

## State and persistence behavior
Declared global state includes ACPI IRQ model, SCI IRQ metadata, OSI/video support flags, `_OSC` acknowledgements, PNP ACPI state, CMOS RTC presence, and platform quirk flags. Many APIs expose firmware-derived persistent configuration that affects device lifetime and migration-independent boot behavior.

## Dependencies and integration points
The header has very high fanout: ACPICA, firmware tables, Linux driver core/fwnode/property APIs, IRQ domains, PCI, WMI, thermal, GPIO, DMA/IOMMU, PM, topology, and architecture ACPI hooks. It is intentionally full of conditional stubs so generic drivers can compile without ACPI.

## Risks and test signals
Risks include stub behavior diverging from enabled behavior, table parser bounds mistakes, resource translation errors, incorrect `_OSC` ownership, IRQ trigger/polarity mismatches, and device lifetime bugs around ACPI companions. Test signals include ACPI boot on multiple architectures, table parser tests, driver probe with ACPI and non-ACPI configs, suspend/resume, hotplug, GPIO/resource translation, and sparse/compile coverage of disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_amd_wbrf.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_amd_wbrf.h

## Purpose
`acpi_amd_wbrf.h` declares AMD ACPI Wifi Band Exclusion/WBRF interfaces for producers and consumers of active frequency band ranges.

## Important APIs, types, and functions
Constants define up to `MAX_NUM_OF_WBRF_RANGES`, record actions `WBRF_RECORD_ADD` and `WBRF_RECORD_REMOVE`, and notifier action `WBRF_CHANGED`. `struct freq_band_range` stores start/end frequencies in Hz. `struct wbrf_ranges_in_out` carries a count and fixed band array. Enabled APIs include producer/consumer support checks, add/remove, frequency-band retrieval, and notifier register/unregister. Disabled stubs return false or `-ENODEV`.

## Control flow
Producer devices publish or remove frequency ranges. Consumers check support, retrieve active ranges, and subscribe to notifier updates to react to changes.

## State and persistence behavior
Active WBRF records are platform/ACPI-managed state outside this header. The fixed-size array bounds the persisted record payload exchanged with firmware.

## Dependencies and integration points
It depends on `struct device` and Linux notifier blocks. Integration points are AMD ACPI platform code, Wi-Fi/radio consumers, and frequency-conflict mitigation logic.

## Risks and test signals
Risks include range count overflow, Hz unit mistakes, stale consumer state after notifier failure, and disabled stubs being ignored. Test signals include ACPI WBRF producer/consumer probe paths, notifier update tests, max-range validation, and non-AMD/non-WBRF builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_amd_wbrf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_dma.h

## Purpose
`acpi_dma.h` declares ACPI-based DMA controller registration and slave-channel lookup helpers.

## Important APIs, types, and functions
`struct acpi_dma_spec` carries channel ID, slave request line, and controller device. `struct acpi_dma` represents a registered controller with list node, device, xlate callback, private data, and CSRT request-line range. `struct acpi_dma_filter_info` is used by simple translation. APIs include controller register/free, devm registration, channel requests by index/name, and `acpi_dma_simple_xlate()`. Disabled stubs return `-ENODEV`, `ERR_PTR(-ENODEV)`, or `NULL`.

## Control flow
DMA controllers register an ACPI translation callback. Slave devices request channels, ACPI resources are parsed into `acpi_dma_spec`, and the controller callback maps the spec to a `dma_chan`.

## State and persistence behavior
Controller registration creates global/listed DMA controller state. Requests return normal dmaengine channel state; the header itself stores no state.

## Dependencies and integration points
It integrates ACPI CSRT/resource parsing with the dmaengine subsystem, `struct device`, and optional devm lifetime management.

## Risks and test signals
Risks include wrong request-line range handling, leaking controller registrations, mismatched channel names/indexes, and callers failing to handle `ERR_PTR`. Test signals include ACPI DMA controller probe/remove, devm cleanup, channel lookup by index/name, and builds without `CONFIG_DMA_ACPI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_iort.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_iort.h

## Purpose
`acpi_iort.h` declares ACPI IORT helpers for MSI mapping, ITS translation, IOMMU configuration, reserved memory regions, PMCG metadata, and domain-token lookup.

## Important APIs, types, and functions
Macros extract IORT IRQ number/trigger fields and define SMMUv3 PMCG model IDs. Token APIs include `iort_register_domain_token()`, deregister/find, and `iort_iwb_handle()`. With `CONFIG_ACPI_IORT`, it declares MSI ID mapping/translation, ITS physical address translation, device IRQ domain lookup, PMSI info, PMSI domain configuration, RMR SID list handling, DMA range lookup, IOMMU configure-by-ID, reserved-region enumeration, and max CPU address lookup. Disabled stubs preserve identity IDs or return no support.

## Control flow
During ACPI enumeration, IORT tables map requester IDs to interrupt controllers and IOMMUs. Device setup calls into these helpers to configure MSI domains, IOMMU fwnodes, DMA limits, and reserved memory regions.

## State and persistence behavior
Domain tokens and parsed IORT relationships are firmware-derived kernel state. RMR SID lists are caller-managed list state populated from table data.

## Dependencies and integration points
The header depends on ACPI, fwnode, irqdomain, IOMMU, MSI, and device core concepts. It is central for arm64 ACPI PCI/platform device DMA and interrupt routing.

## Risks and test signals
Risks include identity fallback masking missing IORT support, incorrect requester-ID translation, broken reserved-region propagation, and DMA limit errors. Test signals include ACPI IORT boot on SMMU systems, MSI delivery, IOMMU group setup, reserved memory tests, PMCG driver probe, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_iort.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_mdio.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_mdio.h

## Purpose
`acpi_mdio.h` provides an ACPI-aware MDIO bus registration wrapper for Ethernet PHY buses.

## Important APIs, types, and functions
When `CONFIG_ACPI_MDIO` is enabled, `__acpi_mdiobus_register()` registers an MDIO bus with a firmware node and owner module, while `acpi_mdiobus_register()` wraps it with `THIS_MODULE`. When disabled, `acpi_mdiobus_register()` falls back to ordinary `mdiobus_register()`.

## Control flow
Network drivers call the wrapper during probe. Enabled builds register with ACPI child/PHY discovery; disabled builds use generic MDIO registration to keep drivers source-compatible.

## State and persistence behavior
The MDIO core owns bus and PHY device state after registration. The header adds no persistent state.

## Dependencies and integration points
It depends on `linux/phy.h`, `struct mii_bus`, fwnodes, modules, and MDIO/PHY registration.

## Risks and test signals
Risks include owner-module mismatch, missing ACPI PHY discovery, and fallback behavior hiding ACPI-specific probe failures. Test signals include ACPI-described PHY enumeration, non-ACPI MDIO registration, module unload, and builds with/without `CONFIG_ACPI_MDIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_mdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_pmtmr.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_pmtmr.h

## Purpose
`acpi_pmtmr.h` declares ACPI PM timer constants and early read/suspend callback helpers for x86 PM timer users.

## Important APIs, types, and functions
It defines `PMTMR_TICKS_PER_SEC`, `ACPI_PM_MASK`, and `ACPI_PM_OVRRUN`. With `CONFIG_X86_PM_TIMER`, it declares `acpi_pm_read_verified()`, `pmtmr_ioport`, `acpi_pm_read_early()`, and suspend/resume callback registration/unregistration. Without the config, `acpi_pm_read_early()` returns zero.

## Control flow
Early readers check `pmtmr_ioport`; if present, they read the verified PM timer value and mask it to 24 bits. Callback registration lets one consumer observe suspend/resume transitions.

## State and persistence behavior
`pmtmr_ioport` is global platform state. The callback registration persists until unregistered.

## Dependencies and integration points
The header depends on clocksource masks and x86 ACPI PM timer support. It integrates clock calibration, early timekeeping, and suspend/resume paths.

## Risks and test signals
Risks include treating zero as a valid timer when no IO port exists, 24-bit wrap handling mistakes, and callback lifetime issues. Test signals include PM timer calibration, suspend/resume callback invocation, early boot reads, and non-x86/disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_pmtmr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_rimt.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_rimt.h

## Purpose
`acpi_rimt.h` declares RISC-V ACPI RIMT IOMMU registration and per-device IOMMU configuration helpers.

## Important APIs, types, and functions
With `CONFIG_ACPI_RIMT`, `rimt_iommu_register()` registers an IOMMU device described by RIMT. With both `CONFIG_IOMMU_API` and `CONFIG_ACPI_RIMT`, `rimt_iommu_configure_id()` configures a device for a given ID. Disabled stubs return `-ENODEV`.

## Control flow
ACPI enumeration registers RIMT IOMMU devices, then device setup calls configure-by-ID to bind devices to the right IOMMU translation path.

## State and persistence behavior
Firmware-derived IOMMU registration and device/IOMMU bindings persist in the IOMMU core; the header stores no state.

## Dependencies and integration points
It integrates ACPI RIMT parsing with Linux device and IOMMU APIs, primarily for RISC-V ACPI systems.

## Risks and test signals
Risks include missing support being surfaced only as `-ENODEV`, incorrect ID binding, and mismatches between RIMT parsing and IOMMU API availability. Test signals include RISC-V ACPI IOMMU boot, device DMA tests, and config-matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_rimt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_viot.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_viot.h

## Purpose
`acpi_viot.h` declares ACPI VIOT initialization and virtio-IOMMU configuration helpers.

## Important APIs, types, and functions
With `CONFIG_ACPI_VIOT`, it exposes `acpi_viot_early_init()`, `acpi_viot_init()`, and `viot_iommu_configure()`. Disabled builds provide no-op init functions and `viot_iommu_configure()` returning `-ENODEV`.

## Control flow
Boot code performs early and normal VIOT parsing. Device setup calls `viot_iommu_configure()` to attach devices to virtio-IOMMU topology described by ACPI.

## State and persistence behavior
Parsed VIOT topology and IOMMU mappings persist in ACPI/IOMMU core state. This header only declares the interface.

## Dependencies and integration points
It depends on `linux/acpi.h` and device declarations. Integration points are ACPI boot, virtio-IOMMU setup, and device DMA configuration.

## Risks and test signals
Risks include early/late init ordering problems, `-ENODEV` paths in generic callers, and incorrect device-to-IOMMU mapping. Test signals include ACPI VIOT boot, virtio-IOMMU DMA tests, and builds without VIOT support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_viot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adb.h -->
# sources/distributed-fs/ceph-client/include/linux/adb.h

## Purpose
`adb.h` declares the kernel Apple Desktop Bus interface for low-level ADB drivers and clients.

## Important APIs, types, and functions
`struct adb_request` carries command data, replies, flags, completion callback, argument, and queue linkage. `struct adb_ids` stores discovered device IDs. `struct adb_driver` defines low-level bus operations: probe, init, request send, autopoll, poll, and reset. Request flags are `ADBREQ_REPLY`, `ADBREQ_SYNC`, and `ADBREQ_NOSEND`. `enum adb_message` describes notifier events, and `adb_client_list` is the blocking notifier head. APIs include request, register/unregister handler, poll, input, reset, handler-change, and info lookup.

## Control flow
Clients build `adb_request` objects and submit them through the active low-level driver. Completion is callback-driven or synchronous based on flags. Bus reset notifications let clients reinitialize after topology changes.

## State and persistence behavior
ADB bus/device/handler state is global to the subsystem. Requests carry mutable completion/reply state until finished.

## Dependencies and integration points
The header includes UAPI ADB definitions and integrates legacy Apple input/power devices, notifier chains, and architecture-specific ADB controllers.

## Risks and test signals
Risks include request lifetime bugs, reply buffer length mistakes, notifier misuse during reset/powerdown, and handler ID conflicts. Test signals include ADB probe/register, sync and async request completion, reset notification ordering, autopoll behavior, and handler-change validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adfs_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/adfs_fs.h

## Purpose
`adfs_fs.h` wraps ADFS UAPI definitions and provides a boot-block checksum helper for Acorn Disc Filing System media.

## Important APIs, types, and functions
The only local helper is `adfs_checkbblk(unsigned char *ptr)`. It computes an 8-bit checksum over the first 511 bytes of a 512-byte boot block and compares it with byte 511. It returns nonzero when the checksum does not match.

## Control flow
The helper walks backward from byte 510 to byte 0, folding carry into the low byte before adding the next byte. The final folded low byte is compared with the stored checksum.

## State and persistence behavior
No state is stored. The helper observes an on-disk 512-byte block; callers must also validate that the disk size is nonzero because all-zero sectors can appear checksum-valid.

## Dependencies and integration points
It depends on `<uapi/linux/adfs_fs.h>` and integrates with ADFS filesystem mount/validation code.

## Risks and test signals
Risks include passing a buffer shorter than 512 bytes, trusting checksum alone, and endian/algorithm regressions. Test signals include known-good and known-bad boot blocks, all-zero-sector handling, and filesystem mount tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adfs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adi-axi-common.h -->
# sources/distributed-fs/ceph-client/include/linux/adi-axi-common.h

## Purpose
`adi-axi-common.h` defines common register offsets and version/FPGA metadata helpers for Analog Devices AXI FPGA IP cores.

## Important APIs, types, and functions
Register offsets include `ADI_AXI_REG_VERSION` and `ADI_AXI_REG_FPGA_INFO`. Version macros pack and unpack semantic major/minor/patch fields. `adi_axi_pcore_ver_gteq()` checks whether a hardware version is at least a required major/minor pair. FPGA info macros decode technology, family, and speed-grade fields. Enums define known FPGA technology, family, and speed-grade values.

## Control flow
Drivers read version/info registers from hardware, decode fields with macros, and gate features using `adi_axi_pcore_ver_gteq()`.

## State and persistence behavior
The header stores no state. It interprets persistent hardware register values.

## Dependencies and integration points
It depends on Linux integer types and is shared by ADI AXI IP drivers that need consistent register decoding.

## Risks and test signals
Risks include version comparison ignoring patch-level requirements, misdecoded bitfields, and assuming unknown enum values cannot occur. Test signals include unit tests for macro packing/unpacking, driver probes across IP versions, and feature-gating tests for boundary versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adi-axi-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adreno-smmu-priv.h -->
# sources/distributed-fs/ceph-client/include/linux/adreno-smmu-priv.h

## Purpose
`adreno-smmu-priv.h` defines the private coordination interface between the Adreno GPU driver and the Adreno-specific ARM SMMU integration.

## Important APIs, types, and functions
`struct adreno_smmu_fault_info` carries fault address, TTBR0, context ID, fault status, syndrome registers, and CBFRSYNRA. `struct adreno_smmu_priv` contains an opaque cookie plus callbacks to get TTBR1 config, set/disable TTBR0 config, fetch fault info, control stall-on-fault, resume translation, and optional PRR bit/address configuration.

## Control flow
When the GPU driver attaches a domain, the SMMU side provides this callback table. GPU context-switch and fault paths call into it to update translation context, inspect faults, stall/resume translation, and configure partially resident region features.

## State and persistence behavior
The cookie points to SMMU-owned state. Callback effects persist in SMMU context-bank registers and GPU translation behavior until changed again.

## Dependencies and integration points
It depends on `io-pgtable` configuration types and physical addresses. Integration is intentionally private to DRM/MSM Adreno GPU and the Adreno SMMU driver.

## Risks and test signals
Risks include callback NULL handling, stale cookie lifetime, register state races during GPU faults/context switches, and PRR optional callbacks being assumed present. Test signals include GPU page fault diagnostics, context-switch stress, stall/resume tests, and attach/detach lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adreno-smmu-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adxl.h -->
# sources/distributed-fs/ceph-client/include/linux/adxl.h

## Purpose
`adxl.h` declares an address translation interface backed by ACPI DSM methods.

## Important APIs, types, and functions
`adxl_get_component_names()` returns a NULL-terminated or implementation-defined list of component names. `adxl_decode(u64 addr, u64 component_values[])` decodes an address into component values.

## Control flow
Callers obtain component labels, allocate/pass a values array, and decode physical addresses through platform ACPI DSM logic implemented elsewhere.

## State and persistence behavior
The header has no state. Decoding reflects firmware/platform topology that is persistent for the boot.

## Dependencies and integration points
It integrates ACPI DSM address decoding with memory/RAS/platform diagnostic code.

## Risks and test signals
Risks include array size mismatches between names and values, firmware DSM failures, and callers assuming names are mutable. Test signals include platform decode tests, invalid address handling, and DSM absence behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adxl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/aer.h -->
# sources/distributed-fs/ceph-client/include/linux/aer.h

## Purpose
`aer.h` declares PCIe Advanced Error Reporting data structures and helper APIs used to log, clear, and recover PCIe AER/DPC errors.

## Important APIs, types, and functions
Severity constants include nonfatal, fatal, correctable, and DPC fatal. TLP log constants size standard header and prefix logs. `struct pcie_tlp_log` stores logged DWORDs, header length, and flit-mode flag. `struct aer_capability_regs` snapshots AER capability registers and source IDs. Enabled APIs include `pci_aer_clear_nonfatal_status()`, `pcie_aer_is_native()`, and `pci_aer_unmask_internal_errors()`, with disabled stubs. Always-declared APIs include `pci_print_aer()`, `cper_severity_to_aer()`, and `aer_recover_queue()`.

## Control flow
PCIe error paths snapshot capability registers, print them, map firmware CPER severity if needed, clear/unmask status, and queue recovery work by domain/bus/devfn/severity.

## State and persistence behavior
Register snapshots are transient; hardware AER status persists until cleared. Recovery queue state is maintained by PCIe AER core.

## Dependencies and integration points
It integrates PCI core, firmware CPER reporting, DPC, AER native-control negotiation, and recovery work queues.

## Risks and test signals
Risks include wrong TLP log length, native-control mismatches with firmware, failing to clear errors, and recovery queued for wrong BDF. Test signals include AER injection, firmware-first CPER paths, DPC events, native/non-native control tests, and disabled `CONFIG_PCIEAER` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/aer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/agp_backend.h -->
# sources/distributed-fs/ceph-client/include/linux/agp_backend.h

## Purpose
`agp_backend.h` declares backend AGPGART structures and APIs for managing AGP bridges, aperture information, and AGP memory bindings.

## Important APIs, types, and functions
Types include `enum chipset_type`, `struct agp_version`, `struct agp_kern_info`, and `struct agp_memory`. Important globals are `agp_bridge`, `agp_bridges`, and `agp_find_bridge`. APIs include memory allocate/free, info copy, bind/unbind, enable, backend acquire, and backend release. Memory type constants distinguish normal and user memory variants.

## Control flow
Drivers acquire a bridge for a PCI device, query bridge/aperture info, allocate AGP memory, bind it at an aperture page offset, then unbind/free and release the bridge. `agp_enable()` programs mode.

## State and persistence behavior
AGP bridge state and bridge lists are global. `struct agp_memory` records pages, scatterlist DMA mappings, binding status, flush status, key, type, and aperture start.

## Dependencies and integration points
The header integrates PCI, VM operations, pages, scatterlists, and AGPGART frontend interfaces.

## Risks and test signals
Risks include aperture offset mistakes, bind/unbind ordering bugs, DMA mapping leaks, stale global bridge pointers, and user memory type confusion. Test signals include AGP bridge probe, allocation/bind/unbind cycles, mmap/aperture tests, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/agp_backend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/agpgart.h -->
# sources/distributed-fs/ceph-client/include/linux/agpgart.h

## Purpose
`agpgart.h` declares AGPGART frontend/user-facing kernel structures layered on top of the AGP backend and UAPI ioctl definitions.

## Important APIs, types, and functions
It defines `struct agp_info`, `agp_setup`, `agp_segment`, `agp_segment_priv`, `agp_region`, `agp_allocate`, `agp_bind`, `agp_unbind`, `agp_client`, `agp_controller`, `agp_file_private`, and `agp_front_data`. Flag bit numbers track file/client/controller validity and permissions.

## Control flow
The frontend tracks file private state, controllers, clients, memory regions, and bind/unbind requests while delegating actual memory/aperture operations to backend functions from `agp_backend.h`.

## State and persistence behavior
`agp_front_data` is the persistent frontend state: mutex, controller lists, file-private list, and backend acquisition flags. Per-process client/controller objects track allocated segments and memory pools.

## Dependencies and integration points
It depends on mutexes, backend AGP declarations, and UAPI AGPGART structures. It integrates char-device/ioctl frontend code with backend bridge management.

## Risks and test signals
Risks include frontend/backend lifetime mismatch, access flag errors, segment bookkeeping leaks, and ioctl ABI structure drift. Test signals include AGPGART ioctl tests, multi-client/controller use, mmap region validation, and backend acquire/release coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/agpgart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ahci-remap.h -->
# sources/distributed-fs/ceph-client/include/linux/ahci-remap.h

## Purpose
`ahci-remap.h` defines register offsets and small helpers for AHCI remapped devices.

## Important APIs, types, and functions
Constants include `AHCI_VSCAP`, `AHCI_REMAP_CAP`, remap device class base `AHCI_REMAP_N_DCC`, remap MMIO offset/size, and `AHCI_MAX_REMAP`. `ahci_remap_dcc(i)` computes a remapped device class-code register offset. `ahci_remap_base(i)` computes the remapped device MMIO base relative to the AHCI BAR.

## Control flow
AHCI or PCI remap code indexes remap slots and uses these helpers to locate class-code and device windows.

## State and persistence behavior
No state is stored. The helpers interpret fixed hardware layout.

## Dependencies and integration points
It depends on size macros and integrates Intel-style AHCI remapping support with storage/PCI probing.

## Risks and test signals
Risks include out-of-range index use, wrong BAR-relative base assumptions, and class-code offset mismatch. Test signals include remap-capable AHCI hardware probe, slot enumeration, and bounds tests for `AHCI_MAX_REMAP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ahci-remap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ahci_platform.h -->
# sources/distributed-fs/ceph-client/include/linux/ahci_platform.h

## Purpose
`ahci_platform.h` declares shared helper APIs for AHCI SATA platform drivers, covering clocks, PHYs, resets, regulators, resources, host initialization, shutdown, and suspend/resume.

## Important APIs, types, and functions
Resource helpers include enable/disable PHYs, clocks, regulators, and all resources, plus reset assert/deassert. Discovery/init helpers include `ahci_platform_find_clk()`, `ahci_platform_get_resources()`, and `ahci_platform_init_host()`. Power/lifecycle helpers include shutdown, host suspend/resume, and device suspend/resume. Flags `AHCI_PLATFORM_GET_RESETS` and `AHCI_PLATFORM_RST_TRIGGER` alter resource acquisition/reset behavior.

## Control flow
Platform probe gets resources, enables power/clock/PHY/reset dependencies in order, initializes the AHCI host, and unwinds on failure. PM paths suspend/resume host and resources.

## State and persistence behavior
Persistent state is in `struct ahci_host_priv` and registered ATA/SCSI host objects. The header only defines function contracts.

## Dependencies and integration points
It integrates libahci, platform devices, clocks, PHYs, regulators, resets, ATA port info, and SCSI host templates.

## Risks and test signals
Risks include resource enable/disable ordering bugs, reset polarity mistakes, missing clock names, and PM imbalance. Test signals include platform AHCI probe failure unwinds, suspend/resume, shutdown, regulator/PHY fault injection, and DT/ACPI platform resource variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ahci_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/aio.h -->
# sources/distributed-fs/ceph-client/include/linux/aio.h

## Purpose
`aio.h` declares kernel asynchronous I/O hooks needed by process teardown and kiocb cancellation.

## Important APIs, types, and functions
It forward-declares `struct kioctx`, `struct kiocb`, and `struct mm_struct`, defines `kiocb_cancel_fn`, and declares `exit_aio()` and `kiocb_set_cancel_fn()` when `CONFIG_AIO` is enabled. Disabled stubs are no-ops.

## Control flow
`exit_aio()` is called during mm/process teardown to release AIO contexts. `kiocb_set_cancel_fn()` lets a request install cancellation behavior.

## State and persistence behavior
AIO context and request state live in implementation structures. Cancellation function pointers persist on requests until completion/cancel.

## Dependencies and integration points
It includes AIO UAPI definitions and integrates fs/aio code, kiocb users, and mm lifetime.

## Risks and test signals
Risks include no-op stubs hiding missing cleanup in non-AIO builds, cancellation races, and teardown ordering with outstanding I/O. Test signals include AIO syscall tests, process exit with pending I/O, request cancellation, and config-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/aio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/alarmtimer.h -->
# sources/distributed-fs/ceph-client/include/linux/alarmtimer.h

## Purpose
`alarmtimer.h` declares the kernel alarm timer abstraction for realtime and boottime alarms built on hrtimers and timerqueue nodes.

## Important APIs, types, and functions
`enum alarmtimer_type` identifies realtime, boottime, and tracing/freezer variants. `struct alarm` stores the timerqueue node, backing hrtimer, callback, type, state flags, and private data. APIs include init, start, relative start, restart, try-cancel, cancel, forward, forward-now, and remaining-time query. `alarmtimer_get_rtcdev()` returns the RTC device when RTC class support exists.

## Control flow
Callers initialize an alarm with type and callback, start it at an absolute or relative expiry, optionally forward periodic expiries, and cancel when no longer needed. Callback execution is driven by the hrtimer/alarmtimer core.

## State and persistence behavior
Each `struct alarm` carries enqueue state and expiry node state. The RTC device association is global subsystem state used for wake-capable alarms.

## Dependencies and integration points
It depends on timekeeping, hrtimer, timerqueue, and optionally RTC class. It integrates POSIX alarm timers, suspend/freezer behavior, and wakeup-capable timers.

## Risks and test signals
Risks include cancel/restart races, wrong clock type, failing to handle inactive state, and RTC absence. Test signals include alarmtimer selftests, suspend wake alarms, periodic forward behavior, cancel return values, and RTC-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/alarmtimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/alcor_pci.h -->
# sources/distributed-fs/ceph-client/include/linux/alcor_pci.h

## Purpose
`alcor_pci.h` defines register maps, constants, private state, and MMIO accessor prototypes for Alcor Micro AU6601/AU662x PCI card reader drivers.

## Important APIs, types, and functions
The header enumerates device IDs, driver names, clock/dma limits, SD/MS register offsets, command/data control bits, interrupt status/mask bits, bus width and power controls, PCIe capability offsets, and card-type identifiers. `struct alcor_dev_cfg` stores DMA configuration. `struct alcor_pci_priv` stores PCI devices, device pointer, MMIO base, IRQ, IDR ID, and config. Accessors include 8/16/32-bit writes, big-endian 32-bit write/read, and 8/32-bit reads.

## Control flow
Card reader drivers use register constants to program command/data transfers, DMA, clocks, resets, interrupts, card detection, and Memory Stick mode. Accessor functions centralize MMIO width/endian handling.

## State and persistence behavior
`alcor_pci_priv` is persistent per PCI function. Hardware register state persists in the controller until reset or reprogramming.

## Dependencies and integration points
It integrates PCI probing, MMIO, IRQ handling, MMC/MemoryStick card drivers, and DMA constraints.

## Risks and test signals
Risks include undocumented register assumptions, AU6601/AU6621 DMA differences, endian accessor misuse, interrupt mask errors, and card-detect races. Test signals include SD/MS card probe, DMA/PIO transfers, interrupt error paths, reset/power sequencing, and device-ID variant tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/alcor_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/align.h -->
# sources/distributed-fs/ceph-client/include/linux/align.h

## Purpose
`align.h` is a Linux include wrapper around generic vDSO alignment helpers.

## Important APIs, types, and functions
It includes `<vdso/align.h>` and defines no local macros or functions. Consumers receive the alignment macros/types exported by the vDSO header.

## Control flow
There is no runtime control flow.

## State and persistence behavior
No state is created. The file affects compile-time macro availability only.

## Dependencies and integration points
It provides a stable Linux include path for code that needs alignment helpers shared with vDSO code.

## Risks and test signals
Risks are limited to include-path breakage and wrapper/header guard mismatch. Test signals are header self-containment builds and users of `ALIGN`-style helpers through this include.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/align.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/alloc_tag.h -->
# sources/distributed-fs/ceph-client/include/linux/alloc_tag.h

## Purpose
`alloc_tag.h` defines allocation callsite tagging for memory allocation profiling. It creates codetag-backed records in a special ELF section and updates per-CPU byte/call counters around allocations.

## Important APIs, types, and functions
Types include `struct alloc_tag_counters`, `struct alloc_tag`, `alloc_tag_kernel_section`, `alloc_tag_module_section`, and `struct codetag_bytes`. With profiling enabled, `DEFINE_ALLOC_TAG()` emits a static tag in `alloc_tags`; `mem_alloc_profiling_enabled()` checks the static key; `alloc_tag_read()` sums per-CPU counters; `alloc_tag_ref_set()`, `alloc_tag_add()`, and `alloc_tag_sub()` maintain references and counts; inaccurate flags can be set/tested; `alloc_hooks()` and `alloc_hooks_tag()` wrap allocation expressions. Debug builds add codetag-empty checks and early PFN tagging.

## Control flow
Allocation wrappers define or use a tag, save it into current allocation context, execute the allocation expression, restore the old tag, and record bytes/calls on success. Free paths subtract bytes/calls through the stored codetag reference and clear it.

## State and persistence behavior
Each callsite tag persists in an ELF section. Counters are per-CPU and accumulate runtime allocation statistics. Object references remember which tag owns their allocation accounting until freed.

## Dependencies and integration points
The header depends on codetag infrastructure, per-CPU variables, current task allocation tag, static keys, preemption/IRQ assumptions, and module section handling. It integrates slab/page allocation profiling and top-user reporting.

## Risks and test signals
Risks include counter imbalance on split/free paths, missing ref clearing, weak per-CPU module behavior, preemption-sensitive counter updates, and disabled stubs changing coverage. Test signals include allocation profiling selftests, debug warnings for stale tags, module load/unload sections, top-user reports, and builds with profiling on/off/debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/alloc_tag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/altera_jtaguart.h -->
# sources/distributed-fs/ceph-client/include/linux/altera_jtaguart.h

## Purpose
`altera_jtaguart.h` declares platform data for the Altera JTAG UART driver.

## Important APIs, types, and functions
It defines legacy character major/minor numbers and `struct altera_jtaguart_platform_uart`, which carries the physical base address and IRQ number.

## Control flow
Platform setup code supplies the struct to the driver, which maps registers and registers the UART using the provided interrupt.

## State and persistence behavior
No runtime state is stored in the header. The platform data is static boot/probe configuration.

## Dependencies and integration points
It integrates board/platform description with the Altera JTAG UART serial driver.

## Risks and test signals
Risks include wrong physical base, wrong IRQ, and stale major/minor assumptions. Test signals include driver probe, console/tty I/O, interrupt receive tests, and platform-data validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/altera_jtaguart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/altera_uart.h -->
# sources/distributed-fs/ceph-client/include/linux/altera_uart.h

## Purpose
`altera_uart.h` declares platform data for Altera UART devices.

## Important APIs, types, and functions
`struct altera_uart_platform_uart` carries the physical MMIO base, IRQ, UART clock rate, and bus address shift/stride.

## Control flow
Platform setup passes the struct to the serial driver, which maps the UART, configures baud from `uartclk`, applies register stride from `bus_shift`, and uses the IRQ for interrupt-driven I/O.

## State and persistence behavior
The header stores no state. The platform data persists as device configuration during driver lifetime.

## Dependencies and integration points
It integrates board/platform descriptions with the Altera UART serial driver.

## Risks and test signals
Risks include incorrect clock causing baud errors, wrong bus shift corrupting register access, and IRQ/base mismatches. Test signals include probe, baud-rate validation, interrupt-driven RX/TX, and polling/console use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/altera_uart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/bus.h -->
# sources/distributed-fs/ceph-client/include/linux/amba/bus.h

## Purpose
`amba/bus.h` defines the Linux AMBA/PrimeCell bus abstraction, device and driver structures, registration helpers, and convenience macros for APB/AHB AMBA devices.

## Important APIs, types, and functions
Constants include `AMBA_NR_IRQS`, `AMBA_CID`, and `CORESIGHT_CID`. `struct amba_cs_uci_id` represents CoreSight unique component identifiers. `struct amba_device` embeds `struct device`, resource, pclk, DMA parameters, periphid/cid, IRQs, UCI, and driver override. `struct amba_driver` wraps `device_driver`, probe/remove/shutdown callbacks, ID table, and managed-DMA flag. APIs include driver register/unregister, `dev_is_amba()`, device alloc/put/add/register/unregister, region request/release, and module/builtin driver macros. Field macros extract config, revision, manufacturer, and part IDs.

## Control flow
AMBA devices are allocated/registered with resources and IDs. The bus matches drivers by AMBA ID/UCI data, calls probe/remove/shutdown, and manages regions/clocks/devices through standard driver core paths.

## State and persistence behavior
Each `amba_device` is persistent device-core state. Driver override strings are core-owned when set through proper APIs. Registered drivers persist on `amba_bustype`.

## Dependencies and integration points
It depends on clocks, device core, resources, regulators, module infrastructure, mod_devicetable, and DMA/IOMMU handling. It integrates ARM PrimeCell, CoreSight, APB/AHB static device declarations, and driver modules.

## Risks and test signals
Risks include invalid CID/periphid matching, direct writes to `driver_override`, DMA mask mistakes for APB/AHB, and config-disabled stubs returning `-EINVAL`. Test signals include AMBA driver probe/remove, CoreSight UCI matching, static APB/AHB device registration, region conflicts, and builds without `CONFIG_ARM_AMBA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/kmi.h -->
# sources/distributed-fs/ceph-client/include/linux/amba/kmi.h

## Purpose
`amba/kmi.h` defines register offsets and bit meanings for the ARM PrimeCell PL050 keyboard/mouse interface.

## Important APIs, types, and functions
Macros define control, status, data, clock divisor, interrupt register offsets, individual control/status/interrupt bits, and `KMI_SIZE`. Register macros are relative to `KMI_BASE`, expected to be defined by the including driver/platform code.

## Control flow
Drivers program control bits to enable KMI and interrupts, read status to determine TX/RX/busy/parity/line levels, access `KMIDATA`, set clock divisor, and service interrupt bits.

## State and persistence behavior
No kernel state is stored. Hardware registers hold device state.

## Dependencies and integration points
It integrates AMBA PL050 input drivers with low-level register programming.

## Risks and test signals
Risks include missing or wrong `KMI_BASE`, bit misprogramming that forces clock/data lines, and interrupt enable/status confusion. Test signals include PL050 keyboard/mouse probe, RX/TX interrupt handling, clock divisor validation, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/kmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/mmci.h -->
# sources/distributed-fs/ceph-client/include/linux/amba/mmci.h

## Purpose
`amba/mmci.h` declares platform data for the ARM PrimeCell MMCI/PL180 MMC controller.

## Important APIs, types, and functions
`struct mmci_platform_data` contains `ocr_mask`, describing supported voltages, and an optional `status(struct device *)` callback to report card presence when no GPIO line is supplied.

## Control flow
The MMCI driver reads platform data during probe, uses voltage masks unless a regulator supersedes them, and calls `status()` to determine card-detect state when needed.

## State and persistence behavior
The header stores no state. Platform data is persistent device configuration.

## Dependencies and integration points
It depends on MMC host voltage definitions and integrates board/platform data with the AMBA MMCI driver.

## Risks and test signals
Risks include wrong voltage mask, card-detect callback sleeping or returning inverted values, and regulator/platform-data conflicts. Test signals include MMCI probe, card insertion/removal, voltage negotiation, and no-GPIO card-detect paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/mmci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/pl022.h -->
# sources/distributed-fs/ceph-client/include/linux/amba/pl022.h

## Purpose
`amba/pl022.h` declares platform and per-chip configuration for the ARM PrimeCell PL022/PL023 SSP SPI controller.

## Important APIs, types, and functions
Enums describe loopback, interface protocol, master/slave hierarchy, RX/TX endian, data size, transfer mode, FIFO trigger levels, SPI clock phase/polarity, Microwire control length/wait state/duplex, feedback clock delay, and chip select commands. `struct ssp_clock_params` stores CPSDVSR/SCR clock fields. `struct pl022_ssp_controller` carries bus ID, DMA enable/filter/params, autosuspend delay, and realtime pump flag. `struct pl022_config_chip` stores per-device SPI/Microwire communication settings.

## Control flow
Controller probe consumes platform controller data. SPI devices pass `pl022_config_chip` as controller data, which the driver uses when setting up transfers, FIFO thresholds, clock parameters, protocol mode, and DMA/polling/interrupt operation.

## State and persistence behavior
Configuration persists as platform data and per-SPI-device controller data. Runtime register state is maintained by the PL022 driver.

## Dependencies and integration points
The header integrates AMBA, SPI core board info, DMA engine filters, runtime PM, and ST/ARM SSP variants.

## Risks and test signals
Risks include invalid data sizes, unsupported endian/duplex settings on non-ST variants, DMA filter mismatches, and bad clock divisors. Test signals include SPI loopback, DMA and interrupt transfers, Microwire devices, runtime PM autosuspend, and per-device mode switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/pl022.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/pl080.h -->
# sources/distributed-fs/ceph-client/include/linux/amba/pl080.h

## Purpose
`amba/pl080.h` defines register offsets, bitfields, transfer constants, and linked-list item layouts for ARM PrimeCell PL080 DMA controllers and related Samsung/Faraday variants.

## Important APIs, types, and functions
Macros cover global interrupt/status/clear/config/sync registers; per-channel register offsets; LLI address bits; control fields for protection, increment, bus select, widths, burst sizes, and transfer size; channel config fields for halt/active/lock/interrupt masks/flow/source/destination; flow-control values; FTDMAC020-specific CSR/CFG/LLI fields; and width/burst constants. `struct pl080_lli` and `struct pl080s_lli` describe DMA linked-list descriptors.

## Control flow
DMA drivers compose control/config words, program source/destination/LLI registers, enable channels, and service terminal-count/error interrupts. Variant-specific macros account for register layout and transfer-size differences.

## State and persistence behavior
No software state is stored. Hardware channel registers and in-memory LLI chains hold active DMA state until completion or abort.

## Dependencies and integration points
It integrates AMBA PL080 DMA engine drivers, Samsung PL080S variants, and Faraday FTDMAC020 derivatives with Linux DMAengine.

## Risks and test signals
Risks include wrong variant register layout, transfer-size mask overflow, LLI field mismatch, interrupt mask errors, and source/destination increment mistakes. Test signals include mem2mem and peripheral DMA transfers, scatter/gather LLI chains, error interrupt handling, abort/halt paths, and variant-specific hardware tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/pl080.h -->
