## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/DefaultMetricsSystem.java

Purpose: Public static access point for the default Hadoop metrics system singleton and source-name uniqueness support.

Important APIs/types/functions: Provides initialize/instance/shutdown helpers, mini-cluster mode controls, source-name allocation/removal, and convenience registration around `MetricsSystemImpl`.

Control flow: Static methods delegate lifecycle to the singleton implementation, track mini-cluster mode, and generate unique source names when duplicate registration is allowed before monitoring starts.

State and persistence: Static process state including singleton system, source-name tracking, and mini-cluster mode flag. No persistence.

Dependencies/integration: Used by Hadoop components that do not manage their own metrics system and by `MetricsSystemImpl` during registration and shutdown.

Risks/test signals: Static state can leak across tests. Test suites should reset/shutdown, verify duplicate-name suffixing, mini-cluster ref counting, and source name removal.
