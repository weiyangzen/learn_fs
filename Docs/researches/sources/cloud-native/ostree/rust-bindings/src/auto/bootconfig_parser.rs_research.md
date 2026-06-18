# sources/cloud-native/ostree/rust-bindings/src/auto/bootconfig_parser.rs

Purpose: Generated wrapper for `OstreeBootconfigParser`, the object used to parse, mutate, and write bootloader entry style configuration.

Important APIs: `new`, `clone`, `get`, `set`, `parse`, `parse_at`, `write`, `write_at`, `tries_done`, `overlay_initrds`/`set_overlay_initrds` behind `v2020_7`, and `tries_left` behind `v2025_2`.

Control flow and state: Parser instances hold key/value bootconfig state in the underlying GObject. `parse`/`parse_at` load config from a `gio::File` or directory fd/path pair. `write`/`write_at` persist current state. Methods follow the GLib error convention and assert error/null consistency in debug builds.

Dependencies and integration points: Depends on Gio files/cancellables, GLib string/vector conversions, and deployment bootconfig APIs. It integrates with `Deployment::bootconfig` and sysroot bootloader entry management.

Risks: File-descriptor based `parse_at`/`write_at` depend on caller-provided directory fd correctness. Version-gated boot counting fields must match installed libostree. The wrapper does not validate arbitrary keys or values.

Test signals: Parse/write round trips, `parse_at`/`write_at` with temporary dirs, overlay initrd round trips under `v2020_7`, and boot-counting field tests under relevant features.
