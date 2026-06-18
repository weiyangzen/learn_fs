# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/test-compact-format-property.xml

## Purpose
Compact Hadoop configuration fixture for tests that verify XML property parsing of attributes rather than nested elements.

## Important APIs, Types, And Functions
Contains two self-closing `<property>` elements with `name` and `value` attributes: `key.1=val1` and `key.2=val2`.

## Control Flow
Loaded by configuration parsers; it has no runtime code.

## State, Persistence, And Dependencies
No persistent state. It depends on Hadoop configuration parsing support for compact property syntax.

## Integration Points
Useful for tests around HttpFS server/testserver configuration loading where both standard and compact XML forms must be accepted.

## Risks
Some XML readers or validation paths may only expect child `<name>`/`<value>` elements, so this fixture guards compatibility with attribute form.

## Test Signals
Expected signal is that both keys resolve to their values after loading. Missing values indicate parser regression for compact properties.
