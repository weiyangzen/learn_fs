# sources/distributed-fs/ceph/src/rgw/rgw_auth_keystone.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_auth_keystone.cc` implements Keystone token authentication and Keystone-backed S3/EC2 authentication for RGW. It validates Keystone tokens, service tokens, EC2 credentials, maps Keystone roles/scopes into RGW remote auth info, and maintains an access-key secret cache for Keystone S3 auth. The source was read as a complete 833-line implementation.

## Important APIs, Types, and Functions

`TokenEngine::is_applicable()`, `get_from_keystone()`, `get_acl_strategy()`, `get_creds_info()`, and `authenticate()` handle token auth. `EC2Engine::get_from_keystone()`, `get_secret_from_keystone()`, `get_access_token()`, `get_acl_strategy()`, `get_creds_info()`, and `authenticate()` handle S3 token/secret validation. `SecretCache::find()` and `SecretCache::add()` implement LRU/TTL caching of Keystone token envelopes and secrets.

## Control Flow

Token auth rejects empty tokens or missing Keystone URL, checks token cache by token id, optionally validates a service token to allow expired user tokens, validates the user token through Keystone `v3/auth/tokens`, updates role flags, checks expiration and accepted roles, caches the envelope, and grants a `RemoteApplier`. Admin-token 401 responses invalidate and retry the admin token cache once.

EC2 auth tries `SecretCache` first and verifies the request signature locally when a secret is cached. On miss or mismatch it posts to Keystone `v3/s3tokens`, fetches the EC2 secret from `/v3/users/{id}/credentials/OS-EC2/{access}`, caches token/secret pairs, checks token expiration and accepted roles, and grants a remote applier plus an S3 completer factory. Signature mismatch for a known Keystone access key is a hard reject to prevent fallback to other engines.

## State and Persistence Behavior

The implementation uses Keystone admin token cache through `rgw::keystone::TokenCache`, the singleton `SecretCache` for EC2 token/secret pairs, and SAL-backed remote appliers for later user/account loading or creation. `SecretCache` holds a map and LRU list under a mutex, expires entries by token expiration or configured TTL, and trims to `rgw_keystone_token_cache_size`.

## Dependencies and Integration Points

Dependencies include Keystone service HTTP transceivers, JSON parser/formatter, Base64 helpers, Ceph crypto/signature helpers through S3 engine interfaces, RGW Keystone config and scope logging, token cache, accepted role config, and `rgw_auth_s3` abstract AWS engine APIs. The file bridges external Keystone identity into RGW's remote auth and S3 completer flow.

## Risks and Edge Cases

Admin-token invalidation/retry must avoid infinite loops. Service token handling intentionally permits expired user tokens for a bounded cache duration, so role and TTL configuration are security-sensitive. EC2 cache mismatch falls back to Keystone and may reject rather than deny when access key exists but signature is wrong. JSON parsing failures and missing credential fields return `-EINVAL`. `SecretCache` stores secrets in memory and must respect TTL/size limits. OPTIONS CORS requests intentionally ignore signature validation in one path.

## Test Signals

Tests should cover token cache hit/miss, admin-token 401 invalidation, service token role checks, expired-token behavior with and without service token, accepted/admin/reader role mapping, Keystone 404/401/error status mapping, EC2 cache hit with valid and invalid signatures, secret fetch JSON errors, LRU eviction and TTL expiry, CORS ignore-signature path, and reject-vs-deny behavior for signature mismatch.
