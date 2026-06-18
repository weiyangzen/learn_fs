<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_nonprint.h -->
# sources/compression/xz/src/common/tuklib_mbstr_nonprint.h

Purpose: declarations and contract for non-printable string masking.

Important APIs/types/functions: `tuklib_has_nonprint`, `tuklib_mask_nonprint_r`, and `tuklib_mask_nonprint`.

Control flow: header-only documentation of reentrant memory ownership and single-threaded convenience behavior.

State and persistence: documents that `tuklib_mask_nonprint` has internal static state and `tuklib_mask_nonprint_r` frees/replaces caller memory.

Dependencies and integration: included by CLI display code handling untrusted filenames.

Risks: callers must initialize `*mem` to NULL before first reentrant use and must not use the static convenience function concurrently.

Test signals: API tests should verify errno preservation, ownership behavior, and thread-safety limitations.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_nonprint.h -->
