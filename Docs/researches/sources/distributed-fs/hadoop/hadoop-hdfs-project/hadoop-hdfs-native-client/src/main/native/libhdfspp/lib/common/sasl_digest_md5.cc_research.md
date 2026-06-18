<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/sasl_digest_md5.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/sasl_digest_md5.cc

## Purpose
Implements the specialized DIGEST-MD5 SASL response generator for HDFS DataTransferProtocol authentication.

## Important APIs, Types, And Functions
`EvaluateResponse` calls `ParseFirstChallenge` then `GenerateFirstResponse`. `NextToken` tokenizes challenge key/value pairs. `GenerateCNonce` uses OpenSSL `RAND_bytes` and base64. `GenerateFirstResponse` builds the SASL response fields. `GenerateResponseValue` computes RFC 2831 MD5-sess response. Helpers quote strings, compute MD5 digests, and hex-encode binary data.

## Control Flow
The challenge parser walks tokens through lvalue, equals, rvalue, comma/end states and requires `algorithm=md5-sess`, `charset=utf-8`, and `nonce`. Response generation rejects non-`auth` QOP, emits fixed `digest-uri=hdfs/0`, max buffer 65536, optional realm, incremented nonce count, and a computed response hash.

## State And Persistence
The authenticator stores parsed server challenge fields, generated cnonce, and nonce count. Credentials and derived values remain in memory for the object's lifetime.

## Dependencies And Integration Points
Depends on OpenSSL RAND/MD5/ERR, `Base64Encode`, and `Status`. It integrates with block reader/DataNode SASL negotiation.

## Risks
OpenSSL MD5 APIs are deprecated in newer OpenSSL versions. Challenge validation is minimal, token parsing accepts a narrow character set, and release builds do not add extra safety. The fixed digest URI and authzid may not match every deployment. Response size is capped at 4096 after construction.

## Test Signals
Tests should cover valid HDFS token challenge responses, nonce-count increments, deterministic cnonce mode, RAND failure, unsupported qop, invalid/missing nonce, quoting embedded quotes, and OpenSSL 3 build warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/sasl_digest_md5.cc -->
