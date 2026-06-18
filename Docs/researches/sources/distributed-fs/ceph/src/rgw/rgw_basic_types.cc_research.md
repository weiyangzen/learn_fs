# sources/distributed-fs/ceph/src/rgw/rgw_basic_types.cc

Purpose: implements JSON/XML conversion, bucket conversion/key formatting, shard encoding, principal formatting, account-id JSON handling, and owner variant parsing for fundamental RGW serialized types.

Important APIs/types/functions: `decode_json_obj(rgw_user&)`, `encode_json/encode_xml(rgw_user)`, `rgw_bucket::rgw_bucket(const rgw_user&, const cls_user_bucket&)`, `rgw_bucket::convert()`, `rgw_bucket::get_key()`, `rgw_bucket_shard::get_key()`, `encode/decode(rgw_bucket_shard)`, `encode_json_impl/decode_json_obj(rgw_zone_id)`, `rgw_data_placement_target::dump/decode_json()`, `rgw_bucket::dump/decode_json()`, `operator<<(Principal)`, `parse_owner()`, `to_string(rgw_owner)`, and JSON encode/decode for `rgw_owner`.

Control flow: bucket keys are assembled conditionally from tenant, bucket name, bucket id, and delimiters. Bucket JSON decode supports old placement fields by falling back to `pool`, `data_extra_pool`, and `index_pool` if `explicit_placement.data_pool` was absent. `parse_owner()` chooses account id when `rgw::account::validate_id()` succeeds, otherwise treats input as `rgw_user`.

State/persistence: these functions define persisted textual and binary-visible identifiers. `rgw_bucket_shard` binary encoding stores bucket then shard id. JSON conversion is used in admin/config/reporting surfaces.

Dependencies/integration: integrates with cls user bucket structures, `rgw_account`, XML/JSON helpers, pool/placement types, and IAM principal display.

Risks: bucket key delimiter choices are protocol-sensitive; tenant/name/id ambiguity can break metadata lookup. Principal streaming prints Role and AssumedRole both as `role/` style except service/wildcard/account special cases. Owner parsing depends on account-id validation staying stricter than user ids.

Test signals: encode/decode round-trips, legacy bucket JSON placement decode, tenant and empty bucket-id key formatting, shard key formatting, owner parsing for account/user strings, and principal ARN rendering.
