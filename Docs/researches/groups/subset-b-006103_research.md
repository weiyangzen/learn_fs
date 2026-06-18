# Research: subset-b-006103

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/nlattr.c -->
# sources/distributed-fs/ceph-client/lib/nlattr.c

## Purpose
Implements the kernel netlink attribute helper library: validation, parsing, lookup, string/memory copy helpers, and, when `CONFIG_NET` is enabled, skb attribute reservation and emission. It is the common safety layer between netlink family command handlers and untrusted attribute streams.

## APIs, Control Flow, and State
Important exports are `__nla_validate()`, `__nla_parse()`, `nla_policy_len()`, `nla_find()`, `nla_strscpy()`, `nla_strdup()`, `nla_memcpy()`, `nla_memcmp()`, `nla_strcmp()`, `nla_reserve*()`, `nla_put*()`, and `nla_append()`. The core flow is `__nla_validate_parse()`: zero the optional type table, iterate attributes, reject unknown types when strict flags require it, sanitize the type through `array_index_nospec()`, run `validate_nla()`, then store the attribute pointer by type. `validate_nla()` enforces fixed sizes, minimum sizes, nested flags, string termination/length, binary size, ranges, masks, bitfield32 selectors, reject policies, and custom callbacks. Nested policies recurse through `NLA_NESTED` and `NLA_NESTED_ARRAY`, capped by `MAX_POLICY_RECURSION_DEPTH`.

## Dependencies and Integration
Depends on `net/netlink.h`, `skbuff`, `jiffies`/ratelimited warnings, nospec helpers, and extack reporting macros. It is integrated by generic netlink families, rtnetlink, and other netlink command parsers. The `CONFIG_NET` block appends `struct nlattr` payloads to `sk_buff` tailroom, including 64-bit alignment padding.

## Risks and Test Signals
Risks include accepting malformed lengths in non-strict compatibility mode, policy recursion abuse, incorrect nested policy lengths, off-by-one string termination decisions, and skb tailroom miscalculation by callers using unchecked `__nla_*` helpers. Test signals include netlink selftests with strict/non-strict validation, nested-array fuzzing, extack message assertions, attribute range/mask tests, and skb alignment tests for 64-bit attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/nlattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/nmi_backtrace.c -->
# sources/distributed-fs/ceph-client/lib/nmi_backtrace.c

## Purpose
Provides generic NMI-triggered CPU backtrace support for architectures that define `arch_trigger_cpumask_backtrace`. It coordinates cross-CPU stack dumps for lockup diagnostics.

## APIs, Control Flow, and State
The main APIs are `nmi_trigger_cpumask_backtrace()` and `nmi_cpu_backtrace()`. Global state consists of `backtrace_mask`, `backtrace_flag`, and module parameter `backtrace_idle`. The trigger path serializes concurrent dumps with `test_and_set_bit()`, copies the requested CPU mask, optionally excludes one CPU, handles the current CPU locally with `nmi_cpu_backtrace(NULL)`, invokes the architecture-provided NMI raiser for remaining CPUs, waits up to 10 seconds while touching the softlockup watchdog, performs stall checks, flushes printk buffers, and clears the flag. The CPU callback prints registers or a stack, skips idle CPUs unless configured, clears its bit in the shared mask, and is marked `NOKPROBE_SYMBOL`.

## Dependencies and Integration
Depends on cpumasks, NMI architecture hooks, printk CPU synchronization, scheduler debug helpers, stall snapshots/checks, and softlockup watchdog touch points. It integrates with SysRq/debug paths and lockup detectors that request all-CPU backtraces.

## Risks and Test Signals
Risks include stalled CPUs leaving mask bits set, noisy or skipped idle backtraces, architecture raisers failing to call back, and printk recursion during NMI context. Test signals include forced all-CPU backtraces, exclude-CPU behavior, idle CPU skip toggling via `backtrace_idle`, concurrent trigger suppression, and architecture NMI watchdog tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/nmi_backtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/notifier-error-inject.c -->
# sources/distributed-fs/ceph-client/lib/notifier-error-inject.c

## Purpose
Implements shared debugfs-backed error injection for kernel notifier chains. It lets specialized modules expose notifier action names and configurable negative errno values.

## APIs, Control Flow, and State
Exports `notifier_err_inject_dir` and `notifier_err_inject_init()`. The initializer wires `err_inject->nb.notifier_call`, sets notifier priority, creates a debugfs directory with an `actions` subdirectory, and creates an `error` file per action. Writes are clamped to `[-MAX_ERRNO, 0]`. The notifier callback scans the null-terminated action array, matches `val`, logs non-zero injection, and returns `notifier_from_errno(err)`. Module init creates the top-level `notifier-error-inject` directory; exit removes it recursively. State is the action array's mutable `error` fields and debugfs dentries.

## Dependencies and Integration
Depends on debugfs, notifier blocks, module lifetime, and the local header. It is reused by PM and OF reconfiguration error-injection modules and can support other notifier chains with action tables.

## Risks and Test Signals
Risks include missing debugfs cleanup on registration failure in users, no locking around action `error` fields, action values not listed in the table returning success, and injection only being available when debugfs is mounted and enabled. Test signals include debugfs read/write of each action, clamping behavior, notifier return conversion, and unregister cleanup under module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/notifier-error-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/notifier-error-inject.h -->
# sources/distributed-fs/ceph-client/lib/notifier-error-inject.h

## Purpose
Declares the small internal interface used by notifier error-injection modules.

## APIs, Control Flow, and State
Defines `struct notifier_err_inject_action` with notifier value, configured errno, and action name; `NOTIFIER_ERR_INJECT_ACTION(action)` for name/value initializer pairs; and `struct notifier_err_inject`, which embeds a `notifier_block` followed by a flexible action table terminated by a zero sentinel. It declares the top-level debugfs dentry and `notifier_err_inject_init()`. There is no executable control flow in the header; state is supplied by including modules through static action arrays.

## Dependencies and Integration
Depends on `linux/atomic.h`, `linux/debugfs.h`, and `linux/notifier.h`. Integrated by `notifier-error-inject.c`, PM notifier injection, OF reconfig notifier injection, and any future notifier-specific injection module.

## Risks and Test Signals
Risks include forgetting the sentinel, using a notifier value that does not match the target chain, and exposing mutable debugfs errno fields without caller-side synchronization. Test signals are compile coverage for action table initializers and module tests that verify each named action directory maps to the intended notifier event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/notifier-error-inject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/objagg.c -->
# sources/distributed-fs/ceph-client/lib/objagg.c

## Purpose
Implements the object aggregation manager. It lets callers represent many user objects as roots plus one-level delta children, reducing hardware/resource programming when objects can be expressed relative to other objects.

## APIs, Control Flow, and State
Exports object accessors, `objagg_obj_get()`, `objagg_obj_put()`, `objagg_create()`, `objagg_destroy()`, stats helpers, and hint helpers. `struct objagg` owns callback ops, a private pointer, an rhashtable keyed by raw object bytes, object list, root IDA, and optional hints. `struct objagg_obj` stores raw object bytes, parent/root status, root or delta private data, root ID, refcount, and stats. Get first reuses an exact object, otherwise tries hint-based placement, then scans existing roots via `delta_create()`, otherwise creates a new root with `root_create()`. Put decrements user stats, drops refs, destroys deltas through `delta_destroy()` or roots through `root_destroy()`, removes from rhashtable/list, and frees memory. Hints are built by a simple greedy graph over possible `delta_check()` edges and later reused to keep root IDs stable.

## Dependencies and Integration
Depends on rhashtable, IDA, list, sort, module infrastructure, `linux/objagg.h`, and tracepoints. Callers provide all locking and all domain-specific object comparison, root allocation, delta allocation, and cleanup callbacks.

## Risks and Test Signals
Risks include caller locking mistakes, callback failures leaving partial objects, unsupported nested aggregation assumptions, O(n^2) hint graph cost, root ID allocation failures, and stale hints not matching future object sets. Test signals include `test_objagg`, callback fault injection, stats ordering checks, hint reuse/root-id stability tests, and tracepoint observation of root/delta lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/objagg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/objpool.c -->
# sources/distributed-fs/ceph-client/lib/objpool.c

## Purpose
Provides initialization and teardown for the lockless object pool abstraction, allocating per-CPU ring slots with prebuilt objects for fast MPMC/FIFO pool operations defined by the public objpool API.

## APIs, Control Flow, and State
Exports `objpool_init()`, `objpool_free()`, `objpool_drop()`, and `objpool_fini()`. Init validates object count and size, aligns object size, rounds capacity to a power of two, allocates a CPU-slot pointer array, and distributes objects across possible CPUs. Each `objpool_slot` stores ring entries plus contiguous object storage; optional `objinit()` initializes each object. Allocation prefers `__vmalloc_node()` when not constrained to atomic GFP, falls back to `kmalloc_node()`, and keeps data node-local. Pool state includes capacity, object size, possible CPU count, refcount, context, release callback, and slot pointers. Finish drains remaining objects with `objpool_pop()`, decrements the pool ref, and frees slots when the last object is dropped.

## Dependencies and Integration
Depends on `linux/objpool.h`, vmalloc/slab allocation, atomics/refcounting, CPU masks, and log2 helpers. It integrates with tracing and other subsystems that need preallocated reusable objects under low-latency constraints.

## Risks and Test Signals
Risks include partial allocation failure cleanup, callback failure after some objects were initialized, capacity overflow, misuse after `objpool_fini()`, and delayed pool freeing until all checked-out objects call `objpool_drop()`. Test signals include init/fini under GFP variants, CPU distribution checks, object init failure injection, pop/push/drop lifecycle tests, and KASAN/KMSAN coverage for slot/object layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/objpool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/of-reconfig-notifier-error-inject.c -->
# sources/distributed-fs/ceph-client/lib/of-reconfig-notifier-error-inject.c

## Purpose
Adds error injection for Open Firmware/device-tree reconfiguration notifier events.

## APIs, Control Flow, and State
Defines a module parameter `priority`, a static `notifier_err_inject` action table for attach node, detach node, add property, remove property, and update property events, and module init/exit routines. Init creates `debugfs/notifier-error-inject/OF-reconfig/actions/.../error`, registers the notifier with `of_reconfig_notifier_register()`, and removes debugfs state on registration failure. Exit unregisters and removes the directory. Runtime state is the debugfs-controlled errno per action and the registered notifier block.

## Dependencies and Integration
Depends on OF reconfig notifier APIs, module parameters, debugfs, and the common notifier error-injection helper. It integrates with dynamic device-tree update paths used by overlays and OF property mutation.

## Risks and Test Signals
Risks include injecting errors into paths that rarely expect notifier failure, incorrect priority changing ordering-sensitive behavior, and stale debugfs entries if registration/unregistration is mishandled. Test signals include OF overlay/reconfig tests with each action errno set, registration failure cleanup checks, and module unload while debugfs files were open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/of-reconfig-notifier-error-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/oid_registry.c -->
# sources/distributed-fs/ceph-client/lib/oid_registry.c

## Purpose
Implements lookup, ASN.1 wrapper parsing, and string formatting for registered object identifiers used by kernel crypto, key, certificate, and ASN.1 consumers.

## APIs, Control Flow, and State
Exports `look_up_OID()`, `parse_OID()`, and `sprint_oid()`. `look_up_OID()` hashes DER OID octets, then binary-searches generated tables from `oid_registry_data.c`, ordered by hash, length, and reverse byte value. `parse_OID()` validates a minimal ASN.1 `ASN1_OID | length | oid` envelope and returns the registered enum or `OID__NR` for unknown OIDs. `sprint_oid()` decodes the first combined arc and subsequent base-128 continuation arcs into dotted decimal text, returning `-EBADMSG` for malformed encodings and `-ENOBUFS` for short buffers. Persistent state is generated static registry data.

## Dependencies and Integration
Depends on ASN.1 constants, generated OID tables, kernel formatting, and exported GPL symbols. Integration points include X.509/PKCS parsers, public key algorithms, and other DER-decoding code.

## Risks and Test Signals
Risks include generated table order/hash mismatches, malformed continuation bytes, buffer truncation, unknown OIDs being represented only as `OID__NR`, and invalid first-arc semantics not deeply validated. Test signals include generated registry self-checks, DER certificate parsing tests, malformed OID fuzzing, dotted string buffer-boundary tests, and lookup tests for every generated OID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/oid_registry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/once.c -->
# sources/distributed-fs/ceph-client/lib/once.c

## Purpose
Backs the `DO_ONCE()` and `DO_ONCE_SLEEPABLE()` helper macros by serializing one-time execution and disabling static branches after the first successful run.

## APIs, Control Flow, and State
Exports `__do_once_start()`, `__do_once_done()`, `__do_once_sleepable_start()`, and `__do_once_sleepable_done()`. Non-sleepable once uses `once_lock` with IRQ save/restore. Start locks and returns false when `*done` is already set, with sparse lock-count annotations. Done marks `*done`, unlocks, allocates deferred work, takes a module reference, and schedules work that disables the static key and releases the module. Sleepable once uses `once_mutex`; its done path disables the static branch directly after unlocking. State is the caller-provided `done` boolean plus static key state.

## Dependencies and Integration
Depends on spinlocks, mutexes, workqueues, static keys, module references, and slab allocation. It integrates with macros in `linux/once.h` used for one-time warnings, setup, and static-branch guarded code paths.

## Risks and Test Signals
Risks include deferred allocation failure leaving the static branch enabled, module lifetime misuse if the wrong module pointer is passed, and deadlocks if callers sleep in the non-sleepable variant. Test signals include repeated macro invocation tests, module unload while deferred work is pending, sleepable/non-sleepable lockdep coverage, and static key state checks after first execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/once.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/packing.c -->
# sources/distributed-fs/ceph-client/lib/packing.c

## Purpose
Implements generic bitfield packing and unpacking between CPU-readable `u64` or C structures and packed byte buffers with hardware-specific layout quirks.

## APIs, Control Flow, and State
Exports `pack()`, `unpack()`, deprecated `packing()`, and field-array helpers for `packed_field_u8`/`u16`. `calculate_box_addr()` maps a logical byte of a big-number view to a physical buffer byte while honoring `QUIRK_LSW32_IS_FIRST` and `QUIRK_LITTLE_ENDIAN`; `QUIRK_MSB_ON_THE_RIGHT` reverses bits within bytes. `__pack()` and `__unpack()` iterate logical bytes from high to low significance, compute per-byte masks, project bits between packed buffer and unpacked value, and update only the target field. Public entry points validate bit order and width limits before modifying output. Field helpers read/write structure members by offset and size and call the raw pack/unpack routines for each declared field.

## Dependencies and Integration
Depends on `linux/packing.h`, bitops, `GENMASK`, `bitrev8`, and kernel module exports. It integrates with drivers for devices whose register or descriptor bitfields do not match CPU endian/layout conventions.

## Risks and Test Signals
Risks include overlapping field definitions, unsupported member sizes falling into the 64-bit default path, value truncation after warning, invalid width arguments, and layout quirk combinations being misunderstood by callers. Test signals are the KUnit packing suite, driver descriptor round trips, fuzzing of start/end bit ranges, and field-array pack/unpack equivalence tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/packing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/packing_test.c -->
# sources/distributed-fs/ceph-client/lib/packing_test.c

## Purpose
Provides KUnit coverage for the generic packing library.

## APIs, Control Flow, and State
Defines parameterized `struct packing_test_case` data and KUnit cases for `pack()`, `unpack()`, `pack_fields()`, and `unpack_fields()`. The cases exercise 64-bit values in 16- to 24-byte buffers, aligned and odd bit offsets, all combinations of `QUIRK_LSW32_IS_FIRST`, `QUIRK_LITTLE_ENDIAN`, and `QUIRK_MSB_ON_THE_RIGHT`, and all-ones values. Field tests use a packed 8-byte buffer and a mixed-size `struct test_data` with `PACKED_FIELD()` definitions. Runtime state is KUnit-allocated buffers and expected constants; there is no persistence beyond test results.

## Dependencies and Integration
Depends on KUnit and `linux/packing.h`. Integrated through `kunit_test_suite(packing_test_suite)` and module metadata, typically selected by kernel test configuration.

## Risks and Test Signals
Risks are mostly test coverage gaps: invalid argument paths, overlapping field definitions, truncation warnings, and unusual structure field sizes are not directly covered. Positive signals include broad layout-quirk matrix coverage, memory equality checks for pack output, exact value checks for unpack output, and field helper validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/packing_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/parman.c -->
# sources/distributed-fs/ceph-client/lib/parman.c

## Purpose
Implements a priority-based array manager that keeps items grouped by priority in a linear backing array while delegating actual movement and resizing to caller callbacks.

## APIs, Control Flow, and State
Exports `parman_create()`, `parman_destroy()`, `parman_prio_init()`, `parman_prio_fini()`, `parman_item_add()`, and `parman_item_remove()`. `struct parman` tracks callbacks, private data, selected algorithm, item count, capacity limit, and an ordered priority list. The implemented `lsort` algorithm enlarges when full, finds the insertion index after the previous used priority group, shifts later priority groups down by moving their first item to the group tail, appends the new item, and increments count. Removal replaces non-tail removed items with their group tail, shifts later groups upward, decrements count, and shrinks when spare capacity reaches `resize_step`. All locking is caller-owned.

## Dependencies and Integration
Depends on list handling, module exports, and `linux/parman.h`. It integrates with subsystems managing priority-ordered hardware tables, where callers implement `resize()` and `move()`.

## Risks and Test Signals
Risks include callback move/resize failures leaving external arrays inconsistent, caller locking mistakes, priority initialization order misuse, shrink failure being ignored in remove, and unsupported algorithms if `ops->algo` indexes beyond the local array. Test signals include add/remove across multiple priorities, resize failure injection, array order validation after shifts, and destroy/fini warnings for non-empty state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/parman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/parser.c -->
# sources/distributed-fs/ceph-client/lib/parser.c

## Purpose
Implements simple token, number, substring, and wildcard parsing helpers historically used by mount option and kernel option parsers.

## APIs, Control Flow, and State
Exports `match_token()`, `match_int()`, `match_uint()`, `match_u64()`, `match_octal()`, `match_hex()`, `match_wildcard()`, `match_strlcpy()`, and `match_strdup()`. `match_token()` scans a null-terminated pattern table and uses `match_one()` to match literal text plus `%s`, `%d`, `%u`, `%o`, `%x`, fixed-length numeric/string modifiers, and escaped `%%`, filling `substring_t` arguments. Number helpers copy bounded substrings into a 24-byte stack buffer and convert with `simple_strtol()` or `kstrto*()`. `match_wildcard()` implements iterative `*` and `?` matching with backtracking to the last star. State is stack-local except for caller-provided substring output.

## Dependencies and Integration
Depends on ctype, kstrtox, slab, string helpers, and `linux/parser.h`. Integration points include filesystems, module parameter style parsers, and legacy option parsers.

## Risks and Test Signals
Risks include simplistic grammar, table termination requirements, overflow/truncation of long numeric substrings, wildcard worst-case backtracking, and callers assuming stronger validation than provided. Test signals include mount option parser tests, numeric boundary tests, wildcard matching matrices, malformed `%` pattern coverage, and `match_strdup()` allocation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/percpu-refcount.c -->
# sources/distributed-fs/ceph-client/lib/percpu-refcount.c

## Purpose
Implements scalable percpu reference counts that run as cheap per-CPU counters while live and switch to an atomic counter for shutdown, kill, and zero detection.

## APIs, Control Flow, and State
Exports init/exit, mode-switch, kill, zero-test, reinit, and resurrect helpers. State lives in `struct percpu_ref`: a flagged percpu pointer, `percpu_ref_data`, atomic global count, release callback, confirm callback, and allow/force flags. Init allocates per-CPU counters, allocates data, chooses live/atomic/dead start state, and seeds the count with `PERCPU_COUNT_BIAS` plus the initial ref. Switching to atomic sets the atomic flag, pins a ref, schedules expedited RCU, sums all per-CPU counters, subtracts the bias, warns on underflow, invokes confirmation, wakes waiters, and optionally frees percpu storage. Switching to percpu adds the bias, zeros counters on all CPUs, and clears the atomic flag with release ordering. Kill marks dead, switches atomic, and drops the initial ref.

## Dependencies and Integration
Depends on per-CPU allocation, RCU, spinlocks, waitqueues, scheduler context, memory-ordering primitives, and `linux/percpu-refcount.h`. It is used by block, memory, filesystem, and other high-frequency lifetime-managed objects.

## Risks and Test Signals
Risks include killing twice, exiting during a pending switch, release callbacks that sleep, missed initial-ref protocol, underflow during mode transition, and reinit without `PERCPU_REF_ALLOW_REINIT`. Test signals include percpu-ref selftests in block/memory users, RCU race tests, kill/reinit cycles, underflow warning coverage, and lockdep checks around switch wait paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/percpu-refcount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/percpu_counter.c -->
# sources/distributed-fs/ceph-client/lib/percpu_counter.c

## Purpose
Implements batched per-CPU counters for scalable approximate counting with precise sum and comparison paths.

## APIs, Control Flow, and State
Exports setters, batched add, sync, precise sum, multi-counter init/destroy, compare, limited add, and the global `percpu_counter_batch`. Each counter has a global `s64 count`, raw spinlock, and per-CPU `s32` deltas. `percpu_counter_add_batch()` keeps small changes on the local CPU and folds into the global count when a batch threshold is exceeded, using local cmpxchg when available or IRQ-disabled fallback otherwise. `__percpu_counter_sum()` locks and includes online plus dying CPUs. Init can allocate multiple adjacent percpu counters and registers debug objects and CPU hotplug list entries. CPU-dead callbacks fold the outgoing CPU's delta into global counts and recompute batch size.

## Dependencies and Integration
Depends on percpu allocation, CPU hotplug, debugobjects, raw spinlocks, and module init. It is used by filesystems, memory, networking, and other subsystems that tolerate bounded counter error but need cheap updates.

## Risks and Test Signals
Risks include approximation errors when callers use rough reads, hotplug races if dying CPU deltas are missed, limited-add overflow assumptions, debug object false positives, and misuse after destroy. Test signals include hotplug folding tests, precise-vs-approx compare tests, limited-add boundary coverage, debugobjects free fixups, and stress tests with interrupt-context updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/percpu_counter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/percpu_test.c -->
# sources/distributed-fs/ceph-client/lib/percpu_test.c

## Purpose
Provides a load-time module test for low-level `this_cpu` and `__this_cpu` arithmetic semantics, especially signed/unsigned subtraction and widening behavior.

## APIs, Control Flow, and State
Defines per-CPU `long_counter` and `ulong_counter`, a `CHECK()` macro comparing native and per-CPU values to expected results, and `percpu_test_init()`. Init disables preemption, performs a sequence of adds, subtracts, decrements, and return-value operations with signed, unsigned, and volatile operands, emits warnings on mismatch, reenables preemption, logs completion, and returns `-EAGAIN` so the module unloads immediately. Exit is empty.

## Dependencies and Integration
Depends on module support, per-CPU accessors, and kernel warning infrastructure. It integrates as a diagnostic module rather than a normal runtime library.

## Risks and Test Signals
Risks are limited to test maintenance: expectations are architecture/compiler-sensitive and the module intentionally fails load with `-EAGAIN`. Test signals are absence of `WARN()` output during load, coverage across compilers/architectures, and correct behavior around unsigned wrap to `ULONG_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/percpu_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/pldmfw/Makefile -->
# sources/distributed-fs/ceph-client/lib/pldmfw/Makefile

## Purpose
Builds the PLDM firmware update helper object when `CONFIG_PLDMFW` is selected.

## APIs, Control Flow, and State
The single build rule is `obj-$(CONFIG_PLDMFW) += pldmfw.o`. There is no runtime code or state; control flow is Kbuild conditional inclusion based on kernel configuration.

## Dependencies and Integration
Depends on the parent Kbuild including this directory and the `CONFIG_PLDMFW` symbol being defined by kernel configuration. It integrates `pldmfw.c` into built-in or module output according to the tristate value.

## Risks and Test Signals
Risks include missing Kconfig selection causing drivers that need PLDM firmware flashing to fail link, or stale object naming if source files change. Test signals are allmodconfig/build coverage, driver configurations selecting `PLDMFW`, and link checks for `pldmfw_flash_image()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/pldmfw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/pldmfw/pldmfw.c -->
# sources/distributed-fs/ceph-client/lib/pldmfw/pldmfw.c

## Purpose
Implements a PLDM firmware package parser and firmware flashing coordinator for drivers that consume DMTF DSP0267-formatted images.

## APIs, Control Flow, and State
Exports `pldmfw_flash_image()` and `pldmfw_op_pci_match_record()`. `struct pldmfw_priv` tracks firmware pointer, parse offset, records, components, header metadata, bitmap sizes, CRC, and the selected record. The flash flow allocates private state, parses the image, finds a matching record via driver ops, optionally sends package data, sends component table entries with start/middle/end flags, flashes matching components, finalizes update, and frees all parsed records/components. Parsing validates header UUID/revision, header size, component bitmap length, record lengths, descriptor TLV lengths for standard descriptors, component offsets/sizes, selected single-component mode, total header size, and CRC32. PCI match extracts vendor/device/subsystem descriptors and compares them against `struct pci_dev`, treating zero descriptor values as wildcards.

## Dependencies and Integration
Depends on firmware loader data, device logging, PCI helpers, UUID, unaligned little-endian access, CRC32, bitmaps, lists, and `linux/pldmfw.h`. Drivers provide callbacks for record matching, package data, component tables, flashing, and finalization.

## Risks and Test Signals
Risks include malformed images exercising variable-length pointer iteration, partial allocations before parse failure, single-component mode skipping allocations without freeing skipped component structs, callback failures mid-update, wildcard PCI matching surprises, and unaligned little-endian field misuse. Test signals include PLDM image fuzzing, CRC mismatch tests, malformed TLV/record/component length tests, PCI descriptor matching matrices, single-component selection tests, and driver callback failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/pldmfw/pldmfw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/pldmfw/pldmfw_private.h -->
# sources/distributed-fs/ceph-client/lib/pldmfw/pldmfw_private.h

## Purpose
Defines the private packed binary-layout structures and iterator macros for PLDM firmware package parsing.

## APIs, Control Flow, and State
Defines the expected package UUID, format revision, timestamp size, packed header, record info, descriptor TLV, record area, component info, component area, and for-each macros for descriptors, records, and components. The structures intentionally model variable-length on-image regions with flexible arrays. Iteration macros advance by descriptor size, record length, or component version length using unaligned little-endian loads. There is no owned runtime state; these definitions are interpreted over immutable firmware bytes by `pldmfw.c`.

## Dependencies and Integration
Depends on UUID and unaligned little-endian access expectations inherited from the implementation file. It is private to the PLDM firmware library so callers use parsed public structures instead of raw packed layouts.

## Risks and Test Signals
Risks include unsafe iteration if callers do not check image bounds before each advancement, direct multi-byte access on unaligned fields, mismatches with future DSP0267 revisions, and flexible-array misuse. Test signals include compile-time packed-layout review, parser boundary tests, cross-architecture unaligned access coverage, and sample PLDM package parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/pldmfw/pldmfw_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/plist.c -->
# sources/distributed-fs/ceph-client/lib/plist.c

## Purpose
Implements non-inline operations for priority-sorted doubly linked lists, where `node_list` preserves all nodes in priority order and `prio_list` links one representative per priority.

## APIs, Control Flow, and State
Exports `plist_add()`, `plist_del()`, and `plist_requeue()` through normal linkage from the list library. Add validates node emptiness, searches from both ends of the priority representatives, inserts into the representative list if this priority is new, then inserts into the full node list before the first lower-priority node. Delete repairs the priority representative list by promoting the next same-priority node when needed, then removes the node from both lists. Requeue moves a node to the end of its same-priority group with optimized lookup. Under `CONFIG_DEBUG_PLIST`, consistency check helpers validate prev/next links and an init-time randomized/worst-case test exercises add/delete/requeue.

## Dependencies and Integration
Depends on `linux/plist.h`, list primitives, BUG/WARN infrastructure, and optional scheduler clock/module init for debug tests. It integrates with scheduler, locking, and wait-priority users that need ordered lists.

## Risks and Test Signals
Risks include corrupting both list dimensions if callers reuse non-empty nodes, priority representative repair bugs, missing caller locking, and debug-only test code not running in production builds. Test signals include `CONFIG_DEBUG_PLIST`, randomized add/delete/requeue validation, lockdep coverage in users, and list corruption warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/plist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/pm-notifier-error-inject.c -->
# sources/distributed-fs/ceph-client/lib/pm-notifier-error-inject.c

## Purpose
Adds debugfs-configurable error injection for power-management notifier events.

## APIs, Control Flow, and State
Defines a `priority` module parameter, an action table for hibernation prepare, suspend prepare, and restore prepare, and module init/exit. Init creates `debugfs/notifier-error-inject/pm/actions/.../error`, registers the notifier with `register_pm_notifier()`, and removes debugfs state on failure. Exit unregisters and removes the directory. Runtime state is the notifier block plus per-action errno fields.

## Dependencies and Integration
Depends on PM notifier APIs, suspend constants, module parameters, debugfs, and the shared notifier error-injection helper. It integrates with suspend/hibernate test workflows.

## Risks and Test Signals
Risks include causing suspend/hibernate abort paths that are rarely exercised, priority-dependent behavior, and debugfs availability. Test signals include suspend and hibernation preparation tests with injected errno values, registration failure cleanup, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/pm-notifier-error-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/radix-tree.c -->
# sources/distributed-fs/ceph-client/lib/radix-tree.c

## Purpose
Implements the legacy radix tree and IDR backing library, now sharing concepts and entries with xarray while preserving exported radix-tree APIs.

## APIs, Control Flow, and State
Exports node preload, insert, lookup, replace, tag, iteration, gang lookup, delete, IDR preload/free-slot/destroy helpers, and initialization. Global state includes `radix_tree_node_cachep` and per-CPU `radix_tree_preloads`. Nodes are allocated from slab or a preloaded per-CPU pool for nonblocking inserts; freeing is RCU-delayed and clears slots/tags before slab return. Insert calls `__radix_tree_create()`, extends tree height as needed, allocates missing nodes, and inserts into an empty slot. Lookup descends through internal entries and retries on `RADIX_TREE_RETRY`. Tags propagate upward to root flags and support tagged iteration. Delete clears tags or marks IDR slots free, replaces slots with NULL, shrinks single-child roots, and frees empty nodes. IDR free-slot discovery uses the `IDR_FREE` tag to find or create free indices up to a max.

## Dependencies and Integration
Depends on bitmap/bitops, RCU, percpu/local locks, slab, CPU hotplug, xarray entry encoding, IDR definitions, and `lib/radix-tree.h`. Integrated by legacy radix-tree users, IDR/IDA allocation paths, and xarray internals that share node cache/freeing helpers.

## Risks and Test Signals
Risks include RCU lifetime misuse by callers, tag propagation bugs, preloading lock misuse, internal/value entry accounting errors, IDR NULL semantics, CPU hotplug preload leaks, and iteration under concurrent mutation. Test signals include radix-tree and IDR selftests, xarray tests, RCU stress, CPU hotplug tests, gang lookup/tag iteration checks, and KASAN/KCSAN coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/radix-tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/radix-tree.h -->
# sources/distributed-fs/ceph-client/lib/radix-tree.h

## Purpose
Declares the radix-tree internals shared with xarray.

## APIs, Control Flow, and State
Forward-declares `struct kmem_cache` and `struct rcu_head`, declares the global `radix_tree_node_cachep`, and declares `radix_tree_node_rcu_free()`. There is no control flow in the header; it exposes node-cache state and RCU freeing for code that must share radix tree node allocation semantics.

## Dependencies and Integration
Used by `radix-tree.c` and xarray-related code needing the same slab cache and RCU cleanup path. It intentionally remains small to avoid exposing full radix tree internals.

## Risks and Test Signals
Risks include accidental ABI expansion of private helpers, mismatch between node cache lifetime and xarray users, and using the RCU free helper with non-radix nodes. Test signals are build coverage for radix tree plus xarray, boot-time `radix_tree_init()`, and memory debug checks around node free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/radix-tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/Kconfig -->
# sources/distributed-fs/ceph-client/lib/raid/Kconfig

## Purpose
Defines configuration symbols for the RAID XOR helper library and its KUnit tests.

## APIs, Control Flow, and State
Declares tristate `XOR_BLOCKS`, bool `XOR_BLOCKS_ARCH`, and tristate `XOR_KUNIT_TEST`. `XOR_BLOCKS_ARCH` depends on `XOR_BLOCKS` and defaults to yes for architectures with optimized XOR implementations. `XOR_KUNIT_TEST` depends on KUnit and XOR blocks and defaults with `KUNIT_ALL_TESTS`. There is no runtime state; Kconfig choices control compilation.

## Dependencies and Integration
Integrated by architecture-specific XOR implementations, RAID/parity code, and KUnit test selection. Architecture feature symbols such as `ALTIVEC`, `RISCV_ISA_V`, `S390`, and x86 variants influence optimized build inclusion.

## Risks and Test Signals
Risks include missing defaults for new optimized architectures, enabling tests without the base library, and drivers assuming XOR support without selecting it. Test signals include allmodconfig/allnoconfig builds, per-architecture config coverage, and `XOR_KUNIT_TEST` execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/Makefile -->
# sources/distributed-fs/ceph-client/lib/raid/Makefile

## Purpose
Routes RAID library builds into the XOR subdirectory.

## APIs, Control Flow, and State
The build rule `obj-y += xor/` always descends into `lib/raid/xor`. There is no runtime logic or persistent state.

## Dependencies and Integration
Depends on Kbuild traversal and the XOR directory's own config-conditional object rules. It integrates the RAID XOR library subtree into the kernel build.

## Risks and Test Signals
Risks are minimal: incorrect directory traversal would omit all XOR objects and tests. Test signals are Kbuild coverage with `CONFIG_XOR_BLOCKS`, `CONFIG_XOR_KUNIT_TEST`, and architecture optimized XOR configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/Makefile -->
# sources/distributed-fs/ceph-client/lib/raid/xor/Makefile

## Purpose
Builds the generic and architecture-optimized XOR block implementations used by RAID/parity code, and descends into XOR tests.

## APIs, Control Flow, and State
Adds the local include path, builds `xor.o` when `CONFIG_XOR_BLOCKS` is enabled, composes it from generic core and register/prefetch implementations, and conditionally appends architecture-specific objects for Alpha, ARM/ARM64 NEON, LoongArch LSX, PowerPC Altivec, RISC-V vector, SPARC, S390, and x86 AVX/SSE/MMX. If `CONFIG_XOR_BLOCKS_ARCH` is enabled, `xor-core.o` receives an architecture include path. ARM/ARM64/PowerPC rules adjust FPU/vector compiler flags. `obj-y += tests/` always descends into tests. There is no runtime state in the Makefile.

## Dependencies and Integration
Depends on Kbuild, architecture feature symbols, compiler support for vector flags, and source files under architecture subdirectories. It integrates optimized XOR routines into the RAID library selection framework.

## Risks and Test Signals
Risks include wrong FPU flags causing build failures or unsafe kernel-mode vector use, duplicate/missing optimized objects for an architecture, and generic fallback performance regressions. Test signals include per-architecture builds, XOR KUnit tests, boot-time XOR speed/selection logs, and RAID parity correctness tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/Makefile -->
