# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestMBeans.java

## Purpose
Tests Hadoop `MBeans` helper registration, additional ObjectName properties, service-name extraction, and cleanup.

## Important APIs, Types, And Functions
Implements `DummyMXBean`. Uses `MBeans.register()`, `MBeans.unregister()`, `MBeans.getMBeanName()`, `MBeans.getMbeanNameService()`, platform `MBeanServer`, and JMX `ObjectName`.

## Control Flow
Registration tests set `counter`, register the test object, read JMX attribute `Counter` from the platform server, assert the value, and unregister in `finally`. Additional-property test passes a `Map` containing `flavour=server`. Name test builds object names with and without custom properties and extracts service.

## State And Persistence Behavior
State is the test instance field `counter` and registered platform MBeans. `finally` cleanup is essential because ObjectNames are process-global.

## Dependencies And Integration Points
Integrates Hadoop metrics2 utility naming with Java Management Extensions and the `DummyMXBean` interface.

## Risks
Duplicate ObjectName registration can fail if prior cleanup did not run. Additional property ordering must be valid for JMX ObjectName syntax. Platform MBeanServer state is shared in the JVM.

## Test Signals
Signals are readable `Counter` values 23 and 42 through JMX and extracted service string `Service`.
