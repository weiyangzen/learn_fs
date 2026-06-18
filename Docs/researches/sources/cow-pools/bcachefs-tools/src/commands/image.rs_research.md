# File Research: sources/cow-pools/bcachefs-tools/src/commands/image.rs

## Purpose
Implements `bcachefs image` subcommands for creating and updating compact bcachefs filesystem images from directory trees. It uses a temporary metadata device so user data can be written sequentially to the primary image, then migrates metadata back and optionally strips allocation information for small read-only images.

## Main Interfaces
- Command group export: `CMD`
- Subcommands:
  - `CMD_CREATE = raw_cmd!("create", ...)`
  - `CMD_UPDATE = typed_cmd!("update", ...)`
- Key functions:
  - `cmd_image_create`
  - `cmd_image_update`
  - `image_create_inner`
  - `image_update_inner`
  - `finish_image`
  - `move_btree`
  - `print_image_usage`

## Behavior
- `image create` manually parses format, filesystem, device, encryption, label, UUID, version, force, quiet, verbose, and source options.
- Creates two devices: the primary image for user data and a temporary `.metadata` image for journal/btree metadata.
- Formats the filesystem with device data-allowed masks so data and metadata are segregated.
- Copies a source directory into the filesystem with `copy_fs`.
- Finishes by moving btree nodes to the primary image, reading usage, truncating the image to used buckets, removing the temporary device from the superblock, enabling journal on primary, marking resize-on-mount, and setting `BCH_FEATURE_small_image`.
- `image update` grows an existing image, adds a temporary metadata device, moves btrees to it, deletes xattrs, copies source content, then runs the same finishing path.
- Supports encrypted images, passphrase files, `--no_passphrase`, explicit format version, UUID, labels, replicas, and deferred options requiring an open filesystem.
- Defaults image format version to the minimum of tool current version and loaded kernel bcachefs metadata version when the kernel reports one.

## Dependencies and Coupling
- Uses `format_util::format` and `format_for_device_add`.
- Uses `copy_fs::{CopyFsState, copy_fs}` for directory-tree import/update.
- Uses `MovingContext::move_data_btree` and a C-compatible predicate to migrate btree nodes.
- Uses disk accounting wrappers and raw C accounting printers for image usage reports.
- Uses `strip_fs_alloc` external C symbol for allocation-info stripping during `finish_image`.
- Uses `DevOpts`, bdev wrappers, superblock field resizing, and raw bcachefs superblock mutation.

## Important Implementation Notes
- `count_input_size` recursively sums allocated blocks and skips `lost+found`.
- Temporary metadata devices are removed from the filesystem view by setting `(*fs.raw).devs[1] = null_mut()` and shrinking `members_v2` to one member.
- `finish_image` calls `fs.read_only()` before deriving final bucket usage and truncating.
- Compression and replicas accounting are printed through `Printbuf`.
- Update mode deletes xattrs because they will be recreated from the source tree.
- Both create and update use a 64 MiB minimum temporary metadata size to ensure enough journal capacity.

## Risks and Edge Cases
- Several superblock and device-array mutations are raw and layout-sensitive.
- `fs_opt_strs.set` stores pointers to temporary `CString`s in a loop; correctness depends on `set` copying or owning the string.
- Cleanup on create failure removes all `device_paths`, including the primary image.
- Update mode grows the destination image before later operations; failures after growth may leave the file enlarged.
- The fixed assumption that temporary metadata is device index `1` is central to finishing.
