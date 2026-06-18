# sources/distributed-fs/ceph/src/rgw/rgw_rest_restore.cc

## Purpose

`rgw_rest_restore.cc` implements REST operations for inspecting RGW object restore state. It supports status for a single object and listing restore entries for a bucket, with optional status filtering. The actual restore backend behavior is delegated to `driver->get_rgwrestore()`.

## Important APIs, types, and functions

- `RGWOp_Restore_Status` requires `buckets=read` caps and handles `GET` requests with an `object` subresource argument. It builds a `rgw::restore::RestoreEntry` with bucket and object key and calls `status()`.
- `RGWOp_Restore_List` also requires `buckets=read` caps and handles bucket-level restore listing. It optionally reads `restore-status-filter` and passes it as `std::optional<std::string>` to `list()`.
- `RGWHandler_Restore::op_get()` dispatches between status and list based on whether `s->info.args.sub_resource_exists("object")`.

## Control flow

For object status, the operation reads `bucket`, `tenant`, and `object` query arguments, fills `RestoreEntry::bucket` and `RestoreEntry::obj_key`, and calls `driver->get_rgwrestore()->status()` with the operation as prefix provider, the entry, request error message string, response flusher, and yield context.

For bucket listing, the operation reads `bucket`, `tenant`, and optionally `restore-status-filter`. It sets only the bucket field on `RestoreEntry`, converts the filter into an optional only when present, then calls `driver->get_rgwrestore()->list()` with the same error-message and flusher integration. The handler makes the list path the default `GET`; object status is selected only by the `object` subresource.

## State and persistence behavior

This file does not mutate restore state. It constructs lookup/list keys and delegates all persistence reads to the restore service returned by `driver->get_rgwrestore()`. Output streaming is handled by the restore service through the provided `flusher`, and detailed error text can be written into `s->err.message`.

## Dependencies and integration points

The implementation depends on `rgw_rest_restore.h` for handler declarations and `rgw_restore.h` for `rgw::restore::RestoreEntry` and restore service APIs. It also uses `RESTArgs`, `rgw_bucket`, `rgw_obj_key`, SAL driver access, operation caps, and RGW response flushing.

## Risks and edge cases

- The code performs no local validation that `bucket` or `object` is non-empty. It relies on the restore service to reject invalid entries.
- Dispatch depends on `sub_resource_exists("object")`, while `execute()` reads the string value of `object`; unusual query forms such as empty `object` subresource need backend coverage.
- Both operations require broad `buckets` read caps rather than a restore-specific cap.
- Error formatting is delegated to the restore service, so response shape consistency depends on that backend.

## Test signals

Tests should cover `GET` bucket restore list, list with `restore-status-filter`, object status with tenant and bucket, empty or missing bucket/object arguments, backend `status()` and `list()` error propagation into `op_ret` and `s->err.message`, cap enforcement, and handler dispatch based on the presence of the `object` subresource.
