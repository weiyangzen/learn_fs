# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_bucket.cc

## Purpose
This file implements RADOS-backed RGW admin REST operations for bucket management. It translates `/admin/bucket` HTTP methods and subresources into `RGWBucketAdminOp` calls, parses request arguments into `RGWBucketAdminOpState`, enforces bucket caps, and handles master-zone forwarding for selected metadata mutations.

## Important APIs, Types, And Functions
- `RGWOp_Bucket_Info` reads bucket information and optional stats/restore stats.
- `RGWOp_Get_Policy` reads bucket or object policy.
- `RGWOp_Check_Bucket_Index` checks or repairs bucket index state and optionally checks objects.
- `RGWOp_Bucket_Link` and `RGWOp_Bucket_Unlink` link/unlink buckets to users or accounts, forwarding to the master first.
- `RGWOp_Bucket_Remove` removes buckets, supports purge and bypass-GC flags, and maps `-ENOENT` to `-ERR_NO_SUCH_BUCKET`.
- `RGWOp_Set_Bucket_Quota` sets per-bucket quota from JSON body, chunked fallback, or HTTP args.
- `RGWOp_Sync_Bucket` toggles bucket sync.
- `RGWOp_Object_Remove` removes one object through bucket admin code.
- `RGWHandler_Bucket::{op_get,op_put,op_post,op_delete}` routes methods and subresources.

## Control Flow
GET dispatches to policy, index check, or bucket info. PUT dispatches to quota, sync, or link. POST unlinks. DELETE removes an object when `object` subresource is present, otherwise removes a bucket. Each operation parses strings/bools/integers from `RESTArgs`, fills `RGWBucketAdminOpState`, and invokes the corresponding admin operation on `driver`. Link and unlink forward the request to the metadata master before applying local admin code. Quota setting chooses JSON input when a body or chunked transfer is present, otherwise loads the current bucket and overlays request parameters on the existing quota.

## State And Persistence Behavior
The file itself does not write RADOS directly; persistence is delegated to `RGWBucketAdminOp` and the SAL driver. The operations can mutate bucket-user/account links, bucket instance metadata, bucket quota fields, bucket sync state, bucket index repair state, object index/data state, and GC scheduling depending on flags. Forwarded requests use site metadata-master logic to keep multisite metadata authoritative.

## Dependencies And Integration Points
It depends on `rgw_op.h`, `driver/rados/rgw_bucket.h`, `rgw_process_env.h`, `rgw_rest_bucket.h`, SAL, zone service, sysobj service, and REST argument helpers. It integrates with the admin caps system through `buckets=read` and `buckets=write`, with `rgw_forward_request_to_master()`, and with `RGWFormatterFlusher` for output.

## Risks And Edge Cases
Quota setting requires both `uid` and `bucket`; missing either returns `-EINVAL`. HTTP-parameter quota updates first load current bucket quota, so load failures abort before mutation. Bucket removal treats forwarded admin requests by checking the `rgwx-zonegroup` system argument rather than only `system_request`. `bypass-gc` is powerful and can remove data without normal GC safety. Index repair can be expensive and optionally object-checking can touch object data.

## Test Signals
Endpoint tests should cover method/subresource dispatch, cap failures, missing required quota arguments, JSON quota and HTTP-argument quota paths, master forwarding failures for link/unlink, bucket removal error mapping, forwarded-zonegroup detection, index check with fix/check-objects flags, and object removal routing.
