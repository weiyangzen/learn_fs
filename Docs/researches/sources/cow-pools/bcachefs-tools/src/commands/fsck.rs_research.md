# File Research: sources/cow-pools/bcachefs-tools/src/commands/fsck.rs

## Purpose
Implements `bcachefs fsck`, covering online fsck against mounted filesystems, in-kernel offline fsck, and userspace offline fsck fallback. It builds the fsck mount-option set, decides whether kernel fsck is required based on metadata-version compatibility, discovers all members of a multi-device filesystem, and splices interactive fsck I/O between the kernel-provided fd and the terminal.

## Main Interfaces
- CLI struct: `FsckCli`
- Command export: `CMD = typed_cmd!("fsck", ...)`
- Key handlers:
  - `cmd_fsck`
  - `fsck_online`
  - `run_userspace_fsck`
  - `should_use_kernel_fsck`
  - `splice_fd_to_stdinout`

## Behavior
- `-p`/`-a` auto-repair exits successfully immediately, matching system fsck behavior where no interactive check is needed.
- Builds default options: `degraded`, `fsck`, `fix_errors=ask`, `read_only`, and `noreconcile_enabled`.
- Omits the default `fsck` option if the user explicitly supplies `recovery_passes`, so the requested pass set is not widened by kernel defaults.
- Applies `-y`, `-n`, `--ratelimit_errors`, `-v`, and extra `-o` options by appending mount options.
- Runs online fsck when the only target is a directory/mountpoint or when any supplied device is detected as mounted through sysfs.
- For a single offline device, scans superblocks to expand to the full member-device list.
- Uses kernel offline fsck when explicitly requested or when userspace and kernel metadata versions make kernel fsck preferable.
- For non-block-device image paths, allocates temporary loop devices with `losetup --show -f` for kernel offline fsck.
- Falls back to userspace fsck if kernel offline setup fails and the user did not explicitly force kernel mode.

## Dependencies and Coupling
- Uses ioctl constants for `BCH_IOCTL_FSCK_OFFLINE` and `BCH_IOCTL_FSCK_ONLINE`.
- Uses `BcachefsHandle` for online fsck handles.
- Uses `device_scan::scan_sbs` and `device_scan::open_scan` for member discovery and userspace opening.
- Uses `find_multipath_holder` and `warn_multipath_component` to warn about multipath component devices.
- Uses `Fs::open` and superblock version data to choose kernel vs userspace fsck.
- Uses `Printbuf` for metadata-version messages and fsck error output.

## Important Implementation Notes
- `splice_fd_to_stdinout` switches stdin and the fsck fd to nonblocking mode and polls both directions, so kernel fsck can ask questions interactively.
- The kernel fsck fd’s close return value is treated as the fsck exit status.
- The offline ioctl payload is manually allocated because the C struct has a flexible array member for device pointers.
- CString lifetimes are preserved in `c_devs` while the ioctl is issued.
- Loop devices are freed before result handling after the ioctl call.

## Risks and Edge Cases
- `setnonblocking` unwraps `fcntl` calls; failure panics.
- `is_blockdev` returns `true` on metadata errors, so missing or inaccessible paths are treated as block devices until later failure.
- The manual flexible-array allocation assumes 8-byte alignment and bindgen layout compatibility.
- Kernel/user metadata-version selection is subtle and should be kept aligned with upstream bcachefs compatibility policy.
