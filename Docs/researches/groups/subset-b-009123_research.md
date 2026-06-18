# subset-b-009123 Research

Grouped research report for the requested git-annex support, packaging, example protocol, standalone wrapper, and vendored JavaScript files.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/Utility/libkqueue.c -->
# sources/sync-backup/git-annex/Utility/libkqueue.c

Purpose: a tiny BSD kqueue C helper library used by git-annex code that wants a minimal file-descriptor change notification interface. It watches vnode write events on already-open file descriptors and exposes a small C ABI rather than requiring the caller to manage `struct kevent` setup directly.

Important APIs and functions: `helper(kq, fdcnt, fdlist, nodelay)` builds a variable-length `struct kevent chlist[fdcnt]`, registers each supplied descriptor with `EVFILT_VNODE`, `EV_ADD | EV_ENABLE | EV_CLEAR`, and `NOTE_WRITE`, then calls `kevent`. `init_kqueue()` creates the queue with `kqueue()` and exits after `perror` on failure. `addfds_kqueue()` registers descriptors by calling `helper` with a zero timeout. `waitchange_kqueue()` blocks by calling `helper` with no changelist and no timeout.

Control flow: callers first call `init_kqueue`, call `addfds_kqueue` one or more times to add descriptors, then call `waitchange_kqueue` to receive the changed descriptor identifier. `helper` returns `evlist[0].ident` only when exactly one event is returned; zero events, errors, and unexpected multi-event results collapse to `-1`.

State and persistence: watched descriptors are held by the kernel kqueue across calls; the C file has no heap allocations or persistent user-space state. File descriptor lifetime remains owned by the caller.

Dependencies and integration points: BSD/macOS kernel APIs from `<sys/event.h>` and `<sys/time.h>`, plus standard C/POSIX headers. The Haskell or C FFI side is expected to link this file and use the ABI declared in `libkqueue.h`.

Risks: `struct kevent chlist[fdcnt]` is a C99 variable-length stack allocation and does not handle negative or very large counts defensively. `helper` ignores `errno` and conflates timeout/no event with real errors. It only watches `NOTE_WRITE`, so rename/delete/attribute changes are outside this helper's scope. `init_kqueue` terminates the process on failure instead of returning an error code.

Test signals: useful tests should exercise kqueue creation, registering a directory or file descriptor, detecting a write, timeout behavior from `addfds_kqueue`, and handling closed descriptors. Platform tests must be limited to systems with kqueue support.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/Utility/libkqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/Utility/libkqueue.h -->
# sources/sync-backup/git-annex/Utility/libkqueue.h

Purpose: public C header for the small kqueue helper library in `libkqueue.c`.

Important APIs and types: declares `int init_kqueue();`, `void addfds_kqueue(const int kq, const int fdcnt, const int *fdlist);`, and `signed int waitchange_kqueue(const int kq);`. No structs, enums, or macros are exported, keeping the ABI intentionally narrow.

Control flow and state: this header describes a create/register/wait lifecycle. It exposes the kqueue file descriptor as an integer and leaves descriptor ownership and cleanup to callers.

Dependencies and integration points: no includes are present, so consumers do not get system declarations from this header. It is intended for local compilation with `libkqueue.c` and FFI consumers that only need function signatures.

Risks: the prototypes use old-style empty parameter lists for `init_kqueue()` rather than `void`, which is tolerated by C but less strict. There is no declaration for closing the kqueue or reporting detailed errors.

Test signals: compile tests should include the header from C and any FFI binding, link with `libkqueue.c`, and validate that the declared ABI matches the implementation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/Utility/libkqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/bash-completion.bash -->
# sources/sync-backup/git-annex/bash-completion.bash

Purpose: Bash completion adapter that delegates completion generation to `git-annex` itself, avoiding a static list of commands or options.

Important functions: `_git-annex` builds `CMDLINE` with `--bash-completion-index $COMP_CWORD` and one `--bash-completion-word` per `COMP_WORDS` entry, then sets `COMPREPLY` from `git-annex` output. `_git_annex` adapts Git's `git annex` completion callback to the standalone `git-annex` command by replacing the first `git`/`annex` pair with a synthetic `git-annex` completion word and reducing the completion index by one.

Control flow: direct `git-annex` completion is registered via `complete -o bashdefault -o default -o filenames -F _git-annex git-annex`. Git's own completion can call `_git_annex` for `git annex`; that path preserves filename completion behavior using `compopt -o filenames +o nospace` with a compatibility fallback.

State and persistence: no durable state; it depends on Bash's `COMP_WORDS`, `COMP_CWORD`, `COMPREPLY`, and local arrays.

Dependencies and integration points: requires Bash completion semantics and a runnable `git-annex` in `PATH`. It integrates with the internal `git-annex --bash-completion-*` protocol and optionally with `git-completion.bash`.

Risks: array expansions are unquoted, so arguments containing whitespace can be split before being passed to `git-annex`. Completion behavior depends on `git-annex` being fast enough for interactive shell use. `compopt` is Bash-specific and guarded only by a fallback command chain.

Test signals: source the script in Bash, verify `git-annex <TAB>` and `git annex <TAB>` completions, include filenames with spaces, and check behavior when `git-annex` is missing or slow.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/bash-completion.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/debian/create-standalone-changelog -->
# sources/sync-backup/git-annex/debian/create-standalone-changelog

Purpose: Debian helper script for generating a NeuroDebian changelog entry for a standalone git-annex package snapshot.

Important operations: runs with `set -eu`, sets `umask 022`, derives `ANNEX_VERSION` from `git describe HEAD`, transforms it into `ANNEX_NDVERSION` by replacing the first dash with `+git` and appending `-1~ndall+1`, then invokes `dch` with forced version/distribution flags and message `Backported fresh snapshot`.

Control flow and state: the script must run inside the git-annex repository so `git describe HEAD` has meaningful tag context. It mutates Debian changelog state through `dch`; no other files are directly written by the script.

Dependencies and integration points: depends on Git, Debian `devscripts`/`dch`, a usable `debian/changelog`, and NeuroDebian package versioning expectations.

Risks: unquoted variable expansions in the `sed` pipeline and `dch` call are acceptable for typical Git describe values but not robust for pathological tag strings. `--force-bad-version` and `--force-distribution` bypass safeguards, so caller discipline matters.

Test signals: run in a throwaway checkout with known tag layouts, inspect the resulting changelog version sort order, and verify failure when outside a Git repository.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/debian/create-standalone-changelog -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/debian/rules -->
# sources/sync-backup/git-annex/debian/rules

Purpose: Debian debhelper rules file for building either the normal package path or a `git-annex-standalone` package variant.

Important variables and targets: exports `BUILDER=./Setup`, `BUILDEROPTIONS=-j1` for reproducible builds, `RELEASE_BUILD=1` to use the changelog version, and `ZSH_COMPLETIONS_PATH`. `STANDALONE_BUILD` is computed by grepping `debian/control` for `Package: git-annex-standalone`. The generic `%:` target delegates to `dh $@`.

Standalone control flow: when `STANDALONE_BUILD=1`, `override_dh_auto_build` runs `make linuxstandalone GIT_ANNEX_PACKAGE_INSTALL=1`; `override_dh_auto_install` runs desktop, docs, and completions install targets into `debian/git-annex-standalone`; `override_dh_fixperms` excludes `ld-linux`; `override_dh_strip` suppresses automatic debug symbols; and `override_dh_makeshlibs` disables maintainer scripts/triggers for private bundled libraries.

State and persistence: produces Debian build artifacts under debhelper-managed directories and package staging roots. It does not persist runtime state.

Dependencies and integration points: debhelper, GNU make, git-annex's `Makefile`, Haskell `Setup`, Debian control metadata, and package split definitions in `debian/install`/`debian/links`.

Risks: package behavior hinges on the grep result from `debian/control`, so control file formatting changes can alter the branch. `-j1` improves reproducibility at build-time cost. Standalone builds deliberately bundle private libraries and skip normal shared-library integration.

Test signals: `dpkg-buildpackage` for both control configurations, check reproducible-build diffs, inspect standalone package contents/permissions, and verify no unwanted `ldconfig` trigger or dbgsym package is generated.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/debian/rules -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/debian/tests/basics -->
# sources/sync-backup/git-annex/debian/tests/basics

Purpose: autopkgtest smoke test for the Debian package.

Control flow: creates a temporary directory with `mktemp -d`, changes into it, and `exec`s `git-annex test`. Using `exec` makes the test process become the git-annex test command, so its exit code is the autopkgtest result.

State and persistence: the temporary directory is not explicitly removed because the process is replaced by `git-annex test`; cleanup depends on the test harness or filesystem policy.

Dependencies and integration points: requires `/bin/sh`, `mktemp`, a working packaged `git-annex`, and any runtime dependencies needed by the built-in test suite.

Risks: no trap cleanup and no environment isolation beyond a temp working directory. Failures can come from broad git-annex test dependencies rather than only package installation problems.

Test signals: passing autopkgtest is a high-level package health signal. Additional checks could assert the temp directory location and ensure required tools are in `PATH`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/debian/tests/basics -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/design/external_backend_protocol/git-annex-backend-XFOO -->
# sources/sync-backup/git-annex/doc/design/external_backend_protocol/git-annex-backend-XFOO

Purpose: executable demonstration of the external backend protocol for generating and verifying git-annex keys. It implements a toy `XFOO` backend using MD5 and file size.

Important functions and protocol messages: `hashfile` runs `md5sum` and extracts the digest. The main loop responds to `GETVERSION` with `VERSION 1`, `CANVERIFY` with yes, `ISSTABLE` with yes, and `ISCRYPTOGRAPHICALLYSECURE` with no. `GENKEY contentfile` emits `GENKEY-SUCCESS XFOO-s<size>--<md5>` or failure. `VERIFYKEYCONTENT key contentfile` recomputes the MD5 and compares it to the suffix after `--`.

Control flow: the script reads line-oriented requests from stdin, splits with `set -- $line`, switches on the first word, and writes one protocol response to stdout. Unknown requests emit `ERROR protocol error`.

State and persistence: stateless; all derived state comes from the requested content file and key string.

Dependencies and integration points: POSIX shell, `md5sum`, `wc`, `cut`, and `sed`. It must be installed in `PATH` as `git-annex-backend-XFOO` for git-annex to discover the backend.

Risks: MD5 is explicitly non-cryptographic and the script says so. Shell word splitting makes paths with whitespace unsafe. Verification only compares the hash suffix, not the embedded size. `set -e` can terminate the backend on unexpected command failures.

Test signals: protocol tests should send each command, verify exact response tokens, use files with known MD5/size, check invalid keys, and include filenames with spaces to document limitations.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/design/external_backend_protocol/git-annex-backend-XFOO -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/install/Android/git-annex-install -->
# sources/sync-backup/git-annex/doc/install/Android/git-annex-install

Purpose: convenience installer intended to be sourced in a Termux shell on Android, installing the appropriate git-annex standalone tarball and updating the current shell `PATH`.

Important control flow: maps `uname -m` to standalone architecture names (`arm64-ancient`, `armel`, `amd64`, `i386`), builds a download URL under `https://downloads.kitenet.net/git-annex/linux/current/`, installs Termux dependencies with `pkg install git wget tar coreutils proot`, downloads and extracts the tarball in `$HOME`, runs `git-annex.linux/git-annex version` to let `runshell` finish adaptation, calls `termux-setup-storage`, and appends the extracted directory to `PATH`.

State and persistence: writes/extracts `~/git-annex.linux`, installs Termux packages, may trigger storage permission setup, and mutates the current shell's `PATH` because it is meant to be sourced.

Dependencies and integration points: Termux `pkg`, `wget`, `tar`, `proot`, Android architecture naming, and the standalone bundle's Android-aware `runshell`.

Risks: piping `wget -O-` directly to `tar zx` has no checksum verification. The `x86_32` case is probably not a common `uname -m` value. Re-running can overlay an existing extracted tree. Because it should be sourced, executing it in a subshell loses the final `PATH` change.

Test signals: test architecture mapping under Termux, dependency install behavior, extraction of the correct tarball, `git-annex version` success, and immediate command availability after sourcing.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/install/Android/git-annex-install -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-imageconvert -->
# sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-imageconvert

Purpose: git-annex compute remote program that uses ImageMagick `convert` to transform an input image into an output image requested by git-annex.

Important protocol behavior: validates two command-line arguments, prints `INPUT <arg1>` and reads the provided local input path, prints `OUTPUT <arg2>` and reads the output path, then runs `convert "$input" "$output"` when an input path was supplied. Conversion diagnostics are redirected to stderr to avoid corrupting stdout protocol messages.

Control flow and state: single transaction, no loop, no durable state. The compute remote protocol supplies concrete temporary paths in response to `INPUT`/`OUTPUT`.

Dependencies and integration points: POSIX shell, git-annex compute remote protocol, and ImageMagick's `convert` executable.

Risks: no explicit success/failure protocol response beyond process exit. It trusts ImageMagick to handle untrusted image data, which historically has had parser vulnerabilities. Missing input quietly skips conversion and exits successfully.

Test signals: run under git-annex compute with a known JPEG-to-GIF conversion, verify output content, check missing arguments, absent `convert`, and malicious/invalid input handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-imageconvert -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-singularity -->
# sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-singularity

Purpose: git-annex compute remote program for running Singularity containers whose image and inputs are stored in the annex.

Important functions and options: `run_singularity` invokes `singularity run --net --network=none --oci --bind="$binddir" --pwd="$rundir"` with optional `--no-compat` and `--fakeroot`. `strip_escape` removes ESC bytes from container output before forwarding to stderr. The argument parser uses `--` separators for stages: container/options/inputs, outputs, and command parameters.

Control flow: without `ANNEX_COMPUTE_passthrough`, the script requests each stage-1 non-option as `INPUT`, hard-links the resolved input into the current sandbox path, treats the first input as the container, requests stage-2 paths as `OUTPUT`, then runs Singularity with remaining arguments and stdin closed. With passthrough enabled, it asks git-annex for `SANDBOX`, binds the sandbox top, requires the passthrough container path through `INPUT-REQUIRED`, and lets stdio pass through to a command inside the container.

State and persistence: creates directories and hard links in the working sandbox. It does not persist configuration, but it depends on git-annex-provided sandbox paths and environment variables.

Dependencies and integration points: Bash, Singularity, `realpath`, process substitution, git-annex compute protocol, and host support for OCI/process namespaces.

Risks: hard-linking requires compatible filesystems and can fail across devices. Network disabling is helpful but not a complete sandbox policy; bind mounts expose the sandbox tree. It only strips ESC characters, not all terminal control sequences. `--fakeroot` broadens behavior and depends on host configuration.

Test signals: exercise normal and passthrough modes, multiple input/output stages, missing container failures, network isolation, stderr sanitization, and hard-link behavior across filesystems.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-singularity -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-wasmedge -->
# sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-wasmedge

Purpose: git-annex compute remote program that runs WebAssembly binaries from the annex using WasmEdge.

Important protocol behavior: requires at least one argument, parses inputs before the first `--`, outputs before the second `--`, and remaining values as WasmEdge arguments. Each input is requested with `INPUT`, symlinked into the working directory, and the first input becomes the wasm program. Each output is requested with `OUTPUT`.

Control flow and execution: after staging, runs `wasmedge --dir "/:<pwd>" --force-interpreter -- "$wasm" "$@"` with stdin closed and stdout/stderr discarded. `--force-interpreter` avoids ahead-of-time native execution for untrusted WASM.

State and persistence: creates directories and symlinks in the sandbox. Output files are expected to be written by the WASM program to paths supplied by git-annex.

Dependencies and integration points: POSIX shell, `realpath`, WasmEdge, and the git-annex compute remote protocol.

Risks: symlink creation uses unquoted `$(realpath "$input")`, which can break on whitespace or glob characters. Discarding stderr makes debugging hard. The sandbox depends on WasmEdge's directory preopen enforcement.

Test signals: run a deterministic WASM program through git-annex compute, verify output registration, check missing wasm, names with spaces, and ensure AOT/native execution is not used.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-wasmedge -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/external/example.sh -->
# sources/sync-backup/git-annex/doc/special_remotes/external/example.sh

Purpose: full shell example of a git-annex external special remote, modeled on the built-in directory remote and demonstrating configuration, credentials, transfer, presence, removal, export, rename, and info protocol messages.

Important functions: `runcmd` redirects command stdout to stderr to preserve the line protocol. `ask`, `getconfig`, and `setconfig` implement synchronous protocol queries. `calclocation` asks git-annex for `DIRHASH` and stores keys under `$mydirectory/$RET/$key`. `setupcreds` and `getcreds` demonstrate `SETCREDS`/`GETCREDS`. `dostore`, `doretrieve`, `docheckpresent`, and `doremove` implement object operations with protocol success/failure responses.

Control flow: emits `VERSION 2`, then loops over stdin. `LISTCONFIGS` advertises `directory`. `INITREMOTE` resolves and stores an absolute directory, creates it, and records credentials. `PREPARE` retrieves credentials and configuration before normal use. `TRANSFER STORE` writes via a temp file under `$mydirectory/tmp` then atomically moves into place. `TRANSFER RETRIEVE`, `CHECKPRESENT`, and `REMOVE` operate by key-derived locations. Export requests use an `exportlocation` set by `EXPORT` and implement transfer, presence, removal, directory removal, and rename semantics.

State and persistence: persistent state is the configured storage directory, files stored under hashed key paths, export paths, and git-annex-managed credentials/config. Runtime variables include `mydirectory`, `LOC`, `RET`, and `exportlocation`.

Dependencies and integration points: POSIX shell plus common tools (`readlink`, `sed`, `cp`, `mv`, `rm`, `mkdir`, `dirname`). It must be installed as `git-annex-remote-directory` or another external type name and is driven entirely by git-annex's external special remote protocol.

Risks: `set -- $line` and many unquoted protocol fields cannot safely represent all filenames/keys with whitespace, though later `file="$@"` mitigates some transfer path cases. `rmdir "$mydirectory/tmp"` can fail if concurrent transfers share the same temp directory. `REMOVEEXPORTDIRECTORY` checks `[ ! -d "$dir" ]` instead of `$mydirectory/$dir`, which is a path confusion risk in the example. Credential demo intentionally requires environment variables during initremote.

Test signals: protocol transcript tests for every request, idempotent `INITREMOTE`, store/retrieve/remove round trips, unavailable-directory `CHECKPRESENT-UNKNOWN`, export store/retrieve/rename/remove, and concurrent transfer behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/external/example.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/external/git-annex-remote-ipfs -->
# sources/sync-backup/git-annex/doc/special_remotes/external/git-annex-remote-ipfs

Purpose: experimental external special remote that stores git-annex content in IPFS and tracks IPFS addresses as git-annex URLs.

Important functions: `isipfsurl` recognizes `ipfs:` URLs, `urltoaddress` strips the prefix, `addresstourl` adds it, `getvalue` parses protocol `VALUE` responses, and `getaddrs` asks git-annex for all URLs for a key and writes matching IPFS URLs to a temp file.

Control flow: emits `VERSION 2`. `INITREMOTE` and `PREPARE` always succeed. `CLAIMURL` accepts only `ipfs:` URLs. `CHECKURL` returns `CHECKURL-CONTENTS UNKNOWN <address>`. `TRANSFER STORE` runs `ipfs add -q`, then emits `SETURIPRESENT` and transfer success. `TRANSFER RETRIEVE` retrieves known IPFS URLs with `GETURLS`, selects the first, and runs `ipfs get --output="$file"`. `CHECKPRESENT` always reports failure, and `REMOVE` reports failure because IPFS content cannot be removed remotely.

State and persistence: no local configuration is persisted by the script. Durable availability is delegated to the user's IPFS node/network and git-annex URL records.

Dependencies and integration points: POSIX shell, `ipfs`, `egrep`, `sed`, `mktemp`, `head`, and git-annex external special remote protocol.

Risks: presence checking is intentionally weak and always says the key is not present. Retrieval picks only the first known IPFS URL. `ipfs get --output="$file"` behavior depends on IPFS client semantics and may create directories for some CIDs. No pinning or garbage-collection policy is managed here.

Test signals: store a file and confirm `SETURIPRESENT`, retrieve from recorded `ipfs:` URL, reject non-IPFS URLs, handle absent `ipfs`, and verify remove/presence responses match the protocol.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/external/git-annex-remote-ipfs -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/external/git-annex-remote-torrent -->
# sources/sync-backup/git-annex/doc/special_remotes/external/git-annex-remote-torrent

Purpose: demonstration external special remote that downloads content from torrent URLs using `aria2c`, with support for single-file and multi-file torrent metadata.

Important functions: `runcmd` preserves stdout protocol cleanliness. `getvalue` and `geturls` retrieve known torrent URLs for a key. `istorrent` matches URLs ending in `.torrent` plus optional `#N` file selector. `downloadtorrent` creates a temp directory, uses `btshowmetainfo` to discover wanted file paths, runs `aria2c`, moves the selected file to the requested destination, and removes temp state.

Control flow: emits `VERSION 2`. `INITREMOTE` and `PREPARE` succeed. `CLAIMURL` accepts torrent URLs. `CHECKURL` downloads a torrent file with restricted curl protocols, inspects metadata, and emits `CHECKURL-MULTI` entries for each file or a single entry. `TRANSFER STORE` is unsupported. `TRANSFER RETRIEVE` selects a known torrent URL, downloads the `.torrent`, derives the selected file number, downloads content, and reports success or failure. `CHECKPRESENT` reports unknown. `REMOVE` emits `SETURLMISSING` for all known torrent URLs and succeeds.

State and persistence: transient temp files and directories are created for torrent metadata and downloads. Persistent state is only the git-annex URL metadata modified by `SETURLMISSING`.

Dependencies and integration points: POSIX shell, `curl`, `aria2c`, `btshowmetainfo`, `mktemp`, `grep`/`egrep`, `sed`, `expr`, and git-annex's external special remote URL protocol.

Risks: no resume support and no progress reporting. Multi-file torrent parsing assumes `btshowmetainfo` output and normalizes spaces to underscores in `CHECKURL-MULTI`, so exact names with spaces are lossy. The `filenum` extraction uses a sed pattern that appears to use `\d`, which is not portable POSIX sed and may fail to extract the fragment. Torrent downloads can fetch extra pieces/files.

Test signals: use fixture torrent metadata for single and multi-file cases, test `CHECKURL-MULTI`, retrieve a selected file, reject upload, remove URL metadata, and exercise filenames with spaces and failed downloads.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/external/git-annex-remote-torrent -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/p2p/git-annex-p2p-iroh -->
# sources/sync-backup/git-annex/doc/special_remotes/p2p/git-annex-p2p-iroh

Purpose: P2P transport adapter that lets git-annex use Iroh's `dumbpipe` for peer-to-peer connections.

Important behavior: resolves the repository git dir, stores a secret at `$git_dir/annex/creds/iroh-secret`, and exports it as `IROH_SECRET` for dumbpipe. In `address` mode it creates the credential directory, generates 32 random bytes with `gpg --gen-random 16 32` under `umask 077` if needed, then runs `dumbpipe generate-ticket`. In connect mode, if no socket file is supplied, it runs `dumbpipe connect <peeraddress>`. In listen mode, it loads the secret and runs `dumbpipe listen-unix --socket-path=<socketfile>`.

State and persistence: persists the Iroh secret inside `.git/annex/creds` so the node identity/ticket remains stable. Runtime state is delegated to dumbpipe sockets and network sessions.

Dependencies and integration points: `git rev-parse --git-dir`, `gpg`, `dumbpipe` version 0.33 or newer with `generate-ticket`, and git-annex's P2P transport program interface.

Risks: the secret file redirection is unquoted, so unusual repository paths could break. Secret generation depends on GPG availability. The script suppresses stderr only while generating the ticket to avoid secret display but otherwise delegates security to dumbpipe.

Test signals: address generation creates a 0600-style secret, repeated address calls reuse it, connect mode relays stdio, listen mode binds the provided Unix socket, and missing dumbpipe/GPG errors are visible.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/p2p/git-annex-p2p-iroh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/p2p/git-annex-p2p-unix-sockets -->
# sources/sync-backup/git-annex/doc/special_remotes/p2p/git-annex-p2p-unix-sockets

Purpose: example P2P transport program that simulates a multi-node network by mapping peer addresses to Unix socket files under `/tmp`.

Control flow: in `address` mode, prints the current Unix timestamp as a mock local address. In connect mode with only a peer address, runs `socat - UNIX-CONNECT:/tmp/<peeraddress>` to relay stdin/stdout. In listen mode with a socket file, symlinks the real socket path to `/tmp/<myaddress>`.

State and persistence: creates or overwrites symlinks in `/tmp`. Addresses are timestamp-based and not stable across invocations.

Dependencies and integration points: POSIX shell, `date`, `realpath`, `ln`, `socat`, and the git-annex P2P transport interface.

Risks: predictable `/tmp` names and symlink replacement are insecure for real deployments; the file is explicitly a demo. Address collisions are possible for invocations in the same second. No cleanup of `/tmp` symlinks is performed.

Test signals: run address/listen/connect flows locally, verify data relays over the socket, test repeated address generation and stale symlink behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/p2p/git-annex-p2p-unix-sockets -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/tips/automatically_adding_metadata/pre-commit-annex -->
# sources/sync-backup/git-annex/doc/tips/automatically_adding_metadata/pre-commit-annex

Purpose: optional hook/helper for extracting media metadata and storing selected fields as git-annex metadata during commits or manual refreshes.

Important configuration and functions: reads `metadata.tool` with default `extract`, `metadata.extract`, `metadata.exiftool`, and `metadata.overwrite`. `addmeta(file, field, value)` converts spaces in field names to underscores and calls `git -c annex.alwayscommit=false annex metadata --set "$field?=$value"` or `=` when overwrite is enabled. `process` runs configured tools against each file, filters output with the configured field regex, parses either `extract`'s `field - value` or exiftool's `field: value`, and calls `addmeta`.

Control flow: exits immediately if no extract fields/tools are configured. Determines diff base as `HEAD` or the empty tree for an initial commit. If arguments are passed, processes those files; otherwise processes staged file names from `git diff-index -z --name-only --cached`, converting NULs to newlines.

State and persistence: mutates git-annex metadata for files and can stage/record annex metadata changes depending on git-annex behavior. No separate state is written.

Dependencies and integration points: Git config, `git annex metadata`, optional `extract` and `exiftool`, `egrep`, `sed`, and pre-commit hook conventions.

Risks: converting NUL-delimited file names to newlines breaks filenames containing newlines. The pipeline uses `eval egrep` with config-derived regex text, which is powerful but risky if untrusted config is present. Tool output parsing is format-specific. Repeated hook runs can be expensive on large files.

Test signals: configure extract/exiftool fields, run against staged and explicit files, test overwrite true/false, initial commit path, missing tools, and filenames with spaces/newlines.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/tips/automatically_adding_metadata/pre-commit-annex -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/tips/dumb_metadata_extraction_from_xbmc/git-annex-xbmc-playcount.pl -->
# sources/sync-backup/git-annex/doc/tips/dumb_metadata_extraction_from_xbmc/git-annex-xbmc-playcount.pl

Purpose: Perl helper that reads XBMC/Kodi video database play counts and writes them to git-annex metadata as `playCount=<count>`.

Important functions: `checkargs` parses `--annex`, `--path`, `--home`, `--dryrun`, and `--verbose` with `Getopt::Long` and uses `Pod::Usage` for help. `finddb(path)` scans for `MyVideos*.db` and returns the newest by modification time. `checkdb` runs a SQLite query joining `movie`, `files`, and `path`, parses `playCount|strPath|strFileName` rows, handles `stack://` multi-file entries, strips the configured annex prefix, and either prints or executes `git annex metadata --set playCount=<count> <file>`.

Control flow: `main` resolves the database directory, finds a database, and processes every movie row. Dry-run mode prints shell-like commands instead of invoking git-annex.

State and persistence: writes git-annex metadata when not in dry-run mode. It reads the XBMC SQLite DB through the `sqlite3` command and does not modify the DB.

Dependencies and integration points: Perl, `Getopt::Long`, `Pod::Usage`, external `sqlite3`, `git annex metadata`, XBMC/Kodi database schema, and repository-relative path conventions.

Risks: the SQL output is parsed by splitting on `|`, and the POD explicitly notes filenames containing pipes can break parsing. `finddb` returns no database when exactly one file is found because it checks `$#flist > 0`, which requires at least two entries; this looks like a bug. Paths are manipulated with regex substitutions using the `--annex` value, which can behave unexpectedly if it contains regex metacharacters. System command exit codes are not checked.

Test signals: unit-test `finddb` with one and multiple DB files, dry-run against a fixture SQLite database, stacked and non-stacked paths, paths containing pipes/spaces, and nonzero git-annex failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/tips/dumb_metadata_extraction_from_xbmc/git-annex-xbmc-playcount.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/tips/transmission_integration/transmission_integration.sh -->
# sources/sync-backup/git-annex/doc/tips/transmission_integration/transmission_integration.sh

Purpose: Transmission completion hook example that adds a finished torrent download to git-annex and commits it with a message containing Transmission environment details.

Control flow: `set -e`, verifies `TR_APP_VERSION` is set, builds a multiline commit message from `TR_APP_VERSION`, `TR_TIME_LOCALTIME`, `TR_TORRENT_DIR`, `TR_TORRENT_HASH`, `TR_TORRENT_ID`, and `TR_TORRENT_NAME`, prints it, changes to `$TR_TORRENT_DIR`, runs `git annex add "$TR_TORRENT_NAME"`, and commits with `git commit -F-` using the same message.

State and persistence: mutates the git-annex repository in the torrent directory by adding content and creating a Git commit.

Dependencies and integration points: Transmission script environment, Git, git-annex, and a repository rooted at or above `TR_TORRENT_DIR`.

Risks: the error message for missing `TR_APP_VERSION` expands the empty value rather than naming the variable. No locking is used, so concurrent torrent completions can race on the same repository. It assumes torrent name maps directly to a path under the torrent directory.

Test signals: run with a mocked Transmission environment in a temporary annex repo, verify add/commit, missing variable failure, duplicate/concurrent invocation behavior, and torrent names with spaces.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/tips/transmission_integration/transmission_integration.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/stack-botan.yaml -->
# sources/sync-backup/git-annex/stack-botan.yaml

Purpose: Stack build configuration for git-annex with Botan crypto support enabled.

Important settings: sets `git-annex` flags for production, parallelbuild, assistant, torrentparser, benchmark, ospath, and `botan: true`; disables magicmime, dbus, debuglocks. Sets `file-io` `os-string: true`. Uses package `'.'`, resolver `lts-24.26`, and extra deps `aws-0.25.2`, `file-io-0.2.0`, `botan-low-0.2.0.1`, and `botan-bindings-0.3.0.0`.

Control flow and state: declarative Stack configuration consumed by `stack build`; it affects dependency solving and Cabal flags but has no runtime state.

Dependencies and integration points: Haskell Stack, Stackage LTS 24.26, local git-annex Cabal flags, and Botan Haskell bindings/native Botan availability.

Risks: Botan deps can require compatible system libraries/headers. Divergence from `stack.yaml` is only the Botan flag/deps, so both files must stay aligned when resolver or shared deps change.

Test signals: `stack build --stack-yaml stack-botan.yaml`, inspect configured Cabal flags, and run crypto-related tests that require Botan.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/stack-botan.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/stack.yaml -->
# sources/sync-backup/git-annex/stack.yaml

Purpose: default Stack build configuration for git-annex without Botan support.

Important settings: enables production, parallelbuild, assistant, torrentparser, benchmark, and ospath flags; disables magicmime, dbus, debuglocks, and `botan`. Sets `file-io` `os-string: true`, uses local package `'.'`, resolver `lts-24.26`, and extra deps `aws-0.25.2` and `file-io-0.2.0`.

Control flow and state: declarative input to Stack's solver/build process, with no persisted runtime state aside from Stack build caches.

Dependencies and integration points: Stack, Stackage LTS 24.26, git-annex's Cabal flags, and the listed extra deps.

Risks: resolver pinning stabilizes builds but needs maintenance for security/compiler updates. The disabled `magicmime`/`dbus` flags exclude optional integrations from this build profile.

Test signals: `stack build`, `stack test` if supported, and verification that Cabal flags match expected default build features.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/stack.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git -->
# sources/sync-backup/git-annex/standalone/linux/skel/git

Purpose: Linux standalone launcher for bundled `git`.

Control flow: resolves the launcher path with `readlink -f "$0"` falling back to `readlink "$0"`, derives `base`, verifies `base` and `base/runshell`, canonicalizes `base` through `cd`/`pwd`, then `exec`s `"$base/runshell" git "$@"`.

State and dependencies: no persistent state; depends on POSIX shell, `readlink`, `dirname`, and the co-located `runshell`.

Integration points and risks: this wrapper ensures git runs inside the standalone environment established by `runshell`. It fails fast with diagnostic messages when moved away from its skeleton. Symlink and path behavior depends on platform `readlink` semantics.

Test signals: invoke through real path and symlink, move/copy without `runshell` to check failure, and verify bundled git is first in the environment.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-annex -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-annex

Purpose: Linux standalone launcher for the bundled `git-annex` command.

Control flow and APIs: identical base resolution and validation pattern to the other Linux skeleton launchers, ending with `exec "$base/runshell" git-annex "$@"`.

State and dependencies: no durable state in the wrapper; all environment setup is delegated to `runshell`.

Integration points and risks: primary user entry point for the standalone bundle. If path canonicalization fails or `runshell` is missing, it exits before invoking git-annex. Behavior with unusual symlink chains depends on `readlink -f`.

Test signals: execute `git-annex version` through the wrapper, test symlinked installation paths, and verify arguments are preserved.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-annex -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-annex-shell -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-annex-shell

Purpose: Linux standalone launcher for `git-annex-shell`, used by SSH and remote repository access.

Control flow: resolves the wrapper base, validates `runshell`, canonicalizes the directory, and executes `"$base/runshell" git-annex-shell "$@"`.

State and integration: stateless itself, but it relies on `runshell` to install SSH helper shims and set bundled paths/libraries. It is a security-sensitive entry point because it may process SSH-original commands.

Risks: wrapper correctness depends on preserving all arguments exactly; this script quotes `"$@"`. Missing or tampered `runshell` prevents operation.

Test signals: call directly and through an SSH forced-command shim, verify command argument forwarding, and check failure diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-annex-shell -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-annex-webapp -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-annex-webapp

Purpose: Linux standalone launcher for `git-annex webapp`.

Control flow: same base resolution as other Linux skeleton wrappers, then `exec "$base/runshell" git-annex webapp "$@"`.

State and integration: delegates environment setup and any app-base behavior to `runshell`. Runtime persistence belongs to git-annex webapp, not the wrapper.

Risks: unlike the macOS wrapper, this one runs in the foreground via `exec`. A missing `runshell` or wrong bundle layout prevents launch.

Test signals: invoke webapp with help/version-style arguments where possible, verify foreground behavior, and confirm bundled environment variables are set.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-annex-webapp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-receive-pack -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-receive-pack

Purpose: Linux standalone launcher for bundled `git-receive-pack`, allowing Git smart protocol operations to use bundled Git.

Control flow: resolves and canonicalizes the skeleton base, validates `runshell`, then `exec "$base/runshell" git-receive-pack "$@"`.

State and integration: stateless wrapper used by remote Git transports and SSH commands. Environment setup is centralized in `runshell`.

Risks: remote protocol correctness depends on stdout/stderr behavior of the underlying command; wrapper diagnostics only happen before exec. Path resolution is the main failure surface.

Test signals: run `git receive-pack` protocol smoke tests through the wrapper against a temporary repository.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-receive-pack -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-remote-annex -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-remote-annex

Purpose: Linux standalone launcher for the `git-remote-annex` transport helper.

Control flow: performs shared skeleton base lookup and validates `runshell`, then executes `"$base/runshell" git-remote-annex "$@"`.

State and integration: no wrapper state; integrates Git remote-helper discovery with the standalone environment.

Risks: if not present in `PATH`, Git will not discover the helper. The wrapper itself only checks local bundle layout.

Test signals: configure a remote using the annex helper and verify Git invokes this wrapper with arguments preserved.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-remote-annex -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-remote-p2p-annex -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-remote-p2p-annex

Purpose: Linux standalone launcher for the P2P annex Git remote helper.

Control flow and integration: shares the standard Linux skeleton wrapper logic and executes `"$base/runshell" git-remote-p2p-annex "$@"`, ensuring the helper runs with bundled binaries and libraries.

State and dependencies: stateless; depends on `runshell` and the bundled helper existing in the bundle path configured by `runshell`.

Risks: P2P remotes may be invoked by Git automatically, so missing wrapper placement in `PATH` breaks discovery. Path canonicalization and `runshell` integrity are the wrapper-level risks.

Test signals: invoke helper discovery through Git and run a minimal P2P remote operation through the standalone bundle.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-remote-p2p-annex -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-remote-tor-annex -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-remote-tor-annex

Purpose: Linux standalone launcher for the Tor annex Git remote helper.

Control flow: standard base resolution and validation, followed by `exec "$base/runshell" git-remote-tor-annex "$@"`.

State and integration: no persistent state in the launcher; Tor/helper configuration is handled by the invoked command and the standalone environment.

Risks: remote-helper discovery depends on executable name and `PATH`. Wrapper failure modes are missing base or missing `runshell`.

Test signals: check `git-remote-tor-annex` invocation through this wrapper and a configured Tor-annex remote smoke test where available.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-remote-tor-annex -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-shell -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-shell

Purpose: Linux standalone launcher for bundled `git-shell`.

Control flow: resolves base via `readlink`, checks `runshell`, canonicalizes base, and executes `"$base/runshell" git-shell "$@"`.

State and integration: stateless wrapper for SSH-restricted Git access using the bundle's Git implementation.

Risks: because `git-shell` can be exposed over SSH, preserving arguments and using the correct bundled binary matters. The wrapper itself has simple path-layout failure modes.

Test signals: execute allowed and disallowed git-shell commands through the wrapper in a temporary environment.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-shell -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-upload-pack -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-upload-pack

Purpose: Linux standalone launcher for bundled `git-upload-pack`, used by fetch/clone smart protocol operations.

Control flow: shared skeleton base validation and canonicalization, then `exec "$base/runshell" git-upload-pack "$@"`.

State and integration: stateless wrapper used by Git transports, with environment setup delegated to `runshell`.

Risks: any pre-exec diagnostics could interfere with Git protocol if emitted after protocol negotiation, but this script only emits before exec on fatal layout errors. Path resolution remains the main wrapper risk.

Test signals: clone/fetch from a repository using this wrapper as the upload-pack command and verify protocol success.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-upload-pack -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/runshell -->
# sources/sync-backup/git-annex/standalone/linux/skel/runshell

Purpose: central Linux standalone environment launcher. It prepares bundled binaries, libraries, Git templates, man pages, locales, CA certificates, Android/Termux adaptations, and SSH helper shims before executing a requested command or shell.

Important behavior: validates `base/bin/git-annex`, canonicalizes `base`, and works around `:` or `;` in paths by symlinking through a temp directory. Unless `GIT_ANNEX_PACKAGE_INSTALL` is set, it installs `~/.ssh/git-annex-shell` and `~/.ssh/git-annex-wrapper` shims. It exports `GIT_ANNEX_APP_BASE`, prepends `$base/bin`, appends `$base/extra`, builds `GIT_ANNEX_LD_LIBRARY_PATH` from `libdirs`, sets `GIT_ANNEX_DIR`, `GCONV_PATH`, `GIT_EXEC_PATH`, `GIT_TEMPLATE_DIR`, and `MANPATH`, and unsets `LD_PRELOAD`.

Control flow: after environment setup, it optionally creates a per-bundle locale cache under `~/.cache/git-annex/locales`, using `buildid`, `gconvdir`, `i18n`, and `localedef` for UTF-8 locales. On Android, it removes incompatible bundled Git pieces, removes bundled `uname`, runs `termux-fix-shebang`, may add the bundle to `.profile`, uses `proot`, sets `GIT_ANNEX_SSH_SOCKET_DIR`, and narrows `GIT_ANNEX_STANDLONE_ENV`. For non-Android it sets CA info from system locations or bundled certs. Finally it restores `IFS`, exports `LD_HWCAP_MASK=`, and execs the requested command or `sh`; when a temp symlink was used, it runs without `exec` so the EXIT trap can clean it.

State and persistence: writes SSH shims, locale caches, Android `.profile` entries, and may mutate the extracted Android bundle by deleting bundled Git-related files and fixing shebangs. It also creates temporary symlink directories for problematic paths.

Dependencies and integration points: POSIX shell, Linux dynamic linker behavior, bundled metadata files (`libdirs`, `gconvdir`, `buildid`), `localedef`, Termux utilities on Android, `proot`, Git, git-annex assistant/webapp, SSH forced-command workflows, and Git SSL certificate discovery.

Risks: this script has broad side effects in `$HOME/.ssh`, `$HOME/.cache`, and on Android inside the bundle. Locale cache creation has race handling but still depends on filesystem semantics. The variable name `GIT_ANNEX_STANDLONE_ENV` is misspelled consistently and likely part of an existing contract. Android cleanup uses `find | grep | xargs rm -rf`, which is intentionally broad inside the bundle.

Test signals: run commands through the standalone bundle on Linux and Android/Termux, verify library path and Git template behavior, locale cache generation/cleanup, CA fallback, SSH shim creation, temp path workaround for colon paths, and package-install mode with system locales.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/runshell -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git

Purpose: macOS app-bundle launcher for bundled `git`.

Control flow: resolves a simple symlink with `readlink "$0"`, derives and validates `base` and `base/runshell`, canonicalizes base, exports `GIT_ANNEX_APP_BASE` when the standalone app marker `base/git-annex` exists, then executes `"$base/runshell" git "$@"`.

State and dependencies: stateless wrapper; depends on `/bin/sh`, `readlink`, and the macOS app's `runshell`.

Integration points and risks: links app-bundle command stubs to the shared macOS runtime setup. Unlike Linux wrappers, it does not use `readlink -f`, matching macOS tool availability. Test with app translocation/symlink layouts is important.

Test signals: invoke through the app bundle and through symlinks, verify app base export and argument forwarding.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex

Purpose: macOS app-bundle launcher for `git-annex`.

Control flow: standard macOS skeleton wrapper path resolution, `runshell` validation, base canonicalization, optional `GIT_ANNEX_APP_BASE` export, and `exec "$base/runshell" git-annex "$@"`.

State and integration: wrapper has no persistent state. It is the main app-bundle command entry point and relies on `runshell` to set `PATH`, `GIT_EXEC_PATH`, templates, and SSH shims.

Risks: app bundle relocation or symlink oddities can affect `base`. Missing `runshell` fails before command execution.

Test signals: run `git-annex version`, verify app-base self-install behavior, and test symlinked command invocation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex-shell -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex-shell

Purpose: macOS app-bundle launcher for `git-annex-shell`, commonly used by SSH integrations.

Control flow: resolves base, validates `runshell`, canonicalizes, exports `GIT_ANNEX_APP_BASE` when applicable, and execs `"$base/runshell" git-annex-shell "$@"`.

State and integration: stateless wrapper over the macOS `runshell`, which creates SSH helper shims in the user's home directory.

Risks: command is security-sensitive when exposed via SSH; wrapper-level argument preservation is correct through quoted `"$@"`.

Test signals: direct command invocation and SSH forced-command shim tests through the app bundle.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex-shell -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex-webapp -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex-webapp

Purpose: macOS app-bundle launcher for `git-annex webapp`.

Control flow: performs normal macOS base resolution and `GIT_ANNEX_APP_BASE` export, then starts `"$base/runshell" git-annex webapp "$@"` in the background. The backgrounding is explicit because macOS app launch behavior expects the wrapper to return.

State and integration: wrapper has no durable state; the webapp and runshell handle runtime state, environment, and self-install hooks.

Risks: backgrounding means caller exit status does not reflect long-term webapp startup success. Diagnostics after backgrounding may be detached from the launcher context.

Test signals: app launch starts the webapp without blocking, arguments are forwarded, and failure modes are observable in app logs or stderr.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex-webapp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-receive-pack -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-receive-pack

Purpose: macOS app-bundle launcher for bundled `git-receive-pack`.

Control flow: standard app skeleton path handling, app-base export when applicable, then `exec "$base/runshell" git-receive-pack "$@"`.

State and integration: stateless wrapper for Git smart protocol receive operations using bundled Git.

Risks: Git protocol operations are sensitive to extra output; this wrapper only emits diagnostics on fatal pre-exec layout failures.

Test signals: push to a repository with this receive-pack command and verify protocol correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-receive-pack -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-annex -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-annex

Purpose: macOS app-bundle launcher for `git-remote-annex`.

Control flow and integration: resolves bundle base, validates `runshell`, exports app base, and execs `"$base/runshell" git-remote-annex "$@"` so Git remote-helper discovery uses the bundled environment.

State and risks: stateless wrapper. It must be executable and discoverable in the effective `PATH`; otherwise annex remotes cannot use the helper.

Test signals: invoke via Git remote-helper discovery and verify arguments/environment through the app bundle.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-annex -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-p2p-annex -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-p2p-annex

Purpose: macOS app-bundle launcher for the P2P annex remote helper.

Control flow: shared macOS launcher pattern ending with `exec "$base/runshell" git-remote-p2p-annex "$@"`.

State and integration: no persistent wrapper state; P2P configuration and sockets belong to the invoked helper and git-annex.

Risks: app-bundle path resolution and helper discoverability are the main wrapper concerns.

Test signals: Git remote-helper invocation for a P2P annex remote through the macOS bundle.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-p2p-annex -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-tor-annex -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-tor-annex

Purpose: macOS app-bundle launcher for the Tor annex remote helper.

Control flow and integration: resolves and validates app bundle base, exports `GIT_ANNEX_APP_BASE`, and execs `"$base/runshell" git-remote-tor-annex "$@"`.

State and risks: stateless wrapper. Tor-specific state is outside this file. Missing `runshell` or incorrect bundle layout is fatal.

Test signals: helper discovery and a smoke invocation with Tor-annex remote configuration.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-tor-annex -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-shell -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-shell

Purpose: macOS app-bundle launcher for bundled `git-shell`.

Control flow: resolves app `base`, validates `runshell`, canonicalizes, exports app base if applicable, then executes `"$base/runshell" git-shell "$@"`.

State and integration: stateless command stub for restricted SSH/Git use with bundled Git.

Risks: security-sensitive when used as a login shell or forced command; argument forwarding is quoted and environment setup is delegated.

Test signals: exercise allowed and denied git-shell commands through the bundle.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-shell -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-upload-pack -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-upload-pack

Purpose: macOS app-bundle launcher for bundled `git-upload-pack`.

Control flow: shared app wrapper logic, optional app-base export, and `exec "$base/runshell" git-upload-pack "$@"`.

State and integration: stateless wrapper for clone/fetch smart protocol service.

Risks: extra output would corrupt protocol, but only pre-exec fatal diagnostics are emitted. Bundle path resolution must work under macOS app layouts.

Test signals: clone/fetch from a repository using this upload-pack command.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-upload-pack -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/runshell -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/runshell

Purpose: central macOS app-bundle environment launcher. It prepares the bundled command directory and Git runtime variables before executing a requested command or an interactive shell.

Important behavior: validates `base/bundle/git-annex` and `base/bundle/git`, canonicalizes `base`, installs `~/.ssh/git-annex-shell` and `~/.ssh/git-annex-wrapper` if missing, prepends `$bundle` to `PATH` and appends `$bundle/extra`, sets `GIT_EXEC_PATH`, `GIT_TEMPLATE_DIR`, `GIT_ANNEX_DIR`, and records `GIT_ANNEX_STANDLONE_ENV="PATH GIT_EXEC_PATH GIT_TEMPLATE_DIR"`.

Control flow and state: after setup it restores `IFS`, executes the requested command with `exec`, or runs `$SHELL` when no command is supplied. Persistent side effects are limited to SSH helper shims in `$HOME/.ssh`.

Dependencies and integration points: POSIX shell, macOS app bundle layout with `Contents/MacOS/bundle`, bundled Git/git-annex, SSH forced-command workflows, and git-annex cleanup behavior for the exported environment variables.

Risks: writes to `$HOME/.ssh` if helper files are absent. No Linux-style locale/library/CA setup is present, so bundle completeness must be handled by macOS packaging. The misspelled `GIT_ANNEX_STANDLONE_ENV` is likely an intentional existing contract.

Test signals: run git/git-annex through app wrappers, verify SSH shim creation, environment variable values, fallback interactive shell behavior, and relocated app bundle paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/runshell -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/rpm/rpmbuild-from-standalone-tarball -->
# sources/sync-backup/git-annex/standalone/rpm/rpmbuild-from-standalone-tarball

Purpose: helper script that builds a `git-annex-standalone` RPM from an existing standalone tarball, without requiring the build host to match the target architecture.

Important control flow: reads `rpmarch`, `tarball`, `version`, and `rpmrepo` from arguments; strips any suffix after the first dash from the version; creates a temp directory with cleanup trap; extracts the tarball there; creates an rpmbuild root; runs `rpmbuild -bb` with `_rpmdir`, `_rpmfilename`, `version`, `release`, and target architecture definitions; then moves the produced `git-annex-standalone.rpm` into `$rpmrepo/git-annex-standalone-$version-$release.$rpmarch.rpm`.

State and persistence: temporary extraction/build root under `mktemp -d`; final RPM written to the requested repository directory. Cleanup removes the temp directory on exit.

Dependencies and integration points: POSIX shell, `tar`, `rpmbuild`, a sibling `git-annex-standalone.spec`, and an existing standalone tarball.

Risks: if required args are missing, it prints usage but does not exit immediately, so subsequent commands can fail less clearly. `cat "$tarball" | tar zx` is less direct than `tar zxf`. It assumes the current directory is a suitable `_rpmdir` for rpmbuild output.

Test signals: build from a fixture tarball for multiple target arches, verify output filename/version, missing-argument behavior, cleanup after failure, and RPM metadata from the spec.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/rpm/rpmbuild-from-standalone-tarball -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/static/js/bootstrap.js -->
# sources/sync-backup/git-annex/static/js/bootstrap.js

Purpose: vendored Bootstrap v3.1.1 JavaScript bundle used by git-annex's static web UI. It adds jQuery plugins for transitions, alerts, buttons, carousel, collapse, dropdowns, modals, tooltips, popovers, scrollspy, tabs, and affix behavior.

Important modules and APIs: the file requires global `jQuery` and registers plugins on `$.fn`: `alert`, `button`, `carousel`, `collapse`, `dropdown`, `modal`, `tooltip`, `popover`, `scrollspy`, `tab`, and `affix`. Each plugin stores component instances under `data('bs.<component>')`, exposes a `Constructor`, and implements `noConflict`. `transition.js` detects CSS transition end event names and adds `$.fn.emulateTransitionEnd(duration)`.

Control flow: each Bootstrap module is wrapped in an IIFE receiving `jQuery`. Data APIs bind delegated handlers on `document` or `window load`: alert dismissal, button toggles, carousel controls/auto-start, collapse toggles, dropdown clicks/keyboard navigation, modal launchers, scrollspy initialization, tab clicks, and affix initialization. Programmatic API calls go through jQuery plugin dispatch, creating an instance if needed and invoking string-named methods.

Component state: components persist runtime state in jQuery data and instance fields. Carousel tracks `paused`, `sliding`, `interval`, `$active`, and `$items`; Collapse tracks `transitioning`; Dropdown uses parent `.open` classes and mobile backdrops; Modal tracks `isShown` and `$backdrop` and toggles `body.modal-open`; Tooltip/Popover track enabled state, timeout, hover state, generated tip/arrow nodes, title/content, and placement; ScrollSpy tracks offsets, targets, and active target; Affix tracks `affixed`, `unpin`, and pinned offset.

Dependencies and integration points: jQuery APIs for events, data, DOM traversal, effects, offset/position, AJAX `.load` for modal remotes, and CSS classes from Bootstrap 3.1.1. Browser integration includes `document`, `window`, transition events, keyboard events, focus handling, and scroll state.

Risks: this is an old Bootstrap release. Tooltip and popover support `html: true` and template/content injection without the later sanitizer facilities, so callers must not pass untrusted HTML. Modal `remote` loads arbitrary URLs into `.modal-content` through jQuery. Selector construction from `href`/`data-target` can be fragile with unusual IDs. Global delegated handlers and jQuery data can leak if DOM nodes are removed without plugin cleanup. Accessibility behavior reflects Bootstrap 3.1.1 and is limited compared with modern components.

Test signals: browser/UI tests should cover every data API and programmatic plugin path, transition/no-transition branches, modal focus trapping and backdrop behavior, dropdown keyboard navigation, tooltip/popover placement including `auto`, scrollspy/affix on scroll, and the git-annex web pages that depend on these plugins. Security tests should verify no untrusted HTML reaches tooltip/popover/modal remote options.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/static/js/bootstrap.js -->
