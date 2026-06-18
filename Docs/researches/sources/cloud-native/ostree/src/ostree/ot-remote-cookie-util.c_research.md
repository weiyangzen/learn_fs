# sources/cloud-native/ostree/src/ostree/ot-remote-cookie-util.c

Purpose: implements cookie jar parsing, add, delete, and list helpers for remote cookie builtins using Netscape cookie text format.

Important APIs/functions: `OtCookieParser` stores the loaded buffer, iteration pointer, current parsed fields, and expiration. `ot_parse_cookies_at()` reads a jar relative to a dirfd, tolerating ENOENT as empty. `ot_parse_cookies_next()` advances line-by-line and parses seven tab-separated fields with `sscanf("%ms...")`. `ot_add_cookie_at()` appends a long-lived cookie. `ot_delete_cookie_at()` rewrites all nonmatching lines to a linkable tmpfile and replaces the jar. `ot_list_cookies_at()` formats parsed cookies with UTC expiration.

Control flow: parse loads full file into memory, then mutates the buffer by replacing newlines with NULs. Add opens append/create and writes one formatted line. Delete parses existing entries, writes all nonmatches to an atomic replacement, records whether a match existed, then errors if none was found. List parses and prints blocks.

State/persistence: cookie jars live as `<remote>.cookies.txt` in the repo directory. Add is append-only. Delete replaces the whole jar. List is read-only. Missing jars parse as empty buffers.

Dependencies/integration: libglnx fd helpers, GLib date/time formatting, private repo access through callers, and `ot-remote-cookie-util.h`.

Risks: `ot_list_cookies_at()` ignores its `dfd` parameter and calls `ot_parse_cookies_at(AT_FDCWD, jar_path, ...)`, which is notable because callers pass the repo dfd; this can list the wrong file unless current working directory is the repo. Parser silently skips malformed lines. Cookie values and names are not escaped, so tabs/newlines would corrupt format. Delete replaces even when not found, potentially normalizing malformed files by dropping unparsable lines.

Test signals: remote cookie tests should catch add/delete/list behavior; a focused test should verify list uses the repository dfd rather than CWD because this implementation appears inconsistent with add/delete.
