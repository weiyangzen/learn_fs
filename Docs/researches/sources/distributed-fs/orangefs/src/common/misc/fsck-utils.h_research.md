<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/fsck-utils.h -->
# sources/distributed-fs/orangefs/src/common/misc/fsck-utils.h

Purpose: declares the fsck utility API for validating PVFS object types and optional filesystem-wide checks. It is intended for driver programs that have already initialized the PVFS system interface.

Important type: `struct PINT_fsck_options` controls behavior: `fix_errors`, `check_stranded_objects`, `check_symlink_target`, `check_dir_entry_names`, `verbose`, `check_fs_configs`, and `start_path`.

Important APIs: initialization/finalization are `PVFS_fsck_initialize()` and `PVFS_fsck_finalize()`. Validation entry points cover datafiles, metafiles, symlinks, dirdata, directories, directory entries, and attributes. `PVFS_fsck_get_attributes()` wraps object attribute retrieval. `PVFS_fsck_check_server_configs()` verifies server config consistency.

State behavior: options are caller-owned and read by validation functions. The implementation may allocate process-global stranded-object tracking state when requested. No repairs are currently declared beyond the TODO; `fix_errors` is present but not implemented by the C file.

Dependencies include PVFS internal/system/management headers, cached config, and sysint utilities. Integration points include fsck command-line tools or administrative diagnostics.

Risks: `PVFS_fsck_validate_dir()` takes a `PVFS_dirent *directory_entries` output buffer without a length parameter, so callers must size it according to directory size or risk overflow. The API returns negative PVFS errors but may also use warnings encoded through `set_return_code()`. Tests should validate each option flag, object type mismatch handling, and caller buffer sizing assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/fsck-utils.h -->
