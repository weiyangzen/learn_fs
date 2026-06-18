# sources/distributed-fs/ceph/src/rgw/driver/json_config/store.h

## Purpose

This header declares the JSON config store factory for RGW SAL configuration. It is a small public entry point that converts a JSON file path into a `std::unique_ptr<ConfigStore>`, implemented as an immutable config store.

## Important APIs, Types, and Functions

- Includes `driver/immutable_config/store.h`, making the immutable store and `ConfigStore` abstraction available.
- Declares `rgw::sal::create_json_config_store(const DoutPrefixProvider* dpp, const std::string& filename) -> std::unique_ptr<ConfigStore>`.

## Control Flow

Consumers call the factory with a logging prefix provider and JSON filename. The implementation handles file IO, JSON parsing, config normalization, and immutable store construction.

## State and Persistence Behavior

The header declares no state. The returned store is expected to contain a snapshot of decoded file state, with no runtime persistence or update mechanism.

## Dependencies and Integration Points

This is the integration point for code that wants `ConfigStore` semantics from a JSON file rather than RADOS or another mutable config backend. It relies on immutable config store declarations and RGW SAL config types.

## Risks and Edge Cases

- The header documentation says the factory parses zonegroup and zone from the given JSON filename; the implementation also decodes `period_config`.
- The API uses exceptions indirectly through the implementation, despite returning a pointer rather than an error-code wrapper.
- There is no schema type exposed here, so callers must know the expected JSON keys out of band.

## Test Signals

No direct tests exist here. Interface coverage is compile-time; behavioral coverage belongs to the `.cc` factory tests.
