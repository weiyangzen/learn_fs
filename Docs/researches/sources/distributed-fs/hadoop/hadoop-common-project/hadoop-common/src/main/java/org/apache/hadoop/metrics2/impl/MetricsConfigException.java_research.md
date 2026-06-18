## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsConfigException.java

Purpose: Package-private exception specializing `MetricsException` for configuration problems.

Important APIs/types/functions: Constructors mirror message and cause variants.

Control flow: Thrown by config loading/stringifying/class instantiation failures and caught by `MetricsSystemImpl.init` to allow nonfatal startup in some cases.

State and persistence: Standard exception state.

Dependencies/integration: Extends public metrics exception but remains implementation-local.

Risks/test signals: Catching this class in init makes startup behavior different from other runtime errors. Tests should distinguish typo/nonfatal config failures from fatal programming errors.
