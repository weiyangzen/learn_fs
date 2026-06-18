# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/fsinfo.h

## Purpose
`FsInfo` represents cluster-level HDFS capacity and block health information returned by libhdfs++.

## Important APIs, Control Flow, and State
The struct stores capacity, used, remaining, under-replicated blocks, corrupt blocks, missing blocks, missing replication-one blocks, and future blocks. Its constructor initializes defaults in the implementation. `str(fs_name)` formats the data in `hdfs_df` style.

## Dependencies and Integration Points
`FileSystem::GetFsStats` returns this type. Tools and C bindings can format or translate it to legacy `hdfsGetCapacity`/`hdfsGetUsed` style outputs.

## Risks and Test Signals
The key risks are 64-bit overflow/formatting and mismatch with Hadoop CLI output. Tests should validate field initialization, proto-to-struct mapping, formatting with nameservice/URI names, and large cluster values.
