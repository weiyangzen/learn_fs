<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/hardware_cputhreads.c -->
# sources/compression/xz/src/liblzma/common/hardware_cputhreads.c

Purpose: Exposes `lzma_cputhreads()`, a public wrapper returning available CPU thread/core count.

Important APIs: Public `lzma_cputhreads()` calls `tuklib_cpucores()`. On Linux symbol-version builds, compatibility aliases provide `lzma_cputhreads@XZ_5.2.2` and default `lzma_cputhreads@@XZ_5.2`.

Control flow/state: No persistent state. It is a thin visibility and ABI wrapper around the tuklib platform implementation.

Dependencies/integration: Includes `common.h` and `tuklib_cpucores.h`. Used by applications and liblzma helpers to choose default thread counts.

Risks/tests: ABI symbol versioning is the risk on affected Linux builds. Tests should confirm nonzero or documented platform fallback behavior and symbol exports in compatibility builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/hardware_cputhreads.c -->
