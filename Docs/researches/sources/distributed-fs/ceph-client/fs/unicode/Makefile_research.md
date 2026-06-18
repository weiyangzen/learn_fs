# sources/distributed-fs/ceph-client/fs/unicode/Makefile

The Unicode Makefile builds the UTF-8 normalization runtime, generated data table, optional KUnit tests, and host-side generator.

When `CONFIG_UNICODE` is set, Kbuild includes `unicode.o` and `utf8data.o`; `unicode-y` is composed from `utf8-norm.o` and `utf8-core.o`. `CONFIG_UNICODE_NORMALIZATION_KUNIT_TEST` adds `tests/utf8_kunit.o`. `hostprogs += mkutf8data` builds the host generator. The `utf8data.c` rule either copies `utf8data.c_shipped` for normal builds or, under `REGENERATE_UTF8DATA=1`, invokes `mkutf8data` with UCD inputs (`DerivedAge.txt`, `DerivedCombiningClass.txt`, `DerivedCoreProperties.txt`, `UnicodeData.txt`, `CaseFolding.txt`, `NormalizationCorrections.txt`, `NormalizationTest.txt`) and writes generated C output.

Persistent build output is `$(obj)/utf8data.c`, which defines the table consumed by the runtime and exported as `utf8_data_table`. Dependencies are Kbuild target syntax, host tooling, UCD files for regeneration, and runtime headers. Risks include stale shipped data, missing UCD files, typo/target mismatches, and module ordering. Test signals are clean incremental builds with and without regeneration and KUnit tests against the generated table.
