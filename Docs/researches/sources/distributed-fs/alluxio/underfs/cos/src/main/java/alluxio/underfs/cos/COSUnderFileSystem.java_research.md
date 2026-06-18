# Research: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSUnderFileSystem.java

Purpose: Tencent Cloud COS object-store `UnderFileSystem` built on `ObjectUnderFileSystem`.

Important APIs and control flow: `createInstance` validates access key, secret key, region, and app id, creates `BasicCOSCredentials`, `ClientConfig`, and `COSClient`, then derives internal bucket name as `<bucket>-<appId>`. It implements object copy, empty object creation, output stream creation, single and batch delete, listing chunks with delimiter/prefix/max keys, directory detection via folder marker or listing, object status from metadata including ETag/CRC, permissions defaults, root key, client config timeouts, and `openObject` using `COSInputStream`.

State, dependencies, integration, risks, tests: state is the COS client and bucket names. Persistence is remote COS objects and local temp files during writes. Dependencies include Tencent COS SDK, Alluxio object UFS base, property keys, and path normalization. Risks include inconsistent bucket name use in `deleteObjects` versus internal bucket, object-store directory marker semantics, no ACL/mode integration, and SDK exception wrapping gaps.
