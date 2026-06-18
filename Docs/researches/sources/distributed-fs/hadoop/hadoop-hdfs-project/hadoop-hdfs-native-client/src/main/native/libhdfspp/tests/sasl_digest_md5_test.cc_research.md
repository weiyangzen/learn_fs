# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/sasl_digest_md5_test.cc

## Purpose

This unit test validates DIGEST-MD5 response generation for token-based SASL authentication.

## Important APIs, types, and functions

It constructs a `DigestMD5Authenticator` with a username, password, and client mode, sets deterministic `cnonce_`, calls `EvaluateResponse()`, and checks that the generated response contains a known MD5 digest.

## Control flow, state, and persistence

The test feeds a server challenge containing realm, nonce, qop, charset, and algorithm. `EvaluateResponse()` parses the challenge and writes a response string. The fixed client nonce makes the digest deterministic. No persistent state is created beyond authenticator instance fields.

## Dependencies and integration points

The file depends on `common/sasl_authenticator.h`, gtest, and protobuf cleanup. It validates the lower-level credential math that can feed datanode SASL streams and RPC SASL mechanisms.

## Risks and test signals

The test catches regressions in MD5-sess digest formatting and nonce handling. It covers one challenge shape only; additional qop/charset/error cases would improve confidence. Because it inspects substring presence, it does not fully validate all response fields.
