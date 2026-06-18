# subset-b-000034 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/bootloader.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-boot/src/bootloader.rs

## Purpose
This module discovers, parses, normalizes, and represents boot resources embedded in a composefs filesystem image. It covers Boot Loader Specification Type 1 entries under `/boot/loader/entries`, Type 2 Unified Kernel Images under `/boot/EFI/Linux` and `/usr/lib/modules`, and traditional `/usr/lib/modules/<kver>/vmlinuz` plus `initramfs.img` layouts. It is the extraction side of the boot pipeline later consumed by `write_boot.rs` and `BootOps::transform_for_boot`.

## Important APIs, types, and functions
`BootLoaderEntryFile` stores parsed BLS lines and exposes `new`, `get_value`, `get_values`, `add_cmdline`, and `adjust_cmdline`. `strip_ble_key` implements BLS key matching with required whitespace, while `substr_range` lets code replace a substring slice inside its parent line.

`Type1Entry<ObjectID>` owns a BLS filename, parsed entry, and a map of referenced boot files. `Type1Entry::load_all` walks `/boot/loader/entries`, filters `.conf`, validates regular files, and loads referenced `linux`, `initrd`, and `efi` paths. `Type1Entry::relocate` renames the entry file and rewrites resource paths into an entry-id directory.

`Type2Entry<ObjectID>` represents UKI/addon PE files with optional kernel version, relative `file_path`, `RegularFile`, and `PEType`. `load_all` scans `/boot/EFI/Linux` and every `/usr/lib/modules/<kver>` directory. `find_uki_components` recursively collects `.efi` files and classifies top-level files as UKIs and nested files as addons.

`UsrLibModulesVmlinuz` represents legacy module-directory kernels. `into_type1` synthesizes a BLS Type 1 entry from `vmlinuz` and `initramfs.img`. `BootEntry` unifies all three resource variants, and `get_boot_resources` returns all discovered variants.

## Control flow
Discovery runs Type 1, Type 2, and module-vmlinuz loaders sequentially. Missing optional directories are treated as empty discovery results, while unexpected image errors propagate. Type 1 loading reads the BLS file contents from the repository, parses line-oriented key values, then resolves each referenced resource through the filesystem tree. Type 2 loading recursively traverses directories and collects PE candidates without parsing PE internals here. The vmlinuz fallback only creates entries for module directories containing `vmlinuz`; missing `initramfs.img` is tolerated during discovery but becomes an error in `into_type1`.

## State and persistence behavior
The module mutates only in-memory representations. `BootLoaderEntryFile::add_cmdline` modifies stored lines, replacing an existing key-like argument or appending one. `Type1Entry::relocate` mutates `filename`, BLS path strings, and the `files` map so future writing emits a coherent relocated tree. It does not write to disk; persistence is handled by `write_boot.rs`.

## Dependencies and integration points
It depends on composefs tree/repository APIs for directory lookup, file reading, inode inspection, and `RegularFile` cloning. It uses `crate::cmdline` for composefs kernel arguments. Its main consumers are `composefs-boot::BootOps::transform_for_boot`, which extracts resources before clearing `/boot`, and `write_boot_simple`, which writes selected `BootEntry` variants to a boot partition.

## Risks
`Type1Entry::relocate` only rewrites values containing `/`; relative or unusual BLS paths are left unchanged. It removes files by original full value and reinserts by the new internal path, so duplicate references or unsupported keys can be surprising. `add_cmdline` treats bare arguments as their own replacement key, so adding `ro` after `rw` appends rather than replacing read/write semantics. Type 2 discovery classifies any recursive `.efi` file under searched roots as UKI/addon material without validating PE sections. `UsrLibModulesVmlinuz::into_type1` uses placeholder title/version strings.

## Test signals
Unit tests cover generated Type 1 entries with and without initramfs, BLS parsing behavior, multiple values, whitespace handling, command-line insertion/replacement, composefs argument adjustment, `strip_ble_key`, and `substr_range`. There is no direct fixture coverage in this file for recursive UKI discovery, BLS resource loading from a real `FileSystem`, or relocation plus write integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/bootloader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/cmdline.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-boot/src/cmdline.rs

## Purpose
This module provides kernel command-line parsing and formatting helpers for composefs boot support. Its main responsibility is locating and constructing `composefs=` arguments, including the optional insecure marker that means fs-verity validation can be skipped.

## Important APIs, types, and functions
`split_cmdline` is a crate-private iterator helper that splits on ASCII whitespace while preserving whitespace inside double quotes. It intentionally matches the kernel's simple quoting model and does not implement backslash escaping.

`get_cmdline_value(cmdline, prefix)` scans split command-line items and returns the suffix of the first item that starts with a requested prefix. `get_cmdline_composefs<ObjectID>` finds `composefs=`, parses the hash using the `FsVerityHashValue` implementation, and returns `(ObjectID, insecure)`. A leading `?` on the value sets the insecure flag and is stripped before hash parsing. `make_cmdline_composefs(id, insecure)` emits either `composefs=<id>` or `composefs=?<id>`.

## Control flow
Parsing is linear. The splitter toggles an `in_quotes` flag when encountering `"`, and a character becomes a delimiter only if it is ASCII whitespace outside quotes. `get_cmdline_composefs` first requires a `composefs=` item, then chooses the secure or insecure parse branch based on `strip_prefix('?')`. Parse errors are annotated with expected hex length and algorithm name.

## State and persistence behavior
There is no persistent state. All functions operate on borrowed strings and return borrowed slices or owned formatted strings. The only externally visible state encoded by this module is the `?` prefix in the command-line value.

## Dependencies and integration points
It depends on `anyhow` for contextual errors and on `composefs::fsverity::FsVerityHashValue` for algorithm-specific hex parsing. `bootloader.rs` uses `split_cmdline` and `make_cmdline_composefs` to update BLS options. `write_boot.rs` uses `get_cmdline_composefs` to verify a UKI's embedded `.cmdline` points at the expected composefs image hash before writing it to the boot partition.

## Risks
The quoting behavior deliberately does not support escaping. An unmatched quote causes the rest of the string to be treated as quoted, which may hide later whitespace splits. `get_cmdline_value` returns the first matching prefix and does not detect duplicate `composefs=` values. It also does not dequote the returned value, which is acceptable for current composefs hash use but would matter if reused for more general parameters.

## Test signals
This file has no local tests. It is indirectly tested through `bootloader.rs` command-line adjustment tests and `write_boot.rs` UKI validation paths. Dedicated tests for quoted command lines, duplicate parameters, insecure parsing, invalid hash lengths, and unmatched quotes would strengthen coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/cmdline.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/lib.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-boot/src/lib.rs

## Purpose
This is the public crate root for composefs boot integration. It exposes bootloader discovery, command-line handling, os-release parsing, SELinux labeling, UKI parsing, and boot writing modules. It also defines the boot transformation trait used to prepare filesystem images for bootable composefs workflows.

## Important APIs, types, and functions
`BootOps<ObjectID>` is the key trait. `transform_for_boot(&mut self, repo)` extracts boot entries, empties required top-level directories, compacts the filesystem, applies SELinux labels, and returns extracted `BootEntry` values. `transform_for_boot_from_dir(&mut self, rootfs)` applies the same filesystem mutation using policy files read from an on-disk root directory and does not extract boot entries.

`REQUIRED_TOPLEVEL_TO_EMPTY_DIRS` lists `boot` and `sysroot`. `empty_toplevel_dirs` clears those directories and sets their mtimes to match `/usr`.

## Control flow
The `FileSystem<ObjectID>` implementation for `BootOps` first calls `get_boot_resources` before clearing `/boot`; this preserves boot resources that would otherwise be removed from the transformed root. It then calls `empty_toplevel_dirs`, `compact`, and `selabel::selabel`. The directory-backed variant skips discovery and repository reads, then applies the same empty/compact/relabel sequence using `selabel_from_dir`.

## State and persistence behavior
The trait mutates the in-memory `FileSystem`. It clears the contents of `/boot` and `/sysroot`, copies `/usr` mtime to those now-empty directories, compacts unreachable leaves, and rewrites SELinux xattrs across the tree. It returns extracted boot resources but does not itself commit images or write boot partition files.

## Dependencies and integration points
The module depends on composefs `FileSystem`, `Repository`, and fs-verity traits; `rustix::fd::AsFd` supports the on-disk SELinux path. It integrates with `bootloader::get_boot_resources` and `selabel`. It is used from `composefs-ctl` when creating bootable images from OCI images or on-disk roots.

## Risks
`empty_toplevel_dirs` assumes `/usr`, `/boot`, and `/sysroot` exist and returns errors if required directories are missing. The ordering is important: extracting boot resources after clearing `/boot` would lose them, while labeling before clearing could label content that is intentionally removed. The from-dir variant cannot return boot resources, so callers that need to write a boot partition must use the repository-backed path.

## Test signals
There are no direct tests in this file. Behavior is exercised indirectly by SELinux tests and by CLI bootable paths. Direct integration tests should assert `/boot` and `/sysroot` clearing, mtime propagation from `/usr`, leaf compaction after clearing, and preservation of returned boot entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/os_release.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-boot/src/os_release.rs

## Purpose
This module parses freedesktop-style `os-release` content and derives boot menu labels. It is used by UKI parsing to convert a `.osrel` PE section into a display label and can also support generated boot entries.

## Important APIs, types, and functions
`dequote` is a private parser for the quoting subset needed by `os-release`. It supports unquoted text, double quotes with simple backslash handling, single quotes, and adjacent quoted/unquoted fragments.

`OsReleaseInfo<'a>` stores a borrowed `HashMap<&str, &str>` of raw assignments. `parse(content)` filters comments and lines without `=`, then stores key/value slices. `get_value(keys)` returns the first dequoted value among a priority list. `get_pretty_name` prefers `PRETTY_NAME`, then `NAME`, then `ID`. `get_version` prefers `VERSION_ID`, then `VERSION`. `get_boot_label` combines the selected name and optional version.

## Control flow
Parsing is intentionally shallow: each non-comment assignment is split once on `=`, and values are dequoted lazily during lookup. If dequoting fails for a higher-priority key, lookup falls through to the next key. Boot-label generation requires a name-like field but treats version absence as non-fatal.

## State and persistence behavior
The parsed map borrows from the input string and holds no owned file content. Returned values are owned `String`s because dequoting may transform escapes and remove quotes. No filesystem state is read or written.

## Dependencies and integration points
The module only uses `std::collections::HashMap`. `uki.rs` calls `OsReleaseInfo::parse(...).get_boot_label()` after extracting a UKI `.osrel` section. It is therefore on the boot-menu label path for Type 2 entries.

## Risks
Duplicate keys are collapsed by `HashMap::from_iter`; later entries overwrite earlier ones based on iterator behavior. The parser does not trim assignment keys or values before storing, except inside `dequote`, so unusual whitespace around keys can affect lookup. It does not implement the full shell language, by design. Invalid quoting silently causes fallback to a lower-priority field rather than surfacing a parse warning.

## Test signals
Tests cover empty strings, single/double quotes, adjacent quote fragments, selected escape cases, malformed quotes returning `None`, and fallback order for boot labels when preferred fields are missing or malformed. Tests are table-driven and protect the intended partial-shell behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/os_release.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/selabel.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-boot/src/selabel.rs

## Purpose
This module applies target SELinux file labels to an in-memory composefs tree. It reads SELinux policy files from either the composefs repository or an on-disk root directory, builds a regex automaton for `file_contexts`, applies substitutions, and writes or removes the `security.selinux` xattr on directories and leaves.

## Important APIs, types, and functions
`XATTR_SECURITY_SELINUX` is the xattr key. `process_spec_file` parses `file_contexts`, `file_contexts.local`, and `file_contexts.homedirs` lines into regex patterns and context strings, including optional file-type filters. `process_subs_file` parses alias mappings from `.subs` files.

`Policy` owns substitution aliases, a lazy DFA, cache, and context list. `Policy::build_from` loads mandatory `file_contexts`, optional extension files, reverses rule order to preserve last-match semantics, and builds a `regex_automata` DFA. `lookup(path, ifmt)` matches path plus SELinux file-type code and returns the selected context unless it is `<<none>>`.

`open_file` reads policy files from composefs inline or external objects. `selabel(fs, repo)` reads policy from the image tree. `selabel_from_dir(fs, rootfs)` reads policy via `openat` from an on-disk root. `build_policy`, `apply_policy`, `strip_selinux_labels`, `relabel`, and `relabel_dir` implement the shared flow.

## Control flow
The public functions first locate `/etc/selinux/config`. If it is absent or lacks `SELINUXTYPE`, all existing SELinux labels are stripped and `false` is returned. If a policy exists, the code loads policy files under `<policy>/contexts/files`, builds the DFA, and recursively walks the filesystem from `/`. For each path it applies any substitution, determines the file-type code, looks up a label, and updates xattrs.

## State and persistence behavior
The module mutates the `FileSystem` in place. Directory stats are relabeled directly. Leaf stats are relabeled through the leaves table. To handle hardlinks, `relabel_dir` tracks labels already committed for each `LeafId`; if another path to the same leaf needs a different label, the leaf is cloned, the directory entry is remapped to the clone, and the new label is applied independently. If no policy is available, all `security.selinux` xattrs are removed.

## Dependencies and integration points
It depends on composefs tree, repository, and dumpfile/test helpers; `regex_automata` for matching; `rustix` for fd-relative policy reads; and `anyhow` plus `fn_error_context` for diagnostics. `lib.rs` calls it during boot transforms. The `composefs-ctl` bootable paths rely on it to ensure the generated root image has target labels, not build-host labels.

## Risks
SELinux regex compatibility is not full PCRE compatibility, so unusual distro policy expressions could mismatch. `process_spec_file` uses whitespace splitting, which may reject or misparse contexts with unexpected whitespace. DFA cache size is fixed at 10 MB. The hardlink-breaking behavior is necessary for correctness but changes deduplication and leaf identity. Substitutions are applied once at directory entry traversal, so subtle differences from libselinux behavior are possible.

## Test signals
Tests build synthetic filesystems with embedded policies and cover normal labeling, no-policy stripping, type-specific labels, `.subs` aliases, `<<none>>`, `.local` overrides, devices and FIFOs, stale label replacement, and hardlink splitting for paths requiring different labels. One test asserts no hardlinks remain in a bootable-layout scenario with cross-domain license-file hardlinks.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/selabel.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/uki.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-boot/src/uki.rs

## Purpose
This module parses the PE/EFI container structure used by Unified Kernel Images and extracts embedded text sections such as `.osrel` and `.cmdline`. It provides boot-label and command-line helpers for Type 2 BLS/UKI workflows.

## Important APIs, types, and functions
`DosStub`, `CoffFileHeader`, `PeHeader`, and `SectionHeader` are zerocopy representations of the PE structures needed for section lookup. `UkiError` distinguishes I/O failures, invalid PE data, missing sections, invalid UTF-8, and missing os-release name data.

`get_section(image, section_name)` parses an in-memory byte slice and returns a raw borrowed section. `get_section_buffered(reader, section_name)` performs the same lookup on a `Read + Seek` stream and returns owned bytes. `get_text_section` and `get_text_section_buffered` add UTF-8 validation. `get_boot_label` and `get_boot_label_buffered` extract `.osrel` and feed it to `OsReleaseInfo`. `get_cmdline` and `get_cmdline_buffered` extract `.cmdline`.

## Control flow
Section extraction constructs an 8-byte padded section-name key, reads the DOS stub to find the PE header offset, verifies the `PE\0\0` magic, skips the optional header, reads the declared section headers, and compares section names. In-memory parsing returns `None` for structurally invalid PE data and `Some(Err(MissingSection))` for valid PE files without the requested section. The public text helpers map invalid structure to `PortableExecutableError`.

## State and persistence behavior
The module does not persist data. Slice-based functions borrow from the input image. Buffered functions seek and read from the supplied stream, changing its cursor position. All parsed metadata is transient.

## Dependencies and integration points
It uses `zerocopy` little-endian wrappers for safe binary parsing and `thiserror` for public error reporting. `write_boot.rs` uses `get_cmdline` to validate that UKI `.cmdline` includes the expected composefs root hash. `get_boot_label` integrates with `os_release.rs` for display names. `bootloader.rs` discovers UKI files but leaves PE section parsing to this module.

## Risks
`section_name.len() > 8` will panic due to fixed PE section-name storage. Section extraction uses `virtual_size` rather than `size_of_raw_data`, which may be incorrect for malformed or unusual PE files. The in-memory API collapses several parse failures into `PortableExecutableError`, while buffered parsing reports some zerocopy failures as I/O errors. The code does not validate machine type, optional header contents, signatures, or UKI-specific required section sets beyond the requested section.

## Test signals
Tests synthesize PE-like byte arrays and cover successful boot-label extraction, buffered/slice parity, invalid PE data, missing `.osrel`, bad section offsets, raw and text extraction for `.osrel` and `.cmdline`, missing arbitrary sections, and invalid UTF-8. There is no test with a real UKI fixture.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/uki.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/write_boot.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-boot/src/write_boot.rs

## Purpose
This module writes extracted boot resources to a boot partition or directory. It handles BLS Type 1 entries, Type 2 UKIs, and generated Type 1 entries from `/usr/lib/modules` vmlinuz data, adding composefs command-line parameters where possible and validating existing UKI parameters where not.

## Important APIs, types, and functions
`write_t1_simple` writes a `Type1Entry` to `bootdir`, optionally under a boot subdirectory, adjusts its command line with the root image id, writes referenced files, and finally writes the loader entry under `loader/entries`.

`write_t2_simple` writes a `Type2Entry` under `EFI/Linux` after reading the UKI content, extracting `.cmdline`, parsing `composefs=`, and ensuring it matches the expected root id.

`write_boot_simple` is the public dispatcher. It accepts a `BootEntry`, expected `root_id`, insecure flag, boot partition path, optional boot subdirectory, optional entry id, and extra command-line arguments.

## Control flow
Type 1 entries may be relocated before writing if `entry_id` is supplied. Then `write_t1_simple` injects `composefs=<root_id>` or `composefs=?<root_id>`, writes all resource files before the `.conf`, creates missing parent directories, and writes a newline-terminated BLS file. Type 2 entries may be renamed, reject `cmdline_extra`, validate embedded `.cmdline`, and write the unchanged UKI. Module-vmlinuz entries are converted to Type 1 and follow the Type 1 path.

## State and persistence behavior
This module performs real filesystem writes using `create_dir_all` and `write`. It materializes kernel/initrd/EFI resources from repository objects and publishes BLS entries. It mutates local `Type1Entry` or `Type2Entry` values before writing but does not update the repository. Write ordering intentionally writes resource files before the loader entry.

## Dependencies and integration points
It depends on composefs repository file reading, bootloader types, `cmdline::get_cmdline_composefs`, and `uki::get_cmdline`. `composefs-ctl` calls `write_boot_simple` from the OCI `prepare-boot` path after transforming and committing a bootable image.

## Risks
Writes are not atomic and there is no rollback if a later resource or entry write fails. `write_t1_simple` unwraps `file_path.parent()` after constructing paths, which is expected for valid paths but is still an assumption. Type 2 writing creates `EFI/Linux` but not necessarily nested addon parent directories if `file_path` contains subdirectories. Existing boot files may be overwritten. UKIs cannot receive extra kernel args, so callers must seal the desired `.cmdline` before this step.

## Test signals
There are no local tests in this file. Important integration tests would cover Type 1 relocation with `boot_subdir`, resource-before-entry behavior, UKI hash mismatch rejection, missing `.cmdline`, extra-argument rejection for UKIs, nested addon output paths, and partial-write failure handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-boot/src/write_boot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ctl/Cargo.toml -->
# sources/cloud-native/composefs-rs/crates/composefs-ctl/Cargo.toml

## Purpose
This manifest defines the `composefs-ctl` crate, its library, and the `cfsctl` binary. The crate is the command-line control surface for composefs repositories and images and also hosts compatibility implementations of `mkcomposefs` and `composefs-info`.

## Important APIs, types, and functions
The manifest declares `src/lib.rs` as the library and `src/main.rs` as the `cfsctl` binary. Features gate optional functionality: `http` enables `composefs-http`; `oci` enables `composefs-oci` and its varlink integration; `containers-storage` adds native storage support through `composefs-storage`; `rhel9` and `pre-6.15` forward compatibility flags to `composefs`.

## Control flow
Cargo feature resolution controls which command variants and dependencies are compiled. The default feature set includes `pre-6.15`, `oci`, and `containers-storage`, so a normal build includes OCI workflows and compatibility behavior for older kernels unless the user disables defaults.

## State and persistence behavior
The manifest itself has no runtime state, but it selects dependencies that own persistent repository state, OCI storage, varlink service behavior, and boot integration. Optional dependencies keep non-default transports out of builds that do not request them.

## Dependencies and integration points
Core dependencies include `anyhow`, `clap`, `composefs`, `composefs-boot`, `env_logger`, `libsystemd`, `rustix`, `serde`, `serde_json`, `tokio`, and `zlink`. Optional dependencies connect to OCI, HTTP, and containers-storage paths. Workspace lints are applied through `[lints] workspace = true`.

## Risks
Defaulting to OCI and containers-storage increases build surface and platform assumptions. The `pre-6.15` default changes lower-level composefs behavior and should stay aligned with kernel support expectations. Feature combinations can hide code paths from CI if not tested explicitly, especially `http` without `oci`, no-default-feature builds, and RHEL-specific behavior.

## Test signals
The manifest has no direct tests. Build matrix coverage across default features, no default features, `http`, `oci`, `containers-storage`, `rhel9`, and `pre-6.15` is the relevant signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ctl/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ctl/src/composefs_info.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-ctl/src/composefs_info.rs

## Purpose
This module implements a Rust `composefs-info` compatibility tool for inspecting composefs EROFS images. It supports listing entries, dumping composefs dumpfile text, listing referenced object paths, finding missing objects in a base directory, and measuring fs-verity digests for files.

## Important APIs, types, and functions
`Cli` and `Command` define clap parsing for `ls`, `dump`, `objects`, `missing-objects`, and `measure-file`. `run` parses process args for standalone or argv0 dispatch. `run_from_args` supports hidden `cfsctl composefs-info` dispatch by prepending a synthetic program name.

`print_escaped` emits C-compatible escaped path bytes. `ls_print` recursively walks sorted filesystem entries, prints directories with trailing slash, prints symlink targets, and prints external object paths for first-seen regular leaves. `collect_objects_from_fs` collects unique external object IDs from the leaves table. `cmd_*` functions implement each subcommand, and `read_image` reads the entire EROFS image into memory before parsing.

## Control flow
Every image-oriented command reads each image into a byte vector, converts it with `erofs_to_filesystem::<Sha256HashValue>`, and then performs its inspection. `ls` recurses from root and applies root-level filters only at the first level. `dump` serializes the tree using `write_dumpfile`. `objects` sorts object IDs by hex. `missing-objects` unions object IDs across all images and filters by `basedir/<object path>`. `measure-file` bypasses image parsing and uses fs-verity measurement with fallback.

## State and persistence behavior
The module is read-only except for stdout/stderr output. It does not mutate repositories or images. It tracks in-memory `seen_leaf_ids` to suppress repeated object path output for hardlinks in `ls`.

## Dependencies and integration points
It depends on composefs EROFS reader, dumpfile writer, tree types, and fs-verity measurement. It is integrated into `cfsctl` through hidden subcommand forwarding and argv0 multi-call dispatch in `main.rs`.

## Risks
Images are read fully into memory, which is simple but can be expensive for very large metadata images. The code assumes SHA-256 images, so it is compatibility-oriented rather than dynamically matching repository hash metadata. `cmd_dump` accepts a filter argument but ignores it. Root-level filtering in `ls` may differ from users expecting recursive name filtering. Output compatibility depends on `print_escaped` matching the C tool exactly.

## Test signals
There are no local tests in this file. Useful coverage would compare output against C `composefs-info` fixtures for listing, dump output, object ordering, hardlinks, whiteouts, escaping, missing object detection, and kernel/fs fallback behavior in `measure-file`.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ctl/src/composefs_info.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ctl/src/lib.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-ctl/src/lib.rs

## Purpose
This is the main library for `cfsctl`. It re-exports composefs crates for downstream convenience, defines the primary CLI, resolves repository configuration, dispatches commands, integrates OCI/HTTP/varlink features, and provides helpers for reading filesystems, computing image IDs, committing images, mounting, garbage collection, boot preparation, and integrity checks.

## Important APIs, types, and functions
Public surface includes re-exports of `composefs`, `composefs_boot`, and optional `composefs_http`/`composefs_oci`; modules `composefs_info`, `mkcomposefs`, and `varlink`; `App`; `HashType`; `ErofsVersion`; `run_from_iter`; `run_if_socket_activated`; `run_app`; `open_repo`; and `default_repo_path`.

`App` defines global repository flags (`--repo`, `--user`, `--system`), hash and EROFS format overrides, verity behavior, upgrade controls, `--no-repo`, and all subcommands. `Command` includes repository lifecycle, image creation, compute/dump, mount, GC, fsck, varlink, compatibility tool forwarding, and optional HTTP/OCI commands. `OciCommand` covers layer import, image pull/list/inspect/tag/untag, mount, compute-id, prepare-boot, fsck, and varlink.

Core helpers include `resolve_repo_path`, `resolve_hash_type`, `run_init`, `open_repo_at`, `load_filesystem_from_ondisk_fs`, `dump_file_impl`, `run_cmd_without_repo`, and `run_cmd_with_repo`. Feature-gated helpers include `IndicatifReporter`, `OciReference`, `resolve_oci_image`, `resolve_oci_config`, and `load_filesystem_from_oci_image`.

## Control flow
`run_app` first handles hidden compatibility tool dispatch, then `init`, then varlink service modes, then no-repository compute/dump paths. For repository-backed commands it resolves the repo path, determines the effective hash algorithm from `meta.json` or old-format inference, opens the correctly typed repository, and dispatches into `run_cmd_with_repo`.

`run_cmd_without_repo` supports compute-id and create-dumpfile by reading an on-disk root and optionally applying boot transforms from a directory fd. `run_cmd_with_repo` wraps the repository in `Arc` and handles each command. OCI commands resolve refs or digests, call composefs-oci APIs, optionally generate boot images, and for `PrepareBoot` transform the rootfs, commit it, write boot resources, and create deployment state directories.

## State and persistence behavior
This file orchestrates persistent repository state. `run_init` creates or updates repo metadata, optionally resetting old metadata and recording default EROFS format. Image creation reads source files into repository objects and commits image refs. GC deletes unreachable objects unless dry-run. Mount commands affect the system mount namespace. Fsck reads and validates repository state. OCI commands create streams, images, refs, tags, and boot image links. `PrepareBoot` also writes boot partition files and creates `state/deploy/<image-id>/var`, `etc/upper`, and `etc/work`.

## Dependencies and integration points
It integrates almost every crate in the workspace: composefs repository, EROFS, filesystem reading, mount, fs-verity, boot transforms, OCI, HTTP, varlink, and progress reporting. It uses `clap` for CLI shape, `tokio` for async operations, `rustix` for fd and mount-related operations, `serde_json` for JSON output, `comfy-table` for image listing, and `indicatif` for progress bars.

## Risks
Dispatch complexity is high and feature-gated paths can diverge. Hash selection must happen before generic repository opening; mistakes can read a repo with the wrong `ObjectID`. No-repo compute-id defaults to SHA-512 when repo metadata cannot be resolved, which may surprise users. `Transaction` parks forever and relies on process lifetime. `PrepareBoot` writes boot state after choosing only the first boot entry. CLI behavior differs by enabled features, effective uid, systemd socket activation environment, and repository metadata age.

## Test signals
Local tests cover `IndicatifReporter` lifecycle behavior when OCI or HTTP features are enabled. Most command behavior is not tested here directly. Strong signals should come from integration tests for repo path/hash resolution, init idempotency, no-repo compute/dump, compatibility subcommand forwarding, varlink activation, bootable transforms, OCI ref resolution, prepare-boot side effects, mount option construction, GC, and fsck JSON/text behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ctl/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ctl/src/main.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-ctl/src/main.rs

## Purpose
This binary entry point implements `cfsctl` multi-call behavior. It dispatches directly to `mkcomposefs` or `composefs-info` when invoked under those names, supports `cfsctl mkcomposefs ...` and `cfsctl composefs-info ...`, initializes containers-storage helper mode when applicable, and otherwise starts the async `cfsctl` CLI.

## Important APIs, types, and functions
`binary_name` extracts `argv[0]` basename. `rest_of_args` returns arguments after the hidden tool token. `main` performs multi-call dispatch and creates the Tokio runtime for the primary CLI. `async_main` initializes logging, handles bare systemd socket activation through `run_if_socket_activated`, parses `App`, and calls `composefs_ctl::run_app`.

## Control flow
The first dispatch branch uses argv0 names `mkcomposefs` and `composefs-info`. The next branches inspect `argv[1]` to forward hidden subcommands before clap parsing. For normal `cfsctl`, containers-storage helper initialization runs before the Tokio runtime is created. The runtime then executes `async_main`, which checks socket activation before clap so a no-argument activated process can serve varlink.

## State and persistence behavior
This file owns no repository state, but it determines which subsystem receives process control. It initializes environment-based logging and may serve a long-lived varlink service. The containers-storage helper path can exit early if the process was spawned as a helper.

## Dependencies and integration points
It depends on `composefs_ctl` library APIs, `tokio` runtime construction, `env_logger`, `clap::Parser`, and optional `cstorage::init_if_helper`. It is the integration point for symlink/hardlink compatibility binaries and systemd socket activation behavior.

## Risks
`std::env::args_os().nth(1)` is called separately in match guards; this is fine because each call creates a fresh iterator, but it is easy to misread. Multi-call dispatch bypasses `env_logger::init` for direct `mkcomposefs` and `composefs-info`. Runtime creation happens after hidden tool dispatch, so those tools cannot use async code unless they create their own runtime. Socket activation must remain before clap for bare activation but after helper initialization for containers-storage semantics.

## Test signals
There are no local tests. Integration tests should cover argv0 dispatch, hidden subcommand forwarding including `--help`, normal CLI dispatch, containers-storage helper startup ordering, and no-argument socket activation.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ctl/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ctl/src/mkcomposefs.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-ctl/src/mkcomposefs.rs

## Purpose
This module implements a Rust `mkcomposefs` compatibility tool. It creates composefs EROFS images from source directories or composefs dumpfiles, optionally writes regular file content into a digest store, supports C-compatible format versions, and can print the fs-verity digest of the generated image.

## Important APIs, types, and functions
`Args` defines CLI flags for dumpfile input, digest printing, epoch mtimes, device and xattr filtering, min/max format version, digest store, hardlink behavior, thread count, source, and output image. `run` parses standalone args; `run_from_args` supports hidden `cfsctl mkcomposefs` dispatch.

`run_with_args` validates arguments, maps version flags to `FormatVersion`, opens an optional `FlatDigestStore`, reads input, applies transformations, builds an EROFS image with `mkfs_erofs_versioned`, writes it unless digest-only mode is selected, and prints digest if requested. `read_dumpfile`, `read_directory`, `write_image`, `compute_fsverity_digest`, `apply_transformations`, `set_all_mtimes_to_epoch`, and `remove_device_nodes` implement the steps.

## Control flow
Argument validation rejects digest-only with an image, missing image without digest-only, invalid version ranges, and unsupported `--min-version > 1`. Directory input opens a current-directory fd, creates a Tokio runtime based on `--threads`, optionally bounds verity work with a semaphore, and calls `read_filesystem_with_opts`. Dumpfile input reads from a file or stdin and parses text. Output to `-` refuses to write binary data to a terminal.

## State and persistence behavior
The module reads source directories or dumpfiles, may populate a digest store using the C-compatible `XX/DIGEST` layout, writes an image file or stdout, and prints digests. In-memory transformations can remove xattrs, keep only `user.*`, zero mtimes, remove block/character devices, and compact the filesystem after device removal.

## Dependencies and integration points
It depends on composefs dumpfile parsing, filesystem reading, object-store APIs, EROFS writer validation, fs-verity computation, and tree mutation. It is exposed through `main.rs` argv0 dispatch and hidden `cfsctl` forwarding. It uses `tokio` for async filesystem reading and `rustix` for fd-relative access.

## Risks
`--max-version` is validated only as a range input; actual selection is driven by `--min-version`, matching the current compatibility comments but potentially surprising. `--digest-store` is ignored with `--from-file` after warning. The generated image is fully materialized in memory before writing. `remove_device_nodes` recursively mutates directories and depends on a final `compact` to avoid orphan leaves. Without `--hardlinks`, host hardlinks are deliberately broken for C-compatible output.

## Test signals
There are no local tests in this file, though comments claim byte-for-byte compatibility is tested elsewhere. Important coverage includes C fixture comparisons for directory and dumpfile input, digest output modes, stdout terminal refusal, digest-store layout, hardlink behavior, xattr/device/mtime flags, version selection, thread counts, and stdin dumpfile parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ctl/src/mkcomposefs.rs -->
