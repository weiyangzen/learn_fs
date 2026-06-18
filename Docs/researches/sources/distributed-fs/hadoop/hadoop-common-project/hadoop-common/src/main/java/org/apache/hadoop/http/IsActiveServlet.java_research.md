<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/IsActiveServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/IsActiveServlet.java

Purpose: abstract load-balancer health servlet for active/standby Hadoop services. It reports success only when subclass-specific HA state is active.

Important APIs, types, and functions: constants define servlet name `isActive`, path `/isActive`, and response text. `doGet()` sets `Connection: close`, calls abstract `isActive()`, writes HTTP 200 with active text, or sends HTTP 405 with not-active text.

Control flow: subclasses implement `isActive()` against NameNode, ResourceManager, Router, or other HA state. Load balancers poll the endpoint and route only to instances returning OK.

State and persistence: no local state; active status comes from subclass implementation.

Dependencies and integration points: integrates servlet APIs with Hadoop HA services through subclassing.

Risks and test signals: HTTP 405 is a deliberate non-OK status but may need load-balancer-specific interpretation. Tests should cover active and inactive statuses, connection-close header, response body, and subclass failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/IsActiveServlet.java -->
