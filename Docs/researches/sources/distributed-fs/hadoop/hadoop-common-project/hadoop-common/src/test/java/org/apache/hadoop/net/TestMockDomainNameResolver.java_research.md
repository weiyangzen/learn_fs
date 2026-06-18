# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestMockDomainNameResolver.java

## Purpose
Tests creation and default behavior of `MockDomainNameResolver` through the configured `DomainNameResolverFactory`.

## Important APIs, Types, And Functions
Uses `Configuration`, `CommonConfigurationKeys.HADOOP_DOMAINNAME_RESOLVER_IMPL`, `DomainNameResolverFactory.newInstance()`, `getAllByDomainName()`, and constants from `MockDomainNameResolver`.

## Control Flow
`@BeforeEach` configures the resolver implementation class. One test creates the resolver and asserts the default domain returns two expected IP addresses. The other asserts lookup of the configured unknown domain throws `UnknownHostException`.

## State And Persistence Behavior
Configuration is per-test. Resolver instance has default in-memory maps.

## Dependencies And Integration Points
Validates that Hadoop configuration can instantiate a custom domain resolver and that consumers see deterministic forward lookup behavior.

## Risks
Class-name configuration must remain compatible with factory reflection. Test name `testMockDomainNameResolverCanNotBeCreated()` actually verifies failed lookup, not construction failure.

## Test Signals
Expected signals are two addresses `10.1.1.1` and `10.1.1.2` for the known domain and an exception for `unknown.foo.bar`.
