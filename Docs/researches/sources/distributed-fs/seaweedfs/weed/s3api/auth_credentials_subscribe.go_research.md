# sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_subscribe.go

Purpose: Handles filer metadata subscriptions for S3 runtime state: bucket metadata, IAM config, OIDC providers, and circuit breaker config.

Important APIs, types, and functions: `subscribeMetaEvents` follows filer metadata and fans each event to `onBucketMetadataChange`, `onIamConfigChange`, `onOIDCProviderChange`, and `onCircuitBreakerConfigChange`. IAM-specific constants and handlers include `oidcProvidersDir`, `onIamConfigChange`, and `onOIDCProviderChange`; bucket cache helpers include `updateBucketConfigCacheFromEntry` and `invalidateBucketConfigCache`.

Control flow and state: The subscription callback handles create/update/delete/rename events. For moves, it processes the destination and then replays delete events for the source directory. For same-directory renames, it replays deletion for stale bucket/circuit-breaker names. `onIamConfigChange` ignores events when IAM is static, reloads on legacy `identity.json`, and reloads on multi-file identities, policies, service accounts, or groups. `onOIDCProviderChange` refreshes the IAM manager's OIDC provider view for changes under `/etc/iam/oidc-providers`.

State and persistence behavior: This file does not persist directly; it reacts to filer metadata and refreshes in-memory IAM, OIDC, circuit breaker, bucket registry, and bucket config cache state from authoritative stores. It uses retry-follow semantics with an incrementing client epoch.

Dependencies and integration points: Integrates with filer path constants, protobuf metadata follow APIs, `pb.WithFilerClientFollowMetadata`, `util.RetryUntil`, S3 bucket registry/cache code, circuit breaker config, and advanced IAM provider storage.

Risks and test signals: Static configs intentionally suppress IAM live reloads, so static detection must be precise. Rename/move handling is subtle because missing source-delete replay can leave stale bucket or config state. The subscribe tests cover legacy identity deletion and multi-file identity directory reloads; static-config tests cover the static/dynamic gating.
