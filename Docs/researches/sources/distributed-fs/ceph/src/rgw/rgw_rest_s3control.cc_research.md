# sources/distributed-fs/ceph/src/rgw/rgw_rest_s3control.cc

## Purpose
`rgw_rest_s3control.cc` implements the currently registered S3Control account-level public access block API under `/v20180820/configuration/publicAccessBlock`. It supports GET, PUT, and DELETE of `PublicAccessBlockConfiguration` on RGW account metadata.

The file also contains retry logic for account metadata write races and the REST handler/manager wiring needed to serve the S3Control dialect with S3 authentication.

## Important APIs, Types, and Functions
`retry_raced_account_write()` executes an account write closure and retries up to ten times when `store_account()` returns `-ECANCELED`. Each retry clears the object version tracker and reloads account info/attrs before reapplying the closure.

`get_account_id()` reads `x-amz-account-id` from request metadata, rejects missing or empty values, and for non-admin callers verifies that the requested account id matches `s->auth.identity->get_account()`.

`RGWGetPublicAccessBlock_S3Control` loads the account, decodes `RGW_ATTR_PUBLIC_ACCESS` into `PublicAccessBlockConfiguration`, verifies `s3GetAccountPublicAccessBlock`, and emits XML.

`RGWPutPublicAccessBlock_S3Control` reads and XML-decodes the request body within `rgw_max_put_param_size`, verifies `s3PutAccountPublicAccessBlock`, forwards the request to the metadata master, encodes the public-access config into `RGW_ATTR_PUBLIC_ACCESS`, and stores the account with race retry.

`RGWDeletePublicAccessBlock_S3Control` verifies the same write permission, forwards to the master, erases `RGW_ATTR_PUBLIC_ACCESS` if present, and returns `204 No Content` on success.

`RGWHandler_PublicAccessBlock` sets `s->dialect = "s3control"`, enables `RGW_REST_S3CONTROL`, allocates XML formatting, and delegates authorization to `RGW_Auth_S3::authorize()`. `RGWRESTMgr_S3Control_PublicAccessBlock` returns that handler, and `RGWRESTMgr_S3Control` registers it under `configuration/publicAccessBlock`.

## Control Flow
A request routed to S3Control reaches `RGWRESTMgr_S3Control`, then `configuration`, then `publicAccessBlock`. The handler picks GET, PUT, or DELETE and performs ordinary RGW op lifecycle: init processing, permission verification, execute, and response.

GET only loads and decodes current account attrs. PUT first validates account id and XML body, then loads the account, forwards the original request/body to the metadata master, and updates attrs locally using optimistic object-version retry. DELETE follows the same load/forward/retry pattern but erases the attr.

## State and Persistence Behavior
The durable state is account metadata attribute `RGW_ATTR_PUBLIC_ACCESS`, containing an encoded `PublicAccessBlockConfiguration`. Writes use `driver->store_account()` with `exclusive = false`, previous account info, attrs, and `RGWObjVersionTracker`.

The implementation is zone-aware. Mutating operations call `rgw_forward_request_to_master()` before local mutation, ensuring account metadata is coordinated through the master zone. Race retries reload the account and reapply the attr update to current attrs.

## Dependencies and Integration Points
The file depends on `rgw_account.h`, `rgw_auth_s3.h`, `rgw_process_env.h`, SAL account load/store APIs, RGW XML decoder/formatter helpers, IAM permission checks, and S3 auth strategy registry. It is registered as a nested manager by `RGWRESTMgr_S3` when S3Control is enabled.

## Risks
The `x-amz-account-id` header is the authority for target account; any change to identity/account matching could expose cross-account metadata. PUT and DELETE use a placeholder root ARN construction marked with `XXX`, so permission resource semantics should be reviewed with account IAM changes.

Forward-to-master happens before local attr mutation. If forwarding succeeds but local retry later fails, client-visible behavior depends on master propagation and error handling. Decode failures of stored public-access attrs are treated as `-EIO`.

## Test Signals
Tests should cover missing/empty/mismatched `x-amz-account-id`, admin bypass, account without public access block, malformed XML, permission allow/deny for get and put/delete actions, master-zone forwarding, concurrent account metadata updates returning `-ECANCELED`, and idempotent delete when the attr is absent.
