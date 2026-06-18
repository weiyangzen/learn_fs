# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khprops.h

## Purpose

`khprops.h` declares NetIDMgr property-sheet support for identities, credential types, and individual credentials. It wraps Win32 `PROPSHEETHEADER`/`PROPSHEETPAGE` with action context and credential metadata so the core and plugins can contribute pages.

## Important APIs, Types, and Functions

- `khui_property_sheet` contains a `PROPSHEETHEADER`, status, sheet and active-page HWNDs, launch `khui_action_context`, optional identity, credential type, credential handle, page count, and a queue of pages.
- Sheet statuses are `NONE`, `RUNNING`, `DONE`, and `DESTROY`.
- `KHUI_PS_MAX_PSP` caps sheets at 16 pages.
- `khui_property_page` stores the Win32 page handle, caller-supplied page template pointer, page window handle, owning credential type, ordinal, and list links.
- Pseudo credential types `KHUI_PPCT_IDENTITY` and `KHUI_PPCT_CREDENTIAL` represent built-in identity and credential pages.
- APIs create a sheet, add/find pages, show/check/destroy the sheet, and associate a property-window record with `khui_property_wnd_set_record()`.

## Control Flow

The NetIDMgr application creates a sheet for a selected action context, then sends property-page KMQ messages so plugins can add pages before the sheet is visible. `khui_ps_add_page()` orders pages by ordinal and credential type metadata before `khui_ps_show_sheet()` creates the Win32 sheet. While running, the message loop passes messages to `khui_ps_check_message()` so modeless property-sheet accelerators and notifications are handled. After completion, the application destroys the sheet and page records.

## State and Persistence Behavior

The sheet owns page records but not necessarily caller-supplied `LPPROPSHEETPAGE` memory until creation; the header states that `ppage` must exist until status becomes `RUNNING`. Sheet status and HWND fields describe runtime UI state. Associated identity/credential handles provide context but their ownership is implementation-specific and must be held while the sheet is live. Property changes are persisted by page dialog procedures or providers, not by the wrapper itself.

## Dependencies and Integration Points

The header depends on Win32 property sheet types and `khui_action_context`. It integrates with `KMSG_CRED_PP_BEGIN`, `PRECREATE`, `END`, and `DESTROY` from `khmsgtypes.h`; KCDB identity/credential handles; and plugin-provided property pages for credential providers.

## Risks and Edge Cases

- Page limit is fixed at 16; additional provider pages should fail cleanly.
- `LPPROPSHEETPAGE` is not managed until page creation, so stack or short-lived descriptors are unsafe.
- Pages can only be added before the sheet is visible; late additions should be rejected.
- Ordering by credential type name is undefined if type metadata is unavailable.
- Sheet destroy status must guard against reentrancy from page callbacks.

## Test Signals

- Add identity, credential, and provider pages with ordinals at boundary values and confirm ordering.
- Try to add pages after `RUNNING` and past `KHUI_PS_MAX_PSP`.
- Drive modeless message handling through `khui_ps_check_message()`.
- Verify `KMSG_CRED_PP_*` message order and plugin cleanup on destroy.
