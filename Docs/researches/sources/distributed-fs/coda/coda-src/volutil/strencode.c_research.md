## sources/distributed-fs/coda/coda-src/volutil/strencode.c

Purpose: `strencode.c` provides YAML double-quoted string escaping for generated ACL metadata in tar output. It returns an allocated encoded copy suitable for insertion between double quotes.

Important APIs/types/functions: helpers `is_ascii_printable`, `yaml_should_escape`, and `hex_nibble` classify bytes and generate hex digits. The exported API is `yaml_encode_double_quoted_string`.

Control flow: the encoder first scans the input string to determine whether escaping is needed and to compute a worst-case output length. If no byte needs escaping, it returns `strdup(string)`. Otherwise it allocates `len + 1`, then emits either the original byte or YAML-style escapes for control characters, quotes, backslash, and other non-printable bytes using `\xXX`.

State and persistence behavior: no global state. The caller owns the returned heap allocation and must `free` it.

Dependencies/integration points: declared in `dump.h` and used by `codadump2tar.cc` when writing `..CodaACLs.yaml`. It depends only on libc and `assert`.

Risks: input is a C string, so embedded NUL bytes terminate encoding even though ACL names/pathnames may theoretically be byte strings elsewhere. `yaml_should_escape` includes only characters that need escaping in double quotes; forward slash handling is present in the switch but disabled in the predicate. `char *c` reads potentially signed `char` values before passing to unsigned helpers, which can matter for bytes above 0x7f.

Test signals: encode plain ASCII, quotes, backslashes, tabs/newlines/carriage returns, ESC, bytes above 0x7f, and empty strings. Verify returned strings parse as YAML double-quoted scalars and memory ownership is clean under ASAN.
