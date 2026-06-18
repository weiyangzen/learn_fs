## sources/distributed-fs/ceph/src/rgw/rgw_oidc_provider.h

Purpose: declares the serialized OIDC provider metadata model used by RGW IAM/OIDC features.

Important APIs/types: `RGWOIDCProviderInfo` stores `id`, `provider_url`, `arn`, `creation_date`, `tenant`, `client_ids`, and `thumbprints`, with encode/decode version 3, JSON dump/decode, and test-instance generation.

Control flow: provider management APIs populate this struct, encode it for storage, and dump/decode JSON for admin/API exchange.

State and persistence: all fields are persisted in Ceph encoding. `tenant` may be tenant name or account id.

Dependencies/integration: includes `common/ceph_json.h` and uses `WRITE_CLASS_ENCODER`.

Risks and test signals: schema evolution requires encode version changes. Tests should verify decoding older records if versions change and that vector fields retain order.
