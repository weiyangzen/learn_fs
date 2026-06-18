# sources/compression/xz/tests/Makefile.am

Purpose: Automake test-suite definition for liblzma, command, generated-file, script, and optional MicroLZMA tests.

Important variables: `EXTRA_DIST` packages fixtures and scripts; `AM_CPPFLAGS` points tests at common and liblzma headers; `LDADD` links liblzma plus optional intl and Windows resources. `check_PROGRAMS` lists C test binaries and `TESTS` defines the executable test order for Automake.

Control flow: all core C tests are built as check programs. Shell tests cover known files, suffixes, generated compression files, and optionally scripts. `test_microlzma` is conditional on `COND_MICROLZMA`; `test_scripts.sh` is conditional on `COND_SCRIPTS`. `clean-local` removes generated compression fixtures and xzgrep temporaries.

State and persistence: test runs create generated files (`compress_generated_*`) and temporary outputs in the tests build directory, then clean selected artifacts.

Dependencies and integration: integrates with configure feature macros, liblzma build artifacts, optional Windows resources, Automake's parallel test harness, and shell scripts that locate built binaries relative to the build tree.

Risks: feature-disabled builds may skip tests or execute only partial assertions, so coverage depends on configure flags. Generated compression files are cached to avoid repeated creation, which is efficient but can hide stale-fixture issues unless cleaned.

Test signals: this file is the top-level signal for which tests are expected in normal `make check`. It explicitly includes the files researched in this subset and shows which behavior has C-level versus shell-level coverage.
