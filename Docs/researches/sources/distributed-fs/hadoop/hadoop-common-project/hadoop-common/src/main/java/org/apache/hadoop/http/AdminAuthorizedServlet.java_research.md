<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/AdminAuthorizedServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/AdminAuthorizedServlet.java

Purpose: Jetty default servlet variant that gates static resource access behind Hadoop administrator authorization. It is used for protected HTTP contexts such as `/logs`.

Important APIs, types, and functions: `doGet()` calls `HttpServer2.hasAdministratorAccess()` with the servlet context, request, and response. Only authorized requests are forwarded to `DefaultServlet.doGet()`.

Control flow: requests fail closed when authorization returns false because the helper has already written an HTTP error. Authorized requests continue through Jetty's normal default static-file handling.

State and persistence: the servlet has no local state. Authorization state comes from servlet context attributes populated by `HttpServer2`.

Dependencies and integration points: depends on Jetty `DefaultServlet`, servlet request/response APIs, and `HttpServer2` admin ACL semantics.

Risks and test signals: correctness depends on context attributes `hadoop.conf` and `admins.acl`. Tests should cover authenticated admin access, non-admin rejection, missing remote user, disabled authorization, and static file serving behavior after approval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/AdminAuthorizedServlet.java -->
