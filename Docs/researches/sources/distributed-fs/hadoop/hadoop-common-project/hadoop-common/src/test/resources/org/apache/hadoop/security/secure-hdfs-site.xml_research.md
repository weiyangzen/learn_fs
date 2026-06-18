# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/org/apache/hadoop/security/secure-hdfs-site.xml

## Purpose
`secure-hdfs-site.xml` is a minimal HDFS security test configuration resource. It enables data transfer protection through a SASL properties resolver.

## Important Properties
The single property is `dfs.data.transfer.protection=org.apache.hadoop.security.SaslPropertiesResolver`.

## Control Flow
HDFS/security tests load the resource into `Configuration`; data-transfer setup code reads the property and configures SASL negotiation/protection behavior accordingly.

## State And Persistence
The file has no runtime state. It influences in-memory HDFS security configuration for tests.

## Dependencies And Integration Points
It integrates with Hadoop security tests under `org/apache/hadoop/security`, HDFS data transfer protection code, and `SaslPropertiesResolver`.

## Risks
The configured value is a class name in a property whose usual values may be expected to be protection levels in other contexts. Tests relying on this fixture are sensitive to how `dfs.data.transfer.protection` is parsed. Missing the resource from the test classpath disables the intended secure path.

## Test Signals
Secure HDFS transfer tests and SASL resolver tests should show that protected data transfer setup is used when this resource is loaded.
