# subset-b-006997 research

Grouped research for Ceph RGW REST pubsub, ratelimit, restore, and role handlers. Each section is source-tree aligned and wrapped for reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_pubsub.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_pubsub.cc

## Purpose

`rgw_rest_pubsub.cc` implements RGW REST operations for two related APIs: SNS-compatible topic management and S3-compatible bucket notification configuration. It bridges HTTP request parsing, IAM authorization, topic policy checks, persistent notification queue lifecycle, and bucket metadata updates into the `RGWPubSub` and SAL driver layers. The file also contains helper validation for topic names, topic ARNs, endpoint secrets, topic policies, and owner/account handling.

## Important APIs, types, and functions

- `verify_transport_security()` and `validate_and_update_endpoint_secret()` protect topic endpoint credentials. They detect credentials embedded in endpoint URLs or topic attributes such as `user-name`, `password`, and `ssl-key-password`, set `rgw_pubsub_dest::stored_secret`, and reject insecure transport unless `rgw_allow_notification_secrets_in_cleartext` permits it.
- `validate_topic_name()` enforces the default SNS-like topic name character and length contract unless relaxed topic names are configured. `validate_topic_arn()` parses and validates `TopicArn`.
- `get_account_or_tenant()` normalizes an `rgw_owner` variant to the account id or tenant string used as the topic namespace.
- `verify_topic_permission()` is the central resource/identity policy evaluator. It handles account-root behavior, same-owner access, cross-account access requiring both identity and resource policy allows, legacy non-account owner fallback, and the compatibility setting for publish without a policy.
- `should_forward_request_to_master()` gates metadata-master forwarding when the local zone is not metadata master and all zonegroups support `notification_v2`.
- SNS-style `RGWOp` classes: `RGWPSCreateTopicOp`, `RGWPSListTopicsOp`, `RGWPSGetTopicOp`, `RGWPSGetTopicAttributesOp`, `RGWPSSetTopicAttributesOp`, and `RGWPSDeleteTopicOp`.
- S3 notification classes: `RGWPSCreateNotifOp`, `RGWPSDeleteNotifOp`, and `RGWPSListNotifsOp`.
- `op_generators` maps AWS `Action` values to operation constructors for `RGWHandler_REST_PSTopic_AWS::op_post()`.
- `remove_notification_by_topic()` and `delete_all_notifications()` coordinate legacy notification and auto-generated topic cleanup.

## Control flow

The SNS path enters through `RGWHandler_REST_PSTopic_AWS::op_post()`, which sets the request dialect/protocol flags, reads `Action`, and dispatches through `op_generators`. The handler authorizes with S3 authentication and explicitly rejects anonymous identities. Each operation parses request arguments in `init_processing()`, often loads existing topic metadata through `RGWPubSub`, evaluates IAM/topic policy in `verify_permission()`, performs metadata-master forwarding in `execute()` when needed, and writes XML SNS responses in `send_response()`.

`CreateTopic` validates name, endpoint, persistence options, retry fields, arbitrary endpoint args, and optional topic policy. It can create persistent queue shards through `driver->add_persistent_topic()` before storing the topic with `RGWPubSub::create_topic()`. Repeated creation of an already persistent topic preserves the existing queue and shard count rather than resharding.

`ListTopics` selects v2 listing when all zonegroups support `notification_v2` and no v1 topic marker exists, otherwise falls back to v1. Account users are authorized up front against account root ARN; non-account users list then filter topics by `snsGetTopicAttributes`. Topic responses containing stored secrets require secure transport.

`GetTopic` and `GetTopicAttributes` parse `TopicArn`, load topic metadata from the ARN account namespace, reject missing topics as `NotFound`, block secret-bearing topic output over insecure transport, and require `snsGetTopicAttributes`.

`SetTopicAttributes` loads a topic, maps a single `AttributeName`/`AttributeValue` into updated destination, opaque data, policy text, or endpoint args, then forwards if needed. It creates persistent queue shards when a topic becomes persistent and removes shards when it becomes non-persistent before rewriting topic metadata.

`DeleteTopic` is idempotent for missing topics. If the topic exists, it authorizes against `snsDeleteTopic`, forwards when needed, and removes topic metadata.

The S3 notification path enters through `RGWHandler_REST_PSNotifs_S3` for `GET`, `PUT`, and `DELETE` on `?notification`. `PUT` parses XML `NotificationConfiguration`, validates notification ids, topic ARNs, event types, and topic existence, then requires bucket `s3PutBucketNotification` and `snsPublish` on every target topic. For v1, it creates per-notification internal topics named by `topic_to_unique()`, stores destination metadata there, and creates bucket notifications. For v2, it writes `RGW_ATTR_BUCKET_NOTIFICATION` on the bucket under `retry_raced_bucket_write()` and updates bucket-topic mapping. Empty configuration deletes all notifications. `DELETE` removes one notification or all notifications, using v2 attr removal when available and legacy `RGWPubSub::Bucket` operations otherwise. `GET` loads the bucket, chooses v2 attr read or legacy topic listing, filters to S3 notifications, and emits XML.

## State and persistence behavior

Topic state is persisted through `RGWPubSub::create_topic()`, `get_topic()`, `get_topics_v1()`, `get_topics_v2()`, and `remove_topic()`. Persistent notification queue state is managed through driver calls `add_persistent_topic()` and `remove_persistent_topic()` using shard names from `rgw_pubsub_dest`. In v1 bucket notifications, the code creates internal per-notification topics and subscription records under `RGWPubSub::Bucket`. In v2, bucket notification configuration is encoded into `RGW_ATTR_BUCKET_NOTIFICATION` on bucket attrs and stored with `merge_and_store_attrs()`, with `retry_raced_bucket_write()` protecting against concurrent bucket metadata updates. Topic-to-bucket reverse mappings are updated with `driver->update_bucket_topic_mapping()`.

The file also persists security-relevant metadata: `stored_secret` marks topics whose endpoint config includes credentials, and topic policy text is stored with topic metadata for later resource-policy evaluation.

## Dependencies and integration points

This file depends on `rgw_pubsub.h`, `rgw_arn.h`, `rgw_iam_policy.h`, `rgw_auth_s3.h`, `rgw_rest_s3.h`, `rgw_process_env.h`, SAL driver APIs, zone feature checks, XML decoding, Ceph formatter/XML output, and notification helper functions such as `get_bucket_notifications()`, `remove_notification_v2()`, `topic_to_unique()`, and `find_unique_topic()`. It is integrated into RGW REST routing through `RGWHandler_REST_PSTopic_AWS` and `RGWHandler_REST_PSNotifs_S3`, with static factory methods allowing other handlers to construct S3 notification ops.

## Risks and edge cases

- Secret-bearing topic metadata is intentionally blocked on insecure transport, but the bypass config is high risk and logs only a warning.
- `SetTopicAttributes` rewrites `push_endpoint_args` by substring search; malformed or overlapping endpoint arg names could be a maintenance-sensitive area.
- Several forwarded operations mutate `s->info.args` before forwarding or local processing. Iterator erasure inside loops over `get_params()` appears delicate and should be tested for skipped entries or invalidation.
- Persistent queue creation/removal is not fully transactional with topic metadata writes. Failures after shard creation or removal can leave queue/topic state needing cleanup.
- V1/v2 migration guards return service unavailable when v1 topics still exist or migration state is unknown. Mixed-version zonegroup behavior is a key compatibility risk.
- `ListTopics` v2/v1 selection uses `stat_topics_v1()` as a migration signal; incorrect signal values would change listing source.
- Permission semantics differ for account and non-account identities and for missing legacy owners. Regression tests should cover cross-account and legacy-owner compatibility.

## Test signals

Useful tests include SNS create/list/get/set/delete topic flows; topic creation with endpoint credentials over HTTP and HTTPS; topic policies for same-owner, cross-account, deny, and allow cases; persistent topic shard creation, idempotent create without resharding, transition to non-persistent, and failure cleanup; S3 `PUT/GET/DELETE ?notification` with empty config, one config, multiple configs, filters, invalid events, missing topics, and specific notification deletion; v1 versus v2 notification storage selection; metadata-master forwarding from secondary zones; and migration-block behavior when v1 topics are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_pubsub.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_pubsub.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_pubsub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_ratelimit.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_ratelimit.cc

## Purpose

`rgw_rest_ratelimit.cc` implements administrative REST operations for reading and updating RGW rate-limit configuration at three scopes: bucket-specific attrs, user-specific attrs, and global period config for bucket, user, and anonymous limits. It exposes `GET` for inspection and `POST` for mutation through `RGWHandler_Ratelimit`.

## Important APIs, types, and functions

- `RGWOp_Ratelimit_Info` is a read operation requiring `ratelimit=read` caps. It parses `ratelimit-scope`, `uid`, `bucket`, `tenant`, and `global`, then returns JSON for the requested scope.
- `RGWOp_Ratelimit_Set` is a write operation requiring `ratelimit=write` caps. It parses maximum operation/byte limits and `enabled`, forwards writes to the master zone, merges the requested changes into existing `RGWRateLimitInfo`, and persists them.
- `RGWOp_Ratelimit_Set::set_ratelimit_info()` is the shared field-merging helper. It only applies provided non-negative numeric values and applies `enabled` when provided. If no valid rate-limit field is present, it sets `op_ret = -EINVAL`.
- `RGWHandler_Ratelimit::op_get()` and `op_post()` create the read and set operations.

## Control flow

The `GET` path validates `global` manually because `RESTArgs::get_bool()` treats an empty boolean as true. For non-global bucket scope, it loads a bucket by `tenant` and `bucket`, decodes `RGW_ATTR_RATELIMIT` if present, and emits `bucket_ratelimit`. For non-global user scope, it loads the user, decodes the same attr, and emits `user_ratelimit`. For global scope, it reads `RGWPeriodConfig` for the current realm id through `s->penv.cfgstore`, tolerates missing config, and emits bucket, user, and anonymous rate-limit blocks. Any unrecognized parameter combination returns `-EINVAL`.

The `POST` path parses all optional numeric limits with `RESTArgs::get_int64()` and validates boolean text for `enabled` and `global`. It first forwards the request to the master zone through `rgw_forward_request_to_master()`. It then builds an initial `RGWRateLimitInfo` from supplied fields, and for user or bucket scope it loads the existing object, decodes existing rate-limit attrs, reapplies supplied fields so updates are merge-style, encodes `RGWRateLimitInfo`, and stores via `merge_and_store_attrs()`. For global scope, it reads period config, selects the bucket, user, or anonymous rate-limit member based on `ratelimit-scope`, merges fields, and writes period config back with `write_period_config()`.

## State and persistence behavior

Bucket and user rate limits are stored as encoded `RGWRateLimitInfo` in `RGW_ATTR_RATELIMIT` on bucket/user attrs. Global rate limits are stored in realm period config as `RGWPeriodConfig::bucket_ratelimit`, `user_ratelimit`, and `anon_ratelimit`. The code uses merge-and-store for attrs so it updates only the rate-limit attr while preserving other attrs. Global writes use `cfgstore->write_period_config()` and therefore affect configuration propagated through period metadata.

## Dependencies and integration points

The implementation depends on `rgw_sal.h` for users and buckets, `rgw_sal_config.h` for period config, `rgw_process_env.h` for site/config store access, `rgw_op.h` for forwarding helpers and operation base behavior, `RESTArgs` parsing, `RGWRateLimitInfo` encode/decode, and JSON formatter output.

## Risks and edge cases

- `set_ratelimit_info()` ignores provided negative numeric values without directly returning an error. If at least one other field is valid, a request with a negative field can succeed while silently ignoring that field.
- The helper sets `op_ret` on the operation object instead of returning a status, so all callers must check `op_ret` after calling it.
- The write path calls `set_ratelimit_info()` before loading existing user/bucket/global state and then again after decoding existing state; this is redundant but also means `ratelimit_configured` remains true across the second call.
- All writes are forwarded before local validation of target object existence. Forwarding failures stop local work; forwarded success followed by local attr failure can leave local metadata temporarily inconsistent until sync.
- Boolean parsing is manually guarded because empty booleans are otherwise accepted as true; future boolean parameters need the same care.
- Global scope requires a valid `ratelimit-scope` of `bucket`, `user`, or `anon`; non-global scopes require the matching identity parameter.

## Test signals

Tests should cover `GET` bucket/user/global with missing attrs, malformed encoded attrs, missing user or bucket, invalid `global` boolean text, and invalid scope combinations. Mutation tests should cover each limit field, `enabled`, merge behavior preserving unspecified fields, negative numeric handling, user and bucket attr persistence, global bucket/user/anonymous config writes, forwarding behavior from non-master zones, and cap enforcement for read versus write operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_ratelimit.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_ratelimit.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_ratelimit.h

## Purpose

`rgw_rest_ratelimit.h` declares the authenticated REST handler and REST manager for RGW rate-limit administration. It connects the ratelimit endpoint to S3-authenticated request handling and exposes a manager that creates the handler for RGW routing.

## Important APIs, types, and functions

- `RGWHandler_Ratelimit` derives from `RGWHandler_Auth_S3`, so requests use S3 authentication. It overrides `op_get()` and `op_post()` to create the concrete read and write operations implemented in `rgw_rest_ratelimit.cc`.
- `RGWHandler_Ratelimit::read_permissions()` returns success, leaving capability enforcement to `RGWOp_Ratelimit_Info::check_caps()` and `RGWOp_Ratelimit_Set::check_caps()`.
- `RGWRESTMgr_Ratelimit` derives from `RGWRESTMgr` and overrides `get_handler()` to return a new `RGWHandler_Ratelimit` with the provided auth strategy registry.

## Control flow

When the REST manager is selected for the ratelimit endpoint, `get_handler()` constructs an authenticated S3 handler. The handler's verb dispatch maps `GET` to ratelimit inspection and `POST` to ratelimit update. The header does not declare `PUT` or `DELETE`, so unsupported methods fall through to base behavior.

## State and persistence behavior

The header stores no persistent state. Handler instances are request-scoped. Persistent behavior is entirely in the `.cc` file: encoded user/bucket attrs and global period config writes.

## Dependencies and integration points

It depends on `rgw_rest.h` and `rgw_rest_s3.h` for REST manager and authenticated handler base classes. Under `WITH_RADOSGW_RADOS`, it includes `rgw_sal_rados.h`, tying the endpoint to RADOS-backed SAL builds. The manager signature accepts a SAL driver, request state, auth registry, and frontend prefix, matching the RGW REST manager contract.

## Risks and edge cases

- Because `read_permissions()` always succeeds, operation-level caps are the only protection beyond authentication. Any future ratelimit operation must implement `check_caps()` correctly.
- `get_handler()` ignores the driver and request state parameters, so handler construction cannot vary by backend or request context without modifying this manager.
- Only `GET` and `POST` are exposed. Clients expecting `PUT` for updates would not be served by this handler.

## Test signals

Route tests should verify that the manager returns `RGWHandler_Ratelimit`, `GET` produces the info op, `POST` produces the set op, read/write caps are enforced by the concrete ops, and unauthenticated or incorrectly signed requests fail through the S3 auth base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_ratelimit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_restore.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_restore.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_restore.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_restore.h

## Purpose

`rgw_rest_restore.h` declares the authenticated REST handler and manager for RGW restore status/list operations. It exposes only `GET` handling and delegates concrete operation selection to the implementation file.

## Important APIs, types, and functions

- `RGWHandler_Restore` derives from `RGWHandler_Auth_S3`, so restore inspection requires S3-authenticated requests. It overrides `op_get()` to select object restore status or bucket restore listing.
- `RGWHandler_Restore::read_permissions()` returns success, leaving caps to the concrete restore operations.
- `RGWRESTMgr_Restore` derives from `RGWRESTMgr` and returns a new `RGWHandler_Restore` from `get_handler()`.

## Control flow

When the restore endpoint is routed, the manager constructs `RGWHandler_Restore`. The handler authenticates through the S3 auth base, then `op_get()` checks request args in the `.cc` file and returns a restore-status op for object-specific requests or a restore-list op otherwise. No write verbs are declared in this handler.

## State and persistence behavior

The header contains no persistence logic and no long-lived state. Restore data access is delegated by the `.cc` operations to the restore service behind the SAL driver.

## Dependencies and integration points

It includes `rgw_rest.h` and `rgw_rest_s3.h` for REST manager and authenticated handler base definitions. The manager signature integrates with the generic RGW REST routing layer and passes the auth strategy registry into the handler.

## Risks and edge cases

- As with other small RGW admin-style handlers, operation-level cap checks are required because `read_permissions()` returns `0`.
- The manager ignores the SAL driver and request state when constructing the handler, so backend-specific restore routing would require changes.
- Only `GET` is supported. Any future restore mutation endpoint needs explicit verb mapping and caps.

## Test signals

Route tests should verify manager construction, S3 auth enforcement, `GET` dispatch to object status when the `object` subresource exists, `GET` dispatch to list otherwise, rejection of unsupported verbs, and concrete operation caps for `buckets=read`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_restore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_role.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_role.cc

## Purpose

`rgw_rest_role.cc` implements RGW IAM role REST operations: create, delete, get, list, update assume-role policy, inline role policy CRUD/list, role tags, update role metadata, and managed policy attach/detach/list for account roles. It provides operation-level IAM authorization and metadata-master forwarding so role metadata is written consistently across zones.

## Important APIs, types, and functions

- `RGWRestRole::verify_permission()` first evaluates IAM identity/resource permissions with `verify_user_permission()` against the operation action and precomputed role ARN, then falls back to cap-based `RGWRESTOp::verify_permission()`. `check_caps()` checks the `roles` cap with the operation's read/write permission.
- `dump_iam_role()` emits the IAM XML/formatter fields for role responses.
- `parse_tags()` parses AWS query parameters `Tags.member.N.Key` and `Tags.member.N.Value` into a multimap.
- `make_role_arn()` and `load_role()` centralize ARN construction and role lookup. `load_role()` maps missing roles to `-ERR_NO_ROLE_FOUND` and sets the resource ARN once the stored role path is known.
- `check_role_limit()` enforces account `max_roles` by loading account info and counting account roles.
- Concrete operations include `RGWCreateRole`, `RGWDeleteRole`, `RGWGetRole`, `RGWModifyRoleTrustPolicy`, `RGWListRoles`, `RGWPutRolePolicy`, `RGWGetRolePolicy`, `RGWListRolePolicies`, `RGWDeleteRolePolicy`, `RGWTagRole`, `RGWListRoleTags`, `RGWUntagRole`, `RGWUpdateRole`, and internal managed-policy ops.
- Factory functions `make_iam_attach_role_policy_op()`, `make_iam_detach_role_policy_op()`, and `make_iam_list_attached_role_policies_op()` expose managed-policy operations to IAM routing.

## Control flow

Most operations follow a common pattern: parse and validate AWS Query arguments in `init_processing()`, set `account_id` from account identity when present, load role metadata and compute the resource ARN, then execute local or forwarded metadata changes. Write operations check whether the site is metadata master. On secondary zones they call `forward_iam_request_to_master()` with the saved POST body, remove already-parsed parameters from `s->info.args`, parse any needed XML response, and then perform local store/delete with race-tolerant behavior. Metadata mutations use `retry_raced_role_write()` around updates to handle concurrent metadata sync/write races.

`CreateRole` validates role name, path, required trust policy, trust policy parse, description length, tags, tag count, account role limit, and tenant consistency. If forwarded, it decodes `RoleId` and `CreateDate` from the master response so local creation matches master metadata. It maps master-zone duplicate creates to `-ERR_ROLE_EXISTS`, while duplicate after forwarding is treated as success because sync may already have replicated the role.

`DeleteRole` loads the role and, on the master, refuses deletion while inline or managed policies remain. It deletes role metadata and maps already-deleted secondary-zone state to success.

`GetRole` formats stored role info. `ModifyRoleTrustPolicy` validates a required JSON policy document and stores it. `ListRoles` supports `PathPrefix`, `Marker`, and `MaxItems` up to 1000, then lists by account id or tenant and emits truncation metadata.

Inline policy operations validate role and policy names, parse policy JSON with tenant restriction for non-account identities, store policy text in role info, fetch by name with `NoSuchEntity` mapping, list names, and delete policies with idempotent secondary-zone behavior.

Tag operations parse tags or tag keys, load the role, and update stored tag metadata. `UpdateRole` optionally changes description and max session duration, validates duration, and stores role info.

Managed policy operations are supported only for account users. Attach validates `PolicyArn`, confirms the managed policy exists through `rgw::IAM::get_managed_policy()`, inserts the ARN idempotently, and stores. Detach removes the ARN, treating missing policy as success only on secondary zones after forwarding. List emits attached policy ARNs and derives names from the ARN suffix.

## State and persistence behavior

Role metadata is represented by `rgw::sal::RGWRole` and persisted through `create()`, `delete_obj()`, `store_info()`, inline policy helpers, tag helpers, and managed policy fields in `RGWRoleInfo`. Account role quotas are read from account metadata. Most write paths are metadata-master-first in multisite setups and then perform local metadata writes, tolerating races where sync has already applied the master change. Role state includes trust policy, inline permission policy map, managed policy ARN set, tags, description, path, max session duration, creation date, role id, tenant, and account id.

## Dependencies and integration points

The file depends on IAM parsing/evaluation (`rgw_iam_policy`, `rgw_rest_iam`), role validation and storage (`rgw_role.h`, SAL `get_role()`, list/count account roles), account metadata, RGW XML parser/formatter, `forward_iam_request_to_master()`, `retry_raced_role_write()`, `verify_user_permission()`, and standard RGW request state. Factory functions integrate with the broader IAM REST action dispatcher rather than declaring a handler in this file.

## Risks and edge cases

- `parse_tags()` inserts into vectors at `begin() + (index - 1)` without bounds checks. Sparse or out-of-order tag indices can risk invalid iterator behavior.
- Several loops erase matching `Tags.member.*` params while iterating a map with `it++` in the loop header; this pattern can skip entries or invalidate iteration depending on container behavior.
- Many write operations mutate `s->info.args` before forwarding. Any later code that relies on original args must use member copies or POST body.
- `ModifyRoleTrustPolicy` validates with `JSONParser`, while create uses full `rgw::IAM::Policy`; policy validation semantics may differ.
- `RGWUpdateRole::execute()` opens `UpdateRoleResult` and then `ResponseMetadata` inside it, which may not match AWS response nesting expectations.
- Managed policy list declares `RGW_CAP_WRITE` in its base constructor despite being a list/read-style operation, which may be intentional or an authorization bug.
- Secondary-zone idempotence intentionally maps some local missing/existing states to success after successful forwarding; tests must distinguish master and secondary behavior.

## Test signals

Tests should cover role create validation, trust policy parse failures, account role quota, duplicate creates on master and secondary, tenant mismatch, delete conflicts with inline/managed policies, get/list role output and pagination, update assume role policy, inline policy put/get/list/delete including malformed policy and missing policy mappings, tag parse with ordered and malformed indices, tag count limits, untag, update description and session duration validation, managed policy attach/detach/list for account and non-account identities, metadata-master forwarding, sync race idempotence, IAM authorization by action/resource ARN, and fallback role caps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_role.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_role.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_role.h

## Purpose

`rgw_rest_role.h` declares the IAM role operation classes implemented in `rgw_rest_role.cc`. It defines a shared authorization base, one class per IAM role action, and factories for managed policy role actions consumed by the broader IAM REST dispatcher.

## Important APIs, types, and functions

- `RGWRestRole` derives from `RGWRESTOp` and stores the IAM action id and cap permission required by a concrete action. It also stores `account_id` and a `rgw::ARN resource` that must be initialized before permission verification. It overrides `check_caps()` and `verify_permission()`.
- Role lifecycle operations: `RGWCreateRole`, `RGWDeleteRole`, `RGWGetRole`, `RGWListRoles`, and `RGWUpdateRole`.
- Trust policy operation: `RGWModifyRoleTrustPolicy`.
- Inline policy operations: `RGWPutRolePolicy`, `RGWGetRolePolicy`, `RGWListRolePolicies`, and `RGWDeleteRolePolicy`.
- Tag operations: `RGWTagRole`, `RGWListRoleTags`, and `RGWUntagRole`.
- Managed-policy factories: `make_iam_attach_role_policy_op()`, `make_iam_detach_role_policy_op()`, and `make_iam_list_attached_role_policies_op()`.

Each concrete class declares `init_processing()`, `execute()`, `name()`, and `get_type()`, and stores request-scoped parsed parameters and loaded role pointers where needed.

## Control flow

The broader IAM REST routing layer constructs these operation classes based on AWS IAM `Action` names. During request processing, `init_processing()` parses role-specific arguments and usually initializes `resource`; `RGWRestRole::verify_permission()` evaluates IAM permissions against `action` and `resource`; and `execute()` performs the role operation and writes an IAM XML-style response. Write operations that need original form data store `bufferlist bl_post_body` for metadata-master forwarding.

## State and persistence behavior

The header defines only request-scoped state: role names, policy names/documents, tags, untag vectors, optional description, max session duration, loaded `rgw::sal::RGWRole` pointers, and POST bodies. Persistent role state is written by the `.cc` implementation through SAL role objects. The `account_id` and `resource` members are central to authorization and account-scoped storage.

## Dependencies and integration points

The header depends on Boost optional, async yield context, `rgw_arn.h`, `rgw_role.h`, and `rgw_rest.h`. It exposes operation types such as `RGW_OP_CREATE_ROLE`, `RGW_OP_DELETE_ROLE`, and policy/tag operation ids for logging, tracing, and RGW operation accounting. The managed-policy factory functions are an integration boundary with IAM action dispatch without exposing the internal classes in the header.

## Risks and edge cases

- The comment on `resource` is important: if a derived class fails to initialize it before `verify_permission()`, IAM authorization may evaluate the wrong ARN.
- Several write classes hold `bufferlist` copies of the POST body; callers should pass the body consistently or forwarding will be incomplete.
- The header uses `boost::optional` for `RGWUpdateRole::description` while other code may prefer `std::optional`, reflecting existing codebase style but worth noting for future changes.
- Loaded `role` pointers are unique ownership and request-scoped. Execute paths assume `init_processing()` successfully populated them.

## Test signals

Construction/routing tests should verify every IAM role action maps to the expected class and `RGWOpType`, each operation name is stable for logging/admin ops, read actions use read caps and write actions use write caps, managed-policy factories return usable ops, and permission verification sees initialized account/resource state for create, list, loaded-role, and managed-policy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_role.h -->
