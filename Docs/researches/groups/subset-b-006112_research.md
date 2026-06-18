# subset-b-006112 research

Grouped research report for the subset B work item. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/list-test.c -->
## sources/distributed-fs/ceph-client/lib/tests/list-test.c

### Purpose
This file is a KUnit regression suite for the kernel list primitives in `linux/list.h` and `linux/klist.h`. It validates three related APIs: circular doubly linked `struct list_head`, hashed singly linked `struct hlist_head`/`struct hlist_node`, and reference-counted `struct klist`/`struct klist_node`. The suite is behavioral: it constructs tiny lists on the stack, mutates them with the public macros/functions, and asserts exact pointer topology, entry ordering, emptiness state, and iterator behavior.

### Important APIs, types, and functions
The file defines local payload containers `struct list_test_struct` and `struct hlist_test_struct`, each embedding the list node used by `list_entry()` or `hlist_entry()`. The `list_test_*` cases cover initialization (`LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`), mutation (`list_add`, `list_add_tail`, `list_del`, `list_replace`, `list_swap`, move and splice variants), predicates (`list_is_head`, `list_is_first`, `list_is_last`, `list_empty`, `list_empty_careful`, `list_is_singular`), cuts/rotations, entry helpers, and all forward/reverse/safe iteration forms.

The hlist section mirrors this for `HLIST_HEAD_INIT`, `INIT_HLIST_HEAD`, `INIT_HLIST_NODE`, `hlist_add_head`, `hlist_add_before`, `hlist_add_behind`, `hlist_del`, `hlist_del_init`, fake nodes, singular detection, list moves, entry helpers, and safe iteration. The klist section uses global test state `node_count` and `last_node`, plus callbacks `check_node()` and `check_delete_node()`, to verify klist get/put notifications, insertion ordering, delayed deletion while an iterator holds a reference, immediate deletion when refcount reaches zero, `klist_remove()`, and `klist_node_attached()`.

### Control flow
There is no module init function of its own; `kunit_test_suites(&list_test_module, &hlist_test_module, &klist_test_module)` registers three independent KUnit suites. Each case follows a build-mutate-assert pattern. List and hlist tests allocate only local stack nodes except for initialization tests, which allocate heads with `kzalloc_obj()`/`kmalloc_obj()` and free them before returning. Klist tests initialize a `struct klist`, add stack nodes, iterate with `klist_iter_init()`/`klist_next()`/`klist_iter_exit()`, and assert callback side effects.

### State and persistence
Most state is stack-local and discarded after each KUnit case. The only cross-function mutable state is `node_count` and `last_node`, reset at the start of each klist case that depends on it. There is no durable persistence, no device registration, and no filesystem or network interaction.

### Dependencies and integration points
The suite depends on KUnit, core list macros, hlist macros, klist internals exposed by `linux/klist.h`, slab allocation helpers for init coverage, and module metadata. It integrates with kernel self-test execution through KUnit suite registration and will normally be selected by the relevant Kconfig entry in the surrounding `lib/tests` build system.

### Risks and edge cases
The tests intentionally avoid validating concurrency or memory-ordering promises: comments call this out for `list_del_init_careful()`, `list_empty_careful()`, `hlist_unhashed_lockless()`, and `klist_remove()`. The pointer-topology assertions are precise but minimal; they do not exhaustively corrupt lists or test invalid inputs. Klist tests use stack nodes, so they exercise ordering/refcount callbacks but not lifetime hazards from dynamically allocated owners.

### Test signals
Strong signals are exact pointer equality checks after every operation, safe-iterator deletion checks, initialized-empty checks after `*_init` operations, and klist callback count transitions. The three-suite split is useful diagnostically: failures report as `list-kunit-test`, `hlist`, or `klist`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/list-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/liveupdate.c -->
## sources/distributed-fs/ceph-client/lib/tests/liveupdate.c

### Purpose
This file is an in-kernel test helper for the liveupdate/LUO mechanism. It defines a small set of synthetic file-live-blocks (FLBs), registers them with a caller-provided `struct liveupdate_file_handler`, and verifies preserve/retrieve/finish callback plumbing by passing deterministic per-FLB magic handles through the liveupdate API.

### Important APIs, types, and functions
`TEST_NFLBS` creates three static `struct liveupdate_flb` instances in `test_flbs[]`. Each entry shares `test_flb_ops` and gets a distinct `compatible` string via `LIVEUPDATE_TEST_FLB_COMPATIBLE(i)`. `test_flb_preserve()` computes the FLB index by pointer subtraction against `test_flbs`, logs, and stores `TEST_FLB_MAGIC_BASE + index` in `argp->data`. `test_flb_retrieve()` validates the incoming `data` handle and stores it back as `argp->obj` on success. `test_flb_finish()` validates that `obj` matches the same magic value. `test_flb_unpreserve()` only logs. `liveupdate_test_register()` is the external integration function that initializes incoming data and registers each FLB on a supplied file handler.

### Control flow
`liveupdate_test_register()` first calls `liveupdate_test_init()`. Initialization is protected by a static `DEFINE_MUTEX(init_lock)` and static `initialized` flag using the cleanup-style `guard(mutex)` helper. The first call walks all test FLBs and invokes `liveupdate_flb_get_incoming()`, tolerating `-ENODATA` and `-ENOENT` while logging other errors. Registration then iterates through all FLBs with `liveupdate_register_flb(fh, flb)`, logs failures, and deliberately tries to register `test_flbs[0]` again to ensure duplicate registration returns `-EEXIST`.

### State and persistence
The only persistent runtime state is the static `initialized` latch and the static `test_flbs[]` table. The liveupdate payload is represented by numeric magic values in `argp->data`; no heap objects are allocated by this file. Across a live update, state enters through `liveupdate_flb_get_incoming()` and is validated by callback data matching.

### Dependencies and integration points
The file includes public liveupdate headers and `../../kernel/liveupdate/luo_internal.h`, making it closely coupled to the liveupdate implementation rather than a pure black-box test. It exports `liveupdate_test_register()` for other liveupdate test code or file handlers to call. It depends on module ownership via `.owner = THIS_MODULE` and normal kernel logging.

### Risks and edge cases
Pointer subtraction assumes every callback receives one of the statically declared `test_flbs`; a foreign FLB would produce an invalid index and magic value. The duplicate-registration check condition `if (!err || err != -EEXIST)` logs unless the result is exactly `-EEXIST`, which is intentional but easy to misread. Initialization logs incoming-data errors but does not fail registration, so a broken retrieve path may be visible only through logs.

### Test signals
Useful signals include preserve/retrieve/finish logs per compatible FLB, validation of deterministic magic data, duplicate registration producing `-EEXIST`, and non-fatal logging for unexpected incoming retrieval errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/liveupdate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/longest_symbol_kunit.c -->
## sources/distributed-fs/ceph-client/lib/tests/longest_symbol_kunit.c

### Purpose
This KUnit file verifies that the kernel can define, retain, and resolve a symbol whose stringified name reaches `KSYM_NAME_LEN`. It specifically guards the upper boundary of kallsyms symbol-name handling and checks that a generated long function remains callable directly and through kallsyms lookup.

### Important APIs, types, and functions
Nested token-pasting macros `DI`, `DDI`, `DDDI`, `DDDDI`, and `DDDDDI` construct `LONGEST_SYM_NAME`, intended to stringify to 511 visible symbol characters plus the terminating byte represented by `KSYM_NAME_LEN`. `_Static_assert(sizeof(__stringify(LONGEST_SYM_NAME)) == KSYM_NAME_LEN, ...)` turns a mismatch into a build failure. The generated noinline function returns `RETURN_LONGEST_SYM`. `test_longest_symbol()` calls it directly. `test_longest_symbol_kallsyms()` uses a temporary `struct kprobe` on `kallsyms_lookup_name` to get the lookup function pointer, resolves the long symbol by string, then calls the resolved function.

### Control flow
The suite registers two cases under KUnit suite name `longest-symbol`. The direct case is a simple equality assertion. The kallsyms case registers a kprobe, fails the test if registration is unavailable, logs a warning on success, saves `kp.addr` as a callable `kallsyms_lookup_name`, unregisters the probe, resolves the long symbol name, and verifies the resolved function returns the expected sentinel.

### State and persistence
There is no mutable persistent state except the static function pointer `longest_sym` inside the kallsyms test. The symbol exists as a compiled function in the test module or built-in test object. Kprobe registration is transient and explicitly undone before symbol invocation.

### Dependencies and integration points
The file depends on KUnit, `linux/kprobes.h`, `linux/kallsyms.h`, stringification macros, module support, and a configuration where kprobes can locate `kallsyms_lookup_name`. The file’s own comment documents an expected kunit.py invocation with `CONFIG_KPROBES=y`, `CONFIG_MODULES=y`, and some coverage/mitigation settings disabled.

### Risks and edge cases
If kprobe registration fails, the kallsyms case fails rather than skips, which makes missing configuration appear as a test failure. The code does not check whether `kallsyms_lookup_name()` returned NULL before calling `longest_sym()`, so a failed lookup could crash or fault the test environment. The build-time assertion is sensitive to `KSYM_NAME_LEN` changes and macro expansion length.

### Test signals
The strongest signals are compile-time enforcement of symbol-name length, direct runtime call success, successful kprobe-based retrieval of `kallsyms_lookup_name`, and successful invocation of the long-name symbol through kallsyms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/longest_symbol_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/memcpy_kunit.c -->
## sources/distributed-fs/ceph-client/lib/tests/memcpy_kunit.c

### Purpose
This KUnit suite validates kernel `memcpy()`, `memmove()`, `memset()`, and related structure-field clearing helpers. It covers small fixed buffers, argument side-effect behavior, overlap handling, architecture-sensitive large copies, and slow exhaustive-ish large-buffer movement patterns.

### Important APIs, types, and functions
`struct some_bytes` overlays a 32-byte byte array with named fields, enabling byte-level checks plus `memset_after()` and `memset_startat()` field-based tests. Macros `check()` and `compare()` verify byte contents and report the active `TEST_OP`. `memcpy_test()`, `memmove_test()`, and `memset_test()` exercise direct assignment, full overwrites, middle overwrites, pointer/count/value side effects, and helper semantics. Large static buffers `large_src`, `large_dst`, and `large_zero` support `copy_large_test()` for non-overlapping copies, `memmove_overlap_test()` for overlapping windows, and `inner_loop()` for verifying preserved source fragments and zero regions.

### Control flow
The suite initializes expected control patterns locally, mutates destination buffers, and compares every byte. Large-copy paths call `init_large()`, which fills source data with random bytes, forces non-zero edges, and clears the destination. `copy_large_test()` iterates copy sizes from 1 to 1024 and all destination offsets within the source-sized window, then checks before-copy zeros, copied bytes, after-copy zeros, and clears the touched region. `memmove_overlap_test()` reduces the full overlap search space with `next_step()` while emphasizing boundaries and cacheline-crossing offsets, periodically calling `cond_resched()`.

### State and persistence
Small tests are stack-local. Large tests share static buffers that are explicitly reinitialized before use. There is no persistent kernel object, no device, and no heap allocation. Random source contents are intentionally non-deterministic, but validation checks byte-for-byte consistency rather than fixed values.

### Dependencies and integration points
The suite depends on KUnit, slab/vmalloc headers only indirectly through includes, random bytes, overflow/kernel helpers, and scheduler rescheduling for long loops. KUnit marks large copy and overlap cases with `KUNIT_CASE_SLOW`, allowing runners to include or exclude expensive coverage.

### Risks and edge cases
The slow cases can be expensive: nested loops over 1024 byte lengths and offsets are intentionally broad. Random data makes reproducing a failing byte pattern harder unless the failure is structural. The tests validate memory contents after legal operations; they do not intentionally invoke undefined `memcpy()` overlap. Architecture-specific comments note i386 `rep movsl` behavior for 256/1024 offsets.

### Test signals
Signals include full byte comparison after each operation, explicit detection that macro/function arguments are evaluated once, large-copy guard-region checks, both backward and forward overlapping `memmove()` checks, and slow KUnit case tagging for broad memory primitive coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/memcpy_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/min_heap_kunit.c -->
## sources/distributed-fs/ceph-client/lib/tests/min_heap_kunit.c

### Purpose
This file is a KUnit suite for the generic min/max heap helpers in `linux/min_heap.h`. It verifies that the same heap implementation can act as either a min-heap or max-heap through comparator callbacks, and that heapify, push, pop-push, and delete operations preserve ordering.

### Important APIs, types, and functions
`struct min_heap_test_case` parameterizes whether a case uses min or max semantics. `DEFINE_MIN_HEAP(int, min_heap_test)` declares the typed heap wrapper. `less_than()` and `greater_than()` provide `struct min_heap_callbacks.less` implementations. `pop_verify_heap()` repeatedly reads the root, pops it with `min_heap_pop_inline()`, and asserts monotonic nondecreasing or nonincreasing order. Test cases cover `min_heapify_all_inline()`, `min_heap_push_inline()`, `min_heap_pop_push_inline()`, `min_heap_del_inline()`, and `min_heap_init_inline()`.

### Control flow
KUnit parameter generation runs each test for both `"min"` and `"max"` cases. `test_heapify_all()` heapifies a known array, drains it through `pop_verify_heap()`, then repeats with random values. `test_heap_push()` starts with an empty heap and pushes known then random data. `test_heap_pop_push()` pre-fills the heap with sentinel extremes, replaces roots with known or random values, and drains. `test_heap_del()` heapifies, deletes random indices from half the entries, then drains to confirm remaining order.

### State and persistence
All heap storage is stack-local arrays inside individual test cases. Random values are generated with `get_random_u32()` and are not persisted. There is no global mutable state and no allocation.

### Dependencies and integration points
The suite depends on KUnit, `linux/min_heap.h`, module metadata, and random number generation. It integrates through `kunit_test_suite(min_heap_test_suite)` under suite name `min_heap`.

### Risks and edge cases
Random deletion uses `get_random_u32() % heap.nr`; because `heap.nr` shrinks, this covers arbitrary valid indices but not deterministically. The tests verify pop order but do not assert internal array shape, which is appropriate because heap shape is not a public contract. Comparator callbacks ignore `args`, so callback argument propagation is not tested.

### Test signals
The main signal is complete draining in sorted order after every operation family for both min and max comparators, with coverage of fixed boundary-like values, duplicates, negative ints, high-bit values, and random input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/min_heap_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/module/Makefile -->
## sources/distributed-fs/ceph-client/lib/tests/module/Makefile

### Purpose
This Makefile builds generated kallsyms stress-test modules under `lib/tests/module`. It wires Kconfig options for four generated modules and defines the build rule that turns `gen_test_kallsyms.sh` output into C sources consumed by kbuild.

### Important APIs, types, and functions
The file declares `obj-$(CONFIG_TEST_KALLSYMS_A)` through `obj-$(CONFIG_TEST_KALLSYMS_D)` for `test_kallsyms_a.o`, `test_kallsyms_b.o`, `test_kallsyms_c.o`, and `test_kallsyms_d.o`. It defines `quiet_cmd_gen_test_kallsyms` and `cmd_gen_test_kallsyms`, passing the target path, `CONFIG_TEST_KALLSYMS_NUMSYMS`, and `CONFIG_TEST_KALLSYMS_SCALE_FACTOR` into the generator script. The pattern rule `$(obj)/%.c: $(src)/gen_test_kallsyms.sh FORCE` invokes kbuild’s `if_changed` helper.

### Control flow
During kbuild, enabled module objects require corresponding generated `.c` files. The pattern rule runs the generator whenever the command or script changes, then the generated source is compiled into the selected object. `targets += $(foreach x, a b c d, test_kallsyms_$(x).c)` tells kbuild these generated C files are build targets.

### State and persistence
The Makefile itself has no runtime state. Its build outputs are generated C files in the object tree and compiled module objects. Rebuild state is managed by kbuild command tracking.

### Dependencies and integration points
This file depends on kbuild variables `obj`, `src`, `CONFIG_TEST_KALLSYMS_*`, `FORCE`, and `if_changed`. It integrates directly with `gen_test_kallsyms.sh`; the script interprets target suffixes `a`, `b`, `c`, and `d` to generate different symbol-count patterns.

### Risks and edge cases
Generated source paths and script assumptions must stay aligned: the script hard-codes `lib/tests/module` into `TARGET`, so unusual object/source layouts can be brittle. If the Kconfig symbol count or scale factor is unset or non-numeric, the generator may produce invalid or empty output. The Makefile does not validate generator success beyond normal kbuild command failure.

### Test signals
The build signal is whether enabled `CONFIG_TEST_KALLSYMS_[A-D]` modules generate and compile. Rebuild correctness is signaled by `if_changed` rerunning the generator when command inputs change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/module/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/module/gen_test_kallsyms.sh -->
## sources/distributed-fs/ceph-client/lib/tests/module/gen_test_kallsyms.sh

### Purpose
This Bash generator creates C source files for synthetic kallsyms test modules. Depending on the target suffix, it emits modules with many exported symbols, a module that references one exported symbol from module A, or larger scaled symbol sets used to stress kallsyms lookup and compression behavior.

### Important APIs, types, and functions
Inputs are positional: `$1` target filename, `$2` number of symbols, and `$3` scale factor. The script derives `TEST_TYPE` from `lib/tests/module/test_kallsyms_*.c`. `gen_template_module_header()` writes SPDX, includes, and `pr_fmt`. `gen_num_syms(prefix, num)` emits global integer symbols named `auto_test_${prefix}_${i}` with zero-padded indexes and `EXPORT_SYMBOL_GPL()` for each. Data templates A/C/D emit exported symbol sets and a zero-returning `auto_runtime_test()`. Template B emits an `extern int auto_test_a_<middle>` declaration and returns that symbol from init-time runtime test. `gen_template_module_exit()` emits module init/exit and metadata.

### Control flow
The script computes `FIRST_B_LOOKUP` as 1 unless `NUM_SYMS > 2`, in which case it uses the midpoint. A `case` on `TEST_TYPE` writes the header, type-specific data, and common footer into `$TARGET`. Type C emits `NUM_SYMS * SCALE_FACTOR` symbols; type D emits twice that scaled number.

### State and persistence
The generator writes the generated C source at a hard-coded `DIR=lib/tests/module` path joined with the basename of the target argument. It does not preserve any prior content. There is no runtime state after generation; generated modules carry the exported symbols and runtime init function.

### Dependencies and integration points
It depends on Bash, `basename`, `sed`, `seq`, shell arithmetic, and kbuild invoking it with numeric config values. The emitted C depends on kernel module, init, printk, and symbol export APIs. The companion Makefile calls this script through `if_changed`.

### Risks and edge cases
The output path ignores the directory of `$1` and always writes under `lib/tests/module`, which may be surprising in out-of-tree or separate object builds. There is no input validation for missing, zero, negative, or nonnumeric `NUM_SYMS`/`SCALE_FACTOR`. Unknown target suffixes fall through silently and produce no file content update. Very large scale factors can generate huge source files and object files.

### Test signals
Useful signals are generated symbol counts, successful cross-module reference from B to A’s midpoint symbol, and successful compilation/loading of generated modules. Type C/D scaling provides stress coverage beyond the baseline A symbol count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/module/gen_test_kallsyms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/overflow_kunit.c -->
## sources/distributed-fs/ceph-client/lib/tests/overflow_kunit.c

### Purpose
This KUnit suite validates the kernel overflow and size-hardening helpers in `linux/overflow.h`. It covers arithmetic overflow detection, wrapping arithmetic helpers, shift validation, allocator-size saturation, size helper APIs, type-range predicates, type identity helpers, castability checks, and stack flexible-array helper macros.

### Important APIs, types, and functions
Macro-generated tables from `DEFINE_TEST_ARRAY_TYPED()` encode expected sum, difference, product, and overflow flags for signed/unsigned integer widths and mixed input/output types. `check_one_op()` validates `check_add_overflow()`, `check_sub_overflow()`, `check_mul_overflow()`, and `wrapping_{add,sub,mul}()`, including one-evaluation side-effect checks. `check_self_op()` validates `wrapping_assign_add()` and `wrapping_assign_sub()`. Shift tests use `check_shl_overflow()`. Allocation tests generated by `DEFINE_TEST_ALLOC()` exercise `kmalloc`, `kmalloc_node`, `kzalloc`, `kvmalloc`, `kvzalloc`, `__vmalloc`, and devm variants. Later tests cover `size_mul`, `size_add`, `size_sub`, `flex_array_size`, `struct_size`, `__overflows_type`, `overflows_type`, `__same_type`, `castable_to_type`, `DEFINE_RAW_FLEX`, `DEFINE_FLEX`, `__struct_size`, `__member_size`, and `STACK_FLEX_ARRAY_SIZE`.

### Control flow
The arithmetic tests are emitted by `DEFINE_TEST_FUNC_TYPED()` and run each table row through all operations. Compiler-specific skip macros avoid known Clang libcall issues for older Clang versions and 64-bit tests on 32-bit hosts. Shift tests are grouped into sane, overflow, truncate, and nonsense categories. Allocation tests register a dummy KUnit device for devm allocation APIs, perform a tiny allocation, a deliberately wrapped allocation expression, and a saturated `array_size()` allocation that must fail. Size/type/flex tests are direct table-style assertions.

### State and persistence
State is local except `global_counter`, used solely to prove macro arguments are evaluated once. The allocation test creates a transient KUnit device and frees successful allocations. No persistent kernel state is intended.

### Dependencies and integration points
The file depends on KUnit, KUnit device helpers, slab/vmalloc allocation APIs, overflow helpers, compiler type builtins/macros, and counted-by/flexible-array compiler support. The suite registers as `overflow`.

### Risks and edge cases
Because many tests are macro-generated, failures can be noisy and line-oriented rather than function-oriented. Some expectations intentionally encode current behavior, including compiler-dependent skip paths. The wrapped allocation test asserts that an unsafe raw `a * b` allocation can unexpectedly allocate a small size; this documents the hazard while the saturated helper must prevent it. Flex-array expectations depend on `CONFIG_CC_HAS_COUNTED_BY`.

### Test signals
Signals include table counts logged with `kunit_info()`, side-effect counters for macro hygiene, shift category counts, allocator saturation failures, exhaustive-ish type range combinations, and flexible-array metadata checks for both raw and counted structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/overflow_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/printf_kunit.c -->
## sources/distributed-fs/ceph-client/lib/tests/printf_kunit.c

### Purpose
This KUnit suite validates kernel `vsnprintf()`/`kvasprintf()` behavior and many kernel-specific `%p` formatting extensions. It checks output text, return lengths, null termination, truncation behavior, guard bytes around buffers, and formatted representations of kernel structures, addresses, flags, bitmaps, firmware nodes, FourCC values, and error pointers.

### Important APIs, types, and functions
`do_test()` is the core verifier: it fills a padded allocation with `FILL_CHAR`, calls `vsnprintf()`, checks the returned length, guard regions before and after the buffer, null termination, no writes beyond the terminator, and expected bytes. `__test()` runs each format through full-size, randomized truncated-size, zero-size, and `kvasprintf()` paths. The `test()` macro captures file/line. Cases include basic strings/numbers, pointer hashing (`hash_pointer()`, `plain_hash_to_buffer()`), null/error/invalid pointers, `struct resource`, `struct range`, hex strings, MAC, IPv4/IPv6, UUID, dentry path formatting, time/date formats, bitmaps, page/vma/gfp flags, firmware/software nodes, FourCC variants, and `%pe`.

### Control flow
`printf_suite_init()` allocates one padded test buffer and resets `total_tests`; `printf_suite_exit()` frees it and logs the total. Each test case calls the shared `test()` helper repeatedly. Pointer hashing tests may skip when pointer hashing is disabled or the CRNG has not initialized. `fwnode_pointer()` registers a small software-node group, validates full and short path output, then unregisters it.

### State and persistence
Persistent suite state is limited to `total_tests`, `test_buffer`, and `alloced_buffer`, all suite-scoped and freed at exit. Static `test_dentry[]` provides a synthetic dentry tree. Software nodes are registered only for the duration of `fwnode_pointer()`.

### Dependencies and integration points
The suite depends on KUnit, kernel formatting internals, random truncation, resource/range/socket/IP/UUID/dcache/time/bitmap/mm/property helpers, and global pointer-hashing behavior (`no_hash_pointers`). It integrates as suite name `printf`.

### Risks and edge cases
Several registered cases are empty placeholders (`symbol_ptr`, `kernel_ptr`, `addr`, `escaped_str`, `struct_va_format`, `struct_clk`, `netdev_features`), so suite coverage is broad but not complete for those format classes. Pointer hash expectations depend on runtime security settings and CRNG readiness, causing skips. Random truncation size broadens coverage but can make a particular truncation failure less deterministic.

### Test signals
High-value signals are guard-byte checks for buffer safety, cross-checking `vsnprintf()` and `kvasprintf()`, explicit hashed-pointer handling, structured `%p` format expected strings, flag-name fallback to numeric output, and suite total logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/printf_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/randstruct_kunit.c -->
## sources/distributed-fs/ceph-client/lib/tests/randstruct_kunit.c

### Purpose
This KUnit suite verifies `CONFIG_RANDSTRUCT` layout randomization and initializer correctness. It compares randomized and non-randomized struct layouts for ordinary members, function-pointer-only structs, mixed-type structs, nested randomized members, and named/compound initializers.

### Important APIs, types, and functions
`DO_MANY_MEMBERS()` generates eight member names consistently for enums, unsigned long fields, function pointer fields, offset-check functions, and initializers. The file defines untouched and shuffled variants: `struct randstruct_untouched`, `struct randstruct_shuffled __randomize_layout`, `struct randstruct_funcs_untouched __no_randomize_layout`, implicit `struct randstruct_funcs_shuffled`, mixed structs, and containers. `check_pair()` counts offset mismatches and expects either equality or greater-than-zero differences. Initializer helpers compare values or function pointers between untouched and shuffled forms.

### Control flow
Suite init `randstruct_test_init()` skips all tests unless `CONFIG_RANDSTRUCT` is enabled. Layout cases compare same-type controls, explicitly randomized structs, implicit all-function-pointer randomization, and nested function-pointer randomization. The deep nested function-pointer case skips under Clang due to a documented compiler issue. `randstruct_initializers()` builds named and unnamed instances, nested compound literals, full struct-copy initializers, mixed structs, and function pointer initializers, then verifies member values survive randomization.

### State and persistence
All test state is stack-local. No runtime layout changes occur; randomization is a compile-time layout property. Generated `func_a` through `func_h` return untouched offsets and serve as stable function pointer values for initializer tests.

### Dependencies and integration points
The suite depends on KUnit, randstruct compiler plugin/attribute support, `__randomize_layout`, `__no_randomize_layout`, `offsetof`, and `CONFIG_RANDSTRUCT`. It integrates under suite name `randstruct`.

### Risks and edge cases
Randomization can theoretically produce the same layout, so mismatch expectations may fail with an “unlucky or broken” message if all members land at matching offsets. The test mitigates this by using eight members but cannot eliminate probability. Compiler differences are explicit: Clang skips deep inner function pointer randomization due to known behavior. Offset comparison across different types relies on parallel member names and compatible member sets.

### Test signals
Signals include offset mismatch counts logged for each compared pair, skips when randstruct is absent or Clang cannot cover a case, and initializer value/function-pointer equality across randomized layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/randstruct_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/scanf_kunit.c -->
## sources/distributed-fs/ceph-client/lib/tests/scanf_kunit.c

### Purpose
This KUnit suite validates kernel `vsscanf()` numeric parsing and legacy `simple_strto*()` conversion helpers across integer widths, signedness, bases, delimiters, field widths, prefixes, and deterministic pseudo-random value lists.

### Important APIs, types, and functions
`_test()` wraps `vsscanf()`, checks the conversion count, then invokes a typed checker. `check_ull`, `check_ll`, `check_ulong`, `check_long`, `check_uint`, `check_int`, `check_ushort`, `check_short`, `check_uchar`, and `check_char` consume varargs and compare parsed values to expected arrays. `numbers[]` supplies boundary values copied from kstrtox tests. Macros generate single-number tests, eight-number delimited list tests, fixed-width tests, exact-value-width tests, digit-slicing tests, prefix overflow tests, and `simple_strtoull`, `simple_strtoll`, `simple_strtoul`, `simple_strtol` checks.

### Control flow
`scanf_suite_init()` allocates `test_buffer` and `fmt_buffer`, then seeds `rnd_state` deterministically. `numbers_simple()` loops through representable values for all target types and scan formats. Parameterized cases run list parsing over delimiters `" "`, `":"`, `","`, `"-"`, and `"/"`. Field-width cases either use maximum width for the type/base or the exact rendered value length. `numbers_slice()` temporarily sets an empty delimiter to parse adjacent values by field width. `numbers_prefix_overflow()` documents userland-derived behavior for `-` and `0x` prefixes that are as wide as the field. Conversion helper tests assert both value and end pointer.

### State and persistence
The suite owns two heap buffers for its lifetime and a deterministic `struct rnd_state`. Individual result arrays are stack-local. There is no persistent kernel state outside the suite.

### Dependencies and integration points
The file depends on KUnit, `vsscanf`, snprintf formatting for test generation, overflow/type helpers, bit operations (`hweight32`, `GENMASK`), prandom, and slab allocation. It registers as suite `scanf`.

### Risks and edge cases
Expected behavior for prefix overflow is derived from userland `sscanf`, so divergence may be a deliberate kernel behavior change or a bug depending on policy. Randomized list values are deterministic by seed but generated through helper logic that favors varied bit lengths rather than statistical rigor. Tests focus on numeric conversions, not string, char-class, or pointer scanning.

### Test signals
Signals include exhaustive boundary-value loops for representable values, deterministic random list parsing across delimiters, field-width slicing without delimiters, explicit conversion-count checks, and end-pointer verification for simple conversion APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/scanf_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/seq_buf_kunit.c -->
## sources/distributed-fs/ceph-client/lib/tests/seq_buf_kunit.c

### Purpose
This KUnit suite validates the `seq_buf` string-building API. It checks initialization, declaration macro behavior, clearing, appending strings/chars/formatted text, overflow semantics, raw buffer access, and commit behavior.

### Important APIs, types, and functions
The suite uses `seq_buf_init()`, `DECLARE_SEQ_BUF`, `seq_buf_has_overflowed()`, `seq_buf_buffer_left()`, `seq_buf_used()`, `seq_buf_str()`, `seq_buf_clear()`, `seq_buf_puts()`, `seq_buf_putc()`, `seq_buf_printf()`, `seq_buf_get_buf()`, and `seq_buf_commit()`. Tests are direct functions: `seq_buf_init_test`, `seq_buf_declare_test`, `seq_buf_clear_test`, `seq_buf_puts_test`, overflow variants for puts/printf, char append behavior, and `seq_buf_get_buf_commit_test`.

### Control flow
Each case constructs a small buffer-backed `struct seq_buf`, performs API operations, and checks `size`, `len`, overflow flag, used bytes, remaining buffer, and visible string. Overflow tests intentionally fill buffers to boundary conditions and then clear them to verify overflow state resets. The get/commit test obtains the writable tail pointer, writes data by hand, commits a shorter length than written for one step, then commits `-1` to force overflow.

### State and persistence
All buffers and `struct seq_buf` instances are stack-local. No allocation or persistent state exists. State transitions of interest are purely the `seq_buf` fields and buffer contents.

### Dependencies and integration points
The file depends on KUnit and `linux/seq_buf.h`. It integrates as KUnit suite `seq_buf`.

### Risks and edge cases
The tests assert current semantics where the backing string remains null-terminated and visible text excludes overflowed characters. The suite covers small buffers but not very large buffers, concurrency, or external users such as tracing. Manual `memcpy()` into `seq_buf_get_buf()` output assumes the returned pointer is valid when length is nonzero, which is part of the API being checked.

### Test signals
Signals are exact `len`/used/left checks, string equality after every mutation, overflow flag transitions, reset after clear, raw buffer lengths from `seq_buf_get_buf()`, and negative commit overflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/seq_buf_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/siphash_kunit.c -->
## sources/distributed-fs/ceph-client/lib/tests/siphash_kunit.c

### Purpose
This KUnit suite verifies the kernel SipHash and HalfSipHash implementations against known reference vectors. It covers aligned and intentionally unaligned byte input plus specialized integer helper entry points.

### Important APIs, types, and functions
Static keys `test_key_siphash` and `test_key_hsiphash` are fixed byte-order test keys. `test_vectors_siphash[64]` contains SipHash2-4 reference outputs. `test_vectors_hsiphash[64]` is selected differently for 64-bit and 32-bit `BITS_PER_LONG`, matching architecture-dependent HalfSipHash key shape. The `chk()` macro wraps `KUNIT_EXPECT_EQ_MSG()`. `siphash_test()` exercises `siphash()`, `hsiphash()`, `siphash_1u64()` through `siphash_4u64()`, `siphash_1u32()` through `siphash_4u32()`, and halfsiphash u32 helpers.

### Control flow
The single test case initializes aligned arrays `in[64]` and `in_unaligned[65]`, fills incremental byte values, and for lengths 0 through 63 compares aligned and `+1` unaligned hash results against the corresponding vector. It then checks specialized integer helper calls by composing integer values whose byte representation corresponds to selected vector lengths.

### State and persistence
All input buffers are stack-local and deterministic. Static key/vector tables are immutable. No persistent state, randomization, or allocation is involved.

### Dependencies and integration points
The suite depends on KUnit, `linux/siphash.h`, kernel type/bitness definitions, and module metadata. It registers as suite `siphash` and is dual-licensed BSD/GPL consistent with the implementation lineage.

### Risks and edge cases
HalfSipHash expected vectors differ by word size, so architecture-specific branches must stay synchronized with implementation behavior. The test validates known vectors and unaligned access but does not benchmark performance or test randomized keys beyond the fixed reference key. Endianness assumptions are encoded in the chosen constants and helper expectations.

### Test signals
Strong signals are 64 reference lengths for SipHash and HalfSipHash, aligned versus unaligned equality to the same vectors, architecture-specific HalfSipHash vector coverage, and coverage of optimized fixed-width integer helper APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/siphash_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/slub_kunit.c -->
## sources/distributed-fs/ceph-client/lib/tests/slub_kunit.c

### Purpose
This KUnit suite exercises SLUB allocator debugging and hardening behavior. It deliberately corrupts redzones, poisoned free objects, freelist pointers, kmalloc redzones, leak accounting, kfree_rcu destruction, krealloc zeroing, and optional nolock allocation from perf overflow context, then checks reported slab error counts.

### Important APIs, types, and functions
`test_kmem_cache_create()` wraps `kmem_cache_create()` with `SLAB_NO_USER_FLAGS` and sets `SLAB_SKIP_KFENCE` to avoid KFENCE intercepting the same corruption. `slab_errors` is exposed to KUnit through `kunit_add_named_resource()` in `test_init()`. Core cases use `validate_slab_cache()`, `kmem_cache_alloc/free/destroy()`, `kasan_disable_current()`/`kasan_enable_current()`, `__kmalloc_cache_noprof()`, `alloc_hooks()`, `kfree_rcu()`, workqueues, `krealloc(... | __GFP_ZERO)`, and optionally perf event overflow callbacks with `kmalloc_nolock()`/`kfree_nolock()`.

### Control flow
Each test creates a purpose-specific cache, performs allocation/free/corruption sequence, calls validation or destruction, and asserts expected `slab_errors`. Non-KASAN-only tests corrupt freed-object metadata and data bytes. RCU tests skip when built-in because module lifetime constraints make `kfree_rcu()` unsuitable. Workqueue destruction repeatedly schedules delayed cache destruction after `kfree_rcu()`. The perf test creates a pinned hardware counter, enables callbacks during heavy allocate/free loops, then checks no slab errors unless allocations failed and the test skips.

### State and persistence
`slab_errors` is reset per test in suite init. Static `resource` and optional static `objects[]` are suite/test support state. Caches, workqueues, perf events, and allocations are intended to be destroyed or freed within each case, though some tests intentionally trigger leak or destroy diagnostics.

### Dependencies and integration points
The suite reaches into allocator internals via `../mm/slab.h`, uses KUnit bug support, mm/slab APIs, KASAN controls, RCU, workqueues/delays, and optional perf events. It integrates as suite `slub_test`.

### Risks and edge cases
The suite intentionally writes out of bounds and after free with KASAN disabled around selected operations; incorrect guard handling could crash the test kernel. Expected error counts are tightly coupled to SLUB validation internals. Some cases skip depending on KASAN, built-in/module mode, workqueue allocation, cache creation, perf support, or allocation failures.

### Test signals
Signals include exact `slab_errors` counts after corruption/repair sequences, zero-error expectations for valid RCU and krealloc paths, skip reasons for unsupported modes, and optional stress of nolock allocation in perf overflow context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/slub_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/stackinit_kunit.c -->
## sources/distributed-fs/ceph-client/lib/tests/stackinit_kunit.c

### Purpose
This KUnit suite validates compiler-based stack variable initialization, especially `-ftrivial-auto-var-init={zero,pattern}` and STRUCTLEAK-style clearing. It detects whether scalars, arrays, structs, unions, padding holes, user-pointer structs, copy assignments, and switch-scope declarations leak prior stack contents.

### Important APIs, types, and functions
The file uses macro generation to create many `do_nothing_*`, `leaf_*`, and `test_*` functions. Global tracking (`check_buf`, `fill_start`, `target_start`, `fill_size`, `target_size`) records the tested stack slot and copied bytes. `DEFINE_TEST()` creates a leaf function that optionally fills a local variable with `FILL_BYTE`, then later exposes the compiler-initialized bytes through `memcpy(check_buf, ...)`. `DEFINE_TEST_DRIVER()` performs the two-call fill/extract protocol, validates stack-frame overlap with `stackinit_range_contains()`, and fails or skips expected-failure cases based on `xfail`.

### Control flow
Macro families generate tests for scalar zero/none, char arrays, structs with small/big/trailing padding holes, packed structs, user-pointer structs, and unions with same or mismatched member sizes. Initialization modes include zero, old zero, static/dynamic/runtime partial/all, assigned static/dynamic partial/all, assigned copy, and none. Special switch tests cover variables declared before the first `case`, which compilers often cannot initialize. The suite registers a large flat KUnit case table grouped by expected behavior.

### State and persistence
Global tracking buffers are overwritten by each test. There is no heap allocation and no persistent kernel object. The “state” under test is transient stack content, with `forced_mask` volatile to keep the compiler from optimizing away fills.

### Dependencies and integration points
The suite depends on KUnit, compiler instrumentation options, kernel config symbols such as `CONFIG_INIT_STACK_NONE`, architecture-specific `CONFIG_M68K`, and `__user` annotations. It integrates as suite `stackinit`.

### Risks and edge cases
Expectations are intentionally compiler- and configuration-dependent. Some tests use XFAIL/skip semantics when uninitialized bytes are expected, so skip counts can represent known gaps rather than infrastructure failures. Stack-frame colocation is checked because compiler layout differences could otherwise invalidate the fill/extract comparison. Copy-assignment tests are expected to fail because copying preserves padding bytes.

### Test signals
Signals include detection of any retained `FILL_BYTE`, assertion that fill and target stack ranges overlap, KUnit skips for expected uninitialized bytes, and broad generated coverage over scalar, array, struct, union, padding, user field, and switch declaration cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/stackinit_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/string_helpers_kunit.c -->
## sources/distributed-fs/ceph-client/lib/tests/string_helpers_kunit.c

### Purpose
This KUnit suite validates helper routines from `lib/string_helpers.c`: unescaping, escaping, human-readable size formatting, and ASCII case conversion. It is heavily table-driven and checks both returned lengths and output bytes.

### Important APIs, types, and functions
`test_string_check_buf()` compares expected lengths and bytes. `strings[]` drives `string_unescape()`, `string_unescape_any()`, and in-place variants for space, octal, hex, and special escapes. `escape0[]` and `escape1[]` encode expected `string_escape_mem()` output without and with a dictionary. `test_string_find_match()` applies flag normalization, including NULL-aware cases and octal-over-hex priority. Size helpers use `string_get_size()` with `STRING_UNITS_10`, `STRING_UNITS_2`, `STRING_UNITS_NO_SPACE`, and `STRING_UNITS_NO_BYTES`. `test_upper_lower()` covers `string_upper()` and `string_lower()`.

### Control flow
`test_unescape()` iterates all unescape flag combinations, runs one random in-place unescape combination, then iterates all escape flag combinations for both dictionaries. `test_string_escape()` optionally injects NULL bytes, builds a concatenated input and expected output, calls `string_escape_mem()`, and separately checks overflow/length-only behavior by passing a NULL output buffer of size 0. `test_get_size()` runs representative small, normal, odd block-size, and huge values through decimal and binary unit modes. `test_upper_lower()` allocates a destination per case, converts, compares, and frees.

### State and persistence
All buffers are KUnit-managed or manually freed within a test. There is no persistent state. One in-place unescape test uses `get_random_u32_below()` to choose flags, but all non-in-place and escape combinations are exhaustive over masks.

### Dependencies and integration points
The suite depends on KUnit, random helpers, string helpers, allocation, and array-size utilities. It integrates as suite `string_helpers`.

### Risks and edge cases
The escape tables are dense, and missing combinations are represented by absent outputs that get skipped for a particular flag set. The one random in-place flag combination does not exhaustively cover every in-place mode in a single run. Expected strings include embedded control and high-bit bytes, so source readability and escaping correctness matter.

### Test signals
Signals include exhaustive flag-mask iteration for non-in-place unescape and escape modes, length-only overflow checks for `string_escape_mem()`, byte-for-byte expected output comparisons, unit-format variations with and without spaces/bytes suffixes, and upper/lower conversion checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/string_helpers_kunit.c -->
