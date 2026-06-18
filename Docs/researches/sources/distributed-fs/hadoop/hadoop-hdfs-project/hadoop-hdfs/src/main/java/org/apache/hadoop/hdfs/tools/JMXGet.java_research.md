# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/JMXGet.java`

## Purpose

`JMXGet` is a command-line utility for querying Hadoop MBeans, typically NameNode or DataNode metrics, either from the local platform MBean server, an RMI JMX server, or an explicit local VM connector URL.

## Important APIs, Types, and Functions

- Setters configure service, port, server, and local VM connector URL.
- `init` builds a JMX service URL or uses the platform MBean server, connects, logs domains/counts to stderr, and queries `Hadoop:service=<service>,*` object names.
- `printAllValues` prints every attribute from all matched object names.
- `printAllMatchedAttributes` prints attributes whose names match a regular expression prefix via `lookingAt`.
- `getValue` returns the first matching attribute value across queried object names, ignoring missing attributes and missing getter reflections.
- `parseArgs` defines Commons CLI options and parses remaining metric keys.
- `main` configures the instance, handles help, initializes, and prints either all values or requested keys.

## Control Flow

CLI parsing accepts `-service`, `-server`, `-port`, `-localVM`, and `-help`. If no port/local VM is supplied, `init` uses the same JVM's platform MBean server, which is useful for tests. Otherwise it constructs an RMI URL or uses the supplied connector URL. After querying object names, `main` prints all attributes when no keys are supplied; otherwise it prints `key=value` for each requested key.

## State and Persistence Behavior

The utility is read-only. It stores the JMX connection and matched object names for one run. It does not close the `JMXConnector` explicitly after connecting, because the connector object is local to `init`.

## Dependencies and Integration Points

It integrates with Java Management Extensions (`MBeanServerConnection`, `ObjectName`, `JMXConnectorFactory`), Commons CLI, Hadoop `ExitUtil`, and the Hadoop MBean naming convention under the `Hadoop` domain.

## Risks and Edge Cases

- The JMX connector is not retained/closed, which can leak resources during repeated in-process use.
- `printAllValues` does not catch per-attribute read failures; one bad attribute can abort the run.
- Query domain is capitalized `Hadoop`, matching Hadoop metrics but not arbitrary MBeans.
- Logging and diagnostics go to stderr, while values go to stdout; scripts should separate streams.
- `getValue` suppresses missing-attribute cases across beans and returns an empty string when none match.

## Test Signals

Tests should cover local platform MBean queries, RMI URL construction, localVM URL use, command parsing errors/help, missing attribute behavior, regex filtering, stdout formatting, and connector lifecycle expectations.
