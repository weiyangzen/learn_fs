# sources/distributed-fs/ceph/src/rgw/rgw_op_type.h

## Purpose
`rgw_op_type.h` defines the `RGWOpType` enum used to classify RGW operations independently of concrete C++ class names. It is consumed by request processing, logging, tracing, rate-limit bypasses, protocol handlers, and feature-specific logic such as health-check handling and public-access operations.

## Important APIs, Types, And Functions
The only exported type is `enum RGWOpType`. It starts with core object, bucket, metadata, ACL, CORS, encryption, request-payment, multipart, bulk, attr, health, lifecycle, object-lock, and ownership-control values. Later ranges cover IAM, RGW admin/sync/period operations, STS operations, pubsub topic/subscription/notification operations, bucket tagging/replication, public-access block APIs, and OIDC provider operations.

## Control Flow
Concrete `RGWOp::get_type()` overrides return values from this enum. `process_request()` stores the type in `req_state::op_type`; `rate_limit()` uses it to exempt health checks, and other RGW code can switch on it without RTTI. The enum is append-only in practice because many components may persist or report numeric operation ids.

## State And Persistence
The enum itself has no runtime state. Its persistence risk is compatibility: logs, metrics, traces, and external consumers may infer meaning from numeric values. Reordering existing values would break that assumption.

## Dependencies And Integration Points
`rgw_op.h` includes this enum through common operation headers. Request-processing, REST handler, admin, IAM, STS, sync, pubsub, and public-access implementations all integrate by returning a stable type.

## Risks And Test Signals
Risks include forgetting to assign new operations a specific enum, duplicate/ambiguous classification, and reordering values. Test signals include operation-specific request tests confirming `req_state::op_type`, logging/tracing classification, rate-limit bypass behavior for health checks, and compile coverage for all new `get_type()` overrides.
