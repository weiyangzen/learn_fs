# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khnewcred.h

## Purpose

`khnewcred.h` declares the data model and helper API for NetIDMgr credential acquisition dialogs. It coordinates core UI, identity providers, and credential provider plugins during password change, new credential, and renewal workflows.

## Important APIs, Types, and Functions

- `KHUI_WM_NC_NOTIFY` is the notification message sent to new-credentials windows and panels.
- Control ID range `KHUI_CW_ID_MIN` through `KHUI_CW_ID_MAX` reserves up to eight controls for identity-provider UI.
- `khui_wm_nc_notifications` defines dialog expansion, setup, activation, movement, panel switching, credtext updates/link clicks, identity change, prompt clearing/setting, preprocess/process/completion, type state, and internal control-row addition.
- Identity callback `khui_ident_new_creds_cb` receives `WMNC_IDENT_INIT`, `WMNC_IDENT_WMSG`, and `WMNC_IDENT_EXIT`.
- `khui_new_creds` stores request subtype, critical section, default-identity flag, identity list, launch action context, UI mode, window handle, participating credential types and subscriptions, result, response, password, prompt/banner fields, identity callback, window title, and provider auxiliary data.
- `khui_new_creds_by_type` describes a participating credential type: dependencies, ordinal, localized name/icon/tooltip, dialog resource/proc, panel handle, credtext, and plugin aux field.
- Response flags describe exit/no-exit, success/failure/pending/completed/processing.
- `khui_new_creds_prompt` describes custom prompts with type, prompt/default/value strings, hidden/stock flags, and associated controls.
- Public helpers create/destroy blobs, lock/unlock, add/delete/find/enable types, set primary/additional identities, manage prompts, get prompt values, set type response, query dependency success, and add identity-provider control rows.

## Control Flow

The UI creates a `khui_new_creds` blob and sends a credential message such as `KMSG_CRED_NEW_CREDS`, `PASSWORD`, or `RENEW_CREDS`. Interested credential providers add `khui_new_creds_by_type` structures with `khui_cw_add_type()` and list dependencies. The UI creates panels during dialog setup, activates the identity provider callback, then sends dialog-stage messages. When processing begins, plugins inspect identities and prompt values, obtain or renew credentials, and call `khui_cw_set_response()` for their type. Pending/no-exit responses keep the dialog alive and can install custom prompts. Completion and `KMSG_CRED_END` allow providers to remove by-type structures and clean plugin-owned memory.

## State and Persistence Behavior

The credential blob is mutable shared state protected by a `CRITICAL_SECTION`. Plugin-supplied `khui_new_creds_by_type` blocks are not copied; they must survive until removed or until the blob is destroyed. Identities are handles owned by the operation list. Prompt values are periodically synchronized from controls and must be refreshed with `khui_cw_sync_prompt_values()` before reading. Actual credential persistence occurs in provider implementations and credential stores; this header only models the UI transaction and responses.

## Dependencies and Integration Points

The header depends on Windows UI types, `khui_action_context` from `khaction.h`, KCDB identity and credential type handles from `kcreddb.h`, KMQ credential messages from `khmsgtypes.h`, and link payloads from `khhtlink.h`. The OpenAFS NetIDMgr plugin files (`afsnewcreds.c`, `afscred.h`, and related config files) use this contract to add AFS credential UI and process AFS token acquisition.

## Risks and Edge Cases

- By-type structures are stored by reference. Stack allocation or early free by a plugin causes dangling UI pointers.
- Dependency handling relies on providers declaring dependencies before processing; otherwise `khui_cw_type_succeeded()` can be queried before a dependency ran.
- Prompt begin/add is all-or-nothing: fewer added prompts than requested means no prompts are displayed.
- Password and prompt buffers have fixed wide-character limits; providers must handle truncation and size errors.
- `KHUI_WM_NC_NOTIFY` shares its numeric value with `KHUI_WM_CFG_NOTIFY`; dialog class/context must disambiguate.
- Identity callback runs in the UI thread and must not block.

## Test Signals

- Simulate new, renew, and password-change flows with multiple provider types and dependencies.
- Verify type add/delete reference lifetime and duplicate type rejection.
- Exercise pending prompt loops, hidden password prompts, sync before read, and boundary-sized prompt values.
- Change primary identity and confirm additional identities are cleared plus panels receive `WMNC_IDENTITY_CHANGE`.
- Test dependency failure propagation and response masks for exit/no-exit, pending, failed, and completed states.
