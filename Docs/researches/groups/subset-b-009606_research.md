# Research Group subset-b-009606

This grouped report covers the assigned `go-nfs` NFSv3 server files and Impacket workflow/example files under `sources/user-network-fs`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onsymlink.go -->
# sources/user-network-fs/go-nfs/nfs_onsymlink.go

## Purpose

`nfs_onsymlink.go` implements the NFSv3 `SYMLINK` procedure handler. It creates a symbolic link inside the filesystem represented by an NFS file handle, applies requested post-creation attributes when the server handler supports mutation, and serializes the NFS success result including the new object handle, post-operation attributes, and weak cache consistency data for the parent directory.

## Important APIs, Types, and Functions

The main API is `onSymlink(ctx context.Context, w *response, userHandle Handler) error`, registered elsewhere as the procedure handler for `NFSProcedureSymlink`. It consumes a `DirOpArg` for parent handle and link name, `ReadSetFileAttributes` for requested link attributes, and `xdr.ReadOpaque` for the symlink target. It depends on the `Handler` interface for `FromHandle`, `ToHandle`, and `Change`, and on helper serializers `WritePostOpAttrs`, `WriteWcc`, and `tryStat`.

## Control Flow

The handler sets `w.errorFmt` to `wccDataErrorFormatter`, decodes request fields in NFS wire order, resolves the parent file handle to a `billy.Filesystem` and path, and rejects stale handles, read-only filesystems, overlong names, existing destination paths, missing or non-directory parents, and filesystem symlink failures with mapped `NFSStatusError` values. After `fs.Symlink(target, newFilePath)` succeeds, it creates an NFS handle for the new path, applies requested attributes via `userHandle.Change(fs)` when available, builds an XDR response with `NFSStatusOk`, a present-object-handle discriminator, the handle, post-op attributes for the link, and WCC data for the parent, then writes the bytes to the response.

## State and Persistence Behavior

The persistent state mutation is the symlink creation in the backing `billy.Filesystem`. Attribute application may further mutate mode, ownership, or times depending on the `Change` implementation. The response includes best-effort post-operation stat data, but no explicit rollback is attempted if attribute application fails after symlink creation. The `ctx` parameter is unused, so cancellation does not interrupt filesystem work.

## Dependencies and Integration Points

This file integrates NFS XDR decoding/encoding (`go-nfs-client/nfs/xdr`), repository NFS status helpers, the repository handler abstraction, and `go-billy` filesystem capability checks. It requires the backing filesystem to advertise `billy.WriteCapability` and implement `Symlink`; filesystems lacking symlink support will surface as `NFSStatusAccess`.

## Risks and Edge Cases

The filename check converts bytes to string and only checks length against `PathNameMax`; path separator or special-name policy depends on the backing filesystem and handler. There is a race between destination `Stat` and `Symlink`, so concurrent creators can still win. Parent pre-operation WCC data is passed as `nil`, reducing cache consistency precision on success. Attribute failure after symlink creation leaves the symlink present while returning an I/O error. Target contents are accepted as an opaque path without normalization or maximum-length enforcement.

## Test Signals

Useful tests should issue real NFS `SYMLINK` calls against writable and read-only billy filesystems, verify returned object handles and link attributes, and cover existing targets, non-directory parents, stale handles, unsupported symlink implementations, overlong names, and attribute mutation failures. Existing integration tests in `nfs_test.go` exercise server/RPC plumbing but do not directly cover this handler.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onsymlink.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onwrite.go -->
# sources/user-network-fs/go-nfs/nfs_onwrite.go

## Purpose

`nfs_onwrite.go` implements the NFSv3 `WRITE` procedure. It writes request payload bytes to an existing regular file at a requested offset, returns weak cache consistency data, reports the number of bytes written, and always advertises file-sync stability with the server write verifier.

## Important APIs, Types, and Functions

`writeStability` models the NFS write stability enum with `unstable`, `dataSync`, and `fileSync`. `writeArgs` mirrors the XDR request payload: file handle, offset, count, stability mode, and opaque data. `onWrite(ctx, w, userHandle)` is the procedure handler. It uses `Handler.FromHandle`, `billy.CapabilityCheck`, `ToFileAttribute(...).AsCache`, `statusFromWriteError`, `WriteWcc`, `tryStat`, and `w.Server.ID`.

## Control Flow

The handler decodes `writeArgs`, resolves the file handle, verifies write capability, rejects oversized `Count` or data lengths beyond `math.MaxInt32`, and validates the stability enum. It stats the target before opening it to produce pre-operation WCC data and to reject missing paths or non-regular files. It opens the file read/write with existing permissions, seeks to the request offset when nonzero, truncates the requested count to the available data length, writes that slice, closes the file, and serializes `NFSStatusOk`, WCC data, written byte count, returned `fileSync` stability, and the server's 8-byte verifier.

## State and Persistence Behavior

The backing filesystem file contents are mutated through `OpenFile` and `Write`. The code does not explicitly call `Sync`; durability depends on the backing `billy.File` and `Close` implementation even though the response advertises `fileSync`. Writes can extend files if the filesystem supports sparse or gap writes. The server verifier is persisted only in the `Server.ID` field for the running server instance and is generated by `Server.Serve` when unset.

## Dependencies and Integration Points

This handler bridges NFS XDR, `go-billy` filesystems, repository status mapping, and the NFS server verifier in `server.go`. It assumes the resolved `billy.File` implements `Seek`, as required by the billy file interface used here. It is covered indirectly by `nfs_test.go`, which creates a file through NFS, opens it, writes bytes, and reads them back through the client.

## Risks and Edge Cases

The file is not closed on a seek failure because the error return happens before `Close`, which can leak handles. A large `Offset` is cast to `int64`; offsets above `math.MaxInt64` wrap and may seek incorrectly. If `req.Count` is larger than `len(req.Data)`, the server silently writes fewer bytes instead of rejecting malformed XDR. Returning `fileSync` without forcing sync can violate strict NFS durability expectations. The `ctx` parameter is unused. Pre-op and post-op stats can race with concurrent writers.

## Test Signals

Existing `TestNFS` confirms basic client write/read behavior and the tracking filesystem can catch leaked close paths in covered scenarios. Additional focused tests should cover invalid stability values, non-regular targets, stale handles, read-only filesystems, short data versus count, seek errors with handle leak detection, offset overflow, close errors, and verifier stability across multiple writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onwrite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_test.go -->
# sources/user-network-fs/go-nfs/nfs_test.go

## Purpose

`nfs_test.go` contains integration tests for the Go NFS server using an in-memory filesystem and the real `go-nfs-client` RPC/NFS client stack. It verifies basic mount, fsinfo, create, write/read, large directory reads, rename semantics, empty directory listing, file handle cleanup, and NFS read EOF behavior.

## Important APIs, Types, and Functions

`NewTrackingFS` wraps a `billy.Filesystem` to track opened files. `trackingFS` overrides `Create`, `Open`, and `OpenFile`, while `trackingFile.Close` removes handles from the tracking map. `TestNFS` is the broad end-to-end server test. Helper `readDir` sends raw `READDIR` RPCs because the client has a `READDIRPLUS` implementation but the test also needs plain `READDIR`. Helper `nfsRead` sends raw `READ` RPCs and parses post-op attributes, count, EOF, and data. `TestReadEOF` verifies exact EOF flag semantics.

## Control Flow

`TestNFS` starts a TCP listener on a random local port, creates a tracking `memfs`, seeds `/test` so root exists, wraps the filesystem with null auth and caching handlers, starts `nfs.Serve` in a goroutine, dials via RPC, mounts `/`, and exercises operations through the client target. It validates file creation metadata, writes `hello world`, reads it back, creates 2000 files, compares both `ReadDirPlus` and raw `READDIR` results after sorting, renames one file and checks old lookup failure, then checks empty directory results. A deferred leak check fails if any tracked files remain open.

`TestReadEOF` creates a 64 KiB random file in memfs, serves it through NFS, mounts the target, and calls `nfsRead` with read ranges that are before EOF, exactly reach EOF, extend past EOF, and start at EOF. It verifies count trimming, EOF flags, and data equality.

## State and Persistence Behavior

The tests mutate only in-memory filesystems and local TCP listeners. The NFS server goroutines are not explicitly shut down; they end when the listener is closed or the process exits. The mount is unmounted via defer and RPC connections are closed. `trackingFS.open` is protected by a mutex and serves as test-only state for leak detection.

## Dependencies and Integration Points

The tests integrate `github.com/willscott/go-nfs`, `helpers.NewNullAuthHandler`, `helpers.NewCachingHandler`, `helpers/memfs`, `go-nfs-client` RPC/NFS packages, and XDR helpers. They are strong signals that server handlers, handler caching, handle translation, and client compatibility work together over real TCP rather than only through unit-level calls.

## Risks and Edge Cases

Because the server goroutine return is ignored and no readiness synchronization is used beyond dialing after goroutine start, failures can be timing-sensitive. Random file contents in `TestReadEOF` are not seeded for reproducibility, though only equality is checked. The tracking wrapper depends on every opened file's `Close` being invoked; it is useful for leaks but can produce false negatives for operations that bypass `OpenFile`. The tests do not directly cover many error mappings or symlink/write corner cases.

## Test Signals

This file is itself the main test signal for the Go NFS subset. It should be run with `go test` for the `go-nfs` package. Regressions in directory cookie handling, EOF calculation, file handle invalidation after rename, response parsing, or file closing are likely to appear here. Additional targeted tests should be added for error paths, write durability flags, symlink creation, and handler cancellation behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfsinterface.go -->
# sources/user-network-fs/go-nfs/nfsinterface.go

## Purpose

`nfsinterface.go` defines the NFSv3 procedure and status enumerations used by the server and exposes small common wire structures. It is the shared type surface that lets handlers identify procedure numbers, convert them to readable names, emit NFS status codes, and decode common directory operation arguments.

## Important APIs, Types, and Functions

`NFSProcedure` is a `uint32` enum for procedures from `NULL` through `COMMIT`, with `String()` returning human-readable names. `NFSStatus` is a `uint32` enum for NFSv3 status values such as `NFSStatusOk`, `NoEnt`, `Access`, `Stale`, `NotSupp`, and `ServerFault`, with `String()` mapping codes to messages. `DirOpArg` carries a parent handle and filename for operations such as lookup, create, remove, mkdir, and symlink.

## Control Flow

There is no dynamic control flow beyond switch-based string conversion. Server dispatch code uses procedure numeric values to select registered handlers, handlers return `NFSStatusError` values containing these status constants, and XDR response writers serialize these constants as `uint32`.

## State and Persistence Behavior

The file is stateless. Constants are compile-time values and `DirOpArg` instances are request-local decoded structures. There is no filesystem, network, or process-global mutation.

## Dependencies and Integration Points

The constants correspond to NFSv3 procedure and `nfsstat3` values and are used across handler registration, request logging, response construction, and client-visible error mapping. `DirOpArg` is consumed by handlers such as `onSymlink`.

## Risks and Edge Cases

Incorrect numeric constants would break wire compatibility. The `NFSStatusOk` string contains a typo (`Successfull`), which affects logs or diagnostics but not protocol behavior. Unknown procedures and statuses stringify to generic values, which is safe but can hide missing enum additions. `DirOpArg.Filename` is raw bytes, so each handler must enforce path/name policy consistently.

## Test Signals

Tests should verify procedure numbers against NFSv3 definitions, status constants against client expectations, and string values for logging. Integration tests that issue raw procedure IDs, such as `readDir` and `nfsRead` in `nfs_test.go`, indirectly verify selected procedure constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfsinterface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/server.go -->
# sources/user-network-fs/go-nfs/server.go

## Purpose

`server.go` defines the main NFS server type, the global RPC handler registry, connection acceptance loop, per-connection construction, handler lookup, and convenience `Serve` function. It is the network entry point for serving NFS requests over a `net.Listener`.

## Important APIs, Types, and Functions

`Server` embeds the user `Handler`, stores an 8-byte write verifier `ID`, and optionally carries a base `context.Context`. `HandleFunc` is the procedure callback signature. `RegisterMessageHandler(protocol, proc, handler)` registers global dispatch callbacks by `(protocol, proc)`. `(*Server).Serve(l net.Listener)` accepts connections and launches `conn.serve`. `(*Server).handlerFor(prog, proc)` resolves registered callbacks. Top-level `Serve(l, handler)` mirrors `http.Serve`.

## Control Flow

`Server.Serve` closes the listener on return, selects `context.Background()` unless `s.Context` is set, initializes `s.ID` from `crypto/rand` if all zeros, and then loops on `Accept`. Temporary timeout errors use exponential backoff from 5 ms up to 1 second before retrying. Non-temporary accept errors stop the server. Successful accepts reset backoff, wrap the `net.Conn` in a `conn` via `newConn`, and serve it in a goroutine with the base context.

## State and Persistence Behavior

The server mutates `s.ID` once per server lifetime when it starts, and uses it as the NFS write verifier in write responses. `registeredHandlers` is package-global mutable state shared by all server instances. Connections are served concurrently in goroutines. No on-disk persistence is used.

## Dependencies and Integration Points

This file integrates with lower-level `conn` request parsing and response writing code elsewhere in the package, all NFS and mount procedure registrations, the user-supplied filesystem `Handler`, and the write handler's verifier emission. It uses Go `net`, `context`, `crypto/rand`, and timeout semantics.

## Risks and Edge Cases

`registeredHandlers` is a global map without synchronization; concurrent registration or lookup can race, and duplicate checks are O(n). Handler state is global rather than server-scoped, so tests or embedders cannot easily isolate registries. The accept loop does not stop on context cancellation; context is only passed to connection handlers. `rand.Reader.Read` is used directly instead of `io.ReadFull`, so a short read could leave a partially random verifier without error if ever returned by the reader. Listener close on `Serve` return can surprise callers that expect ownership to remain outside.

## Test Signals

Existing integration tests start `nfs.Serve` on a local TCP listener and verify mount and file operations, which exercises ID generation, accept, connection goroutines, and handler dispatch. Additional tests should cover duplicate registration, timeout accept behavior with a fake listener, server-specific context propagation, registry race behavior under `go test -race`, and write verifier initialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/time.go -->
# sources/user-network-fs/go-nfs/time.go

## Purpose

`time.go` provides conversion helpers between Go `time.Time` values and the NFS wire time representation used by this package. It wraps seconds and nanoseconds into a simple `FileTime` struct equivalent to the client package's `NFS3Time`.

## Important APIs, Types, and Functions

`FileTime` has `Seconds uint32` and `Nseconds uint32`. `ToNFSTime(t time.Time)` converts a Go time to NFS seconds and nanoseconds. `FileTime.Native()` converts back to a `*time.Time`. `FileTime.EqualTimespec(sec, nsec)` compares against local stat-style second/nanosecond values.

## Control Flow

`ToNFSTime` calls `t.Unix()` and `t.UnixNano() % time.Second`. `Native` calls `time.Unix` with the stored values and returns the address of the local result. `EqualTimespec` casts input seconds and nanoseconds to `uint32` and compares both fields.

## State and Persistence Behavior

The file is stateless. Time values are copied into request/response structs and no global clock state is stored.

## Dependencies and Integration Points

It depends only on the standard `time` package. Attribute serialization and comparison code elsewhere in the NFS package can use `FileTime` when emitting NFS file attributes or applying setattr requests.

## Risks and Edge Cases

Seconds are truncated to 32 bits, so times beyond the NFSv3 unsigned 32-bit range wrap. Negative Unix times also wrap. The TODO in `EqualTimespec` notes missing overflow/bounds checks, and `ToNFSTime` can produce unexpected nanoseconds for pre-epoch times because Go's remainder keeps the sign of the dividend. Returning `*time.Time` from `Native` is safe but uncommon for a value conversion and may force allocation.

## Test Signals

Tests should cover round trips for ordinary times, zero time behavior, boundary seconds near `math.MaxUint32`, negative/pre-epoch times, nanosecond precision, and `EqualTimespec` overflow cases. Attribute-oriented NFS integration tests indirectly exercise this conversion when checking file metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/time.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/.github/labeler.yml -->
# sources/user-network-fs/impacket/.github/labeler.yml

## Purpose

`.github/labeler.yml` defines pull request label rules for the Impacket repository. It maps changed file path patterns to labels such as Examples, Library, CI/CD & Tests, Setup, and Docs.

## Important APIs, Types, and Functions

This is declarative YAML for `srvaroa/labeler`. Top-level `version: 1` selects the labeler config format. Each `labels` entry contains a `label` string and `files` regex-style path patterns.

## Control Flow

Runtime control flow is owned by the labeler GitHub Action. On pull request events, `.github/workflows/labeler.yml` invokes the action, which reads this file, matches changed paths against configured patterns, and applies corresponding labels.

## State and Persistence Behavior

The file itself is repository configuration. Persistent state effects occur in GitHub pull request metadata when labels are applied. No local build or runtime state is changed.

## Dependencies and Integration Points

It integrates with `.github/workflows/labeler.yml` and the `srvaroa/labeler@master` action. Labels align with major repository areas: `examples/`, `impacket/`, `tests/`, workflow/config files, setup files, and docs/license files.

## Risks and Edge Cases

Pattern semantics depend on the external labeler action. Broad patterns such as `.github/.*` and `*.md` may over-label repository-root changes, while nested markdown files may or may not match depending on the action's regex handling. Using label names that do not exist may require the action to create them or fail depending on repository permissions.

## Test Signals

Validation is best done by opening test pull requests or running the labeler action in CI against synthetic changed-file lists. A workflow run with expected labels on examples, library, CI, setup, and docs changes is the primary signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/.github/labeler.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/.github/workflows/build_and_test.yml -->
# sources/user-network-fs/impacket/.github/workflows/build_and_test.yml

## Purpose

`build_and_test.yml` defines Impacket's main GitHub Actions CI workflow. It performs syntax linting, runs the tox-based non-remote unit test suite across supported Python versions, builds a wheel, and attempts to build the Docker image.

## Important APIs, Types, and Functions

The workflow is named `Build and test Impacket` and triggers on `push` and `pull_request`. It defines `DOCKER_TAG: impacket:latests`. Jobs are `lint`, `test`, and `docker`. `lint` uses `actions/checkout@v3`, `actions/setup-python@v4`, installs `flake8`, and runs strict syntax checks plus non-blocking style warnings. `test` runs a matrix over Python 3.9 through 3.13 and experimental `3.14-dev`, installs tox dependencies, runs `tox -- -m 'not remote'`, and builds a wheel. `docker` builds the repository Dockerfile and is allowed to fail.

## Control Flow

All jobs are skipped for same-repository pull requests because their `if` condition allows pushes or pull requests whose head repo differs from the base repository. `test` and `docker` depend on `lint`. The test matrix disables fail-fast and marks only the 3.14-dev include row as experimental with `continue-on-error`. The Docker job also has `continue-on-error: true`.

## State and Persistence Behavior

The workflow creates ephemeral CI virtual environments, tox environments, wheel artifacts in the workspace, and Docker build layers on the runner. It does not upload artifacts in this file. Persistent external state is limited to GitHub check results.

## Dependencies and Integration Points

It integrates with `requirements.txt`, `requirements-test.txt`, `tox.ini`, `setup.py`, and `Dockerfile`. It depends on GitHub-hosted Ubuntu runners, official checkout/setup-python actions, PyPI availability, tox-gh-actions configuration, and Docker build support.

## Risks and Edge Cases

`DOCKER_TAG` contains the likely typo `latests`. The pull request `if` condition appears inverted from common security patterns because it skips same-repo PRs and runs fork PRs; if secrets were added later this would matter. Pinning actions only by major version and using Python `3.14-dev` can introduce drift. The flake8 warning step is exit-zero, so many style regressions remain advisory. Docker failures do not fail the workflow.

## Test Signals

The primary signal is a successful GitHub Actions run with lint, tox matrix, wheel build, and Docker build logs. Local approximations are `flake8` with the same flags, `tox -- -m 'not remote'`, `python setup.py bdist_wheel`, and `docker build -t impacket:latests .`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/.github/workflows/build_and_test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/.github/workflows/labeler.yml -->
# sources/user-network-fs/impacket/.github/workflows/labeler.yml

## Purpose

`labeler.yml` defines the GitHub Actions workflow that labels pull requests using the repository's labeler configuration.

## Important APIs, Types, and Functions

The workflow is named `Label PRs`, triggers on `pull_request`, and has one `build` job on `ubuntu-latest`. The only step uses `srvaroa/labeler@master` and passes `GITHUB_TOKEN` from `${{ secrets.GITHUB_TOKEN }}`.

## Control Flow

On each pull request event, the job starts and the action reads `.github/labeler.yml`, inspects changed files through GitHub APIs, and applies matching labels. No checkout step is present, so the action must fetch configuration through the API or default repository context.

## State and Persistence Behavior

The persistent state effect is mutation of pull request labels. Runner state is ephemeral. No files are generated by the workflow itself.

## Dependencies and Integration Points

It depends on the external `srvaroa/labeler` action, GitHub Actions pull request permissions, the default `GITHUB_TOKEN`, and `.github/labeler.yml`. It is part of repository triage rather than package build or runtime behavior.

## Risks and Edge Cases

Using `@master` is not reproducible and can change behavior without a repository change. If workflow permissions are restricted, the token may lack label write access. Pull requests from forks can have different token permission behavior. Missing checkout may be fine for this action but would break actions that expect local files.

## Test Signals

The signal is a pull request workflow run that applies expected labels from changed paths. A good regression test changes one file under `examples/`, `impacket/`, or `.github/` and checks the resulting labels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/.github/workflows/labeler.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/Dockerfile -->
# sources/user-network-fs/impacket/Dockerfile

## Purpose

The `Dockerfile` builds a small Alpine-based runtime image with Impacket installed into a Python virtual environment. It clones the upstream Fortra Impacket repository during image build rather than installing from the local build context.

## Important APIs, Types, and Functions

The first stage `compile` uses `python:3.13-alpine`, installs build dependencies (`git`, compiler toolchain, Python headers, libffi, OpenSSL, cargo), creates `/opt/venv`, clones `https://github.com/fortra/impacket.git` with depth 1, and installs `impacket/` with pip. The final stage also uses `python:3.13-alpine`, copies `/opt/venv`, sets `PATH`, and uses `/bin/sh` as entrypoint.

## Control Flow

Docker executes a multi-stage build: dependency-heavy compile stage first, then copies only the virtualenv into the final image. At container runtime, no Impacket command is executed by default; the user lands in a shell with Impacket console scripts available on `PATH`.

## State and Persistence Behavior

Build-time state includes a cloned upstream repository and virtualenv. Runtime persistent state is only container filesystem changes made by users. Because the build clones the remote repository, the image contents vary over time unless the upstream default branch is pinned externally.

## Dependencies and Integration Points

It depends on Docker, Alpine packages, PyPI, GitHub network access, and Impacket's install metadata. The CI workflow builds this image in the `docker` job. The image is intended for interactive Impacket use rather than repository-local development.

## Risks and Edge Cases

The build ignores the local source tree, so CI can pass Docker build even if local packaging is broken, and image contents may not match the commit being tested. Unpinned upstream clone and base image tags reduce reproducibility. Alpine/musl can expose dependency compatibility issues. Running as root and entering `/bin/sh` is convenient but not hardened.

## Test Signals

`docker build -t impacket:latests .` is the direct validation path in CI. A stronger test should run `docker run --rm impacket:latests python -c "import impacket"` and invoke a representative installed example command.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/MANIFEST.in -->
# sources/user-network-fs/impacket/MANIFEST.in

## Purpose

`MANIFEST.in` controls source distribution contents for Impacket packaging. It ensures top-level metadata, requirements, tox configuration, examples, and tests are included in generated sdists.

## Important APIs, Types, and Functions

The manifest uses setuptools/distutils directives: `include` for specific files (`LICENSE`, `README.md`, `SECURITY.md`, `TESTING.md`, `requirements.txt`, `tox.ini`, etc.) and `recursive-include` for `examples` and `tests`.

## Control Flow

When `setup.py sdist` runs, setuptools reads the manifest and adds matching files to the source distribution file list. This file does not affect wheel package data unless setup configuration also includes package data.

## State and Persistence Behavior

It influences build artifacts only. The persistent output is an sdist containing the included files. No runtime state is modified.

## Dependencies and Integration Points

It integrates with `setup.py`, CI wheel/source build workflows, PyPI releases, and downstream users who install from sdist or inspect bundled examples/tests.

## Risks and Edge Cases

`recursive-include examples tests *.txt *.py` is unusual because it names two directories before patterns; the later `recursive-include tests *` is broader and may duplicate intent. Files outside listed patterns, such as YAML, JSON, certificates, or binary test fixtures, may be excluded unless captured by other packaging metadata. Including all tests can enlarge source distributions.

## Test Signals

Run `python setup.py sdist` or modern `python -m build --sdist`, inspect the archive contents, and confirm required metadata, examples, and test fixtures are present. CI wheel build does not fully validate sdist completeness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/MANIFEST.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/CheckLDAPStatus.py -->
# sources/user-network-fs/impacket/examples/CheckLDAPStatus.py

## Purpose

`CheckLDAPStatus.py` enumerates domain controllers through DNS SRV records, then checks each controller for LDAP signing enforcement and LDAPS channel binding token policy. It is an unauthenticated or low-auth diagnostic tool for Active Directory LDAP hardening posture.

## Important APIs, Types, and Functions

`CheckLDAP.__init__` stores the domain, resolver/DC IP, and DNS timeout. `list_dc` uses `dns.resolver.Resolver` to query `_ldap._tcp.dc._msdcs.<domain>` SRV records. `run` iterates controllers. `check_ldap_signing` attempts unsigned LDAP login via `LDAPConnection(..., signing=False)`. `check_ldaps_cbt` uses LDAPS, manipulates `LDAPConnection.channel_binding_value`, and classifies errors into `Never`, `When Supported`, `Always`, or `No TLS cert`.

## Control Flow

CLI parsing requires `-dc-ip` and `-domain`. After logger initialization, `CheckLDAP.run` resolves DC hostnames, logs the count, and for each one performs the signing and CBT checks. LDAP signing is considered required when an unsigned bind produces `strongerAuthRequired`. LDAPS CBT starts with no channel binding value; an `80090346` LDAP error means required, a bad-credential `52e` response prompts a second bind with a deliberately corrupted CBT to distinguish `When Supported`, and TLS reset errors are mapped to missing certificate.

## State and Persistence Behavior

The script keeps only in-memory status strings and prints results. It creates short-lived LDAP/TLS connections and DNS queries. No files are written and no directory state is modified.

## Dependencies and Integration Points

It depends on `dnspython`, `pyOpenSSL`, Impacket LDAP classes, Impacket example logging, and an accessible DNS/DC IP. It integrates with Active Directory SRV discovery, LDAP port 389, and LDAPS port 636 behavior.

## Risks and Edge Cases

Policy detection is based on string matching LDAP error text, which can change with localization or library formatting. `check_ldaps_cbt` mutates byte index 15 of the CBT and assumes a sufficiently long binding value. Blank username binds may behave differently across DC policy, anonymous bind settings, and NTLM restrictions. DNS failures abort the whole run. Results are policy inference, not authoritative LDAP configuration reads.

## Test Signals

Tests need integration fixtures or mocked `LDAPConnection` and DNS resolver behavior. Useful cases include SRV enumeration, `strongerAuthRequired`, bad credentials without signing requirement, CBT required error, corrupted-CBT error, TLS reset/no certificate, and unexpected LDAP errors under debug logging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/CheckLDAPStatus.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/DumpNTLMInfo.py -->
# sources/user-network-fs/impacket/examples/DumpNTLMInfo.py

## Purpose

`DumpNTLMInfo.py` extracts unauthenticated or null-auth NTLM negotiation information from SMB or RPC endpoints. It reports SMB dialect, signing requirements, read/write sizes, server time/uptime when available, NTLM target info AV pairs, OS version, and whether null session authentication succeeds.

## Important APIs, Types, and Functions

`RPC` connects to EPM on TCP 135, builds an MSRPC bind with NTLM Type 1 authentication, and parses `NTLMAuthChallenge` from the bind ack. `SMB1` and `SMB3` are lightweight custom SMB negotiation/session-setup implementations that expose `GetNegotiateResponse`, `GetChallange`, and `Authenticate`. `SmbConnection` chooses SMB1 or SMB2/3 using a wildcard negotiate and can probe SMBv1 support. `DumpNtlm` dispatches protocol-specific display paths and formats dialect, signing, I/O sizes, times, AV pairs, and null session results.

## Control Flow

The CLI selects SMB by default unless port 135 is used, in which case RPC is selected unless overridden. SMB mode opens a NetBIOS TCP session, sends a wildcard negotiate containing SMB1 and SMB2 dialects, wraps the response in `SMB1` or `SMB3`, displays negotiate metadata, sends an NTLM/SPNEGO session setup to obtain the challenge, parses AV pairs, and attempts an empty Type 3 authentication to check null sessions. RPC mode sends an authenticated bind to the endpoint mapper and parses the NTLM challenge from the bind response.

## State and Persistence Behavior

State is per-connection: sequence windows, SMB UID/session ID, cached negotiate responses, NTLM tokens, and RPC max fragment size. No credentials are stored and no files are written. Network connections are opened but explicit close behavior is minimal and mostly left to session objects/process exit.

## Dependencies and Integration Points

The script depends on Impacket SMB1, SMB2/3 structs, NetBIOS session transport, SPNEGO, NTLM, DCERPC transport/RPCRT/EPM helpers, and low-level NT status constants. It integrates directly with SMB ports 139/445 and RPC endpoint mapper port 135.

## Risks and Edge Cases

Several method and variable names are misspelled (`Challange`, `MaxTrasmitionSize`) but internally consistent. The custom protocol code is sensitive to Impacket structure changes and SMB dialect quirks. It uses broad `except` blocks around authentication and AV pair decoding, which can hide protocol parsing failures. `DisplayDialect` duplicates the SMB 3.0.2 branch. Null session probing may be logged or blocked by modern systems. RPC and SMB connections are not always explicitly disconnected.

## Test Signals

Strong tests require mocked SMB/RPC responses or controlled Windows/Samba fixtures. Signals should include SMB1-only, SMB2/3, signing-required, signing-enabled-not-required, no SMBv1, null-session success/failure, RPC NTLM challenge parsing, AV pair decoding, and time conversion from FILETIME.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/DumpNTLMInfo.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/Get-GPPPassword.py -->
# sources/user-network-fs/impacket/examples/Get-GPPPassword.py

## Purpose

`Get-GPPPassword.py` finds Group Policy Preferences XML files containing `cpassword`, decrypts the known AES-CBC protected value, and prints recovered credentials. It can scan a remote SMB share such as SYSVOL or parse a local XML file.

## Important APIs, Types, and Functions

`GetGPPasswords` owns an `SMBConnection` and share name. `list_shares` prints available shares. `find_cpasswords` breadth-first scans directories for XML files. `parse` retrieves a remote file into `io.BytesIO`, detects encoding with `charset_normalizer`, and calls `parse_xmlfile_content` if `cpassword` is present. `parse_xmlfile_content` parses XML DOMs and extracts known GPP property fields. `decrypt_password` base64-decodes and decrypts with the published GPP AES key and zero IV. Helper functions `parse_args`, `parse_target`, and `init_smb_session` handle CLI, credentials, and SMB login.

## Control Flow

In `LOCAL` mode, the script opens the provided `-xmlfile`, parses it, and displays results. In remote mode, it parses the target, prompts for a password when needed, initializes SMB or Kerberos login, prints shares, and scans `-base-dir` on the selected share. Each matching XML file is fetched by stream, decoded, searched for `cpassword`, parsed according to root XML type (`ScheduledTasks`, `Groups`, or default), decrypted, and displayed.

## State and Persistence Behavior

The script reads remote SMB files and local XML files but does not modify them. It stores scan queues, result dictionaries, and in-memory file buffers. It prints decrypted passwords to logs/stdout, which is the main side effect. No output file option is present.

## Dependencies and Integration Points

It depends on Impacket SMB connection classes, Impacket example target parsing, PyCryptodome AES/padding, `charset_normalizer`, Python DOM XML parsing, and SMB dialect constants. It integrates with Windows SYSVOL/GPP XML layout and SMB ports 139/445.

## Risks and Edge Cases

The XML parsing uses `minidom.parseString`; while local/remote SYSVOL XML is expected, malformed or hostile XML can still cause parser exceptions or resource use. Decrypted credentials are intentionally exposed in logs. The BFS ignores access-denied folders after debug logging. Some file handles are closed only on certain branches; `BytesIO` cleanup is not critical but inconsistent. Base64 padding repair handles common cases but malformed `cpassword` can raise. Local mode opens files without context managers.

## Test Signals

Unit tests can cover `decrypt_password` with known GPP samples, padding variants, empty values, and `parse_xmlfile_content` for Groups and ScheduledTasks XML. Integration tests should mock SMB `listPath`/`getFile` traversal, access-denied directories, encoding detection, and remote Kerberos/NTLM login selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/Get-GPPPassword.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/GetADComputers.py -->
# sources/user-network-fs/impacket/examples/GetADComputers.py

## Purpose

`GetADComputers.py` queries Active Directory LDAP for computer accounts and prints `sAMAccountName`, DNS hostname, operating system version, operating system, and optionally resolved IP address.

## Important APIs, Types, and Functions

`GetADComputers.__init__` stores credentials, Kerberos/hash options, DC settings, request filters, `-resolveIP`, base DN, and fixed table formatting. `processRecord` extracts attributes from `ldapasn1.SearchResultEntry` records and optionally resolves `dNSHostName` A records through the DC. `run` logs into LDAP with `ldap_login`, creates a paged results control, and performs the computer search.

## Control Flow

The CLI parses `domain[/username[:password]]`, authentication, DC, and `-resolveIP` options. After identity parsing and logger initialization, `run` connects to LDAP, prints the header, builds `(&(objectCategory=computer)(objectClass=computer))`, and searches with attributes `sAMAccountName`, `dNSHostName`, `operatingSystem`, and `operatingSystemVersion`. For each result, `processRecord` decodes LDAP attributes, optionally points dnspython at the DC IP and resolves hostnames, and prints a fixed-width row.

## State and Persistence Behavior

The script is read-only against LDAP and DNS. It keeps credentials and output formatting in memory. It does not write files or modify AD state.

## Dependencies and Integration Points

It depends on Impacket LDAP helpers, SAMR constants for imported but unused account flags, `dnspython` for optional hostname resolution, and Active Directory LDAP schema attributes. It integrates with Kerberos/NTLM login flow through `parse_identity` and `ldap_login`.

## Risks and Edge Cases

`-user` is stored but not used in the LDAP filter. DNS resolution is configured by mutating `dns.resolver.default_resolver`, which can affect later resolver calls in the process. Broad `except` around DNS failures hides resolver issues. Fixed-width columns truncate or misalign long names visually. Attribute decoding assumes at least one value. The search uses paged control, but per-record processing and printing are synchronous.

## Test Signals

Tests should mock LDAP entries with missing, empty, and long attributes; verify filter construction; exercise `-resolveIP` success and failure; and ensure Kerberos/hash/DC options are passed to `ldap_login`. Integration tests require an AD fixture with computer objects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/GetADComputers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/GetADUsers.py -->
# sources/user-network-fs/impacket/examples/GetADUsers.py

## Purpose

`GetADUsers.py` queries Active Directory LDAP for user account information and prints account name, email, password-last-set time, and last-logon time. By default it returns enabled users with email addresses, with options to include all users or request one user.

## Important APIs, Types, and Functions

`GetADUsers.__init__` stores credentials, Kerberos/hash options, DC targeting, `-user`, `-all`, base DN, and table formatting. `getUnixTime` converts Windows FILETIME to Unix seconds. `processRecord` decodes `sAMAccountName`, `pwdLastSet`, `lastLogon`, and `mail`. `run` logs into LDAP, builds the search filter, runs a paged LDAP search, and closes the connection.

## Control Flow

CLI parsing feeds `parse_identity`; an empty domain aborts. `run` uses `ldap_login`, prints headers, and constructs a filter. Default mode requires `sAMAccountName`, `mail`, and not `UF_ACCOUNTDISABLE`; `-all` relaxes this to all users. If `-user` is supplied, the filter adds an `sAMAccountName` clause. Search results are streamed to `processRecord`, which converts FILETIME zero to `<never>` and otherwise formats local `datetime.fromtimestamp`.

## State and Persistence Behavior

The script performs read-only LDAP queries. It keeps credentials and output rows transiently and prints results. No files or directory state are modified.

## Dependencies and Integration Points

It depends on Impacket LDAP helpers, `ldapasn1`, SAMR `UF_ACCOUNTDISABLE`, and Active Directory attributes. It shares the standard Impacket example authentication pattern with Kerberos, hashes, AES keys, and DC host/IP options.

## Risks and Edge Cases

The `-all` filter string is missing a closing parenthesis until the later append, which works but is easy to break. The requested-user clause uses `(sAMAccountName:=%s)`, an unusual LDAP matching syntax that may not behave as intended compared with `(sAMAccountName=%s)`. Times use local timezone, not UTC. Attribute decoding assumes present values. Large domains depend on paged result behavior via `ldap.SimplePagedResultsControl`.

## Test Signals

Unit tests should cover filter construction for default, `-all`, `-user`, and combined cases; FILETIME conversion; disabled account filtering intent; missing mail/logon attributes; and per-record formatting. Integration tests require AD users with and without mail and disabled status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/GetADUsers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/GetLAPSPassword.py -->
# sources/user-network-fs/impacket/examples/GetLAPSPassword.py

## Purpose

`GetLAPSPassword.py` extracts Microsoft LAPS and LAPSv2 passwords from Active Directory. It queries computer objects with legacy `ms-MCS-AdmPwd`, cleartext `msLAPS-Password`, or encrypted `msLAPS-EncryptedPassword`, decrypts LAPSv2 blobs through MS-GKDI when needed, and prints or writes a table of recovered passwords and expiration times.

## Important APIs, Types, and Functions

`GetLAPSPassword.printTable` formats console and optional tab-delimited file output. `__init__` stores credentials, Kerberos/hash options, target computer, LDAPS flag, output file, and a KDS cache. `getLAPSv2Decrypt` parses `EncryptedPasswordBlob`, CMS `EnvelopedData`, key identifiers, recipient info, obtains group key material with `GkdiGetKey`, derives KEK/CEK using `dpapi_ng`, and decrypts plaintext. `run` performs the LDAP search and result extraction.

## Control Flow

The CLI parses target identity, optional `-computer`, `-ldaps`, and output/authentication options. `run` logs into LDAP, builds a filter for computer objects with LAPS attributes, optionally restricts by name, and requests the relevant LAPS fields with a 1000-entry paged control. For each LDAP entry, it decodes the host name, decrypts LAPSv2 when `msLAPS-EncryptedPassword` is present, parses the decrypted JSON-like payload for username/password, handles expiration FILETIME fields, handles legacy `ms-MCS-AdmPwd`, accumulates rows, and prints the table.

## State and Persistence Behavior

The script reads LDAP attributes and, for encrypted LAPSv2, performs RPC calls to MS-GKDI. It caches `GroupKeyEnvelope` values by root key ID in memory. It may write recovered passwords to `-outputfile`. It does not modify AD state.

## Dependencies and Integration Points

It depends on Impacket LDAP, DCERPC transport/EPM/GKDI, DPAPI-NG helpers, pyasn1 CMS decoding, JSON parsing, and Active Directory LAPS/LAPSv2 schema. The `-ldaps` option is important for environments enforcing LDAP over SSL.

## Risks and Edge Cases

Recovered secrets are printed and optionally written in cleartext. `getLAPSv2Decrypt` can reference `key_id` or `laps_enabled` after parse exceptions, so malformed blobs can produce follow-on errors. GKDI cache assignment uses `gke['RootKeyId']`, which must match key identifier types. The decrypted plaintext is sliced with `[:-18]` before UTF-16LE JSON decoding, which assumes blob trailer shape. RPC auth level is set twice, ending at privacy. LDAP result processing catches per-entry errors and continues, which can hide systematic decryption failures.

## Test Signals

Unit tests should cover FILETIME conversion, table output, LAPSv2 blob parse/decrypt with known fixtures or mocks, GKDI cache hits, malformed blobs, legacy LAPS attribute extraction, and output file formatting. Integration tests require an AD/LAPS lab with permissions for both legacy and LAPSv2 reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/GetLAPSPassword.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/GetNPUsers.py -->
# sources/user-network-fs/impacket/examples/GetNPUsers.py

## Purpose

`GetNPUsers.py` finds users with Kerberos pre-authentication disabled and optionally requests AS-REP material for offline cracking in hashcat or John format. It also supports directly testing usernames from a file without LDAP authentication.

## Important APIs, Types, and Functions

`GetUserNoPreAuth.printTable` formats LDAP result rows. `getTGT(userName, requestPAC=True)` manually builds an AS-REQ with `KERB_PA_PAC_REQUEST`, requests RC4 first and AES if RC4 is unsupported, decodes AS-REP versus KRB-ERROR, and formats encrypted AS-REP data. `run` chooses users-file, no-password direct request, LDAP enumeration, or fallback direct request paths. `request_users_file_TGTs` and `request_multiple_TGTs` drive batch output.

## Control Flow

The CLI parses a domain identity, `-request`, `-usersfile`, output format, output file, and authentication/DC options. In users-file mode, the script reads usernames and requests AS-REPs. In `-no-pass` direct mode, it requests for the supplied user without LDAP. Otherwise it attempts LDAP login, searches for enabled non-computer users with `UF_DONT_REQUIRE_PREAUTH`, prints attributes, and if requested, asks the KDC for each user's AS-REP. If LDAP authentication fails for reasons other than `strongerAuthRequired`, it tries to request the current user's AS-REP.

## State and Persistence Behavior

The script performs LDAP reads and KDC AS exchanges. It may write hash lines to `-outputfile`. It does not modify AD state, but incorrect use without `-no-pass` can cause authentication attempts against user accounts as noted in the usage text.

## Dependencies and Integration Points

It depends on Impacket LDAP helpers, Kerberos ASN.1 types, `sendReceive`, `KerberosError`, pyasn1 encoding/decoding, SAMR UAC constants, and AD/KDC behavior. Output formats integrate with hashcat and John the Ripper.

## Risks and Edge Cases

The code assigns `entry = self.getTGT(...)` in some branches but then calls `request_multiple_TGTs`, duplicating the request and ignoring `entry`. LDAP enumeration uses `sizeLimit=999` and comments that paged queries are not implemented, so large domains can be incomplete. Error handling relies on exception strings for NTLM negotiation guidance. AS-REP output contains crackable secret material and output files should be protected. FILETIME conversion uses local time.

## Test Signals

Unit tests can mock `sendReceive` to return KRB-ERROR, RC4 AS-REP, and AES AS-REP and verify hash formatting. LDAP tests should cover search filter construction, size-limit fallback, per-record parsing, users-file mode, and output file writing. Integration tests need a KDC/AD lab with preauth-disabled accounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/GetNPUsers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/GetUserSPNs.py -->
# sources/user-network-fs/impacket/examples/GetUserSPNs.py

## Purpose

`GetUserSPNs.py` enumerates Active Directory service principal names associated with user or machine accounts and optionally requests Kerberos service tickets for Kerberoasting. It can output crackable TGS hashes, save ccache files, query cross-domain targets, process user/SPN lists, and support a no-preauth roasting path.

## Important APIs, Types, and Functions

`GetUserSPNs.printTable` formats LDAP rows. `getTGT` loads an existing ccache TGT or requests one, trying NTLM-derived RC4 material unless `-no-rc4` is set. `outputTGS` decodes `TGS_REP` or `AS_REP` and formats RC4, AES128, AES256, or DES tickets for cracking, with optional ccache save. `run` performs LDAP enumeration and optional TGS requests. `request_users_file_TGSs` and `request_multiple_TGSs` support list-driven operation.

## Control Flow

The CLI parses target identity, optional target domain, stealth/machine filters, request selectors, output/save options, and authentication settings. `run` logs into LDAP for the target domain, builds a filter for enabled person accounts by default or computer accounts with `-machine-only`; unless `-stealth` is set, it adds `servicePrincipalName=*`. It requests SPN and account metadata with a paged control, filters disabled accounts, prints rows, then if `-request`, `-request-user`, or `-request-machine` is active, obtains a TGT and requests one TGS per unique account. Users-file mode bypasses LDAP and requests tickets for supplied principals.

## State and Persistence Behavior

The script performs LDAP reads and Kerberos exchanges. It may write crackable hashes to `-outputfile` and ccache files named `<username>.ccache` when `-save` is set. It reads Kerberos credential caches through `CCache.parseFile`. It does not modify AD objects.

## Dependencies and Integration Points

It depends on Impacket LDAP helpers, Kerberos TGT/TGS APIs, ccache support, pyasn1 ticket decoding, NTLM hash derivation, AD UAC/delegation flags, and hashcat/John TGS formats. Cross-domain behavior intentionally ignores custom KDC host/IP to avoid breaking referral flows.

## Risks and Edge Cases

The script outputs and saves sensitive ticket material. In normal `run`, it requests TGS using a down-level account principal rather than the original SPN from the row, which is a deliberate account-targeted path but can surprise users expecting per-SPN tickets. `-stealth` can query huge account sets and warns about memory. Output file and ccache names may overwrite existing files. Several LDAP filters use extensible-match-like `sAMAccountName:=` syntax. Time formatting is local. Broad exception handling can continue after individual ticket failures.

## Test Signals

Unit tests should cover LDAP filter construction for person, machine-only, request-user, request-machine, and stealth modes; output formatting for each encryption type; ccache save paths; TGT fallback paths; and users-file mode. Integration tests need AD/Kerberos fixtures with SPNs, delegation flags, disabled accounts, and cross-domain trust cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/GetUserSPNs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/addcomputer.py -->
# sources/user-network-fs/impacket/examples/addcomputer.py

## Purpose

`addcomputer.py` adds, deletes, or changes the password of an Active Directory computer account using either SAMR over SMB or LDAPS. It implements the common machine-account quota path and supports Kerberos, NTLM hashes, AES keys, explicit DC host/IP, and custom OU placement for LDAPS.

## Important APIs, Types, and Functions

`ADDCOMPUTER.__init__` validates options, derives target/DC settings, normalizes computer names with trailing `$`, generates random passwords, derives base DN and computer container for LDAPS, and selects default ports. `run_samr` creates a SAMR DCERPC transport. `run_ldaps` uses `init_ldap_session` and LDAP add/modify/delete operations. `LDAPComputerExists`, `LDAPGetComputer`, and `generateComputerName` support LDAP mode. `doSAMRAdd` performs domain lookup, account existence checks, user creation/open/delete, password set, and workstation trust account control updates through SAMR calls.

## Control Flow

CLI parsing produces account credentials and action/method options. `run` dispatches to SAMR or LDAPS. SAMR mode connects to `\pipe\samr`, enumerates domains excluding Builtin, selects a domain, opens it with lookup/create rights, verifies target account existence for delete/password-reset or non-existence for add, creates or opens the user handle, deletes or sets the internal password, and for new accounts reopens the user to set workstation-trust UAC. LDAPS mode binds over LDAP SSL, validates existing or absent computer objects, then deletes, modifies `unicodePwd`, or adds a computer object with DNS hostname, SPNs, UAC, `sAMAccountName`, and password.

## State and Persistence Behavior

This script mutates Active Directory. It can create computer accounts, set/reset computer passwords, delete accounts, set SPNs/DNS hostnames, and assign UAC values. It logs generated computer passwords in cleartext. SAMR handles and LDAP connections are closed in finally paths where possible.

## Dependencies and Integration Points

It depends on Impacket SAMR/EPM/DCERPC transport, SPNEGO imports, Impacket LDAP session helpers, `ldap3`, Kerberos/NTLM credential handling, and AD domain policies such as machine account quota and LDAPS password-change requirements.

## Risks and Edge Cases

This is high-impact code because it changes AD objects. Generated passwords and provided passwords appear in logs. LDAPS object creation uses a caller-provided `computer_group` DN without escaping. SAMR domain selection can fail on multi-domain servers unless `-domain-netbios` is accurate. The import `ldap3_kerberos_login` is unused. Error handling logs critical messages but often swallows exceptions inside mode methods, so callers may not get a nonzero failure signal. Kerberos requires `-dc-host`, and target IP/name handling must be exact.

## Test Signals

Unit tests can mock SAMR and LDAP calls to verify option validation, generated names/passwords, SPN construction, base DN derivation, and error mapping for access denied/quota exceeded/not found. Integration tests require an AD lab and should verify add, no-add password reset, delete, SAMR versus LDAPS, Kerberos and NTLM, multi-domain selection, and cleanup of created accounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/addcomputer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/atexec.py -->
# sources/user-network-fs/impacket/examples/atexec.py

## Purpose

`atexec.py` executes a command on a remote Windows host through the Task Scheduler service over DCE/RPC named pipe `\pipe\atsvc`. It creates a temporary scheduled task running as LocalSystem, starts it, optionally captures output through `ADMIN$\Temp`, deletes the task, and cleans up the temporary output file.

## Important APIs, Types, and Functions

`TSCH_EXEC.__init__` stores credentials, Kerberos/hash/AES settings, command, optional session ID, and silent mode. `play(addr)` builds an `ncacn_np` TSCH transport and sets credentials. `doStuff(rpctransport)` contains output decoding, XML escaping, command splitting, DCERPC bind/authentication, task XML generation, registration, run/poll/delete, output retrieval, and cleanup. CLI code parses target, command, codec, keytab, and authentication settings.

## Control Flow

The script parses target credentials and command, optionally loads a keytab, prompts for password if needed, then calls `TSCH_EXEC.play`. `doStuff` connects to TSCH with packet privacy, creates a random task name and temp file name, wraps normal commands in `cmd.exe /C ... > %windir%\Temp\<tmp> 2>&1` unless session or silent mode changes behavior, registers the task XML, runs it, polls `SchRpcGetLastRunInfo` until the task has run, deletes the task, and if output is expected, reads the temp file via the SMB connection and deletes it.

## State and Persistence Behavior

The script mutates the remote host by creating and deleting a scheduled task and, in normal mode, creating and deleting a temp output file under `ADMIN$\Temp`. If cleanup fails, those artifacts can remain. Locally it may load a keytab but writes no files. It prints command output to stdout.

## Dependencies and Integration Points

It depends on Impacket TSCH DCERPC bindings, transport helpers, RPC auth constants, SMB connection access through the transport, target parsing, keytab support, and Windows Task Scheduler behavior on Vista or later.

## Risks and Edge Cases

Remote command execution is inherently high impact. XML escaping is local and must cover command/argument special characters; `-silentcommand` bypasses normal `cmd.exe` wrapping and output capture. The polling loop has no explicit timeout and can wait indefinitely if task status never updates. Output decoding depends on the chosen codec and may need manual code page mapping. Temporary task/file names can collide, though random eight-letter names reduce likelihood. Cleanup tries to delete created tasks in `finally`, but output files can remain on read/delete errors.

## Test Signals

Unit tests can mock TSCH and SMB calls to verify XML generation, escaping, command wrapping, session-id behavior, task cleanup on errors, and output decode fallback. Integration tests require a Windows target and should cover successful output capture, silent command, session run failure, Kerberos/keytab login, hash login, and cleanup after command failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/atexec.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/attrib.py -->
# sources/user-network-fs/impacket/examples/attrib.py

## Purpose

`attrib.py` queries or modifies Windows file and directory attributes over SMB without relying on remote shell execution. It supports SMB1 and SMB2/3 query/set information paths and exposes common file attribute flags as CLI options.

## Important APIs, Types, and Functions

`FileAttributes` is a dataclass holding boolean flags for known MS-FSCC file attributes. `pack` converts booleans to a bitmask, `unpack` creates an instance from a bitmask, and `__repr__` renders a compact attribute string. `attrib_query(connection, tid, fid)` reads basic file info using SMB1 or SMB2 structures. `attrib_set(connection, tid, fid, attribs)` writes basic file info with times set to zero and attributes set from the dataclass. `main` parses CLI, authenticates, opens the target file/directory, and dispatches query or set.

## Control Flow

After logging and argument parsing, the script validates the subcommand, parses the target identity, prompts for a password if needed, handles hashes/AES/Kerberos, connects to SMB, logs in, connects to the requested share, opens the normalized path with either `FILE_READ_ATTRIBUTES` or `FILE_WRITE_ATTRIBUTES`, and then queries or sets attributes. Query prints the compact attribute string plus share/path. Set builds `FileAttributes` from CLI booleans, calls `setInfo`, prints the new attributes, and finally closes the file, tree, and connection.

## State and Persistence Behavior

Query mode is read-only. Set mode mutates remote file or directory metadata. It does not persist local state. The code tries to close the file, disconnect the tree, and close the SMB session in a nested finally after successful connection/open.

## Dependencies and Integration Points

It depends on Impacket SMB connection APIs, SMB1 info classes, SMB2 `FILE_BASIC_INFORMATION`, NetBIOS default port constants, and example target parsing. It integrates with Windows/Samba filesystem metadata exposed via SMB.

## Risks and Edge Cases

Set mode writes a full attribute mask from only specified flags; omitted flags are cleared rather than preserving existing attributes. `FILE_ATTRIBUTE_NORMAL` semantics are special and can conflict with other flags, but the script leaves validation to the server. Time fields are set to zero in set structures; depending on SMB semantics this may preserve or alter timestamps. If `options.action` is invalid the script logs an error but does not immediately exit before later branching. Some attributes are represented in constants but not exposed as CLI set flags.

## Test Signals

Unit tests should cover `FileAttributes.pack/unpack/repr`, SMB1 versus SMB2 query/set structure selection, and CLI set-mask behavior. Integration tests should run query and set against a temporary file and directory on an SMB server and verify that only intended attributes change.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/attrib.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/badsuccessor.py -->
# sources/user-network-fs/impacket/examples/badsuccessor.py

## Purpose

`badsuccessor.py` is an Impacket example for delegated Managed Service Account (dMSA) and BadSuccessor-related Active Directory operations. It can search OUs for identities with rights that may enable the attack, add a dMSA linked to a target account, modify that link, or delete the dMSA.

## Important APIs, Types, and Functions

`BADSUCCESSOR.__init__` stores credentials, LDAP/LDAPS method, target/DC settings, action, dMSA options, base DN, target OU, principals allowed, target account, and DNS hostname. `run` initializes LDAP and dispatches `add_dmsa`, `delete_dmsa`, `modify_dmsa`, or `search_ous`. `search_ous` reads OU security descriptors and identifies relevant ACEs. `is_excluded_sid` and `resolve_sid_to_name` filter/resolve identities. `convert_sid_to_string` and `build_security_descriptor` construct dMSA membership descriptors. `add_dmsa`, `modify_dmsa`, and `delete_dmsa` perform LDAP mutations.

## Control Flow

The CLI validates action-specific required arguments, parses credentials via `parse_target` or `parse_identity`, initializes logging, then runs `BADSUCCESSOR`. `run` derives `baseDN`, chooses LDAP or LDAPS, handles Kerberos DC host/IP selection, binds through `init_ldap_session`, and dispatches. Search mode first looks for Windows Server 2025 domain controllers, then queries OUs with security descriptors, parses DACL ACEs for create-child/generic-all/write-DACL/write-owner rights and dMSA object-specific GUIDs, filters high-privilege built-in/domain admin SIDs, resolves remaining SIDs, and prints identities and OUs. Add mode builds a dMSA object and security descriptor for the allowed principal, resolves a target account DN, and adds the LDAP object. Modify mode replaces `msDS-ManagedAccountPrecededByLink`. Delete mode removes the object.

## State and Persistence Behavior

Search mode is read-only but reads security descriptors. Add/modify/delete modes mutate AD by creating, changing, or deleting dMSA objects and links. The script may create security descriptors granting rights to a selected principal. It keeps only in-memory LDAP connection and option state locally.

## Dependencies and Integration Points

It depends on `ldap3`, Impacket LDAP session helpers, Impacket `ldaptypes` security descriptor/ACE/SID structures, UUID conversion for object-specific ACE GUIDs, and AD schema features for `msDS-DelegatedManagedServiceAccount`. It is specifically tied to Windows Server 2025 dMSA behavior for exploitation relevance.

## Risks and Edge Cases

This is high-impact AD mutation code. LDAP filters interpolate user-supplied values without escaping, which can break searches or permit LDAP filter injection in lab tooling contexts. `if ('operatingSystem' and 'operatingSystemVersion') not in entry` is logically flawed because it only checks the second string. Domain SID may be undefined if lookup fails, yet later filtering references it. In `add_dmsa`, after finding a preferred user/computer target DN, the code immediately assigns the first entry DN again, potentially overriding the preference. Several exceptions are swallowed in OU parsing, which can hide descriptor parsing gaps. Search output is heuristic and does not prove exploitability by itself.

## Test Signals

Unit tests should cover SID conversion, security descriptor construction, excluded SID filtering, well-known SID resolution, object GUID parsing from ACEs, LDAP filter construction, add/modify/delete attribute dictionaries, and the target-DN selection bug. Integration tests require a Windows Server 2025 AD lab with OUs carrying specific ACEs and permissions to create/modify/delete dMSAs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/badsuccessor.py -->
