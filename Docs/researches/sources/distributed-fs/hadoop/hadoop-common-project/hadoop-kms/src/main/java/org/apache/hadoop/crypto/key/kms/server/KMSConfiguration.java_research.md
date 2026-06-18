# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSConfiguration.java

## Purpose
`KMSConfiguration.java` defines KMS configuration keys, defaults, resource loading, ACL-file freshness checks, and startup validation for required system properties.

## Important APIs, Types, and Functions
Constants cover config file names, prefixes, HTTP host/port/admin ACLs, SSL enablement, provider URI, cache toggles and timeouts, audit aggregation, metrics naming, audit logger classes, and per-key authorization enablement. `getKMSConf`, `getACLsConf`, `getConfiguration`, `isACLsFileNewer`, and `validateSystemProps` are the operational methods.

## Control Flow
Static initialization adds `kms-default.xml` and `kms-site.xml` as Hadoop default resources. `getConfiguration` builds a `Configuration`, optionally using absolute `kms.config.dir` to add file URLs for named resources. `isACLsFileNewer` only checks filesystem modification time when `kms.config.dir` is set and requires a 100 ms freshness margin. `validateSystemProps` aborts if `kms.config.dir` or `log4j.configuration` is missing.

## State and Persistence
The class writes no state. It controls how persisted XML resources are loaded and how `kms-acls.xml` freshness is detected for reload.

## Dependencies and Integration Points
It is used by nearly every KMS server class: `KMSWebServer` for network and SSL config, `KMSWebApp` for provider/cache/audit setup, `KMSACLs` for ACL loading, and shell scripts that set system properties.

## Risks
When `kms.config.dir` is absent, ACL freshness checking always returns false, so classpath ACLs are not hot-reloaded. Absolute-path validation is strict and fails startup for relative config dirs. Default provider URI points to a user-home JCEKS file, which is suitable for defaults/tests but deployment-specific.

## Test Signals
Tests should cover classpath and file URL resource loading, relative config-dir rejection, ACL freshness margin, default values matching `kms-default.xml`, and `validateSystemProps` failure messages.
