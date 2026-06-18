# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khhtlink.h

## Purpose

`khhtlink.h` defines the data payload passed when a user clicks a link inside a NetIDMgr hypertext window. It gives consumers rectangle, identifier, and parameter slices without forcing null-terminated strings.

## Important APIs, Types, and Functions

- `khui_htwnd_link` contains a Win32 `RECT`, an `id` pointer plus `id_len`, and a `param` pointer plus `param_len`.
- `KHUI_MAXCCH_HTLINK_FIELD` limits link ID or parameter fields to 256 wide characters.
- `KHUI_MAXCB_HTLINK_FIELD` is the corresponding byte count.

## Control Flow

The hypertext control parses markup, tracks link rectangles, and sends this structure to a window or panel when a link is activated. Consumers inspect the non-null-terminated `id` and optional `param` slices and then dispatch an action, such as switching a new-credentials panel through `CTLINKID_SWITCH_PANEL` in `khnewcred.h`.

## State and Persistence Behavior

The structure is an event payload, not an owner. The `id` and `param` pointers reference parser/control buffers and must be copied if needed after the notification returns. The rectangle is useful for hit testing, invalidation, or context positioning during the current UI event.

## Dependencies and Integration Points

The header depends on Win32 `RECT` and wide strings. It is included by `khuidefs.h` and integrates with new-credentials credtext links (`WMNC_CREDTEXT_LINK`) and any alert/config text controls that embed clickable spans.

## Risks and Edge Cases

- The fields are not null-terminated. Treating them as C strings can read past the slice.
- Lengths are `int`; callers should validate nonnegative lengths before copying.
- Pointers are mutable `wchar_t *` but should be treated as read-only unless the owning control explicitly allows mutation.
- Field limits are per field, not per rendered line or complete markup.

## Test Signals

- Click links with ID only, ID plus parameter, maximum-length fields, and adjacent links.
- Verify consumers compare by length-aware functions, not `wcscmp`.
- Test panel switching links in new-credentials credtext and ensure out-of-range ordinals are rejected.
