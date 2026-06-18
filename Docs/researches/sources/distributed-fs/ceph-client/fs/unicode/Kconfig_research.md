# sources/distributed-fs/ceph-client/fs/unicode/Kconfig

This Kconfig fragment exposes build switches for filesystem UTF-8 normalization/casefolding and its KUnit tests.

`config UNICODE` is a tristate option for UTF-8 NFD normalization and NFD+CF casefolding support. The help text notes that, when built as a module, the large casefolding table can be requested only when a filesystem needs it. `config UNICODE_NORMALIZATION_KUNIT_TEST` is a tristate test option that depends on `UNICODE && KUNIT` and defaults to `KUNIT_ALL_TESTS`.

The control flow is build-time only: these symbols decide whether the Unicode runtime/data objects and `tests/utf8_kunit.o` are compiled built-in or as modules. No runtime state or persistent data is defined here. Integration is through the Unicode `Makefile` and filesystem users of exported Unicode helpers. Risks are configuration coverage and module-vs-built-in linkage. Test signals are successful kernel builds for disabled, built-in, and module configurations, plus KUnit execution when `CONFIG_UNICODE_NORMALIZATION_KUNIT_TEST` is enabled.
