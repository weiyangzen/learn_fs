# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/UriFsPathParam.java

## Purpose

`UriFsPathParam.java` defines the WebHDFS URI path parameter named `path` and converts Jersey's stripped path value back into an absolute HDFS path. The source was read as a complete 45-line file for this report.

## Important APIs, Types, and Functions

The class extends `StringParam`. It defines `NAME = "path"`, an unconstrained `StringParam.Domain`, a string constructor, `getName()`, and `getAbsolutePath()`.

## Control Flow

The constructor stores the raw URI path fragment through the base parameter class. `getAbsolutePath()` fetches `getValue()` and returns null for null input or prepends `/` because the first slash has been stripped by URI matching.

## State and Persistence Behavior

The class stores a request-scoped path string and does not persist data. Its output controls which HDFS path a WebHDFS operation will target.

## Dependencies and Integration Points

It depends on `StringParam` and integrates with Jersey resource path binding for WebHDFS operations. Downstream integration is broad: file status, open/create, ACL/XAttr, snapshot, content summary, and other path-oriented WebHDFS endpoints consume the absolute path.

## Risks and Edge Cases

The class only prepends a slash and does not normalize dot segments, repeated slashes, encoding, or empty relative path values. It assumes the URI router stripped exactly one leading slash. Path validation and authorization must occur downstream.

## Test Signals

Tests should cover null path, empty path, ordinary nested paths, encoded characters, root-path behavior, and WebHDFS resource methods that use the resulting absolute path.
