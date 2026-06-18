# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/cyrus_sasl_engine.h

Purpose: declares `CySaslEngine`, the Cyrus SASL implementation of the abstract `SaslEngine`.

Important APIs and types: constructor/destructor, overrides `Start`, `Step`, `Finish`, private `InitCyrusSasl`, `SaslError`, `sasl_conn_t *conn_`, and per-connection callback vector. Callback functions are friends so they can read engine credential fields.

Control flow: callers configure base SASL info, choose a mechanism, then call `Start`/`Step`/`Finish`. Implementation state follows the base `SaslEngine::State` model.

State and persistence: owns a Cyrus connection pointer and callback vector. No persistent storage.

Dependencies and integration: includes Cyrus `<sasl/sasl.h>` and base `sasl_engine.h`; included only when the build enables Cyrus SASL.

Risks and test signals: raw `sasl_conn_t *` ownership must be disposed exactly once. Friend callbacks couple external C callback behavior to internal optional credential state; tests should exercise absent optional values and destructor-after-partial-init.
