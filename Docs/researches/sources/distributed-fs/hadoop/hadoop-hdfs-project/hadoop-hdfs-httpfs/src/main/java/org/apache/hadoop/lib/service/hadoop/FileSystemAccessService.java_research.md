<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/hadoop/FileSystemAccessService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/hadoop/FileSystemAccessService.java

## Purpose
`FileSystemAccessService` is the concrete `FileSystemAccess` implementation. It initializes Hadoop authentication/configuration, validates allowed NameNodes, impersonates request users, caches per-user filesystems, instruments executor timings, and provides managed and unmanaged filesystem access paths.

## Important APIs, Types, And Functions
Configuration keys cover auth mode/keytab/principal, filesystem cache purge frequency/timeout, NameNode whitelist, and Hadoop config directory. `CachedFileSystem` tracks a cached `FileSystem`, use count, idle timestamp, timeout, release, and purge behavior. Main methods include `init`, `postInit`, `loadHadoopConf`, `getNewFileSystemConfiguration`, `createFileSystem`, `closeFileSystem`, `validateNamenode`, `execute`, `createFileSystemInternal`, public `createFileSystem`, `releaseFileSystem`, and `getFileSystemConfiguration`.

## Control Flow
Initialization configures UGI for kerberos or simple auth, loads `core-site.xml`/`hdfs-site.xml`, marks service-created filesystem config, clears server-side umask to `000`, disables HDFS FS cache, and loads the whitelist. Post-init registers instrumentation and schedules idle cache purging if enabled. `execute` validates user/config/defaultFS/whitelist, creates a proxy UGI, obtains a cached filesystem under `doAs`, checks health, starts a cron, invokes the executor, records timing, and releases the cache reference.

## State And Persistence
State includes Hadoop service config, service-created filesystem config, whitelist, purge timeout, unmanaged filesystem count, and a concurrent map of user to `CachedFileSystem`. Filesystem instances may be closed immediately or after idle timeout; cache entries remain indefinitely.

## Dependencies And Integration Points
It depends on Hadoop `FileSystem`, `UserGroupInformation`, Hadoop config files, `Instrumentation`, `Scheduler`, `ConfigurationUtils`, and `FSOperations` through the executor interface.

## Risks
Cache entries are never removed, only their filesystem is reopened/closed, so a very large user population grows the map. Whitelist validation uses only URI authority and lower-case matching. Public unmanaged filesystem users must call `releaseFileSystem` or metrics/cache counts leak. Kerberos login uses configured keytab/principal and fails service startup on errors.

## Test Signals
Tests should cover simple and kerberos config validation, missing Hadoop config dir/files, service-created config marker enforcement, defaultFS missing, whitelist accept/reject, executor exception wrapping, cron recording, cache reference counting/purge, umask clearing, and unmanaged count release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/hadoop/FileSystemAccessService.java -->
