# sources/distributed-fs/openafs/src/WINNT/afsd/cm_nls.h

## Purpose
`cm_nls.h` defines the Windows cache manager's naming and string character model. It maps client-visible strings to UTF-16 (`clientchar_t`), file-server strings to UTF-8 (`fschar_t`), and normalized strings to UTF-16 NFC (`normchar_t`). Most cache-manager code uses the abstract macros in this header instead of directly calling `wcs*`, `str*`, or Windows conversion APIs.

## Important APIs, types, and macros
- `cm_unichar_t`, `cm_normchar_t`, `cm_utf8char_t`, `clientchar_t`, `fschar_t`, and `normchar_t` establish the three implementation encodings and the public aliases used by higher layers.
- Literal helpers `_C`, `_FS`, and `_N` produce client, file-server, and normalized literals.
- Conversion aliases such as `cm_ClientStringToFsStringAlloc`, `cm_FsStringToClientString`, and `cm_FsStringToNormStringAlloc` route callers to UTF-16/UTF-8 conversion and normalization functions.
- Client-string operations map to wide-character or custom Unicode-aware helpers: `cm_ClientStrCmp`, `cm_ClientStrCmpI`, `cm_ClientStrCpy`, `cm_ClientStrPrintfV`, `cm_ClientCharNext`, and related macros.
- File-server string operations map to narrow UTF-8 helpers: `cm_FsStrCmp`, `cm_FsStrCmpI`, `cm_FsStrCpy`, and logging helpers.
- Exported functions cover normalization, UTF-8/UTF-16 conversion, case-insensitive compare, UTF-16 navigation, case folding, and UTF-16 validation.

## Control flow and state behavior
The header has no runtime state, but it strongly shapes control flow by forcing all filename conversion through a narrow set of macros. Allocation-returning routines accept source length and optional destination length out-parameters; non-allocating routines accept explicit destination buffer sizes. The SAL annotations document buffer contracts for static analysis and Windows builds.

## Dependencies and integration points
It depends on Windows wide-character conventions, `MultiByteToWideChar` for OEM/ANSI conversion wrappers, `StringCch*` safe string functions, `towupper`, logging helpers such as `osi_LogSaveStringW`, and implementation functions defined elsewhere in the national-language support code. It is included by cache, directory, redirector, and SMB-facing modules that need consistent path handling.

## Risks and edge cases
- The macro layer hides encoding conversions; misuse can silently compare UTF-8 data as UTF-16 or vice versa if a caller picks the wrong alias.
- `_FS(s)` leaves narrow literals unchanged, so source literals must already be UTF-8-compatible.
- Case-insensitive UTF-8 comparisons are custom and should be tested for non-ASCII behavior, not assumed equivalent to locale-specific Windows comparisons.
- `lengthof(a)` only works for arrays, not pointers.

## Test signals
Useful tests include UTF-16 validation failures, surrogate-pair navigation via `char_next_utf16` and `char_prev_utf16`, UTF-8 round trips, NFC normalization equivalence, ASCII and non-ASCII case-insensitive comparisons, OEM/ANSI conversion behavior, and buffer-size failure paths for the non-allocating conversion APIs.
