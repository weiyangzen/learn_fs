# subset-b-009125 research

Grouped research report for git-annex browser JavaScript, git-crypt C++/workflow/manpage files, and git-lfs GitHub automation files. Each section preserves the exact source path and is wrapped for reconciliation into the requested source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/static/js/jquery.ui.sortable.js -->
# sources/sync-backup/git-annex/static/js/jquery.ui.sortable.js

Purpose: vendored jQuery UI Sortable 1.10.4 plugin that turns a container's child elements into reorderable items, with support for connected sortable lists, placeholder/helper elements, containment, grid snapping, auto-scroll, revert animation, and jQuery UI event callbacks.

Important APIs/types/functions: registers `$.widget("ui.sortable", $.ui.mouse, ...)`; public methods include `refresh`, `refreshPositions`, `serialize`, `toArray`, and `cancel`. Core mouse hooks are `_mouseCapture`, `_mouseStart`, `_mouseDrag`, and `_mouseStop`. Internal movement helpers include `_intersectsWith`, `_intersectsWithPointer`, `_intersectsWithSides`, `_contactContainers`, `_createPlaceholder`, `_createHelper`, `_setContainment`, `_generatePosition`, `_convertPositionTo`, `_rearrange`, `_clear`, `_trigger`, and `_uiHash`.

Control flow: creation marks the element as `ui-sortable`, gathers items, determines floating orientation, initializes mouse handling, and sets `ready`. Mouse capture refreshes item metadata, finds the clicked sortable item, and validates an optional handle. Drag start creates/caches the helper, records offsets and original DOM position, creates a placeholder, applies cursor/opacity/z-index/containment state, fires `start` and `activate`, and invokes an initial drag. Drag events compute helper position, perform auto-scroll, update helper CSS, test intersections, rearrange the placeholder, contact connected containers, notify the droppable manager, and fire `sort`. Stop either animates to the placeholder or clears immediately. Clear restores CSS, moves the current item before the placeholder, removes helper/placeholder, emits delayed `receive`, `update`, `remove`, `deactivate`, `out`, `beforeStop`, and `stop` events, and resets drag state.

State/persistence behavior: all state is in DOM, jQuery data, widget instance fields, and transient event state. The plugin stores per-item ownership with `data(this.widgetName + "-item")`, tracks `currentItem`, `currentContainer`, `containers`, `items`, cached geometry, `domPosition`, `lastPositionAbs`, and temporary style values. It does not persist data to storage; DOM order is the durable observable result for callers.

Dependencies/integration: depends on jQuery UI core, mouse, and widget factory, with optional integration with `$.ui.ddmanager`. It uses jQuery dimensions, offsets, scroll parents, callbacks, selectors, data APIs, and animation. `serialize` and `toArray` provide integration points for sending reordered IDs to a server.

Risks/test signals: geometry is sensitive to scroll parents, relative positioning, tables, images, nested sortables, connected containers, and old browser behavior. Test signals should cover pointer and intersect tolerances, horizontal/floating layouts, nested containers, placeholder sizing, helper clone/original behavior, cancel/revert cleanup, event ordering, disabled state, and serialization after reordering.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/static/js/jquery.ui.sortable.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/static/js/jquery.ui.widget.js -->
# sources/sync-backup/git-annex/static/js/jquery.ui.widget.js

Purpose: vendored jQuery UI Widget Factory 1.10.4, providing the base class and plugin bridge used by jQuery UI widgets such as sortable. It standardizes widget construction, inheritance, option management, event binding, teardown, and effect helpers.

Important APIs/types/functions: exports `$.widget`, `$.widget.extend`, `$.widget.bridge`, and base constructor `$.Widget`. Base prototype methods include `_createWidget`, `_getCreateOptions`, `_create`, `_init`, `destroy`, `widget`, `option`, `_setOptions`, `_setOption`, `enable`, `disable`, `_on`, `_off`, `_delay`, `_hoverable`, `_focusable`, `_trigger`, `_show`, and `_hide`. It also wraps `$.cleanData` to trigger `remove` before element cleanup.

Control flow: `$.widget` parses `namespace.name`, creates or redefines a constructor, sets up `_super`/`_superApply` wrappers for function properties, builds the prototype from the base plus proxied prototype, updates child constructors on redefinition, and installs a jQuery plugin bridge. The bridge dispatches string method calls to existing instances and object calls to initialization or option update. `_createWidget` binds the instance to an element, merges defaults with create options and caller options, sets document/window references, calls `_create`, fires `create`, and calls `_init`.

State/persistence behavior: state is per-widget instance and stored with jQuery data under `widgetFullName`, legacy widget name, and camel-case compatibility keys. It tracks `uuid`, `eventNamespace`, `options`, `bindings`, `hoverable`, and `focusable`. Destruction unbinds namespaced events, removes disabled/hover/focus classes, and clears data. No browser storage or server persistence is used.

Dependencies/integration: depends on jQuery core features including data, events, selectors, `$.Event`, `$.Callbacks`-style callbacks, delegation, and optional `$.effects`. It is the integration substrate for all widgets in this vendored UI stack.

Risks/test signals: method dispatch intentionally blocks private `_` methods and errors before initialization. Option handling must preserve nested option semantics and avoid sharing prototype options. Tests should cover widget inheritance, `_super` calls, redefinition of base widgets, delegated events with disabled checks, automatic destroy on remove, callback cancellation from `_trigger`, and fallback show/hide behavior when effects are absent.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/static/js/jquery.ui.widget.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/static/js/longpolling.js -->
# sources/sync-backup/git-annex/static/js/longpolling.js

Purpose: small git-annex web UI polling helper that repeatedly fetches HTML or text endpoints and lets callers continue, refresh UI fragments, or fail after repeated connection failures.

Important APIs/types/functions: global `connfails`, global `longpollcallbacks = $.Callbacks()`, `longpoll_div(url, divid, cont, fail)`, and `longpoll_data(url, cont)`.

Control flow: `longpoll_div` issues an HTML AJAX request, replaces the DOM element with matching `divid` on success, fires registered callbacks, resets failure count, and invokes `cont()`. On error it increments `connfails`; above 12 failures it calls `fail()`, otherwise it calls `cont()` to keep polling. `longpoll_data` issues a text AJAX request and calls `cont(1, data)` on success or `cont(0)` on failure.

State/persistence behavior: only global in-memory failure count and callback list are maintained. DOM replacement is the primary observable state change. There is no durable persistence, retry backoff, or cancellation token in this file.

Dependencies/integration: depends on jQuery AJAX and callback APIs. Callers provide continuation functions, so scheduling/repetition lives outside the helper. `longpollcallbacks` allows other UI modules to rerun behaviors after a div replacement.

Risks/test signals: `connfails` is shared across all long-poll elements, so one failing endpoint can affect another. The 12-failure threshold assumes up to four elements and expected failures during navigation. Tests should simulate success, repeated failure, DOM replacement, callback firing, and independent callers sharing the global failure counter.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/static/js/longpolling.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/.github/workflows/release-linux-arm64.yml -->
# sources/sync-backup/git-crypt/.github/workflows/release-linux-arm64.yml

Purpose: GitHub Actions workflow that builds and uploads a Linux ARM64 git-crypt binary whenever a GitHub release is published.

Important APIs/types/functions: `on.release.types: [published]`, build job on `ubuntu-22.04-arm`, upload job on `ubuntu-latest`, `actions/checkout@v3`, `actions/upload-artifact@v4`, `actions/download-artifact@v4`, and `actions/github-script@v6` calling `github.rest.repos.uploadReleaseAsset`.

Control flow: the build job checks out the repository, installs `libssl-dev`, runs `make`, and uploads the `git-crypt` binary as `git-crypt-artifacts`. The upload job depends on build, downloads that artifact, and uploads it to the release with a `linux-aarch64` asset name derived from `github.event.release.name`.

State/persistence behavior: state is carried between jobs via Actions artifacts and then persisted as a GitHub release asset. The build job has read-only contents permission; the upload job has write permission for release assets.

Dependencies/integration: integrates the repository Makefile with an ARM64 hosted runner and OpenSSL development package. Release identity is taken from the release event payload.

Risks/test signals: runner label availability and artifact naming are critical. The script imports `sha` from context but does not use it. Tests are release-dry-run/manual workflow checks: confirm ARM runner availability, binary architecture, successful artifact transfer, and uploaded asset name.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/.github/workflows/release-linux-arm64.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/.github/workflows/release-linux.yml -->
# sources/sync-backup/git-crypt/.github/workflows/release-linux.yml

Purpose: GitHub Actions workflow that builds and uploads a Linux x86_64 git-crypt release binary when a release is published.

Important APIs/types/functions: same two-job structure as the ARM64 workflow, using `ubuntu-22.04` for build and `ubuntu-latest` for upload, with `actions/checkout@v3`, `actions/upload-artifact@v4`, `actions/download-artifact@v4`, and `actions/github-script@v6`.

Control flow: checkout, install `libssl-dev`, run `make`, upload `git-crypt` artifact, then download and upload it to the release as `git-crypt-${release.name}-linux-x86_64`.

State/persistence behavior: the binary moves through the Actions artifact store and becomes a release asset. Permissions are narrowed to `contents: read` for build and `contents: write` for upload.

Dependencies/integration: relies on Ubuntu package OpenSSL headers/libraries, the C++ Makefile, and release event metadata.

Risks/test signals: no checksum, signature, or architecture validation is performed. Release tests should verify the output is executable, linked as expected, built from the intended tag, and asset upload does not collide with existing assets.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/.github/workflows/release-linux.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/.github/workflows/release-windows.yml -->
# sources/sync-backup/git-crypt/.github/workflows/release-windows.yml

Purpose: GitHub Actions workflow that builds and uploads a Windows x86_64 `git-crypt.exe` release binary when a release is published.

Important APIs/types/functions: build job on `windows-2022`, `msys2/setup-msys2@v2`, package list for MINGW64 toolchain and OpenSSL, `make LDFLAGS="-static-libstdc++ -static -lcrypto -lws2_32 -lcrypt32"`, artifact upload/download, and GitHub Script release asset upload.

Control flow: checkout, install MSYS2/MINGW dependencies, run a static-ish Windows build under the MSYS2 shell, upload `git-crypt.exe`, then upload the downloaded executable to the release as `git-crypt-${release.name}-x86_64.exe`.

State/persistence behavior: the executable is passed through the artifact store and persisted to the release. No signing or checksum state is produced in this workflow.

Dependencies/integration: integrates MSYS2 packages, MinGW OpenSSL, Windows system libraries `ws2_32` and `crypt32`, and the common git-crypt Makefile.

Risks/test signals: static linking flags and OpenSSL/MSYS2 package changes are likely failure points. There is no smoke test after build. Useful signals include `git-crypt.exe --version`, dependency inspection, artifact download validation, and release upload collision handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/.github/workflows/release-windows.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/Makefile -->
# sources/sync-backup/git-crypt/Makefile

Purpose: simple portable Makefile for building, optionally generating the manpage, cleaning, and installing the git-crypt binary and manpage.

Important APIs/types/functions: variables `CXXFLAGS`, `PREFIX`, `BINDIR`, `MANDIR`, `ENABLE_MAN`, `DOCBOOK_XSL`, `OBJFILES`, `LDFLAGS`, `XSLTPROC`, and `DOCBOOK_FLAGS`; targets `all`, `build`, `build-bin`, `git-crypt`, `build-man`, `clean`, `install`, and related `*-bin`/`*-man` targets.

Control flow: default `all` maps to `build`. `BUILD_TARGETS` conditionally includes `build-man` based on `ENABLE_MAN`. `git-crypt` links C++11 objects against `-lcrypto`. `util.o` and `coprocess.o` depend on both platform-specific implementation files because their `.cpp` files include the selected platform source. Manpage generation runs `xsltproc` over `man/git-crypt.xml`.

State/persistence behavior: build outputs are object files, `git-crypt`, and optionally `man/man1/git-crypt.1`. Install creates destination directories under `DESTDIR` plus prefix paths and copies the binary/manpage with expected modes.

Dependencies/integration: requires a C++11 compiler, OpenSSL libcrypto, make, and optionally `xsltproc` plus DocBook XSL. Release workflows invoke `make` directly and override `LDFLAGS` for Windows.

Risks/test signals: no dependency auto-generation for headers; platform-specific source inclusion is unusual but intentional. Test signals are clean rebuilds on Linux and Windows, optional `ENABLE_MAN=yes`, `make install DESTDIR=...`, and link failures against newer OpenSSL.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/commands.cpp -->
# sources/sync-backup/git-crypt/commands.cpp

Purpose: main implementation of git-crypt command behavior: Git filter plumbing (`clean`, `smudge`, `diff`), repository initialization/unlocking/locking, GPG collaborator key wrapping, key export/generation/migration, and status/fix reporting.

Important APIs/types/functions: public command functions declared in `commands.hpp`; helper functions for Git config/filter management, Git version parsing, state path resolution, `git checkout` batching, file attribute lookup, encrypted blob detection, encrypted file enumeration, key loading, GPG key decryption/encryption, and plumbing option parsing. Major commands are `clean`, `smudge`, `diff`, `init`, `unlock`, `lock`, `add_gpg_user`, `export_key`, `keygen`, `migrate_key`, and `status`; `rm_gpg_user`, `ls_gpg_users`, and `refresh` are stubs.

Control flow: path helpers locate internal `.git/git-crypt/keys` state and committed `.git-crypt/keys` repository state, with optional `git-crypt.repoStateDir`. `init` validates key names, generates a `Key_file`, stores it internally, and configures Git filters. `unlock` requires a clean worktree, loads symmetric key files or decrypts GPG-wrapped keys, installs internal key files, configures filters, touches encrypted files, and checks them out. `lock` removes internal key files and filter config, touches encrypted files, and checks them out to encrypted form. `clean` reads stdin, computes HMAC-SHA1 over plaintext, uses the HMAC as deterministic AES-CTR nonce, writes the `\0GITCRYPT\0` header plus nonce, and encrypts content. `smudge` and `diff` detect that header, decrypt, and verify the HMAC before returning success. `status` walks Git index/worktree entries, checks filter/diff attributes and encrypted blob headers, reports mismatches, and optionally stages fixed encrypted versions.

State/persistence behavior: persistent internal state is per-key key files under Git's private dir. Shared access state is GPG-encrypted key files under the repository `.git-crypt/keys/<key>/<version>/<fingerprint>.gpg` tree plus a `.git-crypt/.gitattributes` exemption file. Git config filter/diff sections are added/removed. File contents in the worktree and index are transformed through Git checkout/add/filter operations. Large clean inputs spill after about 8 MiB into `temp_fstream`.

Dependencies/integration: uses `git` commands extensively (`config`, `rev-parse`, `status`, `check-attr`, `ls-files`, `cat-file`, `checkout`, `add`, `commit`), the `Coprocess` wrapper for streaming subprocesses, GPG helpers, `Key_file`, AES/HMAC crypto, and platform utilities for touch/remove/directory listing. It relies on Git 1.8.5+ for efficient batch `check-attr` but falls back for older versions.

Risks/test signals: crypto correctness depends on deterministic HMAC nonce, HMAC verification, key version availability, and AES-CTR byte counter limits. Command safety depends on clean-worktree checks, path parsing with NUL-delimited Git output, correct attributes for named keys, and robust subprocess error handling. Important tests include round-trip clean/smudge, tamper detection, huge-file limit, unlock/lock with dirty worktrees, named keys, GPG collaborator addition with `--no-commit`, status warnings/fixes for unencrypted staged blobs, Git versions before/after 1.8.5, and custom repo state dirs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/commands.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/commands.hpp -->
# sources/sync-backup/git-crypt/commands.hpp

Purpose: public interface for git-crypt command handlers and command-specific help emitters.

Important APIs/types/functions: `struct Error` carries user-facing error messages; declarations for plumbing commands `clean`, `smudge`, `diff`; public commands `init`, `unlock`, `lock`, `add_gpg_user`, `rm_gpg_user`, `ls_gpg_users`, `export_key`, `keygen`, `migrate_key`, `refresh`, `status`; matching `help_*` functions; and `get_git_config`.

Control flow: this header has no runtime flow, but it defines the command dispatch contract consumed by `git-crypt.cpp` and implemented by `commands.cpp`.

State/persistence behavior: no direct state. Declared commands manipulate Git config, key files, worktree files, and repository `.git-crypt` state in the implementation.

Dependencies/integration: includes only `<string>` and `<iosfwd>` to keep compile coupling low. It is the boundary between CLI dispatch, GPG helper access to Git config, and command implementation.

Risks/test signals: adding a command requires updating this header, `commands.cpp`, and dispatch/help in `git-crypt.cpp`. Tests should verify every declared public command is either dispatched or intentionally hidden/stubbed.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/commands.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/coprocess-unix.cpp -->
# sources/sync-backup/git-crypt/coprocess-unix.cpp

Purpose: Unix implementation of the `Coprocess` abstraction for spawning child processes with optional stdin/stdout pipes backed by C++ streams.

Important APIs/types/functions: local `execvp` vector adapter, `Coprocess` constructor/destructor, `stdin_pipe`, `close_stdin`, `stdout_pipe`, `close_stdout`, `spawn`, `wait`, static `write_stdin`, and static `read_stdout`.

Control flow: pipe accessors lazily create POSIX pipes and wrap the parent ends in `ofhstream`/`ifhstream`. `spawn` forks; the child closes unused pipe ends, dup2s requested pipe ends onto fd 0/1, execs the command, and exits on failure. The parent closes child-side pipe ends. `wait` waits for the recorded pid and returns raw wait status.

State/persistence behavior: maintains pid, pipe file descriptors, and stream wrapper pointers. The destructor closes streams and pipe ends but does not wait for the child automatically.

Dependencies/integration: depends on POSIX `pipe`, `fork`, `dup2`, `execvp`, `waitpid`, `read`, `write`, and `close`, plus `System_error` and `fhstream`. Used by `util.cpp` command execution helpers.

Risks/test signals: callers must avoid deadlocks when writing and reading large bidirectional streams because this abstraction does not multiplex. Child lifetime is caller-managed through `wait`. Tests should cover command success/failure, stdout capture, stdin input, EINTR retry, descriptor closure, and wait status conversion by `exit_status`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/coprocess-unix.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/coprocess-unix.hpp -->
# sources/sync-backup/git-crypt/coprocess-unix.hpp

Purpose: Unix declaration of the `Coprocess` class used to run external commands with streamable stdin/stdout.

Important APIs/types/functions: class fields for `pid_t pid`, stdin/stdout pipe descriptors, `ofhstream` and `ifhstream` pointers, static read/write callbacks, deleted copy/assignment, and public methods `stdin_pipe`, `close_stdin`, `stdout_pipe`, `close_stdout`, `spawn`, and `wait`.

Control flow: no implementation flow in the header; it defines lazy pipe creation before `spawn`, stream closure, process spawn, and wait responsibilities.

State/persistence behavior: state is process and descriptor ownership. It has no persistent storage but manages OS handles that affect subprocess communication.

Dependencies/integration: includes `fhstream.hpp`, `<unistd.h>`, and `<vector>`. Selected by `coprocess.hpp` on non-Windows builds.

Risks/test signals: copy prevention avoids double-close, but raw pointers/descriptors require disciplined implementation. Tests should verify destructor cleanup and no descriptor leaks across repeated subprocess calls.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/coprocess-unix.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/coprocess-win32.cpp -->
# sources/sync-backup/git-crypt/coprocess-win32.cpp

Purpose: Windows implementation of `Coprocess`, using Win32 process creation and inheritable pipes to provide command execution compatible with the Unix abstraction.

Important APIs/types/functions: command-line quoting helpers `escape_cmdline_argument` and `format_cmdline`, `spawn_command`, `Coprocess` constructor/destructor, pipe accessors/closers, `spawn`, `wait`, `write_stdin`, and `read_stdout`.

Control flow: pipe accessors create inheritable pipes with `CreatePipe` and mark parent ends non-inheritable with `SetHandleInformation`. `spawn` formats the argument vector into a Windows command line, calls `CreateProcessA` with selected std handles, closes child-side pipe handles in the parent, and stores the process handle. `wait` waits indefinitely and returns the process exit code. Reads treat `ERROR_BROKEN_PIPE` as EOF and retry zero-byte pipe reads.

State/persistence behavior: maintains process and pipe `HANDLE`s plus stream wrappers. The destructor closes streams, pipe handles, and process handle. No durable state is written.

Dependencies/integration: depends on Win32 API, `fhstream`, and `System_error`. It is selected by `coprocess.hpp` when `_WIN32` is defined and underlies all Git/GPG subprocess calls on Windows.

Risks/test signals: Windows argument quoting is subtle, especially trailing backslashes and quotes. The implementation does not expose stderr capture. Tests should include arguments with spaces, quotes, and backslashes; stdin/stdout streaming; child nonzero exit codes; broken pipe EOF; and handle inheritance leaks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/coprocess-win32.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/coprocess-win32.hpp -->
# sources/sync-backup/git-crypt/coprocess-win32.hpp

Purpose: Windows declaration of the `Coprocess` class.

Important APIs/types/functions: fields for process, stdin, and stdout `HANDLE`s; stream pointers; static read/write callbacks; disabled copy/assignment; public pipe, spawn, and wait methods.

Control flow: declares the same lifecycle as the Unix header: request pipes, spawn process, close pipe ends, wait for exit.

State/persistence behavior: state is OS handle ownership and stream wrapper ownership. No persistent files are managed here.

Dependencies/integration: includes `fhstream.hpp`, `<windows.h>`, and `<vector>`. Used through `coprocess.hpp`.

Risks/test signals: handle cleanup and inheritance flags are the key correctness areas. Tests should check repeated subprocess creation without leaked handles and parity with Unix behavior for command execution helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/coprocess-win32.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/coprocess.cpp -->
# sources/sync-backup/git-crypt/coprocess.cpp

Purpose: platform-selection translation unit for the `Coprocess` implementation.

Important APIs/types/functions: conditionally includes `coprocess-win32.cpp` when `_WIN32` is defined, otherwise includes `coprocess-unix.cpp`.

Control flow: compile-time include selection only. The Makefile compiles `coprocess.cpp`, so the chosen platform implementation becomes part of `coprocess.o`.

State/persistence behavior: no state in this file; state lives in the selected implementation.

Dependencies/integration: pairs with `coprocess.hpp`, which similarly selects the platform header. This inclusion pattern explains the Makefile dependency on both platform source files.

Risks/test signals: unusual `.cpp` inclusion can surprise build tooling and dependency scanners. Test signals are successful single-definition builds on Windows and Unix and correct rebuilds when platform-specific files change.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/coprocess.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/coprocess.hpp -->
# sources/sync-backup/git-crypt/coprocess.hpp

Purpose: platform-selection header for the `Coprocess` class.

Important APIs/types/functions: includes `coprocess-win32.hpp` on `_WIN32`, otherwise `coprocess-unix.hpp`.

Control flow: compile-time selection only. Consumers include `coprocess.hpp` and get the right platform class declaration.

State/persistence behavior: no direct state; selected headers define process and pipe handle state.

Dependencies/integration: centralizes platform choice for `util.cpp` and command helpers, avoiding conditional code at call sites.

Risks/test signals: platform macros must be consistent between this header and `coprocess.cpp`. Build tests on both Windows and Unix are the primary signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/coprocess.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/crypto-openssl-11.cpp -->
# sources/sync-backup/git-crypt/crypto-openssl-11.cpp

Purpose: OpenSSL-backed implementation of AES-ECB block encryption, HMAC-SHA1 state, crypto initialization, and random byte generation for git-crypt.

Important APIs/types/functions: `init_crypto`, `Aes_ecb_encryptor::Aes_impl`, `Aes_ecb_encryptor` constructor/destructor/`encrypt`, `Hmac_sha1_state::Hmac_impl`, HMAC constructor/destructor/`add`/`get`, and `random_bytes`.

Control flow: initialization loads OpenSSL error strings. AES construction calls `AES_set_encrypt_key`; encryption calls `AES_encrypt`. HMAC construction allocates `HMAC_CTX`, initializes with `EVP_sha1`, streams data via `HMAC_Update`, and finalizes via `HMAC_Final`. Random generation calls `RAND_bytes` and constructs a detailed OpenSSL error message on failure.

State/persistence behavior: key material is held in OpenSSL `AES_KEY` and HMAC context objects. The AES destructor explicitly zeroes the key schedule. No persistent state is stored.

Dependencies/integration: depends on OpenSSL AES, SHA/HMAC/EVP/RAND/ERR APIs and `explicit_memset`. `crypto.cpp` uses `Aes_ecb_encryptor` for CTR mode; `key.cpp` uses `random_bytes`.

Risks/test signals: these are low-level security primitives. Tests should cover AES-CTR round trips, HMAC deterministic output, random generation failure propagation where injectable, key material zeroing under review, and compatibility with current OpenSSL deprecation behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/crypto-openssl-11.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/crypto.cpp -->
# sources/sync-backup/git-crypt/crypto.cpp

Purpose: implementation of AES-CTR stream processing built on top of the AES-ECB block encryptor declared in `crypto.hpp`.

Important APIs/types/functions: `Aes_ctr_encryptor` constructor/destructor, `process`, and static `process_stream`. `Aes_ctr_decryptor` is a typedef to the same class because CTR encryption and decryption are symmetric.

Control flow: construction copies a 12-byte nonce into the first part of a 16-byte counter block and starts `byte_counter` at zero. `process` generates a new AES pad every 16 bytes by storing the block counter in big-endian form into the last 4 bytes, encrypting the counter block, and XORing input bytes with pad bytes. Counter wrap throws a `Crypto_error`. `process_stream` reads chunks from an input stream, processes in place, and writes to output.

State/persistence behavior: state is the fixed nonce, rolling 32-bit byte counter, current counter block, and current pad. The destructor clears the pad. No persistent storage is used.

Dependencies/integration: depends on `Aes_ecb_encryptor`, `store_be32`, stream I/O, and `Crypto_error`. Used by `commands.cpp` for file clean/smudge/diff.

Risks/test signals: counter limit enforcement is essential because nonce/counter reuse breaks CTR security. Tests should verify known-vector behavior, chunk-boundary equivalence, in-place processing, decryption symmetry, and error on maximum byte counter wrap.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/crypto.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/crypto.hpp -->
# sources/sync-backup/git-crypt/crypto.hpp

Purpose: public crypto abstraction for git-crypt, declaring initialization, AES block/CTR classes, HMAC-SHA1 state, and random byte generation.

Important APIs/types/functions: `init_crypto`, `struct Crypto_error`, `class Aes_ecb_encryptor`, `class Aes_ctr_encryptor`, `typedef Aes_ctr_decryptor`, `class Hmac_sha1_state`, and `random_bytes`. Constants expose AES key length, HMAC key length, block length, nonce length, and `MAX_CRYPT_BYTES`.

Control flow: no direct runtime flow in the header; it defines object lifecycles for crypto operations implemented in `crypto.cpp` and `crypto-openssl-11.cpp`.

State/persistence behavior: classes encapsulate key schedules, counters, pads, and HMAC contexts using private implementation structs and `unique_ptr` where OpenSSL types are hidden.

Dependencies/integration: includes `key.hpp` for key-length constants and standard headers. Consumed by command filtering, key generation, and CLI initialization.

Risks/test signals: header constants define file format/security limits, especially 12-byte nonce and 32-bit block counter. ABI/source compatibility relies on implementation files matching the declarations.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/crypto.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/fhstream.cpp -->
# sources/sync-backup/git-crypt/fhstream.cpp

Purpose: custom C++ stream buffer implementation that adapts arbitrary read/write callbacks into `std::ostream` and `std::istream` behavior for subprocess pipes.

Important APIs/types/functions: `ofhbuf` constructor/destructor, `overflow`, `sync`, `xsputn`, `setbuf`; `ifhbuf` constructor/destructor, `underflow`, `xsgetn`, and `setbuf`.

Control flow: output buffers accumulate writes until overflow/sync, then repeatedly invoke the write callback until all bytes are written. Large `xsputn` writes flush the buffer and write directly. Input underflow preserves a small putback area, reads from the callback, and exposes buffered bytes; large `xsgetn` copies remaining buffered data and then reads directly.

State/persistence behavior: state is heap-allocated buffers, callback handles, put/get pointers, and output buffering. There is no persistent file state; the callback target owns actual handles.

Dependencies/integration: used by `Coprocess` pipe streams. Relies on callback functions throwing exceptions on OS-level errors.

Risks/test signals: partial reads/writes and EOF behavior must match C++ stream expectations. Tests should cover small/large writes, explicit `sync`, unbuffered mode via `setbuf(0,0)`, putback after direct reads, EOF propagation, and exception behavior from callbacks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/fhstream.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/fhstream.hpp -->
# sources/sync-backup/git-crypt/fhstream.hpp

Purpose: declares stream adapters `ofhstream` and `ifhstream` plus their underlying stream buffers for callback-backed handles.

Important APIs/types/functions: `ofhbuf`, `ofhstream`, `ifhbuf`, and `ifhstream`; callback signatures `size_t (*write_fun)(void*, const void*, size_t)` and `size_t (*read_fun)(void*, void*, size_t)`; deleted copy/assignment for buffers.

Control flow: constructors install custom buffers into standard stream base classes. Implementations handle overflow, sync, underflow, direct bulk I/O, and buffer switching.

State/persistence behavior: state is internal buffer memory and callback handle pointers. Destructors release buffers; `ofhbuf` destructor attempts to sync while ignoring exceptions.

Dependencies/integration: included by platform `Coprocess` headers to expose pipe streams as standard C++ iostreams.

Risks/test signals: destructor sync can hide final write errors unless callers explicitly sync/close. Tests should use fake callbacks to verify buffering and partial I/O behavior deterministically.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/fhstream.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/git-crypt.cpp -->
# sources/sync-backup/git-crypt/git-crypt.cpp

Purpose: program entry point and command dispatcher for the git-crypt CLI.

Important APIs/types/functions: global `argv0`, `print_usage`, `print_version`, `help_for_command`, `help`, `version`, and `main`.

Control flow: `main` records `argv0`, initializes standard streams and crypto, parses global `--help`, `--version`, and `--`, requires a command, then dispatches to public or plumbing command functions. Command-specific `Option_error` is caught close to dispatch so help for the selected command can be printed. Top-level catches translate `Error`, `Gpg_error`, `System_error`, `Crypto_error`, `Key_file` exceptions, and I/O failures into user-facing stderr messages and nonzero exit codes.

State/persistence behavior: only global process state is `argv0` and initialized stream/crypto settings. Persistent mutations are delegated to command handlers.

Dependencies/integration: includes all command, utility, crypto, key, GPG, and option headers. It is the executable target linked by the Makefile.

Risks/test signals: command dispatch must stay aligned with declarations and help text. Tests should cover global option parsing, unknown options/commands, command help, version output, and exception-to-exit-code mapping.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/git-crypt.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/git-crypt.hpp -->
# sources/sync-backup/git-crypt/git-crypt.hpp

Purpose: small global header defining the git-crypt version and exposing `argv0` for utility path resolution.

Important APIs/types/functions: `#define VERSION "0.8.0"` and `extern const char* argv0`.

Control flow: no runtime flow. `git-crypt.cpp` initializes `argv0`, and platform utilities read it to determine the executable path.

State/persistence behavior: `argv0` is process-global transient state. No persistent files are touched.

Dependencies/integration: included by CLI and utility code. Version text is used by the CLI and should align with documentation/release assets.

Risks/test signals: version drift between this header, manpage product name, tags, and release asset naming can confuse packaging. Tests should verify `git-crypt --version` output.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/git-crypt.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/gpg.cpp -->
# sources/sync-backup/git-crypt/gpg.cpp

Purpose: GPG command wrapper for looking up public keys, listing secret keys, extracting UIDs, and encrypting/decrypting git-crypt key files.

Important APIs/types/functions: `gpg_get_executable`, `gpg_nth_column`, `gpg_get_uid`, `gpg_lookup_key`, `gpg_list_secret_keys`, `gpg_encrypt_to_file`, and `gpg_decrypt_from_file`.

Control flow: `gpg_get_executable` prefers Git config `gpg.program` and falls back to `gpg`. Lookup/list functions run GPG with `--batch`, `--with-colons`, and fingerprint/list flags, then parse colon-separated records. Encryption runs `gpg --batch`, optionally `--trust-model always`, writes to the target file for a recipient fingerprint, and streams plaintext via stdin. Decryption runs `gpg -q -d` and writes plaintext to an output stream.

State/persistence behavior: persistent output is GPG-encrypted key files written by `gpg_encrypt_to_file`. Other state is subprocess output and parsed fingerprint lists. GPG keyrings and trust databases are external persistent dependencies.

Dependencies/integration: uses `exec_command`, `exec_command_with_input`, `get_git_config`, and `Gpg_error`. `commands.cpp` uses these helpers for `unlock` and `add-gpg-user`.

Risks/test signals: colon output parsing assumes specific GPG record layouts and fingerprint column positions. Trust behavior differs with `--trusted` and user GPG configuration. Tests should cover configured `gpg.program`, no key/multiple key lookup, secret key listing, UID extraction, encryption/decryption round trip, and GPG failure propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/gpg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/gpg.hpp -->
# sources/sync-backup/git-crypt/gpg.hpp

Purpose: declares the GPG integration surface used by git-crypt command logic.

Important APIs/types/functions: `struct Gpg_error`, `gpg_get_uid`, `gpg_lookup_key`, `gpg_list_secret_keys`, `gpg_encrypt_to_file`, and `gpg_decrypt_from_file`.

Control flow: no implementation flow; callers receive vectors of fingerprints or exceptions on unrecoverable GPG failures.

State/persistence behavior: declared functions may read GPG keyrings and write/read encrypted key files, but the header itself has no state.

Dependencies/integration: includes `<string>`, `<vector>`, and `<cstddef>`. Used by `commands.cpp` and caught by `git-crypt.cpp`.

Risks/test signals: API exposes only fingerprints and raw stream encryption/decryption, so higher-level code must validate key names and key file contents. Tests should assert `Gpg_error` messages are surfaced cleanly by the CLI.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/gpg.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/key.cpp -->
# sources/sync-backup/git-crypt/key.cpp

Purpose: serialization, parsing, generation, storage, and validation for git-crypt symmetric key files.

Important APIs/types/functions: `Key_file::Entry` constructor, `load`, `load_legacy`, `store`, `generate`; `Key_file` methods `get_latest`, `get`, `add`, `load_legacy`, `load`, `load_header`, `store`, `load_from_file`, `store_to_file`, `store_to_string`, `generate`, `latest`; and `validate_key_name`.

Control flow: modern key files start with `\0GITCRYPTKEY` plus format version 2, then optional header fields such as key name, an end marker, and one or more entry records. Entry records are field/value encoded with critical odd field IDs causing `Incompatible` and safe even unknown fields skipped within a maximum length. Legacy loading reads one AES key and one HMAC key as version 0 and rejects trailing data. Generation selects version 0 for empty files or latest+1 and fills AES/HMAC keys with random bytes.

State/persistence behavior: `Key_file` stores entries in a descending `std::map` keyed by version and optional key name. `store_to_file` calls `create_protected_file`, writes binary key data, and checks close status. Key bytes are held in memory; constructors zero initialize, but entries are not explicitly wiped on destruction.

Dependencies/integration: uses big-endian helpers, random bytes, explicit memset, protected file creation, and key-name validation. Command handlers load/store internal keys, exported symmetric keys, migrated legacy keys, and GPG-wrapped per-version key files.

Risks/test signals: malformed/incompatible parsing is security-critical. Key-name validation currently dereferences `key_name`, so callers must not pass null except where logic bypasses validation for default keys. Tests should cover modern and legacy round trips, unknown critical/noncritical fields, maximum field lengths, invalid key names, multiple versions ordering, protected file permissions, and malformed/truncated inputs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/key.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/key.hpp -->
# sources/sync-backup/git-crypt/key.hpp

Purpose: declares git-crypt key file structures, constants, exceptions, and key-name validation.

Important APIs/types/functions: constants `HMAC_KEY_LEN`, `AES_KEY_LEN`, and `KEY_NAME_MAX_LEN`; `struct Key_file` with nested `Entry`, exception tags `Malformed` and `Incompatible`, versioned entry map accessors, load/store/generate helpers, key name getters/setters, and `validate_key_name`.

Control flow: no direct implementation flow; the declarations encode the modern key file model of one optional key name and one or more versioned AES/HMAC entries.

State/persistence behavior: `Entry` contains raw AES and HMAC key arrays. `Key_file` owns a version-sorted map and optional key name. Serialized files are binary and versioned.

Dependencies/integration: included by crypto for key-length constants and by command code for key management. `Key_file::Entry` is the bridge between stored key material and encryption commands.

Risks/test signals: public constants are file-format/security contract. Tests should detect accidental changes to key lengths, format version behavior, and named-key validation rules.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/key.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/man/git-crypt.xml -->
# sources/sync-backup/git-crypt/man/git-crypt.xml

Purpose: DocBook XML source for the `git-crypt(1)` manual page.

Important APIs/types/functions: DocBook `refentry` structure with metadata, synopsis sections, command descriptions for `init`, `status`, `add-gpg-user`, `unlock`, `export-key`, `help`, and `version`, usage guidance, `.gitattributes` rules, multiple-key support, and see-also links.

Control flow: documentation flow introduces transparent Git encryption, lists command synopses, describes each command and option, then provides setup/share/unlock workflow and attribute examples.

State/persistence behavior: describes persistent states rather than implementing them: encrypted files in Git history, `.gitattributes` rules, committed `.git-crypt` GPG-encrypted key files, and exported symmetric keys. The generated manpage is produced by the Makefile's `build-man` target.

Dependencies/integration: consumed by `xsltproc` with DocBook XSL to generate `man/man1/git-crypt.1`. It should stay aligned with `git-crypt.cpp` usage/help and `commands.cpp` implemented options.

Risks/test signals: documentation can drift from implementation; notably not all stubbed commands are documented as available. Tests/signals include successful DocBook validation/generation, checking command option parity, and verifying version/date/product metadata during release.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/man/git-crypt.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/parse_options.cpp -->
# sources/sync-backup/git-crypt/parse_options.cpp

Purpose: small option parser for git-crypt subcommands supporting long options, `--name=value`, `--name value`, clustered short flags, short options with attached values, and `--` termination.

Important APIs/types/functions: `find_option` and `parse_options`.

Control flow: `parse_options` walks argv until a non-option or `--`. Long options split at `=`, look up a declared `Option_def`, set boolean flags or consume values, and reject unexpected/missing values. Short option clusters process one character at a time; boolean flags continue through the cluster, while value options consume the rest of the cluster or the next argv and then stop the cluster.

State/persistence behavior: mutates caller-provided bools or `const char**` value slots. It returns the index of the first positional argument. No persistent state.

Dependencies/integration: used by command handlers and `git-crypt.cpp` catches `Option_error` to print command help.

Risks/test signals: parser has no support for optional values or combined long abbreviations. Tests should cover `-abc`, `-kname`, `-k name`, `--key-name=name`, `--key-name name`, `--`, invalid options, missing values, and value supplied to flag-only options.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/parse_options.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/parse_options.hpp -->
# sources/sync-backup/git-crypt/parse_options.hpp

Purpose: declares the lightweight subcommand option parser.

Important APIs/types/functions: `struct Option_def`, `typedef Options_list`, `parse_options`, and `struct Option_error`.

Control flow: headers define option descriptors for either boolean flags or string-valued options. Runtime parsing is implemented in `parse_options.cpp`.

State/persistence behavior: option parsing writes directly into caller-owned variables and returns an argv index. No persistent state.

Dependencies/integration: used throughout command handlers to keep command parsing uniform.

Risks/test signals: `Option_def` can represent only bool or string value options; future option types require extension. Tests should check that thrown `Option_error` includes the right option name and message for CLI reporting.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/parse_options.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/util-unix.cpp -->
# sources/sync-backup/git-crypt/util-unix.cpp

Purpose: Unix/POSIX implementation of platform utility functions used by git-crypt.

Important APIs/types/functions: `System_error::message`, `temp_fstream::open/close`, `mkdir_parent`, `our_exe_path`, `exit_status`, `touch_file`, `remove_file`, `init_std_streams_platform`, `create_protected_file`, `util_rename`, and `get_directory_contents`.

Control flow: temp files are created under `$TMPDIR` or `/tmp` with `mkstemp` under a restrictive umask, opened as `fstream`, immediately unlinked, and closed via RAII. `mkdir_parent` walks slash-separated prefixes and creates missing directories. `our_exe_path` resolves absolute/relative `argv0` with `realpath` where possible. Directory listing skips `.`/`..`, checks `readdir` errors, sorts results, and returns names.

State/persistence behavior: touches mtimes, removes files, creates parent directories, creates protected files with mode 0600, and renames files. Temporary spill files are unlinked after opening and disappear on close.

Dependencies/integration: uses POSIX APIs including `stat`, `mkdir`, `mkstemp`, `umask`, `utimes`, `unlink`, `open`, `rename`, `opendir/readdir`, and wait-status macros. Included by `util.cpp` on non-Windows builds.

Risks/test signals: `realpath(argv0, nullptr)` is not null-checked, so failed relative path resolution could crash. Temp file security and protected key permissions are important. Tests should cover long/missing TMPDIR, nested directory creation, directory listing sort/error handling, `touch_file` on missing files, and protected file mode.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/util-unix.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/util-win32.cpp -->
# sources/sync-backup/git-crypt/util-win32.cpp

Purpose: Windows implementation of platform utility functions used by git-crypt.

Important APIs/types/functions: `System_error::message`, `temp_fstream::open/close`, `mkdir_parent`, `our_exe_path`, `exit_status`, `touch_file`, `remove_file`, `init_std_streams_platform`, `create_protected_file`, `util_rename`, and `get_directory_contents`.

Control flow: error messages use `FormatMessageA`; temp files use `GetTempPath` and `GetTempFileName`, are opened as `fstream`, and deleted on close. `mkdir_parent` creates missing slash-separated prefixes. `our_exe_path` grows a buffer until `GetModuleFileNameA` fits. `touch_file` opens the file for write attributes and sets the last write time. Directory listing uses `FindFirstFileA`/`FindNextFileA`.

State/persistence behavior: sets stdin/stdout to binary mode, touches/removes/renames files, creates directories, and deletes temp files. `create_protected_file` is currently a TODO no-op, so protected key file permissions are not enforced on Windows by this layer.

Dependencies/integration: uses Win32 APIs, MSVCRT `_setmode`, and `unlink`/`rename`. Included by `util.cpp` on Windows builds.

Risks/test signals: the no-op `create_protected_file` is a security gap relative to Unix permissions. Directory listing is not sorted, unlike Unix, which can affect deterministic behavior. Tests should cover binary stdin/stdout, temp file cleanup, rename-over-existing behavior, missing file touch/remove, directory iteration, and key file ACL expectations.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/util-win32.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/util.cpp -->
# sources/sync-backup/git-crypt/util.cpp

Purpose: platform-neutral utility functions for subprocess execution, shell argument quoting, binary integer encoding, explicit memory clearing, constant-time comparison, and stream initialization.

Important APIs/types/functions: `exec_command`, `exec_command` with output capture, `exec_command_with_input`, `escape_shell_arg`, `load_be32`, `store_be32`, `read_be32`, `write_be32`, `explicit_memset`, `leakless_equals`, and `init_std_streams`.

Control flow: command helpers instantiate `Coprocess`, optionally attach stdout/stdin streams, spawn, stream all output or input, close stdin where needed, and wait. Encoding helpers read/write 32-bit big-endian values. `explicit_memset` writes via volatile pointer to avoid optimization. `leakless_equals` accumulates XOR differences across all bytes. Stream initialization disables iostream/stdio sync, unties cin, enables badbit exceptions, and calls platform-specific setup.

State/persistence behavior: subprocess helpers may cause external process side effects. Other utilities only mutate buffers or stream global settings. Platform-specific utilities are included at the bottom based on `_WIN32`.

Dependencies/integration: depends on `Coprocess`, `git-crypt.hpp` for platform utility inclusion needs, iostreams, and selected platform source. Used by nearly every subsystem.

Risks/test signals: `escape_shell_arg` is used for Git config command strings, so quoting semantics matter. `exec_command_with_input` can deadlock if a child writes enough stdout/stderr while input is being written because output is not drained concurrently. Tests should cover command output capture, input delivery, nonzero exit handling, big-endian round trips, constant-time compare behavior at API level, and binary stream mode on Windows.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/util.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-crypt/util.hpp -->
# sources/sync-backup/git-crypt/util.hpp

Purpose: declares common utility and platform abstraction APIs for git-crypt.

Important APIs/types/functions: `struct System_error`, `class temp_fstream`, filesystem helpers `mkdir_parent`, `touch_file`, `remove_file`, `create_protected_file`, `util_rename`, `get_directory_contents`, process helpers `exec_command`, `exec_command_with_input`, `exit_status`, `successful_exit`, stream initialization, shell quoting, big-endian helpers, `explicit_memset`, and `leakless_equals`.

Control flow: no direct implementation flow; this header defines contracts shared by commands, crypto, key handling, GPG, and process wrappers.

State/persistence behavior: declared functions cover filesystem mutations, subprocess side effects, temporary files, stream global settings, and memory clearing.

Dependencies/integration: included broadly across the C++ codebase. Platform-specific behavior is supplied by `util-unix.cpp` or `util-win32.cpp` through `util.cpp`.

Risks/test signals: this is a high-fanout header, so API changes ripple widely. Test signals include platform parity for filesystem/process helpers and correct error messages from `System_error::message`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-crypt/util.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/.github/dependabot.yml -->
# sources/sync-backup/git-lfs/.github/dependabot.yml

Purpose: Dependabot configuration for git-lfs dependency update pull requests.

Important APIs/types/functions: Dependabot `version: 2`; two update entries for `github-actions` at `/` and `gomod` at `/`, both scheduled monthly.

Control flow: Dependabot periodically scans GitHub Actions workflow dependencies and Go module dependencies in the repository root and opens update PRs according to the monthly interval.

State/persistence behavior: no repository runtime state; Dependabot creates external PRs and branch state when updates are available.

Dependencies/integration: integrates with GitHub Dependabot and the repo's GitHub Actions and Go module ecosystem.

Risks/test signals: monthly cadence may batch multiple updates and increase CI/release workflow churn. Signals are successful Dependabot PR creation, CI pass on update PRs, and absence of unsupported ecosystem/directory errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/.github/workflows/ci.yml -->
# sources/sync-backup/git-lfs/.github/workflows/ci.yml

Purpose: comprehensive GitHub Actions CI for git-lfs covering default Go/Git builds, specific Go version, Windows packaging, latest and earliest Git compatibility, and Docker package builds including ARM.

Important APIs/types/functions: trigger `on: [push, pull_request]`, `GOTOOLCHAIN=local`, jobs `build-default`, `build-go`, `build-windows`, `build-latest`, `build-earliest`, `build-docker`, and `build-docker-arm`; Actions `checkout@v6`, `setup-go@v6`, artifact upload, Git for Windows SDK setup, and scripts `script/cibuild`, `script/build-git`, docker build scripts, and Makefile release/package targets.

Control flow: matrix default builds run on Ubuntu and macOS with Go 1.26, run cibuild, build release assets, and upload OS artifacts. A Go 1.25 Ubuntu job checks compatibility. Windows installs Asciidoctor, Go, InnoSetup, Git SDK, builds/test, then creates x86, x64, and arm64 executables plus installer assets. Latest/earliest Git jobs build Git from source on Ubuntu/macOS and run cibuild, with latest also testing SHA-256 repositories. Docker jobs build package containers for x86 and ARM.

State/persistence behavior: CI produces artifacts under `bin/assets`, modifies generated man content during Windows builds, clones Git and build-docker repositories into `$HOME`, and uploads build artifacts. No repo commits are made.

Dependencies/integration: depends on Ruby gems, Go toolchains, GNU gettext/libarchive tools, Chocolatey packages, Git for Windows SDK, external Git source, and git-lfs docker packaging scripts.

Risks/test signals: broad external dependencies make CI sensitive to runner image, Go version, Git source, Chocolatey, and docker image changes. Test signals are matrix pass/fail, uploaded assets per OS, Windows cross-arch binary creation, SHA-256 Git compatibility, earliest Git compatibility, and docker packaging success.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/.github/workflows/release.yml -->
# sources/sync-backup/git-lfs/.github/workflows/release.yml

Purpose: tag-triggered git-lfs release workflow that builds, signs/notarizes, packages, and uploads release artifacts for Windows, macOS, Linux packages, and ARM Linux packages.

Important APIs/types/functions: trigger `push.tags: '*'`, `GOTOOLCHAIN=local`, jobs `build-windows`, `build-macos`, `build-main`, `build-docker`, and `build-docker-arm`; Actions `checkout@v6`, `setup-go@v6`, `download-artifact@v8`, `upload-artifact@v7`, `azure/artifact-signing-action@v2.0.0`, Git for Windows SDK, and Makefile targets for release, Windows staging/signing/rebuild, Darwin release, certificate import, and packagecloud upload.

Control flow: Windows builds zip assets for amd64/386/arm64, stages Windows installer/signing phases, signs stage1 and stage2 executables with Azure code signing, rebuilds release artifacts, and uploads `windows-assets`. macOS builds release assets, writes/imports Developer ID certificate from secrets, runs Darwin release/notarization tooling, and uploads `macos-assets`. Main Linux job downloads Windows/macOS artifacts, builds Linux release assets with `CGO_ENABLED=0`, replaces generated Windows/Darwin assets with signed/notarized ones, and uploads a consolidated `release-assets` bundle. Docker jobs build Linux packages and upload to packagecloud except for pre-release tags; ARM uses `ubuntu-24.04-arm` and arm64 docker targets.

State/persistence behavior: release artifacts are staged under `bin/releases`, temporary signing folders, `release-assets/bin`, and workflow artifacts. Secrets provide signing credentials, macOS certificates, notarization credentials, and packagecloud token. Package upload persists externally to packagecloud for non-pre-releases.

Dependencies/integration: integrates GitHub Actions environments, Go, Ruby/asciidoctor/packagecloud gems, Chocolatey, InnoSetup, jq, zip, Git for Windows SDK, Azure code signing, Apple signing/notarization, docker packaging repositories, and project Makefile/script release targets.

Risks/test signals: high-risk areas are secret availability, signing endpoint configuration, certificate import, artifact name/path conventions, cross-job artifact replacement, pre-release tag shell condition, and ARM runner availability. Tests/signals include signed executable validation, notarization success, expected artifact set in `release-assets`, packagecloud dry-run or controlled release, and reproducible `git describe` from full-depth checkout.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/.github/workflows/release.yml -->
