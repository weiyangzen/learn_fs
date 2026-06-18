# Group Research: group_238_bcachefs_tools_sources_cow_pools_bcachefs_tools_raid_raid_c_sources__9a099c4746e2

Scope checked against `Docs/research_subset_a.md`. All 19 listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/raid.c -->
# File Research: sources/cow-pools/bcachefs-tools/raid/raid.c

This is the central RAID parity generation and data-recovery dispatcher for the bundled bcachefs-tools RAID library. It implements GF(2^8)-based erasure coding using either the default Cauchy matrix mode, supporting up to 6 parity blocks and 251 data blocks, or Vandermonde/triple-parity mode for CPUs without fast SSSE3/AVX2 support.

Key responsibilities:
- Maintains `raid_gfgen`, `raid_gen_ptr[]`, `raid_gen3_ptr`, and `raid_genz_ptr` dispatch state.
- Exposes `raid_mode()` to switch Cauchy vs Vandermonde behavior.
- Exposes `raid_zero()` for the zero-filled recovery scratch block required by recovery paths.
- Validates block size and parity count in `raid_gen()`, then calls the selected generator.
- Implements `raid_invert()` for small GF matrix inversion used by recovery.
- Implements `raid_delta_gen()`, which recomputes parity over surviving data while temporarily replacing missing data with the zero block.
- Implements optimized one- and two-data-block recovery helpers: `raid_rec1of1()` and `raid_rec2of2_int8()`.
- Implements public recovery dispatch with `raid_rec()` and `raid_data()`.

Important behavior:
- `size` must be a multiple of 64 bytes.
- Failure index arrays must be sorted.
- `raid_rec()` handles mixed data/parity failures: data is reconstructed first, then bad parity blocks are regenerated up to the highest failed parity.
- Parity functions are assumed to write parity blocks in order; `raid_delta_gen()` relies on that to protect unused parity buffers.

Dependencies:
- `internal.h` for dispatch declarations, macros, and helper prototypes.
- `gf.h` for GF arithmetic tables/functions such as `mul`, `inv`, `pow2`, and `table`.
- Architecture-specific implementations live outside this file, especially in `x86.c` and `x86z.c`.

Notes:
- Public APIs `raid_init()`, `raid_selftest()`, `raid_check()`, and `raid_scan()` are declared in `raid.h` but implemented in other RAID files, not here.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/raid.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/raid.h -->
# File Research: sources/cow-pools/bcachefs-tools/raid/raid.h

This is the public header for the RAID library used by bcachefs-tools. It defines supported modes, hard limits, initialization, parity generation, recovery, verification, and scan APIs.

Key definitions:
- `RAID_MODE_CAUCHY`: default mode, up to 6 parity blocks.
- `RAID_MODE_VANDERMONDE`: up to 3 parity blocks, useful on lower-end CPUs without SSSE3.
- `RAID_PARITY_MAX = 6`.
- `RAID_DATA_MAX = 251`.

Public API:
- `raid_init()` initializes function dispatch and default Cauchy mode.
- `raid_selftest()` runs a startup integrity test.
- `raid_mode()` changes the parity matrix mode for later calls.
- `raid_zero()` sets the required zero-filled recovery buffer.
- `raid_gen()` computes parity blocks.
- `raid_rec()` recovers data and/or parity failures.
- `raid_data()` recovers data failures only using specified parity blocks.
- `raid_check()` validates a suspected failure set using one extra parity.
- `raid_scan()` brute-force scans for failed blocks.

Important contract:
- Block sizes must be multiples of 64 bytes.
- Failure index arrays must be ordered.
- Recovery does not independently verify parity correctness unless `raid_check()`/`raid_scan()` is used.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/raid.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/tag.c -->
# File Research: sources/cow-pools/bcachefs-tools/raid/tag.c

This file maps active RAID function pointers to short backend tags for diagnostics or reporting.

Key behavior:
- Builds a static `RAID_FUNC[]` table from function pointer to backend name.
- Always includes generic integer backends such as `int8`, `int32`, and `int64`.
- Conditionally includes x86/x86_64 SIMD backends depending on build flags:
  - `sse2`
  - `ssse3`
  - `avx2`
  - extended x86_64 variants such as `sse2e`, `ssse3e`, and `avx2e`
- `raid_tag()` returns the matching string for a function pointer, or `"unknown"` as a fallback.

Exported tag helpers:
- Parity generation tags: `raid_gen1_tag()` through `raid_gen6_tag()`, plus `raid_genz_tag()`.
- Recovery tags: `raid_rec1_tag()`, `raid_rec2_tag()`, and `raid_recX_tag()`.

Dependencies:
- Uses dispatch globals from `internal.h`, including `raid_gen_ptr[]`, `raid_genz_ptr`, and `raid_rec_ptr[]`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/tag.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/test.c -->
# File Research: sources/cow-pools/bcachefs-tools/raid/test.c

This file implements RAID self-test helpers for combination generation, insertion/sorting helpers, parity generation, and data recovery.

Test coverage:
- `raid_test_combo()` verifies combination and permutation iterators against recursive binomial/power counts.
- `raid_test_insert()` checks `raid_insert()` keeps arrays sorted across all permutations.
- `raid_test_sort()` checks `raid_sort()` sorts all permutations.
- `raid_test_rec()` tests recovery functions across all data-failure and parity-selection combinations for the chosen mode.
- `raid_test_par()` tests parity generation functions against reference parity output.

Mode handling:
- Cauchy mode tests all 6 parity levels.
- Vandermonde mode tests 3 parity levels.

Backend handling:
- Always tests generic int implementations.
- Adds SSSE3/AVX2/SSE2 variants only when compiled and detected at runtime through CPU feature helpers.

Memory/test pattern:
- Uses RAID memory helpers to allocate aligned vectors.
- Fills deterministic pseudo-random data with fixed seeds.
- Uses saved parity/data buffers and separate test buffers to compare reconstructed output.

Failure behavior:
- Returns `0` on success and `-1` on any mismatch/allocation failure.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/test.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/test.h -->
# File Research: sources/cow-pools/bcachefs-tools/raid/test.h

This header declares the RAID test entry points implemented in `test.c`.

Declared tests:
- `raid_test_insert()`
- `raid_test_sort()`
- `raid_test_combo()`
- `raid_test_rec(unsigned mode, int nd, size_t size)`
- `raid_test_par(unsigned mode, int nd, size_t size)`

The header documents that recovery tests grow exponentially with disk count because they enumerate failure combinations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/test.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/x86.c -->
# File Research: sources/cow-pools/bcachefs-tools/raid/x86.c

This is the main x86/x86_64 SIMD implementation file for RAID parity generation and recovery. It provides SSE2, SSSE3, and AVX2 implementations selected by compile-time configuration and runtime CPU detection elsewhere.

Major generator families:
- `raid_gen1_sse2()` and `raid_gen1_avx2()` implement RAID5 XOR parity.
- `raid_gen2_sse2()`, `raid_gen2_avx2()`, and `raid_gen2_sse2ext()` implement RAID6 P/Q parity using powers of 2 in GF(2^8).
- `raid_gen3_*`, `raid_gen4_*`, `raid_gen5_*`, and `raid_gen6_*` implement Cauchy-matrix parity for 3 through 6 parity blocks.
- x86_64 “ext” variants use more XMM/YMM registers and larger loop bodies.
- Single-data-disk special cases copy the only data block to all parity blocks.

SIMD technique:
- Uses inline assembly directly.
- Uses non-temporal stores (`movntdq`/`vmovntdq`) for parity output.
- Uses `pshufb`/`vpshufb` nibble lookup tables for fast GF multiplication in SSSE3/AVX2 Cauchy generation.
- Uses `gfconst16.poly` for GF multiply-by-2 reduction and `gfconst16.low4` for nibble extraction.
- x86-32 variants for 5/6 parity spill accumulator state through aligned stack buffers due to register pressure.

Recovery implementations:
- `raid_rec1_ssse3()` / `raid_rec1_avx2()` recover one data block.
- `raid_rec2_ssse3()` / `raid_rec2_avx2()` recover two data blocks.
- `raid_recX_ssse3()` / `raid_recX_avx2()` recover a variable number of blocks up to `RAID_PARITY_MAX`.
- Recovery builds a coefficient matrix with `A(ip[j], id[k])`, inverts it with `raid_invert()`, computes delta parity with `raid_delta_gen()`, and applies SIMD GF multiplication lookup tables to reconstruct missing blocks.

Dependencies:
- `internal.h` for SIMD begin/end wrappers and dispatch declarations.
- `gf.h` for GF tables such as `gfgenpshufb`, `gfmulpshufb`, and matrix coefficient macro/function `A`.

Important assumptions:
- Input buffers are aligned as required by `movdqa`/`vmovdqa`.
- Callers satisfy the RAID library’s block-size multiple constraints.
- AVX/SSE state transition handling is delegated to `raid_sse_begin/end()` and `raid_avx_begin/end()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/x86.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/x86z.c -->
# File Research: sources/cow-pools/bcachefs-tools/raid/x86z.c

This file implements x86 SIMD versions of `GENz`, the Vandermonde-style triple parity scheme using coefficients `1`, `2`, and `2^-1`.

Implementations:
- `raid_genz_sse2()` for x86 SSE2.
- `raid_genz_sse2ext()` for x86_64 SSE2 with 16 XMM registers.
- `raid_genz_avx2ext()` for x86_64 AVX2.

Algorithm:
- Computes P as XOR parity.
- Computes Q through repeated GF multiply-by-2.
- Computes R through repeated GF divide-by-2 using masks/constants.
- Processes buffers in 16-, 32-, or 64-byte chunks depending on backend.

Constants:
- `gfzconst16.poly` is the GF reduction polynomial.
- `gfzconst16.half` supports divide-by-2 correction.
- `gfzconst16.low7` masks shifted values.

Role in system:
- Used when `raid_mode(RAID_MODE_VANDERMONDE)` installs `raid_genz_ptr` as the third parity generator.
- Optimized for triple parity on systems where Cauchy SSSE3/AVX2 may not be available or desired.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/raid/x86z.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/rustfmt.toml -->
# File Research: sources/cow-pools/bcachefs-tools/rustfmt.toml

This is the Rust formatting configuration for bcachefs-tools.

Settings:
- Uses Rust 2021 edition.
- Forces Unix newlines.
- Aligns enum discriminants and struct fields when alignment thresholds are 20.

The file is small and only affects formatting/style, not runtime behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/rustfmt.toml -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/scripts/deploy-poo.sh -->
# File Research: sources/cow-pools/bcachefs-tools/scripts/deploy-poo.sh

This Bash script builds and deploys the “Principles of Operation” PDF.

Behavior:
- Uses `set -e`.
- Changes to the repository root relative to the script path.
- Consumes stdin when run as a git hook.
- Runs `make bcachefs-principles-of-operation.pdf`.
- Copies the PDF to `root@evilpiepirate.org:/home/bcachefs/doc/`.
- Runs remote `chown bcachefs:bcachefs` on the deployed PDF.
- Prints the public deployment URL.

Operational notes:
- Can be run directly or symlinked as `.git/hooks/pre-push`.
- Requires SSH access to the deployment host as root.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/scripts/deploy-poo.sh -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/bcachefs.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/bcachefs.rs

This is the Rust main entry point for the `bcachefs` CLI binary.

Responsibilities:
- Declares Rust modules for commands, device scanning, key handling, logging, qcow2, wrappers, HTTP, and utility code.
- Installs C-side fatal signal handlers early.
- Sets C stdout to line-buffered to reduce Rust/C output reordering.
- Handles symlink invocations:
  - `mkfs*` maps to `format`.
  - `fsck*` maps to `fsck`.
  - `mount.fuse*` maps to `fusemount`.
  - `mount*` maps to `mount`.
- Prints grouped command usage for missing/help commands.
- Supports hidden `_doc_gen` command to generate LaTeX CLI documentation.
- Calls `raid_init()` before dispatching commands.
- Initializes Linux shrinkers unless the command defers them.
- Warns if the running kernel lacks `CONFIG_RUST`.
- Dispatches to the command registry.

Documentation generation:
- Walks the clap command tree.
- Escapes LaTeX special characters.
- Converts `<<sec:...>>` references to LaTeX section references.
- Writes `doc/generated/cli-reference.tex`.

Dependencies:
- Uses generated C bindings from `bch_bindgen::c`.
- Uses `commands::COMMAND_GROUPS` and `commands::dispatch()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/bcachefs.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/attr.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/attr.rs

This file implements file-level option commands for bcachefs.

Commands:
- `set-file-option`
- `reflink-option-propagate`

`set-file-option` behavior:
- Builds dynamic clap arguments from inode option metadata.
- Sets extended attributes named `bcachefs.<option>`.
- Removes a specific option when value is `-`.
- Supports `--remove-all`, excluding `casefold` because it only works on empty directories.
- If the target is a directory, recursively propagates inherited attributes to children through `BCHFS_IOC_REINHERIT_ATTRS`.
- Skips symlink recursion.

`reflink-option-propagate` behavior:
- Propagates current IO options to reflinked extents.
- Optional `--set-may-update` calls an ioctl to set the permission bit on old reflink pointers.
- Maps `EPERM` to a user-facing error suggesting rerun as root with `--set-may-update`.

Key ioctls:
- `BCHFS_IOC_REINHERIT_ATTRS`
- `BCHFS_IOC_SET_REFLINK_P_MAY_UPDATE_OPTS`
- `BCHFS_IOC_PROPAGATE_REFLINK_P_OPTS`

Dependencies:
- `rustix::fs` for xattr operations.
- `bch_bindgen::c` for option metadata.
- Local `opts` helpers for option parsing.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/attr.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/completions.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/completions.rs

This file implements the `bcachefs completions` command.

Behavior:
- Uses clap’s derive parser for a single `Shell` argument.
- Calls `clap_complete::generate()` against `super::build_cli()`.
- Writes completions to stdout.
- Registers the command as a typed `CmdDef`.

Supported shells are those provided by `clap_complete::Shell`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/completions.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/counters.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/counters.rs

This file implements `reset-counters`, a command for resetting persistent filesystem counters on an unmounted device.

Behavior:
- Accepts optional comma-separated counter names through `--counters` / `--counter`.
- Validates names against `COUNTERS`.
- Scans member devices from the provided device path.
- Opens the filesystem with:
  - `nostart = 1`
  - `degraded = very`
- Calls `bch2_counter_reset()` for either all counters or selected counters.
- Locks and writes the superblock to persist the reset.

Dependencies:
- `bch_bindgen::fs::Fs` for filesystem opening.
- Generated counter metadata from `bch_bindgen::sb::COUNTERS`.
- `crate::device_scan::scan_sbs()` for member discovery.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/counters.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/data_read.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/data_read.rs

This file implements `data-read`, a low-level read command with extended bcachefs error reporting.

Behavior:
- Opens the target file with `O_DIRECT`.
- Requires offset and length to be 512-byte sector aligned.
- Allocates a 512-byte-aligned buffer manually.
- Calls the raw pread ioctl `_IOWR(0xbc, 67, struct bch_ioctl_pread_raw)`.
- Supports `--no-poison-check` to read data from poisoned extents.
- Reports error bitmask categories:
  - checksum
  - IO
  - decompression
  - erasure-code reconstruction
- Prints kernel-provided error text when available.
- Writes raw output to a file if `--output` is set, otherwise prints a hex dump.

Important note:
- If the ioctl returns an error, the command still dumps whatever data was returned, then exits with code 1.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/data_read.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/device.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/device.rs

This file implements the `bcachefs device` command group.

Subcommands:
- `add`
- `online`
- `offline`
- `remove`
- `evacuate`
- `set-state`
- `resize`
- `resize-journal`

Major behavior:
- `add` first tries online add through a mounted filesystem handle, then falls back to offline add with `nostart`, `copygc_enabled=0`, and `reconcile_enabled=0`.
- Device-add formatting reuses `format_util::format_for_device_add()`.
- Device paths and numeric device indexes can be resolved against a filesystem handle.
- Multipath component devices are detected and require `--force`.
- `offline`, `remove`, and `set-state` set force flags for degraded/data/metadata-loss cases.
- Offline `set-state` edits member state directly in the superblock.
- `resize` supports online growth and offline growth; shrinking is explicitly rejected.
- `resize-journal` supports online and offline paths.
- `evacuate` sets a device readonly/evacuating, triggers reconcile wakeup, and polls until visible non-hidden data sectors reach zero.

Version/safety checks:
- Evacuation requires kernel and filesystem metadata version supporting reconcile.
- Offline resize helpers require exactly one online device in the filesystem.

Dependencies:
- `BcachefsHandle` for online ioctls/sysfs-backed operations.
- `Fs` for offline open/start/write-super flows.
- `device_multipath`, `format_util`, `sysfs`, and accounting wrappers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/device.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/dump.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/dump.rs

This file implements metadata dump and undump commands using qcow2 images.

Commands:
- `dump`: dumps filesystem metadata to one or more `.qcow2` images.
- `undump`: converts qcow2 dump files back to raw device images.

Dump behavior:
- Opens the filesystem read-only with no changes, no recovery, degraded-very, continue-on-error, and no fsck fixes.
- Collects ranges for:
  - superblock layout and all superblock copies
  - journal buckets
  - btree node locations
- Walks every alive btree id and every level using btree iterators, capturing nodes reachable through journal overlay.
- Writes one qcow2 image for a single online device, or indexed images for multiple devices.

Sanitization:
- `--sanitize` defaults to inline data sanitization.
- `--sanitize=filenames` also overwrites dirent names with `X`.
- Sanitizes journal key payloads and btree node key payloads.
- Handles encrypted journal/btree blocks by calling C decrypt bridge functions before sanitization.
- Clears checksums and checksum-type flags after modifying sanitized structures.

Undump behavior:
- Requires `.qcow2` input suffix.
- Refuses to overwrite outputs unless `--force` is used.
- Converts qcow2 contents back to raw images.

Dependencies:
- `crate::qcow2`
- btree/accounting/data bindings
- superblock wrapper helpers
- C decrypt bridge functions `rust_jset_decrypt()` and `rust_bset_decrypt()`
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/dump.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/format.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/format.rs

This file implements `bcachefs format` / `mkfs` argument parsing and high-level format orchestration.

Design:
- Uses manual parsing instead of clap because device-specific options are positional/sticky and dynamic C options are parsed through generated option tables.

Parsing supports:
- Filesystem options from the C option table.
- Device options that apply to subsequent device paths.
- `--replicas`
- `--encrypted`
- `--passphrase_file`
- `--no_passphrase`
- `--fs_label` / `-L`
- `--uuid` / `-U`
- `--superblock_size`
- `--version`
- `--source`
- `--no_initialize`
- `--force`, `--quiet`, `--verbose`, and help.

High-level flow:
- Parses arguments into `FormatConfig`.
- Prompts or reads passphrase when encryption requires it.
- Loads the bcachefs module opportunistically to detect kernel metadata version.
- Chooses requested/current/kernel-compatible metadata version.
- Disables initialization for version mismatch or `BCACHEFS_KERNEL_ONLY`.
- Builds C `format_opts` and deferred string options.
- Builds `format_util::DevOpts` for each device.
- Checks multipath components and opens devices.
- Calls `format_util::format()`.
- Prints superblock unless quiet.
- Optionally opens the new filesystem and initializes it, including copying from `--source`.

Validation:
- Rejects missing devices.
- Rejects dangling device-specific options.
- Rejects incompatible `--source`/`--no_initialize`.
- Requires `--encrypted` for passphrase file usage.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/format.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/format_util.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/format_util.rs

This file is the Rust implementation of bcachefs formatting internals, replacing C `bch2_format` and `bch2_format_for_device_add`.

Core type:
- `DevOpts` owns a device fd, path, label, size/offset metadata, per-device options, and closes the fd on drop.

Main functions:
- `format()` creates and writes a new filesystem superblock across one or more devices.
- `format_for_device_add()` formats a single device for adding to an existing filesystem.
- `format_opts_default()` chooses default metadata version from kernel/current support.
- `pick_block_size()` chooses 512 bytes for small filesystems and at least 4 KiB/physical block size for larger ones.
- `pick_bucket_size()` chooses a filesystem-wide bucket size based on block size, btree node size, encoded extent size, total filesystem size, and fsck memory constraints.
- `check_bucket_size()` validates per-device bucket constraints.

Format logic:
- Determines missing device sizes.
- Selects block size, bucket sizes, btree node size, UUIDs, labels, member fields, feature bits, and time base.
- Sets all superblock options from filesystem and device `bch_opts`.
- Builds members_v2 and v1 compatibility copies.
- Resolves foreground/background/promote/metadata targets from device paths or disk groups.
- Initializes encryption field when requested.
- Writes superblock layouts and zeroes the start of disks when using the default superblock sector.
- Triggers `udevadm trigger --settle` for formatted devices.

Important safety behavior:
- Device opening uses exclusive read/write buffered mode and blkid checks unless explicitly bypassed by special helpers.
- Fatal validation failures call wrapper `die()`, matching older C behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/format_util.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/fs_usage.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/fs_usage.rs

This file implements the `usage` command for detailed filesystem space reporting.

CLI behavior:
- Default field is `rebalance_work`.
- `--fields/-f` accepts comma-separated field names.
- `--all/-a` enables replicas, btree, compression, rebalance/reconcile work, and devices.
- `--human-readable/-h` enables human-readable sizes.
- Defaults mountpoint argument to `.`.

Reported sections:
- Filesystem UUID, size, used, and online reserved.
- Replica/durability summary.
- Optional detailed replica rows.
- Optional compression stats.
- Optional per-btree usage.
- Optional rebalance or reconcile pending work.
- Device summary or full per-device breakdown.

Accounting behavior:
- Queries accounting through `BcachefsHandle::query_accounting()`.
- Chooses old `rebalance_work` or newer `reconcile_work`/`dev_leaving` accounting based on kernel metadata version.
- Sorts accounting entries by bpos before printing.
- Computes durability/degraded matrices for replicated data.
- Groups erasure-coded entries by data+parity configuration.
- Separately tracks cached and persistent reserved sectors.
- Reads device info from sysfs and per-device usage through the handle.

Dependencies:
- Accounting wrappers for decoding `DiskAccountingKind`.
- `Printbuf` for aligned text and size formatting.
- `sysfs` wrappers for device discovery and kernel version.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/fs_usage.rs -->