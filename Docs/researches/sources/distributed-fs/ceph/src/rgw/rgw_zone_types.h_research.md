# sources/distributed-fs/ceph/src/rgw/rgw_zone_types.h

## Purpose

`rgw_zone_types.h` defines the lower-level serialized data types shared by RGW zone configuration code: name-to-id records, default metadata references, zone placement/storage-class records, public zone records, zonegroup placement/tiering records, and cloud-tier restore settings. It avoids radosgw-only includes because these types are part of serialized contracts. The file was read as a complete 766-line header.

## Important APIs, Types, and Functions

Important types include `RGWNameToId`, `RGWDefaultSystemMetaObjInfo`, `RGWZoneStorageClass`, `RGWZoneStorageClasses`, `RGWZonePlacementInfo`, `RGWZone`, `RGWDefaultZoneGroupInfo`, `RGWTierACLMapping`, `HostStyle`, `RGWZoneGroupPlacementTierS3`, `GlacierRestoreTierType`, `RGWZoneGroupTierS3Glacier`, `RGWTierType`, `RGWZoneGroupPlacementTier`, and `RGWZoneGroupPlacementTarget`.

Key helpers include storage class lookup/mutation (`find()`, `exists()`, `set_storage_class()`, `remove_storage_class()`), placement pool getters (`get_data_pool()`, `get_data_extra_pool()`, `get_compression_type()`), zone sync/feature predicates (`syncs_from()`, `supports()`), target-bucket naming for cloud S3 tiers, and user tag checks on placement targets.

## Control Flow

Most control flow is inline compatibility decoding and simple selection logic. `RGWZonePlacementInfo::decode()` reconstructs legacy standard data/compression fields into `RGWZoneStorageClasses`. `RGWZone::decode()` handles legacy id/name and optional sync/redirect/feature fields. `RGWZoneGroupPlacementTier::decode()` branches by serialized version and tier type to decide whether to decode S3 and glacier substructures. `RGWZoneGroupPlacementTarget::user_permitted()` allows all users when no tags are configured or requires at least one matching user tag.

## State and Persistence Behavior

Every major type has explicit Ceph buffer encoding via `WRITE_CLASS_ENCODER`. `RGWZoneStorageClasses` maintains an in-memory-only `standard_class` pointer into its map and resets it after copy/assignment/decode. `RGWZone` persists public zone behavior such as endpoints, logging flags, read-only flag, tier type, sync sources, redirect zone, bucket index shard default, and supported features. Placement/tier records persist storage-class pools, compression, inline-data preference, cloud endpoint credentials, target path/bucket templates, ACL mappings, multipart thresholds, read-through restore controls, and glacier restore settings.

## Dependencies and Integration Points

The header depends on Ceph types, bucket layout, zone features, pool/ACL/placement types, and formatter declarations. It is included by `rgw_zone.h`, admin tooling, config-store implementations, tiering/sync code, and bucket placement logic. It integrates with object placement via `rgw_placement_rule`, bucket index layout via `rgw::BucketIndexType`, and external cloud-tier sync via S3/glacier tier settings.

## Risks and Edge Cases

Serialized layout changes are high risk because these records live in cluster metadata. `RGWZoneStorageClasses::remove_storage_class()` refuses to remove the default class when passed an empty storage class, which is intentional but easy to miss. Optional pool/compression values can result in empty static fallback values. Cloud tier bucket-name templates are lowercased and token-substituted; missing `${bucket}` in target-by-bucket mode appends the bucket name, which can surprise administrators. The S3 tier stores access keys/secrets in serialized config, so dumps and handling paths must be careful.

## Test Signals

Test signals include dencoder round trips, legacy decode tests for placement and tier versions, storage-class existence/fallback unit tests, user tag permission tests, cloud target-bucket-name template tests, glacier restore config tests, and integration tests for bucket placement selection and cloud tier sync configuration.
