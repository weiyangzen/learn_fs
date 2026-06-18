# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/cyrus_sasl_engine.cc

Purpose: implements the Cyrus SASL-backed `SaslEngine` for Kerberos/GSSAPI authentication.

Important APIs and functions: `CySaslEngine` constructor/destructor, `InitCyrusSasl`, `Start`, `Step`, `Finish`, `SaslError`, error helpers, callbacks `sasl_my_log`, `sasl_getopt`, `get_path`, `get_name`, `getrealm`, and singleton `CyrusPerProcessData`.

Control flow: process-wide Cyrus is lazily initialized under the GSSAPI mutex. Per-connection `sasl_client_new` uses callbacks bound to the engine. `Start` calls `sasl_client_start` for the chosen mechanism, transitions to success or waiting-for-data, and returns the first token. `Step` feeds server data to `sasl_client_step` and returns the next token. `Finish` disposes the SASL connection.

State and persistence: per-engine state includes `sasl_conn_t *conn_` and per-connection callbacks. `CyrusPerProcessData` is a Meyers singleton that initializes and later calls `sasl_done`. No disk persistence, but global library state is process-wide.

Dependencies and integration: depends on Cyrus SASL, `hdfspp/locks.h`, logging, and base `SaslEngine`. Integrated by `SaslProtocol` when the build enables Cyrus SASL.

Risks and test signals: global SASL/GSSAPI locking is critical. Callback functions return pointers into optional strings and assume principal/id are set for selected callback IDs. `PLUGINDIR` is hard-coded to `/usr/local/lib/sasl2`. Tests should cover initialization failure, missing credentials, multi-threaded auth, state transitions, and cleanup paths.
