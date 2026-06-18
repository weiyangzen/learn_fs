# Group Research: group_218_bcachefs_tools_sources_cow_pools_bcachefs_tools_github_dependabot_ym_5757e8a143a8

Scope verified against `Docs/research_subset_a.md`: `sources/cow-pools/bcachefs-tools` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/.github/dependabot.yml -->
# File Research: sources/cow-pools/bcachefs-tools/.github/dependabot.yml

This is a minimal Dependabot configuration for GitHub Actions dependency updates. It uses Dependabot config version 2, watches the repository root, and schedules weekly update checks for workflow action versions.

Integration role: keeps `.github/workflows/*` action pins current. It does not cover Rust crates, Nix inputs, Debian dependencies, or other package ecosystems.

Risk/maintenance notes: the scope is intentionally narrow; workflow action drift is automated, but Cargo/Nix updates are handled elsewhere.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/.github/dependabot.yml -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/.github/workflows/nix-flake-update.yml -->
# File Research: sources/cow-pools/bcachefs-tools/.github/workflows/nix-flake-update.yml

This workflow updates `flake.lock`. It runs manually, monthly on the first day at midnight UTC, and on pushes that change `flake.nix`.

The single `lockfile` job checks out the repo, installs Nix via `cachix/install-nix-action@v27`, passes the GitHub token to Nix as an access token, and invokes `DeterminateSystems/update-flake-lock@v21`.

Integration role: complements Dependabot by refreshing Nix flake inputs. It is lockfile maintenance only and does not build or test the flake.

Risk/maintenance notes: action versions differ from the main Nix workflow, which uses `install-nix-action@v30`; that may be intentional but is a version-skew point.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/.github/workflows/nix-flake-update.yml -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/.github/workflows/nix-flake.yml -->
# File Research: sources/cow-pools/bcachefs-tools/.github/workflows/nix-flake.yml

This workflow validates Nix flake build outputs on pushes and pull requests. It first evaluates `.#githubActions.matrix` with `nix eval --json`, exports that JSON as a job output, then runs a matrix of `nix build -L '.#${{ matrix.attr }}'`.

Integration role: delegates build matrix definition to the flake itself, so CI targets live in Nix code rather than duplicated GitHub YAML.

Risk/maintenance notes: if the flake matrix evaluation fails, no build jobs can fan out. The workflow assumes the flake exposes `githubActions.matrix` with fields `name`, `system`, `os`, and `attr`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/.github/workflows/nix-flake.yml -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/.github/workflows/obs.yml -->
# File Research: sources/cow-pools/bcachefs-tools/.github/workflows/obs.yml

This is a reusable `workflow_call` workflow for publishing Debian source artifacts into an OBS-style Git repository. Inputs identify the source artifact, runner, architecture, and distribution metadata; secrets provide GPG keys and snapshot/release repository URLs.

The workflow builds a controlled environment by mounting the workspace on tmpfs, installing Podman, starting a privileged Debian `trixie` container, and installing base packaging/signing tools. For non-PR events it imports GPG subkeys, exports apt keyrings, configures SSH support through `gpg-agent`, and uses the selected OBS repository URL based on whether the event is a tag release or snapshot.

The artifact path is verified through GitHub artifact attestations on non-PR events, unpacked from `artifact-src.tar`, and checked for GPG signatures when signing is available. It then clones the OBS repo, removes existing tracked state, copies `.dsc`, `.tar.xz`, and `.tar.xz.sig` inputs, extracts RPM/Debian packaging files from the tarball, patches the spec version, adds rpmlint filters, signs unsigned tracked payloads, emits an OBS `_service` file with SHA-256 `verify_file` entries, signs that service file, creates an attestation checksum manifest, attests provenance, commits, and pushes.

Integration role: release/snapshot publication pipeline from GitHub-produced source artifacts to OBS package repository state, with provenance, GPG, Git LFS, and per-file checksum services.

Risk/maintenance notes: the job is highly privileged inside Podman and depends on several secrets. Most steps have one-minute timeouts, so slow package mirrors, large repositories, or GPG startup delays can fail the workflow. The “Attest” step is not gated off for pull requests in the current YAML comment state, although earlier verification/signing steps are gated.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/.github/workflows/obs.yml -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/Cargo.toml -->
# File Research: sources/cow-pools/bcachefs-tools/Cargo.toml

This is the Rust workspace and primary `bcachefs-tools` package manifest. The workspace contains the root crate, `bch_bindgen`, and `doc/docgen`, with the root crate and bindgen crate as default members.

The package builds the `bcachefs` binary from `src/bcachefs.rs`, targets Rust 1.85.0 and edition 2021, and defaults to the optional `fuse` feature. Dependencies cover CLI parsing/completion, logging, serde/JSON, fiemap, udev, UUIDs, errno, C/Rust bindings through `bch_bindgen`, terminal UI, HTTP, demangling, time, zeroization, and optional `fuser`.

Release profile keeps debug info and sets `panic = "abort"` so C/Rust faults cannot be hidden by unwinding across libbcachefs boundaries. Vendor filtering is limited to Linux platforms.

Integration role: root Rust entrypoint that links to the C/static lib build through `build.rs` and to generated C bindings through `bch_bindgen`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/Cargo.toml -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/Makefile -->
# File Research: sources/cow-pools/bcachefs-tools/Makefile

This is the top-level build/install orchestrator for the mixed Rust/C bcachefs tools and DKMS module. It locks `VERSION` once at make startup from Git, `.version`, or Cargo metadata so DKMS paths, generated headers, and install steps do not diverge if `HEAD` changes mid-recipe.

The file configures C flags for userspace libbcachefs compilation, pkg-config dependencies, Rust toolchain/profile settings, generated systemd units, initramfs hooks, Cargo builds, C object compilation, `libbcachefs.a`, version files, DKMS config generation, installation, uninstall, DKMS reload, Debian/RPM packaging, docs, MSRV lockfile refresh, vendored kernel source updates, and source tarball creation.

Important targets include `all`, `debug`, `install`, `install_dkms`, `dkms-reload`, `clean`, `deb`, `rpm`, `docgen`, `cargo-update-msrv`, and `tarball`. Debug mode persists build variables into `build.vars` and forwards selected debug/test flags into DKMS builds. Install creates symlinks for `mkfs.bcachefs`, `fsck.bcachefs`, `mount.bcachefs`, and FUSE variants, plus bash completion when the built binary can run on the host.

Integration role: central bridge between Cargo, C compilation, systemd, initramfs, udev, DKMS, packaging, and release artifacts.

Risk/maintenance notes: pkg-config is skipped for some targets but required for most builds; cross compilation skips completion generation. DKMS parallelism is memory-budgeted at 512 MB per job to avoid OOMs. The source tarball depends on `.gitcensus`, which is generated only when `.git` exists.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/arch/etc/initcpio/hooks/bcachefs -->
# File Research: sources/cow-pools/bcachefs-tools/arch/etc/initcpio/hooks/bcachefs

This mkinitcpio runtime hook tries to unlock an encrypted bcachefs root device during early boot. `run_hook` resolves `$root`, probes `bcachefs unlock -c` quietly, and if unlocking is needed either prompts via Plymouth or runs `bcachefs unlock` directly.

Integration role: Arch initramfs boot support for encrypted bcachefs root filesystems.

Risk/maintenance notes: it depends on mkinitcpio’s `resolve_device`, `$root`, optional Plymouth runtime state, and the `bcachefs` binary being present in the image.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/arch/etc/initcpio/hooks/bcachefs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/arch/etc/initcpio/install/bcachefs -->
# File Research: sources/cow-pools/bcachefs-tools/arch/etc/initcpio/install/bcachefs

This mkinitcpio install hook adds the `bcachefs` kernel module, the `bcachefs` userspace binary, and the runtime hook script to the initramfs image.

Integration role: pairs with `arch/etc/initcpio/hooks/bcachefs` so encrypted root devices can be unlocked at boot.

Risk/maintenance notes: it assumes the module and binary names are both `bcachefs`. Help text documents Plymouth as optional.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/arch/etc/initcpio/install/bcachefs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/arch/etc/mkinitcpio.conf -->
# File Research: sources/cow-pools/bcachefs-tools/arch/etc/mkinitcpio.conf

This is an example/default mkinitcpio configuration tailored for bcachefs root boot. It includes `bcachefs` in `MODULES`, includes the `bcachefs` binary, leaves `FILES` empty, and sets `HOOKS=(base udev autodetect modconf block filesystems bcachefs keyboard fsck)`.

Integration role: Arch packaging/example configuration for generating an initramfs with bcachefs module, binary, filesystem support, unlock hook, keyboard, and fsck.

Risk/maintenance notes: ordering matters: `bcachefs` appears after `filesystems` and before `keyboard fsck`. Users with encrypted passphrases may need keyboard earlier depending on boot environment; this file follows mkinitcpio conventions but is not dynamically generated.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/arch/etc/mkinitcpio.conf -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bcachefs-wait-devices@.service.in -->
# File Research: sources/cow-pools/bcachefs-tools/bcachefs-wait-devices@.service.in

This is a systemd template unit generated by the Makefile into `bcachefs-wait-devices@.service`. It is a oneshot service with `RemainAfterExit=true` and runs `@sbindir@/bcachefs wait-devices UUID=%i`.

Integration role: systemd integration for waiting until every device in a multi-device bcachefs filesystem UUID is present.

Risk/maintenance notes: `@sbindir@` is substituted at build time from Makefile install paths. The unit has no explicit ordering dependencies in this template.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bcachefs-wait-devices@.service.in -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/Cargo.toml -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/Cargo.toml

This manifest defines the `bch_bindgen` library crate, edition 2021, Rust 1.85.0. It depends on `anyhow`, `uuid`, `bitfield`, `bitflags`, `fiemap`, `libc`, and `paste`; build dependencies are `pkg-config`, `bindgen`, and `cc`.

Integration role: Rust-side binding crate for libbcachefs, generated C headers, and helper wrappers used by the top-level tools.

Risk/maintenance notes: bindgen version and generated layout behavior are central to ABI correctness; the build script carries target-layout fixes for this reason.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/Cargo.toml -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/build.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/build.rs

This build script generates Rust bindings and companion Rust source from bcachefs C headers. It parses C x-macros from kernel-style headers, generates typed bkey dispatch enums, superblock field marker trait impls, string tables, persistent counter metadata, and extent-entry size lookup code.

The main bindgen builder reads `src/libbcachefs_wrapper.h`, passes target triple and include paths, probes `liburcu`, configures many allowlists/blocklists, makes selected enums rustified or newtyped, marks complex C types opaque or non-copy, wraps static inline functions into generated C, and writes patched bindings to `OUT_DIR/bcachefs.rs`. It compiles bindgen’s generated `extern.c` wrapper with `cc` as `bcachefs_static_wrappers`.

The script also emits Debian `dh-cargo:deb-built-using` metadata, generates Rust files from `bcachefs_format.h`, `members_format.h`, `counters_format.h`, and `extents_format.h`, and separately bindgens keyutils from `src/keyutils_wrapper.h`.

A major function, `packed_and_align_fix`, post-processes generated Rust to replace problematic `repr(C, packed(8))` cases with `repr(C, align(8))`, and on 32-bit targets adds alignment for bkey-containing structures.

Integration role: foundation of the Rust/C ABI. Most `bch_bindgen::c::*` types and helper dispatch modules depend on its generated output.

Risk/maintenance notes: fragile by nature because it depends on exact header names, x-macro shapes, bindgen output strings, target layout, and static inline wrapper generation. The script contains explicit workarounds for bindgen issue 753, flexible-array/union layout, static inline functions, and 32-bit alignment.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/build.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/accounting.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/accounting.rs

This module provides typed Rust handling for bcachefs disk accounting positions and counters. It re-exports key accounting-related C enums and safely converts raw `u8` values into bindgen enum values with sentinel fallback.

`DiskAccountingPos` wraps `bpos` as the on-disk accounting key encoding. `DiskAccountingKind` decodes/encodes known accounting key variants such as inode count, persistent reservation, replicas, device data type, compression, snapshot, btree, rebalance work, inode number, reconcile work, and device leaving. Encoding and decoding use a 20-byte reversed bpos representation matching the C `memcpy_swab` convention. A compile-time assertion requires `BCH_DISK_ACCOUNTING_TYPE_NR == 11`.

The module also defines `AccountingEntry`, helpers for empty/hidden data types, print helpers that route to C printbuf functions, btree ID string formatting, and member state string lookup.

Integration role: supports Rust commands that inspect or present accounting btree data and in-memory accounting counters.

Risk/maintenance notes: the compile-time accounting type count intentionally breaks builds when C accounting variants change, forcing Rust decode coverage updates. Endianness and byte order assumptions are core correctness points.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/accounting.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/bcachefs.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/bcachefs.rs

This module includes generated `OUT_DIR/bcachefs.rs` and layers Rust helpers on top of bindgen types. It suppresses naming/style lints expected from C bindings.

It defines bitfield wrappers for scrypt and crypt flags, adds methods on `bch_sb_field_crypt`, implements partial equality for selected `bch_sb` identity/version fields, and adds convenience methods to `bch_sb` for field lookup, crypt field access, UUID conversion, device count, and encryption nonce derivation.

For `bch_sb_handle`, it adds pointer dereference helpers, typed superblock field access/mutation/resizing, member access, and a `Drop` implementation that calls `bch2_free_super`. It also adds deferred option-string helpers for `bch_opt_strs`.

Integration role: ergonomic layer above raw generated bindings for superblock and option handling.

Risk/maintenance notes: many methods dereference raw C pointers and rely on C ownership rules. `bch_sb_handle::Drop` makes ownership significant; borrowed handles must avoid accidental dropping.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/bcachefs.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/bitmask.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/bitmask.rs

This module reimplements little-endian 64-bit bitmask getter/setter logic in Rust. `le64_bitmask_get` and `le64_bitmask_set` operate on `c::__le64` using exported offset and width constants.

The `bitmask_accessors!` macro generates typed getter/setter methods for C structs and fields, supporting both array fields such as `flags[1]` and plain fields such as `bch_member.flags`.

Integration role: replaces C static-inline `LE64_BITMASK` accessors that bindgen cannot expose directly. It is used by the superblock module to add methods on `bch_sb` and `bch_member`.

Risk/maintenance notes: correctness depends on generated constant names following `{NAME}_OFFSET` and `{NAME}_BITS`. The mask expression assumes valid nonzero bit widths from C definitions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/bitmask.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/bkey.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/bkey.rs

This module wraps bcachefs keys and positions. `BkeySC` holds split const key/value references plus phantom iterator lifetime, and generated code from `bkey_types_gen.rs` provides typed bkey value dispatch.

`BkeySC::to_text` formats a key/value through C `bch2_bkey_val_to_text`, and `BkeySC::v` returns generated typed value enum dispatch. The module implements position comparison helpers for full `bpos` ordering and key-only ordering that ignores snapshot, plus min/max helpers and `bkey_start_pos`.

Integration role: core Rust-side btree key representation used by btree iterators, extent handling, dumps, and formatting.

Risk/maintenance notes: conversion from raw `bkey_s_c` pointers is unsafe and depends on iterator lifetime discipline. Snapshot-aware and snapshot-agnostic comparison helpers must be used in the right context.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/bkey.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/btree/mod.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/btree/mod.rs

This module provides Rust wrappers for bcachefs btree transactions, key iterators, node iterators, commit/restart loops, and node formatting. `BtreeTrans` owns a C `btree_trans` pointer from `__bch2_trans_get`, exposes `begin`, restart verification, raw pointer access, and commit, and drops by resetting restart state before `bch2_trans_put`.

`BtreeIterFlags` mirrors C iterator flags through `bitflags`. `lockrestart_do`, `commit_do`, `trans_commit_do`, and `trans_run` model C transaction retry macros in Rust, retrying on `BCH_ERR_transaction_restart`.

`BtreeIter` initializes key iterators, peeks forward/backward, supports slot-aware max peeking, iterates with restart handling, advances, and exits on drop. `BtreeNodeIter` similarly iterates btree nodes and advances explicitly via node max key successor to avoid skipping journal-overlay nodes. `c::btree` gains formatting and key iteration helpers.

Integration role: primary safe-ish Rust interface for reading and mutating bcachefs btrees from CLI/tooling code.

Risk/maintenance notes: lifetimes are used to tie keys to iterators, but raw pointers still dominate. The restart-loop logic is critical; skipping `verify_not_restarted` or advancing incorrectly could produce stale reads or missed nodes.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/btree/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/extents.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/extents.rs

This module iterates extent entries and extent pointers inside typed bkeys. It includes generated `extent_entry_type_u64s()` from the build script, decodes extent entry type from bit-position encoding, computes value-end pointers from `bkey.u64s`, and maps only key types with extent-like payloads.

`ExtentEntryIter` walks variable-sized extent entries while checking bounds. `ExtentPtrIter` filters entries down to `BCH_EXTENT_ENTRY_ptr`. Convenience functions operate on either generated typed `BkeyValSC` or raw `bkey_i`.

Integration role: used by Rust tooling that needs to inspect data extent mappings and device pointers.

Risk/maintenance notes: pointer arithmetic assumes valid bkey layout and generated entry sizes. If new extent-bearing bkey types are added, `bkey_ptrs_raw` may need updates.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/extents.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/io.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/io.rs

This module exposes read and write operations as Rust `Future`s backed by C shims. It defines a 1 MiB maximum IO size, page-derived bvec count, FFI declarations for `rust_write_submit` and `rust_read_submit`, and heap-pinned state structs for write and read operations.

`WriteOp` submits IO at construction, stores submit-time errors, wakes through `write_endio`, and resolves to `WriteResult { sectors_delta }` or `BchError`. `ReadOp` submits reads with inode options and resolves when the C bio endio callback stores completion. Both use `AtomicBool` and `UnsafeCell<Option<Waker>>`, with a recheck after waker installation to avoid missed wakeups. A small `block_on` loop uses a noop waker and `thread::yield_now`.

Integration role: Rust async abstraction over libbcachefs data IO for FUSE and migration/tool commands.

Risk/maintenance notes: buffers passed to C must outlive the future. The C header says data must be block-aligned and <= 1 MiB, but Rust constructors do not enforce all alignment/size constraints locally. The simple executor spins/yields rather than integrating with a full runtime.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/io.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/mod.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/mod.rs

This module is a namespace aggregator for data-related helpers. It exports `extents`, `io`, and `moving`.

Integration role: lets callers import `bch_bindgen::data::*` submodules coherently.

Risk/maintenance notes: no direct behavior; changes are limited to module surface organization.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/moving.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/moving.rs

This module wraps C `moving_context` in a pinned, heap-allocated Rust RAII type. `MovingContext::new` zeroes and initializes the context with `bch2_moving_ctxt_init`, while `Drop` calls `bch2_moving_ctxt_exit`.

The wrapper is pinned because the C struct contains embedded `list_head` fields that become self-referential after initialization. `move_data_btree` exposes `bch2_move_data_btree` with a caller-provided C predicate and argument pointer.

Integration role: supports Rust commands that move/rebalance/copy data through bcachefs’s C moving infrastructure.

Risk/maintenance notes: `move_data_btree` is unsafe because predicate arguments must remain valid and match C expectations. Moving the raw context after initialization would be invalid, hence pinning is load-bearing.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/moving.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/errcode.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/errcode.rs

This module wraps bcachefs and errno-style errors in `BchError`, storing positive raw codes rather than constructing invalid bindgen enum discriminants. It provides message formatting through `bch2_err_str`, class matching via `__bch2_err_matches`, errno-class mapping through `__bch2_err_class`, and standard `Display`, `Debug`, and `Error` impls.

It also converts C negative return codes and ERR_PTR-style pointers into Rust `Result`s with `ret_to_result`, `errptr_to_result`, and `errptr_to_result_c`.

Integration role: common error bridge for all Rust wrappers around C APIs.

Risk/maintenance notes: the ERR_PTR detection casts through pointer-sized integers and assumes Linux-style `-4095..-1` encoded pointers. Return conversion only treats negative values greater than `-4096` as errors.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/errcode.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/fs.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/fs.rs

This module is the main Rust wrapper around `struct bch_fs`. `Fs` owns a raw `bch_fs` pointer and drops by calling `bch2_fs_exit`; `borrow_raw` returns `ManuallyDrop<Fs>` for non-owning views. It exposes superblock handle access, superblock locking, opening devices with `bch2_fs_open`, explicit `exit`, filesystem start/recovery, read-only transition, device add, device reference handling, accounting reads, btree root access, journal flushing, range deletion, inode lookup, time conversion, and read/write operation creation.

It defines `DevRef`, an RAII guard for referenced devices, and `SbLockGuard`, an RAII guard around `bch_fs::sb_lock`. It also adds standalone helpers for bucket-to-sector, bucket byte size, hashed writepoints, device target IDs, and allocator btree classification.

Integration role: central API used by Rust CLI commands to open, inspect, mutate, read, and write bcachefs filesystems through libbcachefs.

Risk/maintenance notes: many methods expose interior mutability via raw C pointers and rely on external locks documented in comments. `Drop` ownership is important; raw borrowed filesystem pointers must use `borrow_raw` or risk double exit.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/fs.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/journal/mod.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/journal/mod.rs

This module provides Rust iterators and helpers for bcachefs journal sets. It implements pointer arithmetic for variable-sized `jset_entry` and `bkey_i` records, computes jset byte and sector sizes, reads the `JSET_NO_FLUSH` flag, iterates entries within a `jset`, iterates keys within an entry, converts entry type and btree ID bytes into enums, and extracts/compares log entry messages.

Integration role: supports dump/recovery/inspection tooling that needs to walk journal replay records without relying on C macros.

Risk/maintenance notes: offsets such as 56-byte `jset` header and 8-byte `jset_entry` header are hard-coded from C layout. Layout changes require updates here.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/journal/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/keyutils.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/keyutils.rs

This module includes bindgen-generated keyutils bindings from `OUT_DIR/keyutils.rs` and suppresses C-style naming/unused warnings.

Integration role: Rust access to Linux keyring/keyutils symbols used by encryption unlock/key management paths.

Risk/maintenance notes: all behavior is generated at build time from `keyutils_wrapper.h` and system headers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/keyutils.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/keyutils_wrapper.h -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/keyutils_wrapper.h

This wrapper header includes `<keyutils.h>` for bindgen.

Integration role: minimal C header input for generating Rust keyutils bindings.

Risk/maintenance notes: generated output depends on the target system’s keyutils development headers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/keyutils_wrapper.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/lib.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/lib.rs

This is the root of the `bch_bindgen` crate. It declares modules for accounting, raw bindings, bitmasks, bkeys, btrees, data, errors, filesystem, journal, keyutils, options, printbuf, and superblocks, and re-exports `paste`.

It defines `c` as a namespace alias to generated bcachefs bindings, const constructors and sentinels for `bpos`, ordering implementations for `bpos` and `bbpos`, raw-to-enum helpers for `btree_id`, display formatting through C string tables, path-to-C-string conversion, parse errors, parsing for btree IDs, `bbpos`, `BbposRange`, bkey types, and `bpos` strings including sentinel tokens.

It also adds `printbuf::new`, `Drop` for generated `printbuf`, and `printbuf_to_formatter` for routing C print functions into Rust `fmt`.

Integration role: public facade and shared utility layer for the generated binding crate.

Risk/maintenance notes: `Drop` on `c::printbuf` assumes all constructed printbufs follow heap allocation semantics. String parsing depends on C `match_string` tables and sentinel text matching.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/lib.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/libbcachefs_wrapper.h -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/libbcachefs_wrapper.h

This is the main bindgen input header for bcachefs tools. It includes filesystem format/options/error headers, btree/cache/iter headers, data checksum/IO/move/update headers, debug/init/fsck/inode/dirent/xattr/allocation/journal/superblock/RAID headers, tool utility headers, Rust shim headers, Linux bio/blkdev headers, and FUSE shim declarations.

It also defines `MARK_FIX_753`, a workaround for bindgen macro constant generation, and emits constants for `BLK_OPEN_READ`, `BLK_OPEN_WRITE`, `BLK_OPEN_EXCL`, and `BLK_OPEN_CREAT` under temporary `Fix753_` names that the build script strips.

Integration role: umbrella C ABI surface consumed by `bch_bindgen/build.rs`.

Risk/maintenance notes: adding or removing included headers changes the generated Rust API and compile dependencies. The workaround constants depend on build-script parse callbacks.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/libbcachefs_wrapper.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/opts.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/opts.rs

This module wraps bcachefs option table access and option parsing. It turns bindgen’s zero-length `bch2_opt_table` into a slice using `bch2_opts_nr`, provides macros for option set/get/defined operations, safely converts table indexes to `bch_opt_id`, reads default values, sets options by ID or into a superblock, and exposes safe string accessors for option name, hint, help, and choices.

`parse_mount_opts` calls C `bch2_parse_mount_opts` with optional filesystem context, option string, and unknown-option policy. `parse_mount_opts_vec` joins Rust strings with commas before parsing.

Integration role: shared option infrastructure for format, mount, device, and CLI commands.

Risk/maintenance notes: `opt_id` panics on out-of-range indexes, making caller validation important. Option strings are converted with `CString::new`, so embedded NUL bytes panic.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/opts.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/printbuf.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/printbuf.rs

This module wraps C `printbuf` in a Rust `Printbuf` type that implements `fmt::Write` through `bch2_prt_bytes_indented`. It provides string access, tabstop management, indentation RAII, tab/right-justify/newline helpers, automatic tabular alignment, unit/human-readable formatting, metadata version printing, superblock printing, bitflag printing, and raw printbuf access for C functions.

`PrintbufIndent` removes indentation on drop and dereferences to `Printbuf`, enabling scoped formatting.

Integration role: common formatting buffer for Rust commands while preserving bcachefs’s C printbuf behavior and alignment semantics.

Risk/maintenance notes: `as_str` assumes `printbuf.buf` points to NUL-terminated UTF-8-ish data. Many methods call raw C print functions and depend on `c::printbuf::new`/Drop behavior from the crate root.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/printbuf.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/sb/io.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/sb/io.rs

This module wraps superblock read operations. `read_super_opts` and `read_super` call C `bch2_read_super` and return an owned `bch_sb_handle`; `read_super_silent` calls `bch2_read_super_silent` and returns `BchError` directly.

Integration role: Rust interface for reading on-disk superblocks during inspection, unlock, format, and metadata commands.

Risk/maintenance notes: error sign handling differs between call sites: `read_super_opts` wraps `BchError::from_raw(ret)`, while silent mode also uses `ret` directly. Correctness depends on the C functions’ return sign convention.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/sb/io.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/sb/mod.rs -->
# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/sb/mod.rs

This module provides typed superblock field and member access. It includes generated `SbField` impls from `BCH_SB_FIELDS`, member state names from `BCH_MEMBER_STATES`, and persistent counter info from `BCH_PERSISTENT_COUNTERS`.

It defines typed `sb_field_get`, mutable `sb_field_get_mut`, `sb_field_resize`, and `sb_field_get_minsize`. The mutable APIs take `&mut bch_sb_handle` so Rust borrowing prevents stale field references across resize operations.

For device members, it provides bounds-checked `MembersV2`, `MembersV2Mut`, and `MembersV1` readers/writers that handle variable `member_bytes` and v1 fixed 56-byte entries by copying into zeroed `bch_member` structs. It also generates pure-Rust LE64 bitmask accessors for many `bch_sb.flags[]` and `bch_member.flags` fields.

Integration role: central Rust API for inspecting and modifying superblock metadata and device member state.

Risk/maintenance notes: mutable member access can return references into entries smaller than full `bch_member`; callers are warned to write only fields fitting in `member_bytes`. Generated field trait coverage must track C superblock field changes.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/bch_bindgen/src/sb/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/build.rs -->
# File Research: sources/cow-pools/bcachefs-tools/build.rs

This top-level Rust build script links the root binary crate against the locally built static `libbcachefs.a` and required system libraries: urcu, zstd, blkid, uuid, sodium, zlib, lz4, udev, keyutils, aio, and unwind.

It emits `-rdynamic` for binaries so tools-side symbol lookup/backtrace formatting can resolve static symbols through `dladdr`. It also documents that the `fuser` crate talks directly to `/dev/fuse`, so no libfuse3 link is required.

Integration role: Cargo link bridge to the Makefile-produced C archive and external C libraries.

Risk/maintenance notes: Cargo builds require `libbcachefs.a` to exist in the repository root build directory. Library list must stay synchronized with C object dependencies.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/build.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/config.h -->
# File Research: sources/cow-pools/bcachefs-tools/c_src/config.h

This file is empty.

Integration role: placeholder/config header included by some C compatibility code paths.

Risk/maintenance notes: because it defines no feature macros, included code must obtain required configuration from compiler flags or other headers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/config.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/crypto.c -->
# File Research: sources/cow-pools/bcachefs-tools/c_src/crypto.c

This file implements userspace encryption helper functions for bcachefs tools. `read_passphrase` reads from stdin with terminal echo disabled when stdin is a TTY. `derive_passphrase` derives a `bch_key` using libsodium’s scrypt implementation and parameters from the superblock crypt field.

The file checks whether a superblock is encrypted, verifies a passphrase by decrypting the stored encrypted key and checking its magic, adds derived passphrase keys to Linux keyrings, initializes a new encrypted superblock key with random bytes, and updates or removes passphrase encryption around a filesystem key.

Integration role: supports encrypted filesystem format, unlock, passphrase update, and keyring operations.

Risk/maintenance notes: error handling is fatal through `die` in many paths. Sensitive data is explicitly zeroed for passphrase key, description, and temporary superblock key in some flows, but the returned passphrase buffer from `read_passphrase` must be handled carefully by callers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/crypto.h -->
# File Research: sources/cow-pools/bcachefs-tools/c_src/crypto.h

This header declares bcachefs tools encryption helpers for passphrase reading, key derivation, encrypted superblock detection, passphrase checking, keyring insertion, crypt field initialization, and passphrase updates.

Integration role: exposes `crypto.c` to C tools, bindgen wrapper headers, and Rust FFI.

Risk/maintenance notes: declarations rely on forward-declared bcachefs structs plus `tools-util.h`; callers must include full definitions where field access is needed.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/crypto.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/fuse_shims.c -->
# File Research: sources/cow-pools/bcachefs-tools/c_src/fuse_shims.c

This file provides C shims for the Rust FUSE mount command when `BCACHEFS_FUSE` is enabled. It wraps libbcachefs operations that require C macros, inline functions, `qstr`, transaction closures, or other types awkward for bindgen.

It initializes per-thread userspace kernel context for fuser worker threads, registers/unregisters RCU/percpu state, wraps time/block/nlink inline helpers, and implements FUSE operations for lookup, create, unlink, rename, link, setattr, post-write inode timestamp updates, readdir, statfs usage, and inode counting.

Integration role: bridge between Rust FUSE code and bcachefs C filesystem operations.

Risk/maintenance notes: `rust_fuse_ensure_current` allocates a fake `task_struct` for worker threads if `current` is absent. Rename has an explicit `XXX handle overwrites` comment. The file is compiled only with FUSE support enabled.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/fuse_shims.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/fuse_shims.h -->
# File Research: sources/cow-pools/bcachefs-tools/c_src/fuse_shims.h

This header declares the FUSE C shim API used by Rust. It includes core bcachefs, inode, and bucket headers, documents why shims are needed, and exposes thread initialization, inline wrappers, filesystem operation wrappers, readdir callback type, usage reading, and inode counting.

Integration role: bindgen-visible API for Rust FUSE mount support.

Risk/maintenance notes: function signatures mirror C layout types such as `subvol_inum`, `bch_inode_unpacked`, and `timespec64`; ABI changes in those types affect Rust callers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/fuse_shims.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/ida.c -->
# File Research: sources/cow-pools/bcachefs-tools/c_src/ida.c

This file implements a userspace ID allocator for bcachefs-tools. It replaces kernel xarray-backed IDA behavior with a flat d-ary bitmap tree in Eytzinger layout, where each node is a machine word and set bits indicate subtrees or leaf IDs with free capacity.

It supports initialization, destruction, growth by adding a tree level, range-limited allocation, batch allocation, free, and finding the first allocated ID. Internal helpers compute node counts, capacity, first leaf index, bit spans, overlapping bit ranges, and recursive descent. Debug builds can verify parent/child “has free” invariants.

Integration role: userspace compatibility implementation for code that expects Linux IDA-style allocation.

Risk/maintenance notes: growth math guards against shift overflow and saturates capacity. Double-free and invariant failures use `BUG_ON`, making allocator misuse fatal. The allocator does not implement pointer mapping, only ID allocation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/ida.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/libbcachefs.c -->
# File Research: sources/cow-pools/bcachefs-tools/c_src/libbcachefs.c

This file implements small libbcachefs tool helpers around option strings. `bch2_opt_strs_free` frees every duplicated option string in a `bch_opt_strs`. `bch2_parse_opts` parses populated option strings through `bch2_opt_parse`, tolerates options needing an open filesystem, sets parsed values by option ID, and returns a `bch_opts` struct.

Integration role: C-side helper used by Rust deferred option parsing and command option handling.

Risk/maintenance notes: invalid options call `die`, so parsing failures terminate rather than returning recoverable errors in this helper.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/libbcachefs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/libbcachefs.h -->
# File Research: sources/cow-pools/bcachefs-tools/c_src/libbcachefs.h

This header declares tool-side libbcachefs option and format structures. `bch_opt_strs` is a union of by-ID string pointers and named option fields generated from `BCH_OPTS`. It declares option string cleanup and parsing.

It also defines `format_opts`, `dev_opts`, `dev_opts_list`, and `dev_opts_default`, covering filesystem label/UUID/version/encryption/passphrase/source/superblock placement and per-device file, block device, offsets, sizes, labels, and options.

Integration role: shared C data model for format/device setup paths and bindgen.

Risk/maintenance notes: the union relies on `BCH_OPTS()` order matching `bch2_opts_nr` table IDs. `dev_opts_default` only initializes `.opts`, leaving other fields zero/null.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/libbcachefs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/rust_shims.c -->
# File Research: sources/cow-pools/bcachefs-tools/c_src/rust_shims.c

This file implements C wrappers for Rust code that cannot directly call static inline functions, macros, or complex C closure patterns. It includes shims for superblock checksums, stripping allocation metadata from clean filesystems, online device iteration/refcounting, collecting journal replay entries, decrypting jsets/bsets for sanitized dumps, atomic bit setting, device reference get/put, write/read data submission, migration extent linking, and accounting reads.

`strip_fs_alloc` removes allocator btree roots from the clean section, clears replicas and journal fields, marks member freespace uninitialized, and sets the `no_alloc_info` feature. `rust_write_submit` prepares a `bch_write_op`, maps caller data into a bio, obtains disk reservation, and calls `bch2_write`. `rust_read_submit` prepares a `bch_read_bio` and calls `bch2_read`. `rust_link_data` builds extent keys pointing at existing physical sectors, splits at bucket boundaries, reserves space, marks reconcile state, and inserts into the extents btree.

Integration role: major FFI bridge between Rust commands and libbcachefs internal helpers.

Risk/maintenance notes: comments describe the IO shim as currently synchronous-ish through `BCH_WRITE_sync` and closure behavior. `rust_link_data` assumes device 0 and validates block alignment with `BUG_ON`. Several functions return allocated arrays or C resources that Rust must free or manage correctly.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/rust_shims.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/rust_shims.h -->
# File Research: sources/cow-pools/bcachefs-tools/c_src/rust_shims.h

This header declares C shim functions consumed by Rust. It documents wrappers for superblock checksums, allocation metadata stripping, journal replay collection, online member iteration, encrypted dump decryption, bitmap setting, device references, data IO submission, migration extent linking, and accounting reads.

It defines `RUST_IO_MAX` as 1 MiB and `struct rust_journal_entries` as a flat array of journal replay pointers plus count.

Integration role: bindgen-visible declaration surface for `rust_shims.c`.

Risk/maintenance notes: comments specify IO data must be block-aligned and <= 1 MiB; Rust callers need to preserve those preconditions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/rust_shims.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/tools-util.c -->
# File Research: sources/cow-pools/bcachefs-tools/c_src/tools-util.c

This file contains userspace utility functions for bcachefs tools. It implements fatal `die`, fatal signal handlers that print unified backtraces, formatted allocation helpers, checked `fstat`, sysfs-style file string/u64 readers, blkid probing/wiping checks, yes/no prompting, and CRC32C.

The blkid check refuses formatting with libblkid older than 2.40.1 unless forced, probes for existing filesystems/labels, prompts unless forced, and wipes detected signatures. CRC32C uses a software table by default and resolves to SSE4.2 assembly implementation on x86_64 when available, avoiding ifunc by default.

Integration role: common process/error/file/probe/checksum utilities used by C tools and Rust FFI.

Risk/maintenance notes: many helpers terminate the process on errors. The fatal signal handler intentionally uses non-async-signal-safe backtrace formatting for better diagnostics. The CRC resolver stores a static function pointer without explicit synchronization, relying on benign initialization behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/tools-util.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/tools-util.h -->
# File Research: sources/cow-pools/bcachefs-tools/c_src/tools-util.h

This header declares utility functions and macros for bcachefs tools. It provides `die`, fatal signal handler installation, formatted string allocation, checked `fstat`, zeroing `xmalloc`, checked `openat`/`ioctl`/`close` macros, file readers, blkid checks, yes/no prompting, and CRC32C.

It includes Linux compatibility headers and renames `crc32c` to `bch_crc32c` to avoid conflicts with libblkid in static builds.

Integration role: shared utility declarations for C files and bindgen-visible wrappers.

Risk/maintenance notes: checked macros terminate on failure, so callers use them only where fatal behavior is acceptable.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/c_src/tools-util.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/ccan/array_size/array_size.h -->
# File Research: sources/cow-pools/bcachefs-tools/ccan/array_size/array_size.h

This vendored CCAN header defines `ARRAY_SIZE(arr)` with an optional compile-time pointer misuse check using `typeof` and `__builtin_types_compatible_p`.

Integration role: compatibility utility for C code needing safe array element counts.

Risk/maintenance notes: pointer rejection depends on feature macros from `config.h`; otherwise `_array_size_chk` is zero and pointer misuse is not detected.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/ccan/array_size/array_size.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/ccan/build_assert/build_assert.h -->
# File Research: sources/cow-pools/bcachefs-tools/ccan/build_assert/build_assert.h

This vendored CCAN header defines `BUILD_ASSERT(cond)` for statement-context compile-time checks and `BUILD_ASSERT_OR_ZERO(cond)` for expression-context checks.

Integration role: low-level compile-time assertion support used by other compatibility headers such as `array_size`.

Risk/maintenance notes: uses negative-size char array tricks, so diagnostics are compiler-dependent but portable to old C compilers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/ccan/build_assert/build_assert.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/ccan/compiler/compiler.h -->
# File Research: sources/cow-pools/bcachefs-tools/ccan/compiler/compiler.h

This vendored CCAN header defines compiler feature macros such as `COLD`, `NORETURN`, `PRINTF_FMT`, `CONST_FUNCTION`, `PURE_FUNCTION`, `UNNEEDED`, `NEEDED`, `UNUSED`, `IS_COMPILE_CONSTANT`, and `WARN_UNUSED_RESULT`, gated by feature macros from `config.h`.

Integration role: compiler portability layer for C code and vendored helpers.

Risk/maintenance notes: because `c_src/config.h` is empty in this tree, actual feature macro definitions must come from another `config.h`, build flags, or default to disabled paths depending on include resolution.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/ccan/compiler/compiler.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/debian/gbp.conf -->
# File Research: sources/cow-pools/bcachefs-tools/debian/gbp.conf

This git-buildpackage configuration disables pristine-tar, maps upstream tags to `v%(version)s`, ignores branch checks, exports to `../bcachefs-tools-deb-export-dir`, runs `cargo vendor-filterer --versioned-dirs` after export, and uses xz compression level 9.

Integration role: Debian source packaging/export configuration for bcachefs-tools.

Risk/maintenance notes: post-export depends on `cargo vendor-filterer`; missing tooling breaks package export.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/debian/gbp.conf -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/debian/rules -->
# File Research: sources/cow-pools/bcachefs-tools/debian/rules

This Debian rules file drives package builds through debhelper with DKMS support. It enables verbose output, exports dpkg build flags/tools, disables LTO, enables hardening, imports Debian/rust architecture defaults, sets Cargo path/home/crate metadata, configures multiarch pkg-config, sets `PREFIX=/usr` and `ROOT_SBINDIR=/usr/sbin`, freezes Cargo, and sets the Cargo build target.

Overrides prepare Debian vendoring before clean/configure, intentionally neuter `dh_clean` because deleting vendored files breaks Cargo checksumming, skip `dh_usrlocal` due to a documented failure, skip tests, and run `dh-cargo-built-using` after install.

Integration role: Debian packaging build glue for Rust+C+DKMS output.

Risk/maintenance notes: tests are disabled at package build time. Comments warn split/compressed debug info can hurt reproducibility or break DWZ.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/debian/rules -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/debian/tests/kernel-smoke-test -->
# File Research: sources/cow-pools/bcachefs-tools/debian/tests/kernel-smoke-test

This autopkgtest shell script verifies kernel module and tool availability. It removes a dangling `./bcachefs` symlink, fails if `bcachefs` is already loaded, loads the module, runs `modinfo`, lists the loaded module file, runs `bcachefs version`, and then executes sibling test scripts matching the script basename, skipping `.disabled` files.

Each subtest gets a temporary directory exported as `TMPDIR`; failures are accumulated and reported as final exit status.

Integration role: Debian package smoke test for DKMS module loadability plus additional test fragments.

Risk/maintenance notes: the test requires privileges and a kernel where the module can be unloaded/not preloaded. `set +e` is used with manual status checks.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/debian/tests/kernel-smoke-test -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/dkms/Makefile -->
# File Research: sources/cow-pools/bcachefs-tools/dkms/Makefile

This Makefile drives external DKMS module builds. It exports `BCACHEFS_DKMS=1`, includes generated `build.vars`, exports debug/test/restart-injection flags, and when invoked by kbuild adds `src/fs/bcachefs/` as an external module with include path `$(src)/include`.

Outside kbuild, it builds or cleans against `/lib/modules/$(uname -r)/build` by passing `M=$PWD`.

Integration role: DKMS entrypoint installed under `/usr/src/bcachefs-<version>` by the top-level Makefile.

Risk/maintenance notes: relies on `build.vars` generated during `make install_dkms` for debug/test propagation; missing file is tolerated.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/dkms/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/dkms/dkms.conf.in -->
# File Research: sources/cow-pools/bcachefs-tools/dkms/dkms.conf.in

This is the DKMS configuration template. It names the package `bcachefs`, substitutes `@PACKAGE_VERSION@`, enables autoinstall, identifies the built module and source location, installs under `/kernel/fs/bcachefs`, disables stripping, and restricts builds to kernels 6.16 or newer.

Integration role: generated into `dkms/dkms.conf` by the top-level Makefile and installed into the DKMS source directory.

Risk/maintenance notes: kernel minimum is a hard gate; unsupported kernels are skipped by DKMS.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/dkms/dkms.conf.in -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/dkms/module-version.c -->
# File Research: sources/cow-pools/bcachefs-tools/dkms/module-version.c

This C file includes Linux module support and generated `version.h`, then emits `MODULE_VERSION(bcachefs_version)`.

Integration role: DKMS-only object appended by `fs/Makefile` to embed module version metadata.

Risk/maintenance notes: depends on `version.h` being generated and copied into the DKMS source tree.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/dkms/module-version.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/Kconfig -->
# File Research: sources/cow-pools/bcachefs-tools/fs/Kconfig

This Kconfig fragment defines bcachefs kernel configuration options. `BCACHEFS_FS` is an experimental tristate depending on block support and selecting exportfs, checksums, ACLs, compression libraries, crypto primitives, keys, RAID/XOR, xxhash, and symbolic error names.

Additional options enable quota, debugging, transaction restart injection, unit/performance tests, lock time stats, latency-accounting disablement, six-lock optimistic spinning, extra path tracepoints, transaction allocation tracing, and a KUnit mean/variance test.

Integration role: in-tree kernel configuration surface for the bcachefs filesystem module.

Risk/maintenance notes: DKMS builds do not get this Kconfig directly, so `fs/Makefile` mirrors selected config via environment/compiler defines.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/Makefile -->
# File Research: sources/cow-pools/bcachefs-tools/fs/Makefile

This kbuild Makefile builds the bcachefs kernel module. In DKMS mode it sets `CONFIG_BCACHEFS_FS=m`, forwards environment flags for debug, transaction restart injection, and tests into `subdir-ccflags-y`, verifies or degrades the copied `getdents_callback64` layout through `scripts/getdents-layout.sh`, mirrors quota enablement for DKMS when host `CONFIG_QUOTA` is set, and adds include paths.

The `bcachefs-y` object list covers allocation/accounting, btree, data IO/compression/erasure coding/reconcile, debug, filesystem namespace/inode/dirent/quota/xattr, initialization/recovery, journal, options, superblock, snapshots, utilities, vendored bio/closure/minheap code, and VFS integration. It conditionally adds debugfs async objects, excludes the mean/variance KUnit test from DKMS, and includes `module-version.o` for DKMS.

Integration role: authoritative kernel object manifest for both in-tree and DKMS bcachefs builds.

Risk/maintenance notes: external builds depend on generated `bch2_getdents_layout.h`; if the script is missing, the build defines `BCH_GETDENTS_LAYOUT_UNVERIFIED`. The object list must stay synchronized with filesystem source layout.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/Makefile -->