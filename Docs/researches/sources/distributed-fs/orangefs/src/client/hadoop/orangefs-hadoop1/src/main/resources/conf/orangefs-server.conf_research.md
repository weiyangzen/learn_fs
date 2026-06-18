<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/orangefs-server.conf -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/orangefs-server.conf

## Purpose

This OrangeFS server configuration defines the single-node filesystem used by the Hadoop examples. It sets defaults, the `localhost` BMI/TCP alias, filesystem identity, root handle, metadata/data handle ranges, storage directories, log file, and storage hints.

## Important APIs, Types, and Functions

Important directives are `Alias localhost tcp://localhost:3334`, filesystem `Name orangefs`, `RootHandle`, `DataStorageSpace`, `MetadataStorageSpace`, handle ranges, `FileStuffing`, distributed-directory parameters, and Trove storage hints.

Active directives observed:

- `<Defaults>`
- `UnexpectedRequests 50`
- `EventLogging none`
- `EnableTracing no`
- `LogStamp datetime`
- `BMIModules bmi_tcp`
- `FlowModules flowproto_multiqueue`
- `PerfUpdateInterval 1000`
- `ServerJobBMITimeoutSecs 30`
- `ServerJobFlowTimeoutSecs 30`
- `ClientJobBMITimeoutSecs 300`
- `ClientJobFlowTimeoutSecs 300`
- `ClientRetryLimit 5`
- `ClientRetryDelayMilliSecs 2000`
- `PrecreateBatchSize 0,32,512,32,32,32,0`
- `PrecreateLowThreshold 0,16,256,16,16,16,0`
- `DataStorageSpace /tmp/orangefs_hadoop_storage/data`
- `MetadataStorageSpace /tmp/orangefs_hadoop_storage/meta`
- `LogFile /tmp/orangefs_hadoop_storage/orangefs-server.log`
- `</Defaults>`

## Control Flow

`pvfs2-server` reads the file during format (`-f`) and normal startup. The example scripts format, copy `pvfs2tab`, start the server, and ping the mounted filesystem; Hadoop clients then connect through the configured `ofs://localhost-orangefs:3334` authority.

## State, Persistence, and Concurrency

The config itself is static, while the data and metadata directories under `/tmp/orangefs_hadoop_storage` hold the persistent test filesystem state. Cleanup scripts remove those directories, effectively destroying the example volume.

## Dependencies and Integration Points

It must agree with `core-site.xml`, `pvfs2tab`, `/mnt/orangefs`, and OrangeFS binaries under `ORANGEFS_PREFIX`.

## Risks and Test Signals

Using `/tmp` makes the example volatile. Handle ranges and root handles are hard-coded for one server, so copying this into a multi-server deployment without regeneration is unsafe. Tests should format, start, `pvfs2-ping`, create a file through Hadoop, restart, and verify visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/orangefs-server.conf -->
