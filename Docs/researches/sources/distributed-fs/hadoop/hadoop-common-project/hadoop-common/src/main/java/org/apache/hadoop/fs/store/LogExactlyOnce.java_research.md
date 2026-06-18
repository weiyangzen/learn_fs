# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/LogExactlyOnce.java

Purpose: helper that logs a warning message only once per helper instance, suppressing repeated noisy warnings.

Important APIs, types, and functions: constructor accepting an SLF4J `Logger`, `warn(String, Object...)`, and reset/testing support if present.

Control flow: first warning call logs through the wrapped logger; later calls are suppressed by an atomic flag.

State and persistence: holds logger reference and in-memory boolean/atomic logged state. No persistence.

Dependencies and integration points: used by `HttpReferrerAuditHeader` to avoid flooding logs when URI/header construction repeatedly fails.

Risks and test signals: suppressing repeated messages can hide recurring failures after the first occurrence. Tests should cover first-call logging, later suppression, thread safety under concurrent warnings, and reset/test hooks if available.
