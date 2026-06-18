# sources/distributed-fs/ceph/src/rgw/rgw_auth_keystone.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_auth_keystone.h` declares Keystone-specific RGW auth engines and the Keystone S3 secret cache. It separates token-based Keystone auth from EC2/S3-token auth while both produce RGW remote appliers. The source was read as a complete 210-line header.

## Important APIs, Types, and Functions

`rgw::auth::keystone::TokenEngine` derives from `Engine` and owns token extractors, a remote applier factory, Keystone config, and token cache. `SecretCache` is a singleton cache of token envelopes and secret strings with `find()` and `add()`. `EC2Engine` derives from `rgw::auth::s3::AWSEngine`, owns a remote applier factory, Keystone config/token cache, and `SecretCache`, and overrides the AWS auth path with Keystone-backed secret lookup.

## Control Flow

The declarations show token auth extracting auth and service tokens from `req_state`, then delegating to private helpers. EC2 auth accepts access key, signature, session token, string-to-sign, signature factory, completer factory, and request state from the S3 AWS engine abstraction, then uses Keystone helpers to obtain a token/secret and return a granted remote applier with completer.

## State and Persistence Behavior

`TokenEngine` and `EC2Engine` hold references to long-lived Keystone config and token cache objects. `SecretCache` owns an in-memory map, LRU list, mutex, maximum size, and TTL derived from Ceph config. No persistent data is stored by this header itself.

## Dependencies and Integration Points

The header depends on `rgw_auth.h`, `rgw_auth_s3.h`, `rgw_rest_s3.h`, `rgw_common.h`, and `rgw_keystone.h`. It is used by authentication registry/strategy construction when Keystone is enabled.

## Risks and Edge Cases

The singleton `SecretCache` captures `g_ceph_context` config at construction time, so tests and dynamic config must account for initialization timing. Engine references must outlive requests and appliers/completers they produce. EC2 auth cannot fully support streaming AWSv4 completers unless a secret key is available.

## Test Signals

Compile tests should validate construction with token extractors, remote applier factories, and S3 version abstractors. Runtime tests should validate cache thread safety, token extraction wiring, and EC2 engine behavior through the AWS engine interface.
