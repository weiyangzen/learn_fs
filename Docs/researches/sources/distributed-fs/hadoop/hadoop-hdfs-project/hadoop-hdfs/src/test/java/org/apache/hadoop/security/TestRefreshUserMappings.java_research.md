# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/security/TestRefreshUserMappings.java

## Purpose
`TestRefreshUserMappings` verifies administrative refresh of cached user-to-group mappings and proxy-superuser group/host configuration through `DFSAdmin`.

## Important APIs, types, and functions
- `MockUnixGroupsMapping` implements `GroupMappingServiceProvider`; each uncached lookup returns incrementing group names in both list and set forms.
- `setUp()` installs the mock group mapping, sets a one-second cache TTL, starts MiniDFSCluster, and raises group logging.
- `testGroupMappingRefresh()` calls `DFSAdmin -refreshUserToGroupsMappings` and checks cache invalidation before and after timeout.
- `testRefreshSuperUserGroupsConfiguration()` configures proxy-user groups/hosts, mocks UGI real/effective users, calls `ProxyUsers.authorize`, writes a temporary XML resource with changed proxy groups, runs `DFSAdmin -refreshSuperUserGroupsConfiguration`, and validates authorization flips.
- `addNewConfigResource` writes a classpath XML resource and registers it with `Configuration.addDefaultResource`.

## Control flow
Group refresh first proves two immediate group lookups return cached identical values. It runs DFSAdmin refresh and asserts the next lookup differs. It then waits until TTL expiry yields a further changed mapping. Proxy refresh first authorizes only the user whose groups match `gr3,gr4,gr5`, then adds an XML resource changing allowed groups to `gr2`, runs DFSAdmin refresh, and expects the previously denied user to succeed while the previously allowed user fails.

## State and persistence behavior
The class starts a MiniDFSCluster per test and deletes it in teardown. It writes a temporary XML resource beside `hdfs-site.xml` on the classpath and deletes the file afterward. `Configuration.addDefaultResource` is global, so resource registration may outlive file deletion in process state.

## Dependencies and integration points
It integrates `Groups`, `GroupMappingServiceProvider`, `DFSAdmin`, `ProxyUsers`, `DefaultImpersonationProvider`, MiniDFSCluster admin RPCs, mocked `UserGroupInformation`, and classpath configuration loading.

## Risks and edge cases
The cache-timeout test uses polling and a multiplied timeout. The temporary default resource addition is process-global and could affect later tests if keys collide. The mock group mapper increments on both list and set lookups, so new callers can change expected sequences.

## Test signals
Passing confirms DFSAdmin refresh commands reach NameNode-side services, group caches are invalidated on demand and by TTL, and proxy-user authorization reloads group/host rules from refreshed configuration resources.
