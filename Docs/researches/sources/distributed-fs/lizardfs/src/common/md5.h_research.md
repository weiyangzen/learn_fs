<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/md5.h -->
# sources/distributed-fs/lizardfs/src/common/md5.h

## Purpose
Declares the MD5 context and digest/authentication helper functions. The source was read completely for this report.

## Important APIs, Types, And Functions
`md5ctx` stores four state words, two count words, and a 64-byte buffer; functions initialize, update, finalize, build challenge responses, and parse 32-character hex strings.

## Control Flow
Header has no runtime flow beyond declarations.

## State And Persistence Behavior
Caller owns all digest state; serialized/persisted digest use happens in higher layers.

## Dependencies And Integration Points
Used by password/auth protocol code.

## Risks And Edge Cases
The API uses raw pointers and a `uint32_t` input length, limiting a single update call to 4 GiB-1 bytes and relying on caller buffer validity.

## Test Signals
Compile coverage plus known-vector tests are recommended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/md5.h -->
