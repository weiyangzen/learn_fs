# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/DummyMXBean.java

## Purpose
Minimal MXBean interface used by MBean registration tests.

## Important APIs, Types, And Functions
Defines `int getCounter()`.

## Control Flow
No implementation or branching; classes implementing this interface expose a JMX `Counter` attribute.

## State And Persistence Behavior
No state in the interface. Implementations provide the value.

## Dependencies And Integration Points
Used by `TestMBeans` so Java's platform `MBeanServer` recognizes the implementation as an MXBean-compatible management interface.

## Risks
Method naming controls the exported JMX attribute name. Changing `getCounter()` would break JMX attribute assertions.

## Test Signals
Successful MBean registration should allow reading attribute `Counter`.
