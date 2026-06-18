# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/SignatureInfo.java

Purpose: `SignatureInfo` is an immutable value object holding parsed AWS signature metadata before it is converted to `AwsAuthInfo`.

Important fields/APIs are `Version` (`V4`, `V2`), access ID, signature, credential date, full timestamp, signed headers, credential scope, algorithm, and `signPayload`. Getters expose every field. Control flow is absent; parser utilities construct this object, and `AwsSignatureProcessor`/`StringToSignProducer` consume it.

State and persistence are final in-memory values only. Dependencies are none beyond Java. Integration points include V2/V4 header parsers, V4 query parser, canonical string production, and authentication handoff. The `signPayload` flag distinguishes header-signed payloads from presigned URLs where payload is treated as unsigned. Risks include no internal validation, so downstream code must handle null/empty fields correctly; V2 instances intentionally have empty V4-specific fields. Tests validate selected getters in V2 and V4 parser tests.
