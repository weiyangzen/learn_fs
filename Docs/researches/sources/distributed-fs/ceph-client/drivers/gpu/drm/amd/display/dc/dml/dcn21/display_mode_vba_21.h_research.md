# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_mode_vba_21.h

## Purpose

This header is the public DCN 2.1 Display Mode Library VBA interface. It exposes the two entry points implemented in `display_mode_vba_21.c` so the common DML library can bind DCN 2.1 validation and recalculation callbacks.

## Important APIs and types

The header declares:

- `void dml21_recalculate(struct display_mode_lib *mode_lib);`
- `void dml21_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib);`

It does not define `struct display_mode_lib`; users are expected to include it in a context where the core DML headers have already declared the type. The include guard is `__DML21_DISPLAY_MODE_VBA_H__`.

## Control flow and integration

The header itself has no executable control flow. It is included by the DCN 2.1 implementation and by the common DML dispatch setup. In `display_mode_lib.c`, these functions populate the DCN 2.1 function table entries for `.validate` and `.recalculate`.

`dml21_ModeSupportAndSystemConfigurationFull()` is the full mode-validation/state-selection entry point. `dml21_recalculate()` is the recalculation path for a chosen state. Both operate on the mutable `mode_lib->vba` state block owned by the caller.

## State and persistence behavior

The header stores no state and declares no globals. State changes happen only through the implementation functions and the passed `struct display_mode_lib *`.

## Dependencies

This file has no direct includes besides its guard. Its declarations depend on `struct display_mode_lib` being visible to translation units that include it, usually through `display_mode_lib.h` or neighboring DML headers included first.

## Risks and edge cases

- Because the header does not include or forward-declare `struct display_mode_lib`, include order matters. In-tree usage appears to satisfy that ordering, but standalone inclusion would trigger compiler diagnostics.
- The closing comment uses `_DML21_DISPLAY_MODE_VBA_H_`, which differs from the actual guard macro `__DML21_DISPLAY_MODE_VBA_H__`; this is cosmetic but can confuse readers.
- Any signature change must be coordinated with `display_mode_lib.c` callback binding and all DCN 2.1 callers.

## Test signals

Relevant checks are compile-time rather than runtime:

- Build the DML objects that include this header.
- Confirm `display_mode_lib.c` resolves `dml21_ModeSupportAndSystemConfigurationFull` and `dml21_recalculate` for the DCN 2.1 function table.
- Confirm no standalone or reordered include path relies on this header to define `struct display_mode_lib`.
