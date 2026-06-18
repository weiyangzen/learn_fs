# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/KeystoneV3Access.java

## Purpose
`KeystoneV3Access` is a JOSS `Access` implementation carrying Keystone v3 token and endpoint URLs.

## Important APIs, Types, And Functions
It stores internal URL, preferred region, public URL, and token. It implements `getInternalURL`, `getPublicURL`, `getTempUrlPrefix`, `getToken`, `isTenantSupplied`, and `setPreferredRegion`.

## Control Flow
The object is a simple value holder. `setPreferredRegion` updates the region field and logs it; `getTempUrlPrefix` returns null, indicating temp URL support is not implemented here.

## State And Persistence
State is in-memory endpoint/token data for the lifetime of the JOSS account access object.

## Dependencies And Integration Points
It is produced by `KeystoneV3AccessProvider.authenticate` and consumed by JOSS Swift clients.

## Risks
The field name `mPrefferedRegion` is misspelled but internally consistent. Returning null for temp URL prefix may break callers expecting temporary URL support.

## Test Signals
No direct test is present in this subset. Coverage is expected through Keystone authentication and Swift client construction paths.
