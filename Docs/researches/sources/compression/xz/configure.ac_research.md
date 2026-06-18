<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/configure.ac -->
# sources/compression/xz/configure.ac

Purpose: Autoconf input for the XZ Utils build. It establishes package identity/versioning, canonical host detection, configure-time feature switches, generated `config.h` macros, Automake conditionals, Libtool setup, gettext setup, platform probes, and generated makefiles/scripts.

Important APIs/types/functions: the public surface is the generated `configure` options such as `--enable-encoders`, `--enable-decoders`, `--enable-match-finders`, `--enable-checks`, `--enable-threads`, `--enable-sandbox`, `--enable-small`, `--enable-symbol-versions`, and component toggles for `xz`, `xzdec`, `lzmadec`, `lzmainfo`, scripts, docs, and Doxygen. It defines `HAVE_ENCODER_*`, `HAVE_DECODER_*`, `HAVE_CHECK_*`, `MYTHREAD_*`, `HAVE_*CRC*`, `HAVE_LINUX_LANDLOCK`, `ASSUME_RAM`, and symbol-versioning macros.

Control flow: the script first normalizes host/Windows behavior, validates requested filters and checks, enforces LZMA2 requiring LZMA1, validates match-finder availability for LZ encoders, selects threading, components, sandboxing, POSIX shell and compiler, then runs feature probes for headers, typedefs, functions, CRC intrinsics, external SHA-256, Landlock/Capsicum/Pledge, gettext, visibility, warnings, and Libtool symbol versioning before emitting all configured files.

State and persistence: generated state is persisted in `config.h`, makefiles, script substitutions, `AM_CFLAGS`, `LIBS`, `LTLIBINTL`, conditional Automake variables, and substituted executable names. No runtime state is kept by this file.

Dependencies and integration: depends on Autoconf, Automake, Libtool, gnulib macros, gettext macros, `build-aux/version.sh`, tuklib feature macros, platform headers, compiler/linker probes, and downstream makefiles in `lib`, `src`, `tests`, and `debug`.

Risks: invalid option combinations are blocked, but the file is a high-blast-radius integration point: a missed macro affects many C translation units. Symbol versioning has Linux/PIC/static-library caveats. Landlock rejects sanitizer builds. Feature-disabled liblzma builds can break examples/tools expecting filters/checks. The warning flag loop depends on `-Werror` probes being clean.

Test signals: confidence comes from successful `autoreconf`/`configure`, generated `config.h`, `make`, platform CI, and feature-specific builds that exercise disabled filters, threading variants, sandbox choices, and CRC intrinsic paths.
<!-- END_FILE_RESEARCH: sources/compression/xz/configure.ac -->
