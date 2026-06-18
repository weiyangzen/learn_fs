<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_config.h -->
# sources/compression/xz/src/common/tuklib_config.h

Purpose: thin configuration include for tuklib modules.

Important APIs/types/functions: includes `sysdefs.h` when `HAVE_CONFIG_H` is available; otherwise includes standard `stddef.h`, `stdbool.h`, `inttypes.h`, and `limits.h`.

Control flow: preprocessor-only fallback used by standalone tools such as table generators.

State and persistence: compile-time include state only.

Dependencies and integration: sits between tuklib common code and project-specific configuration.

Risks: no-config fallback assumes standard headers exist and lacks Autoconf feature macros, so only limited standalone modules should use it.

Test signals: compile `crc32_tablegen.c` or similar no-config consumers and normal configured builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_config.h -->
