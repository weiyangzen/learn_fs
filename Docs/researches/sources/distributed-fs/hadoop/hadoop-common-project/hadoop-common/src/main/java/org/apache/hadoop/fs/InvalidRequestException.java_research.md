# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InvalidRequestException.java

Purpose: `InvalidRequestException` reports malformed user requests, such as missing required parameters or invalid parameter values, using checked IO exception semantics.

Important APIs: constructors with message and message/cause.

Control flow and state: simple `IOException` subclass with serial version `0L`; no additional fields or behavior.

Dependencies and integration: used by filesystem APIs that validate request objects/options and want callers to handle the failure as an IO-level request error.

Risks: broad checked type may be caught with generic IO failures, so messages and causes are important for diagnostics. No Hadoop classification annotations are present in this file.

Test signals: malformed builder/request validation, cause propagation, message stability, and caller differentiation from unsupported options or illegal arguments.
