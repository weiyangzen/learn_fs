# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/sasl_engine.cc

Purpose: implements base `SaslEngine` credential setters, state accessor, destructor, and mechanism selection.

Important APIs and functions: `GetState`, destructor, `SetKerberosInfo`, `SetPasswordInfo`, and `ChooseMech`.

Control flow: callers set credentials while unstarted, then pass available server mechanisms to `ChooseMech`. The implementation currently accepts only `GSSAPI`, deep-copies the chosen method, and returns true. If none match, it sets error state and clears `chosen_mech_`.

State and persistence: inherited state includes current state and optional principal/realm/id/password plus chosen mechanism. No disk persistence.

Dependencies and integration: depends on base header and logging/status indirectly. Used by Cyrus and GSASL implementations and by SASL protocol negotiation.

Risks and test signals: `ChooseMech` returns `auth.mechanism.c_str()` as a bool, which works as non-null true but is semantically odd. Only GSSAPI is supported despite password setters. Tests should cover empty mechanism lists, non-GSSAPI choices, and deep-copy lifetime after input vector destruction.
