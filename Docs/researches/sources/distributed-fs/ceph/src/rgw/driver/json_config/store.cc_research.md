# sources/distributed-fs/ceph/src/rgw/driver/json_config/store.cc

## Purpose

This file implements a JSON-backed factory for creating an immutable RGW config store. The intended flow is to read a JSON file containing `zonegroup`, `zone`, and `period_config`, decode those into RGW structures, normalize missing defaults, validate that the config describes a single-zone deployment, then return an `ImmutableConfigStore`.

## Important APIs, Types, and Functions

- `DecodedConfig` holds `RGWZoneGroup zonegroup`, `RGWZoneParams zone`, and `RGWPeriodConfig period_config`; its `decode_json()` method decodes those named JSON fields.
- `parse_config()` reads a file into a `bufferlist`, parses JSON with `JSONParser`, decodes into `DecodedConfig`, logs failures, and throws `std::system_error` on read/parse/decode errors.
- `sanity_check_config()` fills default ids/names/api name, adds default placement, initializes zone pool names, validates or creates the zonegroup zone entry, enables supported zone features for generated zone entries, and sets default placement target.
- `create_json_config_store()` creates a `DecodedConfig`, invokes parsing and sanity checks, then delegates to `create_immutable_config_store()`.

## Control Flow

The intended factory sequence is:

1. Read the JSON file.
2. Parse it.
3. Decode `zonegroup`, `zone`, and `period_config`.
4. Normalize empty zonegroup and zone identifiers to `"default"`.
5. Ensure `zone.placement_pools` has `"default-placement"` with `STANDARD`.
6. Run `rgw::init_zone_pool_names()` to populate pool names.
7. If a zonegroup already has one zone, verify that its id/name/master zone match the decoded zone.
8. If the zonegroup has no zones, call `rgw::add_zone_to_group()` with all supported zone features enabled.
9. Add `"default-placement"` to zonegroup placement targets and default placement.
10. Construct an immutable config store.

## State and Persistence Behavior

The JSON file is read once during factory creation. No live file watching or persistence is performed after the immutable store is created. Normalized config lives as value state in the returned `ImmutableConfigStore`.

Error handling is exception-based within parse/sanity helpers: file read failures throw system errors using the negated Ceph errno, parse/decode failures throw invalid-argument system errors, and helper failures throw the underlying errno.

## Dependencies and Integration Points

The implementation depends on Ceph `bufferlist`, `common/errno.h`, `common/ceph_json.h`, RGW zone helpers (`rgw_zone.h`, `rgw::init_zone_pool_names()`, `rgw::add_zone_to_group()`), and the immutable config store factory. It integrates with RGW deployments that want to bootstrap a static single-zone config from a JSON document.

## Risks and Edge Cases

- High risk: `parse_config()` currently returns `void` and decodes into a local `DecodedConfig config`; `create_json_config_store()` creates a separate default-constructed `DecodedConfig config`, calls `parse_config(dpp, filename.c_str())`, and then sanity-checks the still-empty local object. As written, successfully parsed JSON content is discarded, so the returned store is based on defaults rather than file content.
- `parse_config()` should likely return `DecodedConfig` or accept an output reference.
- `sanity_check_config()` unconditionally `emplace()`s `"default-placement"` into `zone.placement_pools` and zonegroup placement targets; existing entries are preserved, but incompatible existing definitions are not reconciled.
- The single-zone validator rejects zonegroups with more than one zone and requires exact id/name/master-zone matches for a one-zone group.
- `rgw_pool pool` is default-constructed, so correct pool naming depends on `init_zone_pool_names()` filling names later.
- Exceptions propagate from the factory; callers must expect construction-time throws rather than error-code returns.

## Test Signals

No tests are in this file. Important tests would include successful parsing with non-default ids/names, invalid JSON, missing file, one-zone mismatch errors, multi-zone rejection, generated single-zone defaults, and a regression that proves decoded JSON is actually passed into `create_immutable_config_store()`.
