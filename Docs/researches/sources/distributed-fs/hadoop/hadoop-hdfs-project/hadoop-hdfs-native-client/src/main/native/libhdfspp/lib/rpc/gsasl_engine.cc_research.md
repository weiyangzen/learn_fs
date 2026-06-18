# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/gsasl_engine.cc

Purpose: implements the GNU SASL-backed `SaslEngine` for GSSAPI/Kerberos authentication.

Important APIs and functions: `GSaslEngine::~GSaslEngine`, `gsasl_new`, `Start`, `init_kerberos`, `Step`, `Finish`, plus helpers `rc_to_status` and `base64_encode`.

Control flow: `Start` initializes GSASL context, creates a client session for the chosen mechanism, sets Kerberos properties, marks state waiting-for-data, and immediately runs `Step` with the initial challenge. `Step` calls `gsasl_step`, returns output tokens for `GSASL_NEEDS_MORE`/`GSASL_OK`, and updates success/failure state. `Finish` cleans up session and context.

State and persistence: owns raw `Gsasl *ctx_` and `Gsasl_session *session_`, protected during library calls by the GSSAPI mutex. No disk persistence.

Dependencies and integration: depends on GNU SASL, `hdfspp/locks.h`, logging, and base `SaslEngine`. Built conditionally by RPC CMake.

Risks and test signals: `Start` ignores the return value of `gsasl_new`, so failed initialization can lead to null-context use. `init_kerberos` calls `principal_.value()` with a TODO, so missing principal can throw or fail unexpectedly. `base64_encode` is unused. Tests should cover missing principal, init failure, concurrent auth, and cleanup on partial initialization.
