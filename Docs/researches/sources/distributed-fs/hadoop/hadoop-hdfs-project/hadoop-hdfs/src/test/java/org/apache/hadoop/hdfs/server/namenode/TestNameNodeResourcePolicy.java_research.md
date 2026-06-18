# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeResourcePolicy.java

Purpose: Unit-tests `NameNodeResourcePolicy.areResourcesAvailable` across combinations of required and redundant resources, including excessive minimum redundant resource settings.

Important APIs and functions: `testResourceScenario` builds mocked `CheckableNameNodeResource` instances with controlled `isRequired` and `isResourceAvailable` responses. Public tests cover single redundant, single required, multiple redundant, multiple required, mixed required/redundant, and excessive minimum redundant resources. The excessive-minimum test also captures logs from `NameNodeResourcePolicy`.

Control flow: Each scenario constructs a collection containing a requested count of redundant and required resources. It marks the first N resources in each category unavailable, then calls `areResourcesAvailable(resources, minimumRedundantResources)`. Assertions encode the policy: all required resources must be available, and at least the configured minimum count of redundant resources must be available.

State and persistence behavior: No persistence exists. All state is mocked in-memory resource availability for a single policy call.

Dependencies and integration points: Depends on Mockito, JUnit assertions, SLF4J logger capture through `GenericTestUtils.LogCapturer`, and the `CheckableNameNodeResource` interface. It isolates the pure policy used by `NameNodeResourceChecker`.

Risks: The test is concise but pins policy behavior tightly. A future policy that distinguishes no redundant resources from insufficient redundant resources would require scenario updates. The log assertion couples the excessive-minimum path to message content.

Test signals: Passing means required-resource failures always make the policy unavailable, redundant-resource failures are tolerated only down to the configured minimum, impossible minimums fail, and the failure path emits a "Resources not available." log signal.
