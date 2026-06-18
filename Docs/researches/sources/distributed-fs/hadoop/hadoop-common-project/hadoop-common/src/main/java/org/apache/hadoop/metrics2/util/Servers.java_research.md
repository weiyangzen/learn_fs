<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Servers.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Servers.java

## Purpose
`Servers` parses compact server address lists for metrics sinks.

## Important APIs and Types
The sole public method is `parse(String specs, int defaultPort)`, returning a list of `InetSocketAddress` values. The class is public, evolving, and non-instantiable.

## Control Flow
If `specs` is null, it returns `localhost:defaultPort`. Otherwise it splits the string on spaces and commas, then delegates each token to `NetUtils.createSocketAddr` with the default port.

## State and Persistence
There is no mutable state or persistence.

## Dependencies and Integration Points
Ganglia sink setup uses this parser for the `servers` property. Other metrics utilities can use it for comma/space separated endpoint lists. It depends on Hadoop `NetUtils` and `Lists`.

## Risks and Test Signals
An empty but non-null string can produce an empty token and rely on `NetUtils` to reject it. IPv6 address handling depends on `NetUtils.createSocketAddr`. Tests should cover null defaults, comma and whitespace mixtures, explicit ports, default ports, invalid tokens, and IPv6 forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Servers.java -->
