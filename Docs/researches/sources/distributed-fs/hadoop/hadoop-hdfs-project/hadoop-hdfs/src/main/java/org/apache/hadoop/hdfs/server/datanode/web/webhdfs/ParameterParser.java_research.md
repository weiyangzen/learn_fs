# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/ParameterParser.java

## Purpose

`ParameterParser` wraps Netty `QueryStringDecoder` output and converts WebHDFS request parameters into typed Hadoop resource parameter objects. It centralizes path extraction, operation lookup, create/open options, delegation token decoding, and NameNode identity handling for DataNode WebHDFS.

## Important APIs, Control Flow, and State

The constructor strips the WebHDFS prefix from the decoded path and stores the parameter map. Methods parse `op`, `offset`, `length`, NameNode address, `doas`, `user.name`, buffer size, block size, replication, permissions, overwrite, noredirect, create-parent, and create flags. `delegationToken` decodes a URL token, builds `hdfs://namenodeId`, and sets the token service to the logical HA service or concrete NameNode address as appropriate. `createFlag` decodes the createflag parameter with UTF-8 `QueryStringDecoder` to preserve comma/list parsing.

State is per request and immutable after construction. There is no persistence. The private `param` helper returns only the first value for each key, matching common WebHDFS parameter semantics. `decodeHexNibble` is a private helper currently unused in this file.

## Dependencies, Integration, Risks, and Tests

Dependencies include WebHDFS parameter classes, `HAUtilClient`, `SecurityUtil`, `Token`, `DelegationTokenIdentifier`, and `Configuration`. It integrates with `WebHdfsHandler` and `DataNodeUGIProvider`.

Risks include first-value-only handling, invalid parameter exceptions bubbling to `ExceptionHandler`, token service misassignment for HA logical URIs, path substring assumptions if prefix validation is bypassed, and unused helper drift. Tests should cover every parsed parameter, missing/default values, create flag/overwrite interaction, logical and physical delegation token service, invalid parameter conversion, and URL-encoded create flags.
