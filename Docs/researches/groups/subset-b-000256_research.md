# subset-b-000256 research

Grouped research for the listed OSTree CLI, remote, date parser, rofiles-fuse, switchroot, and test files. Each section is bounded by reconciliation markers for deterministic per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-editor.c -->
# sources/cloud-native/ostree/src/ostree/ot-editor.c

Purpose: implements the CLI editor prompt helper used by OSTree commands that need user-edited text. It chooses an editor using `OSTREE_EDITOR`, then `VISUAL`, then `EDITOR`, and falls back to `vi` unless the terminal is dumb and no editor is configured.

Important APIs/functions: `get_editor()` contains the environment-selection policy. `ot_editor_prompt()` creates a temporary file, writes the supplied input, closes the stream, invokes the editor through `/bin/sh -c`, reads UTF-8 content back with `glnx_file_get_contents_utf8_at()`, and deletes the temporary file before returning.

Control flow: editor resolution happens before any file work. The function writes the initial buffer to a `GFileIOStream`, shell-quotes the temp path, launches `GSubprocess` with inherited stdin, waits with `g_subprocess_wait_check()`, prefixes editor failures, reads final file contents, then runs cleanup in the `out:` block.

State/persistence: state is intentionally temporary. The only filesystem persistence is a `g_file_new_tmp()` file that is deleted best-effort on all exit paths. The edited content is returned as allocated memory; repository parameter is currently unused.

Dependencies/integration: depends on GLib/GIO subprocess and stream APIs, libglnx helpers, and `otutil.h`. It integrates with CLI code through `ot-editor.h` and follows git-like editor environment semantics.

Risks: launching through `/bin/sh -c` intentionally supports editor commands with arguments, so correctness relies on shell-quoting only the filename and trusting the editor environment variables. A dumb terminal without editor variables is a hard error. Temp-file deletion failures are ignored.

Test signals: no direct test is in this subset. Coverage would come from commands that call `ot_editor_prompt()` and from manual/editor-invocation tests, especially for env precedence, dumb terminal behavior, and editor failure propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-editor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-editor.h -->
# sources/cloud-native/ostree/src/ostree/ot-editor.h

Purpose: declares the editor prompt interface for OSTree CLI code.

Important APIs/types/functions: includes `<gio/gio.h>` and `ostree.h`, then exports `char *ot_editor_prompt(OstreeRepo *repo, const char *input, GCancellable *cancellable, GError **error)`.

Control flow/state: this header has no executable flow or persistent state. Its contract is transfer-full string ownership on success and GLib-style error reporting on failure.

Dependencies/integration: the signature accepts `OstreeRepo *` for command integration even though the current implementation does not use it. Consumers must link `ot-editor.c`.

Risks: callers must free the returned string and handle `NULL` with `GError`. The unused repo parameter can mislead readers into expecting repository-scoped temp files.

Test signals: compile/link coverage is the main signal; behavioral coverage lives in callers of `ot_editor_prompt()`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-editor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-main.c -->
# sources/cloud-native/ostree/src/ostree/ot-main.c

Purpose: provides the core OSTree command-line runtime: global option handling, command dispatch, external command lookup/exec, repo/sysroot option parsing, admin sysroot loading, colored error output, GPG result printing, and repository writability helpers.

Important APIs/functions: `ostree_main()` sets locale/program name and wraps `ostree_run()`. `ostree_run()` strips the command verb from `argv`, finds an `OstreeCommand`, parses root options for help/error paths, and invokes the command function. `ostree_option_context_parse()` adds `--repo`, command options, and global options, handles `--version`, verbosity, `--`, and repo opening. `ostree_admin_option_context_parse()` adds `--sysroot`, initializes/loads sysroots, supports hidden `--print-current-dir`, and enforces admin flags. `ostree_parse_sysroot_or_repo_option()` supports remote builtins that may target either a sysroot or repo. `parse_repo_option_and_maybe_remount()` remounts `/sysroot` writable in a private namespace when operating on a system repo. `ostree_command_lookup_external()` and `ostree_command_exec_external()` implement extension binary support. `ot_enable_tombstone_commits()` mutates repo config.

Control flow: CLI entry starts at `ostree_main()`, which calls `ostree_run()`. The dispatcher scans arguments, records the first non-option as `command_name`, compacts the remaining `argv`, finds the builtin, and calls its `fn`. Option parsing is layered: command-specific parsers call `ostree_option_context_parse()`, which injects repo/global entries and opens or remounts the repository unless `NO_REPO` is set. Admin parsing further initializes an `OstreeSysroot`, creates a mount namespace/lock unless `UNLOCKED`, then loads deployments unless `NO_LOAD`.

State/persistence: global static option variables hold parsed CLI state for the process. Persistent mutations include repo config writes in `ot_enable_tombstone_commits()` and possible remount of `/sysroot` in a new mount namespace for system repos. `--print-current-dir` prints the first deployment directory and exits.

Dependencies/integration: uses GLib/GIO `GOptionContext`, libglnx, libostree repo/sysroot APIs, `ot-admin-functions.h`, `otutil.h`, Unix `signal`, `unshare`, `mount`, `stat`, and locale support. It is the common integration point for most `ostree` and `ostree admin` builtins.

Risks: static option variables are process-global and assume one parse lifecycle. Argument compaction mutates `argv`, so callers must not depend on the original vector after dispatch. The system-repo remount path is privileged and mount-namespace-sensitive. Extension lookup ignores flags until the first non-option verb and can execute matching `ostree-$verb` from the libexec extension directory or `$PATH`.

Test signals: `tests/admin-test.sh` exercises admin option handling through `--print-current-dir`, sysroot deploy/status/upgrade, and remote add through physical/nonphysical sysroot modes. Remote command tests elsewhere cover `ostree_option_context_parse()` with `--repo`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-main.h -->
# sources/cloud-native/ostree/src/ostree/ot-main.h

Purpose: defines the shared command framework ABI for OSTree CLI builtins and admin builtins.

Important APIs/types/functions: `OstreeBuiltinFlags` controls repo opening/checking and hidden commands. `OstreeAdminBuiltinFlags` controls superuser checks, sysroot locking/loading, and sysroot omission. `OstreeCommand` names a command, flags it, provides its function pointer, and optional description. `OstreeCommandInvocation` currently wraps the selected command for extensibility. The header declares `ostree_main()`, `ostree_run()`, usage, external command lookup/exec, repo/sysroot parsers, admin parsers, `ostree_ensure_repo_writable()`, GPG result printing, and tombstone config enabling.

Control flow/state: this header supplies no implementation but defines how commands receive `argc/argv`, invocation metadata, cancellables, and `GError` propagation.

Dependencies/integration: includes `libglnx.h` and `ostree.h`. Remote, admin, and root builtins include this header directly or via subsystem builtin headers.

Risks: command flags are bitmasks; using the wrong flag can silently skip repo opening, skip repo checks, fail to lock sysroot, or demand unnecessary privileges. The terminal color helpers depend on `glnx_stdout_is_tty()`.

Test signals: broad compile coverage plus CLI integration tests. `admin-test.sh` is a strong signal for admin flags, sysroot loading, and `--print-current-dir`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-add-cookie.c -->
# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-add-cookie.c

Purpose: implements `ostree remote add-cookie`, adding a Netscape-format cookie record for a named remote.

Important APIs/functions: `ot_remote_builtin_add_cookie()` parses no custom options beyond the shared repo options, validates `NAME DOMAIN PATH COOKIE_NAME VALUE`, builds `<remote>.cookies.txt`, and calls `ot_add_cookie_at(ostree_repo_get_dfd(repo), ...)`.

Control flow: parse options and open repo through `ostree_option_context_parse()`, validate five positional arguments, derive the jar filename, append the cookie, and return boolean status.

State/persistence: appends to a cookie jar file under the repository directory fd. The cookie utility writes an expiration about 25 years in the future and creates the jar if missing.

Dependencies/integration: depends on `ostree-repo-private.h` for repo dfd access and `ot-remote-cookie-util.h`. The builtin is only declared when HTTP support is compiled.

Risks: remote names become filenames with a `.cookies.txt` suffix, so correctness depends on remote-name validation elsewhere. Cookie values are printed/stored verbatim by utility code and are not escaped.

Test signals: likely covered by remote cookie tests outside this exact subset, such as `tests/test-remote-cookies.sh`; this file has no local unit test section here.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-add-cookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-add.c -->
# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-add.c

Purpose: implements `ostree remote add`, creating or replacing a remote configuration, optional branch restrictions, verification settings, content URL/custom backend settings, collection ID, and optional GPG import.

Important APIs/functions: `add_verify_opt()` parses `KEYTYPE=inline:DATA` or `KEYTYPE=file:/path` sign verification specs and adds `verification-<keytype>-key/file` variants. `ot_remote_builtin_add()` parses options, opens repo or sysroot via `ostree_parse_sysroot_or_repo_option()`, validates positional args, builds an `a{sv}` option variant, chooses `OstreeRepoRemoteChange`, calls `ostree_repo_remote_change()`, and optionally imports all GPG keys from `--gpg-import`.

Control flow: option parsing precedes sysroot/repo resolution. Custom backend mode permits `NAME` without URL; normal mode requires `NAME URL`. Branch arguments after URL become a `branches` string array. `--set` key/value options are parsed generically and inserted into the variant. GPG and sign verification flags are reconciled before remote change. GPG import is a post-create convenience path.

State/persistence: mutates repository remote configuration, either in repo config or sysroot remote config locations depending on libostree policy. Optional GPG import writes remote keyring data. No local state survives except static parsed option variables for the process.

Dependencies/integration: depends on `ot-main` repo/sysroot parsing, libostree remote APIs, signature plugin lookup via `ostree_sign_get_by_name()`, GVariant option passing, and optional GPGME code.

Risks: `--if-not-exists` with `--gpg-import` imports regardless of whether the remote already existed. `--no-sign-verify` conflicts with `--sign-verify`, but `--no-gpg-verify` also disables GPG verification when compiled with GPGME. Option names in `--set` pass through to config and need library-side validation.

Test signals: `tests/admin-test.sh` exercises remote add on a physical sysroot, nonphysical sysroot, and `core.add-remotes-config-dir=false`; it verifies whether remote config lands in repo config or deployment `/etc/ostree/remotes.d`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-add.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-delete-cookie.c -->
# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-delete-cookie.c

Purpose: implements `ostree remote delete-cookie`, removing a named cookie from a remote cookie jar.

Important APIs/functions: `ot_remote_builtin_delete_cookie()` validates `NAME DOMAIN PATH COOKIE_NAME`, derives `<remote>.cookies.txt`, and calls `ot_delete_cookie_at()` against the repository dfd.

Control flow: parse/open repo, validate four positional arguments, derive jar path, rewrite the cookie jar without matching records, and propagate any utility error.

State/persistence: rewrites the cookie jar atomically using the utility's temporary file/link replacement path. It reports an error if no matching cookie was found.

Dependencies/integration: depends on private repo dfd access and `ot-remote-cookie-util.c`.

Risks: deleting from a missing jar creates/replaces an empty jar through the utility path and then returns "Cookie not found in jar". Matching is exact on domain, path, and name only.

Test signals: expected coverage is the remote cookie integration test suite, not included in this item.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-delete-cookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-delete.c -->
# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-delete.c

Purpose: implements `ostree remote delete`, removing a remote configuration.

Important APIs/functions: `ot_remote_builtin_delete()` parses `--if-exists`, `--repo`, and `--sysroot`, opens the target through `ostree_parse_sysroot_or_repo_option()`, validates `NAME`, and calls `ostree_repo_remote_change()` with delete or delete-if-exists operation.

Control flow: parse options, resolve repo/sysroot, validate one positional remote name, invoke remote-change API, return success/failure.

State/persistence: mutates remote configuration in the selected repository/sysroot. `--if-exists` suppresses missing-remote errors through the libostree change operation.

Dependencies/integration: uses the same special sysroot-or-repo path as remote add, so it participates in deployment-local versus physical repo config behavior.

Risks: wrong target selection via `--sysroot` versus `--repo` deletes from a different config scope. There is no confirmation prompt.

Test signals: remote delete behavior is likely covered in remote/config tests outside this subset; `admin-test.sh` indirectly validates remote config scoping via add.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-delete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-gpg-import.c -->
# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-gpg-import.c

Purpose: implements `ostree remote gpg-import`, importing GPG keys into a remote keyring from stdin or one or more keyring files.

Important APIs/functions: `open_source_stream()` returns a `GInputStream` from stdin or a chained stream of all `--keyring` files using `OstreeChainInputStream`. `ot_remote_builtin_gpg_import()` validates `NAME`, disallows `--stdin` with `--keyring`, passes optional key IDs, calls `ostree_repo_remote_gpg_import()`, and prints an imported count.

Control flow: parse repo options, validate remote name and mutually exclusive source options, create source stream, import selected or all keys, print result.

State/persistence: writes remote GPG keyring state in the repository. It does not persist source streams or local temp files.

Dependencies/integration: uses `gio/gunixinputstream.h`, libglnx, `ostree-chain-input-stream.h`, and libostree remote GPG import APIs.

Risks: with no `--stdin` and no keyrings, the chained stream is built from an empty array; library behavior determines whether that means no keys or an error. Stdin is not closed by the stream. Errors can occur late while reading chained keyrings.

Test signals: GPG import is typically covered by remote GPG tests. This subset includes `admin-test.sh` remote operations but not explicit GPG import checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-gpg-import.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-gpg-list-keys.c -->
# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-gpg-list-keys.c

Purpose: implements `ostree remote list-gpg-keys`, dumping configured GPG keys for one remote or all remotes.

Important APIs/functions: `ot_remote_builtin_list_gpg_keys()` opens the repo, treats `argv[1]` as optional remote name, calls `ostree_repo_remote_get_gpg_keys()`, and prints each key with `ot_dump_gpg_key()`.

Control flow: parse/open repo, fetch keys into `GPtrArray`, iterate and dump, stopping on any dump error.

State/persistence: read-only; it inspects remote keyring data and writes text to stdout.

Dependencies/integration: uses `ot-dump.h` formatting helpers and libostree remote key APIs.

Risks: output format is owned by `ot_dump_gpg_key()` and may be consumed by scripts. Large keyrings produce unbounded stdout.

Test signals: likely covered by `tests/test-remote-gpg-list-keys.sh` in the broader tree; not one of this item’s final source files.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-gpg-list-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-list-cookies.c -->
# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-list-cookies.c

Purpose: implements `ostree remote list-cookies`, displaying all cookies in a named remote jar.

Important APIs/functions: `ot_remote_builtin_list_cookies()` validates `NAME`, derives `<remote>.cookies.txt`, and calls `ot_list_cookies_at()`.

Control flow: parse/open repo, validate remote name, parse the cookie jar, print each parsed cookie block.

State/persistence: read-only; it reads `<remote>.cookies.txt` from the repo and writes cookie values to stdout.

Dependencies/integration: uses private repo dfd access and `ot-remote-cookie-util`.

Risks: cookie values are printed in cleartext. Missing or malformed lines are silently skipped by the parser, so list output may hide corrupt entries.

Test signals: expected integration coverage is `tests/test-remote-cookies.sh`; not directly included here.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-list-cookies.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-list.c -->
# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-list.c

Purpose: implements `ostree remote list`, optionally with URLs.

Important APIs/functions: `ot_remote_builtin_list()` opens a repo, obtains `ostree_repo_remote_list()`, and either prints one name per line or aligns names with URLs from `ostree_repo_remote_get_url()` when `--show-urls/-u` is set.

Control flow: parse options, retrieve remotes and count, compute max name length for URL mode, print each row.

State/persistence: read-only inspection of repo remote config.

Dependencies/integration: depends on libostree remote listing/get-url APIs and shared option parsing.

Risks: URL lookup failure for any remote aborts the full listing. Aligned output is human-oriented and script consumers should prefer simpler name-only output.

Test signals: `tests/admin-test.sh` runs `ostree --repo=sysroot/ostree/repo remote list -u` and verifies a changed origin remote URL appears.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-refs.c -->
# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-refs.c

Purpose: implements `ostree remote refs`, listing refs advertised by a remote, with optional revisions.

Important APIs/functions: `ot_remote_builtin_refs()` parses `--revision/-r` and `--cache-dir`, optionally calls `ostree_repo_set_cache_dir()`, fetches refs via `ostree_repo_remote_list_refs()`, sorts keys, and prints `remote:ref` or `remote:ref<TAB>rev`.

Control flow: parse/open repo, validate remote name, set cache dir if requested, fetch refs into a hash table, sort ref names with `strcmp`, print.

State/persistence: read-only with respect to repository config, but remote fetch/listing may populate or read network cache under the configured cache directory.

Dependencies/integration: libostree remote ref listing and cache directory API; GLib `GHashTable`/`GList`.

Risks: network/cache failures surface through libostree. Sorting only keys means duplicate names are impossible by hash table contract. `--revision` output format includes a tab and may be parsed by scripts.

Test signals: broader tree contains remote refs tests; not directly in this subset. Pull/admin tests indirectly rely on remote refs being resolvable.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-refs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-show-url.c -->
# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-show-url.c

Purpose: implements `ostree remote show-url`, printing a remote's configured URL.

Important APIs/functions: `ot_remote_builtin_show_url()` opens a repo, validates `NAME`, calls `ostree_repo_remote_get_url()`, and prints the URL.

Control flow: parse/open repo, validate one argument, resolve URL, print line.

State/persistence: read-only.

Dependencies/integration: shared option parsing and libostree remote URL lookup.

Risks: errors if the remote lacks a URL, has only custom backend semantics, or is missing. Output is raw URL, suitable for scripts but may include credentials if configured.

Test signals: remote add/list tests indirectly verify URLs; direct show-url coverage likely exists outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-show-url.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-summary.c -->
# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-summary.c

Purpose: implements `ostree remote summary`, fetching and dumping a remote summary file, selected metadata, or raw variant data, with optional signature display.

Important APIs/functions: `ot_remote_builtin_summary()` parses `--list-metadata-keys`, `--print-metadata-key`, `--cache-dir`, and `--raw`. It sets an optional cache dir, calls `ostree_repo_remote_fetch_summary()`, dumps metadata via `ot-dump` helpers, and when GPGME is enabled verifies/prints summary signatures with `ostree_repo_verify_summary()` and `ostree_print_gpg_verify_result()`.

Control flow: parse/open repo, validate remote name, configure cache, fetch summary/signature bytes, error if no summary exists, choose one of metadata-key listing, single metadata value, or full summary dump, then optionally print GPG signature details for non-raw output.

State/persistence: read-only from repo config; may use remote network/cache state. No repository config mutation.

Dependencies/integration: `ot-dump.h`, libostree remote summary fetch/verify APIs, optional GPGME support, GLib bytes/variant handling.

Risks: raw mode suppresses signature display. Summary verification happens during fetch; later signature parsing is for display. Missing summary is a command error. Cache-dir selection can affect test reproducibility.

Test signals: broader tests include summary update/view/pull summary scripts. This subset’s admin tests rely on summary/remote flows indirectly through pull/upgrade.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtin-summary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtins.h -->
# sources/cloud-native/ostree/src/ostree/ot-remote-builtins.h

Purpose: declares all `ostree remote` subcommand entry points.

Important APIs/types/functions: includes `ot-main.h`, wraps declarations in `G_BEGIN_DECLS`/`G_END_DECLS`, and uses `BUILTINPROTO(name)` to declare the standard builtin signature for add, delete, GPG, list, show-url, refs, summary, and HTTP-cookie commands.

Control flow/state: no runtime flow or persistent state. Conditional declarations for cookie commands depend on `HAVE_LIBCURL_OR_LIBSOUP`.

Dependencies/integration: consumed by `ot-builtin-remote.c` and each remote subcommand implementation. It standardizes signatures so they can be placed in `OstreeCommand` tables.

Risks: conditional prototypes must match build-system conditional sources; mismatch can cause compile/link failures. Command names such as `list_gpg_keys` map to hyphenated CLI names in the command table elsewhere.

Test signals: compile coverage plus all remote command integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-builtins.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-cookie-util.c -->
# sources/cloud-native/ostree/src/ostree/ot-remote-cookie-util.c

Purpose: implements cookie jar parsing, add, delete, and list helpers for remote cookie builtins using Netscape cookie text format.

Important APIs/functions: `OtCookieParser` stores the loaded buffer, iteration pointer, current parsed fields, and expiration. `ot_parse_cookies_at()` reads a jar relative to a dirfd, tolerating ENOENT as empty. `ot_parse_cookies_next()` advances line-by-line and parses seven tab-separated fields with `sscanf("%ms...")`. `ot_add_cookie_at()` appends a long-lived cookie. `ot_delete_cookie_at()` rewrites all nonmatching lines to a linkable tmpfile and replaces the jar. `ot_list_cookies_at()` formats parsed cookies with UTC expiration.

Control flow: parse loads full file into memory, then mutates the buffer by replacing newlines with NULs. Add opens append/create and writes one formatted line. Delete parses existing entries, writes all nonmatches to an atomic replacement, records whether a match existed, then errors if none was found. List parses and prints blocks.

State/persistence: cookie jars live as `<remote>.cookies.txt` in the repo directory. Add is append-only. Delete replaces the whole jar. List is read-only. Missing jars parse as empty buffers.

Dependencies/integration: libglnx fd helpers, GLib date/time formatting, private repo access through callers, and `ot-remote-cookie-util.h`.

Risks: `ot_list_cookies_at()` ignores its `dfd` parameter and calls `ot_parse_cookies_at(AT_FDCWD, jar_path, ...)`, which is notable because callers pass the repo dfd; this can list the wrong file unless current working directory is the repo. Parser silently skips malformed lines. Cookie values and names are not escaped, so tabs/newlines would corrupt format. Delete replaces even when not found, potentially normalizing malformed files by dropping unparsable lines.

Test signals: remote cookie tests should catch add/delete/list behavior; a focused test should verify list uses the repository dfd rather than CWD because this implementation appears inconsistent with add/delete.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-cookie-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-cookie-util.h -->
# sources/cloud-native/ostree/src/ostree/ot-remote-cookie-util.h

Purpose: declares cookie jar helper functions for remote cookie subcommands.

Important APIs/functions: `ot_add_cookie_at()`, `ot_delete_cookie_at()`, and `ot_list_cookies_at()` all take a directory fd, jar path, and `GError **`; add/delete also take cookie identity/value fields.

Control flow/state: no implementation. The API implies operations relative to `dfd`.

Dependencies/integration: includes `libglnx.h` for GLib/error/fd conventions and is consumed by cookie builtins.

Risks: callers expect all helpers to honor `dfd`; implementation review shows list currently does not, so the header contract is stronger than actual behavior.

Test signals: compile coverage and remote cookie integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-remote-cookie-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/parse-datetime.h -->
# sources/cloud-native/ostree/src/ostree/parse-datetime.h

Purpose: exposes a GNU-style natural language date/time parser used by OSTree timestamp-related CLI paths.

Important APIs/functions: declares `bool parse_datetime(struct timespec *result, char const *input, struct timespec const *now)`.

Control flow/state: no implementation. `now` may be `NULL`, in which case the implementation reads current realtime. The result is a `timespec` with nanosecond precision.

Dependencies/integration: includes `<stdbool.h>` and `<time.h>`. Consumers must compile/link the Bison-generated parser from `parse-datetime.y`.

Risks: the parser accepts broad human syntax, relative expressions, time zones, and `TZ="..."` prefixes, so callers need to decide whether ambiguous input is acceptable.

Test signals: timestamp CLI and RFC/date tests in the broader tree are the likely coverage points.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/parse-datetime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/parse-datetime.y -->
# sources/cloud-native/ostree/src/ostree/parse-datetime.y

Purpose: Bison grammar and lexer for parsing absolute, relative, ISO-8601, timezone, and epoch-style date/time strings into `struct timespec`.

Important APIs/functions: parser-visible state lives in `parser_control`. Grammar rules parse `@seconds`, dates, times, local zones, named zones, days, relative units, and hybrid numeric+relative forms. Lexer `yylex()` tokenizes signed/unsigned integers, decimal seconds, words, comments, punctuation, and timezone/month/unit tables. Helpers include `digits_to_date_time()`, `apply_relative_time()`, `set_hhmmss()`, `time_zone_hhmm()`, `to_hour()`, `to_year()`, `lookup_word()`, `mktime_ok()`, `get_tz()`, and exported `parse_datetime()`.

Control flow: `parse_datetime()` establishes `now`, initializes parser defaults from localtime, optionally parses and installs a `TZ="..."` prefix, fills local timezone abbreviation tables, calls `yyparse()`, then either returns an explicit `@` timespec or converts parsed calendar fields through `mktime()`. It adjusts requested weekdays, applies relative year/month/day via `mktime()`, applies numeric timezone deltas, then applies relative hour/min/sec/ns arithmetic with overflow checks. It restores the original `TZ` before returning.

State/persistence: most state is stack-local in `parser_control`. The major process-global side effect is temporary mutation of the `TZ` environment when parsing `TZ="..."` or retrying boundary timezone conversions; it is restored on exit if possible. It reads current realtime through `clock_gettime()` or `gettimeofday()` when `now` is absent.

Dependencies/integration: generated by Bison with a pure parser, but uses non-reentrant C library calls such as `localtime()`, `gmtime()`, `mktime()`, `setenv()`, and `unsetenv()`. Depends on GLib allocation and config feature macros.

Risks: comments note arithmetic overflow is not exhaustively checked. Timezone abbreviations are inherently ambiguous. The `TZ` environment mutation is process-global and can be risky in multithreaded contexts. Grammar intentionally has 31 shift/reduce conflicts. Natural-language parsing can accept surprising input.

Test signals: broader tests such as RFC2616 date parsing and commit timestamp scripts should exercise this parser. Focused tests should include ISO-8601 with offsets, relative expressions, epoch `@` values, DST boundaries, invalid overflow, and `TZ="..."` restoration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/parse-datetime.y -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/rofiles-fuse/Makefile-inc.am -->
# sources/cloud-native/ostree/src/rofiles-fuse/Makefile-inc.am

Purpose: automake fragment building the `rofiles-fuse` helper binary.

Important build entries: adds `rofiles-fuse` to `bin_PROGRAMS`, sets `rofiles_fuse_SOURCES` to `src/rofiles-fuse/main.c`, supplies `_GNU_SOURCE`, `_FILE_OFFSET_BITS=64`, FUSE, internal GIO Unix, libostree, and libglnx include flags, and links `libglnx.la`, FUSE libs, GIO Unix libs, and `libostree-1.la`.

Control flow/state: build metadata only; no runtime flow.

Dependencies/integration: ties `main.c` to configured FUSE version and libostree internals. The include paths allow use of private libostree headers.

Risks: build correctness depends on `BUILDOPT_FUSE_CFLAGS/LIBS` and `FUSE_USE_VERSION` being defined through `config.h`. Linkage against libostree means the helper must track ABI/build changes.

Test signals: build/test jobs compiling `rofiles-fuse`; runtime behavior needs FUSE-capable integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/rofiles-fuse/Makefile-inc.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/rofiles-fuse/main.c -->
# sources/cloud-native/ostree/src/rofiles-fuse/main.c

Purpose: implements `rofiles-fuse`, a FUSE filesystem that exposes a base directory with writable directories but protects OSTree hardlinked regular files/symlinks from mutation unless `--copyup` is enabled.

Important APIs/functions: FUSE callbacks cover getattr, readlink, readdir, mkdir/unlink/rmdir/symlink/rename/link, chmod/chown/truncate/utimens, create/open, read/write buffer paths, statfs, release/fsync/access, and xattrs. `ENSURE_RELPATH()` normalizes absolute FUSE paths. `can_write_stbuf()` rejects writes to hardlinked regular files/symlinks and fsverity files. `verify_write_or_copyup()` enforces that rule or invokes `copyup()`. `copyup()` uses `glnx_file_copy_at()` for regular files and `ostree_break_hardlink()` for symlinks. `rofs_parse_opt()` parses basepath and `--copyup`; `main()` calls `fuse_main()`.

Control flow: startup parses FUSE options and opens the first non-option as `basefd`. Read-only operations directly proxy to `*at` syscalls under `basefd`. Mutating operations normalize path then run `verify_write_or_copyup()` when they can alter file contents/metadata. Open/create distinguishes read-only from write access. The callback table supplies the operations to FUSE.

State/persistence: global `basefd` points to the exposed tree. With default mode, writes to hardlinked content fail with `EROFS`; directory changes and non-hardlinked file mutations persist in the base tree. With `--copyup`, protected hardlinks are broken before mutation, persistently creating independent file/symlink objects.

Dependencies/integration: depends on libfuse version conditionals, Linux `statx`, `renameat2`, xattr syscalls, libglnx copy helpers, and libostree hardlink-breaking. It is built by the sibling automake fragment.

Risks: global `basefd`/`opt_copyup` assume one mounted filesystem per process. `renameat2` assumes Linux 3.15+. Xattr operations build `/proc/self/fd/%d/%s` paths and need procfs. `access(W_OK)` intentionally lies by delegating to underlying access, so callers may still receive later `EROFS`. `can_write_stbuf()` depends on link count and fsverity attributes being accurate from `statx`.

Test signals: no file in this subset directly tests rofiles-fuse. Meaningful tests should mount FUSE, verify hardlinked file writes fail, `--copyup` breaks hardlinks, directory mutations persist, xattrs work, and fsverity files stay immutable.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/rofiles-fuse/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/switchroot/ostree-mount-util.h -->
# sources/cloud-native/ostree/src/switchroot/ostree-mount-util.h

Purpose: shared small C utility header for switchroot/remount binaries that must run early in boot with minimal dependencies.

Important APIs/macros: defines `INITRAMFS_MOUNT_VAR`, `_OSTREE_SYSROOT_READONLY_STAMP`, `_OSTREE_COMPOSEFS_ROOT_STAMP`, and an `autofree` cleanup attribute. `path_is_on_readonly_fs()` checks `statvfs()` for `ST_RDONLY`. `read_proc_cmdline()` reads `/proc/cmdline`. `find_proc_cmdline_key()` extracts `key=value` tokens. `touch_run_ostree()` creates `/run/ostree-booted` best-effort.

Control flow: helpers either return allocated strings/bools or terminate through `err()` on critical filesystem query failure.

State/persistence: `touch_run_ostree()` creates a stamp file; other helpers are read-only. `read_proc_cmdline()` allocates caller-owned memory.

Dependencies/integration: used by prepare-root static/nonstatic and remount code. It deliberately uses libc/POSIX APIs suitable for initramfs/static contexts.

Risks: `read_proc_cmdline()` assumes nonempty content before checking `cmdline[len - 1]`. `find_proc_cmdline_key()` does simple space tokenization and does not handle quoting. `path_is_on_readonly_fs()` exits process on stat failure.

Test signals: `tests-unit-container/test-prepare-root.sh` indirectly exercises cmdline reading and read-only filesystem detection through `ostree-prepare-root`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/switchroot/ostree-mount-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/switchroot/ostree-prepare-root-static.c -->
# sources/cloud-native/ostree/src/switchroot/ostree-prepare-root-static.c

Purpose: static, pid-1 variant of prepare-root for systems without an initramfs. It resolves the OSTree deployment from the kernel command line, constructs the deployment root, pivots or moves mounts, prepares `/boot`, `/etc`, `/usr`, `/var`, and execs `/sbin/init`.

Important APIs/functions: `sysroot_is_configured_ro()` manually scans `ostree/repo/config` for `[sysroot] readonly=true` without GLib. `resolve_deploy_path()` reads `ostree=` from `/proc/cmdline`, validates it is a symlink, resolves it, and optionally logs to systemd journal. `pivot_root()` wraps the syscall. `main()` asserts pid 1 and performs the mount choreography.

Control flow: ensure `/proc/cmdline` is readable, mounting proc temporarily if needed; resolve `/` and deployment path; inspect readonly config; make mounts private; create `/sysroot.tmp`; bind the deployment there; optionally stamp read-only sysroot; bind `/boot` if needed; make `/etc` writable for readonly sysroot; mount `/usr` overlay or read-only bind; prepare `/var`; pivot to deployment or move mounts; make `/sysroot` private; exec init.

State/persistence: mutates the live mount namespace, may create `_OSTREE_SYSROOT_READONLY_STAMP`, bind/overlay mounts directories, and changes process cwd/root. It does not write `/run/ostree-booted` metadata like the nonstatic path.

Dependencies/integration: minimal libc/syscall implementation plus optional systemd journal. Shares macros/helpers from `ostree-mount-util.h`.

Risks: asserts pid 1, so it aborts outside the intended boot mode. Manual config parsing is fragile. Missing `ostree=` is not explicitly checked before path formatting. Mount ordering errors can leave an unusable boot. Static path lacks newer composefs/transient-root logic from `ostree-prepare-root.c`.

Test signals: `tests-unit-container/test-prepare-root.sh` targets the nonstatic initramfs path, not this static path. Static behavior needs boot/integration tests on embedded/no-initramfs systems.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/switchroot/ostree-prepare-root-static.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/switchroot/ostree-prepare-root.c -->
# sources/cloud-native/ostree/src/switchroot/ostree-prepare-root.c

Purpose: initramfs/systemd prepare-root implementation. It turns the physical root mounted at a sysroot path into an OSTree deployment root, supports composefs/transient root configuration, prepares `/etc`, `/usr`, `/sysroot`, and `/var`, writes boot metadata, and leaves systemd to switch root.

Important APIs/functions: `sysroot_is_configured_ro()` reads repo config with `GKeyFile`. `resolve_deploy_path()` uses `otcore_get_ostree_target()` to parse the kernel command line, validates the target symlink, resolves the deployment, and journals deployment device/inode/path. `main()` parses `SYSROOT [KERNEL_CMDLINE]`, loads `prepare-root.conf`, loads `RootConfig`, mounts composefs or legacy bind root via `otcore_mount_rootfs()`, mounts transient/persistent `/etc` via `otcore_mount_etc()`, handles `/usr` hotfix overlay, binds physical root to future `/sysroot`, detaches old sysroot, prepares `/var`, writes `OTCORE_RUN_BOOTED` metadata, moves `/sysroot.tmp` to target, and optionally remounts `/sysroot` read-only.

Control flow: after config and target resolution, all later operations assume cwd is the deployment directory. Composefs is attempted first; legacy bind mount is fallback. Metadata is accumulated in a `GVariantBuilder` and written to `/run/ostree-booted` before final move. `/boot` is intentionally not mounted here; generator handles it.

State/persistence: heavily mutates mount namespace and writes `/run/ostree` directories plus `OTCORE_RUN_BOOTED` metadata. It may leave `/sysroot` read-only by configuration and ensures `/var` and `/etc` mutability through bind/overlay mounts.

Dependencies/integration: GLib/GIO option/keyfile/variant APIs, libglnx, libostree core/private APIs, `otcore` rootfs helpers, systemd journal IDs, Linux mount/umount semantics, and `ostree-mount-util.h`.

Risks: this is boot-critical code with many privileged mount operations. Composefs, transient root, readonly sysroot, and hotfix overlays interact; signed composefs forbids `/usr` hotfix overlay. It relies on symlink deployment targets and correct kernel cmdline/config. Errors exit the process, which fails boot preparation.

Test signals: `tests-unit-container/test-prepare-root.sh` directly exercises legacy prepare-root in a podman container, verifies `/run/ostree-booted`, `/etc` and `/usr` mountpoints, default readonly sysroot config, default config fallback, `etc.transient`, and that `/boot` is not mounted by prepare-root.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/switchroot/ostree-prepare-root.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/switchroot/ostree-remount.c -->
# sources/cloud-native/ostree/src/switchroot/ostree-remount.c

Purpose: post-switchroot remount helper that restores intended writability for `/sysroot`, `/etc`, and `/var`, and relabels transient `/etc` overlay contents for SELinux.

Important APIs/functions: `do_remount()` checks target existence, skips symlinks/nonmounts, compares current `ST_RDONLY` state, and remounts rw/ro. `relabel_dir_for_upper()` recursively restorecons overlay upperdir entries when SELinux is enabled. `main()` reads `OTCORE_RUN_BOOTED` metadata, handles legacy stamp fallback, relabels transient `/etc`, detects composefs, and remounts selected paths.

Control flow: read `/run/ostree-booted` variant dict if present; if transient `/etc` metadata exists, optionally unshare mount namespace to expose the real `/etc/machine-id`, relabel upperdir-backed files, then restore namespace. If `/` is read-only and not composefs, exit without remounts. Otherwise remount `/sysroot` according to readonly metadata, `/etc` writable when it is a bind mount, and `/var` writable.

State/persistence: mutates mount flags and, under SELinux, filesystem labels. It may create `/run/ostree-booted` as an empty compatibility stamp if missing.

Dependencies/integration: depends on `ostree-mount-util.h`, `otcore.h` metadata keys, libglnx variant/dir iterators, mount namespace syscalls, and optional SELinux restorecon.

Risks: relabeling recursively mirrors upperdir paths into `/etc`; races with systemd-sysusers are partly tolerated for ENOENT. Namespace unshare/setns failures are fatal. Incorrect metadata can leave `/sysroot` writable or read-only contrary to policy.

Test signals: prepare-root container tests validate metadata creation and mount state before remount; full boot/admin tests are needed to exercise `ostree-remount` behavior and SELinux relabeling.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/switchroot/ostree-remount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/switchroot/ostree-system-generator.c -->
# sources/cloud-native/ostree/src/switchroot/ostree-system-generator.c

Purpose: small systemd generator frontend that delegates actual unit generation to libostree private command code.

Important APIs/functions: `main()` accepts either no arguments or the three systemd generator directories, assigns `arg_dest` and `arg_dest_late`, then calls `ostree_cmd__private__()->ostree_system_generator(arg_dest, NULL, arg_dest_late, &error)`.

Control flow: validate argc, map generator args, invoke private implementation, print fatal error on failure, exit success otherwise.

State/persistence: this frontend itself writes no files directly, but the private generator writes systemd units into the generator output directories.

Dependencies/integration: depends on `ostree-cmd-private.h`, libglnx/GError handling, and the systemd generator calling convention. It is tied to `/boot` and `/var` mount behavior moved out of prepare-root.

Risks: argument validation is strict: any argc other than 1 or 4 fails. Actual generator behavior is hidden in libostree private API, so frontend tests only validate delegation.

Test signals: `tests-unit-container/test-prepare-root.sh` asserts prepare-root does not mount `/boot`, explicitly pointing to generator responsibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/switchroot/ostree-system-generator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/switchroot/switchroot.sh -->
# sources/cloud-native/ostree/src/switchroot/switchroot.sh

Purpose: demonstration shell implementation of the historical OSTree switchroot mount sequence.

Important operations: inspects environment for `ostree`, bind-mounts the deployment, bind-remounts `/usr` read-only, binds physical root into deployment `/sysroot`, binds stateroot `/var`, creates default var subdirectories, and moves the deployment mount to `$sysroot`.

Control flow: linear shell commands with no error handling flags. It documents the conceptual flow implemented more robustly in C.

State/persistence: mutates mount namespace and creates directories under deployment `/var`.

Dependencies/integration: uses shell, `mount`, `grep`, `mkdir`, and environment variables `$sysroot` and `$ostree`. It is documentation/example-like rather than production path.

Risks: typo in comments, no validation, no quoting, no cleanup, and hardcoded `ostree/deploy/os/var`. It should not be treated as the authoritative implementation.

Test signals: no direct tests. It serves as a readable reference for prepare-root behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/switchroot/switchroot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests-unit-container/run.sh -->
# sources/cloud-native/ostree/tests-unit-container/run.sh

Purpose: simple container unit-test runner for scripts named `test-*` in the same directory.

Important APIs/functions: shell loop over `${dn}/test-*`, executes each case, prints "Running" and "ok" lines, counts cases, and exits 0 under `set -euo pipefail`.

Control flow: any failing test aborts the runner due to `set -e`. Successful tests increment `n` and final output reports the count.

State/persistence: no persistent state beyond whatever individual tests create.

Dependencies/integration: bash and executable test scripts in `tests-unit-container`. It is intended for the `privunit`/podman workflow mentioned by test comments.

Risks: glob order is shell/filesystem sorted and includes any executable or non-executable matching `test-*`; if a matching file is not executable, the runner fails. No TAP plan is emitted.

Test signals: this is itself a test harness; its output gives count and per-case pass markers.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests-unit-container/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests-unit-container/test-prepare-root.sh -->
# sources/cloud-native/ostree/tests-unit-container/test-prepare-root.sh

Purpose: privileged container test for `ostree-prepare-root`, treating a podman container as an initramfs.

Important operations: asserts `TEST_CONTAINER=1`, defines cleanup for `/target-sysroot` and `/sysroot.tmp`, creates a bind-mounted target sysroot, initializes OSTree admin fs/stateroot, fakes a deployment, binds a temporary `/proc/cmdline`, runs `/usr/lib/ostree/ostree-prepare-root /target-sysroot`, and validates mount/layout behavior.

Control flow: first run disables composefs on the kernel cmdline and checks `/run/ostree-booted`, `/etc` and `/usr` mountpoints, no transient `/etc`, no `/boot` mount, and default read-only `/sysroot`. It then removes prepare-root config to test writable default fallback. Next it enables `[etc] transient = true` and checks overlay upperdir. Finally it creates a traditional `/boot/loader` symlink and verifies prepare-root still does not mount `/boot`.

State/persistence: creates and tears down target sysroot, fake deployment files, bind mounts, `/run/ostree-booted`, `/run/ostree`, and temporary edits to `/usr/lib/ostree/prepare-root.conf`.

Dependencies/integration: requires podman/privileged container capabilities, mount/umount/findmnt, `ostree admin`, and installed `/usr/lib/ostree/ostree-prepare-root`.

Risks: modifies installed prepare-root config in-place with backup/restore; cleanup must run to avoid leaked mounts. The test disables composefs for unprivileged container compatibility, so composefs path is not covered here.

Test signals: strong direct coverage for nonstatic prepare-root legacy bind path, readonly sysroot config defaulting, transient `/etc`, and generator-owned `/boot` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests-unit-container/test-prepare-root.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/admin-test.sh -->
# sources/cloud-native/ostree/tests/admin-test.sh

Purpose: large sourced integration test script for `ostree admin` workflows: sysroot initialization, deployment, bootloader layout, status, upgrades, origins, remote config placement, undeploys, kernel arguments, downgrade guards, and fsfreeze watchdog behavior.

Important operations: initializes sysroots with modern/epoch modes; defines `validate_bootloader()` and `assert_ostree_deployment_refs()`; pulls local commits; deploys with kargs; verifies status text and JSON; checks composefs artifacts when enabled; tests `--print-current-dir`; validates bootloader directories/entries and deployment refs across multiple deploys; exercises staging failure when not booted; independent OS deployments; retain/rollback behaviors; modified `/etc` merge; undeploy errors; upgrades with remote add; set-origin; deploy unknown OS failure; multiple kargs; upgrade title/version formatting; override commit downgrade policy; source title display; remote add to physical and nonphysical sysroot; `core.add-remotes-config-dir=false`; and fsfreeze failure injection.

Control flow: linear shell assertions under `set -euo pipefail`, with many `echo "ok ..."` checkpoints. It mutates the test sysroot through a progression of deployments, upgrades, and cleanup operations, checking filesystem and command output after each stage.

State/persistence: creates/removes sysroot directories, repository refs, deployment directories, bootloader entries, origin files, remote config entries, and test commits. It deliberately changes deployment `/etc`, symlinks deployment `sysroot` for nonphysical tests, and configures repo settings.

Dependencies/integration: depends on the broader test harness for `CMD_PREFIX`, `assert_*`, `fatal`, `test_tmpdir`, `os_repository_new_commit`, `has_ostree_feature`, `bootcsum`, and repository fixtures. Uses `jq`, `stat`, `diff`, `sort`, and helper Python `bootloader-entries-crosscheck.py`.

Risks: because it is sourced, it assumes harness variables/functions are defined and current directory is controlled. Many assertions depend on exact bootversion/subbootversion layout and command output. Sleep is used to create chronological commit differences.

Test signals: broad high-value integration coverage for `ot-main` admin parsing, remote add/list behavior, deployment state persistence, bootloader integration, and upgrade/downgrade safety. It does not directly test prepare-root mount namespace code.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/admin-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/archive-test.sh -->
# sources/cloud-native/ostree/tests/archive-test.sh

Purpose: sourced integration test for archive/repo checkout and commit behavior.

Important operations: checks out `test2`, validates files and contents, creates `repo2`, initializes it, pulls local repo content, checks out from the clone, tests user-mode checkout `-U`, commits a uid/gid 0 tree, verifies `ostree ls` ownership output, reads file content with `ostree cat`, runs `ostree fsck`, and commits overlay content with base/owner overrides while checking recursive listing counts and ownership.

Control flow: linear shell assertions under `set -euo pipefail`, with `echo "ok ..."` markers after each tested behavior.

State/persistence: creates checkout directories, a secondary repo, commits new branches (`test2-uid0`, `test-base`), output files such as `uid0-ls-output.txt`, `cow-contents`, and `ls.txt`, and temporary overlay directories.

Dependencies/integration: relies on harness variables/functions such as `$OSTREE`, `CMD_PREFIX`, `COMMIT_ARGS`, `test_tmpdir`, `ostree_repo_init`, `assert_*`, and `can_create_whiteout_devices`.

Risks: line-count expectations depend on whiteout device capability. It is sourced and assumes fixture branch `test2` exists. It mutates current directory repeatedly.

Test signals: covers checkout, pull-local clone, user checkout, commit ownership metadata, `ls`, `cat`, `fsck`, and overlay-base commit behavior; useful as a sanity signal for archive-mode object persistence and checkout correctness.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/archive-test.sh -->
