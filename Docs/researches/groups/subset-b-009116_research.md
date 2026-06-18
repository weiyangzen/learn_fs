# Research Group subset-b-009116

This grouped report covers the exact source files assigned to work item `subset-b-009116`. Each source file has its own marker-delimited section for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/testfile2 -->
## sources/sync-backup/bup/test/testfile2

Purpose: `testfile2` is a large ASCII executable-looking Bup test fixture or corpus file. Its contents are ROT13-obfuscated Python 2 command modules: the shebang `#!/hfe/ova/rai clguba` decodes to an env Python shebang, `ohc` decodes to `bup`, and common tokens such as `vzcbeg`, `qrs`, and `pynff` decode to Python syntax. The file concatenates many Bup command implementations and repeats that command set several times. It is not shaped like a normal importable module, because it contains many shebang boundaries in one file and some deliberately odd or corrupted-looking fragments.

Important APIs, types, and functions: visible fragments include command option specs (`bcgfcrp`, a ROT13 `optspec`) and functions/classes corresponding to Bup commands: recursive listing, split/save/join/index, memory tests, virtual filesystem list/ftp/fuse helpers, repository init, midx generation, damage injection, server protocol handling, remote backup proxying, newline display, margin calculation, and fsck verification. The APIs referenced through obfuscation include Bup modules analogous to `git`, `options`, `client`, `hashsplit`, `index`, `vfs`, `helpers`, `ssh`, and Python libraries for `os`, `sys`, `stat`, `struct`, `mmap`, `subprocess`, `signal`, `readline`, and `fnmatch`.

Control flow: the file is a corpus of command entrypoints. Each block parses arguments, validates command-specific invariants, then runs command work against repository state, filesystem walks, pack/index files, or remote subprocess protocols. Several blocks use loops over files or pack entries, signal handlers around remote backup, and fork/wait logic for parallel fsck jobs. Because the same block family repeats later in the file, consumers should treat this as fixture data rather than canonical source.

State and persistence: decoded command logic reads and writes Bup repository state, refs, pack files, index files, temporary files, FUSE mount state, remote streams, and optional par2 recovery metadata. Some commands intentionally mutate files, such as the damage command. This makes execution unsafe unless a test explicitly expects destructive fixture behavior.

Dependencies and integration points: this fixture is part of Bup tests and likely feeds parser, hashing, indexing, or byte-content tests. It integrates with Python 2 syntax, Bup internals, git-style object storage, ssh/subprocess protocols, `/proc/self/status`, `/dev/urandom`, `/dev/null`, and optional FUSE/par2 tooling.

Risks: executing this file directly is risky and probably nonsensical because it concatenates many scripts. The ROT13 encoding can hide command semantics from naive scanners. Corrupted-looking snippets and repeated blocks should not be normalized away without knowing the fixture's test purpose. The content includes destructive command logic after decoding, so test runners must avoid accidental execution against real data.

Test signals: useful validation is byte-for-byte fixture stability, line-count/hash checks, and tests that consume the fixture as data. The observed SHA-256 during this research was `edd99e04101e315e71335aec5aa4f5b0557964667310774e6d81a728b5541f30`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/testfile2 -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/wvtest-bash.sh -->
## sources/sync-backup/bup/wvtest-bash.sh

Purpose: this Bash-specific extension augments the portable `wvtest.sh` assertions with stack tracking, caller location discovery, SIGPIPE-aware pipeline assertions, and regex matching. It is sourced only when `BASH_VERSION` is set, allowing the base harness to stay compatible with `/bin/sh`.

Important APIs and functions: `_wvbtstack` records asserted command text. `_wvpushcall` and `_wvpopcall` maintain that stack. `_wvbacktrace` walks Bash `FUNCNAME`, `BASH_SOURCE`, and `BASH_LINENO` to print nested WV assertion calls. `_wvfind_caller` records `WVCALLER_FILE` and `WVCALLER_LINE`. `WVPIPE` runs a command like `WVPASS` but treats SIGPIPE as success, using a runtime-computed `_wvsigpipe_rc`. `wv-match-rx` checks a string against a Bash regex and emits diagnostic context.

Control flow: on source, the script initializes the stack and computes the platform SIGPIPE exit code via `dev/python`. Assertion helpers push call text before running commands, find the caller, and pop on success. Failures delegate to `_wvcheck` from `wvtest.sh`, which exits the test script. `wv-match-rx` prints both compared values before the regex test.

State and persistence: all state is process-local shell state: `_wvbtstack`, `_wvsigpipe_rc`, `WVCALLER_FILE`, and `WVCALLER_LINE`. It does not persist files. It depends on stderr output as the test reporting channel.

Dependencies and integration points: it requires Bash arrays, Bash regex syntax, Bash stack variables, `sed`, and `dev/python`. It is loaded by `wvtest.sh`, so its functions are part of the wider Bup shell test framework.

Risks: failures in `dev/python` abort sourcing. Bash-specific syntax must never be parsed by plain `sh`, which is why the base harness gates sourcing. `wv-match-rx` prints failure text but does not explicitly exit; callers need the surrounding harness to interpret output. SIGPIPE handling assumes conventional shell exit status `128 + signal`.

Test signals: tests using nested `WVPASS` or `WVFAIL` should show meaningful backtraces. Pipeline tests such as producer piped into `head` should pass via `WVPIPE` when the producer receives SIGPIPE. Regex tests should emit clear "Matching" and "Against" diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/wvtest-bash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/wvtest-bup.sh -->
## sources/sync-backup/bup/wvtest-bup.sh

Purpose: `wvtest-bup.sh` is a tiny Bup-specific wrapper around the generic shell test harness. It sources `wvtest.sh`, captures the repository top directory, and provides helpers for creating temporary test directories and mount points under stable Bup test paths.

Important APIs and functions: `_wvtop="$(pwd -P)"` records the physical working directory at source time. `wvmktempdir` creates `$_wvtop/test/tmp` and returns a `mktemp -d` directory named from the current script. `wvmkmountpt` does the same under `$_wvtop/test/mnt`, intended for filesystem or FUSE mount tests.

Control flow: callers source this file from Bash tests. Sourcing first loads `wvtest.sh`, then initializes `_wvtop`. Each helper derives `script_name` from `$0`, ensures the parent directory exists, then calls `mktemp -d` with a per-script prefix. Any mkdir or mktemp failure exits the test immediately through `|| exit $?`.

State and persistence: it persists temporary directories under `test/tmp` and `test/mnt` in the source tree. It does not register cleanup itself, so test suites or callers must clean these directories.

Dependencies and integration points: depends on the Bup `wvtest.sh` assertion framework, POSIX `mkdir`, `mktemp`, `basename`, and the test suite convention that tests run from the Bup top directory. It integrates with mount-oriented tests by keeping mount points under a known tree.

Risks: if sourced from the wrong current directory, `_wvtop` points to the wrong root and helpers create directories outside the intended test tree. Mount-point directories may require special cleanup if a test fails while mounted. `$0` can be less descriptive for sourced scripts or unusual shell launchers.

Test signals: successful use returns unique directories. Failure is intentionally hard because temp directory creation is foundational for isolation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/wvtest-bup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/wvtest.sh -->
## sources/sync-backup/bup/wvtest.sh

Purpose: this is Bup's shell assertion harness. It exposes WvTest-style helpers for POSIX shell tests, with richer diagnostics when sourced from Bash. It also normalizes Bup test environment defaults by setting `BUP_TEST_LEVEL`, `BUP_DIR`, and `GIT_DIR`.

Important APIs and functions: `_wvtextclean` formats assertion text while disabling glob expansion. `_wvcheck` emits the canonical `! file:line text ok|FAILED` line and exits on failure. `WVEXPRC` asserts a command's exit status matches a shell case pattern. `WVPASS` and `WVFAIL` assert command success/failure. `WVPASSEQ` and `WVPASSNE` compare two strings. `WVPASSRC` and `WVFAILRC` assert the previous command's return code. `WVSTART`, `WVSKIP`, and `WVDIE` announce test sections, skips, and fatal failures.

Control flow: on source, the script sets defaults and conditionally sources `wvtest-bash.sh` for Bash-only stack/caller support. Non-Bash shells get no-op backtrace helpers and an "unknown:0" caller. Each assertion records the command, locates the caller, runs the test expression or command, and calls `_wvcheck`. Failures exit immediately with the failing code.

State and persistence: all state is shell process state plus stderr output. It deliberately points `BUP_DIR` and `GIT_DIR` to `/dev/null` unless tests override them, preventing accidental use of ambient repositories.

Dependencies and integration points: integrates with `wvtest-bash.sh` when Bash is available. It relies on shell builtins, test `[ ]`, and stderr output consumed by Bup's test runner. Bup tests source this file directly or through `wvtest-bup.sh`.

Risks: functions use `local`, which is not strictly POSIX in every `/bin/sh`. Assertion text intentionally expands `$*` unquoted after disabling globbing, so whitespace/newlines are normalized for output but still require care. `WVEXPRC` temporarily disables `set -e`, which is necessary but can surprise test authors.

Test signals: passing assertions emit `ok`; failures emit `FAILED`, optionally a Bash backtrace, and exit nonzero. `WVSKIP` emits `skip ok`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/wvtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/doc/conf.py -->
## sources/sync-backup/casync/doc/conf.py

Purpose: `doc/conf.py` configures Sphinx documentation generation for casync. It is a minimal Python 3 Sphinx configuration focused on reStructuredText sources, HTML output, and manual page generation.

Important settings: `extensions = ['sphinx.ext.todo']` enables todo directives. `templates_path`, `source_suffix`, `master_doc`, `project`, `version`, `release`, `language`, `exclude_patterns`, `pygments_style`, and `todo_include_todos` define core Sphinx behavior. `html_theme = 'alabaster'` and `html_static_path = ['_static']` configure HTML output. `htmlhelp_basename` names HTML Help output. `man_pages` defines one manual page, `casync(1)`, generated from the `casync` source.

Control flow: Sphinx executes this file as Python during documentation builds. There are no functions or classes; the file sets module globals read by Sphinx.

State and persistence: it does not persist state itself. Sphinx uses it to generate build artifacts in the Meson build directory and installed man pages through `doc/meson.build`.

Dependencies and integration points: depends on Sphinx and the `sphinx.ext.todo` extension. It integrates with `doc/meson.build`, which invokes `sphinx-build` for man output when the Meson `man` option is enabled.

Risks: version and release are hardcoded to `1`, while the Meson project version is `2`, so generated docs may report stale version metadata. `language = None` is accepted by older Sphinx but can warn on newer versions. `_static` and `_templates` are referenced even if absent, which may warn depending on Sphinx configuration.

Test signals: Meson's `man` custom target is the primary validation. A successful `sphinx-build -b man` should produce `casync.1`; warnings about version drift or missing static paths would indicate maintenance issues.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/doc/conf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/doc/meson.build -->
## sources/sync-backup/casync/doc/meson.build

Purpose: this Meson fragment builds and optionally installs casync's manual page from Sphinx documentation sources.

Important declarations: `sphinx_sources` lists `conf.py`, `casync.rst`, and `index.rst`. `man_pages` lists `casync.1`. `mandir1` resolves to `get_option('mandir')/man1`. When `get_option('man')` is true, Meson finds `sphinx-build-3` or `sphinx-build` and creates a `custom_target('man')`.

Control flow: the top-level build enters this subdir unconditionally. The actual Sphinx target is conditional on the `man` option. The custom target runs Sphinx with `-b man`, using the current source directory as input and current build directory as output, then installs the generated page into section 1.

State and persistence: generated state is limited to the Meson build directory and installed man page output. No source files are modified.

Dependencies and integration points: depends on Meson, Sphinx, the doc source files, and `doc/conf.py`. It is included by the top-level `meson.build`, and its `man` option is declared in `meson_options.txt`.

Risks: if `man=true` and Sphinx is missing, configuration fails because `find_program` is required by default. The hardcoded output list must match what Sphinx writes; source renames require updates here. The `man` option description in `meson_options.txt` appears to have a missing closing parenthesis, a cosmetic issue but useful signal for polish.

Test signals: configuring with `-Dman=true` should find Sphinx and build `casync.1`. Configuring with `-Dman=false` should skip Sphinx entirely.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/doc/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/meson.build -->
## sources/sync-backup/casync/meson.build

Purpose: the top-level Meson project file configures casync's C build, feature detection, dependencies, generated config header, executables, tests, fuzzers, documentation, completions, and install-time protocol symlinks.

Important APIs and declarations: `project('casync', 'c', version : '2', ...)` sets GNU11 defaults and install dirs. A large `c_args` list enforces warning and hardening flags when supported. `configuration_data()` writes `config.h` values for version, `_GNU_SOURCE`, type sizes, functions (`renameat2`, `copy_file_range`, `getrandom`), compression libraries, and feature toggles. Dependencies include `liblzma`, `zlib`, `libzstd`, `libcurl`, `openssl`, `acl`, optional `fuse`, `selinux`, `udev`, `threads`, and `m`. It builds `casync`, `casync-http`, `notify-wait`, shell completions, docs, tests, fuzzers, and tag targets.

Control flow: configuration detects compiler support and selected options, then enters `src`, `test`, `shell-completion/bash`, and `doc`. It creates executables from source lists populated by subdirs. It configures shell test scripts with paths and feature booleans, registers unit tests, and conditionally installs udev rules. It creates protocol symlinks for `casync-https`, `casync-ftp`, and `casync-sftp`.

State and persistence: build state includes `config.h`, configured test scripts, generated udev rules, executable outputs, installed binaries, protocol symlinks, and optional man/completion artifacts. Source state is not mutated except build-directory postconf symlinks.

Dependencies and integration points: central integration point for all C modules in `src`, tests in `test`, fuzzers, Sphinx docs, bash completion, and udev. It also injects `-include config.h` into all C compilation.

Risks: `auto_features=enabled` plus required dependencies can make configuration strict by default. The udev rule dir auto-detection assumes `udev.pc` provides `udevdir`; if not found with `udev=true`, this can fail. Install/postconf symlink scripts assume Unix shell behavior. Test timeouts are long and may need privileged features for FUSE/NBD.

Test signals: `meson test` covers shell scripts, C unit tests, help output tests, and fuzzer binary builds. Configuration with different feature options is important because `CA_COMPRESSION_DEFAULT` and optional code paths depend on generated macros.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/meson_options.txt -->
## sources/sync-backup/casync/meson_options.txt

Purpose: this file defines Meson project options controlling optional integrations, compression support, fuzzing modes, man page generation, udev install paths, and bash completion installation.

Important options: boolean `fuse`, `selinux`, and `udev` default to true. `udevrulesdir` allows overriding the rules install directory. `man` controls Sphinx man page generation. Feature options `libzstd`, `liblzma`, and `libz` control compression library linking. Booleans `oss-fuzz` and `llvm-fuzz` select fuzzer integration modes. `bashcompletiondir` controls shell completion install path, with `"no"` disabling installation.

Control flow: options are read by the top-level and subdirectory Meson files. The top-level build rejects enabling both fuzzing modes, resolves dependencies based on these settings, writes feature macros into `config.h`, and controls installation of udev rules, docs, and completions.

State and persistence: no direct runtime state. These options influence generated build outputs, installed files, and compiled feature availability.

Dependencies and integration points: maps directly into dependency detection in `meson.build`, `doc/meson.build`, and `shell-completion/bash/meson.build`. Compression options affect `cacompression.h` through generated `HAVE_LIB*` macros.

Risks: default true values for FUSE, SELinux, and udev can make builds fail on systems without development packages unless users disable them. The `man` option description is missing a closing parenthesis. The fuzz options are typed boolean but use string-looking default values `'false'`; Meson accepts booleans more idiomatically as `false`.

Test signals: option matrix builds should verify `-Dfuse=false`, `-Dselinux=false`, `-Dudev=false`, compression library combinations, `-Dman=false`, and each fuzzer mode independently.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/meson_options.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/shell-completion/bash/meson.build -->
## sources/sync-backup/casync/shell-completion/bash/meson.build

Purpose: this Meson fragment installs the casync bash completion script into a discovered or configured completion directory.

Important declarations: it reads `bashcompletiondir = get_option('bashcompletiondir')`. If empty, it tries `dependency('bash-completion', required : false)` and reads the `completionsdir` pkg-config variable. If that dependency is unavailable, it falls back to `datadir/bash-completion/completions`. If the result is not `"no"`, it installs the `casync` completion file.

Control flow: execution is straightforward at configure time. The install step is conditional only on the final directory value.

State and persistence: no build-time generated state. Install-time state is one completion file under the selected completion directory.

Dependencies and integration points: depends on Meson, the top-level `datadir` variable, `meson_options.txt`, and optionally the `bash-completion` pkg-config package. It is included unconditionally by the top-level build.

Risks: `bashcompletiondir=no` is a string sentinel, not a boolean. Packaging scripts need to pass exactly `-Dbashcompletiondir=no` to disable. If `bash-completion` is missing, the fallback may not match distribution policy. The script assumes the completion source file is named `casync` in this directory.

Test signals: configure with default, explicit path, and `"no"` values. Install dry runs should show the completion installed only when enabled.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/shell-completion/bash/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/75-casync.rules.in -->
## sources/sync-backup/casync/src/75-casync.rules.in

Purpose: this is a udev rules template for casync's NBD integration. It asks udev to query `casync udev` for block devices matching `nbd*` and creates a symlink from the returned `CASYNC_NAME` environment value.

Important rules: removal events jump to `casync_end`. For block subsystem devices with kernel name `nbd*`, udev imports properties from `@bindir_unquoted@/casync udev %N`. If `ENV{CASYNC_NAME}` is non-empty, it appends a symlink using that name. The final label terminates the rule sequence.

Control flow: Meson configures `@bindir_unquoted@` into the generated `75-casync.rules`. At runtime, udev evaluates rules on device events. The import program runs only for matching NBD block devices that are not remove events.

State and persistence: installed state is the generated rule under the udev rules directory. Runtime state is udev-created device symlinks based on `CASYNC_NAME`.

Dependencies and integration points: integrates with `meson.build`, the `udev` option, libudev support, NBD block devices, and the `casync udev` command implementation elsewhere in `src`.

Risks: udev imports execute a casync binary on device events, so the path must be correct and the command must be fast and robust. Unsanitized or unexpected `CASYNC_NAME` values could affect symlink creation. Rules install only when `udev=true`.

Test signals: after installation, NBD device events should call `casync udev %N` and create symlinks only when a valid `CASYNC_NAME` is produced. Meson should configure the binary path correctly.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/75-casync.rules.in -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cacache.c -->
## sources/sync-backup/casync/src/cacache.c

Purpose: `cacache.c` implements `CaCache`, a reference-counted lookup cache that maps a source `CaLocation` to a chunk ID and origin chain. It accelerates repeated chunk generation by avoiding rehashing unchanged source locations.

Important APIs and functions: `ca_cache_new/ref/unref` manage lifetime. `ca_cache_set_digest_type`, `ca_cache_set_fd`, and `ca_cache_set_path` configure the cache before use. `ca_cache_get` reads a cache entry and reconstructs `CaOrigin`. `ca_cache_put` writes an origin-to-chunk mapping. `ca_cache_remove` deletes a mapping. Internally `ca_cache_open` lazily creates/opens the cache directory and marks it `FS_NODUMP_FL`.

Control flow: cache keys are derived from the first location via `ca_location_id_make` and formatted through `ca_chunk_id_format_path` with `.cachi` suffix. `get` accepts two on-disk formats: symlink targets for single-location origins, and regular files containing a binary chunk ID followed by NUL-terminated location strings. It validates that cached locations include size and mtime and that the first origin item matches the lookup location. `put` prefers a symlink for a single origin item, otherwise writes a temporary regular file and atomically renames it.

State and persistence: persistent state lives in the cache directory as sharded `.cachi` entries. The object stores fd/path/digest state in memory. Writes are immutable-ish: existing entries cause a no-op success result.

Dependencies and integration points: depends on `cachunkid`, `calocation`, `caorigin`, `cadigest`, `realloc-buffer`, `chattr`, and utility cleanup helpers. It integrates with chunk generation and matching paths that can use cached origins.

Risks: cache correctness depends on location metadata, especially mtime and feature flags. Corrupt or truncated entries return `-EINVAL`. Symlink target length can force fallback to regular files. `ca_cache_set_fd` takes ownership-like responsibility for the fd and closes it on unref; callers must not also close it unexpectedly. Cache entries are redundant but stale entries can reduce performance or produce validation failures.

Test signals: unit tests should cover missing cache path, symlink entries, regular file entries, stale metadata mismatch, corrupt/truncated data, duplicate put idempotence, and remove cleanup of empty shard directories.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cacache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cacache.h -->
## sources/sync-backup/casync/src/cacache.h

Purpose: `cacache.h` declares the opaque `CaCache` API used to memoize source location to chunk/origin mappings.

Important APIs and types: `typedef struct CaCache CaCache` hides implementation details. Public functions create, ref, unref, set digest type, configure by fd or path, get a mapping, put a mapping, and remove a mapping. `DEFINE_TRIVIAL_CLEANUP_FUNC(CaCache*, ca_cache_unref)` provides cleanup-attribute integration.

Control flow contract: callers allocate a cache, configure either fd or path before use, optionally set a digest type before any digest is created, then call get/put/remove. `ca_cache_get` can return a chunk ID and optionally transfer a referenced `CaOrigin`.

State and persistence: the header abstracts persistent cache entries stored by `cacache.c`. The API implies reference counting and ownership transfer for returned origins.

Dependencies and integration points: includes `cachunkid.h`, `calocation.h`, `caorigin.h`, and `util.h`, so users get chunk IDs, location objects, origin objects, and cleanup macros. It is consumed by chunk generation/matching code.

Risks: the fd/path setters are mutually exclusive and are one-shot in the implementation. Changing digest type after cache use returns busy. Callers must respect negative errno-style returns.

Test signals: compile-level tests should ensure the opaque type remains hidden and cleanup macro works. Behavioral tests belong with `cacache.c`.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cacache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cachunk.c -->
## sources/sync-backup/casync/src/cachunk.c

Purpose: `cachunk.c` implements chunk load/save helpers, compression/decompression wrappers, and sharded chunk-file storage operations. It is central to reading and writing casync chunk payloads in compressed or uncompressed form.

Important APIs and functions: `ca_load_fd`, `ca_load_and_decompress_fd`, and `ca_load_and_compress_fd` read fd contents into `ReallocBuffer`. `ca_save_fd`, `ca_save_and_compress_fd`, and `ca_save_and_decompress_fd` write data to fds. `ca_compress` and `ca_decompress` operate in memory. Chunk-file APIs include `ca_chunk_file_open`, `ca_chunk_file_test`, `ca_chunk_file_load`, `ca_chunk_file_save`, `ca_chunk_file_mark_missing`, and `ca_chunk_file_remove`.

Control flow: load/save functions enforce min/max chunk sizes and stream through `CompressorContext`. Detection uses `detect_compression` before decoding. Chunk paths are formatted as `<prefix><first4>/<fullid><suffix>`. Saves first test for existing chunks, write a random `.tmp` suffixed file, transform data if requested, then rename without replacement to the final suffix. Loads try the desired representation first and fall back to the alternate representation, converting as needed. Missing chunks are represented by symlinks to `/dev/null`; open with `O_NOFOLLOW` returns `-ELOOP`, translated to `-EADDRNOTAVAIL`.

State and persistence: persistent state is the chunk store directory, shard directories, immutable read-only chunk files, compressed chunk suffix variants, temporary files, and missing-marker symlinks. Temporary files are unlinked on failure.

Dependencies and integration points: depends on `cachunkid`, `cacompression`, `compressor`, `cautil`, `def`, `realloc-buffer`, and utility wrappers such as `loop_write`, `rename_noreplace`, and `random_u64`. Compression availability depends on build-time feature macros.

Risks: decompression and compression limits are security-critical. Some paths return `-EINVAL` where preserving the original unlink error might be more diagnostic, notably `ca_chunk_file_remove` after uncompressed unlink failures other than `ENOENT`. `ca_load_and_decompress_fd` appears to return `0` if `compressor_input` fails inside the main loop, which may mask an error. Race handling relies on no-replace rename and immutable files.

Test signals: tests should cover round-trips for every compression type, load fallback between compressed and uncompressed storage, max-size rejection, empty chunk rejection, missing-marker behavior, duplicate save returning `-EEXIST`, temp cleanup on transform errors, and removal of both suffix variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cachunk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cachunk.h -->
## sources/sync-backup/casync/src/cachunk.h

Purpose: `cachunk.h` declares chunk payload limits, compression representation choices, fd/in-memory conversion helpers, and chunk-file store operations.

Important APIs and types: `CA_CHUNK_SIZE_LIMIT_MAX` is 128 MiB and `CA_CHUNK_SIZE_LIMIT_MIN` is 1 byte. `CaChunkCompression` distinguishes `CA_CHUNK_UNCOMPRESSED`, `CA_CHUNK_COMPRESSED`, and `CA_CHUNK_AS_IS`. The API covers loading, saving, compressing, decompressing, opening chunk files, testing existence, loading/saving chunk files with desired/effective compression, marking missing chunks, and removing chunks.

Control flow contract: callers choose desired storage representation and a compression algorithm where relevant. `CA_CHUNK_AS_IS` is allowed for load/save desired behavior but not as an effective on-disk representation. `ca_chunk_file_load` can report the effective representation.

State and persistence: declarations map to chunk-store files managed by `cachunk.c`. The header itself does not expose store layout beyond requiring a cache fd, optional prefix, chunk id, and suffix-aware helpers.

Dependencies and integration points: includes `cachunkid.h`, `cacompression.h`, and `realloc-buffer.h`. It is used by higher-level encoder, store, and network code that needs consistent chunk limits and compression semantics.

Risks: callers must enforce ownership and lifetime for `ReallocBuffer` and fds. Passing inconsistent effective/desired compression values is rejected by implementation. The max-size constant is a hard safety limit and must stay aligned with protocol expectations.

Test signals: compile tests should exercise enum values and prototypes; runtime behavior is covered through `cachunk.c` tests and integration tests that write/read chunk stores.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cachunk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cachunker.c -->
## sources/sync-backup/casync/src/cachunker.c

Purpose: `cachunker.c` implements casync's content-defined chunk boundary scanner using a rolling buzhash. It supports configurable min/average/max sizes and a fixed-size special case.

Important APIs and functions: `ca_chunker_set_size` validates and computes chunk sizing parameters and the discriminator. `ca_chunker_start` initializes rolling hash state over a full window. `ca_chunker_roll` advances the hash by removing one byte and adding another. `ca_chunker_scan` consumes data until it finds a boundary or reports that more data is needed.

Control flow: size configuration fills zero values from defaults or proportional values, bounds them by `CA_CHUNK_SIZE_LIMIT_MIN/MAX`, and computes a discriminator adjusted by `CA_CHUNKER_DISCRIMINATOR_FROM_AVG`. Scanning skips boundary checks until the minimum size window can matter, fills the 48-byte window, then rolls over incoming bytes. A boundary occurs at max size or when `hash % discriminator == discriminator - 1`. On boundary, hash/window/chunk counters reset.

State and persistence: all state is in the caller-owned `CaChunker`: rolling hash, window bytes, window size, current chunk size, configured sizes, and discriminator. No persistent I/O is performed.

Dependencies and integration points: depends on `cachunk.h` for hard chunk size limits and `util.h` for rotation/min/assert/log helpers. Higher-level chunkers feed file data through `ca_chunker_scan` to split streams before hashing and storing chunks.

Risks: `ca_chunker_set_size` returns `-EBUSY` once scanning has started (`window_size != 0`), so callers must configure early. The average-size discriminator is approximate and assumes common min/max ratios. Fixed-size mode has separate control flow and should be tested. Passing empty buffers is not explicitly accepted because `ca_chunker_scan` asserts `p`.

Test signals: `test-cachunker` and histogram tests should validate default distribution, configured min/max bounds, fixed-size cuts, streaming behavior across calls, and low-level buzhash start/roll consistency.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cachunker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cachunker.h -->
## sources/sync-backup/casync/src/cachunker.h

Purpose: `cachunker.h` exposes the content-defined chunker state structure, constants, initializer, and scanning functions.

Important APIs and types: `CA_CHUNK_SIZE_AVG_DEFAULT` is 64 KiB. `CA_CHUNKER_WINDOW_SIZE` is 48 bytes. `CA_CHUNKER_DISCRIMINATOR_FROM_AVG(avg)` encodes the empirical average-size correction. `CaChunker` stores hash, window counters, configured min/max/avg sizes, discriminator, and the rolling window. `CA_CHUNKER_INIT` initializes default min/avg/max and discriminator. Public functions configure size, scan data, and expose low-level buzhash start/roll for tests.

Control flow contract: callers initialize with `CA_CHUNKER_INIT`, optionally call `ca_chunker_set_size` before scanning, then feed data to `ca_chunker_scan` until it returns an offset or `(size_t)-1`.

State and persistence: state is entirely in the struct and is reset on discovered chunk boundaries. No heap allocation or persistent storage is implied by the header.

Dependencies and integration points: includes integer, size, and boolean headers. It integrates with `cachunker.c` and higher-level encoding/chunking code.

Risks: because the struct is public, external callers can corrupt invariants if they mutate fields directly. The macro discriminator uses floating-point constants and casts to `size_t`, so extreme averages should be validated through `ca_chunker_set_size`.

Test signals: tests should use both public scan behavior and the exported low-level hash functions. ABI-sensitive consumers should be rebuilt if struct fields change.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cachunker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cachunkid.c -->
## sources/sync-backup/casync/src/cachunkid.c

Purpose: `cachunkid.c` implements parsing, formatting, hashing, and path formatting for fixed 32-byte casync chunk IDs.

Important APIs and functions: `ca_chunk_id_parse` decodes a 64-character lowercase hex string into `CaChunkID`. `ca_chunk_id_format` encodes a chunk ID as lowercase hex. `ca_chunk_id_make` hashes data through a caller-provided `CaDigest` and copies the digest into a chunk ID. `ca_chunk_id_format_path` creates sharded paths using the first four hex characters as a directory and the full hex ID as the filename, with optional prefix and suffix.

Control flow: parser decodes two nibbles per byte and rejects non-hex or trailing characters. Formatter writes two hex chars per byte and a NUL terminator. Maker validates digest, data pointer, size limits, and digest size, then resets/writes/reads the digest. Path formatting first writes the full ID after the directory separator area, copies the first four ID characters into the shard directory, inserts `/`, and appends suffix if present.

State and persistence: no persistent state by itself. Its path format determines on-disk layout for cache and chunk files.

Dependencies and integration points: depends on `cadigest`, `cachunk` for size limits, and logging/util headers. Used by `cacache.c`, `cachunk.c`, and any code that names chunks.

Risks: parser accepts only lowercase `a-f`, not uppercase. `ca_chunk_id_format_path` assumes caller-provided buffer matches `CA_CHUNK_ID_PATH_SIZE`. Incorrect prefix/suffix sizing can overflow if callers ignore the macro. `ca_chunk_id_make` reuses and mutates the digest context.

Test signals: tests should cover parse/format round-trips, invalid hex, uppercase rejection if intentional, path formatting with/without prefix/suffix, and digest size mismatch.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cachunkid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cachunkid.h -->
## sources/sync-backup/casync/src/cachunkid.h

Purpose: `cachunkid.h` defines the fixed-size `CaChunkID` type and helper API for chunk ID equality, null checks, digest creation, formatting, and path sizing.

Important APIs and types: `CA_CHUNK_ID_SIZE` is 32 bytes. `CA_CHUNK_ID_FORMAT_MAX` is 65 bytes including NUL. `CaChunkID` is a union of byte and u64 views. Functions parse, format, make IDs from digest/data, and format sharded paths. Inline helpers `ca_chunk_id_equal` and `ca_chunk_id_is_null` support comparisons. `CA_CHUNK_ID_PATH_SIZE(prefix, suffix)` computes buffer length.

Control flow contract: callers pass non-null buffers sized by the macros. Chunk IDs may represent SHA-256 or SHA-512/256 depending on digest context.

State and persistence: the type is embedded in cache and chunk-store records. The path macro defines the buffer contract used by store code.

Dependencies and integration points: includes `cadigest.h`, string/int headers, and relies on `strlen_null` for path sizing. Used throughout chunk, cache, index, and protocol code.

Risks: `ca_chunk_id_is_null` appears to loop over all u64 slots but checks `a->u64[0]` each iteration instead of `a->u64[i]`; a value with the first word zero and later words nonzero would be incorrectly reported null. This is a correctness bug if the helper is used for validation. The public union exposes representation and alignment assumptions.

Test signals: add a regression test where only a later `u64` lane is nonzero. Existing tests should also cover equality, null pointer behavior, and path size correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cachunkid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cacommon.h -->
## sources/sync-backup/casync/src/cacommon.h

Purpose: `cacommon.h` defines a shared iteration direction enum used by casync APIs that navigate ordered collections.

Important APIs and types: `CaIterate` contains `CA_ITERATE_CURRENT`, `CA_ITERATE_FIRST`, `CA_ITERATE_LAST`, `CA_ITERATE_NEXT`, `CA_ITERATE_PREVIOUS`, `_CA_ITERATE_MAX`, and `_CA_ITERATE_INVALID = -1`.

Control flow contract: callers can pass these enum values to functions that need relative or absolute iteration movement. `_CA_ITERATE_MAX` is a sentinel for bounds checking, and `_CA_ITERATE_INVALID` supports error/default initialization.

State and persistence: no state or persistence. This is a pure shared type header.

Dependencies and integration points: it has no includes and is safe to include broadly. It likely integrates with index, archive, or traversal code elsewhere in `src`.

Risks: because this header is small and generic, meaning depends entirely on consuming APIs. Callers should not persist enum numeric values across incompatible versions unless the protocol documents them.

Test signals: compile-time coverage comes from consumers. Unit tests for iterator consumers should exercise every enum value and invalid handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cacommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cacompression.c -->
## sources/sync-backup/casync/src/cacompression.c

Purpose: `cacompression.c` maps casync compression enum values to user-facing strings and parses strings back to enum values.

Important APIs and functions: a static `table` maps `CA_COMPRESSION_XZ` to `"xz"`, `CA_COMPRESSION_GZIP` to `"gzip"`, and `CA_COMPRESSION_ZSTD` to `"zstd"`. `ca_compression_type_to_string` bounds-checks an enum and returns a string or `NULL`. `ca_compression_type_from_string` rejects empty input, treats `"default"` as `CA_COMPRESSION_DEFAULT`, otherwise scans the table and returns a matching enum or invalid.

Control flow: parsing is linear over `_CA_COMPRESSION_TYPE_MAX`. Formatting is direct table lookup after range checks.

State and persistence: no mutable state. These conversions influence CLI/config/protocol-facing representation but do not persist anything themselves.

Dependencies and integration points: depends on `cacompression.h` and utility helpers `isempty` and `streq`. It integrates with chunk load/save code, command-line option parsing, and build-time compression feature selection.

Risks: the table contains strings for all enum values even if the corresponding library was not built. Callers must still check build support before attempting compression. Empty or null strings return invalid. The default mapping depends on compile-time `HAVE_LIB*` macros, so behavior changes across builds.

Test signals: tests should parse each string, format each valid enum, reject unknown/empty strings, and verify `"default"` maps to the build-selected default.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cacompression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cacompression.h -->
## sources/sync-backup/casync/src/cacompression.h

Purpose: `cacompression.h` defines the compression type enum and conversion API used across casync chunk storage and user-facing options.

Important APIs and types: `CaCompressionType` enumerates XZ, gzip, and zstd, plus `_CA_COMPRESSION_TYPE_MAX` and `_CA_COMPRESSION_TYPE_INVALID`. `CA_COMPRESSION_DEFAULT` is selected at compile time: zstd if available, else gzip, else xz, else invalid. Public functions convert to/from strings.

Control flow contract: callers should validate values against `_CA_COMPRESSION_TYPE_MAX` and handle `_CA_COMPRESSION_TYPE_INVALID`, especially when no compression library is enabled. `CA_COMPRESSION_DEFAULT` is not a distinct runtime value; it aliases one concrete enum or invalid through preprocessor selection.

State and persistence: no state. The enum may be serialized indirectly through strings or chunk suffix behavior.

Dependencies and integration points: relies on build-generated macros `HAVE_LIBZSTD`, `HAVE_LIBZ`, and `HAVE_LIBLZMA`, supplied by `config.h` included globally from Meson. Used by `cachunk.h/c`, compressor code, and option parsing.

Risks: including this header without generated config macros would break default selection, but the build injects `-include config.h`. Default compression can change when build dependencies change, which affects output compatibility/performance expectations.

Test signals: build matrix tests with different compression libraries should verify default selection and conversion behavior. Runtime tests should ensure unsupported algorithms are rejected by the compressor layer even if string parsing recognizes them.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cacompression.h -->
