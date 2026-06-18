# sources/cloud-native/buildkit/source/util/pathutil/pathutil.go

## Purpose
Sanitizes untrusted filename strings for source backends that need to materialize a single file.

## Important APIs, Types, And Functions
- `SafeFileName(s string) string` trims whitespace, converts slash paths to OS paths, takes the base name, rejects empty/dot/dotdot names and names containing NUL or Unicode control characters, and falls back to `"download"`.

## Control Flow
The function applies `filepath.Base(filepath.FromSlash(strings.TrimSpace(s)))`, validates simple unsafe cases, scans runes for NUL/control characters, and returns either the sanitized base or default.

## State And Persistence
No state. Used at file creation time by HTTP source.

## Dependencies And Integration Points
Depends on `filepath`, `strings`, and `unicode`. `http.getFileName` uses it for manual filenames, `Content-Disposition`, URL path basenames, and default fallback.

## Risks And Edge Cases
Backslash path handling is OS-dependent: on Unix, backslashes remain literal; on Windows, `filepath.Base` treats them as separators. It does not reject reserved Windows device names or path names with ordinary separators after basename extraction.

## Test Signals
`pathutil_test.go` covers unicode preservation, whitespace trimming, Unix paths, traversal-ish inputs, control/NUL rejection, and OS-specific Windows backslash behavior.
