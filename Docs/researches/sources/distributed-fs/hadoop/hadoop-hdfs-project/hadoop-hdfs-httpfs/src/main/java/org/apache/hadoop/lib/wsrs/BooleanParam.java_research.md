# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/BooleanParam.java

## Purpose
`BooleanParam` is a base JAX-RS query parameter parser for boolean HttpFS parameters.

## Important APIs, Types, and Functions
It extends `Param<Boolean>`. The constructor passes the parameter name and default value to `Param`. `parse(String)` accepts case-insensitive `"true"` and `"false"` only. `getDomain()` returns `"a boolean"` for validation messages.

## Control Flow
`Param.parseParam` handles default retention for blank or null input; nonblank values reach `BooleanParam.parse`, which returns a boxed Boolean or throws `IllegalArgumentException`.

## State and Persistence
State is the inherited per-instance `value`. Instances are request parameter objects and are not persisted.

## Dependencies and Integration Points
Subclasses in `HttpFSParametersProvider` use this parser for options such as upload-data flags, overwrite, recursive, no-redirect, and all-users style parameters. `ParametersProvider` creates a fresh instance for each query value.

## Risks
Values like `1`, `0`, `yes`, or `no` are rejected. That is strict and predictable, but compatibility depends on WebHDFS clients sending true/false strings.

## Test Signals
`TestCheckUploadContentTypeFilter` uses `HttpFSParametersProvider.DataParam.NAME` and true/false strings around upload requests, indirectly signaling expected boolean query values.
