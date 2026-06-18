<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_cpucores.h -->
# sources/compression/xz/src/common/tuklib_cpucores.h

Purpose: public tuklib declaration for CPU core detection.

Important APIs/types/functions: `tuklib_cpucores` symbol macro and `extern uint32_t tuklib_cpucores(void)`.

Control flow: declaration-only.

State and persistence: no state.

Dependencies and integration: included by tools/examples that need CPU thread count, with optional symbol prefixing.

Risks: callers must handle zero meaning unknown.

Test signals: compile/link against `tuklib_cpucores.c`; verify prefixed symbol builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_cpucores.h -->
