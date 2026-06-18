# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp.h

## Purpose

`metadisp.h` defines the shared macros and helper prototype used by all metadisp source files.

## Important APIs, Types, and Functions

Macros `METADATA_CHILD(this)` and `DATA_CHILD(this)` identify child roles. `build_backend_loc` is declared for GFID path rewriting. `METADISP_TRACE` wraps `gf_log`. `METADISP_FILTER_ROOT` and `METADISP_FILTER_ROOT_BY_GFID` route root operations directly to metadata. `RESOLVE_GFID_REQ` validates extraction of `gfid-req` from a dict.

## Control Flow

The filter macros inject early-return control flow into fops. Root-path or root-GFID operations are wound to metadata with the default callback and return immediately.

## State and Persistence Behavior

No state is stored here. The macros define routing behavior based on translator child topology and request loc/GFID values.

## Dependencies and Integration Points

It includes Gluster logging and dict headers and assumes core xlator macros such as `FIRST_CHILD`, `SECOND_CHILD`, `STACK_WIND`, and `default_*_cbk` are available through included Gluster headers.

## Risks and Edge Cases

The macros reference local variables such as `frame`, `this`, and `loc`, so misuse in a different lexical context can fail compile or route incorrectly. `RESOLVE_GFID_REQ` assumes xdata is non-null and jumps to a caller-provided label on failure.

## Test Signals

Compile coverage for each macro use, root operation tests, create with missing `gfid-req`, and child ordering tests validate this header's integration.
