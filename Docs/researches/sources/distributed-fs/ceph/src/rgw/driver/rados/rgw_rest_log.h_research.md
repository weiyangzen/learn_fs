# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_log.h

## Purpose
This header declares the admin REST operation classes for RGW metadata, bucket index, and data logs, plus the REST handler and manager that dispatch log requests.

## Important APIs, Types, And Functions
- `RGWOp_BILog_List`, `Info`, and `Delete` expose bucket-index log list/info/trim behavior and require `bilog` read or write caps.
- `RGWOp_MDLog_List`, `Info`, `ShardInfo`, `Lock`, `Unlock`, `Notify`, and `Delete` expose metadata-log operations and require `mdlog` caps.
- `RGWOp_DATALog_List`, `Info`, `ShardInfo`, `Notify`, `Notify2`, and `Delete` expose data-log operations and require `datalog` caps.
- `RGWHandler_Log` routes GET, DELETE, and POST to the correct log operation and lets each operation enforce permissions.
- `RGWRESTMgr_Log::get_handler()` constructs the authenticated log handler.

## Control Flow
The classes store response state such as entries, markers, truncation flags, log info, notify payloads, and sync format version. Concrete `execute()` and `send_response()` implementations in `rgw_rest_log.cc` parse request arguments, call the relevant service, and serialize JSON responses.

## State And Persistence Behavior
The header itself does not persist state, but the declared operations map to persistent mdlog, bilog, datalog, log-lock, and sync-status objects. Notify operations affect in-memory sync scheduling rather than direct persistence.

## Dependencies And Integration Points
It depends on datalog, REST/S3 auth, metadata, mdlog, and data sync headers. It is intentionally lighter than the `.cc` for some status operations, which are declared locally in the implementation to avoid pulling heavier sync headers into this header.

## Risks And Edge Cases
The operation classes expose `verify_permission()` methods that directly call caps on `s->user`; tests must ensure `s->user` is initialized for all log routes. Adding new routes requires matching both handler dispatch and cap checks. `RGWOp_BILog_List` maintains streaming response state (`sent_header`), so response methods must be called in the expected order.

## Test Signals
Header-level coverage should compile all operation classes, verify their `name()` strings and operation types for notify operations, and exercise handler dispatch through the public method overrides.
