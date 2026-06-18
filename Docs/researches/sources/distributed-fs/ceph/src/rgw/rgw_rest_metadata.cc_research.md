# sources/distributed-fs/ceph/src/rgw/rgw_rest_metadata.cc

## Purpose

`rgw_rest_metadata.cc` implements authenticated admin REST access to RGW metadata entries. It supports listing metadata keys, reading entries, writing entries with sync-apply modes, deleting entries, and the special `myself` lookup.

## Important APIs and Functions

`frame_metadata_key()` builds the metadata key from the URL bucket/init-state section and the `key` query arg. Operations implemented are `RGWOp_Metadata_Get`, `RGWOp_Metadata_Get_Myself`, `RGWOp_Metadata_List`, `RGWOp_Metadata_Put`, and `RGWOp_Metadata_Delete`. `RGWHandler_Metadata` dispatches GET to list/get/myself, PUT to write, and DELETE to remove.

`RGWOp_Metadata_Put::get_data()` reads fixed-length or chunked request bodies into a bufferlist. `string_to_sync_type()` maps `update-type` strings to `RGWMDLogSyncType`.

## Control Flow

GET with `myself` appends the authenticated owner id as `key` and reuses normal get. GET with `key` calls the metadata manager's `get()`. GET without `key` decodes an optional base64 marker, parses optional `max-entries`, initializes metadata listing, loops through `meta_list_keys_next()`, and emits either legacy `keys` output or an extended response with truncation/count/marker.

PUT reads the body, completes AWS4 auth after body read, frames the metadata key, parses `update-type` (`update-by-version`, `update-by-timestamp`, or `always`), and calls the RADOS metadata manager `put()`. `send_response()` maps internal apply/skipped statuses to 204 and emits `RGWX_UPDATE_STATUS` and `RGWX_UPDATE_VERSION` headers. DELETE frames the metadata key and calls metadata manager `remove()`.

## State and Persistence Behavior

GET/list are read-only. PUT and DELETE mutate RADOS-backed RGW metadata through `static_cast<rgw::sal::RadosStore*>(driver)->ctl()->meta.mgr`. PUT persists the new metadata blob and records the on-disk object version returned by the metadata manager. The sync type controls whether incoming metadata is always applied, only newer by timestamp, or by version.

## Dependencies and Integration Points

This file depends on RADOS SAL metadata control, mdlog sync types, request body I/O, base64 marker encoding, strict integer parsing, and AWS auth completion. It is used by admin tools and multisite metadata synchronization flows.

## Risks and Edge Cases

The implementation assumes a RADOS store via static cast. `get_data()` manually allocates request buffers and relies on `s->length` or exact `HTTP_TRANSFER_ENCODING == "chunked"`. In list mode, errors before `meta_list_keys_complete()` can leak the listing handle because early returns bypass completion. Base64 marker decode catches all exceptions and silently resets the marker. `max-entries` is parsed with `strict_strtol()` then cast to unsigned.

## Test Signals

Tests should cover key framing from URL bucket plus `key`, `myself`, fixed and chunked PUT bodies, missing length errors, AWS4 body auth completion, all update-type modes, update status/version headers, list legacy versus extended response formats, base64 marker round trips, delete behavior, cap enforcement, and handle cleanup on listing failures.
