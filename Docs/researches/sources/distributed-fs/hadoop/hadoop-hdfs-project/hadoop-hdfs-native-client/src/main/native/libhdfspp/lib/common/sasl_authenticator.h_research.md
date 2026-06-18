<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/sasl_authenticator.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/sasl_authenticator.h

## Purpose
Declares the DIGEST-MD5 SASL authenticator used for HDFS DataTransferProtocol token authentication.

## Important APIs, Types, And Functions
`DigestMD5Authenticator` exposes a constructor taking username/password and optional test nonce behavior, plus `EvaluateResponse`. Private helpers parse the first challenge, generate a client nonce, generate the first response, compute the response value, and tokenize challenge payloads.

## Control Flow
The server challenge is parsed, nonce/qop/realm fields are stored, a client nonce is generated, and a SASL response string is produced.

## State And Persistence
Per-authenticator state includes username, password, nonce, cnonce, realm, qop, and nonce count. It is in-memory and not wiped after use.

## Dependencies And Integration Points
Implemented in `sasl_digest_md5.cc` and used by DataNode/block reader authentication flows when token auth requires SASL.

## Risks
The header documents incomplete RFC 2831 support: no ISO-8859-1 conversion, weak challenge validation, fixed authzid/digest-uri/maxbuf behavior, and only `auth` QOP support. Password/token material remains in strings.

## Test Signals
Unit tests should cover known RFC-style challenge/response vectors, invalid challenges, unsupported QOP, deterministic mock nonce, and password/realm quoting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/sasl_authenticator.h -->
