## sources/distributed-fs/ceph/src/rgw/rgw_oidc_provider.cc

Purpose: implements JSON dump/decode and test fixtures for OIDC provider metadata.

Important APIs/functions: `RGWOIDCProviderInfo::dump()` writes id, provider URL, ARN, creation date, tenant, client ids, and thumbprints. `decode_json()` reads the same fields. `generate_test_instances()` returns a populated provider plus a default provider for encoding tests.

Control flow: admin/API code can decode JSON into provider info, persist it through class encoding, and dump it back for responses.

State and persistence: provider info is a serializable value object; persistence is handled by metadata/config code elsewhere.

Dependencies/integration: depends on Ceph JSON/Formatter support and the header's encoder.

Risks and test signals: creation date is a plain string, so validation is external. Tests should cover JSON round trips, empty client/thumbprint vectors, tenant/account id behavior, and binary encode compatibility.
