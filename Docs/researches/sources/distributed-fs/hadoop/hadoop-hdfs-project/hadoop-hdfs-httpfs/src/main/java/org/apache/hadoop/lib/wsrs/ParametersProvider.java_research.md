# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ParametersProvider.java

## Purpose
`ParametersProvider` turns a servlet request parameter map into a typed `Parameters` object based on an operation-dispatched parameter definition table.

## Important APIs, Types, and Functions
The constructor takes the operation/driver parameter name, an enum class for operations, and a `Map<Enum, Class<Param<?>>[]>` defining expected parameter classes per operation. `get(HttpServletRequest)` performs parsing. `newParam` reflectively calls default constructors on parameter classes.

## Control Flow
`get` reads `request.getParameterMap()`, extracts the first value of the driver parameter, uppercases it, converts it to the operation enum, checks support in `paramsDef`, and then iterates every parameter class for that operation. For each class it creates a parameter instance; if request values exist, each value is parsed into a fresh instance and appended to the list. If absent, one default instance is added. The result map is wrapped in `Parameters`.

## State and Persistence
The provider stores immutable-ish definition references but no request state after `get` returns. The returned `Parameters` owns the per-request objects.

## Dependencies and Integration Points
`HttpFSParametersProvider` subclasses/configures this class for WebHDFS operation parameters. `HttpFSServer` holds a static provider and calls it for each request.

## Risks
Reflective construction requires every concrete `Param` class to have a public/default constructor. If the servlet parameter map contains a key with an empty array, `queryString.get(driverParam)[0]` can throw. Wrapped parse errors become `IllegalArgumentException(ex.toString(), ex)`, so clients receive generic bad-request responses through `ExceptionProvider`.

## Test Signals
`BaseTestHttpFSWith` tests every declared client operation against the server, and negative cases for invalid operations/values depend on this parser rejecting malformed or missing parameters. `TestCheckUploadContentTypeFilter` references provider-defined `DataParam` names.
