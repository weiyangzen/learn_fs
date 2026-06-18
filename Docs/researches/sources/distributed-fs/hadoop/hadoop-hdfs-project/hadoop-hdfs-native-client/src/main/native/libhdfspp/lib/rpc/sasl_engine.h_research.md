# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/sasl_engine.h

Purpose: declares the abstract SASL engine interface and common mechanism/credential state.

Important APIs and types: `SaslMethod`, `SaslEngine::State`, `SetKerberosInfo`, `SetPasswordInfo`, `ChooseMech`, `GetState`, abstract `Start`, `Step`, `Finish`, and public `chosen_mech_`.

Control flow: expected lifecycle is unstarted, start to waiting-for-data, repeated step to success/failure, then finish. Concrete backends implement token exchange with Cyrus or GSASL.

State and persistence: state enum, optional principal/realm/id/password, raw `SaslProtocol *`, and chosen mechanism. No persistent state.

Dependencies and integration: depends on libhdfspp `Status` and optional wrapper. Used by `SaslProtocol` and backend engines selected at build time.

Risks and test signals: comments duplicate the transition diagram. `chosen_mech_` is public mutable state, and no copy prevention exists in base class. Tests should verify backend implementations respect state preconditions and cleanup even after failure.
