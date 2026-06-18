# Research: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSInputStream.java

Purpose: COS object input stream with multi-range support. It extends `MultiRangeObjectInputStream` to efficiently read remote objects in bounded ranges.

Important APIs and control flow: constructors store bucket, key, COS client, start position, retry policy, and object content length from metadata. `createStream(startPos, endPos)` builds a `GetObjectRequest`, sets an inclusive range capped at content length minus one, copies the retry policy, and retries 404 responses for eventual consistency while failing immediately for other COS service exceptions. It returns a `BufferedInputStream` over object content.

State, dependencies, integration, risks, tests: state includes object length, current inherited position, and retry policy. Dependencies include Tencent COS SDK, Apache HTTP status, Alluxio multi-range stream base, and object metadata. Risks include range math for empty objects, object mutations after metadata fetch, and retry behavior only for not-found responses.
