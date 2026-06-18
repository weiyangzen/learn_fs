# Group Research: group_1776_stratisd_sources_block_storage_stratisd_src_bin_stratis_min_stratis_6190958a2dfb

Scope: `Docs/research_subset_a.md`, source tree `sources/block-storage/stratisd`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/stratis-min/stratis-min.rs -->
# File Research: sources/block-storage/stratisd/src/bin/stratis-min/stratis-min.rs

Minimal Stratis client binary. It defines a `clap` command tree for `key`, `pool`, `filesystem`, and `report`, then dispatches each command to `stratisd::jsonrpc::client::{key,pool,filesystem,report}`.

Key behavior:
- Parses key operations: `set`, `list`, `unset`; `set` accepts either captured input or `--keyfile-path`, but dispatch passes only the optional file path.
- Parses pool lifecycle commands: `start`, `stop`, `create`, `init-cache`, `rename`, add data/cache devices, destroy, and status predicates.
- Converts pool IDs between name and UUID with `PoolIdentifier::{Name,Uuid}`.
- Handles encryption inputs for pool creation: `--key-descs` values as `key_desc[:token_slot]`; `--clevis-infos` as whitespace-separated key/value pairs with `pin=tang|tpm2`, token slots, Tang URL, thumbprint, or `trust_url`.
- Implements bind/unbind/rebind for keyring and Clevis/Tang/TPM2, including legacy token-slot handling through `OptionalTokenSlotInput`.
- Filesystem subcommands create, destroy, rename, list, and print origin.
- `report` prints formatted JSON from the daemon.

Important details:
- Errors are normalized by `main()` into `Result<(), String>`.
- `parse_args().debug_assert()` is covered by a unit test.
- The file is argument translation glue; filesystem/block-storage semantics are in the JSON-RPC client and engine calls.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/stratis-min/stratis-min.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/stratis-min/stratisd-min.rs -->
# File Research: sources/block-storage/stratisd/src/bin/stratis-min/stratisd-min.rs

Minimal daemon entry point for `stratisd-min`. It exposes `--log-level` and `--sim`, configures logging, locks PID files, and calls `stratisd::stratis::run()`.

Key behavior:
- Uses `/run/stratisd-min.pid` as its own nonblocking flock-guarded PID file.
- Also attempts to lock `/run/stratisd.pid` so full `stratisd` and `stratisd-min` do not run together.
- Writes its current PID into the min PID file after acquiring the lock.
- Uses explicit log-level filtering for the `stratisd` target, otherwise honors `RUST_LOG`.
- `--sim` selects the simulator engine via `run(args.get_flag("sim"))`.

Filesystem relevance:
- This is the minimal daemon used by initrd/rootfs setup paths.
- Locking prevents two Stratis engine instances from concurrently managing the same device state.

Testing:
- Includes `parse_args().debug_assert()` unit coverage.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/stratis-min/stratisd-min.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/stratis-utils.rs -->
# File Research: sources/block-storage/stratisd/src/bin/stratis-utils.rs

Top-level multiplexer for utility executables.

Key behavior:
- Imports `mod utils` and dispatches to `utils::cmds()`.
- Supports invocation as `stratis-utils <executable>` or as a symlink/name matching a concrete utility.
- Validates `<executable>` against known utility command names when invoked as `stratis-utils`.
- Extracts the basename from `argv[0]` to identify which utility to run.
- Returns `ExecutableError` for invalid executable names or non-string command names.

Registered commands come from `src/bin/utils/cmds.rs`: predict usage, decode device-mapper names, and systemd generators when enabled.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/stratis-utils.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/stratisd-tools.rs -->
# File Research: sources/block-storage/stratisd/src/bin/stratisd-tools.rs

Top-level multiplexer for daemon/admin tools.

Key behavior:
- Imports `mod tools` and dispatches through `tools::cmds()`.
- Initializes `env_logger` from `RUST_LOG`, defaulting to logger defaults otherwise.
- Supports invocation as `stratisd-tools <executable>` or directly through a symlink/binary name.
- Builds top-level help listing tools whose `show_in_after_help()` returns true.
- Exits with code `1` for run errors and code `2` for unknown executable names.

This wrapper exposes metadata inspection/checking and legacy-pool test tooling.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/stratisd-tools.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/stratisd.rs -->
# File Research: sources/block-storage/stratisd/src/bin/stratisd.rs

Primary `stratisd` daemon entry point.

Key behavior:
- Defines `--sim` and `--log-level`.
- Acquires `/run/stratisd.pid` with nonblocking flock, writes current PID, and errors if another full daemon is running.
- Checks `/run/stratisd-min.pid`; if locked by `stratisd-min`, reads its PID, sends `SIGINT`, and waits for the lock to release.
- Configures logging for `stratisd` from explicit log level or `RUST_LOG`.
- Calls `stratisd::stratis::run(sim)` and exits with process status `0` or `1`.

Filesystem relevance:
- The lock handoff from `stratisd-min` to full `stratisd` avoids concurrent block-device ownership during boot transition.
- PID-file handling is part of daemon exclusivity for pool/device management.

Testing:
- Includes `parse_args().debug_assert()`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/stratisd.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/tools/check_metadata.rs -->
# File Research: sources/block-storage/stratisd/src/bin/tools/check_metadata.rs

Metadata JSON validation/printing helper.

Key behavior:
- Reads an input file as UTF-8 text.
- Parses JSON into Stratis pool-inspection metadata structures via `serde_json::from_str`.
- If `print` is false, calls `engine::pool_inspection::inspectors::check`.
- If `print` is true, calls `inspectors::print`.

This is used by `stratis-checkmetadata` and `stratis-printmetadata`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/tools/check_metadata.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/tools/cmds.rs -->
# File Research: sources/block-storage/stratisd/src/bin/tools/cmds.rs

Command registry and CLI definitions for `stratisd-tools`.

Commands:
- `stratis-dumpmetadata`: reads Stratis metadata from a device; accepts `--print-bytes/-b` and `--only pool`.
- `stratis-checkmetadata`: validates pool-level metadata JSON.
- `stratis-printmetadata`: prints a human-readable metadata representation.
- `stratis-legacy-pool`: creates a v1 pool for testing, with optional key and Clevis/Tang/TPM2 options.

Important structures:
- `ToolCommand` trait abstracts `name`, `run`, and help visibility.
- Each command owns a `clap::Command` builder and parses its own arguments.
- `cmds()` returns boxed command implementations for the multiplexer.

Testing:
- Parser debug assertions cover dump/check/print metadata commands.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/tools/cmds.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/tools/dump_metadata.rs -->
# File Research: sources/block-storage/stratisd/src/bin/tools/dump_metadata.rs

Reads and prints Stratis on-device metadata from a block device.

Key behavior:
- Opens the device read-only.
- Reads both static signature blocks with `StaticHeader::read_sigblocks`.
- Prints one or both signature blocks depending on equality.
- Optionally pretty-hex dumps signature-block bytes.
- Repairs/selects a valid static header with `StaticHeader::repair_sigblocks(..., StaticHeader::do_nothing)`.
- Loads the BDA using `BDA::load`.
- Seeks back to device start, loads pool state through `bda.load_state`, parses it as JSON, and pretty-prints it.
- `--only pool` suppresses signature/BDA output and prints only machine-readable pool JSON.

Filesystem relevance:
- Direct inspection path for Stratis metadata layout: static headers, BDA, and serialized pool state.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/tools/dump_metadata.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/tools/legacy_pool.rs -->
# File Research: sources/block-storage/stratisd/src/bin/tools/legacy_pool.rs

Testing-only v1 pool creation helper.

Key behavior:
- Parses pool name, block devices, optional key description, and optional Clevis binding.
- Supports Clevis `nbde`/`tang` with Tang URL plus thumbprint or trust URL, and `tpm2` with empty JSON config.
- Warns interactively that generated v1 pools are only for testing and exits unless the user confirms.
- Converts block-device paths through `ProcessedPathInfos`.
- Builds legacy encryption info with `InputEncryptionInfo::new_legacy`.
- Registers Clevis token support, then calls `StratPool::initialize`.

Filesystem relevance:
- Creates old-format pools for compatibility testing against current Stratis code.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/tools/legacy_pool.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/tools/mod.rs -->
# File Research: sources/block-storage/stratisd/src/bin/tools/mod.rs

Small module aggregator for `stratisd-tools`.

Contents:
- Declares `check_metadata`, `cmds`, `dump_metadata`, and `legacy_pool`.
- Re-exports `cmds::cmds`.

No runtime logic beyond module wiring.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/tools/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/udev-lib/stratis-base32-decode.rs -->
# File Research: sources/block-storage/stratisd/src/bin/udev-lib/stratis-base32-decode.rs

Tiny udev helper that decodes a base32 value.

Key behavior:
- Requires two arguments: variable name and base32 string.
- Decodes with `data_encoding::BASE32_NOPAD`.
- Interprets decoded bytes as UTF-8.
- Prints `name=decoded_value`.

Likely used from udev rules to decode Stratis-safe encoded values into environment assignments.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/udev-lib/stratis-base32-decode.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/udev-lib/stratis-str-cmp.rs -->
# File Research: sources/block-storage/stratisd/src/bin/udev-lib/stratis-str-cmp.rs

Tiny udev helper for string comparison.

Key behavior:
- Requires two string arguments.
- Prints `0` if equal, `1` otherwise.
- Returns errors only for missing arguments.

The stdout convention is suitable for udev rule condition pipelines.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/udev-lib/stratis-str-cmp.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/cmds.rs -->
# File Research: sources/block-storage/stratisd/src/bin/utils/cmds.rs

Command registry and CLI definitions for `stratis-utils`.

Commands:
- `stratis-predict-usage`: predicts pool/filesystem space usage.
- `stratis-decode-dm`: maps `/dev/mapper/<dm-name>` to pool name, filesystem name, or `/dev/stratis/<pool>/<fs>` symlink.
- `stratis-setup-generator`: systemd generator when `systemd_compat` is enabled.
- `stratis-clevis-setup-generator`: systemd generator for Clevis rootfs setup when `systemd_compat` is enabled.

Important details:
- `ExecutableError` is the shared boxed-error type for unsupported utility paths.
- `StratisPredictUsage` validates integrity tag spec values using `IntegrityTagSpec::VARIANTS`.
- Pool prediction takes device sizes, optional filesystem sizes, overprovision flag, and integrity options.
- Filesystem prediction requires one or more filesystem sizes and overprovision flag.
- `StratisDecodeDm` requires an absolute path and an output enum: `filesystem-name`, `pool-name`, or `symlink`.
- Systemd generator commands accept normal/early/late generator directories but use the early directory.

Testing:
- Parser debug assertions for predict-usage and, conditionally, generator CLI shape.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/cmds.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/decode_dm.rs -->
# File Research: sources/block-storage/stratisd/src/bin/utils/decode_dm.rs

Maps Stratis filesystem device-mapper paths back to user-facing Stratis names.

Key behavior:
- Connects to the system D-Bus and calls ObjectManager `GetManagedObjects` on `org.storage.stratis3`.
- Extracts device-mapper names from absolute `/dev/mapper/<name>` paths.
- Parses names of form `stratis-1-<pool_uuid>-thin-fs-<filesystem_uuid>`.
- Looks up `Name` properties by matching `Uuid` properties on current package-minor revision interfaces:
  - `org.storage.stratis3.pool.r<minor>`
  - `org.storage.stratis3.filesystem.r<minor>`
- Exposes:
  - `pool_name(dm_path)`
  - `filesystem_name(dm_path)`
  - `symlink(dm_path)` returning `/dev/stratis/<pool>/<filesystem>`.

Filesystem relevance:
- Bridges low-level device-mapper names and Stratis logical filesystem naming.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/decode_dm.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/generators/lib.rs -->
# File Research: sources/block-storage/stratisd/src/bin/utils/generators/lib.rs

Shared helpers for systemd generators.

Key behavior:
- Defines a logger that forwards log records to `stratisd::systemd::syslog`.
- `setup_logger()` installs the systemd logger at `Info`.
- `get_kernel_cmdline()` reads `/proc/cmdline` and returns a map from option name to optional list of values.
- Handles repeated kernel parameters by accumulating values.
- Bare flags are represented as `None`.
- `write_unit_file()` creates/truncates a destination file and writes generated unit contents.

Used by both Stratis rootfs and Clevis setup generators.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/generators/lib.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/generators/mod.rs -->
# File Research: sources/block-storage/stratisd/src/bin/utils/generators/mod.rs

Module aggregator for systemd generator support.

Contents:
- Private `lib`.
- Public `stratis_clevis_setup_generator`.
- Public `stratis_setup_generator`.

Compiled only through the parent `utils` module when `systemd_compat` is enabled.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/generators/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/generators/stratis_clevis_setup_generator.rs -->
# File Research: sources/block-storage/stratisd/src/bin/utils/generators/stratis_clevis_setup_generator.rs

Systemd generator for Clevis setup of a Stratis root filesystem.

Key behavior:
- Reads `stratis.rootfs.pool_uuid` from `/proc/cmdline`.
- If missing, logs a warning and disables itself without error.
- Parses the pool UUID.
- Writes `stratis-clevis-setup.service` into the early generator directory.
- The generated unit wants/starts `stratisd-min.service` and `network-online.target`, runs `/usr/lib/systemd/stratis-clevis-rootfs-setup`, and exports `STRATIS_ROOTFS_UUID`.

Error handling:
- `generator()` sets up systemd logging, runs the generator, logs failures, and returns the original result.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/generators/stratis_clevis_setup_generator.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/generators/stratis_setup_generator.rs -->
# File Research: sources/block-storage/stratisd/src/bin/utils/generators/stratis_setup_generator.rs

Systemd generator for Stratis root filesystem setup in initrd.

Key behavior:
- Reads `stratis.rootfs.pool_uuid` from `/proc/cmdline`.
- If missing, logs a warning and exits successfully.
- Parses the pool UUID.
- Writes `stratis-setup.service` into the early generator directory.
- Creates `/run/systemd/system/initrd.target.wants` if needed and symlinks the generated unit into it.
- Generated unit wants `stratisd-min.service`, console ask-password, and Clevis setup, then runs `/usr/lib/systemd/stratis-rootfs-setup`.

Filesystem relevance:
- Boot-time bridge for activating a Stratis-managed root filesystem.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/generators/stratis_setup_generator.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/mod.rs -->
# File Research: sources/block-storage/stratisd/src/bin/utils/mod.rs

Small module aggregator for `stratis-utils`.

Contents:
- Declares `cmds`, `decode_dm`, optional `generators`, and `predict_usage`.
- Re-exports `cmds::{cmds, ExecutableError}`.

No runtime logic beyond feature-gated module wiring.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/predict_usage.rs -->
# File Research: sources/block-storage/stratisd/src/bin/utils/predict_usage.rs

Implements JSON space-usage prediction for Stratis pool/filesystem creation.

Key behavior:
- Filesystem logical size must be at least 512 MiB, less than 32 PiB, and sector-aligned.
- Overprovisioned filesystem usage uses `FSSizeLookup`, a recorded usage table indexed by rounded-up log2 size.
- Non-overprovisioned filesystem usage sums logical sectors directly.
- Pool prediction subtracts:
  - Stratis BDA/metadata allocation.
  - dm-integrity metadata space from `integrity_meta_space`.
  - crypt metadata offset `DEFAULT_CRYPT_DATA_OFFSET_V2`.
  - thin-pool metadata and MDV sizes from `ThinPoolSizeParams`.
  - optional predicted filesystem usage.
- Emits JSON strings for byte counts:
  - Filesystem: `{"used": "..."}`
  - Pool: `{"total","used","free","stratis-admin-space","stratis-metadata-space"}`.

Filesystem relevance:
- Encodes practical capacity planning rules for Stratis layered storage: block device metadata, integrity metadata, crypt offset, thin metadata, and filesystem provisioning.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/bin/utils/predict_usage.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_0/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_0/methods.rs

D-Bus method implementation for blockdev r0 user info mutation.

Key behavior:
- `set_user_info_method()` gets the mutable pool by UUID.
- Converts D-Bus optional tuple to Rust `Option<&str>`.
- Calls `pool.set_blockdev_user_info`.
- Maps `RenameAction` to D-Bus result tuple:
  - `Renamed` returns changed with blockdev UUID.
  - `Identity` returns OK unchanged.
  - `NoSource` returns error.
- Uses `handle_action!` for action logging.

This is the method-style API used before later revisions make user info a writable property.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_0/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_0/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_0/mod.rs

D-Bus interface implementation `org.storage.stratis3.blockdev.r0`.

Key behavior:
- Defines `BlockdevR0` with engine, manager, parent pool UUID, and blockdev UUID.
- Registers/unregisters the object with zbus object server.
- Exposes method `SetUserInfo`.
- Exposes properties:
  - `Devnode`
  - `HardwareInfo`
  - `UserInfo`
  - `InitializationTime`
  - `Pool`
  - `Uuid`
  - `Tier`
  - `PhysicalPath`
  - `TotalPhysicalSize`

Property reads are delegated to shared `blockdev_prop()` plus r0 property functions.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_0/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_0/props.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_0/props.rs

Property accessors for blockdev D-Bus revisions.

Properties:
- `devnode_prop`: returns metadata path.
- `hardware_info_prop`: optional hardware info as D-Bus `(bool, String)`.
- `init_time_prop`: initialization timestamp as `u64`.
- `physical_path_prop`: actual device node path.
- `pool_prop`: resolves parent pool object path from manager.
- `total_physical_size_prop`: device size in bytes as string.
- `tier_prop`: data/cache tier as `u16`.
- `user_info_prop`: optional user info as `(bool, String)`.

These functions are reused by later blockdev revisions.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_0/props.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_1/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_1/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r1`.

This revision is structurally the same as r0:
- Owns engine, manager, parent pool UUID, and blockdev UUID.
- Registers/unregisters `BlockdevR1`.
- Reuses r0 method/property helpers.
- Exposes method-style `SetUserInfo`.
- Exposes the same properties as r0.

Purpose is API revision continuity under a distinct interface name.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_1/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_2/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_2/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r2`.

This revision matches r1/r0 behavior:
- Method-style `SetUserInfo`.
- Same read-only/read-write property surface as r0.
- Reuses r0 helper functions for property extraction and user-info mutation.
- Registers a separate revisioned zbus interface on the same object path.

No additional blockdev semantics are introduced in this file.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_2/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_3/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_3/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r3`.

Changes relative to r0-r2:
- Adds stored `connection` so property setters can emit change signals.
- Converts `UserInfo` from method-style mutation to a writable D-Bus property.
- Adds `NewPhysicalSize` property.
- Uses shared `set_blockdev_prop()` for setter flow: acquire mutable pool, apply change, emit signal only if changed.

Other properties remain inherited from r0 helpers.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_3/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_3/props.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_3/props.rs

Additional blockdev property helpers for r3+.

Key behavior:
- `new_physical_size_prop()` returns optional detected new size as `(bool, String)`.
- `set_user_info_prop()` compares current user info before mutating, returning whether a property signal is needed.
- Uses `pool.set_blockdev_user_info` for actual mutation.
- `send_user_info_signal_on_change()` resolves the blockdev object path from manager and sends the user-info changed signal.

This file supports the writable-property API introduced in blockdev r3.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_3/props.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_4/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_4/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r4`.

Behavior:
- Same r3 property-style API.
- Keeps writable `UserInfo`.
- Keeps `NewPhysicalSize`.
- Reuses r0 common property helpers and r3 setter/signal helpers.
- Registers as a distinct revisioned interface.

No unique semantic delta from r3 is present in this file.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_4/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_5/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_5/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r5`.

Behavior:
- Same as r4/r3: writable `UserInfo`, `NewPhysicalSize`, and inherited blockdev properties.
- Uses `set_blockdev_prop()` to emit user-info signals only on value changes.
- Separate interface revision for compatibility.

No file-local behavior change from r4.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_5/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_6/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_6/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r6`.

Behavior:
- Same blockdev property surface as r3-r5.
- Includes an explicit `#[allow(non_snake_case)]` on `devnode`, but the exposed property remains the same.
- Writable `UserInfo` and `NewPhysicalSize` are retained.
- Reuses r0/r3 helpers.

No storage semantic change is introduced here.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_6/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_7/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_7/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r7`.

Behavior:
- Same as r6: revisioned compatibility interface.
- Exposes inherited properties and writable `UserInfo`.
- Exposes `NewPhysicalSize`.
- Uses shared blockdev property getter/setter infrastructure.

No file-local semantic delta from r6.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_7/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_8/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_8/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r8`.

Behavior:
- Carries forward r3+ writable-property API.
- Exposes `Devnode`, `HardwareInfo`, `UserInfo`, `InitializationTime`, `Pool`, `Uuid`, `Tier`, `PhysicalPath`, `TotalPhysicalSize`, and `NewPhysicalSize`.
- Uses r0 property helpers and r3 user-info/new-size helpers.

No additional behavior beyond revisioned compatibility.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_8/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_9/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_9/mod.rs

D-Bus interface `org.storage.stratis3.blockdev.r9`.

Behavior:
- Latest listed blockdev revision in this group.
- Same surface as r8/r7: writable `UserInfo`, `NewPhysicalSize`, and common blockdev properties.
- Uses manager lookups for pool path and change-signal routing.
- No unique semantic delta from r8 in this file.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_9/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/mod.rs

Blockdev D-Bus revision registry.

Key behavior:
- Declares blockdev revisions r0 through r9 plus shared helpers.
- Re-exports `BlockdevR0` through `BlockdevR9`.
- `register_blockdev()` creates a unique object path under `/org/storage/stratis3/<counter>`, registers every blockdev revision on that path, logs individual registration failures, and records the path-to-UUID mapping in `Manager`.
- `unregister_blockdev()` removes every revision from zbus, resolves UUID from `Manager`, removes manager mapping, and returns the UUID.

Filesystem/block-storage relevance:
- Ensures one physical block device appears through all supported D-Bus API revisions on a single object path.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/shared.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/blockdev/shared.rs

Shared blockdev D-Bus property helpers.

Key functions:
- `set_blockdev_prop()`:
  - Gets mutable pool by UUID.
  - Applies a caller-provided async mutation closure.
  - Drops the pool guard before signal emission.
  - Emits a caller-provided signal only when the mutation reports a change.
- `blockdev_prop()`:
  - Gets pool by UUID.
  - Gets blockdev by device UUID.
  - Calls a provided property extraction closure with tier, UUID, and blockdev reference.

This centralizes pool lookup, error mapping, and signal-after-unlock behavior for blockdev interfaces.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/blockdev/shared.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/consts.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/consts.rs

D-Bus constants.

Definitions:
- `STRATIS_BASE_PATH = "/org/storage/stratis3"`
- `STRATIS_BASE_SERVICE = "org.storage.stratis3"`
- `OK_STRING = "Ok"`

These constants are shared by manager/object registration and D-Bus result tuple construction.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/consts.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_0/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_0/methods.rs

Filesystem r0 method implementation for renaming.

Key behavior:
- `set_name_method()` gets mutable pool by parent pool UUID.
- Calls `pool.rename_filesystem`.
- Maps `RenameAction` into D-Bus result tuple:
  - `Renamed` returns changed filesystem UUID.
  - `Identity` returns OK unchanged.
  - `NoSource` returns error.
- Sends filesystem name change signal through manager path lookup after a successful rename.
- Uses `handle_action!` for action logging.

This method is reused by later filesystem revisions.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_0/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_0/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_0/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r0`.

Key behavior:
- Defines `FilesystemR0` with engine, connection, manager, parent pool UUID, and filesystem UUID.
- Registers/unregisters this interface on a zbus object path.
- Exposes `SetName` method.
- Exposes properties:
  - `Created`
  - `Devnode`
  - `Name`
  - `Pool`
  - `Size`
  - `Used`
  - `Uuid`

Property reads use shared `filesystem_prop()` and r0 property helper functions.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_0/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_0/props.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_0/props.rs

Property accessors for filesystem D-Bus revisions.

Properties:
- `created_prop`: RFC3339 creation timestamp, seconds precision.
- `devnode_prop`: mountable filesystem path derived from pool and filesystem names.
- `name_prop`: filesystem name.
- `pool_prop`: parent pool object path from manager.
- `size_prop`: filesystem size as string.
- `used_prop`: optional used bytes as `(bool, String)`.
 
These helpers are reused across filesystem revision files.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_0/props.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_1/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_1/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r1`.

Behavior:
- Same surface as r0: `SetName`, `Created`, `Devnode`, `Name`, `Pool`, `Size`, `Used`, `Uuid`.
- Reuses r0 methods and props.
- Registers as a separate revisioned interface on the filesystem object path.

No file-local semantic delta from r0.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_1/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_2/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_2/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r2`.

Behavior:
- Same interface as r1/r0.
- Uses r0 helper implementations for rename and property reads.
- Separate revision name preserves compatibility.

No additional filesystem behavior in this file.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_2/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_3/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_3/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r3`.

Behavior:
- Same filesystem API as r0-r2.
- Retains method-style `SetName`.
- Exposes base properties only.
- Reuses r0 helpers.

No file-local semantic delta from r2.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_3/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_4/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_4/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r4`.

Behavior:
- Same as r3/r0: rename method and base filesystem properties.
- Reuses r0 `set_name_method` and property helpers.
- Separate revisioned zbus interface.

No additional behavior is introduced.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_4/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_5/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_5/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r5`.

Behavior:
- Same as r4: base filesystem properties and `SetName`.
- Uses shared `filesystem_prop()` plus r0 helper functions.
- Maintains compatibility under revision r5.

No unique semantic additions.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_5/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_6/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_6/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r6`.

Changes relative to r0-r5:
- Adds `SizeLimit` property.
- Adds writable setter for `SizeLimit` using shared `set_filesystem_prop()`.
- Emits size-limit change signal only when the value changes.
- Keeps `SetName` and base properties.

This revision introduces filesystem quota/limit control through D-Bus.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_6/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_6/props.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_6/props.rs

Size-limit property helpers for filesystem r6+.

Key behavior:
- `size_limit_prop()` returns optional size limit bytes as `(bool, String)`.
- `set_size_limit_prop()` parses optional string into `devicemapper::Bytes` and calls `pool.set_fs_size_limit`.
- Maps `PropChangeAction::NewValue` to changed, `Identity` to unchanged.
- `send_size_limit_signal_on_change()` resolves filesystem object path from manager and sends D-Bus signal.

This is the mutation backend for the r6 `SizeLimit` property.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_6/props.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_7/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_7/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r7`.

Changes relative to r6:
- Adds `Origin` property for snapshot origin UUID.
- Adds `MergeScheduled` property and writable setter.
- Retains writable `SizeLimit`.
- Retains base properties and `SetName`.

Filesystem relevance:
- Exposes snapshot lineage and deferred merge scheduling through D-Bus.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_7/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_7/props.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_7/props.rs

Snapshot-origin and merge-scheduling helpers for filesystem r7+.

Key behavior:
- `origin_prop()` returns optional origin filesystem UUID as `(bool, uuid_string)`, using nil UUID when absent.
- `merge_scheduled_prop()` reads `fs.merge_scheduled()`.
- `set_merge_scheduled_prop()` calls `pool.set_fs_merge_scheduled` and maps `PropChangeAction` to changed/unchanged.
- `send_merge_scheduled_signal_on_change()` resolves the filesystem object path and emits the property signal.

This backs D-Bus control of snapshot merge scheduling.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_7/props.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_8/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_8/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r8`.

Behavior:
- Carries forward r7 surface:
  - `Origin`
  - writable `MergeScheduled`
  - writable `SizeLimit`
  - base filesystem properties
  - `SetName`
- Uses r0, r6, and r7 helper modules.
- Separate revisioned interface for compatibility.

No file-local semantic delta from r7.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_8/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_9/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_9/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r9`.

Behavior:
- Latest listed filesystem revision in this group.
- Same surface as r8/r7:
  - snapshot origin
  - merge scheduling
  - size limits
  - base properties and rename method
- Uses shared setter helpers to release pool locks before emitting D-Bus signals.

No unique semantic delta from r8 in this file.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_9/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/mod.rs

Filesystem D-Bus revision registry.

Key behavior:
- Declares filesystem revisions r0 through r9 plus shared helpers.
- Re-exports `FilesystemR0` through `FilesystemR9`.
- `register_filesystem()` creates a unique object path, records filesystem UUID in `Manager`, and registers every filesystem revision on that path.
- `unregister_filesystem()` removes manager mapping first, then unregisters every revision from zbus, returning the filesystem UUID.

Filesystem relevance:
- Ensures each Stratis filesystem is exposed through all supported D-Bus API revisions on a single object path.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/shared.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/filesystem/shared.rs

Shared filesystem D-Bus property helpers.

Key functions:
- `set_filesystem_prop()`:
  - Gets mutable pool by UUID.
  - Applies a caller-provided async mutation closure.
  - Drops the lock before sending change signals.
  - Sends signal only when changed.
- `filesystem_prop()`:
  - Gets pool by UUID.
  - Finds filesystem by filesystem UUID.
  - Passes pool name, filesystem name, filesystem UUID, and filesystem reference to an extraction closure.

This centralizes lookup, locking, and signal discipline for filesystem D-Bus properties.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/filesystem/shared.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/macros.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/macros.rs

Defines `handle_action!` macro for D-Bus action logging and availability signaling.

Forms:
- `handle_action!(action)` logs successful actions via `log::info!`.
- `handle_action!(action, connection, manager, pool_uuid)` additionally checks errors for available-action changes and sends action-availability signal for the pool path.

Important details:
- Uses blocking futures executor to read manager and send signal from inside macro context.
- Logs a warning if the pool path cannot be found.
- Used around engine/pool actions to keep D-Bus clients informed when failure changes future valid actions.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/macros.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_0/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_0/methods.rs

Method implementations for manager r0/r1 and shared manager operations.

Key behavior:
- Key handling:
  - `list_keys_method()` lists key descriptions.
  - `set_key_method()` stores key material from an fd and reports created/value-changed/identity.
  - `unset_key_method()` removes key mapping.
- Pool creation:
  - Converts D-Bus optional key/Clevis tuples.
  - Parses Clevis JSON.
  - Uses legacy encryption info and default integrity spec.
  - Calls `engine.create_pool`.
  - Registers pool and child filesystem paths on creation.
- Pool destruction:
  - Resolves pool UUID from object path.
  - Captures blockdev/filesystem UUIDs before destruction.
  - Calls `engine.destroy_pool`.
  - Unregisters blockdevs, filesystems, and pool object.
- Unlock:
  - Parses pool UUID.
  - Calls `engine.unlock_pool`.
  - Emits locked-pools signal on start.
- Report:
  - Serializes `engine.engine_state_report()` to JSON string.

D-Bus style:
- All methods return Stratis D-Bus result tuples with `DbusErrorEnum` code and return string.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_0/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_0/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_0/mod.rs

D-Bus interface `org.storage.stratis3.Manager.r0`.

Exposes:
- Properties:
  - `Version`
  - `LockedPools`
- Methods:
  - `ListKeys`
  - `SetKey`
  - `UnsetKey`
  - `CreatePool`
  - `DestroyPool`
  - `UnlockPool`
  - `EngineStateReport`

Important details:
- Holds engine, connection, manager, and object-path counter.
- `CreatePool` still accepts a `redundancy` argument but does not use it.
- Registers the manager object at `/org/storage/stratis3`.

This is the early top-level D-Bus management API.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_0/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_0/props.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_0/props.rs

Manager r0 property helpers.

Properties:
- `version_prop()` returns `stratis::VERSION`.
- `locked_pools_prop()` returns `engine.locked_pools().await`.

Used by manager r0 and r1.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_0/props.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_1/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_1/mod.rs

D-Bus interface `org.storage.stratis3.Manager.r1`.

Behavior:
- Same method/property surface as manager r0.
- Reuses r0 method and property implementations.
- Registers at the same base path as a separate revisioned interface.
- Keeps `LockedPools` property and `UnlockPool` method.

No file-local semantic delta from r0.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_1/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_2/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_2/methods.rs

Manager r2 pool start/stop/refresh methods.

Key behavior:
- `start_pool_method()`:
  - Parses pool UUID.
  - Converts optional `UnlockMethod` to `TokenUnlockMethod`.
  - Calls `engine.start_pool`.
  - Registers filesystems, then pool/blockdevs, for the started pool.
  - Emits locked-pools signal if encrypted and stopped-pools signal after start.
  - Returns pool path, blockdev paths, and filesystem paths.
- `stop_pool_method()`:
  - Resolves pool UUID from object path.
  - Captures current blockdev/filesystem UUIDs.
  - Calls `engine.stop_pool`.
  - Unregisters filesystem/blockdev paths that disappeared from engine state, even on partial stop/error paths.
  - On stopped/partial, unregisters pool object and emits stopped-pools signal.
  - Emits locked-pools signal when stopped encrypted pool still has unlock info.
  - Distinguishes identity, stopped, partial, and error.
- `refresh_state_method()` calls `engine.refresh_state()`.

Filesystem/block-storage relevance:
- Handles dynamic D-Bus object lifecycle when pools are stopped/started.
- Carefully reconciles partial teardown state with registered object paths.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_2/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_2/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_2/mod.rs

D-Bus interface `org.storage.stratis3.Manager.r2`.

Changes relative to r0/r1:
- Replaces `LockedPools` exposure with `StoppedPools`.
- Adds `StartPool`.
- Adds `StopPool`.
- Adds `RefreshState`.
- Continues to expose key methods, create/destroy pool, version, and engine state report.

Important details:
- `StartPool` returns pool, blockdev, and filesystem object paths.
- `CreatePool` still delegates to r0 method and accepts unused redundancy.
- Registers at the D-Bus base path as another revisioned manager interface.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_2/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_2/props.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_2/props.rs

Manager r2 property helper.

Key behavior:
- `stopped_pools_prop()` returns `engine.stopped_pools().await` wrapped in `dbus::types::ManagerR2`.

This backs the manager r2 `StoppedPools` D-Bus property.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_2/props.rs -->