# sources/distributed-fs/ceph-client/drivers/iio/test/Kconfig

Purpose: Kconfig menu entries for IIO unit tests covering gain-time-scale helpers, rescale conversion functions, formatting functions, and multiply helpers.

Important APIs/types/functions: Defines `IIO_GTS_KUNIT_TEST`, `IIO_RESCALE_KUNIT_TEST`, `IIO_FORMAT_KUNIT_TEST`, and `IIO_MULTIPLY_KUNIT_TEST`. Each is tristate, depends on KUnit, defaults to `KUNIT_ALL_TESTS`, and selects or depends on the helper code it tests.

Control flow: no runtime flow; it controls build inclusion. Entries are intended to remain alphabetical, though the current order places RESCALE before FORMAT/MULTIPLY after GTS.

State and persistence: Kconfig selections persist only in kernel build configuration.

Dependencies/integration: integrates with the kernel KUnit framework and the IIO test Makefile. `IIO_GTS_KUNIT_TEST` selects `IIO_GTS_HELPER`; `IIO_RESCALE_KUNIT_TEST` depends on `IIO_RESCALE`.

Risks: dependency mistakes can build tests without the target helper or hide tests from `KUNIT_ALL_TESTS`. Ordering comments are easy to violate when new tests are added.

Test signals: `kunit.py run` or equivalent configs should list the four suites when enabled; all options should build as built-in or module according to tristate selection.
