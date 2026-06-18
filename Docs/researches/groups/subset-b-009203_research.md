# subset-b-009203 Research

Grouped code research for subset `subset-b-009203`. Each section preserves the original source path and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/transfer-bench_test.go -->
# sources/sync-backup/syncthing/test/transfer-bench_test.go

Purpose: integration benchmark tests for Syncthing transfer throughput under the `integration && benchmark` build tags. The file creates either many small files or one very large file in `s1`, starts two local Syncthing instances, waits for synchronization into `s2`, verifies the result, and logs throughput plus per-process usage.

Important APIs/functions: `TestBenchmarkTransferManyFiles`, `TestBenchmarkTransferLargeFile{1,2,4,8,16,32}G`, `TestBenchmarkTransferSameFiles`, `setupAndBenchmarkTransfer`, `benchmarkTransfer`, and `cleanBenchmarkTransfer`. It depends on helper functions from `util.go` such as `generateFiles`, `generateOneFile`, `directoryContents`, `compareDirectoryContents`, `startInstance`, `checkedStop`, `removeAll`, and platform `printUsage`.

Control flow: benchmark setup removes old `s1`, `s2`, and instance indexes, generates input data, starts sender and receiver via `rc.Process`, resumes both, waits first for a receiver `ItemFinished` event, then waits for `rc.InSync("default", sender, receiver)`. It stops both processes before verification so resource usage is available.

State/persistence: mutates test directories `s1`, `s2`, Syncthing homes `h1`, `h2`, and log files through `startInstance`. It deliberately deletes generated state at both start and end.

Dependencies/integration: requires a built `../bin/syncthing`, configured test homes, Syncthing REST/event APIs from `lib/rc`, and the benchmark-only resource-usage implementation selected by OS.

Risks: very large tests allocate sparse/non-sparse files by copying repeated `../LICENSE` content, so disk pressure is the dominant operational risk. `total/1024/1024` is used as a divisor for per-MiB timing and usage; current benchmark sizes avoid zero, but small future benchmarks could divide by zero. Waiting for the first `ItemFinished` assumes at least one item will finish; the same-files benchmark may rely on event behavior despite no transfer.

Test signals: success requires no fatal test errors, in-sync REST state, byte/mode/mtime/hash directory comparison, and logged wall-time/KiB-per-second/resource metrics.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/transfer-bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/usage_unix.go -->
# sources/sync-backup/syncthing/test/usage_unix.go

Purpose: Unix-like implementation of benchmark resource reporting for Syncthing integration benchmarks, compiled under `integration && benchmark && !windows`.

Important APIs/functions: `printUsage(name string, proc *os.ProcessState, total int64)` extracts `*syscall.Rusage` from `ProcessState.SysUsage`, logs user CPU, system CPU, and maximum resident set size.

Control flow: if the process state exposes `syscall.Rusage`, it computes `mib := total / 1024 / 1024`, logs `Utime.Nano()/mib` and `Stime.Nano()/mib`, adjusts Darwin RSS units from bytes to KiB, then logs `Maxrss`.

State/persistence: no persistent state. It only reads OS-provided process usage after a child exits and writes benchmark log output.

Dependencies/integration: integrates with `transfer-bench_test.go` after `sender.Stop()` and `receiver.Stop()`. Uses Syncthing `build.IsDarwin` to normalize platform RSS semantics.

Risks: CPU-per-MiB division assumes `total >= 1 MiB`; current benchmark callers satisfy this, but generic reuse may not. Linux and Darwin report `Maxrss` in different units, and the code handles only the documented Darwin special case.

Test signals: benchmark output should include `Receiver` and `Sender` `Utime`, `Stime`, and `MaxRSS` lines on supported Unix platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/usage_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/usage_windows.go -->
# sources/sync-backup/syncthing/test/usage_windows.go

Purpose: Windows implementation of benchmark process CPU reporting for Syncthing transfer benchmarks, compiled under `integration && benchmark && windows`.

Important APIs/functions: `ftToDuration` converts a Windows `syscall.Filetime` to `time.Duration`, although current code uses the `Nanoseconds()` methods on `Rusage.UserTime` and `KernelTime`. `printUsage` logs user and kernel time per MiB.

Control flow: `printUsage` type-asserts `proc.SysUsage()` to `*syscall.Rusage`, computes MiB from total transferred bytes, and logs user/kernel time normalized by transfer size.

State/persistence: no filesystem or process state mutation; it reads the already-finished child process state.

Dependencies/integration: called by `benchmarkTransfer` in the benchmark file after stopping sender and receiver. It depends on Windows Go runtime support for `ProcessState.SysUsage`.

Risks: `ftToDuration` is dead code and may indicate an older conversion path. As with Unix, `mib` must be nonzero. No RSS/memory metric is logged on Windows, so cross-platform benchmark comparisons are CPU-only there.

Test signals: benchmark logs should show `Utime` and `Stime` per MiB for each Syncthing process on Windows.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/usage_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/test/util.go -->
# sources/sync-backup/syncthing/test/util.go

Purpose: shared Syncthing integration-test utilities for deterministic file generation, mutation, directory comparison, process startup, cleanup, timeout detection, and remote sync checks.

Important APIs/functions: generation helpers `generateFiles`, `generateFilesWithTime`, `generateOneFile`, `ReadRand`, `randomName`, and `infiniteReader`; mutation helper `alterFiles`; cleanup `removeAll`; comparison helpers `compareDirectories`, `directoryContents`, `mergeDirectoryContents`, `compareDirectoryContents`, `startWalker`, `sha256file`, and `fileInfo`; process helpers `startInstance`, `checkedStop`, `getTestName`, `isTimeout`, `symlinksSupported`, and `checkRemoteInSync`.

Control flow: file generation opens a seed file and repeats it through `infiniteReader`, creating randomized names, modes, sizes, and mtimes. Directory walking emits canonical `fileInfo` records through channels and hashes regular files. Comparison sorts or pairwise compares these records. Instance startup builds REST addresses and log names, starts `../bin/syncthing` with per-instance home directories, awaits startup, and pauses folders for controlled tests.

State/persistence: writes trees under caller-supplied dirs, changes modes and mtimes, deletes globbed paths, creates logs under `logs/`, and uses Syncthing homes `hN`. Randomness is seeded in `init()` for repeatability, with some tests explicitly reseeding.

Dependencies/integration: relies on Go stdlib filesystem APIs, `crypto/sha256`, Syncthing `build` platform flags, and `lib/rc` process/REST helpers. `checkRemoteInSync` uses remote device status from running instances.

Risks: `removeAll` expands globs and recursively chmods before deletion, so callers must pass constrained paths. `alterFiles` intentionally races against walking and ignores some disappeared paths. Directory comparison includes Unix mode and second-level mtimes, which may be platform-sensitive. `startWalker` closes shared channels, so `compareDirectories` assumes all walkers are consumed uniformly.

Test signals: generated trees are verified by SHA-256, size, mode, symlink target hash, and coarse mtime; process helpers fail tests immediately on startup/stop errors; remote sync helper returns explicit device/folder mismatch errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/test/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/.github/ISSUE_TEMPLATE/config.yml -->
# sources/sync-backup/unison/.github/ISSUE_TEMPLATE/config.yml

Purpose: GitHub issue-template configuration for the Unison repository.

Important fields: `blank_issues_enabled: false` disables unstructured issues. `contact_links` sends help questions and not-fully-designed feature requests to the Unison mailing-list wiki page.

Control flow: no executable control flow; GitHub consumes this YAML when rendering the new issue UI.

State/persistence: repository metadata only. It changes user workflow in GitHub but does not affect source builds.

Dependencies/integration: depends on GitHub issue template semantics and external wiki URL availability.

Risks: disabling blank issues can reduce low-quality reports but may also block useful reports if structured templates are missing or too restrictive. External mailing-list links can rot.

Test signals: manual GitHub UI validation is the relevant check; CI does not exercise this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/.github/workflows/CI.yml -->
# sources/sync-backup/unison/.github/workflows/CI.yml

Purpose: primary GitHub Actions CI/release workflow for Unison on pull requests and pushes. It builds docs, native/text/GUI binaries, package artifacts, release uploads, RPC ABI compatibility tests, dune builds, bytecode builds, and older-compiler compatibility builds.

Important jobs: `docs` builds manual artifacts with OCaml 4.14, HeVeA, lynx, and TeX; `build` runs a platform matrix across macOS, Ubuntu, Windows MinGW/MSVC, i386 variants, OCaml 4.14 and 5.x, packages binaries, and optionally publishes release assets; `rpc_abicheck` checks new/old client/server interoperability against tagged versions; `opam_dune_build` verifies dune/opam packaging; `bytecode_build` validates non-native builds; `build_compat` covers older OCaml and static/musl packaging.

Control flow: `build` depends on `docs` but runs even if docs failed via `if: !cancelled()`. A `vars` step derives executable suffixes, Windows architecture, staging paths, ref/tag metadata, package names, compression commands, and make implementation. Platform-specific sections install multilib, GTK, lablgtk, patch Windows MSVC opam packages, build `tui fsmonitor`, run self-tests over sockets, build GUI/mac UI, stage docs, strip binaries, collect DLLs/framework support files, package, upload artifacts, and publish tagged releases.

State/persistence: creates `_staging`, package directories, `pkg`, `_new`, `_prev`, local sockets, test backup dirs, GTK cache, `_opampkgs`, generated archives, and GitHub artifacts/releases.

Dependencies/integration: uses `actions/checkout`, `ocaml/setup-ocaml`, cache, upload/download-artifact, setup-python, `softprops/action-gh-release`, OS package managers, opam, make/nmake, lablgtk3, gvsbuild, dumpbin/objdump, and Unison self-tests.

Risks: high matrix complexity and many pinned workarounds for runner, opam, GTK, cairo, pkg-config, MSVC, and MinGW behavior. Release gating relies on tag parsing and `publish` matrix flags. Windows GTK packaging is fragile because dependency discovery and architecture selection depend on PATH ordering. The RPC compatibility patching embeds historical source diffs that can drift.

Test signals: successful docs artifacts, `make test`, local/RPC self-tests, GUI build completion, package creation, artifact uploads, ABI smoke tests in both client/server directions, dune build, bytecode test run, and release upload on version tags.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/.github/workflows/CI.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/Makefile -->
# sources/sync-backup/unison/Makefile

Purpose: portable top-level Unison make entrypoint compatible with GNU Make, BSD make, Solaris make/dmake, and NMAKE.

Important targets: `all` builds `src` and `manpage`; `src` recursively invokes `$(MAKE)` in `src`; `tui`, `gui`, `macui`, `fsmonitor`, `manpage`, `docs`, `clean`, and `depend` delegate to `src`; `test` runs `ocaml src/make_tools.ml run ./src/unison -ui text -selftest`; `install` runs `ocaml src/make_tools.ml install`.

Control flow: intentionally recursive and `.NOTPARALLEL` because portability requires multiple recursive make invocations. `FRC` is used for phony-like behavior on make implementations that do not handle `.PHONY` consistently.

State/persistence: build outputs are created under `src`, docs/manpage outputs through delegated targets, and install writes through `make_tools.ml` according to install variables.

Dependencies/integration: relies on `src/Makefile`, OCaml, `src/make_tools.ml`, and platform make semantics.

Risks: parallelism is disabled at the top level to avoid recursive-make races. Any edit here must preserve non-GNU syntax portability; even convenient GNU-only features can break supported build environments.

Test signals: `make`, `make tui`, `make gui`, `make fsmonitor`, `make test`, and `make install DESTDIR=...` are the relevant checks across supported make implementations.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/data/unison-gui.desktop -->
# sources/sync-backup/unison/data/unison-gui.desktop

Purpose: freedesktop desktop-entry metadata for launching the Unison GUI on Linux/Unix desktop environments.

Important fields: `Type=Application`, `Exec=unison-gui`, `Name=Unison`, `GenericName=File Synchronizer`, `Comment=GUI for Unison file synchronizer`, `Terminal=false`, `Icon=unison-gui`, `StartupNotify=true`, and `Categories=Utility`.

Control flow: no executable code; desktop shells parse the file to display and launch the GUI.

State/persistence: installed as packaging/desktop metadata. It does not alter runtime state except by launching `unison-gui`.

Dependencies/integration: depends on installed `unison-gui` binary and matching icon theme resource.

Risks: packaging must ensure the executable and icon names match installed paths. If distributions rename binaries, this file must be patched.

Test signals: desktop-file validation and manual launcher test are sufficient; CI packaging may indirectly include it.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/data/unison-gui.desktop -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/dev/check-memory -->
# sources/sync-backup/unison/dev/check-memory

Purpose: POSIX shell developer experiment to estimate memory/stack limits needed for Unison syncs with many files.

Important functions: `log`, `fatal`, `goto_dir`, `fini`, `init_N_M`, `touch_N_M_all`, `limit`, `limit_display`, `start_server`, `do_sync`, `simple_test`, and `all`.

Control flow: creates `/tmp/UNISON-TEST`, initializes `local` with `N*M` files, applies `ulimit` constraints for data/RSS/stack, starts a socket-mode Unison server with isolated `UNISON` archive directories, runs a batch sync, touches every local file, runs a second sync, logs parseable `sync` result lines, then removes generated state.

State/persistence: owns `/tmp/UNISON-TEST`, `local`, `remote`, `.unison.local`, `.unison.remote`, and socket `s`. It refuses to start if `local` or `remote` already exists to avoid accidental data loss.

Dependencies/integration: requires `unison` in PATH, POSIX shell tools, `seq`, `find`, `date`, `ulimit`, and socket support.

Risks: comments note it is a work in progress. `ulimit` flags vary substantially by OS and may not constrain malloc consistently. Cleanup uses `rm -rf` but checks the parent directory first. Remote process limits are not separately controlled.

Test signals: parseable log lines include test name, file counts, memory/stack limits, and Unison exit status for initial and touch-all syncs.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/dev/check-memory -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/dev/ktrace-netbsd -->
# sources/sync-backup/unison/dev/ktrace-netbsd

Purpose: NetBSD developer script to trace executable/path usage during Unison build, install, and clean phases.

Important flow: validates it is run at the Unison source top level by checking `src/Makefile.OCaml`, runs `make clean`, removes old `ktrace*`, traces `make`, traces `make DESTDIR=/tmp/U install`, traces `make clean`, dumps traces with `kdump`, extracts `NAMI` path records, normalizes `/usr` and `/pkg`, filters bin/sbin paths, counts unique entries, and writes `NAMI.txt`.

State/persistence: creates `ktrace-make.txt`, `ktrace-install.txt`, `ktrace-clean.txt`, `NAMI.txt`, and `/tmp/U`. It intentionally avoids deleting `/tmp/U`.

Dependencies/integration: NetBSD `ktrace`, `kdump`, `egrep`, `awk`, `sed`, `sort`, `uniq`, and a working Unison make build.

Risks: NetBSD-specific and intentionally not portable. The path normalization is heuristic and focused on bin-like directories. `/tmp/U` may already exist or accumulate files.

Test signals: useful output is `NAMI.txt`, a counted list of command paths observed during build/install/clean.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/dev/ktrace-netbsd -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/dev/test-limits.c -->
# sources/sync-backup/unison/dev/test-limits.c

Purpose: tiny C helper for probing process memory limits by allocating memory until `malloc` fails.

Important API: `main` loops up to 4 GiB in 4 KiB chunks, writes the first int of each allocation to force a touched page, intentionally discards the pointer, and prints allocated KiB.

Control flow: allocation continues until failure or the fixed 4 GiB ceiling is reached. There is no cleanup because the process exits immediately after printing.

State/persistence: no files; it consumes address space and memory pages during the process lifetime.

Dependencies/integration: standard C library only. Intended to be compiled and run under different `ulimit`/`setrlimit` settings.

Risks: intentionally leaks every successful allocation. The hard cap prevents unbounded growth if limits are ineffective, but running it can still stress memory. It measures rough allocation behavior, not Unison-specific memory use.

Test signals: stdout numeric KiB value indicates observed allocation ceiling.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/dev/test-limits.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/doc/Makefile -->
# sources/sync-backup/unison/doc/Makefile

Purpose: portable makefile for generating Unison manual outputs and OCaml embedded help strings.

Important targets/variables: `all` builds `unison-manual.pdf`, `.html`, `.txt`, and `../src/strings.ml`; `m=unison-manual`; `DRAFT=false`; includes `../src/Makefile.ProjectInfo`; `SOURCES` includes manual TeX, local/short TeX, generated version/preferences files; `HEVEA_FOUND` gates HeVeA-dependent outputs.

Control flow: writes `unisonversion.tex` from `VERSION`, generates separate directive files for text and non-text builds, uses HeVeA plus lynx to make text, uses `docs.ml` to derive `strings.ml`, runs `pdflatex` twice in draft mode for aux/toc and once for PDF, uses HeVeA for HTML, and generates preference listings by running `../src/$(NAME)`.

State/persistence: creates TeX aux/toc/log files, manual `.pdf/.html/.txt/.dtxt`, `prefs.tmp`, `prefsdocs.tmp`, `unisonversion.tex`, directive files, and `../src/strings.ml`.

Dependencies/integration: requires built Unison text binary for preference extraction, OCaml for `docs.ml`, HeVeA, lynx, pdflatex, and make portability features.

Risks: uses GNU group target syntax `&:` with BSD/Solaris compatibility comments; edits must preserve portability. If HeVeA is missing, some targets silently do little, which can leave stale outputs.

Test signals: CI `docs` job runs `opam exec -- make -j 2 docs` and uploads manual text/html/pdf plus generated manpage.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/doc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/man/unison.1.in -->
# sources/sync-backup/unison/man/unison.1.in

Purpose: mandoc template for the Unison `unison(1)` manual page.

Important content: name/synopsis/description, generated placeholders `@OPTIONS_SHORT@` and `@OPTIONS_FULL@`, root URI grammar, path/pathspec syntax, profiles, termination signals, environment variables, files, examples, exit statuses, compatibility notes, and links to the full manual.

Control flow: no program control flow. Build tooling substitutes option placeholders and emits `man/unison.1`.

State/persistence: documents Unison state locations such as `$UNISON`, `~/.unison/*.prf`, archive files, fingerprint caches, and locks. Also documents command behavior for socket, ssh, file, local roots, continuous sync, and GUI limitations.

Dependencies/integration: integrates with the documentation/manpage generation target and must stay aligned with actual preferences and runtime behavior.

Risks: stale documentation can mislead users about path grammar, environment variables, exit status semantics, and compatibility. The generated option placeholders are critical; if substitution fails the manpage is incomplete.

Test signals: docs CI should generate `man/unison.1`; manual review should compare documented options with `-help`/`-prefsdocs` output and self-test behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/man/unison.1.in -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/Makefile -->
# sources/sync-backup/unison/src/Makefile

Purpose: portable source-level make dispatcher that generates configuration makefiles and delegates real builds to `Makefile.OCaml`.

Important targets: default `all`; BSD `.BEGIN`, Solaris `.INIT`, and generic `Makefile.cfg` rules all run `ocaml make_tools.ml conf` and `conf2`; target set includes `all`, `tui`, `gui`, `macui`, `fsmonitor`, `manpage`, `docs`, `clean`, `depend`, `dependgraph`, and `paths`; developer `tags` target runs etags.

Control flow: generated `Makefile.cfg` and `Makefile2.cfg` are prerequisites for delegated targets. The file avoids directly including freshly generated config because non-GNU make implementations read includes before generating them.

State/persistence: creates `_mk.cfg`, `Makefile.cfg`, `Makefile2.cfg`, build products (`unison`, `unison.exe`, GUI/fsmonitor binaries), and tags.

Dependencies/integration: depends on OCaml, `make_tools.ml`, `Makefile.OCaml`, and make-specific hooks. The trailing fsmonitor object/library definitions look like included fragments for platform-specific fsmonitor builds.

Risks: portability is the primary constraint. Direct inclusion or GNU-only conveniences can break BSD/Solaris/NMAKE. `.NOTPARALLEL` is used because recursive generated configuration is fragile under parallelism.

Test signals: cross-platform CI matrix exercises this file through top-level `make`, `make tui`, `make gui`, `make fsmonitor`, and Windows `nmake`.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/bytearray_stubs.c -->
# sources/sync-backup/unison/src/bytearray_stubs.c

Purpose: OCaml C stubs for copying between OCaml byte/string values and Bigarray-backed buffers.

Important APIs: `ml_blit_bytes_to_bigarray`, `ml_blit_string_to_bigarray`, and `ml_blit_bigarray_to_bytes`. `Array_data(a,i)` computes a byte pointer into `Caml_ba_data_val(a)` plus an OCaml integer offset.

Control flow: each stub extracts source/destination pointers from OCaml values, calls `memcpy` for `Long_val(l)` bytes, and returns unit. The string variant delegates to the bytes variant.

State/persistence: mutates only caller-provided OCaml bytes or bigarray memory; no external state.

Dependencies/integration: includes `caml/bigarray.h` and `caml/memory.h`. Used by OCaml code needing efficient buffer transfers without per-byte copying.

Risks: no bounds checks are performed in C; correctness depends on OCaml callers passing valid offsets/lengths. `memcpy` is unsafe for overlapping ranges, though intended use is between distinct storage classes.

Test signals: buffer roundtrip tests should verify exact copied contents and boundary behavior from the OCaml side.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/bytearray_stubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/copy_stubs.c -->
# sources/sync-backup/unison/src/copy_stubs.c

Purpose: platform-specific OCaml C stubs for efficient file clone/copy operations.

Important APIs: `unison_clone_path(src,dst)` for macOS `clonefile`; `unison_clone_file(in_fd,out_fd)` for Linux `FICLONE`; `unison_copy_file(in_fd,out_fd,in_offs,len)` for Linux `copy_file_range`/`sendfile`, FreeBSD `copy_file_range`, Solaris `sendfile`, Windows ReFS `FSCTL_DUPLICATE_EXTENTS_TO_FILE`, or `ENOSYS` fallback.

Control flow: clone APIs must never raise and return boolean success. Copy APIs release the OCaml runtime around blocking syscalls, return copied byte count, or raise Unix errors. Linux tries `copy_file_range` first, then `sendfile` on unsupported/cross-device-like failures. Windows validates block-clone support on both handles, reads integrity/cluster size, checks cluster alignment, toggles sparse status when needed, extends destination length, performs extent duplication, and advances the output file pointer manually.

State/persistence: changes destination file contents, length, sparseness, and file offset. Source offset is protected by explicit offsets where platform APIs allow.

Dependencies/integration: OCaml runtime/unixsupport compatibility shims, OS clone/copy syscalls, Windows HANDLE APIs, MinGW compatibility typedefs, and filesystem support such as APFS/ReFS/Btrfs/XFS.

Risks: platform behavior is subtle: partial `sendfile`, cluster-alignment requirements on Windows, unsupported filesystem paths, sparse toggling, and offset semantics differ. Windows code assumes source and destination cluster size compatibility on the same ReFS volume.

Test signals: copy tests should cover unsupported fallback, partial return handling, offset preservation, output offset advancement, sparse files, cross-device behavior, large files, and Windows aligned/unaligned extents.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/copy_stubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/fsmonitor.py -->
# sources/sync-backup/unison/src/fsmonitor.py

Purpose: legacy Python filesystem monitor helper for Unison, supporting Linux pyinotify, macOS FSEvents, and Windows pywin32 `ReadDirectoryChangesW`.

Important functions/classes: logging helpers `mydebug`/`mymesg`; path conversion `relpath`, `my_abspath`, `mangle_filename`, `make_symlinks`, `update_follow`; config parser `conf_parser`; Linux `HandleEvents` and `linuxwatcher`; macOS `filelevel_approx`, `fsevents_callback`, `my_FSEventStreamCreate`, `macosxwatcher`; Windows `win32watcherThread` and `win32watcher`; CLI setup in `__main__`.

Control flow: parses either a root/path list or a Unison profile, resolves local roots/paths/follow directives, truncates the changes file, starts a stdin-watchdog thread that exits when parent closes stdin, then dispatches to the platform watcher. Events are converted to root-relative paths and appended to the configured changes file.

State/persistence: writes change log and macOS state file under the Unison config directory, maintains in-memory symlink-follow maps, and watches recursive directory trees.

Dependencies/integration: Python 2 syntax (`print >>`, `dict.has_key`), pyinotify, PyObjC FSEvents bindings, pywin32, Unison profile semantics, and the external fsmonitor protocol that reads the changes file.

Risks: Python 2 dependency is obsolete. Event coalescing and dropped-event paths can force broad rescans. Symlink-follow handling is partial, especially deletion of followed links. Windows writes binary-mode strings and relies on daemon threads.

Test signals: platform manual tests should verify profile parsing, follow directives, relative path output, dropped-event recovery, stdin-triggered exit, and change-file consumption by Unison.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/fsmonitor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/fsmonitor/inotify/Makefile -->
# sources/sync-backup/unison/src/fsmonitor/inotify/Makefile

Purpose: small platform fragment for Linux inotify fsmonitor build inputs.

Important variables: `FSMOCAMLOBJS` lists Lwt, Unix implementation, inotify OCaml modules, watcher common code, and watcher implementation; `FSMCOBJS` includes `inotify_stubs.o`; `FSMOCAMLLIBS=unix.cma`.

Control flow: no rules, only variable definitions consumed by the surrounding build system.

State/persistence: contributes object dependencies for building `unison-fsmonitor`.

Dependencies/integration: integrates with `src/Makefile`/`Makefile.OCaml`, OCaml bytecode objects, and the C inotify stub.

Risks: object ordering can matter for OCaml linking. Missing any Lwt or inotify object breaks fsmonitor builds.

Test signals: Linux `make fsmonitor` and CI build steps that copy `src/unison-fsmonitor`.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/fsmonitor/inotify/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/fsmonitor/inotify/inotify_stubs.c -->
# sources/sync-backup/unison/src/fsmonitor/inotify/inotify_stubs.c

Purpose: OCaml C bindings for Linux inotify used by Unison fsmonitor.

Important APIs: `stub_inotify_init`, `stub_inotify_ioctl_fionread`, `stub_inotify_add_watch`, `stub_inotify_rm_watch`, `stub_inotify_struct_size`, and `stub_inotify_convert`. Flag tables map OCaml flag-list indexes to inotify masks and returned event masks.

Control flow: initialization opens an inotify fd; add/remove watch convert OCaml flag lists and call inotify APIs; `FIONREAD` reports available bytes; conversion copies one `struct inotify_event` from an OCaml string and constructs an OCaml tuple `(wd, flags, cookie, len)`.

State/persistence: kernel inotify watch state exists behind the returned fd and watch descriptors. No file state is changed.

Dependencies/integration: Linux `<sys/inotify.h>`, OCaml unixsupport error mapping, and fsmonitor OCaml modules that read raw event buffers and names.

Risks: `inotify_init` lacks `IN_CLOEXEC`/nonblocking flags here. `stub_inotify_convert` assumes the buffer contains at least one full event header. `IN_EXCL_UNLINK` is treated as zero if unavailable, reducing behavior on old headers.

Test signals: fsmonitor tests should add/remove watches, trigger create/delete/modify/move events, verify flag decoding and cookie propagation, and handle queue overflow.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/fsmonitor/inotify/inotify_stubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/fsmonitor/solaris/Makefile -->
# sources/sync-backup/unison/src/fsmonitor/solaris/Makefile

Purpose: Solaris/illumos fsmonitor build fragment.

Important variables: `FSMOCAMLOBJS` includes Lwt, generic Unix Lwt implementation, watcher common code, `ubase/safelist.cmo`, and the Solaris watcher; `FSMCOBJS` includes `fen_stubs.o`; `FSMOCAMLLIBS=unix.cma`.

Control flow: variable-only make fragment consumed by the main build.

State/persistence: controls which OCaml and C objects are linked into the fsmonitor binary on Solaris-like platforms.

Dependencies/integration: relies on Solaris event ports/FEN C stubs and OCaml watcher modules.

Risks: object list must stay synchronized with watcher implementation dependencies; portable make syntax is required.

Test signals: Solaris/illumos `make fsmonitor` and runtime file-event tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/fsmonitor/solaris/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/fsmonitor/solaris/fen_stubs.c -->
# sources/sync-backup/unison/src/fsmonitor/solaris/fen_stubs.c

Purpose: OCaml C bindings for Solaris/illumos file event notification via event ports.

Important APIs: `unsn_port_create`, `unsn_port_close`, `unsn_port_associate`, `unsn_port_reassociate`, `unsn_port_dissociate`, `unsn_port_get`, and `unsn_free_event_object`. `event_obj` stores a cookie, previous event mask, and `struct file_obj`.

Control flow: association allocates an `event_obj`, stores a duplicated path in `fo_name`, and calls `port_associate` with follow/no-follow event masks. Events are one-shot; `unsn_port_get` queries event count, allocates an event array, converts `PORT_SOURCE_FILE` events to OCaml tuples including port, event object pointer, cookie, and decoded flags. Reassociation returns false rather than raising for disappeared paths.

State/persistence: holds malloc-managed event objects that remain valid while associated. The OCaml side must free after event or dissociation. Kernel event-port registrations are mutated.

Dependencies/integration: Solaris `<port.h>`, file event flags, OCaml runtime, and the Solaris watcher implementation.

Risks: raw pointers are encoded as OCaml immediate-like values without custom finalizers, so misuse can cause double free/use-after-free. Comments call out this tradeoff. Event loss around recursive deletes is handled by false reassociation, not guaranteed delivery.

Test signals: tests should cover associate/get/reassociate/dissociate/free lifecycles, deleted-path reassociation, no-follow behavior, event flag decoding, and memory tooling for pointer lifecycle mistakes.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/fsmonitor/solaris/fen_stubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/fsmonitor/windows/Makefile -->
# sources/sync-backup/unison/src/fsmonitor/windows/Makefile

Purpose: Windows fsmonitor build fragment.

Important variables: `FSMOCAMLOBJS` includes marshalling, regex/unicode support, Windows system modules, Lwt Windows modules, watcher common code, and Windows watcher; `FSMCOBJS` includes bytearray, Windows system, Lwt, xattr, ACL, and copy stubs; dependencies ensure watcher objects wait for `lwt/win/lwt_win`.

Control flow: no executable rules beyond dependency declarations consumed by the parent build.

State/persistence: determines object linkage for Windows `unison-fsmonitor`.

Dependencies/integration: ties together Windows system wrappers, async Lwt stubs, property stubs, and watcher code.

Risks: Windows fsmonitor depends on many native stubs; missing one can link but fail at runtime if optional external declarations drift. Object extensions use `$(OBJ_EXT)` for compiler portability.

Test signals: Windows CI `make fsmonitor`, local `unison-fsmonitor.exe` startup, and watcher integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/fsmonitor/windows/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/hash_compat.c -->
# sources/sync-backup/unison/src/hash_compat.c

Purpose: preserved pre-OCaml-4 universal hash implementation for Unison archive/version compatibility.

Important API: `unsn_hash_univ_param(count, limit, obj)` initializes `hash_state`, recursively hashes an OCaml value with historical `Alpha` and `Beta` combine constants, and returns a positive 30-bit value stable across 32/64-bit architectures.

Control flow: `hash_aux` decrements traversal limits, handles immediate ints, non-heap pointers, strings, doubles, double arrays, abstract/infix/forward/object/custom blocks, closure blocks under `NO_NAKED_POINTERS`, and generic blocks recursively.

State/persistence: no external state. The persistence concern is semantic: hash output affects compatibility with stored archives or protocols.

Dependencies/integration: OCaml runtime internals and tags. Comments warn removal will break Unison version compatibility and must wait for long user upgrade windows.

Risks: depends on OCaml runtime representation details. Compatibility value is high, so refactoring or replacing it can silently invalidate archives or cross-version behavior. Naked-pointer/no-naked-pointer runtime differences are explicitly conditional.

Test signals: regression vectors comparing known OCaml values to historical hash results on 32-bit/64-bit and old/new compiler configurations.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/hash_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/lwt/lwt_unix_stubs.c -->
# sources/sync-backup/unison/src/lwt/lwt_unix_stubs.c

Purpose: Windows-focused OCaml C stubs for Unison’s bundled Lwt/Unix async I/O, plus buffer blits, sockets, named pipes, directory-change notifications, and path helpers.

Important APIs: buffer blits `ml_blit_*_buffer`; completion management `init_lwt`, `win_wait`, `get_queue`; fd wrapping `win_wrap_fd`, `win_wrap_overlapped`, `win_kill_threads`; async I/O `win_read`, `win_write`; socket wait helpers `win_register_wait`, `win_check_connection`, `win_socket`; named pipe helpers `win_pipe_in/out`; watcher helpers `win_readdirtorychanges`, `win_parse_directory_changes`, `win_open_directory`; path helper `win_long_path_name`.

Control flow: overlapped handles use `ReadFileEx`/`WriteFileEx` with APC completion callbacks. Synchronous handles queue work to helper threads that call blocking `ReadFile`/`WriteFile`, then queue an APC back to the main thread. Completions are stored in a dynamically resized queue and drained into an OCaml callback from `win_wait`.

State/persistence: global completion callback root, completion queue, helper thread handles, main thread handle, dummy event, and pipe serial. Kernel handles and sockets are allocated and returned to OCaml.

Dependencies/integration: Windows Winsock2/Win32 APIs, OCaml runtime compatibility macros, Bigarray buffers, and Unison's Lwt OCaml layer.

Risks: global queue is not obviously synchronized beyond intended main/APC threading. Helper thread lifecycle must be killed to avoid leaks. `win_readdirtorychanges` name contains a typo that likely matches existing OCaml external binding. Buffer offsets are unchecked in C.

Test signals: Windows tests should exercise async read/write, waits/timeouts, socket connect/accept readiness, directory-change parsing, long-path normalization, named-pipe inheritance/cloexec, and clean helper-thread shutdown.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/lwt/lwt_unix_stubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/osxsupport.c -->
# sources/sync-backup/unison/src/osxsupport.c

Purpose: macOS-specific OCaml C stubs for Finder info and resource fork metadata.

Important APIs: `isMacOSX`, `getFileInfos(path, need_size)`, and `setFileInfos(path, fInfo)`.

Control flow: on Apple platforms, `getFileInfos` calls `getattrlist` for `ATTR_CMN_FNDRINFO` and optionally `ATTR_FILE_RSRCLENGTH`, validates returned buffer length, and returns a pair of 32-byte Finder info string and int64 resource fork length. `setFileInfos` calls `setattrlist`; on `EACCES`, it temporarily adds owner-write permission, retries, and restores the original mode.

State/persistence: reads and writes macOS Finder metadata and may briefly chmod read-only files while setting metadata.

Dependencies/integration: Apple `getattrlist`/`setattrlist`, OCaml Unix error mapping, and higher-level Unison property synchronization.

Risks: temporary chmod has failure windows if restoration fails or another process observes the mode. Non-Apple builds raise `ENOSYS`. Buffer-size validation is strict and can fail if OS API shape changes.

Test signals: macOS tests should verify Finder info/resource fork size roundtrip, read-only file metadata updates, and `ENOSYS` behavior on non-macOS.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/osxsupport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/props_acl.c -->
# sources/sync-backup/unison/src/props_acl.c

Purpose: platform-specific ACL synchronization stubs for Unison.

Important APIs: `unison_acl_from_text(path, acl)` sets/removes ACLs; `unison_acl_to_text(path)` returns deterministic ACL text, empty string for no/trivial ACL, or `"-1"` for unsupported paths/platforms.

Control flow: unsupported platforms no-op on set and return not-supported. Windows converts SDDL to a security descriptor, applies DACL/protection flags with `SetNamedSecurityInfoW`, and when reading removes inherited ACEs before serializing SDDL. Unix-like code supports Solaris, FreeBSD, NetBSD, and Darwin using native ACL APIs, choosing NFSv4/POSIX/extended ACL types, stripping ACLs on empty input, normalizing text output, and detecting trivial ACLs.

State/persistence: mutates filesystem ACL metadata. Windows ignores inherited ACEs because they cannot be restored independently. Unix removals may strip ACLs back to mode-derived/trivial state.

Dependencies/integration: Windows ACL/SDDL APIs, Solaris ACL APIs, BSD/Darwin `<sys/acl.h>`, pathconf ACL capability checks, OCaml Failure exceptions, and `props.ml` archive/property logic.

Risks: ACL text is intentionally platform-specific, limiting cross-platform ACL sync. Subject identity mapping is hard, especially Windows SIDs versus Unix users/groups. Raw native normalization differences can cause repeated sync diffs. Windows access denied often needs restore/admin privileges.

Test signals: same-platform ACL roundtrip tests, inherited-ACE stripping tests, empty/trivial ACL detection, unsupported path behavior, permission-denied reporting, and cross-filesystem capability checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/props_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/props_xattr.c -->
# sources/sync-backup/unison/src/props_xattr.c

Purpose: extended-attribute synchronization stubs for Unison across Linux, BSDs, macOS, and Solaris/illumos.

Important APIs: `unison_xattr_set`, `unison_xattr_remove`, `unison_xattr_get`, `unison_xattrs_list`, and `unison_xattr_updates_ctime`. Unsupported platforms raise the registered OCaml exception `XattrNotSupported`.

Control flow: Linux mangles attribute names by stripping `user.` and prefixing non-user namespaces with `!`; other platforms pass names directly. Set/remove/get call platform APIs (`setxattr`, `extattr_*`, `attropen`, etc.), skipping system attributes. Get first queries length, retries up to ten times on Linux/Darwin `ERANGE`, enforces a 32-bit OCaml string limit, and returns binary strings. List builds OCaml `(name, length)` pairs from platform-specific name buffers or Solaris attribute directories.

State/persistence: mutates xattr name/value pairs on files/directories. Solaris xattrs are treated as simplified file-like name/value blobs without synchronizing their own metadata.

Dependencies/integration: Linux xattr namespace semantics, BSD `extattr`, Darwin `sys/xattr.h`, Solaris `attropen`/attribute directories, OCaml named exception registration, and property synchronization code.

Risks: system attribute filtering is conservative and platform-specific; missing a system attribute can cause permission errors or meaningless syncs. Long paths are capped at 32767 bytes for list. Concurrently changing attributes can trigger retry failure. Solaris does not update ctime for xattr changes, affecting scan strategy.

Test signals: xattr set/get/remove/list roundtrips, binary values, changing-size retry behavior, namespace name mangling on Linux, unsupported exception behavior, system-attribute filtering, and `unison_xattr_updates_ctime` platform result.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/props_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/pty.c -->
# sources/sync-backup/unison/src/pty.c

Purpose: OCaml C stubs for pseudo-terminal and controlling-terminal support on Unix-like systems and Windows.

Important APIs: Unix `setControllingTerminal` and `c_openpty`; Windows `win_openpty`, `win_closepty`, `w_create_process_pty`, and `win_alloc_console`; non-supported fallbacks raise `ENOSYS`.

Control flow: Unix variants use `openpty` and `ioctl(TIOCSCTTY)`, with Cygwin calling `setsid` because OCaml lacks it there. Windows dynamically resolves `CreatePseudoConsole`/`ClosePseudoConsole`, creates separate pipes for ConPTY input/output, returns OCaml handles plus an abstract HPCON, builds `STARTUPINFOEX` with pseudo-console and handle-list attributes, duplicates std handles, launches a child with `CreateProcessW`, cleans duplicated handles/attribute lists, and returns the process handle.

State/persistence: creates OS PTY handles, pipes, consoles, child processes, and process handles. `win_alloc_console` may attach a console and repair C runtime `stderr`.

Dependencies/integration: Unix libutil/pty headers, Windows ConPTY APIs, OCaml handle allocation, and SSH/terminal interaction code.

Risks: Windows ConPTY is available only on newer systems, so dynamic ENOSYS paths are important. Handle inheritance and cleanup are subtle. `hStdError` is intentionally NULL for Cygwin/MSYS2 SSH compatibility. Abstract HPCON lacks a finalizer, so OCaml must close it correctly.

Test signals: interactive SSH/password prompt behavior, PTY open/close, child process launch, console fallback, Cygwin/MSYS2 clients, and handle leak checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/pty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/system/system_win_stubs.c -->
# sources/sync-backup/unison/src/system/system_win_stubs.c

Purpose: Windows system stubs for accurate stat/lstat metadata, console detection/initialization, console modes/code pages, and VT capability.

Important APIs: `win_has_correct_ctime`, `win_stat(path,lstat)`, `win_hasconsole_gui_stdout`, `win_hasconsole_gui_stderr`, `win_init_console`, `win_get_console_mode`, `win_set_console_mode`, `win_get_console_output_cp`, `win_set_console_output_cp`, and `win_vt_capable`.

Control flow: `win_init` dynamically resolves `NtQueryInformationFile` and `RtlNtStatusToDosError` from `ntdll`. `win_stat` opens the path with backup semantics and optionally reparse-point behavior, uses NT file information when available, falls back to `GetFileInformationByHandle`, detects symlink reparse points for `lstat`, computes device/inode/kind/mode/nlink/size/times, and returns an OCaml stat tuple. Console code detects GUI-only output, allocates or repairs consoles, restores C runtime stdio, and returns optional handles for streams that were not redirected.

State/persistence: reads file metadata and may allocate a console or change console mode/code page. Maintains cached NT API availability and `CONIN$` handle.

Dependencies/integration: Windows kernel/NT APIs, libuv-derived struct definitions, OCaml runtime compatibility shims, GUI/text UI startup, and file scanning code.

Risks: NT struct compatibility and dynamic resolution are delicate. Inode hashing and fallback behavior affect archive identity. The console repair path addresses rare invalid inherited handle cases and must avoid breaking legitimate redirection. Recursive call from `lstat` to `stat` for non-symlinks must preserve error semantics.

Test signals: Windows stat/lstat tests for files, dirs, symlinks, reparse points, link counts, ctime behavior, GUI console startup under cmd/PowerShell/Cygwin/MSYS2, redirected stdout/stderr, code-page changes, and VT detection.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/system/system_win_stubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/Bridge.h -->
# sources/sync-backup/unison/src/uimac/Bridge.h

Purpose: Objective-C bridge header exposing C-callable entry points for Unison’s macOS UI integration.

Important APIs: `cocoaPut`, `cocoaGet`, `cocoaInit`, `cocoaRunning`, `cocoaStop`, `cocoaSystem`, `cocoaOpenFile`, `cocoaShowPreference`, `cocoaSelect`, `cocoaSetToolbarItems`, `cocoaBeginSheet`, `cocoaEndSheet`, `cocoaSetEnabled`, `cocoaSetVisible`, `cocoaSetModified`, `cocoaSetDefaultButton`, `cocoaSetTitle`, `cocoaSetString`, `cocoaAppendString`, `cocoaSetContentSize`, `cocoaSetFrameAutosaveName`, `cocoaSetAutosaveTableColumns`, `cocoaSetValidateMenuItem`, `cocoaSetAction`, and `cocoaSetDoubleAction`.

Control flow: declarations only. The implemented bridge likely lets OCaml/C code address Cocoa objects by string identifiers, set UI state, run modal sheets, invoke actions, and exchange values.

State/persistence: no state in the header, but declared functions imply mutation of Cocoa control state, toolbar/menu configuration, window autosave names, and application lifecycle state.

Dependencies/integration: Objective-C/C boundary for `uimac`, Cocoa runtime implementation files, and macOS app build (`make macui` and CI app packaging).

Risks: stringly typed object/action identifiers are easy to mistype and may fail at runtime. Header/implementation drift can break linkage. UI calls must run on the correct Cocoa thread in the implementation.

Test signals: macOS `make macui`, app launch, UI smoke tests for controls/actions/sheets/toolbars, and linker checks that every declared symbol is implemented.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/Bridge.h -->
