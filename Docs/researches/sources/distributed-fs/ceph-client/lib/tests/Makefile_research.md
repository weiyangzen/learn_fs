
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
