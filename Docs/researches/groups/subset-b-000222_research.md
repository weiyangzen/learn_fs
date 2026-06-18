# subset-b-000222 Research

Grouped research report for the subset B work item. Each section preserves the original source path and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/tarball.rs -->
# sources/cloud-native/nydus/builder/src/tarball.rs

## Purpose
This Rust module implements the tarball-backed `Builder` for Nydus RAFS generation. It converts tar, gzip tar, eStargz-style gzip tar, reference tar, and tarfs inputs into a RAFS tree, optional data blob, and bootstrap metadata. The design is explicitly stream-aware: tar entries are processed once, nodes are created from headers, file data is optionally written to blob artifacts, and the resulting `Tree` is serialized by shared builder/bootstrap code.

## Important APIs, Types, and Functions
`TarballBuilder` is the exported builder implementing `Builder::build`. `TarballTreeBuilder` owns the conversion state for one layer: conversion type, `BuildContext`, `BlobManager`, blob artifact writer, chunk buffer, and `TarBuilder`. `TarReader` abstracts readable tar input variants and implements `Read` plus limited `Seek`; seek support is only available for direct files and `BufReaderInfoSeekable`. `CompressionType` is a small gzip/no-compression detector result. Core functions are `build_tree`, `parse_entry`, `detect_compression_algo`, `set_v5_dir_size`, `get_uid_gid`, `get_mode`, and `get_file_name`.

## Control Flow
`Builder::build` creates bootstrap context and a blob writer, builds the tree, builds bootstrap metadata, dumps blob data and blob metadata, then finalizes blob/bootstrap in inline-meta-dependent order. `build_tree` opens the source, detects compression and conversion type, chooses a `TarReader`, configures `tar::Archive`, creates an initial root node, iterates entries using seek-aware entries when possible, skips stargz special files, and delegates each entry to `parse_entry`. `parse_entry` rejects unsupported tar extensions, derives metadata, resolves special devices, symlinks, hardlinks, PAX xattrs, creates a RAFS V5 or V6 inode, dumps node data from the entry for non-hardlinks, fixes V5 blocks, and inserts the node into the tree.

## State, Persistence, and Dependencies
State persists through `BuildContext` fields such as `blob_zran_generator`, `blob_tar_reader`, and `blob_features`, plus blob artifacts written via `ArtifactWriter` or `NoopArtifactWriter`. The module depends on `tar`, `anyhow`, Nydus RAFS metadata/layout types, storage blob features and ZRAN helpers, digest/compression utilities, and shared builder tree/node/blob/bootstrap code.

## Integration Points
It integrates with `ConversionType` to support RAFS, reference, and tarfs outputs; `BlobManager` and `Blob::dump` for data persistence; `BootstrapManager` for bootstrap serialization; `TarBuilder` for path/tree handling; and RAFS V5/V6 inode formats. Reference conversions set up ZRAN or raw tar readers for later access rather than always copying data into a blob.

## Risks and Test Signals
Risks include unsafe assumptions around hardlink target ordering, rejected tar extensions that may appear in real archives, `unwrap` in compression rewind, device major/minor requirements for FIFO handling, and very large files exceeding `RAFS_MAX_CHUNKS_PER_BLOB`. Seekability changes behavior for hash calculation and tarfs. Tests cover basic and encrypted `TarToTarfs` builds against texture archives, but visible tests do not cover gzip, ZRAN, hardlink error cases, unsupported tar headers, xattrs, or reference conversions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/tarball.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/clib/Cargo.toml -->
# sources/cloud-native/nydus/clib/Cargo.toml

## Purpose
This manifest defines `nydus-clib`, the C wrapper library around selected Nydus SDK functionality. It builds both dynamic and static C-compatible Rust libraries so C programs can open RAFS filesystems and file handles through the FFI exported in `clib/src`.

## Important APIs, Types, and Functions
The important package-level settings are `crate-type = ["cdylib", "staticlib"]`, package metadata, and feature flags for storage backends. The crate name exposed to Cargo is `nydus-clib`, while the library artifact name is `nydus_clib`.

## Control Flow
Cargo uses this file to resolve dependencies and enabled backend features. The feature section maps crate features to `nydus-storage` backend features for S3, OSS, registry, HTTP proxy, and local disk. There is a typo-like feature name `baekend-s3`, which appears to be intended as `backend-s3`.

## State, Persistence, and Dependencies
The manifest depends on `libc`, `log`, `fuse-backend-rs`, `nydus-api`, `nydus-rafs`, and `nydus-storage`, with most Nydus crates resolved from sibling paths. Persistent build output is produced by Cargo as C ABI libraries.

## Integration Points
This crate bridges Rust Nydus RAFS/storage code to generated C headers under `clib/include/nydus.h`. Downstream users link the produced static or dynamic library and include the generated header.

## Risks and Test Signals
The backend feature typo can surprise users expecting `backend-s3`. Because this is a cdylib/staticlib FFI crate, ABI stability depends on the exported symbols in Rust and the generated header matching. Tests live in Rust source files rather than this manifest.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/clib/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/clib/examples/nydus_rafs.c -->
# sources/cloud-native/nydus/clib/examples/nydus_rafs.c

## Purpose
This C example demonstrates the minimum FFI flow for opening and closing a RAFS filesystem through the Nydus C wrapper.

## Important APIs, Types, and Functions
It includes `nydus.h`, uses `NydusFsHandle`, calls `nydus_open_rafs`, checks against `NYDUS_INVALID_FS_HANDLE`, prints success or failure, and calls `nydus_close_rafs`.

## Control Flow
`main` builds hard-coded bootstrap and TOML config strings pointing at repeatable test fixtures. It opens RAFS, exits with `-1` on invalid handle, prints a success line otherwise, closes the RAFS handle, and returns zero.

## State, Persistence, and Dependencies
The example has no persistent state. It depends on fixture paths relative to the example directory and on the C ABI library being linked correctly. The config chooses a localfs backend and dummy cache.

## Integration Points
This file is an integration smoke example for the generated header and Rust exported symbols. It is useful for consumers learning handle lifetime and expected invalid-handle checks.

## Risks and Test Signals
The hard-coded relative paths make the example sensitive to the current working directory. It only tests open/close, not file operations. It does not inspect `errno`, so detailed FFI failures are opaque from the example.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/clib/examples/nydus_rafs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/clib/include/nydus.h -->
# sources/cloud-native/nydus/clib/include/nydus.h

## Purpose
This generated C header exposes the public C ABI for the `nydus-clib` library. It defines opaque integer handles for Nydus filesystem and file objects and declares open/close entry points.

## Important APIs, Types, and Functions
The header defines `NYDUS_FILE_HANDLE_MAGIC`, `NYDUS_INVALID_FILE_HANDLE`, `NYDUS_FS_HANDLE_MAGIC`, and `NYDUS_INVALID_FS_HANDLE`. It typedefs `NydusFileHandle` and `NydusFsHandle` as `uintptr_t`. Public functions are `nydus_fopen`, `nydus_fclose`, `nydus_open_rafs`, `nydus_open_rafs_default`, and `nydus_close_rafs`.

## Control Flow
C callers open a RAFS filesystem with explicit config or default localfs config, optionally open file handles from the filesystem, close file handles, then close the filesystem. The comments state that file handles must be closed before closing the filesystem.

## State, Persistence, and Dependencies
The handles are raw pointer values managed by Rust allocation and deallocation. The header has no persistence but encodes the ABI contract. It includes standard C integer and boolean headers.

## Integration Points
It is generated from Rust source by cbindgen and must remain synchronized with `clib/src/file.rs` and `clib/src/fs.rs`. Consumers use it for linking C or C++ code against static/dynamic Rust artifacts.

## Risks and Test Signals
The ABI exposes raw integer handles, so invalid, stale, double-closed, or cross-thread handles can trigger Rust assertions or memory unsafety. The header comments warn about leak and panic risks but cannot enforce them. Tests in Rust exercise opening/closing RAFS; file operations remain skeletal.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/clib/include/nydus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/clib/src/file.rs -->
# sources/cloud-native/nydus/clib/src/file.rs

## Purpose
This Rust FFI module defines C-facing RAFS file handle operations. It currently provides handle allocation and close/forget behavior, with actual path lookup and read/seek operations still absent.

## Important APIs, Types, and Functions
Exports are `nydus_fopen` and `nydus_fclose`. `FileState` stores a magic value, inode, current position, and owning filesystem handle. Public constants are `NYDUS_FILE_HANDLE_MAGIC`, `NYDUS_INVALID_FILE_HANDLE`, and type alias `NydusFileHandle`.

## Control Flow
`nydus_fopen` validates the C path pointer, converts the filesystem handle through `FileSystemState::try_from_handle`, then currently creates a `FileState` pointing to the filesystem root inode and returns its boxed raw pointer. `nydus_fclose` converts the handle back to `Box<FileState>`, asserts the magic value, obtains the filesystem from `fs_handle`, calls RAFS `forget` for one lookup on the stored inode, mutates the magic, and drops the box.

## State, Persistence, and Dependencies
State is heap-allocated per file handle. It depends on `fuse_backend_rs::api::filesystem::{Context, FileSystem}` for the `forget` call and on crate-level `set_errno`, `FileSystemState`, `Inode`, and `NydusFsHandle`.

## Integration Points
It integrates with `fs.rs` handles and RAFS inode lifecycle accounting. The header advertises this as file-open/close API for C callers, but the actual open implementation is marked TODO and does not use the requested path.

## Risks and Test Signals
Major risks are unsafe raw pointer ownership, null or stale handle misuse, double close causing undefined behavior, and `assert_eq!` panics across FFI boundaries. `nydus_fopen` ignores the path and opens root, so consumers cannot rely on true file access yet. There are no visible direct tests for file handles in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/clib/src/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/clib/src/fs.rs -->
# sources/cloud-native/nydus/clib/src/fs.rs

## Purpose
This module implements the filesystem-level C ABI for opening and closing RAFS instances from Rust. It parses C strings into Rust strings, constructs RAFS with either caller-supplied or default localfs configuration, imports bootstrap metadata, and returns opaque handles.

## Important APIs, Types, and Functions
Exports are `nydus_open_rafs`, `nydus_open_rafs_default`, and `nydus_close_rafs`. `FileSystemState` stores a magic number, root inode, and `Rafs` instance. Helper methods `from_handle` and `try_from_handle` convert raw handles back into mutable references. `default_localfs_rafs_config`, `do_nydus_open_rafs`, and `fs_error_einval` implement shared behavior.

## Control Flow
Open functions reject null pointers, convert C strings via `cstr_to_str!`, construct `ConfigV2`, call `Rafs::new`, import the reader, capture the root inode, box `FileSystemState`, and return the pointer as `NydusFsHandle`. The default open path resolves a relative bootstrap under the supplied directory and synthesizes a TOML localfs config. Close converts the handle back to a `Box`, asserts the magic, mutates it, and calls `rafs.destroy().unwrap()`.

## State, Persistence, and Dependencies
State is heap-owned by the returned handle and includes RAFS runtime state. Dependencies include `nydus_api::ConfigV2`, `nydus_rafs::fs::Rafs`, `Arc`, and path/C string utilities.

## Integration Points
This is the root of the C ABI object graph: file handles store a `NydusFsHandle` and call back into this state. It integrates with storage backend config parsing and RAFS metadata import.

## Risks and Test Signals
Unsafe handle conversion returns `'static mut` references from raw pointers, so aliasing and lifetime correctness rely entirely on the caller. Invalid non-null handles and double close panic. `rafs.destroy().unwrap()` can panic across FFI. Tests cover null open errors, explicit config open, and default localfs open against fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/clib/src/fs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/clib/src/lib.rs -->
# sources/cloud-native/nydus/clib/src/lib.rs

## Purpose
This crate root documents the C wrapper library, declares public FFI modules, and provides small shared helpers for errno and C string conversion.

## Important APIs, Types, and Functions
It re-exports `file::*` and `fs::*`, defines `Inode = u64`, imports `file` and `fs` modules, and defines the `set_errno` helper plus `cstr_to_str!` macro. The macro converts `*const c_char` into UTF-8 `&str`, sets `EINVAL`, and returns a caller-supplied value on invalid C string or invalid UTF-8.

## Control Flow
FFI functions call `cstr_to_str!` after null checks to normalize C string handling. `set_errno` writes to platform errno through `libc::__errno_location` on Linux or `libc::__error` on macOS.

## State, Persistence, and Dependencies
The module mutates thread-local process errno. It depends on `libc`, `std::ffi::CStr`, and exported modules. There is no durable persistence.

## Integration Points
This file is the shared support layer for `fs.rs` and potentially future FFI modules. Its cbindgen command in the docs drives `include/nydus.h` generation.

## Risks and Test Signals
The errno helper is platform-gated to Linux and macOS. Returning from the macro requires each call site to supply a valid return expression. Invalid UTF-8 is treated as `EINVAL`. Tests are indirect through the filesystem module’s null pointer and open cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/clib/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/goreleaser/main.go -->
# sources/cloud-native/nydus/contrib/goreleaser/main.go

## Purpose
This tiny Go program is a placeholder binary used to work around goreleaser behavior when it cannot prebuild another target binary.

## Important APIs, Types, and Functions
The only API is `main`, which calls `fmt.Println`.

## Control Flow
Execution prints `Hello, World!` and exits.

## State, Persistence, and Dependencies
There is no state or persistence. The only dependency is the Go standard library `fmt`.

## Integration Points
Its integration point is release tooling, not runtime Nydus behavior. It gives goreleaser a buildable Go main package.

## Risks and Test Signals
Risk is low, but accidental shipping or invocation would be misleading because it does not perform real release logic. No tests are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/goreleaser/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-backend-proxy/Cargo.toml -->
# sources/cloud-native/nydus/contrib/nydus-backend-proxy/Cargo.toml

## Purpose
This manifest defines the `nydus-backend-proxy` Rust binary crate: a fake HTTP container registry serving Nydus blob files for `nydusd`.

## Important APIs, Types, and Functions
The manifest sets package metadata, Rust 2021 edition, and dependencies on `rocket`, `http-range`, `nix` with `uio`, `clap`, `once_cell`, and `lazy_static`. It also marks this directory as its own workspace.

## Control Flow
Cargo uses the dependency graph to compile the Rocket server and CLI. The `nix` `uio` feature enables positional reads for range streaming.

## State, Persistence, and Dependencies
Persistent state is only build output. Runtime state is implemented in `src/main.rs`. Dependency versions are pinned semver-style.

## Integration Points
It integrates with its Makefile for formatting, debug, release, and static musl builds. Runtime integration is with Nydus clients expecting registry-like blob endpoints.

## Risks and Test Signals
`rocket = 0.5.0` and global workspace isolation matter for dependency resolution. No manifest-level tests exist; behavior is in the source file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-backend-proxy/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-backend-proxy/Makefile -->
# sources/cloud-native/nydus/contrib/nydus-backend-proxy/Makefile

## Purpose
This Makefile provides local build, format-check, release, static-release, and clean targets for the Rust backend proxy.

## Important APIs, Types, and Functions
Targets include `all`, `.format`, `.musl_target`, `.release_version`, `build`, `release`, `static-release`, and `clean`. Variables include `current_dir`, `rust_arch`, and `CARGO_BUILD_FLAGS`.

## Control Flow
Default `all` runs format check and build. Release targets append `--release`; static release adds a musl target `${rust_arch}-unknown-linux-musl`. Build delegates to `cargo build`; clean delegates to `cargo clean`.

## State, Persistence, and Dependencies
The Makefile persists build artifacts through Cargo target directories. It depends on `cargo`, `rustfmt`, and musl target availability for static builds.

## Integration Points
This is the developer and release entrypoint for the proxy crate. CI can use `.format` or `release` to enforce formatting and optimized build.

## Risks and Test Signals
`uname -p` does not always match Rust target architecture naming on every platform. There is no test target. Static release will fail unless the musl Rust target and C toolchain are installed.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-backend-proxy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-backend-proxy/src/main.rs -->
# sources/cloud-native/nydus/contrib/nydus-backend-proxy/src/main.rs

## Purpose
This Rust binary implements a simple Rocket HTTP server that behaves like enough of a registry blob backend for Nydus clients. It serves files from a blob directory under registry-style `/namespace/repo/blobs/sha256:<digest>` routes, with whole-file and range-read support.

## Important APIs, Types, and Functions
`BlobBackend` stores the root directory and a digest-to-open-file map. `BLOB_BACKEND` is a global async mutex. Routes are `check` for `HEAD` and `fetch` for `GET`. `FileStream` and `RangeStream` implement Rocket responders. `HeaderData` extracts `Host` and `Range` headers. `init_blob_backend` and `populate_blobs_map` initialize and refresh blob state.

## Control Flow
`main` parses required `--blobsdir`, initializes the backend map, mounts routes plus a static file server, and launches Rocket. `fetch` validates the `sha256:` prefix, serves the full file through `NamedFile` when no `Range` header is present, or looks up/repopulates the open-file map and streams bytes using `pread` for range requests. `check` validates the digest and returns a responder if the file exists.

## State, Persistence, and Dependencies
The server state is global in-memory mapping of blob file names to `Arc<fs::File>`. Persistent data is the supplied blob directory. Dependencies include Rocket, `http_range`, `nix::sys::uio`, `clap`, `lazy_static`, and standard filesystem APIs.

## Integration Points
It integrates with Nydus daemon storage flows that expect registry-like blob checks and reads. Docker headers such as `Docker-Content-Digest` and `Content-Range` are emitted for compatibility.

## Risks and Test Signals
Range handling uses only the first parsed range and reports `Content-Range` total as range length rather than full object size, which may be semantically incorrect. The global mutex guards map access but readdir refresh is coarse. `populate_blobs_map` panics if the root directory cannot be read. Digest names are accepted after prefix trimming without validating SHA-256 hex. No tests are visible for this binary.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-backend-proxy/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-overlayfs/.golangci.yml -->
# sources/cloud-native/nydus/contrib/nydus-overlayfs/.golangci.yml

## Purpose
This configuration defines static analysis and formatting rules for the `nydus-overlayfs` Go helper.

## Important APIs, Types, and Functions
It uses golangci-lint config version 2, disables default linters, enables `staticcheck`, `unconvert`, `revive`, `ineffassign`, `govet`, `unused`, and `misspell`, and enables `gofmt` plus `goimports` formatters.

## Control Flow
golangci-lint reads this file, runs the enabled linters and formatters, applies a five-minute timeout, and excludes paths under `misc`.

## State, Persistence, and Dependencies
There is no runtime state. It depends on golangci-lint supporting config version 2 and the named linters/formatters.

## Integration Points
This file integrates with local or CI lint targets for the overlayfs helper. Revive rule selection focuses on idiomatic error, naming, flow, and import hygiene.

## Risks and Test Signals
The config is strict enough to reject style regressions but not behavior. Excluding `misc` can hide issues there. It is a test signal for static quality rather than runtime correctness.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-overlayfs/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-overlayfs/Makefile -->
# sources/cloud-native/nydus/contrib/nydus-overlayfs/Makefile

## Purpose
This Makefile builds and tests the `nydus-overlayfs` Go mount helper.

## Important APIs, Types, and Functions
Variables include `GIT_COMMIT`, `BUILD_TIME`, `PACKAGES`, `GOARCH`, optional `GOPROXY`, and derived `PROXY`. Targets include `all`, `build`, `release`, `test`, and `clean`.

## Control Flow
`build` compiles `cmd/main.go` as a Linux static-ish CGO-disabled binary with version/build-time ldflags. `release` adds static external linker flags. `test` depends on build. `clean` removes the output directory.

## State, Persistence, and Dependencies
Build output is `bin/nydus-overlayfs`. It depends on Go tooling, git for commit hash, and environment architecture. The `PACKAGES` variable is prepared but not used in the visible `test` rule content.

## Integration Points
The Makefile supports release automation and local development of the containerd mount helper.

## Risks and Test Signals
`test: build` without an explicit `go test` command is weak if no omitted continuation exists; it may only build. Cross-compilation is limited to Linux output. Version injection depends on git availability.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-overlayfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-overlayfs/cmd/main.go -->
# sources/cloud-native/nydus/contrib/nydus-overlayfs/cmd/main.go

## Purpose
This Go command is a containerd mount helper that receives overlay mount arguments, strips Nydus/Kata passthrough metadata, converts known mount options to syscall flags, and invokes `mount(2)`.

## Important APIs, Types, and Functions
Key symbols are `mountArgs`, `parseArgs`, `parseOptions`, `run`, `main`, version variables `Version` and `BuildTime`, and injectable `mountFn`. Constants identify filtered options: `extraoption=` and `io.katacontainers.volume=`.

## Control Flow
`main` builds a urfave CLI app and requires exactly four positional arguments. `run` calls `parseArgs`, logs the parsed mount, calls `parseOptions`, and invokes `mountFn(fsType, target, fsType, flags, data)`. `parseArgs` validates overlay filesystem type, non-empty target, expects `-o`, splits comma options, and filters containerd/Kata metadata. `parseOptions` maps known options to Linux mount flags and passes unknown options as comma-joined mount data.

## State, Persistence, and Dependencies
There is no durable state. The process performs a privileged mount syscall. Dependencies include `urfave/cli`, `pkg/errors`, `golang.org/x/sys/unix`, `syscall`, and logging.

## Integration Points
It integrates with containerd `fuse.mount` style invocation and Kata container volume metadata. `mountFn` is intentionally injectable for tests.

## Risks and Test Signals
The flags table appears counterintuitive for positive options such as `dev`, `exec`, `suid`, and `rw`, mapping them to disabling flags (`MS_NODEV`, `MS_NOEXEC`, `MS_NOSUID`, `MS_RDONLY`). This may be deliberate inverse handling or a bug. Parsing assumes at least four args; CLI `Before` enforces that for real runs, but direct calls to `parseArgs` with short slices would panic. Tests cover filtering, validation, flag/data splitting, run success, and error wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-overlayfs/cmd/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-overlayfs/cmd/main_test.go -->
# sources/cloud-native/nydus/contrib/nydus-overlayfs/cmd/main_test.go

## Purpose
This Go test file validates argument parsing, mount option conversion, and mount invocation behavior for the overlayfs helper.

## Important APIs, Types, and Functions
It defines `fakeArgs` implementing `cli.Args`, then tests `parseArgs`, `parseOptions`, and `run`. It temporarily replaces package-level `mountFn`.

## Control Flow
`TestParseArgs` table-tests normal filtering and validation failures. `TestParseOptions` asserts flag bitmasks and data passthrough. `TestRun` checks parse errors avoid mount calls, valid inputs call the injected mount function with expected source/target/fstype/flags/data, and mount errors are wrapped.

## State, Persistence, and Dependencies
Tests mutate global `mountFn` but restore it with defer. They do not perform real mounts. Dependencies include `testing`, `reflect`, `strings`, `urfave/cli`, and `unix`.

## Integration Points
The tests lock the helper’s CLI-to-syscall contract and make future refactors safer by verifying the injectable mount seam.

## Risks and Test Signals
The tests are good unit signals but do not exercise real CLI `Before` behavior, short argument panic cases, privileged mount semantics, or every flags table option. They encode the current controversial mapping of options such as `nosuid`, but do not validate whether mappings are semantically correct for Linux overlay mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydus-overlayfs/cmd/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/.golangci.yml -->
# sources/cloud-native/nydus/contrib/nydusify/.golangci.yml

## Purpose
This golangci-lint configuration defines static analysis and formatting policy for the `nydusify` Go tool.

## Important APIs, Types, and Functions
It enables the same focused linter set as overlayfs: `staticcheck`, `unconvert`, `revive`, `ineffassign`, `govet`, `unused`, and `misspell`. It enables `gofmt` and `goimports`, with revive rules for imports, errors, naming, ranges, and control flow.

## Control Flow
golangci-lint applies this configuration with a five-minute timeout and excludes `misc`.

## State, Persistence, and Dependencies
There is no runtime state. It depends on golangci-lint v2 config compatibility.

## Integration Points
This is a CI/local quality gate for a large CLI and package tree. It complements unit tests by catching static issues.

## Risks and Test Signals
The lint setup enforces style but cannot prove registry, mount, or backend correctness. `misc` exclusion may hide stale helper code. It is still a useful signal for regressions in the Go subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/Makefile -->
# sources/cloud-native/nydus/contrib/nydusify/Makefile

## Purpose
This Makefile builds, tests, releases, and cleans the `nydusify` Go CLI.

## Important APIs, Types, and Functions
Variables include `GIT_COMMIT`, `BUILD_TIME`, `PACKAGES`, `GOARCH`, optional `GOPROXY`, and `PROXY`. Targets include `all`, `build`, `release`, `test`, and `clean`.

## Control Flow
`build` compiles `cmd/nydusify.go` into `bin/nydusify`, injects version/build time, disables CGO, and targets Linux. `release` builds with static linker flags. `test` depends on build; the visible content does not show a `go test` invocation. `clean` removes build output.

## State, Persistence, and Dependencies
The main persistent output is `bin/nydusify`. It depends on Go tooling and git. `GOPROXY` can be injected into build commands.

## Integration Points
The Makefile is the developer/release entrypoint for the CLI that orchestrates conversion, checking, copying, optimization, packing, chunkdict, and commit workflows.

## Risks and Test Signals
As with overlayfs, `test` appears weak if it only builds. The build hardcodes Linux output and relies on runtime architecture. Version strings are `main` package variables in the CLI.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/cmd/nydusify.go -->
# sources/cloud-native/nydus/contrib/nydusify/cmd/nydusify.go

## Purpose
This is the main `nydusify` CLI. It converts OCI images to Nydus images, checks Nydus images, generates chunk dictionaries, mounts/views images, builds RAFS from directories, copies images, optimizes Nydus images, and commits container changes.

## Important APIs, Types, and Functions
Important helpers include `isPossibleValue`, `parseBackendConfig`, `getBackendConfig`, `addReferenceSuffix`, `getTargetReference`, `getCacheReference`, `getPrefetchPatterns`, `validateSourceAndTargetArchives`, `setupLogLevel`, `getGlobalFlags`, and `tryReverseConvert`. `main` defines the urfave CLI app and commands. It dispatches into packages `converter`, `checker`, `generator`, `viewer`, `packer`, `copier`, `optimizer`, and `committer`.

## Control Flow
Startup configures log formatting, creates a CLI app, registers global flags, then builds command definitions. The `convert` action validates archives, target reference, backend config, cache options, fs version, prefetch patterns, optional chunk dict, OCI media type flags, optional reverse conversion, then constructs `converter.Opt` and calls `converter.Convert`. `check` builds source/target parsers and `checker.Opt`. Other commands similarly parse flags and hand off to package-level workflows. At the end, unsupported architectures abort before `app.Run`.

## State, Persistence, and Dependencies
Persistent state is created by delegated workflows in work directories, registries, archives, or storage backends. This file itself manages CLI flag state and logging output. Dependencies include OCI reference parsing, human size parsing, logrus, urfave CLI, and many local packages.

## Integration Points
This is the top-level integration surface for Nydus image lifecycle tooling. It maps environment variables and flags into lower-level package option structs, handles registry backend defaults for mount/optimize, and controls version strings injected by the Makefile.

## Risks and Test Signals
Risk concentrates in flag conflict handling, inconsistent backend env var names, backend config validation, archive path validation, and large command surface complexity. `--reverse` always attempts reverse conversion rather than detecting format. `getPrefetchPatterns` reads stdin when enabled, which can block interactive use. Tests cover helper validation, backend config parsing, target/cache references, prefetch conflicts, log files, and archive validation, but not full command execution against registries.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/cmd/nydusify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/cmd/nydusify_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/cmd/nydusify_test.go

## Purpose
This unit test file validates the helper functions that turn CLI flags and inputs into normalized `nydusify` behavior.

## Important APIs, Types, and Functions
Tests cover `isPossibleValue`, `addReferenceSuffix`, `parseBackendConfig`, `getBackendConfig`, `getTargetReference`, `getCacheReference`, `getPrefetchPatterns`, `getGlobalFlags`, `setupLogLevel`, and `validateSourceAndTargetArchives`. It uses `gomonkey`, `testify/require`, `testify/assert`, and urfave CLI contexts.

## Control Flow
Tests construct temporary files, flag sets, and CLI contexts to exercise success and failure paths. `setupLogLevel` tests monkeypatch `cli.Context.String` to drive log-file behavior. Archive validation tests create temporary source files and directories and table-test missing path errors.

## State, Persistence, and Dependencies
Tests create temporary backend config files and log files, remove them afterward, and mutate the global logrus output. They do not call external registry or conversion workflows.

## Integration Points
The tests stabilize the public CLI helper contract used by `convert`, `check`, and related commands. They are especially relevant for environment/flag compatibility because helpers are reused with prefixes.

## Risks and Test Signals
Coverage is strong for small pure helpers but light for command-level integration, stdin prefetch content, reverse conversion dispatch, and package workflow options beyond helper outputs. Monkeypatching logrus and CLI methods can leave global side effects if a test fails before cleanup, though defers mitigate most cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/cmd/nydusify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/examples/converter/main.go -->
# sources/cloud-native/nydus/contrib/nydusify/examples/converter/main.go

## Purpose
This example demonstrates embedding the converter package directly from Go instead of invoking the `nydusify` CLI.

## Important APIs, Types, and Functions
It imports `converter`, builds a `converter.Opt`, and calls `converter.Convert(context.Background(), opt)`.

## Control Flow
`main` sets sample work directory, nydus-image path, source, target, platform, insecure flags, prefetch patterns, merge setting, and Docker-to-OCI conversion flag. It panics on conversion error.

## State, Persistence, and Dependencies
State and persistence are delegated to `converter.Convert`, which may create temporary work directories, push images, and invoke `nydus-image`. This file depends on `context` and the local converter package.

## Integration Points
It is a developer-facing code sample for library-style integration of conversion behavior.

## Risks and Test Signals
The hard-coded `nydus-image` path and registry references are placeholders, so running it as-is will usually fail. It does not expose backend, cache, or retry options. The companion test monkeypatches `converter.Convert` to validate the option wiring.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/examples/converter/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/examples/converter/main_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/examples/converter/main_test.go

## Purpose
This test ensures the converter example constructs the expected `converter.Opt` and calls `converter.Convert`.

## Important APIs, Types, and Functions
It monkeypatches `converterpkg.Convert`, invokes example `main`, and asserts selected option fields.

## Control Flow
The patch replaces conversion with a function that checks work dir, binary path, source, target, insecure flags, and platform. Then `main()` is called directly.

## State, Persistence, and Dependencies
No real conversion or persistence happens. Dependencies are `gomonkey`, `testify/require`, and the converter package.

## Integration Points
It guards the example from drifting away from converter API expectations.

## Risks and Test Signals
The test does not validate all options in the example, and it depends on monkeypatch support. It is a narrow wiring test, not an end-to-end conversion signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/examples/converter/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/examples/manifest/cache_manifest.json -->
# sources/cloud-native/nydus/contrib/nydusify/examples/manifest/cache_manifest.json

## Purpose
This JSON file is a sample OCI image manifest representing a Nydus build-cache image. It illustrates how cache records are stored as alternating Nydus blob and bootstrap layers.

## Important APIs, Types, and Functions
Important fields are `mediaType`, `schemaVersion`, `config`, `layers`, and manifest-level `annotations`. Layers use Nydus blob media type `application/vnd.oci.image.layer.nydus.blob.v1` and bootstrap tar gzip media type with annotations such as `containerd.io/snapshot/nydus-bootstrap`, `containerd.io/snapshot/nydus-source-chainid`, `containerd.io/uncompressed`, and `containerd.io/snapshot/nydus-reference-blob-ids`.

## Control Flow
The file is static data consumed by humans or tests as an example. Cache import/export code in `pkg/cache` uses the same annotation conventions to reconstruct `Record` objects.

## State, Persistence, and Dependencies
It models persisted registry manifest state. The referenced digests and sizes are sample values.

## Integration Points
This sample aligns with the cache package’s `Manifest` and `Record` conversion logic. It also documents how Nydus build cache layers can reference shared blob IDs.

## Risks and Test Signals
Because it is static, it can drift from current annotation names or media types. It is not itself a test, but it is a strong format signal for maintainers and users.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/examples/manifest/cache_manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/examples/manifest/index.json -->
# sources/cloud-native/nydus/contrib/nydusify/examples/manifest/index.json

## Purpose
This JSON file is a sample image index containing both a standard Docker/OCI image manifest and a Nydus manifest for the same platform.

## Important APIs, Types, and Functions
Fields include `schemaVersion` and `manifests`. Each manifest has `mediaType`, `digest`, `size`, and `platform`. The Nydus entry is identified by OCI media type and `artifactType: application/vnd.nydus.image.manifest.v1+json`.

## Control Flow
The file is static documentation/example data. Parser and checker code in the broader nydusify tree use similar structure when handling merged or multi-platform images.

## State, Persistence, and Dependencies
It represents persisted registry index state. No runtime behavior occurs.

## Integration Points
The example supports `--merge-platform` and checker multi-platform concepts by showing source and Nydus artifacts coexisting in an index.

## Risks and Test Signals
Static examples can drift from current OCI artifact conventions. The file is useful for format comprehension but does not validate code by itself.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/examples/manifest/index.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/examples/manifest/manifest.json -->
# sources/cloud-native/nydus/contrib/nydusify/examples/manifest/manifest.json

## Purpose
This JSON file is a sample Nydus image manifest showing multiple Nydus blob layers followed by a bootstrap layer.

## Important APIs, Types, and Functions
It includes `schemaVersion`, `config`, and `layers`. Blob layers use Nydus blob media type and `containerd.io/snapshot/nydus-blob` annotations. The final bootstrap layer uses a gzip tar media type and annotations including `containerd.io/snapshot/nydus-bootstrap` and `containerd.io/snapshot/nydus-reference-blob-ids`.

## Control Flow
The file is static example data. Manifest checker rules enforce a related invariant: non-final layers are Nydus blobs and the final layer is a bootstrap for non-model artifacts.

## State, Persistence, and Dependencies
It models registry manifest persistence. Digests and sizes are sample identifiers.

## Integration Points
The file documents the shape expected by parser/checker/cache logic and by runtimes consuming Nydus images.

## Risks and Test Signals
The example is only as accurate as its maintenance. It is not executable but helps identify media type and annotation expectations used elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/examples/manifest/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/backend.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/backend.go

## Purpose
This file defines the backend abstraction used by nydusify to upload, check, and read Nydus blob artifacts from registry, OSS, or S3 storage.

## Important APIs, Types, and Functions
`Backend` is the central interface with `Upload`, `Finalize`, `Check`, `Type`, `Reader`, `RangeReader`, and `Size`. Backend type constants are `OssBackend`, `RegistryBackend`, and `S3backend`. `blobDesc` builds OCI descriptors for Nydus blobs. `NewBackend` selects concrete implementations from a backend type string.

## Control Flow
Callers create a backend via `NewBackend`, upload blobs through `Upload`, optionally finalize or cancel pending state, and use checks/readers when validating or building cache. `blobDesc` consistently annotates descriptors with uncompressed digest and Nydus blob marker.

## State, Persistence, and Dependencies
This abstraction has no concrete state. It depends on containerd remote range reader interfaces, OCI descriptors, digest helpers, local remote package, and media annotation constants from `utils`.

## Integration Points
Converter/cache/checker flows depend on this interface to abstract storage. Registry uses OCI distribution; OSS and S3 use object storage and expose remote URLs in descriptors.

## Risks and Test Signals
Concrete backends do not implement all methods equally; registry reader methods panic. The type string switch must stay aligned with CLI validation. Tests cover descriptor creation and constructor dispatch for oss, s3, registry, and unsupported backends.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/backend_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/backend_test.go

## Purpose
This test file validates backend descriptor generation and factory selection.

## Important APIs, Types, and Functions
Tests include `TestBlobDesc` and `TestNewBackend`. They exercise `blobDesc`, `NewBackend`, `newOSSBackend`, `newS3Backend`, and `newRegistryBackend` indirectly.

## Control Flow
The tests build sample JSON configs, construct backends for OSS/S3/registry, assert returned type constants, and assert unsupported types return errors. `TestBlobDesc` checks size, digest, media type, and annotations.

## State, Persistence, and Dependencies
Tests do not contact real services. SDK constructors validate some local config shape. Dependencies include `testify/require`, JSON validation, provider remote creation, and utility constants.

## Integration Points
These tests guard the backend creation contract used by CLI and conversion code.

## Risks and Test Signals
They do not test actual upload/read/check behavior or network paths. They rely on SDK validation for OSS/S3 config without mocking remote object storage.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/backend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/oss.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/oss.go

## Purpose
This file implements the Alibaba Cloud OSS backend for Nydus blobs. It uploads blobs as multipart OSS objects, optionally skips existing objects, verifies CRC64 integrity, and exposes object readers/range readers.

## Important APIs, Types, and Functions
`OSSBackend` stores object prefix, OSS bucket, pending multipart statuses, and mutex. `multipartStatus` tracks initiated upload, parts, object key, and CRC channels. Functions include `newOSSBackend`, `calcCrc64ECMA`, `Upload`, `Finalize`, `Check`, `RangeReader`, `Reader`, `Size`, and `remoteID`.

## Control Flow
`newOSSBackend` parses JSON config, validates endpoint and bucket, creates SDK client and bucket handle. `Upload` builds a blob descriptor and URL, skips existing objects unless forced, starts CRC calculation in a goroutine, splits the file into 200 MB chunks, uploads parts concurrently with `errgroup`, appends multipart status, and returns before completion. `Finalize(false)` completes each multipart upload and compares server CRC64 against local CRC when available; `Finalize(true)` aborts pending uploads.

## State, Persistence, and Dependencies
Persistent state is OSS objects. In-memory state is the pending multipart list guarded by `msMutex`. Dependencies include aliyun OSS SDK, crc64, errgroup, logrus, HTTP headers, and OCI descriptors.

## Integration Points
Converter code can upload blobs into OSS while cache manifests record blob descriptors/remote IDs. Checker/cache can use `Check`, `Reader`, `RangeReader`, and `Size` for validation.

## Risks and Test Signals
Multipart upload is two-phase: callers must call `Finalize`, or uploaded parts may remain pending. CRC goroutine channels are consumed only in finalize. Object key is simple prefix concatenation, so missing slashes in prefix change paths. `calcCrc64ECMA` error text says md5sum, a misleading message. Tests cover config parsing, remote ID, type, and CRC calculation, but not real multipart upload/finalize.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/oss.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/oss_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/oss_test.go

## Purpose
This test file validates OSS backend configuration, remote ID formatting, backend type, and local CRC64 calculation.

## Important APIs, Types, and Functions
It defines `tempOSSBackend` and tests `calcCrc64ECMA`, `remoteID`, `newOSSBackend`, and `Type`.

## Control Flow
Tests create temporary files for CRC checks, build several JSON config variants, and assert expected success or validation errors from OSS SDK bucket naming rules.

## State, Persistence, and Dependencies
Temporary files are created and removed. The tests instantiate SDK bucket objects but do not upload to real OSS. Dependencies include `hash/crc64`, `os`, JSON validation, and `testify/require`.

## Integration Points
The tests stabilize the accepted OSS config shape and descriptor URL formatting used by conversion and cache manifests.

## Risks and Test Signals
No test covers multipart upload, abort, complete, remote reads, or CRC header verification. SDK behavior may change validation error strings, making tests brittle.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/oss_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/registry.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/registry.go

## Purpose
This file implements the registry backend for storing Nydus blobs as OCI/distribution blob layers.

## Important APIs, Types, and Functions
`Registry` wraps a `remote.Remote`. Methods implement `Upload`, `Finalize`, `Check`, `Type`, and placeholder `RangeReader`, `Reader`, and `Size` methods that panic.

## Control Flow
`Upload` builds a Nydus blob descriptor, opens the blob file, and pushes it through `remote.Push` by digest. `Finalize` is a no-op. `Check` returns true without remote verification. `newRegistryBackend` creates the wrapper.

## State, Persistence, and Dependencies
Persistent state is the remote registry blob store. Local state is just the remote handle. Dependencies include OCI descriptors, containerd range reader interfaces, local `remote`, and filesystem open.

## Integration Points
This is the default backend for nydusify cache and conversion when storing blobs in registry manifests. It uses the same descriptor annotations as other backends.

## Risks and Test Signals
`Check` returning true can mask missing blobs. Reader methods panic, so callers must avoid using registry backend for direct object reads. `forcePush` is ignored because registries do not allow overwriting existing blobs. Tests cover upload success/failure via monkeypatched remote push, helpers, constructor, and panic behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/registry_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/registry_test.go

## Purpose
This file tests registry backend upload behavior, helper methods, constructor behavior, and expected panics for unimplemented readers.

## Important APIs, Types, and Functions
Tests cover `Registry.Upload`, `Finalize`, `Check`, `Type`, `RangeReader`, `Reader`, `Size`, and `newRegistryBackend`. They use `gomonkey` to patch `remote.Remote.Push`.

## Control Flow
Upload tests create a temporary blob file, patch `Push` to validate descriptor and reader content, then assert returned descriptor metadata. Failure tests cover missing file and push error. Panic tests assert direct reader methods panic.

## State, Persistence, and Dependencies
Tests use temp files and monkeypatch the remote type. No network registry is contacted. Dependencies include digest, OCI descriptors, `testify/require`, and gomonkey.

## Integration Points
These tests guard the registry backend contract used by cache and converter code.

## Risks and Test Signals
The tests intentionally encode that read methods panic and `Check` is optimistic. They do not validate actual registry resolver behavior or retry semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/registry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/s3.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/s3.go

## Purpose
This file implements an S3-compatible object storage backend for Nydus blob uploads and reads.

## Important APIs, Types, and Functions
`S3Backend` stores object prefix, bucket name, endpoint with scheme, and S3 client. `S3Config` defines JSON config fields. Methods include `newS3Backend`, `Upload`, `Finalize`, `Check`, `Type`, `existObject`, `blobObjectKey`, `RangeReader`, `Reader`, `Size`, and `remoteID`. `rangeReader` implements containerd range reads.

## Control Flow
`newS3Backend` parses JSON, defaults endpoint to `s3.amazonaws.com` and scheme to `https`, requires bucket and region, loads AWS default config, and customizes endpoint, region, path-style addressing, and static credentials if provided. `Upload` creates a descriptor and URL, checks existence unless forced, opens the file, uploads with AWS manager multipart uploader using the shared 200 MB part size and CRC32 checksum, then returns the descriptor. Read methods issue `GetObject`, ranged `GetObject`, or object attributes calls.

## State, Persistence, and Dependencies
Persistent state is S3 objects. Runtime state is an AWS SDK client. Dependencies include AWS SDK v2, manager uploader, HTTP errors, URL/path helpers, OCI descriptors, and logrus.

## Integration Points
The backend plugs into the same `Backend` interface as OSS/registry. Nydusify can record returned URLs and descriptors in manifests/cache and later validate object presence.

## Risks and Test Signals
`Size` dereferences `output.ObjectSize` without nil check. `remoteID` ignores URL parse errors and uses path join, which can normalize prefixes unexpectedly. Default AWS config loading may consult environment/metadata services depending on SDK behavior. Tests cover config defaults, static credentials, object key, remote ID, type, and finalize no-op, but not live upload/read/check behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/s3_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/s3_test.go

## Purpose
This test file validates S3 backend construction, config defaults, credentials wiring, object key construction, remote URL formatting, and type/finalize helpers.

## Important APIs, Types, and Functions
It defines `tempS3Backend` and tests `remoteID`, `blobObjectKey`, `newS3Backend`, `Type`, and `Finalize`.

## Control Flow
Tests build valid and invalid JSON configs, assert parsed backend fields, retrieve AWS credentials from the configured provider, and check error handling for malformed JSON and missing required fields.

## State, Persistence, and Dependencies
No real S3 calls are made. Tests depend on AWS SDK config/credential types and `testify/require`.

## Integration Points
The tests document the JSON contract expected by CLI `--backend-config` for S3 storage.

## Risks and Test Signals
Coverage does not include `Upload`, `Check`, range reads, full reads, or size queries. Tests can be sensitive to AWS SDK config-loading behavior in unusual environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/backend/s3_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/cache/cache.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/cache/cache.go

## Purpose
This package implements Nydus build cache manifests. It maps source layer chain IDs to generated Nydus bootstrap/blob descriptors so later conversions can skip rebuilding layers and reuse cached artifacts.

## Important APIs, Types, and Functions
`Opt` configures max records, cache version, RAFS fs version, Docker media type compatibility, and backend. `Cache` holds remote, pulled records, reference records, and records to push. Key methods are `New`, `GetReference`, `SetReference`, `recordToLayer`, `exportRecordsToLayers`, `layerToRecord`, `importRecordsFromLayers`, `Export`, `Import`, `Check`, `Record`, `PullBootstrap`, and `Push`. `Record.GetReferenceBlobs` parses referenced blob IDs.

## Control Flow
Import resolves and pulls a cache manifest, validates cache version and fs version, and imports layers into records. `layerToRecord` parses bootstrap, blob, or reference blob layers from annotations. `recordToLayer` emits bootstrap and optional blob descriptors, with different behavior for registry versus object backends. `Record` maintains a bounded front-biased queue. `Export` emits layers, builds config rootfs diff IDs, pushes config, then pushes the cache manifest. `Check` verifies cached bootstrap and blob availability and returns readers.

## State, Persistence, and Dependencies
Persistent state is the remote cache image manifest/config/layers and possibly backend blob objects. In-memory state is maps by digest and ordered pushed records. Dependencies include containerd image media types, OCI descriptors, digest, local backend/remote/utils packages, and JSON.

## Integration Points
Converter code uses this package for `--build-cache` and related flags. It integrates tightly with backend type behavior: registry stores blob layers in the cache manifest, while OSS/S3 record blob digest/size annotations on bootstrap layers.

## Risks and Test Signals
Risk includes nil backend assumptions in `recordToLayer`, invalid or missing annotations silently dropping records, optimistic registry checks, and diff ID compatibility with Docker pulls. `exportRecordsToLayers` assumes referenced registry records exist before dereferencing blob descriptors. Tests are broad for record/layer conversion, queue behavior, import/export success and errors, check paths, and pull/push wrappers, but most remote behavior is mocked.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/cache/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/cache/cache_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/cache/cache_test.go

## Purpose
This file provides extensive unit coverage for Nydus cache record parsing, export/import behavior, bounded queue ordering, and remote interaction error handling.

## Important APIs, Types, and Functions
It defines helpers `makeRecord`, `makeBootstrapLayer`, `makeBlobLayer`, `testWithBackend`, mock content writer/fetcher/pusher/resolver types, and tests for `GetReferenceBlobs`, `layerToRecord`, `recordToLayer`, `SetReference`, `mergeRecord`, `Record`, `Export`, `Import`, `Check`, `Push`, and `PullBootstrap`.

## Control Flow
Tests create synthetic descriptors and records, compare exported layers for registry and object backends, simulate remote resolve/fetch/push through mocks, and assert expected errors for version mismatch, fs version mismatch, pull errors, push errors, and absent records.

## State, Persistence, and Dependencies
The tests use in-memory buffers and mock remotes, not real registries. Some temporary target paths are used for pull bootstrap error cases. Dependencies include containerd content/remotes, errdefs, OCI specs, digest, backend, remote, utils, and testify.

## Integration Points
These tests are the main safety net for cache manifest format compatibility and backend-specific layer encoding.

## Risks and Test Signals
Coverage is strong for pure cache logic but not for real registry auth, network retries, Docker pull compatibility, or backend object existence beyond mocks. Some tests use generated digests from strings rather than real SHA-256 encodings, which is fine for logic but less representative of production descriptors.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/cache/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/cache/spec.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/cache/spec.go

## Purpose
This file defines the small data model used by the cache package for cache manifests and records.

## Important APIs, Types, and Functions
`Manifest` embeds `ocispec.Manifest` and adds an optional `mediaType` JSON field. `Record` stores a source chain ID, optional Nydus blob descriptor, Nydus bootstrap descriptor, and bootstrap diff ID.

## Control Flow
These types are passive structs. Cache import/export methods populate and consume them.

## State, Persistence, and Dependencies
`Manifest` maps directly to persisted registry JSON. `Record` is in-memory cache state. Dependencies are OCI descriptors and `opencontainers/go-digest`.

## Integration Points
`cache.go` uses these types to convert between OCI manifest layers and internal cache records. Other converter code consumes `Record` values for cache hits.

## Risks and Test Signals
The structs intentionally allow nil descriptors, so callers must guard when converting records. Tests in `cache_test.go` exercise many valid and invalid combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/cache/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/checker.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/checker.go

## Purpose
This file implements the high-level Nydus image checker orchestration. It parses source/target images, writes diagnostic artifacts, and runs manifest, bootstrap, and filesystem validation rules.

## Important APIs, Types, and Functions
`Opt` captures workdir, image refs, insecurity flags, backend config, multi-platform flag, binary paths, and expected architecture. `Checker` stores options plus source and target parsers. Important methods are `New`, `Check`, and internal `check`.

## Control Flow
`New` creates a target remote/parser and optionally source remote/parser. `Check` calls `check`, and if the error is retryable with HTTP, it toggles source/target remotes to HTTP and retries once. `check` parses target and optional source, removes the work directory, outputs source/target image info, creates three rule objects, and validates each in order.

## State, Persistence, and Dependencies
Persistent output is written under `WorkDir`, including manifests, configs, bootstrap contents, and rule outputs. Dependencies include provider/default remotes, parser, checker rules, utils retry logic, filesystem cleanup, and logrus.

## Integration Points
This is invoked by `nydusify check`. It integrates parser output with rules from `pkg/checker/rule`, and passes backend information to bootstrap/filesystem validators.

## Risks and Test Signals
`os.RemoveAll(WorkDir)` is destructive for the configured path. Retrying with HTTP mutates remote state after certain errors. The `MultiPlatform` option is present but not used in this file directly. Tests cover constructor failures/success, HTTP retry, cleanup/output/rule failure paths via monkeypatches.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/checker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/checker_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/checker_test.go

## Purpose
This test file validates checker construction, retry behavior, and internal check error handling.

## Important APIs, Types, and Functions
Tests target `New`, `Check`, and `check`. They monkeypatch `parser.New`, `parser.Parser.Parse`, `Checker.Output`, and rule `Validate` methods.

## Control Flow
Constructor tests simulate target remote failure, parser failure, source remote failure, source parser failure, and success. `TestCheck` simulates a retryable HTTPS connection error and confirms HTTP fallback, then a non-retryable parse error. `TestCheckInternal` covers cleanup failure, source parse failure, output failures, and rule validation failure.

## State, Persistence, and Dependencies
Most tests use temporary workdirs or invalid paths. No real registries or binaries are invoked due to monkeypatching. Dependencies include gomonkey, parser, remote, rule, syscall, and testify.

## Integration Points
These tests guard the orchestration layer without depending on parser/rule internals.

## Risks and Test Signals
Monkeypatch-heavy tests can miss integration mismatches between real parser output and rule inputs. They do not cover successful full validation with real image data.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/checker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/output.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/output.go

## Purpose
This file writes parsed OCI/Nydus image metadata and pulled Nydus bootstrap contents into the checker work directory. It also validates bootstrap diff ID consistency and model artifact subject shape.

## Important APIs, Types, and Functions
`prettyDump` marshals objects as indented JSON to files. `Checker.Output` writes index, manifest, config, and bootstrap artifacts for a parsed image.

## Control Flow
`Output` creates the output directory, writes OCI and/or Nydus index/manifest/config JSON depending on parsed content, pulls the Nydus bootstrap layer when present, decompresses it, unpacks the tar into `nydus_bootstrap`, hashes the uncompressed tar stream, and compares the calculated digest with the last rootfs diff ID except for model artifacts. Model manifests require a subject with image-manifest media type.

## State, Persistence, and Dependencies
Persistent outputs include `oci_index.json`, `nydus_index.json`, `oci_manifest.json`, `oci_config.json`, `nydus_manifest.json`, `nydus_config.json`, and unpacked bootstrap files. Dependencies include JSON, containerd compression, digest, parser, checker tool image type, utils tar unpacking, OCI spec, and model-spec.

## Integration Points
Checker rules expect output artifacts, especially bootstrap files under `WorkDir/<source|target>/nydus_bootstrap`. This function bridges parser/remote state to filesystem-based validation.

## Risks and Test Signals
The parser selection uses `dir == "source"` rather than robust path identity, so callers must pass exact labels. It indexes `diffIDs[len(diffIDs)-1]` without an explicit empty check for non-model Nydus images. Tests cover JSON dump, OCI output, bootstrap diff mismatch, model subject errors, and successful bootstrap unpacking with monkeypatched pull.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/output.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/output_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/output_test.go

## Purpose
This file tests checker output generation, JSON dump error behavior, bootstrap unpacking, diff ID validation, and model artifact subject validation.

## Important APIs, Types, and Functions
It defines `buildBootstrapLayer` to create an in-memory gzip-compressed tar and tests `prettyDump` plus `Checker.Output`.

## Control Flow
Tests write OCI parsed artifacts to a temp directory and assert expected files exist. Nydus tests monkeypatch `Parser.PullNydusBootstrap`, first trigger diff ID mismatch, then model manifest missing subject, invalid subject media type, and success with a valid image manifest subject.

## State, Persistence, and Dependencies
Temporary directories are used for most output, but the Nydus validation test writes to literal `source` and removes it afterward. Dependencies include archive/tar, gzip, digest, OCI spec, parser, remote, utils, gomonkey, and testify.

## Integration Points
These tests ensure the checker’s filesystem outputs match downstream rule expectations.

## Risks and Test Signals
The literal `source` directory can collide with a working directory if cleanup fails. Tests do not cover empty diff ID slices or pull/decompression failures beyond the monkeypatched success path.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/output_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/bootstrap.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/bootstrap.go

## Purpose
This rule validates that a Nydus bootstrap is structurally valid and that blobs recorded inside the bootstrap are represented by manifest blob layers, except for OCI reference layers.

## Important APIs, Types, and Functions
`BootstrapRule` stores workdir, `nydus-image` path, parsed source/target images, and backend configs. `output` models `nydus-image check` debug JSON with a `blobs` array. Methods are `Name`, `validate`, and `Validate`.

## Control Flow
`validate` skips nil/non-Nydus parsed images, runs `nydus-image check` through `tool.Builder.Check` against the unpacked bootstrap path, reads and unmarshals debug output, builds a set of blob digests from all manifest layers except the final bootstrap and layers annotated as OCI reference layers, then ensures bootstrap blob IDs all appear in manifest layers when manifest blob layers are present. `Validate` applies this to source and target.

## State, Persistence, and Dependencies
It reads bootstrap files and writes/reads `nydus_output.json` under the checker workdir. Dependencies include checker tool builder, parser, nydus snapshotter label constants, utils bootstrap file name, JSON, and logrus.

## Integration Points
This rule depends on `checker.Output` having already unpacked bootstrap files. It integrates external `nydus-image` binary validation with manifest-level consistency checks.

## Risks and Test Signals
If there are no blob layers in the manifest, missing bootstrap blobs are tolerated. Blob digest comparison uses hex strings from descriptors. External binary failures are wrapped as invalid bootstrap format. Tests monkeypatch builder checks to cover success, missing blob mismatch, reference-layer skip, bad JSON, and missing output file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/bootstrap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/bootstrap_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/bootstrap_test.go

## Purpose
This test file validates bootstrap rule behavior without invoking a real `nydus-image` binary.

## Important APIs, Types, and Functions
It monkeypatches `tool.Builder.Check`, constructs synthetic `parser.Parsed` and `parser.Image` values, and tests `BootstrapRule.validate`.

## Control Flow
The main test writes synthetic debug JSON matching or missing manifest blob IDs, asserts success or mismatch, then marks a layer as a Nydus reference layer to ensure it is ignored. Error tests write invalid JSON or remove the expected output file and assert wrapped read/unmarshal errors.

## State, Persistence, and Dependencies
Temporary workdirs hold fake bootstrap and output paths. Dependencies include JSON, filesystem APIs, gomonkey, digest, OCI spec, parser, remote, utils, and snapshotter label constants.

## Integration Points
The tests stabilize the contract between `nydus-image check` debug output and manifest layer validation.

## Risks and Test Signals
Tests do not cover real bootstrap parsing or actual `nydus-image` execution. They focus on the rule’s interpretation of debug output and annotations.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/bootstrap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/filesystem.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/filesystem.go

## Purpose
This rule validates filesystem equivalence between source and target images by mounting them, walking both root filesystems, and comparing metadata, symlink targets, xattrs, and file content hashes.

## Important APIs, Types, and Functions
`FilesystemRule` stores workdir, `nydusd` path, source/target images, and backend configs. `Image` wraps parsed image and insecure flag. `Node` captures path, size, mode, rdev, symlink, UID, GID, xattrs, and hash. Key functions are `getXattrs`, `walk`, `mountNydusImage`, `mountOCIImage`, `mountImage`, `verify`, and `Validate`. `WorkerCount` controls source layer pull concurrency.

## Control Flow
`Validate` skips if either parsed image is nil, mounts source and target, defers unmounts, and calls `verify`. OCI mount pulls layers concurrently, unpacks them, and mounts overlay via `tool.Image`. Nydus mount builds `tool.NydusdConfig`, derives registry backend config if not supplied, enables digest validation for RAFS V5, handles model artifact external backend config, starts nydusd, and returns an unmount cleanup function. `verify` walks both trees concurrently and compares all nodes except root.

## State, Persistence, and Dependencies
Persistent/transient state includes layer unpack directories, mountpoints, nydusd cache/config/API socket directories, and external backend config files. Dependencies include parser, checker tools, utils, xattr library, model-spec, OCI reference parsing, syscall stat, worker pool, and logrus.

## Integration Points
This is the deepest end-to-end checker rule. It integrates registry pulls, tar unpacking, overlay mounting, nydusd mounting, backend configuration generation, and filesystem hashing.

## Risks and Test Signals
It requires privileges and working mount/nydusd binaries in real use. `walk` always hashes regular files, despite a comment suggesting backend-type gating, causing full data reads. Node comparison includes UID/GID/xattrs/rdev, which may vary by environment. `mountOCIImage` may leak readers because pulled layer readers are not explicitly closed in the visible code. Tests cover walking, node string, xattrs, verify success/missing/extra/mismatch, invalid mount image, and skip behavior, but not real mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/filesystem_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/filesystem_test.go

## Purpose
This test file covers pure filesystem rule helpers and also contains manifest/bootstrap rule name and manifest validation tests.

## Important APIs, Types, and Functions
Tests cover `FilesystemRule.Name`, `Node.String`, `ManifestRule.Name`, `BootstrapRule.Name`, `ManifestRule.validateOCI`, `ManifestRule.validateNydus`, `ManifestRule.validateConfig`, `ManifestRule.validate`, `FilesystemRule.walk`, `FilesystemRule.verify`, `getXattrs`, `mountImage`, and `Validate` skip behavior.

## Control Flow
Tests create temporary directory trees with files, subdirectories, and symlinks; walk them; compare identical and mismatched roots; and exercise manifest validation with synthetic OCI/Nydus images. No real mounts are performed except validation of the invalid-image branch.

## State, Persistence, and Dependencies
Temporary directories and files are created by tests. Dependencies include digest, OCI spec, parser, utils, and testify.

## Integration Points
The file is an important unit safety net for checker rule logic that can be tested without root privileges or external binaries.

## Risks and Test Signals
The tests do not exercise `mountOCIImage`, `mountNydusImage`, worker pool layer pulls, backend config generation, model artifact path, or unmount cleanup. Some manifest tests are located here rather than in `manifest_test.go`, which can make ownership less obvious.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/filesystem_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/manifest.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/manifest.go

## Purpose
This rule validates OCI and Nydus image manifest structure and compares source and target image configs when both are present.

## Important APIs, Types, and Functions
`ManifestRule` stores parsed source and target images. Methods include `Name`, `validateConfig`, `validateOCI`, `validateNydus`, `validate`, and `Validate`.

## Control Flow
`validate` skips nil parsed input, logs image type, then validates either OCI or Nydus image shape. OCI validation checks rootfs diff ID count equals layer count except for model artifacts. Nydus validation requires the final layer to be a bootstrap, non-final layers to be Nydus blob layers for non-model artifacts, model artifact annotation consistency on the final layer, and matching diff ID count. `Validate` runs source and target validation, then compares source and target `ImageConfig` JSON after normalizing deprecated `ArgsEscaped`.

## State, Persistence, and Dependencies
The rule is pure in-memory validation. Dependencies include JSON, reflection, model-spec artifact types, parser types, checker tool logging helpers, and utils annotation/media constants.

## Integration Points
It is the first rule run by checker and establishes basic manifest correctness before bootstrap and filesystem validation. It supports both normal container images and model artifacts.

## Risks and Test Signals
`validateNydus` indexes `layer.Annotations[...]` without checking nil maps, but reading from a nil map is safe in Go; however, empty layer lists would skip bootstrap validation and then only diff ID count may catch issues. Config comparison by marshaled JSON is strict and may flag semantically equivalent but differently normalized configs. Tests in `filesystem_test.go` cover name, OCI diff ID mismatch, Nydus bootstrap/blob validation, config equality/mismatch, and nil parsed input.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/manifest.go -->
