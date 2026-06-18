# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/Param.java

## Purpose
`Param<T>` is the generic base class for typed query parameter parsing in HttpFS's JAX-RS layer.

## Important APIs, Types, and Functions
It stores a parameter `name` and protected mutable `value`. Public APIs are `getName()`, `parseParam(String)`, `value()`, and `toString()`. Subclasses must implement `getDomain()` and `parse(String)`.

## Control Flow
`parseParam` only calls subclass parsing when the input string is non-null and nonblank after trimming. Otherwise it keeps the existing default. Parse exceptions are converted to `IllegalArgumentException` with the parameter name, invalid value, and expected domain.

## State and Persistence
Each instance is mutable and holds the current parsed/default value. No persistence occurs. Correct usage requires request-local instances.

## Dependencies and Integration Points
`ParametersProvider` instantiates `Param` subclasses reflectively, fills them from the servlet parameter map, and wraps them in `Parameters` for HttpFS resource methods.

## Risks
Because `parseParam` retains the previous value for blank input, defaults are sticky and instances must not be reused across requests or values unless intentionally reset. The wrapper exception drops the original cause, making detailed parse failures less visible. Subclasses like `StringParam` override this method to trim before validation.

## Test Signals
Every operation in `BaseTestHttpFSWith` passes through the concrete HttpFS parameter provider, indirectly exercising default retention, type conversion, and error mapping.
