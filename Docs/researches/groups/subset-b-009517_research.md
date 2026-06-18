# Research Group subset-b-009517

This grouped report covers syzkaller tooling files under `sources/test-tools/syzkaller/tools`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-copyright.sh -->
# sources/test-tools/syzkaller/tools/check-copyright.sh

## Purpose

CI lint script enforcing the canonical syzkaller copyright and Apache 2 header on tracked source/config files.

## Important APIs, Types, and Functions

Shell loop over `git ls-files`, regex filters, `tr`, `grep`, generated-file marker checks, and `FILES`/`FAILED` variables.

## Control Flow

Collects eligible tracked files, flattens each file to match the required two-line header, skips known generated files, emits file-position diagnostics for misses, and exits 1 if any file failed.

## State and Persistence Behavior

Reads git index and files only; keeps counters in process memory and writes nothing.

## Dependencies and Integration Points

Requires bash, Git, grep/coreutils, and repo-root execution. Used by presubmit linting.

## Risks and Edge Cases

Command substitution is filename-whitespace fragile; only `//` and `#` headers are accepted; generated marker coverage must stay current.

## Test Signals

Run on compliant, missing-header, generated, vendored, and testdata fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-copyright.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-html.sh -->
# sources/test-tools/syzkaller/tools/check-html.sh

## Purpose

HTML formatting lint that rejects tracked HTML files mixing tabs and repeated spaces for formatting.

## Important APIs, Types, and Functions

Uses `find`, `grep`, `wc`, `git ls-files --error-unmatch`, and simple shell counters.

## Control Flow

Counts tab lines and double-space lines for every HTML file, ignores `Commit.Date` spacing and untracked files, reports files that contain both styles, and fails if any were found.

## State and Persistence Behavior

No writes; only `FILES` and `FAILED` shell state.

## Dependencies and Integration Points

Depends on bash, Git, find/grep/wc; integrated with repository style checks.

## Risks and Edge Cases

Heuristic can flag intentional content spacing and assumes current-directory scan scope.

## Test Signals

Fixtures with tabs only, spaces only, mixed whitespace, untracked files, and `Commit.Date` exemption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-html.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-k8s.sh -->
# sources/test-tools/syzkaller/tools/check-k8s.sh

## Purpose

Kubernetes manifest validation for syzkaller agent and cluster deployment targets.

## Important APIs, Types, and Functions

Defines `run_checks`; invokes Make/Kustomize, kubeconform, and kube-linter via pinned `go run` module versions with mock deployment environment variables.

## Control Flow

Exports mock secrets/image vars, renders each Make target, validates rendered YAML with kubeconform, lints with kube-linter through process substitution, skips non-Linux hosts, and accumulates failures.

## State and Persistence Behavior

Keeps a shell `FAILED` flag and mock environment; manifests flow through variables/pipes and are not persisted.

## Dependencies and Integration Points

Requires Linux, Go module/network/cache access, target Makefiles, `.kube-linter.yaml`, and K8s schema tooling.

## Risks and Edge Cases

Pinned `go run` tools still depend on module availability; template variable drift can fail rendering before schema validation.

## Test Signals

Run in Linux CI and inject bad YAML/schema/linter fixtures to verify failure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-k8s.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-language.sh -->
# sources/test-tools/syzkaller/tools/check-language.sh

## Purpose

Terminology lint for tracked source/docs/config files.

## Important APIs, Types, and Functions

Bash `nocasematch`, `git ls-files`, line-by-line `read`, regex checks for `slave`, `blacklist`, and `whitelist`, and suggestion strings.

## Control Flow

Filters tracked files, scans each line, ignores `bond_enslave`, chooses replacement suggestions, prints diagnostics and offending line, and exits non-zero on any match.

## State and Persistence Behavior

No persistence; stores counters and failure flag only.

## Dependencies and Integration Points

Requires bash and Git; part of presubmit policy checks.

## Risks and Edge Cases

Simple substring matching can false-positive in quoted/history/vendor text; exception list is hard-coded.

## Test Signals

Fixtures for each term, case variants, exception path/word, generated paths, and clean files.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-language.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-shebang.sh -->
# sources/test-tools/syzkaller/tools/check-shebang.sh

## Purpose

Executable shebang portability lint.

## Important APIs, Types, and Functions

Uses `git ls-files -s` mode `100755`, `head`, and `grep -E` to inspect executable tracked files.

## Control Flow

Checks executable non-generated files, allows `/bin/sh` and `/usr/bin/env ...`, reports other shebang interpreters, and fails if any are found.

## State and Persistence Behavior

Reads Git modes and first lines only; no writes.

## Dependencies and Integration Points

Depends on Git, bash, head/grep, and executable bit correctness in the index.

## Risks and Edge Cases

Filename splitting is whitespace-fragile; policy deliberately rejects otherwise common `/bin/bash` shebangs.

## Test Signals

Fixtures with `/bin/sh`, `/usr/bin/env bash`, `/bin/bash`, no shebang, generated executable.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-shebang.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-sql-newlines.sh -->
# sources/test-tools/syzkaller/tools/check-sql-newlines.sh

## Purpose

SQL newline-at-EOF guard.

## Important APIs, Types, and Functions

Uses `find . -name '*.sql'`, `test -s`, `tail -c 1`, and a shell failure flag.

## Control Flow

Scans SQL files, checks non-empty files for a final newline byte, reports missing-newline diagnostics, and exits 1 on failures.

## State and Persistence Behavior

No writes; only local shell variables.

## Dependencies and Integration Points

Requires bash/coreutils and intended scan-root execution.

## Risks and Edge Cases

Scans untracked SQL files too, so local scratch files can fail CI-like runs.

## Test Signals

Empty, newline-terminated, and unterminated SQL fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-sql-newlines.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-syzos.sh -->
# sources/test-tools/syzkaller/tools/check-syzos.sh

## Purpose

SYZOS binary checker that rejects problematic data accesses in the syz-executor `guest` ELF section.

## Important APIs, Types, and Functions

Uses `TARGETOS`, `BUILDOS`, `TARGETARCH`, target-prefixed objdump fallback, `awk`/`gawk`, grep/sed, section headers, disassembly, and arch-specific patterns.

## Control Flow

Skips non-Linux/cross-build/unsupported archs, locates `bin/${TARGETOS}_${TARGETARCH}/syz-executor`, verifies `guest`, disassembles it, then flags amd64 RIP-relative references outside the section and arm64/riscv64 `adrp`/`auipc` accesses.

## State and Persistence Behavior

Reads the executor binary only; all section bounds and matches are process-local.

## Dependencies and Integration Points

Requires a built executor and usable objdump; integrated into SYZOS build validation.

## Risks and Edge Cases

Objdump text parsing is version-sensitive; non-amd64 checks are instruction-pattern heuristics; guest-end boundary handling is approximate.

## Test Signals

Run after linux amd64/arm64/riscv64 executor builds, including negative binaries with synthetic out-of-section references.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-syzos.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-whitespace.sh -->
# sources/test-tools/syzkaller/tools/check-whitespace.sh

## Purpose

Whitespace lint for tracked repository files.

## Important APIs, Types, and Functions

Uses `git ls-files`, extension/path filters, line scanning, grep/tail style checks, counters, and a failure flag.

## Control Flow

Scans candidate files for trailing whitespace, disallowed tabs in text formats, and missing final newlines, printing file/line diagnostics and failing on any violation.

## State and Persistence Behavior

Reads tracked files only and writes nothing.

## Dependencies and Integration Points

Requires bash, Git, and coreutils; used by lint/presubmit.

## Risks and Edge Cases

Filters must exclude generated/binary-like files correctly; filename whitespace remains fragile.

## Test Signals

Fixtures covering trailing spaces, tabs where allowed/disallowed, final newline, generated exclusions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-whitespace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check_links.py -->
# sources/test-tools/syzkaller/tools/check_links.py

## Purpose

Markdown local-link checker and same-repo GitHub absolute-link detector.

## Important APIs, Types, and Functions

Python regex `link_re`, helpers `filter_link`, `fix_link`, `check_link`, `os.path.exists`, and CLI `<root_dir> <doc_files>...`.

## Control Flow

Extracts inline Markdown links, flags absolute GitHub master links to syzkaller, ignores HTTP/anchor/mailto links for existence checks, strips query/fragment suffixes, resolves root-relative and doc-relative local paths, and reports missing targets.

## State and Persistence Behavior

Keeps link/error lists in memory; no writes.

## Dependencies and Integration Points

Requires Python and docs filesystem access; used by docs CI.

## Risks and Edge Cases

Regex misses reference-style links and nested parentheses; anchor existence inside local files is not checked.

## Test Signals

Docs fixtures with valid/broken local links, root-relative paths, HTTP/mailto/anchor links, and GitHub master links.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check_links.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check_translation_update.py -->
# sources/test-tools/syzkaller/tools/check_translation_update.py

## Purpose

Translation freshness checker for `docs/translations` based on source commit markers in translation commit messages.

## Important APIs, Types, and Functions

Functions include `get_git_repo_root`, `get_latest_commit_info`, `extract_source_commit_info`, `extract_translation_language`, `check_translation_update`, `extract_compact_date`, and `main`; shells out to `git` through `subprocess.run`.

## Control Flow

Finds repo root, walks translations or checks `--files`, skips README/non-translation paths, parses `Update to commit HASH ("TITLE")` from latest translation commit, maps translation path to source doc, compares commit prefixes, and prints summary counts.

## State and Persistence Behavior

Reads Git history and files; no writes; exits 0 currently even for stale translations.

## Dependencies and Integration Points

Requires Python, Git history, and mirrored `docs/translations/<lang>/...` layout.

## Risks and Edge Cases

Shallow clones and malformed commit messages reduce coverage; source path mapping is convention-based; stale translations are informational until exit codes change.

## Test Signals

Temporary git repo fixtures for matching, stale, missing-marker, missing-source, and explicit `--files` cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check_translation_update.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/build.go -->
# sources/test-tools/syzkaller/tools/clang/build.go

## Purpose

Linux-only cgo build shim for Clang-based syzkaller tools.

## Important APIs, Types, and Functions

cgo directives for C++23, warning suppressions, dynamic `-lclang-cpp -lclang -lLLVM`, and hard-coded LLVM 22/21/19 include/library paths.

## Control Flow

Imported for cgo side effects; build flags are applied when Go compiles the package, while runtime behavior lives in the C++ files selected by `SYZ_RUN_CLANGTOOL`.

## State and Persistence Behavior

No runtime state or persistence; build-time toolchain selection only.

## Dependencies and Integration Points

Requires Linux, cgo, a C++ compiler, and matching LLVM/Clang development libraries; dynamic linking preserves Clang plugin constructors.

## Risks and Edge Cases

Hard-coded distro paths and runtime shared-library lookup can fail on unsupported systems; build tag excludes non-Linux.

## Test Signals

Build and `go test` clangtool packages on supported LLVM versions and run a tiny ClangTool invocation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/build.go -->
# sources/test-tools/syzkaller/tools/clang/codesearch/build.go

## Purpose

Linux-only cgo build shim for Clang-based syzkaller tools.

## Important APIs, Types, and Functions

cgo directives for C++23, warning suppressions, dynamic `-lclang-cpp -lclang -lLLVM`, and hard-coded LLVM 22/21/19 include/library paths.

## Control Flow

Imported for cgo side effects; build flags are applied when Go compiles the package, while runtime behavior lives in the C++ files selected by `SYZ_RUN_CLANGTOOL`.

## State and Persistence Behavior

No runtime state or persistence; build-time toolchain selection only.

## Dependencies and Integration Points

Requires Linux, cgo, a C++ compiler, and matching LLVM/Clang development libraries; dynamic linking preserves Clang plugin constructors.

## Risks and Edge Cases

Hard-coded distro paths and runtime shared-library lookup can fail on unsupported systems; build tag excludes non-Linux.

## Test Signals

Build and `go test` clangtool packages on supported LLVM versions and run a tiny ClangTool invocation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/codesearch.cpp -->
# sources/test-tools/syzkaller/tools/clang/codesearch/codesearch.cpp

## Purpose

Clang LibTooling AST indexer that produces a kernel source database for syzkaller agentic codesearch.

## Important APIs, Types, and Functions

Classes `Instance`, `PPCallbacksTracker`, `IndexerAstConsumer`, `Indexer`, `NamedDeclEmitter`, `ScopedState`; visitors for functions, globals, records, enums, typedefs, calls, decl refs, member refs, and type refs.

## Control Flow

Constructor dispatches to `Main` when `SYZ_RUN_CLANGTOOL=codesearch`; `ClangTool` traverses each translation unit, opens definition contexts with body/comment ranges, records calls/uses/read-write/address references and record layouts, then emits JSON.

## State and Persistence Behavior

State is per-process `Output`, current definition pointer, source manager, callee/type-reference flags, and AST traversal context; persistence is stdout consumed by Go indexing.

## Dependencies and Integration Points

Depends on Clang/LLVM tooling, compilation database, and local `json.h`/`output.h`; integrated by `tools/syz-codesearch` and `pkg/codesearch`.

## Risks and Edge Cases

Macro source ranges can cross files and are clamped; macro recording is stubbed; anonymous/duplicate names and simple parent-based write detection limit precision.

## Test Signals

Golden C fixtures for calls, callback arrays, comments, static globals, typedef/struct uses, field reads/writes, macro-generated declarations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/codesearch.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/codesearch.go -->
# sources/test-tools/syzkaller/tools/clang/codesearch/codesearch.go

## Purpose

Marker Go package for the codesearch Clang implementation.

## Important APIs, Types, and Functions

Exports `const Tool = "codesearch"` in package `clangtoolimpl`.

## Control Flow

Go wrappers pass this selector to `pkg/clangtool`; the C++ constructor runs only when `SYZ_RUN_CLANGTOOL` matches it.

## State and Persistence Behavior

No mutable state or persistence.

## Dependencies and Integration Points

Used by `tools/syz-codesearch` to launch the correct C++ tool.

## Risks and Edge Cases

String mismatch with C++ dispatch would build but not execute the intended indexer.

## Test Signals

Build/run `syz-codesearch index` against a small compile database.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/codesearch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/output.h -->
# sources/test-tools/syzkaller/tools/clang/codesearch/output.h

## Purpose

JSON schema and output accumulator for the Clang codesearch indexer.

## Important APIs, Types, and Functions

Defines entity/ref kind constants, `LineRange`, `Reference`, `FieldInfo`, `Definition`, `print` overloads, and `Output::emit/print`.

## Control Flow

AST traversal appends `Definition` records with ranges, refs, and field layout; `Output::print` emits top-level JSON `definitions` through `JSONPrinter`.

## State and Persistence Behavior

In-memory `std::vector<Definition>` only; writes to stdout via printer.

## Dependencies and Integration Points

Consumed by Go `pkg/codesearch` and agentic codesearch tools, so field names are API surface.

## Risks and Edge Cases

Schema renames are compatibility breaks; reference kinds are intentionally coarse; anonymous field/record names can collide.

## Test Signals

Golden JSON for every entity/ref kind, comments, static globals, empty refs, and field offsets/sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/output.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/build.go -->
# sources/test-tools/syzkaller/tools/clang/declextract/build.go

## Purpose

Linux-only cgo build shim for Clang-based syzkaller tools.

## Important APIs, Types, and Functions

cgo directives for C++23, warning suppressions, dynamic `-lclang-cpp -lclang -lLLVM`, and hard-coded LLVM 22/21/19 include/library paths.

## Control Flow

Imported for cgo side effects; build flags are applied when Go compiles the package, while runtime behavior lives in the C++ files selected by `SYZ_RUN_CLANGTOOL`.

## State and Persistence Behavior

No runtime state or persistence; build-time toolchain selection only.

## Dependencies and Integration Points

Requires Linux, cgo, a C++ compiler, and matching LLVM/Clang development libraries; dynamic linking preserves Clang plugin constructors.

## Risks and Edge Cases

Hard-coded distro paths and runtime shared-library lookup can fail on unsupported systems; build tag excludes non-Linux.

## Test Signals

Build and `go test` clangtool packages on supported LLVM versions and run a tiny ClangTool invocation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/declextract.cpp -->
# sources/test-tools/syzkaller/tools/clang/declextract/declextract.cpp

## Purpose

Clang LibTooling declaration extractor for syzkaller description generation.

## Important APIs, Types, and Functions

Class `Extractor`, matcher thunk, `PPCallbacksTracker`, `ConstDesc`, `FunctionAnalyzer`; helpers `genType`, `extractRecord`, `extractEnum`, `extractIoctl`, `evaluate`, `findAllMatches`, `getTypingEntity`.

## Control Flow

When `SYZ_RUN_CLANGTOOL=declextract`, runs matchers for function definitions, `SYSCALL_DEFINEx`, io_uring tables, `nla_policy`, generic netlink families, and `file_operations`, emitting type/const/function/syscall/ioctl/netlink/file-op JSON plus typing facts from function bodies.

## State and Persistence Behavior

Maintains macro map, dedup maps, current matcher bindings, AST/source managers, and `Output`; persists only stdout JSON.

## Dependencies and Integration Points

Depends on Clang AST matchers/tooling, Linux ioctl macros, kernel compilation databases, and local JSON/output schema; feeds Go syzlang tooling.

## Risks and Edge Cases

Best-effort inference: other-TU definitions become TODO, anonymous names are heuristic, nested anonymous aggregate indexing is incomplete, indirect calls are ignored, non-int constants evaluate to zero.

## Test Signals

Golden tests over declextract testdata and kernel snippets for structs, bitfields, counted arrays, ioctls, netlink, io_uring, and file ops.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/declextract.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/declextract.go -->
# sources/test-tools/syzkaller/tools/clang/declextract/declextract.go

## Purpose

Marker Go package for the declextract Clang implementation.

## Important APIs, Types, and Functions

Exports `const Tool = "declextract"`.

## Control Flow

Shared clangtool runner uses the selector; C++ constructor exits into extractor `Main` when the environment matches.

## State and Persistence Behavior

No mutable state or persistence.

## Dependencies and Integration Points

Used by Go-side declaration extraction wrappers.

## Risks and Edge Cases

String mismatch prevents dispatch to the intended C++ extractor.

## Test Signals

Build and run declextract against a tiny compilation database.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/declextract.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/output.h -->
# sources/test-tools/syzkaller/tools/clang/declextract/output.h

## Purpose

JSON schema for declextract output, covering C types, constants, structs/enums, functions/scopes, syscalls, file ops, ioctls, io_uring, and netlink.

## Important APIs, Types, and Functions

Variant `FieldType` with `IntType`, `PtrType`, `ArrType`, `BufferType`, struct name; records `Struct`, `Enum`, `Function`, `Syscall`, `FileOps`, `Ioctl`, `NetlinkPolicy`, `TypingFact`; `Output::emit/print`; `TodoType`.

## Control Flow

Extractor callbacks build typed records and push them into category vectors; print emits fixed top-level arrays through `JSONPrinter`.

## State and Persistence Behavior

All state is owned by `Output` vectors and `unique_ptr` variant fields; no direct file writes.

## Dependencies and Integration Points

The JSON field names are a contract with downstream Go consumers and generated syzlang tooling.

## Risks and Edge Cases

Default/empty `FieldType` can be unsafe if printed without a branch; schema changes need synchronized consumers.

## Test Signals

Golden JSON for each record type, optional elem fields, TODO type, and nested typing facts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/output.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/json.h -->
# sources/test-tools/syzkaller/tools/clang/json.h

## Purpose

Minimal streaming JSON printer used by the C++ Clang tools.

## Important APIs, Types, and Functions

`JSONPrinter`, RAII `Scope`, string escaping, scalar/string/vector/pointer `Field` overloads, and free `print` overload dispatch for complex types.

## Control Flow

Callers open scopes and write fields; printer handles commas, nesting, vectors, optional pointers, and escaped strings to stdout.

## State and Persistence Behavior

Printer formatting state only; no parsed data ownership or file persistence.

## Dependencies and Integration Points

Included by both Clang output schemas instead of an external JSON dependency.

## Risks and Edge Cases

Correctness depends on caller `last` flags and matching `print` overloads; it is an emitter only, not a validator/parser.

## Test Signals

Golden output with escaping, empty vectors, nested objects, optional pointers, and comma boundaries.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/json.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-buildroot-image.sh -->
# sources/test-tools/syzkaller/tools/create-buildroot-image.sh

## Purpose

Buildroot automation for syzkaller Linux guest images across several architectures.

## Important APIs, Types, and Functions

Env vars `TARGETARCH`, `NOMAKE`, `LINUX_VERSION`, `LINUX_KERNEL_CONFIG`; Buildroot defconfigs; generated rootfs/post-image scripts; `make olddefconfig`/`make`.

## Control Flow

Pins Buildroot checkout, appends common/per-arch config, patches package defaults, writes rootfs hooks for debugfs/securityfs/configfs/SSH/host keys/bootloader, adjusts arm64 image config, and optionally builds.

## State and Persistence Behavior

Mutates the Buildroot checkout and output tree: `.config`, package files, scripts, custom genimage config, and images.

## Dependencies and Integration Points

Requires external Buildroot checkout, host build deps, network/package access, and kernel config path; used for syzkaller VM image production.

## Risks and Edge Cases

Invasive if run in wrong directory; version-pinned sed/hash patches can drift; passwordless root SSH is testing-only.

## Test Signals

Run with `NOMAKE=yes` per arch, then boot representative images and verify SSH/KCOV/filesystem mounts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-buildroot-image.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-ec2-rootfs.sh -->
# sources/test-tools/syzkaller/tools/create-ec2-rootfs.sh

## Purpose

Creates or resizes an Amazon Linux 2023 EC2/QEMU root filesystem image.

## Important APIs, Types, and Functions

Parses format/name/platform/size; uses truncate, mkfs, loop mount, Docker export, tar, chroot, dnf, systemctl, resize2fs/xfs_growfs.

## Control Flow

Existing image path resizes and exits; new path formats image, exports AL2023 container, installs systemd/network/SSH tools, enables DHCP, configures passwordless root SSH, and unmounts.

## State and Persistence Behavior

Persists the rootfs image; temporary mount dir/container/image cache are side effects.

## Dependencies and Integration Points

Requires sudo, Docker, loop devices, mkfs/resizer tools, DNF/network access, and compatible platform emulation.

## Risks and Edge Cases

Assumes `/dev/loop0` during resize; failures can leave mounts; passwordless root is unsafe outside fuzzing guests.

## Test Signals

Create/resize ext4 and xfs images, boot with documented QEMU, verify DHCP and SSH.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-ec2-rootfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-freebsd-gce-ci.sh -->
# sources/test-tools/syzkaller/tools/create-freebsd-gce-ci.sh

## Purpose

Builds a FreeBSD GCE image that starts syz-ci.

## Important APIs, Types, and Functions

Downloads FreeBSD VM raw image, generated setup/rc scripts, mkisofs, expect, QEMU, tar packaging.

## Control Flow

Expands disk, builds config ISO, boots QEMU, logs in over serial, mounts ISO, runs setup to install packages/SSH/console/syzkaller dir, powers off, and archives disk for GCE upload.

## State and Persistence Behavior

Creates disk.raw/image.iso/setup.sh/rc.local/install_log/final tarball; booted image later clones syzkaller and runs syz-ci.

## Dependencies and Integration Points

Requires FreeBSD image URL, QEMU, expect, mkisofs, package repos, `id_ed25519.pub`, GCE metadata at runtime.

## Risks and Edge Cases

Hard-coded version/prompt/package assumptions are brittle; root SSH by key and cloud rc logic are CI-specific.

## Test Signals

Complete QEMU install, inspect log, boot disk locally, verify syz-ci starts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-freebsd-gce-ci.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-gce-image.sh -->
# sources/test-tools/syzkaller/tools/create-gce-image.sh

## Purpose

Creates a minimal bootable Linux raw disk for syzkaller/GCE from userspace and kernel image.

## Important APIs, Types, and Functions

Args userspace/kernel/arch; loop or nbd, fdisk, mkfs.ext4, mount/copy, SSH/network/fstab/udev injection, grub-install or zipl.

## Control Flow

Validates inputs, creates disk.raw, partitions per arch, formats/mounts, copies userspace/kernel, configures serial/DHCP/debugfs/securityfs/configfs/binder/i915/vim2m/passwordless SSH, optional sysctl/cmdline, installs bootloader.

## State and Persistence Behavior

Writes disk.raw and temporary disk.mnt/device attachments; trap cleans loop/nbd/mounts.

## Dependencies and Integration Points

Requires sudo, block device tooling, grub/zipl, init-capable userspace, and kernel image naming by arch.

## Risks and Edge Cases

Destructive to local disk.raw/disk.mnt; Debian path assumptions; failures may leave mounts/devices.

## Test Signals

Boot amd64 and one non-x86 image in QEMU; verify serial, DHCP, SSH, mounts, cmdline/sysctl.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-gce-image.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-image.sh -->
# sources/test-tools/syzkaller/tools/create-image.sh

## Purpose

Creates a Debian chroot and ext4 image for syzkaller guests.

## Important APIs, Types, and Functions

Flags arch/distribution/feature/output/perf/size; debootstrap, qemu-user-static, chroot apt, ssh-keygen, mkfs/mount/copy.

## Control Flow

Maps arch names, checks foreign emulation, debootstraps with optional archive fallback, runs second stage if needed, configures root SSH/DHCP/fstab/DNS/hostname, optional perf build, udev rule, and copies chroot to `<output>.img`.

## State and Persistence Behavior

Persists chroot dir, image, and generated SSH keypair; removes/recreates output dir.

## Dependencies and Integration Points

Requires sudo, debootstrap, apt repos, qemu/binfmt for foreign arch, kernel source if perf enabled.

## Risks and Edge Cases

`sudo rm -rf` on output demands validation; generated root key/passwordless login are testing-only; package drift can break builds.

## Test Signals

Build minimal/full host image, one foreign image, perf mode, then boot and SSH.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-image.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-openbsd-gce-ci.sh -->
# sources/test-tools/syzkaller/tools/create-openbsd-gce-ci.sh

## Purpose

Builds OpenBSD GCE syz-ci image from snapshots.

## Important APIs, Types, and Functions

OpenBSD snapshot discovery, custom site set, autoinstall config, growisofs, qemu-img, expect, tar/gcloud instructions.

## Control Flow

Downloads ISO, injects site/autoinstall/disklabel/boot/random files, runs installer in QEMU, installs packages/configures syzkaller mount and syz-ci rc.local, verifies `pkg_add OK`, archives disk.raw.

## State and Persistence Behavior

Creates ISO/site/autoinstall/disklabel/disk.raw/install_log/tarball artifacts.

## Dependencies and Integration Points

Requires OpenBSD mirrors, QEMU/KVM, expect, growisofs, network packages, GCE metadata at runtime.

## Risks and Edge Cases

Moving snapshots and installer prompts are brittle; embedded test credentials/keys are CI-only.

## Test Signals

Run installer, verify package marker, boot image, confirm syz-ci and serial console.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-openbsd-gce-ci.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-openbsd-vmm-worker.sh -->
# sources/test-tools/syzkaller/tools/create-openbsd-vmm-worker.sh

## Purpose

Builds minimal OpenBSD worker disk image.

## Important APIs, Types, and Functions

Snapshot ISO, install.site, generated ed25519 worker key, autoinstall config, growisofs, qemu-img, expect.

## Control Flow

Generates worker keys, injects minimal set/autoinstall files into patched ISO, installs to worker_disk.raw via QEMU/expect, prints host keys, and reports the disk.

## State and Persistence Behavior

Persists worker_disk.raw, worker_key files, ISO support files, install_log.

## Dependencies and Integration Points

Requires OpenBSD snapshots, QEMU/KVM, growisofs, expect, ssh-keygen.

## Risks and Edge Cases

Generated keys/password settings are for testing; snapshot prompt drift can break automation.

## Test Signals

Boot worker_disk.raw and verify SSH with worker_key plus minimal set selection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-openbsd-vmm-worker.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/demo_setup.sh -->
# sources/test-tools/syzkaller/tools/demo_setup.sh

## Purpose

Legacy demo setup that downloads pinned syzkaller/kernel/toolchain artifacts and starts qemu fuzzing.

## Important APIs, Types, and Functions

apt, curl/wget, old Go/gcc/image/corpus downloads, `go get`, git checkout, kernel clone/build, generated manager config.

## Control Flow

Installs deps, sets GOPATH/PATH, downloads artifacts, builds old syzkaller and Linux v4.13, writes manager config, starts syz-manager.

## State and Persistence Behavior

Creates go/gcc/gopath/linux/workdir/images/corpus/config under current dir.

## Dependencies and Integration Points

Depends on obsolete external artifacts, KVM/QEMU, apt hosts, old Go behavior.

## Risks and Edge Cases

Pinned old versions and downloaded binaries are unsuitable for production; artifacts may vanish.

## Test Signals

Smoke only if legacy URLs work; otherwise compare generated config to modern setup expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/demo_setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/env/Dockerfile -->
# sources/test-tools/syzkaller/tools/docker/env/Dockerfile

## Purpose

Current syzkaller development/test Docker environment.

## Important APIs, Types, and Functions

Multi-stage Debian trixie image: prebuilt Fuchsia/NetBSD toolchains, custom Git, Go 1.26, LLVM 22, cross compilers, fs tools, Spanner emulator, Rust, node, gcloud.

## Control Flow

Downloads/install packages and archives, configures alternatives, GOPATH/GOMODCACHE/source dirs, gcloud components, writable dirs for host UID, and bash entrypoint.

## State and Persistence Behavior

Container filesystem stores toolchains/SDKs/cache dirs; runtime persistence comes from mounts.

## Dependencies and Integration Points

Depends on Debian, apt.llvm.org, storage.googleapis.com, Go/Rust/gcloud downloads, Docker networking.

## Risks and Edge Cases

Many pinned remote downloads and `trusted=yes` LLVM repo increase reproducibility/supply-chain risk; image is large.

## Test Signals

Build image, run presubmit subsets, cross-compile executor, dashboard/gcloud tests, verify tool versions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/env/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/old-env/Dockerfile -->
# sources/test-tools/syzkaller/tools/docker/old-env/Dockerfile

## Purpose

Legacy Ubuntu-based syzkaller environment image.

## Important APIs, Types, and Functions

Ubuntu 20.04, cross compilers, Go 1.22.7, clang-12 from apt.llvm xenial, precreated syz-env dirs.

## Control Flow

Installs packages layer-by-layer, downloads Go, adds LLVM repo/key, installs clang-12, symlinks clang, prepares writable dirs.

## State and Persistence Behavior

State baked into image only.

## Dependencies and Integration Points

Depends on old Ubuntu/LLVM/Go repos and Docker.

## Risks and Edge Cases

Old repos/tools can disappear or contain CVEs; apt-key is deprecated; may not match current repo needs.

## Test Signals

Build and run representative old-branch bisection/build commands.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/old-env/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/syzbot/Dockerfile -->
# sources/test-tools/syzkaller/tools/docker/syzbot/Dockerfile

## Purpose

syzbot command execution container image.

## Important APIs, Types, and Functions

Static strace build stage; final Debian image with kernel deps, cross compilers, LLVM 22/clang-15, QEMU, Rust, gcloud, bazelisk, syzkaller user, command wrapper.

## Control Flow

Builds strace, installs broad toolchain set, configures alternatives and Cloud Source credential helper, fetches bazelisk dynamically, creates user, copies wrapper.

## State and Persistence Behavior

Container filesystem stores tools and system git config.

## Dependencies and Integration Points

Depends on Debian/LLVM/GitHub/gcloud repos and architecture-specific packages.

## Risks and Edge Cases

Dynamic latest bazelisk harms reproducibility; broad trusted tool install expands supply-chain surface.

## Test Signals

Build image and run `/run-syz-command.sh make presubmit` or representative syzbot commands.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/syzbot/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/syzbot/run-syz-command.sh -->
# sources/test-tools/syzkaller/tools/docker/syzbot/run-syz-command.sh

## Purpose

Runs a command inside a fresh shallow clone of syzkaller master.

## Important APIs, Types, and Functions

`mktemp -d`, `git clone --depth 1 --branch master`, `"$@"`, `rm -rf` cleanup after success.

## Control Flow

Creates temp dir, clones master, cd's into it, executes provided command, returns, removes clone.

## State and Persistence Behavior

No intended persistence on success; failures leave temp clone because no trap is installed.

## Dependencies and Integration Points

Requires Git/GitHub access; used inside syzbot container.

## Risks and Edge Cases

Always targets master; failed commands leak temp dirs.

## Test Signals

Run successful and failing commands to verify clone, cwd, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/syzbot/run-syz-command.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/extract_workflows.sh -->
# sources/test-tools/syzkaller/tools/extract_workflows.sh

## Purpose

Extracts completed dashboard AI workflow job JSON files for jobs at/after a commit date or matching a commit.

## Important APIs, Types, and Functions

Args URL/commit/output; git log timestamp, curl with optional `ACCESS_TOKEN`, jq, GNU date, mkdir/file writes.

## Control Flow

Fetches job list with `json=1`, filters finished jobs, compares created timestamp to commit date or exact revision, fetches details, writes `<output>/<workflow>/<id>.json`.

## State and Persistence Behavior

Persists downloaded JSON files in output tree.

## Dependencies and Integration Points

Requires jq, curl, Git history, GNU date, dashboard schema/network/auth.

## Risks and Edge Cases

Workflow names become dirs unsanitized; shell parsing is schema-sensitive; downloaded JSON is not validated.

## Test Signals

Local fixture server with old/new/unfinished/exact-revision jobs and auth header checks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/extract_workflows.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/fops_probe/fops_probe.cc -->
# sources/test-tools/syzkaller/tools/fops_probe/fops_probe.cc

## Purpose

KCOV/kallsyms utility to discover file_operations callbacks reached by basic file actions.

## Important APIs, Types, and Functions

Functions `read_kallsyms`, `probe_callback`, `should_skip`, `failf`; uses `/proc/kallsyms`, `/sys/kernel/debug/kcov`, KCOV ioctls, mmap, ioctl/read/write/mmap probes.

## Control Flow

Opens target file, loads text symbols, enables KCOV, probes ioctl/mmap/write/read, maps PCs to nearest symbols, starts at VFS entrypoints, deduplicates/filter noisy symbols, prints callback chain.

## State and Persistence Behavior

Uses KCOV shared memory and local symbol map only; no regular-file writes.

## Dependencies and Integration Points

Requires root/debugfs, KCOV, readable kallsyms, target file safe for simple ops.

## Risks and Edge Cases

Symbol mapping is approximate; target operations can have side effects; single-process diagnostic only.

## Test Signals

Build static and run on a controlled device/driver, verifying expected callbacks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/fops_probe/fops_probe.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/git-cookie-authdaemon -->
# sources/test-tools/syzkaller/tools/git-cookie-authdaemon

## Purpose

GCE metadata OAuth token daemon that writes Git HTTP cookies for Google source hosts.

## Important APIs, Types, and Functions

Functions `read_meta`, `select_scope`, `configure_git`, `acquire_token`, `update_cookie`, `refresh_loop`; supports `--debug`/`--nofork` and Python 2/3 urllib imports.

## Control Flow

Selects service-account scope, configures global git `http.cookiefile`, writes Mozilla cookies for source hosts with access token expiry, daemonizes unless disabled, refreshes before expiry.

## State and Persistence Behavior

Persists `~/.git-credential-cache/cookie` and global Git config; cleanup removes cookie files on process exit.

## Dependencies and Integration Points

Requires GCE metadata server and supported OAuth scopes; Windows path handling included.

## Risks and Edge Cases

Token cookie on disk requires permissions; first token fetch does not retry; missing scopes exit hard.

## Test Signals

Run on GCE with `--nofork --debug`; mock metadata for scope/token/refresh failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/git-cookie-authdaemon -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/gvisor-smoke-test.sh -->
# sources/test-tools/syzkaller/tools/gvisor-smoke-test.sh

## Purpose

Runs a syz-manager smoke test in gVisor mode.

## Important APIs, Types, and Functions

mktemp config, optional `GVISOR_VMLINUX_PATH`, curl latest runsc, chmod/install, `sudo -E ./bin/syz-manager --mode smoke-test`.

## Control Flow

Creates temp workdir/config, obtains runsc as kernel image, then runs one-count gVisor VM smoke test; trap removes workdir.

## State and Persistence Behavior

Temporary workdir only, removed on exit.

## Dependencies and Integration Points

Requires built syz-manager, sudo, curl or local runsc, gVisor backend support.

## Risks and Edge Cases

Latest runsc is unpinned; network-disabled args limit coverage; cleanup uses sudo rm.

## Test Signals

Run with downloaded and local runsc and verify smoke-test success.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/gvisor-smoke-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/kcovfuzzer/kcovfuzzer.c -->
# sources/test-tools/syzkaller/tools/kcovfuzzer/kcovfuzzer.c

## Purpose

LibFuzzer bridge that feeds kernel interfaces while converting KCOV PCs into libFuzzer counters.

## Important APIs, Types, and Functions

`LLVMFuzzerTestOneInput`, fuzz targets `bpf`, `trace_filter`, `binfmt`, KCOV `init`, `cover_start/stop`, `/dev/kmsg` input logging.

## Control Flow

First input selects target from `KCOVFUZZER`, initializes KCOV, then each iteration logs input, exercises subsystem under coverage, hashes PCs into `__libfuzzer_extra_counters`.

## State and Persistence Behavior

Global target function/KCOV buffer and persistent fds; writes kernel control files and kmsg.

## Dependencies and Integration Points

Requires Linux root/debugfs, KCOV, libFuzzer, and enabled BPF/tracing/binfmt_misc.

## Risks and Edge Cases

Can destabilize host kernel state; `KCOVFUZZER` is not null-checked; static builds need sanitizer signal options.

## Test Signals

Run each mode in an isolated VM with bounded corpus and check counters change.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/kcovfuzzer/kcovfuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/kcovtrace/kcovtrace.c -->
# sources/test-tools/syzkaller/tools/kcovtrace/kcovtrace.c

## Purpose

Exec wrapper that prints KCOV PCs for a child program.

## Important APIs, Types, and Functions

OS-specific KCOV device/ioctls, mmap, fork, execve, waitpid, atomic coverage reads.

## Control Flow

Initializes KCOV, forks, child enables coverage and execs program, parent waits, prints collected PCs, unmaps/closes.

## State and Persistence Behavior

Process-local shared coverage buffer; stdout only.

## Dependencies and Integration Points

Requires KCOV permissions on Linux/FreeBSD/NetBSD.

## Risks and Edge Cases

Simplistic for threads/grandchildren; NetBSD branch should be build-checked for variable consistency.

## Test Signals

Compile per OS and run known syscall program, then symbolize PCs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/kcovtrace/kcovtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/kfuzztest-gen/main.go -->
# sources/test-tools/syzkaller/tools/kfuzztest-gen/main.go

## Purpose

CLI that extracts KFuzzTest metadata from vmlinux and emits syzlang.

## Important APIs, Types, and Functions

`kfuzztest.NewExtractor`, `ExtractAll`, `NewBuilder`, `EmitSyzlangDescription`, `tool.Fail`.

## Control Flow

Validates one arg, extracts ELF metadata, logs summary, builds syzlang description, prints to stdout.

## State and Persistence Behavior

Extractor state until close; no file writes.

## Dependencies and Integration Points

Depends on `pkg/kfuzztest` and vmlinux debug/annotation data.

## Risks and Edge Cases

Output quality depends on kernel metadata; exits on first error.

## Test Signals

Run on known annotated vmlinux and compare syzlang golden output.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/kfuzztest-gen/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-aflow/aflow.go -->
# sources/test-tools/syzkaller/tools/syz-aflow/aflow.go

## Purpose

CLI for registered syzkaller agentic workflows and syzbot bug input download.

## Important APIs, Types, and Functions

Flags workflow/input/workdir/model/cache/download/auth/html; functions `run`, `downloadBug`, `get`, `getAccessToken`, `parseSize`; uses `pkg/aflow` and trajectory HTML.

## Control Flow

Download mode queries syzbot and writes input JSON; run mode reads input, opens cache, executes selected flow, logs spans, and rewrites optional live HTML report.

## State and Persistence Behavior

Persists input JSON, workdir/cache artifacts, and optional HTML trajectory.

## Dependencies and Integration Points

Depends on registered flows, syzbot.org, optional Google ADC, filesystem workdir.

## Risks and Edge Cases

Direct JSON type assertions can panic on schema/no-crash changes; workflows may have broad side effects.

## Test Signals

Unit parse/download fixtures and a fake flow emitting spans/cache/HTML.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-aflow/aflow.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-base-commit/main.go -->
# sources/test-tools/syzkaller/tools/syz-base-commit/main.go

## Purpose

Debug tool for blob-based base commit detection.

## Important APIs, Types, and Functions

Flag `--sourcedir`; reads diff; `vcs.Git.BaseForDiff` with `debugtracer.GenericTracer`.

## Control Flow

Validates repo and diff args, reads diff, runs base detection, logs no candidates or candidate commits/branches.

## State and Persistence Behavior

Reads repo/diff; writes logs only.

## Dependencies and Integration Points

Depends on full Git repo and `pkg/vcs`; commit graph recommended for speed.

## Risks and Edge Cases

Diagnostic text output is not stable API; large repos are slow without commit graph.

## Test Signals

Known patch fixtures with expected base candidate hashes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-base-commit/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-benchcmp/benchcmp.go -->
# sources/test-tools/syzkaller/tools/syz-benchcmp/benchcmp.go

## Purpose

Visualizer for syz-manager benchmark JSON streams.

## Important APIs, Types, and Functions

Types `Graph`, `Point`; functions `readFile`, `addExecSpeed`, `skipStart`, `restoreMissingPoints`, `printFinalStats`, `display`; Go HTML template with Google Visualization.

## Control Flow

Reads JSON records, derives exec speed, merges metrics by x-axis, filters graphs, sorts/skips/interpolates points, prints final stats, writes HTML, opens browser unless `--out`.

## State and Persistence Behavior

Writes temp/requested HTML; graph data in memory.

## Dependencies and Integration Points

Depends on JSON bench files, browser/xdg-open, Google JSAPI in generated HTML.

## Risks and Edge Cases

Zero means missing during interpolation, which can be wrong; default negative skip removes first 30 percent.

## Test Signals

Small multi-file bench fixtures for missing points, `--all`, `--out`, custom `--over`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-benchcmp/benchcmp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-bisect/bisect.go -->
# sources/test-tools/syzkaller/tools/syz-bisect/bisect.go

## Purpose

Standalone driver for syzkaller crash cause/fix bisection.

## Important APIs, Types, and Functions

JSON `Config`; flags config/crash/fix/kernel/syzkaller commits; `loadFile`, `saveResultCommits`; `bisect.Run` with tracer.

## Control Flow

Loads configs, creates temp workdir if needed, loads repro/config files, defaults commits to HEAD, runs bisection, writes `cause.commit` or `fix.commit`.

## State and Persistence Behavior

Writes trace artifacts and result commit file in crash dir; may create temp manager workdir.

## Dependencies and Integration Points

Depends on repos, toolchains, userspace, manager config, and repro files.

## Risks and Edge Cases

Expensive and side-effectful; overwrites result files; missing both repro formats is fatal.

## Test Signals

Mock/tiny-repo tests and integration fixture for cause/fix outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-bisect/bisect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-bq.sh -->
# sources/test-tools/syzkaller/tools/syz-bq.sh

## Purpose

BigQuery coverage aggregation orchestration script.

## Important APIs, Types, and Functions

getopts for workdir/duration/date/namespace/repo/branch/client; git clone/fetch/log, GNU date, `bq query`, `go run syz-covermerger`.

## Control Flow

Updates kernel repo, picks latest commit before date, checks BigQuery partition row count for date range, then invokes syz-covermerger with dashboard upload settings.

## State and Persistence Behavior

Persists/updates repo under workdir and merger outputs/uploads.

## Dependencies and Integration Points

Requires Git, bq auth, GNU date, Go build, dashboard API.

## Risks and Edge Cases

Unquoted vars are whitespace-fragile; date/commit pipeline is format-sensitive; client name optionality is weak.

## Test Signals

Mock git/bq tests and small real namespace/date integration.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-bq.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-build/build.go -->
# sources/test-tools/syzkaller/tools/syz-build/build.go

## Purpose

Testing wrapper around `pkg/build.Image`.

## Important APIs, Types, and Functions

Flags OS/arch/vm/kernel/make/compiler/linker/ccache/config/sysctl/cmdline/userspace/trace; fills `build.Params`.

## Control Flow

Parses flags, warns if not root, disables sandboxing, reads optional config, builds image into cwd, optionally traces, logs signature/compiler.

## State and Persistence Behavior

Writes build outputs in current dir and optional trace artifacts; sets process env.

## Dependencies and Integration Points

Depends on pkg/build backends, root/image tooling, toolchains, supplied paths.

## Risks and Edge Cases

Running in wrong cwd scatters artifacts; non-root can fail late; test wrapper UX is minimal.

## Test Signals

Run known target with and without trace; verify image and signature logs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-build/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-check/check.go -->
# sources/test-tools/syzkaller/tools/syz-check/check.go

## Purpose

Static checker for syzkaller syscall descriptions against kernel DWARF structs and netlink policy data.

## Important APIs, Types, and Functions

Functions `check`, `writeWarnings`, `checkStruct`, `parseDescriptions`, `checkNetlink*`; warning constants; `nlaPolicy` layout.

## Control Flow

For each `-obj-arch`, compiles sys descriptions, optionally parses vmlinux DWARF and compares struct sizes/fields/offsets/bitfields, optionally reads amd64 rodata netlink policies and compares nlattr type/size/range, writes grouped `.warn` files and removes stale ones.

## State and Persistence Behavior

Persists `sys/<os>/*.warn`; in-memory AST/prog/DWARF/symbol warning state.

## Dependencies and Integration Points

Depends on syzkaller compiler/prog, vmlinux DWARF, ELF rodata symbols, target consts; netlink check is amd64-specific.

## Risks and Edge Cases

Known false positives for unions, overlays, varlen/split policies; `nlaPolicy` layout is kernel/64-bit sensitive.

## Test Signals

Run with documented multi-arch vmlinux files and inspect `.warn` diffs; unit fixtures for struct/netlink mismatches.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-check/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-check/dwarf.go -->
# sources/test-tools/syzkaller/tools/syz-check/dwarf.go

## Purpose

Parallel DWARF struct extraction backend for syz-check.

## Important APIs, Types, and Functions

`parseKernelObject`, `extractCompilationUnits`, `extractOffsets`, `extractStructs`, and `Unit` offset ranges.

## Control Flow

Opens ELF, drops unneeded sections, pipelines compile-unit enumeration, offset extraction, type resolution, and map merging across goroutines based on GOMAXPROCS.

## State and Persistence Behavior

Returns in-memory map of struct names to DWARF types; no writes.

## Dependencies and Integration Points

Uses Go debug/elf,dwarf; parallelism accounts for DWARF type extraction races.

## Risks and Edge Cases

Duplicate names overwrite; assumes top-level DWARF entries are compile units; large vmlinux remains resource-heavy.

## Test Signals

Synthetic ELF/DWARF fixtures plus real vmlinux performance smoke.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-check/dwarf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-codesearch/codesearch.go -->
# sources/test-tools/syzkaller/tools/syz-codesearch/codesearch.go

## Purpose

CLI for building/querying the Clang-based kernel codesearch database.

## Important APIs, Types, and Functions

Flags database/kernel-src/kernel-obj; `index` command via `clangtool.Run[codesearch.Database]`; query dispatch through `codesearch.NewIndex().Command`.

## Control Flow

Index mode runs Clang tool and writes database; query mode opens database with source roots, executes registered command, writes result stdout; usage lists commands/arity.

## State and Persistence Behavior

Persists database on index; query mode read-only except stdout.

## Dependencies and Integration Points

Depends on compilation database, LLVM/cgo clangtool, and `pkg/codesearch` schema.

## Risks and Edge Cases

Indexing is expensive; database schema changes require rebuild; command validation is delegated.

## Test Signals

Tiny compile database index plus every registered command valid/invalid arity.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-codesearch/codesearch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-cover/syz-cover.go -->
# sources/test-tools/syzkaller/tools/syz-cover/syz-cover.go

## Purpose

Coverage report generator from raw PCs or coverage history file view.

## Important APIs, Types, and Functions

Flags config/modules/exports/period/date/file/repo/commit/namespace/debug/force; functions `toolFileCover`, `initModules`, `doReport`, `readPCs`, `loadModules`.

## Control Flow

File mode renders historical file coverage; normal mode loads manager config/modules, builds report generator, reads PCs or all callback points, runs selected exports, writes outputs, and starts xdg-open.

## State and Persistence Behavior

Writes HTML/CSV/raw/JSON report files; reads rawcover and module JSON.

## Dependencies and Integration Points

Depends on manager config, kernel obj/src, coverage backend/db, xdg-open for interactive use.

## Risks and Edge Cases

Opening outputs is bad for headless CI; malformed PC aborts; `all` omits JSON/JSONL.

## Test Signals

Test PC parsing, each export, modules override, file mode with mocked DB.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-cover/syz-cover.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-covermerger/syz_covermerger.go -->
# sources/test-tools/syzkaller/tools/syz-covermerger/syz_covermerger.go

## Purpose

Batch coverage merger that streams BigQuery coverage rows to merged JSONL and dashboard/GCS storage.

## Important APIs, Types, and Functions

Flags workdir/repo/commit/namespace/duration/date/rows/to-gcs/to-dashapi/client; uses `coveragedb.NewReader`, `covermerger.MergeCSVWriteJSONL`, `gcs`, `dashapi`.

## Control Flow

Initializes config and reader, optionally obtains dashboard upload URL, opens GCS writer, streams CSV through merger into JSONL, closes writer, prints coverage, then asks dashboard to save coverage.

## State and Persistence Behavior

Persists repo/cache under workdir and uploaded JSONL/coverage metadata; merging is streaming.

## Dependencies and Integration Points

Requires BigQuery/GCS/dashboard credentials, repo access, and correct row count/date inputs.

## Risks and Edge Cases

Long-running network/auth-sensitive job; without output URL it can discard JSONL; row count correctness matters.

## Test Signals

Small namespace/date integration with test bucket or mock writer; separate dashboard save test.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-covermerger/syz_covermerger.go -->
