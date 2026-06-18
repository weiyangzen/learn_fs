<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/FSRegistryOperationsService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/FSRegistryOperationsService.java

## Purpose

Filesystem-backed RegistryOperations implementation using `_record` files under directories. The source was read as a complete 248-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class FSRegistryOperationsService extends CompositeService`, `public FSRegistryOperationsService()`, `public FileSystem getFs()`, `protected void serviceInit(Configuration conf)`, `public boolean mknode(String path, boolean createParents)`, `public void bind(String path, ServiceRecord record, int flags)`, `public ServiceRecord resolve(String path) throws PathNotFoundException,`, `public RegistryPathStatus stat(String path)`, `public boolean exists(String path) throws IOException`, `public List<String> list(String path)`.

## Control Flow

serviceInit obtains FileSystem; mknode creates directories; bind writes marshalled ServiceRecord to path/_record with overwrite semantics; resolve reads/parses/validates; stat/list/delete map registry paths to FS operations.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `File`, `FileNotFoundException`, `IOException`, `ArrayList`, `List`, `NotImplementedException`, `Configuration`, `FSDataInputStream`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

No registry-specific ACL support; addWriteAccessor/clearWriteAccessors throw NotImplementedException; stat requires `_record`, so empty nodes may not stat like ZK nodes.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/FSRegistryOperationsService.java -->
