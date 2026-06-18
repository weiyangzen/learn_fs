# sources/distributed-fs/ceph/src/rgw/rgw_rest_pubsub.h

## Purpose

`rgw_rest_pubsub.h` declares the REST handler classes that expose Ceph RGW pubsub functionality. It separates S3 bucket-notification routing from AWS SNS-style topic routing and provides factory hooks used by the implementation and by other REST routing code.

## Important APIs, types, and functions

- `RGWHandler_REST_PSNotifs_S3` derives from `RGWHandler_REST_S3` and handles S3-compatible `?notification` operations. It overrides `op_get()`, `op_put()`, and `op_delete()` to create notification list/create/delete operations. It disables quota support and returns success from permission initialization/read hooks, leaving operation-level checks to the concrete ops.
- `RGWHandler_REST_PSNotifs_S3::create_get_op()`, `create_put_op()`, and `create_delete_op()` are static factories that let another REST handler instantiate the same operations without going through method dispatch.
- `RGWHandler_REST_PSTopic_AWS` derives directly from `RGWHandler_REST` for AWS Query/SNS-style topic actions. It stores an auth strategy registry reference and the POST body bufferlist because some topic mutations must forward the original request body to the metadata master.
- `RGWHandler_REST_PSTopic_AWS::op_post()` dispatches `Action=` requests to topic operations.
- `authorize()` performs S3 authentication and rejects anonymous use.
- `action_exists()` overloads provide a cheap route probe on `req_state` or `req_info`.

## Control flow

The S3 notification handler is selected for bucket notification subresources. HTTP verbs are mapped to operation instances declared only by pointer in the header and implemented in `rgw_rest_pubsub.cc`. Because `init_permissions()` and `read_permissions()` return `0`, concrete operations such as `RGWPSCreateNotifOp` and `RGWPSListNotifsOp` enforce bucket and topic permissions themselves.

The AWS topic handler is selected for SNS-style POST requests. Construction captures `auth_registry` and `bl_post_body`. After post-auth initialization, `authorize()` authenticates the request. `op_post()` then checks the `Action` argument and constructs the matching topic op from the implementation file.

## State and persistence behavior

The header owns no persistent state directly. Its only stored state is request-scoped: an auth registry reference and a moved POST body bufferlist for topic forwarding. Persistence is delegated to the concrete operations in `rgw_rest_pubsub.cc`, which update topic metadata, persistent queues, and bucket notification attrs.

## Dependencies and integration points

The header depends on `rgw_rest_s3.h`, which supplies `RGWHandler_REST_S3`, `RGWHandler_REST`, `RGWOp`, `req_state`, and authentication-related types. It is an integration surface for RGW REST routing: external code can test `RGWHandler_REST_PSTopic_AWS::action_exists()` before selecting this handler, and can use the S3 notification static factories to embed notification handling in another handler.

## Risks and edge cases

- The S3 handler intentionally bypasses handler-level permission checks, so every operation returned by these factories must maintain complete authorization logic.
- `RGWHandler_REST_PSTopic_AWS` stores `auth_registry` by reference; its lifetime must exceed the handler.
- The POST body is moved into the handler and later into operation factories, so dispatch paths must not assume it remains available after op creation.
- `action_exists()` only checks the `Action` string against known operations; authentication and parameter validation still happen later.

## Test signals

Route-level tests should verify `GET`, `PUT`, and `DELETE` on S3 `?notification` produce the correct operation types, topic POST actions are accepted only for known actions, unknown or missing `Action` returns no op, anonymous topic requests are rejected, and operation factories work when called through the static methods as well as through handler virtual dispatch.
