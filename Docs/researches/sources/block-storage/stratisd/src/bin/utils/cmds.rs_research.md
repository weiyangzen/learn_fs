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
