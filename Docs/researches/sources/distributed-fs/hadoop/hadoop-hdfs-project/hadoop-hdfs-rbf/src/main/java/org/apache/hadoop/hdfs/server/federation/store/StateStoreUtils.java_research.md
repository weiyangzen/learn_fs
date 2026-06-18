# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreUtils.java

## Purpose
`StateStoreUtils` provides helper methods for record-class normalization, record filtering, and address string formatting.

## Important APIs, Types, And Functions
Methods include `getRecordClass(Class<T>)`, `getRecordClass(T)`, `getRecordName(Class<T>)`, `filterMultiple(Query<T>, Iterable<T>)`, `getHostPortString`, and `getIpPortString`.

## Control Flow
Record-class normalization walks superclasses while class names end in `Impl`, stopping before `BaseRecord`. Filtering iterates records and applies `Query.matches`. Host formatting converts wildcard `0.0.0.0` to local host name; IP formatting uses `NetUtils.getConnectAddress`.

## State, Persistence, And Dependencies
The utility is stateless. It depends on `BaseRecord`, `Query`, network address classes, `NetUtils`, and logging.

## Integration Points
Drivers and stores use record-name normalization for storage names and query behavior. Address formatting is used in router state/registration paths.

## Risks
The `Impl` suffix heuristic depends on naming conventions and may fail for differently named generated classes. `getHostPortString` can return an empty string on local host resolution failure. `getIpPortString` assumes the connect address has a resolved `InetAddress`.

## Test Signals
Tests should cover PB implementation class normalization, accidental `BaseRecord` over-walk, query filtering, wildcard host replacement, unresolved addresses, and IP formatting through `NetUtils`.
