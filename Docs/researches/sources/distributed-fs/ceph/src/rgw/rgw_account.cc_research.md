# sources/distributed-fs/ceph/src/rgw/rgw_account.cc

## Purpose
Implements account admin operations for RGW: id generation/validation, account creation/modification/removal, account info/stat retrieval, and account user listing.

## Important APIs, Types, and Functions
- `generate_id()` creates `RGW` plus 17 numeric digits.
- `validate_id()` and `validate_name()` enforce account identifier and account name constraints.
- `root_arn()` constructs an IAM root ARN for an account id.
- `create()`, `modify()`, `remove()`, `info()`, `stats()`, and `list_users()` implement the operations declared in `rgw_account.h`.

## Control Flow
Create validates name/id, applies quota defaults from config, creates an `RGWAccountInfo`, generates a write version, and calls `driver->store_account()` in exclusive mode. Modify loads by id/name/email, rejects tenant changes, applies name/email/limit/quota updates, and stores non-exclusively with the old info for index updates. Remove loads the account, then lists users, buckets, roles, groups, OIDC providers, and topics in chunks; without `purge_data`, any child resource aborts deletion, while with purge it removes each child before deleting the account. Info and stats load the account and format JSON; stats can sync or reset account stats before loading them. `list_users()` pages through account users and optionally filters to root users.

## State and Persistence
All durable work is delegated to `rgw::sal::Driver`: account records and indexes, users, buckets, roles, groups, OIDC providers, topics, quotas, and stats. `RGWObjVersionTracker` is used for account/group/topic persistence paths. Output is streamed through `RGWFormatterFlusher`.

## Dependencies and Integration Points
Depends on SAL driver account APIs, quota helpers, ARN support, role/OIDC/topic/bucket/user abstractions, and Ceph UTF-8/random utilities. It is used by RGW admin REST/CLI account paths.

## Risks and Edge Cases
`remove()` can be highly destructive with `purge_data=true`, cascading through users, buckets, roles, groups, OIDC providers, and topics. Partial failures can leave some children removed and the account still present. `list_users()` subtracts all returned users from `remaining`, including entries skipped by `root_only`, so a root-only query with max entries may return fewer visible users than requested. Name validation forbids `$` and `:` but not all possible operationally confusing characters.

## Test Signals
Tests should cover id/name validation, create default quota application, duplicate create behavior, modify by each lookup key, tenant immutability, quota scope updates, non-purge deletion blockers, purge cascade ordering/failure, stats sync/reset, and paginated user listing with `root_only`.
