# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestHttpCrossOriginFilterInitializer.java

Purpose: Unit test for extracting CORS filter parameters from Hadoop configuration.

Important APIs/types/functions: `HttpCrossOriginFilterInitializer.getFilterParameters`, `HttpCrossOriginFilterInitializer.PREFIX`, and `Configuration`.

Control flow: sets two keys under the initializer prefix and one unrelated key. Calls `getFilterParameters` and verifies prefix-stripped keys are present while the out-of-scope key is absent.

State and persistence: local configuration map only.

Dependencies/integration points: Hadoop HTTP CORS filter initialization.

Risks: only tests extraction, not actual filter registration or CORS behavior.

Test signals: confirms prefix scoping and key stripping for CORS filter parameters.
