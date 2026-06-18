# sources/cloud-native/containers-storage/pkg/longpath/longpath.go

Purpose: provides Windows long-path prefix handling.

Important APIs, types, and functions: `Prefix` and `AddPrefix`.

Control flow: `AddPrefix` returns the input unchanged if it already starts with `\\?\`. For UNC paths beginning with `\\`, it converts them to `\\?\UNC\server\share...`; all other paths receive `\\?\` directly.

State and persistence: no state or persistence; it only transforms path strings.

Dependencies and integration points: depends on `strings`. Used by Windows temp directory handling and other filesystem code that must support paths beyond legacy limits.

Risks and edge cases: it is purely syntactic and does not validate absolute paths, drive letters, or malformed UNC strings. Applying it on non-Windows paths would produce Windows-specific strings.

Test signals: `longpath_test.go` validates normal drive-letter and UNC path conversions.
