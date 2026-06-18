<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/JettyUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/JettyUtils.java

Purpose: tiny Jetty constants holder for Hadoop HTTP code.

Important APIs, types, and functions: `UTF_8` is the content-type charset suffix `charset=utf-8`; `HEADER_SIZE` is 64 KiB.

Control flow: no control flow beyond static constant access.

State and persistence: no mutable or persistent state.

Dependencies and integration points: used by servlet and Jetty setup code that need shared charset/header-size constants.

Risks and test signals: low risk. Compatibility tests should ensure callers relying on 64 KiB header sizing still match the configured defaults in `HttpServer2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/JettyUtils.java -->
