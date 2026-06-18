# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-readdir.c

## Purpose

`metadisp-readdir.c` routes directory reads through the metadata child while requesting enough stat data for callers such as NFS.

## Important APIs, Types, and Functions

Functions are `metadisp_readdir` and `metadisp_readdirp`.

## Control Flow

Both fops ensure an xdata dict exists, set `stat-source-of-truth` to the metadisp translator pointer, and wind `readdirp` to `METADATA_CHILD`. Even plain `readdir` is converted to `readdirp` so entry types and stat fields are initialized.

## State and Persistence Behavior

No state is persisted. The xdata hint tells lower layers how to source stat information while merging metadata and data views.

## Dependencies and Integration Points

The file depends on metadata child readdirp behavior and metadisp stat handling for the `stat-source-of-truth` convention. It also relies on dict allocation and static pointer storage.

## Risks and Edge Cases

When xdata is newly allocated it is not unrefed in this function after winding, so ownership expectations must be confirmed. `dict_set_static_ptr` return is stored in an unused variable, so failure to set the hint does not alter control flow. Always issuing readdirp may be more expensive than readdir.

## Test Signals

Tests should cover NFS-style readdir requiring type data, readdirp xdata propagation, dict allocation failure behavior, and stat-source-of-truth integration with `metadisp_stat`.
