# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/pom.xml

Purpose: Maven WAR module for Hadoop Auth example web application and client.

Important APIs, types, and functions: artifact `hadoop-auth-examples` packages as `war`; dependencies include servlet API provided by the container, `hadoop-auth`, SLF4J, reload4j, and slf4j-reload4j. Build plugins set the WAR name, skip deploy, and configure `exec-maven-plugin` to run `WhoClient` with `${url}`.

Control flow: Maven builds a WAR containing `WhoServlet`, `RequestLoggerFilter`, and `web.xml`; the exec plugin can run the example client against a supplied URL.

State and persistence: no application state in the POM. Build output is `hadoop-auth-examples.war`.

Dependencies and integration points: integrates with the parent Hadoop build, servlet container deployment, Hadoop auth filter library, and logging runtime.

Risks and test signals: examples use older web.xml/servlet configuration while the dependency is marked Jakarta in Maven but imports in sources are `javax.servlet`, so dependency alignment should be verified through compilation. Test signals include WAR packaging and running the exec goal against the deployed sample endpoints.
