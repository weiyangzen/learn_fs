# subset-b-006111 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_xarray.c -->
# sources/distributed-fs/ceph-client/lib/test_xarray.c

## Purpose
`test_xarray.c` is a loadable kernel self-test module for the XArray API. It exercises both the public helpers (`xa_load`, `xa_store`, `xa_insert`, `xa_erase`, `xa_alloc`, `xa_find`, marks, reserves, compare/exchange, destroy) and the advanced `xas_*` state-machine API used by subsystems such as page cache and workingset shadow-node handling.

## Important APIs, types, and functions
The test centers on `struct xarray`, `XA_STATE`, `XA_STATE_ORDER`, `struct xa_node`, `xa_mk_value()`, `XA_RETRY_ENTRY`, `XA_ZERO_ENTRY`, mark constants, and allocation variants created by `DEFINE_XARRAY`, `DEFINE_XARRAY_ALLOC`, and `DEFINE_XARRAY_ALLOC1`. Local helpers such as `xa_store_index()`, `xa_insert_index()`, `xa_alloc_index()`, and `xa_store_order()` normalize value entries and retry out-of-memory allocation paths with `xas_nomem()`. The broad check functions cover error encoding, retry behavior, loading, marks, shrinking, insertion, `xa_cmpxchg()`, reservation, multi-index storage, cyclic allocation, conflict iteration, find/pause/move traversal, range creation, range storage, splitting, object alignment, workingset update callbacks, accounting, order lookup, and destruction.

## Control flow
`module_init(xarray_checks)` runs a fixed sequence of `check_*()` routines against a global `array` and the allocation arrays `xa0`/`xa1`. Each helper mutates an array, validates invariants through `XA_BUG_ON`, and normally tears state down through `xa_erase()` or `xa_destroy()` before returning. Multi-index tests are guarded by `CONFIG_XARRAY_MULTI`; the non-multi configuration still validates single-entry behavior with reduced order limits. Some advanced loops deliberately stress large index ranges and use `schedule()` in page-cache-like lookups to avoid soft lockups.

## State and persistence
The module persists only in-kernel test counters (`tests_run`, `tests_passed`), the static XArrays, `some_val` sentinel objects, and a temporary `shadow_nodes` list. No filesystem or durable state is written. Concurrency-sensitive paths explicitly use `rcu_read_lock()`, `xa_lock()`, `xas_lock()`, and IRQ-safe locking where the tested API expects them.

## Dependencies and integration points
It depends on `<linux/xarray.h>`, module infrastructure, RCU, scheduler calls, page-size constants, and internal XArray node details. It integrates with the kernel module test path rather than KUnit; pass/fail is reported through `printk()` and the module init return code.

## Risks and edge cases
The test intentionally touches internal node fields (`count`, `nr_values`, `xa_head`, `private_list`) and advanced APIs, so it is sensitive to legitimate XArray implementation refactors. Large multi-order loops can be expensive. Assertions rely on value-entry encoding and may need updates if reserved/retry/internal entry semantics change.

## Test signals
Success is `XArray: <n> of <n> tests passed` and a zero module init return. Failures dump the function/line, XArray contents when available, and a stack trace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_xarray.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/Makefile -->
# sources/distributed-fs/ceph-client/lib/tests/Makefile

## Purpose
This Makefile wires kernel library tests into Kbuild. It maps many `CONFIG_*_KUNIT` and legacy test symbols to the corresponding object files under `lib/tests`, and applies test-specific compiler flags where instrumentation or compiler diagnostics would otherwise obscure the test intent.

## Important APIs, types, and functions
The file uses standard Kbuild `obj-$(CONFIG_SYMBOL) += object.o` declarations. Notable flag overrides include `DISABLE_STRUCTLEAK_PLUGIN` for bitfield and fortify tests, `cc-disable-warning` for fortify warning families, `CC_FLAGS_FTRACE` for fprobe sanity testing, `-DDISABLE_BRANCH_PROFILING` for printf KUnit, and warning suppression for longest symbol, overflow, and stackinit tests.

## Control flow
There is no runtime control flow. Kbuild evaluates the config-gated object list and compiles only enabled suites. `obj-$(CONFIG_TEST_RUNTIME_MODULE) += module/` descends into a runtime module subdirectory when that test is selected.

## State and persistence
The Makefile has no mutable state. It influences build products and object inclusion but does not persist runtime data.

## Dependencies and integration points
It integrates the researched KUnit files in this subset: `base64_kunit.o`, `bitfield_kunit.o`, `bitops_kunit.o`, `blackhole_dev_kunit.o`, `checksum_kunit.o`, `cmdline_kunit.o`, `cpumask_kunit.o`, `ffs_kunit.o`, `fortify_kunit.o`, `glob_kunit.o`, `hashtable_test.o`, `is_signed_type_kunit.o`, `kfifo_kunit.o`, `kunit_iov_iter.o`, and `list-private-test.o`.

## Risks and edge cases
Build behavior is config-sensitive. Test-specific CFLAGS are part of the contract: removing them may convert intended runtime tests into compile warnings, false positives, or plugin interactions. The fortify flags are especially important because that suite intentionally exercises overread/overwrite paths.

## Test signals
The signal is successful object selection and compilation under the relevant Kconfig symbols. Runtime signals are emitted by each KUnit suite registered by the selected object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/base64_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/base64_kunit.c

## Purpose
`base64_kunit.c` validates kernel Base64 encoding and decoding for standard, URL-safe, and IMAP variants, with and without padding. It also includes a small timing benchmark for the standard variant.

## Important APIs, types, and functions
The suite calls `base64_encode()`, `base64_decode()`, `get_random_bytes()`, `ktime_get_ns()`, `div64_u64()`, `kmalloc()`, `kfree()`, and KUnit assertions. Helpers `expect_encode_ok()`, `expect_decode_ok()`, and `expect_decode_err()` wrap output length, string, memory, and error checks. `run_perf_and_check()` allocates buffers, does a random round trip, then reports average encode/decode nanoseconds with `kunit_info()`.

## Control flow
`base64_test_cases` registers four tests: performance, standard encode vectors, standard decode vectors, and variant checks. The encode/decode tests walk RFC-style examples (`f`, `fo`, `foo`, `foobar`) plus longer alphabet and punctuation strings. Decode tests cover invalid characters, malformed padding, too-short padded input, excess padding, embedded NUL, and mismatched padding policy. Variant tests derive expected URL-safe and IMAP output by rewriting standard `+`, `/` characters and verify decoding back to the sample bytes.

## State and persistence
All state is stack- or heap-local to each test. Random benchmark input is transient and not used as a golden vector. No global mutable state or persistent output is kept beyond KUnit logs.

## Dependencies and integration points
The file depends on `<linux/base64.h>` and KUnit. It is built through `CONFIG_BASE64_KUNIT` in the tests Makefile.

## Risks and edge cases
The benchmark test is not a strict performance gate; it can add noise to test logs and runtime. Fixed 128-byte helper buffers are adequate for listed vectors but would need resizing for larger new cases. Error behavior assumes `base64_decode()` returns `-1` for invalid input.

## Test signals
Pass signals are KUnit equality, string, and memory assertions. Performance emits informational timing lines for 64B and 1KB standard-variant round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/base64_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/bitfield_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/bitfield_kunit.c

## Purpose
`bitfield_kunit.c` tests the typed bitfield encode/get helpers across native, little-endian, and big-endian integer forms. It is aimed at compile-time constant folding and runtime variable mask correctness.

## Important APIs, types, and functions
The macros `CHECK_ENC_GET_U`, `CHECK_ENC_GET_LE`, `CHECK_ENC_GET_BE`, and `CHECK_ENC_GET` exercise `u8/u16/u32/u64_encode_bits()`, `*_get_bits()`, and endian wrappers such as `le16_encode_bits()` and `be64_get_bits()`. `test_bitfields_constants()` uses literal masks and expected encoded values. `test_bitfields_variables()` uses `hweight32()` and `__ffs64()` to verify variable mask shifting for many typed widths.

## Control flow
The KUnit suite registers two test functions. Constant tests run a fixed matrix for 8-, 16-, 32-, and 64-bit fields. Variable tests loop every value representable by the mask width and assert that encoding equals `v << __ffs64(mask)`. An optional `TEST_BITFIELD_COMPILE` block contains deliberately invalid uses for negative compile testing but is not part of the normal suite.

## State and persistence
The file has no persistent state; all checks are expression-level assertions.

## Dependencies and integration points
It depends on `<linux/bitfield.h>`, endian conversion helpers, and KUnit. The Makefile disables the structleak plugin for this object and builds it through `CONFIG_BITFIELD_KUNIT`.

## Risks and edge cases
This test is tightly coupled to macro diagnostics and compiler optimization. The variable loop uses `1 << hweight32(mask)`, which is safe for the listed masks but would need care for full-width masks. The compile-fail block must stay disabled in regular test runs.

## Test signals
Failures report the encoded value and mask through KUnit assertion messages. Passing means native and endian encode/get helpers preserve value semantics for the covered masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/bitfield_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/bitops_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/bitops_kunit.c

## Purpose
`bitops_kunit.c` validates core bit operations and order helpers. It covers individual bit mutation APIs and `get_count_order()`/`get_count_order_long()` boundary behavior.

## Important APIs, types, and functions
The suite uses `DECLARE_BITMAP`, `bitmap_zero()`, `set_bit()`, `clear_bit()`, `change_bit()`, `test_bit()`, `test_and_set_bit()`, `test_and_clear_bit()`, `test_and_change_bit()`, `find_first_bit()`, `get_count_order()`, and `get_count_order_long()`. Parameter fixtures are declared with `KUNIT_ARRAY_PARAM_DESC()`.

## Control flow
Parameterized bit tests run across enum-derived bit positions 4, 7, 11, 31, and 88 in a 256-bit bitmap. Each test mutates one bit, verifies visible state and return values, then confirms the bitmap is empty via `find_first_bit() == BITOPS_LENGTH`. Order tests feed selected counts around powers of two and high-bit boundaries. On 64-bit builds, an additional long-count table exercises values above 32 bits.

## State and persistence
Each test allocates only stack bitmaps and local parameters. No state persists between KUnit cases.

## Dependencies and integration points
It depends on `<linux/bitops.h>`, `<linux/module.h>`, and KUnit. It is built by `CONFIG_BITOPS_KUNIT`.

## Risks and edge cases
The order tables encode architecture expectations, especially for `CONFIG_64BIT`. Any change in helper semantics around zero or high-bit rounding must update these fixtures. The bit mutation tests do not exercise concurrent atomicity; they validate single-threaded API semantics.

## Test signals
KUnit parameter descriptions identify the failing bit position or order value. Pass means mutation APIs return prior state correctly, leave expected bitmap content, and order helpers round counts as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/bitops_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/blackhole_dev_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/blackhole_dev_kunit.c

## Purpose
`blackhole_dev_kunit.c` smoke-tests the networking `blackhole_netdev` by transmitting a constructed IPv6/UDP skb through `dev_queue_xmit()` and expecting the kernel to handle it without crashing.

## Important APIs, types, and functions
The test uses `alloc_skb()`, `skb_reserve()`, `__skb_put()`, `skb_push()`, `skb_set_transport_header()`, `skb_set_network_header()`, `skb_set_mac_header()`, `dev_queue_xmit()`, `blackhole_netdev`, `struct ipv6hdr`, `struct udphdr`, and Ethernet protocol constants.

## Control flow
`test_blackholedev()` allocates a 256-byte skb, reserves room for Ethernet, IPv6, and UDP headers, fills payload bytes, pushes UDP, IPv6, and Ethernet header space, assigns protocol metadata, sets `skb->dev` to `blackhole_netdev`, and transmits. The only runtime assertion after construction is that `dev_queue_xmit()` returns `NET_XMIT_SUCCESS`.

## State and persistence
The skb is transient and is handed to the networking stack on transmit. The test does not maintain global state. It relies on the globally initialized blackhole device from networking subsystem setup.

## Dependencies and integration points
It depends on KUnit, skb and netdevice APIs, IPv6/UDP headers, and `net/dst.h`. It is selected by `CONFIG_BLACKHOLE_DEV_KUNIT_TEST`.

## Risks and edge cases
This is a crash/sanity test, not a packet semantic test. Header fields are minimal and UDP checksum is zero, so behavior depends on blackhole device acceptance rather than full protocol validation. It requires networking initialization sufficient to expose `blackhole_netdev`.

## Test signals
Failure signals are allocation failure or a transmit return other than `NET_XMIT_SUCCESS`. Kernel crashes or warnings in the transmit path would also be meaningful regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/blackhole_dev_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/checksum_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/checksum_kunit.c

## Purpose
`checksum_kunit.c` verifies Internet checksum helpers with fixed golden data. It covers `csum_partial()` plus `csum_fold()`, carry-heavy inputs, no-carry inputs, IPv4 header checksums via `ip_fast_csum()`, and IPv6 pseudo-header checksums via `csum_ipv6_magic()`.

## Important APIs, types, and functions
The file uses `<asm/checksum.h>`, `<net/ip6_checksum.h>`, `__wsum`, `__sum16`, `csum_partial()`, `csum_fold()`, `ip_fast_csum()`, and `csum_ipv6_magic()`. Helpers `to_sum16()` and `to_wsum()` translate little-endian stored vectors into CPU-native checksum types. `CHECK_EQ` compares force-cast checksum values through KUnit.

## Control flow
Large static arrays provide deterministic random input and expected outputs: `random_buf`, `expected_results`, `init_sums_no_overflow`, `expected_csum_ipv6_magic`, and `expected_fast_csum`. `assert_setup_correct()` validates fixture lengths. The partial checksum tests iterate every alignment up to `TEST_BUFLEN` and every length up to `MAX_LEN` that fits. IPv4 checks sweep header word counts from 5 to 14 and 181 offsets. IPv6 checks derive source, destination, length, protocol, and starting checksum fields from offsets in `random_buf`; the test returns early if `CONFIG_NET` is not enabled.

## State and persistence
The only mutable state is the static temporary buffer `tmp_buf`, rewritten per test. There is no persistent storage.

## Dependencies and integration points
It is built via `CONFIG_CHECKSUM_KUNIT` and integrates with architecture-specific checksum implementations. It also depends on networking types for IPv6 pseudo-header validation.

## Risks and edge cases
Golden vectors are endian-aware through conversion helpers; incorrect fixture updates could mask regressions. The alignment/length sweeps are intentionally broad and may be relatively expensive. The IPv6 test silently skips if networking is not enabled, reducing coverage in minimal configs.

## Test signals
Pass means all checksum outputs match the golden vectors for the covered alignments, lengths, and protocol variants. Failures identify the KUnit assertion but not every loop coordinate unless instrumented further.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/checksum_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/cmdline_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/cmdline_kunit.c

## Purpose
`cmdline_kunit.c` tests command-line integer parsing helpers from `cmdline.c`, especially malformed tokens, leading/trailing integers, negative signs, separators, and range expansion.

## Important APIs, types, and functions
The suite calls `get_option()`, `get_options()`, `get_random_u8()`, `memchr_inv()`, `sprintf()`, `strlen()`, and KUnit assertions. Static tables pair input strings with expected return codes, pointer offsets, parsed counts, and expanded integer arrays.

## Control flow
`cmdline_do_one_test()` calls `get_option()` on a mutable output pointer and verifies both return code and consumed offset. Three tests compose no-int, leading-int, and trailing-int cases from the same punctuation table. `cmdline_do_one_range_test()` calls `get_options()` twice: once with a result capacity to validate parsed values, then with zero capacity to validate count-only behavior and ensure the data region stays zeroed. `cmdline_test_range()` iterates fixed range strings with expected expansions.

## State and persistence
All buffers are stack-local. Random bytes are used only to vary valid integer prefixes/suffixes; expected behavior depends on token structure, not specific value.

## Dependencies and integration points
It depends on KUnit, kernel string helpers, random helpers, and `get_option()`/`get_options()` implementations. It is built through `CONFIG_CMDLINE_KUNIT_TEST`.

## Risks and edge cases
The tests encode subtle pointer-consumption semantics for bare `-` and malformed negative ranges. Random values improve variety but can make reproducing exact input strings slightly less direct unless logs are added.

## Test signals
Failures report the pattern string and whether parsed count, pointer offset, value expansion, or validation-only behavior diverged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/cmdline_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/cpumask_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/cpumask_kunit.c

## Purpose
`cpumask_kunit.c` validates basic CPU mask counting, first/last/next lookup helpers, iterator macros, binary mask-iterator variants, wrap iteration, and built-in possible/online/present CPU iterators.

## Important APIs, types, and functions
The file uses `cpumask_t`, `cpu_possible_mask`, `cpu_online_mask`, `cpu_present_mask`, `cpumask_weight()`, `cpumask_empty()`, `cpumask_full()`, `cpumask_first()`, `cpumask_first_zero()`, `cpumask_last()`, `cpumask_next()`, `cpumask_next_zero()`, `for_each_cpu*()` macros, `num_*_cpus()`, and `cpu_hotplug_disable()/enable()`.

## Control flow
Suite init clears `mask_empty` and fills `mask_all`. The tests compare helper results against `nr_cpu_ids` and `nr_cpumask_bits`, then use iterator-count macros to ensure iteration count equals `cpumask_weight()` or the result of a corresponding mask operation. Built-in online and present iterator tests run while CPU hotplug is disabled so the masks do not change mid-test.

## State and persistence
The file has three static masks: `mask_empty`, `mask_all`, and `mask_tmp`. They are initialized per KUnit test through the suite `.init` hook. CPU hotplug is temporarily disabled in one test and re-enabled before return.

## Dependencies and integration points
It depends on `<linux/cpu.h>`, `<linux/cpumask.h>`, and KUnit. It is built via `CONFIG_CPUMASK_KUNIT_TEST`.

## Risks and edge cases
The suite assumes CPU 0 is possible and that `nr_cpu_ids` aligns with possible CPU mask weight in the active test configuration. Any failure path inside the hotplug-disabled region must still re-enable hotplug; the current code has no early assert/return there.

## Test signals
KUnit messages print mask contents with `%*pbl`, making failures diagnosable by actual mask membership and iterator count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/cpumask_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/ffs_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/ffs_kunit.c

## Purpose
`ffs_kunit.c` tests the find-first/find-last bit helper family: `ffs()`, `fls()`, `__ffs()`, `__fls()`, `fls64()`, `__ffs64()`, and `ffz()`. It also verifies that selected functions retain `__attribute_const__` behavior useful for compile-time optimization.

## Important APIs, types, and functions
The suite defines structured fixtures for 32-bit/unsigned-long and 64-bit values. Validators check exact outputs, mathematical relationships between 1-based and 0-based APIs, range bounds, and zero-input special cases. `CREATE_WRAPPER()` emits noinline functions with `BUILD_BUG_ON()` and `barrier_data()` to confirm static initializer behavior after function calls.

## Control flow
Tests run fixture tables for basic `ffs/fls`, 64-bit cases, relationship checks, edge patterns, `ffz()` exact cases, `ffz()` relationship patterns, and attribute-const wrappers. Undefined cases are deliberately skipped or only invoked for completion: `__ffs*()`/`__fls()` on zero are not asserted, and `ffz(~0UL)` is treated as implementation-defined.

## State and persistence
There is no persistent state. All fixtures are static constants and all validation state is local to test functions.

## Dependencies and integration points
It depends on `<linux/bitops.h>` and KUnit and is selected by `CONFIG_FFS_KUNIT_TEST`.

## Risks and edge cases
Many constants are 32-bit shaped but stored in `unsigned long`; behavior on 64-bit remains valid but does not exhaust all high unsigned-long positions outside explicit 64-bit tests. The attribute-const regression is compiler-sensitive by design.

## Test signals
Assertion messages include function name, hexadecimal input, description, expected value, and actual value for most correctness checks. Pass means exact and relational semantics hold for the covered patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/ffs_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/fortify_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/fortify_kunit.c

## Purpose
`fortify_kunit.c` is a runtime test suite for `CONFIG_FORTIFY_SOURCE`. It verifies compile-time and dynamic object-size discovery, allocation size attributes, string helper bounds checks, memory helper bounds checks, and protected failure behavior.

## Important APIs, types, and functions
The file intentionally redefines `fortify_panic()` and `fortify_warn_once()` before including string headers so overflows increment KUnit counters instead of panicking. `fortify_add_kunit_error()` finds named KUnit resources for read/write overflow counters. Tests cover `__compiletime_strlen`, `__builtin_object_size`, `__builtin_dynamic_object_size`, `kmalloc`/`kcalloc`/`krealloc` families, `vmalloc`, `kvmalloc`, devm allocators, `kmemdup`, `strlen`, `strnlen`, `strcpy`, `strncpy`, `strscpy`, `strcat`, `strncat`, `strlcat`, `memcpy`, `memmove`, `memscan`, `memchr`, `memchr_inv`, and `memcmp`.

## Control flow
Suite init skips unless `CONFIG_FORTIFY_SOURCE` is enabled, resets counters, and registers them as KUnit resources. Allocation-size tests are macro-generated for constant and dynamic lengths; dynamic tests skip if the compiler lacks `__builtin_dynamic_object_size`. String and memory tests build padded structs so overflow attempts can be counted while confirming guard fields are not modified.

## State and persistence
Static resources and global counters track overflow classifications per test. Allocations are freed directly, through devm teardown, or by KUnit device cleanup. No durable state is produced.

## Dependencies and integration points
It depends on KUnit device/resource APIs, test-bug support, allocator APIs, string/memory fortify wrappers, vmalloc, and compiler builtins. The Makefile suppresses expected string warnings, unsequenced warnings, and structleak instrumentation effects.

## Risks and edge cases
The suite is highly compiler- and configuration-sensitive. It depends on include ordering and macro redefinition to intercept fortify behavior. Because it deliberately performs invalid operations under guarded wrappers, unrelated sanitizer or compiler changes can alter expected counters.

## Test signals
Pass means expected overflow counters increment and surrounding padding remains unchanged. Skips indicate missing `CONFIG_FORTIFY_SOURCE` or dynamic object-size builtin support for specific dynamic allocation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/fortify_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/glob_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/glob_kunit.c

## Purpose
`glob_kunit.c` tests `glob_match()` pattern matching. It covers exact strings, empty patterns, character classes, negated classes, ranges, bracket corner cases, `?`, `*`, and multi-asterisk backtracking.

## Important APIs, types, and functions
The central fixture is `struct glob_test_case` with `pat`, `str`, and `expected`. `glob_case_to_desc()` formats parameter descriptions. `KUNIT_ARRAY_PARAM()` generates one KUnit parameter per fixture, and `glob_test_match()` compares `glob_match()` with the expected boolean.

## Control flow
The single parameterized test runs through all fixtures. Early cases validate exact and empty behavior. Middle cases focus on bracket parsing, including `!` negation, ranges, literal `-`, `[` and `]`. Later cases exercise wildcard length constraints and backtracking over repeated `*` segments.

## State and persistence
All state is constant fixture data plus KUnit parameter plumbing. There is no mutable global state.

## Dependencies and integration points
It depends on `<linux/glob.h>`, module metadata, and KUnit. It is built with `CONFIG_GLOB_KUNIT_TEST`.

## Risks and edge cases
The suite is table-driven and easy to extend, but failures in complex backtracking only identify the pattern/string pair, not internal matcher state. It does not cover path separators or locale-specific behavior; it tests the kernel glob semantics directly.

## Test signals
KUnit parameter descriptions include both pattern and string, and failure messages include expected result. Pass means every listed glob fixture matches the encoded semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/glob_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/hashtable_test.c -->
# sources/distributed-fs/ceph-client/lib/tests/hashtable_test.c

## Purpose
`hashtable_test.c` validates Linux kernel hashtable macros for initialization, emptiness, hashed-node detection, insertion, deletion, full iteration, safe deletion during iteration, and key-bucket iteration.

## Important APIs, types, and functions
The local `struct hashtable_test_entry` embeds an `hlist_node` plus `key`, `data`, and `visited`. Tests use `DEFINE_HASHTABLE`, `DECLARE_HASHTABLE`, `hash_init()`, `hash_empty()`, `hash_add()`, `hash_hashed()`, `hash_del()`, `hash_for_each()`, `hash_for_each_safe()`, `hash_for_each_possible()`, and `hash_for_each_possible_safe()`.

## Control flow
Each KUnit case builds a small stack hashtable, inserts one or more entries, then validates macro behavior. The possible-iteration tests intentionally add three entries with key 0 and one entry with key 1, then inspect bucket placement to allow either three or four visits depending on whether both keys hash to the same bucket. Safe tests delete entries during traversal and verify each original entry was visited once.

## State and persistence
All hashtables and entries are stack-local. `visited` fields provide per-test state for traversal coverage.

## Dependencies and integration points
The file depends on `<linux/hashtable.h>` and KUnit and is built by `CONFIG_HASHTABLE_KUNIT_TEST`.

## Risks and edge cases
Because `hash_for_each_possible()` iterates a bucket rather than filtering by key, the test correctly accepts same-bucket non-key entries. Future readers must not tighten that expectation incorrectly. The tests do not cover concurrent RCU hashtable variants.

## Test signals
Failures indicate unexpected emptiness, missing hashed state, unexpected keys/data during traversal, incorrect visit counts, or failed deletion semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/hashtable_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/is_signed_type_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/is_signed_type_kunit.c

## Purpose
`is_signed_type_kunit.c` tests the `is_signed_type()` compile-time type trait for scalar integer types, enums, pointers, and `bool`.

## Important APIs, types, and functions
The suite defines one unsigned enum and one signed enum, then calls `is_signed_type(type)` inside `KUNIT_EXPECT_EQ()` checks. Covered types include `bool`, signed/unsigned char, plain `char`, int, unsigned int, long, unsigned long, long long, unsigned long long, enum variants, `void *`, and `const char *`.

## Control flow
A single KUnit test function runs all type-trait assertions in sequence. The suite registers that function under the `is_signed_type` suite name.

## State and persistence
There is no runtime state other than assertion results. The tested property is a compile-time expression.

## Dependencies and integration points
It depends on `<linux/compiler.h>` for `is_signed_type()` and KUnit. It is selected by `CONFIG_IS_SIGNED_TYPE_KUNIT_TEST`.

## Risks and edge cases
The expected result for plain `char` is `false`, which reflects this kernel/compiler configuration and is intentionally distinct from `signed char`. Enum signedness expectations depend on the negative enumerator in `enum signed_enum`.

## Test signals
Pass means the trait returns the expected boolean for each listed type category. A failure points directly to the type assertion that changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/is_signed_type_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/kfifo_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/kfifo_kunit.c

## Purpose
`kfifo_kunit.c` tests the generic kernel FIFO API for static FIFOs, declared/initialized FIFOs, pointer-backed allocated FIFOs, insertion/removal, length accounting, reset behavior, and peek semantics.

## Important APIs, types, and functions
The file uses `DEFINE_KFIFO`, `DECLARE_KFIFO`, `DECLARE_KFIFO_PTR`, `INIT_KFIFO`, `kfifo_initialized()`, `kfifo_is_empty()`, `kfifo_len()`, `kfifo_reset()`, `kfifo_put()`, `kfifo_get()`, `kfifo_in()`, `kfifo_out()`, `kfifo_alloc()`, `kfifo_free()`, `kfifo_peek()`, and `__is_kfifo_ptr()`.

## Control flow
Ten KUnit cases each create a local FIFO. Tests verify a defined FIFO starts initialized and empty, reset clears length, repeated `kfifo_in()` grows length, `put/get` preserves FIFO order, `in/out` bulk operations copy expected buffers, `DECLARE_KFIFO` plus `INIT_KFIFO` matches `DEFINE_KFIFO`, pointer FIFOs transition from uninitialized to initialized after allocation, and `peek` returns the front element without consuming it.

## State and persistence
FIFO buffers are local to each test except pointer-backed allocation, which is freed before return. No global state persists across tests.

## Dependencies and integration points
It depends on `<linux/kfifo.h>` and KUnit. It is selected by `CONFIG_KFIFO_KUNIT_TEST`.

## Risks and edge cases
The test uses small byte FIFOs of size 32 and does not cover wraparound at capacity, overfill behavior, record FIFOs, DMA helpers, or concurrent producers/consumers. One test name contains a spelling typo (`initiliaze`) but it has no behavioral effect.

## Test signals
Failures indicate broken initialization, length accounting, order preservation, allocation, free, or non-consuming peek behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/kfifo_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/kunit_iov_iter.c -->
# sources/distributed-fs/ceph-client/lib/tests/kunit_iov_iter.c

## Purpose
`kunit_iov_iter.c` tests kernel-backed `iov_iter` variants. It validates copying to/from KVEC, BVEC, FOLIOQ, and XARRAY iterators; page extraction from those iterators; and conversion from iterators to scatterlists, including user-buffer extraction.

## Important APIs, types, and functions
The suite uses `struct iov_iter`, `struct kvec`, `struct bio_vec`, `struct folio_queue`, `struct xarray`, `struct sg_table`, `copy_to_iter()`, `copy_from_iter()`, `iov_iter_kvec()`, `iov_iter_bvec()`, `iov_iter_folio_queue()`, `iov_iter_xarray()`, `iov_iter_ubuf()`, `iov_iter_advance()`, `iov_iter_extract_pages()`, `extract_iter_to_sg()`, `sg_copy_to_buffer()`, page allocation, `vmap()`, `kunit_vm_mmap()`, and user `put_user()`.

## Control flow
Helpers allocate non-contiguous page-backed buffers, fill deterministic byte patterns, and construct iterator ranges. KVEC and BVEC tests copy full logical ranges, then build expected images and compare every byte. FOLIOQ and XARRAY copy tests repeatedly reset iterators to subranges before copying. Extraction tests drain iterators in bounded page batches and verify returned page pointers and offsets. Scatterlist tests first validate zero-entry extraction, then partial and full extraction, mark the final sg entry, copy to a scratch buffer, and compare against the pattern.

## State and persistence
All pages, vmaps, folio queues, xarrays, scatterlists, and user mappings are per-test resources. Cleanup uses KUnit actions (`iov_kunit_unmap`, folio queue destruction, xarray destruction, and conditional sg page unpinning). No durable state is produced.

## Dependencies and integration points
It depends on memory management, uio, bvec, folio queue, xarray, scatterlist, min/max, mmap, and KUnit APIs. The Makefile builds it through `CONFIG_TEST_IOV_ITER`.

## Risks and edge cases
Tests allocate and map 1 MiB buffers per case, so they are heavier than simple unit tests. Correctness depends on KUnit cleanup for pages and mappings. User-buffer scatterlist extraction may pin pages, so `iov_iter_extract_will_pin()` controls cleanup registration. The suite covers kernel-backed iterator types only, plus one ubuf scatterlist path.

## Test signals
Byte-for-byte pattern mismatches report the failing offset. Iterator count, segment count, iov offset, page pointer, sg entry count, and extraction length assertions identify structural regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/kunit_iov_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/list-private-test.c -->
# sources/distributed-fs/ceph-client/lib/tests/list-private-test.c

## Purpose
`list-private-test.c` is a compile/smoke KUnit test for private list primitives. It verifies that `list_private_*` helpers can operate on a `struct list_head` member marked private through controlled access.

## Important APIs, types, and functions
The test includes `<linux/list_private.h>`, redefines `__private` as `volatile`, and redefines `ACCESS_PRIVATE()` to recover a non-volatile `struct list_head *` for primitive calls. It covers `list_private_entry()`, first/last/next/prev entry helpers, circular next/prev helpers, `list_private_entry_is_head()`, forward/reverse/continue/from iteration macros, safe iteration macros, and `list_private_safe_reset_next()`.

## Control flow
`list_private_compile_test()` initializes a one-element list, calls each helper or macro enough to force type checking and expansion, and returns early if `list_private_entry_is_head()` evaluates true. The loops have empty bodies except the safe loop, which resets the next pointer.

## State and persistence
Only a local list head, local entry, and iterator pointers are used. No state persists outside the test.

## Dependencies and integration points
It depends on private list macro definitions and KUnit. It is selected by `CONFIG_LIST_PRIVATE_KUNIT_TEST`.

## Risks and edge cases
This is mostly a compilation/type-safety smoke test, not a deep runtime list-behavior test. The redefinition of `__private` and `ACCESS_PRIVATE` is intentionally local to the file; include-order changes could affect the intended diagnostics.

## Test signals
The main signal is successful compilation and KUnit execution without type errors or crashes. Runtime assertions are minimal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/list-private-test.c -->
