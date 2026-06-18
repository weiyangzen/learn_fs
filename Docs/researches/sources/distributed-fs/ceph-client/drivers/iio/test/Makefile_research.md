# sources/distributed-fs/ceph-client/drivers/iio/test/Makefile

Purpose: Builds IIO KUnit test objects according to the corresponding Kconfig symbols.

Important APIs/types/functions: Maps `CONFIG_IIO_RESCALE_KUNIT_TEST`, `CONFIG_IIO_FORMAT_KUNIT_TEST`, `CONFIG_IIO_GTS_KUNIT_TEST`, and `CONFIG_IIO_MULTIPLY_KUNIT_TEST` to `iio-test-*.o`. Adds `$(DISABLE_STRUCTLEAK_PLUGIN)` to `iio-test-format.o`.

Control flow: standard kbuild object selection; no runtime logic.

State and persistence: build-system only.

Dependencies/integration: integrates with Kconfig in the same directory and kbuild/KUnit module or built-in test execution.

Risks: object ordering does not match the "alphabetical" comment. Missing CFLAGS for other tests may matter if compiler plugins interfere with stack buffers, but only format currently opts out.

Test signals: enabling each Kconfig symbol should compile the matching object and register its KUnit suite.
