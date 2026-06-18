# sources/distributed-fs/ceph-client/include/linux/string_helpers.h

Purpose: declares higher-level string formatting, parsing, escaping, unescaping, case conversion, and quotable duplication helpers used by drivers and core code.

Important APIs and types: `string_is_terminated()` checks bounded NUL termination. `enum string_size_units` selects SI or binary scaling and output modifiers. Public functions include `string_get_size()`, `parse_int_array()`, `parse_int_array_user()`, `string_unescape()`, `string_escape_mem()`, `kstrdup_quotable*()`, `kstrdup_and_replace()`, `kasprintf_strarray()`, `kfree_strarray()`, and `devm_kasprintf_strarray()`. Flag sets define escape and unescape policies such as `ESCAPE_SPACE`, `ESCAPE_NP`, `ESCAPE_HEX`, and `UNESCAPE_OCTAL`.

Control flow: callers select escape/unescape flags, then either write into a caller buffer or duplicate into newly allocated strings. Inline wrappers provide in-place unescape and common "any non-printable" escaping. `string_upper()` and `string_lower()` copy while converting until the source NUL is copied.

State and persistence: no module state is owned here. Allocation helpers return caller-owned or devm-managed arrays/strings.

Dependencies and integration points: depends on ctype, bit helpers, core string APIs, device management, task/file formatting, and user-copy parsing. It is widely used in sysfs/debug formatting and command parsers.

Risks and test signals: risks include output truncation, incorrect escape flag combinations, in-place unescape aliasing mistakes, user buffer faults, and ownership confusion for allocated arrays. Test with string helper selftests, sysfs/debugfs inputs, user-copy fault injection, and KASAN leak detection.
