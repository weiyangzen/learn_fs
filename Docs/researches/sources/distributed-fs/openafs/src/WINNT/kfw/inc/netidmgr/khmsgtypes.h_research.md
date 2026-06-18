# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khmsgtypes.h

## Purpose

`khmsgtypes.h` defines the standard NetIDMgr KMQ message type IDs and subtypes. It is the protocol map for system lifecycle events, credential database notifications, module manager coordination, credential acquisition, action updates, alert delivery, and identity-provider requests.

## Important APIs, Types, and Functions

- Global message types: `KMSG_SYSTEM`, `ADHOC`, `KCDB`, `KMM`, `CRED`, `ACT`, `ALERT`, `IDENT`, and user-defined types at `KMSGBASE_USER`.
- System subtypes: init, exit, and completion.
- KCDB subtypes: identity, credential type, attribute, type, and credential request.
- KMM subtypes: internal register and done.
- Action subtypes: enable, check, refresh, new, delete, activate, and command-line/config-sync internals.
- Credential subtypes: root delta, refresh, password, new, renew, dialog setup/prestart/start, identity/options changes, process, end, import, destroy, property-page lifecycle, and address-change.
- `IS_CRED_ACQ_MSG(msg)` checks whether a credential subtype is in the acquisition/dialog range 16..31.
- Alert subtypes map to showing, queueing, showing queued, checking queue, and modal display.
- Identity subtypes drive provider lifecycle, name validation/canonicalization/comparison, default/searchable flags, info, enumeration, update, UI callback lookup, and creation notification.

## Control Flow

KMQ publishers use these constants with `kmq_post_message`, `kmq_send_message`, or subscription-specific send/post functions. Credential acquisition is a multi-stage sequence: providers respond to password/new/renew by adding `khui_new_creds_by_type` participants, then UI drives setup, prestart, start, process, and end messages. Identity-provider messages are often sent to a specific subscription rather than broadcast. Alert messages carry held `khui_alert` pointers and are consumed by the notifier/UI. Property-sheet messages let credential providers add pages before and after the sheet is displayed.

## State and Persistence Behavior

The header is a static protocol contract. Runtime state lives in KMQ queues (`kmq.h`), credential blobs (`khnewcred.h`), property sheets (`khprops.h`), alert objects (`khalerts.h`), and KCDB identity/credential objects (`kcreddb.h`). Message values must remain stable because plugins and import libraries compiled against this header use them as ABI.

## Dependencies and Integration Points

This header is included by `khuidefs.h` and referenced by KMQ, KMM, KCDB, UI actions, alerts, new credentials, property sheets, and identity providers. The OpenAFS NetIDMgr plugin under `src/WINNT/netidmgr_plugin` uses these protocol values through the public headers to participate in AFS credential acquisition and configuration.

## Risks and Edge Cases

- Typographical documentation errors do not affect ABI but can mislead plugin authors; message parameter names must be checked against structures.
- `IS_CRED_ACQ_MSG` includes `KMSG_CRED_PROCESS` and `KMSG_CRED_END` even though they are not strictly dialog-only.
- Some messages are explicitly not for broadcast, especially plugin-originated dialog identity/options messages.
- Held-pointer ownership is message-specific; alert messages release held alert objects at completion/queue display.
- Numeric ranges are manually allocated, so new subtypes must avoid collisions with internal blocks.

## Test Signals

- Run message-sequence tests for credential acquisition from initial request through end, including dependency ordering.
- Verify identity-provider messages are routed to the intended subscription and not broadcast accidentally.
- Send action state changes and confirm menus/toolbars update through `KMSG_ACT_*`.
- Queue and display alerts through `KMSG_ALERT_*`.
- Confirm KMQ completion handlers clean up message payloads for each standard message class.
