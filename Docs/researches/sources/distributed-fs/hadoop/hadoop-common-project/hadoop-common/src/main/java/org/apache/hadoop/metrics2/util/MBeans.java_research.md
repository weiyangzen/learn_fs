<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/MBeans.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/MBeans.java

## Purpose
`MBeans` is a public stable utility for registering and unregistering Hadoop-standard JMX MBeans under object names shaped as `Hadoop:service=...,name=...[,extra=...]`.

## Important APIs and Types
Main APIs are `register(serviceName, nameName, Object)`, `register(serviceName, nameName, Map<String,String>, Object)`, `unregister(ObjectName)`, `getMbeanNameService(ObjectName)`, `getMbeanNameName(ObjectName)`, and test-visible `getMBeanName`.

## Control Flow
Registration builds an `ObjectName` with `DefaultMetricsSystem.newMBeanName`, then calls the platform MBean server. Duplicate instances are logged and return null. Other exceptions are logged and return null. Unregister removes the MBean from the platform server and then removes the name from `DefaultMetricsSystem`.

## State and Persistence
State lives in the JVM MBean server and in `DefaultMetricsSystem`'s MBean name registry. This class itself is stateless.

## Dependencies and Integration Points
It integrates Hadoop services with JMX and metrics system name tracking. Additional ObjectName properties are joined directly from the provided map.

## Risks and Test Signals
Additional property keys/values are not quoted or escaped here, relying on `ObjectName` creation to reject invalid names. The parser regex only recognizes the standard prefix/order. Tests should cover successful registration/unregistration, duplicate handling, null property rejection, invalid names returning null, parser failures, and cleanup of metrics system MBean names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/MBeans.java -->
