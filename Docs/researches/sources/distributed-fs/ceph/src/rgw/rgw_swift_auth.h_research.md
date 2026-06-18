# sources/distributed-fs/ceph/src/rgw/rgw_swift_auth.h

## Purpose
`rgw_swift_auth.h` declares Swift authentication engines, appliers, default strategy wiring, signature helpers, and the Swift auth REST handler.

## Important APIs, Types, and Functions
`TempURLApplier`, `TempURLEngine`, `SignedTokenEngine`, `ExternalTokenEngine`, `SwiftAnonymousApplier`, and `SwiftAnonymousEngine` define authentication units. `DefaultStrategy` constructs and orders TempURL, signed-token, optional Keystone, optional external-token, and anonymous engines while producing local/remote/temp-url appliers. Signature templates define digest size/name metadata, `SignatureHelperT`, and `FormatSignature` for bare hex or `name:base64url` signatures. `RGW_SWIFT_Auth_Get`, `RGWHandler_SWIFT_Auth`, and `RGWRESTMgr_SWIFT_Auth` expose the auth endpoint.

## Control Flow
The default strategy adds engines with `SUFFICIENT` control and conditionally enables Keystone/external auth based on config. Engines receive tokens through extractor structs reading `HTTP_X_AUTH_TOKEN` and `HTTP_X_SERVICE_TOKEN`.

## State and Persistence Behavior
The header declares request-local applier state and engine references to config, SAL driver, token extractors, and factories. It does not define durable storage.

## Dependencies and Integration Points
Includes RGW REST/auth/filter/Keystone/SAL/B64 headers, Ceph crypto types, Formatter, and XML-adjacent request classes. It is central to Swift REST authentication setup.

## Risks
Factories return heap-allocated composed applier wrappers, so ownership must remain consistent with `aplptr_t`. Signature template defaults use `-1` in unsigned constants for unsupported types, which should never instantiate. Anonymous auth is sufficient and must remain last to avoid bypassing real token failures.

## Test Signals
Compile tests should instantiate all supported hash/flavor combinations. Integration tests should verify engine ordering, Keystone/external enablement flags, extractor behavior, factory-created appliers, and Swift auth manager handler selection.
