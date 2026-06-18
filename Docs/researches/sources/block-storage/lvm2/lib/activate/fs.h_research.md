# File Research: sources/block-storage/lvm2/lib/activate/fs.h

## Role

`fs.h` is the private header for activation filesystem fallback operations. It is intended for the activation unit rather than broad library consumers.

## Declared Interface

- `fs_add_lv()` creates the VG directory and LV symlink for a logical volume.
- `fs_del_lv()` removes an LV symlink and possibly the empty VG directory.
- `fs_del_lv_byname()` removes an LV symlink by explicit device directory, VG name, LV name, and udev-check policy.
- `fs_rename_lv()` handles old-to-new LV symlink transitions, including cross-VG rename as delete plus add.
- `fs_ensure_cookie()`, `fs_get_cookie()`, and `fs_set_cookie()` manage the shared udev cookie.
- `fs_set_create()` and `fs_has_non_delete_ops()` expose pending create/non-delete state.
- `fs_unlock()` is intentionally not declared here anymore; the comment notes it moved to `activate.h` to keep this private header hidden.

## Dependency Context

The header includes `lib/metadata/metadata.h`, so the filesystem operations can accept full `struct logical_volume` pointers and derive VG, command context, device directory, and udev settings.

## Invariants

- This header should stay private to activation/backend code; public callers should use activation-level APIs.
- Cookie APIs must remain consistent with `dev_manager.c` tree cookie transfer.
- Link operations assume LV and VG names have already been validated by metadata layers.
