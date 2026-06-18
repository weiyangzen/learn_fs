## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsException.java

Purpose: Runtime exception class for metrics framework configuration, registration, and type errors.

Important APIs/types/functions: Provides message-only, cause-only, and message-plus-cause constructors.

Control flow: Thrown throughout registry duplicate checks, annotation processing, filters, and metrics system misuse paths.

State and persistence: Standard exception state only.

Dependencies/integration: Extends `RuntimeException`; subclasses include implementation configuration exceptions.

Risks/test signals: Because it is unchecked, code paths must validate inputs early and produce actionable messages. Tests should assert duplicate metric/tag and unsupported annotation type failures.
