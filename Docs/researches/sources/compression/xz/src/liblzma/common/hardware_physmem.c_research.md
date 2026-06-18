<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/hardware_physmem.c -->
# sources/compression/xz/src/liblzma/common/hardware_physmem.c

Purpose: Exposes `lzma_physmem()`, a public wrapper returning total physical memory.

Important API: `lzma_physmem()` calls `tuklib_physmem()` and returns its `uint64_t` result.

Control flow/state: Stateless wrapper. The local comment notes this avoids symbol visibility complications in tuklib modules.

Dependencies/integration: Includes `common.h` and `tuklib_physmem.h`. Used by applications and threaded presets to choose memory limits.

Risks/tests: Platform-specific tuklib behavior is the main uncertainty. Tests should check the API returns a plausible value or documented fallback across supported OSes.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/hardware_physmem.c -->
