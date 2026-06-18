# sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/string_kunit.c

Purpose: KUnit suite validating public WMI UTF-16LE string conversion helpers.

Important APIs and types: Static `struct wmi_string` fixtures cover ASCII, special BMP characters, a surrogate-pair string, padded strings, oversized length fields, and invalid surrogate input. Tests call `wmi_string_to_utf8s()` and `wmi_string_from_utf8s()`.

Control flow: Parameterized round-trip tests convert WMI to UTF-8 and UTF-8 to WMI for representative strings. Focused tests ensure padded WMI strings stop at NUL, UTF-8 input with embedded NUL/padding converts to canonical WMI length, oversized WMI length does not over-read intended content, too-long UTF-8 input truncates to available WMI space, invalid UTF-16 is ignored into the expected output, and invalid UTF-8 returns `-EINVAL`.

State and persistence: Test fixtures are static. Output buffers are KUnit stack or KUnit-allocated memory. No state persists after the suite.

Dependencies and integration points: Depends on KUnit, WMI public string helpers, endian macros, and NLS conversion behavior.

Risks: The source uses non-ASCII literals and a surrogate-pair character, so compiler/source encoding must be correct. Tests encode current behavior for invalid UTF-16 being ignored; changing helper semantics to hard-fail would require test updates.

Test signals: Suite name `wmi_string`; failures identify UTF conversion, NUL termination, truncation, length-field, or invalid-input regressions.
