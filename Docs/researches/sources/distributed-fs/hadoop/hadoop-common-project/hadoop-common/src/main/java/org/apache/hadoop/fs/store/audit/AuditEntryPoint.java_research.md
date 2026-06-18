# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditEntryPoint.java

Purpose: source-retention marker annotation identifying filesystem methods that create and activate audit spans.

Important APIs, types, and functions: annotation type with `@Documented` and `@Retention(RetentionPolicy.SOURCE)`.

Control flow: no runtime flow because retention is source-only. It documents method-level audit boundaries and discourages nested entry-point calls.

State and persistence: no runtime state. It persists only in source and generated documentation.

Dependencies and integration points: used by filesystem source code and reviewers/static checks to identify audit entry points.

Risks and test signals: because retention is source-only, runtime reflection cannot enforce it. Test signals are source-level checks, code review, and documentation generation.
