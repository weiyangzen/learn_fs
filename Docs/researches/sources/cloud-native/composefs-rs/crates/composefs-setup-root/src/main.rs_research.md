# sources/cloud-native/composefs-rs/crates/composefs-setup-root/src/main.rs

## Purpose
This binary is an early-boot root filesystem setup tool. It reads the composefs image address from the kernel command line, mounts the composefs root image or a test root filesystem, overlays or bind-mounts mutable subdirectories, preserves old `/sysroot` when present, and replaces the initramfs `/sysroot` with the composed root.

## Important APIs, Types, and Functions
Config types are `MountType`, `RootConfig`, `MountConfig`, and `Config`, parsed from TOML. `Args` defines CLI/test options for command, sysroot path, config path, root-fs override, cmdline override, and target. Helpers include `open_dir()`, `ensure_dir()`, `bind_mount()`, `mount_tmpfs()`, `overlay_state()`, `overlay_transient()`, `open_root_fs()`, `mount_composefs_image()`, `mount_subdir()`, `gpt_workaround()`, `parse_image_address()`, `setup_root()`, and `main()`.

## Control Flow
`main()` parses CLI args, runs `gpt_workaround()` best-effort, then calls `setup_root()`. `setup_root()` reads optional TOML config, opens sysroot, obtains cmdline text, parses a SHA-512 composefs digest first and falls back to legacy SHA-256 on invalid length, then obtains `new_root` either by bind-cloning `--root-fs` or mounting a composefs image from `sysroot/composefs`. It clones the current sysroot, optionally mounts early for `pre-6.15`, optionally overlays the whole root transiently, attempts to mount old sysroot under the new root, opens per-image state under `state/deploy/<image_addr>`, mounts `etc` and `var` according to config/defaults, and on newer kernels detaches and replaces `/sysroot`.

## State and Persistence
Persistent state is outside the binary: composefs repository under sysroot, image-specific state under `state/deploy/<digest>`, overlay `upper` and `work` directories, and `/run/systemd/volatile-root` symlink from the GPT workaround. Transient mode uses tmpfs-backed overlay state. `overlay_state()` intentionally creates `upper` as 0755 so merged directory permissions do not block non-root services.

## Dependencies and Integration Points
The code integrates `rustix` mount/fs syscalls, composefs repository and mount APIs, overlayfs mount compatibility helpers, `composefs_boot::cmdline`, `clap`, `serde`/`toml`, and digest types for SHA-256/SHA-512. It depends on kernel mount API behavior, overlayfs, EROFS/composefs support, and systemd GPT auto-root behavior.

## Risks
Most behavior requires privileges and early-boot filesystem state, so unit coverage is necessarily narrow. Mount sequencing differs by `pre-6.15`; mistakes can leave abandoned mounts or fail to replace sysroot. The `cmd` and `target` args are currently parsed but not used in `setup_root()`, suggesting testing hooks or future behavior may be incomplete. `gpt_workaround()` ignores errors, which is deliberate best-effort behavior but can hide integration issues. The image digest length dispatch assumes SHA-512 is 128 hex and SHA-256 is 64 hex.

## Test Signals
The included test verifies invalid command lines fail, SHA-256 legacy digests still parse, and SHA-512 digests parse and round-trip to hex. Mount, overlay, config, and state behavior are not unit-tested here because they require kernel and privilege conditions.
