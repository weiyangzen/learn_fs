# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/connect_cancel/connect_cancel.c

## Purpose
This C example demonstrates creating a disconnected libhdfs++ filesystem, connecting it, and canceling a pending connection from a SIGINT handler.

## Important APIs, Control Flow, and State
Global `hdfsFS fs` lets the signal handler call `hdfsCancelPendingConnection`. `main` sets logging level, registers `SIGINT`, requires no arguments, requires `HADOOP_CONF_DIR`, creates a builder from that directory, allocates a filesystem with `hdfsAllocateFileSystem`, connects with `hdfsConnectAllocated`, then disconnects and frees resources. The signal handler uses x-platform direct stdout writes to avoid malloc-heavy stdio/logging in signal context.

## Dependencies and Integration Points
It uses `hdfspp/hdfs_ext.h`, `common/util_c.h`, and x-platform syscall wrappers. It exercises builder-from-directory config loading, two-phase filesystem allocation/connect, cancellation, logging level, and protobuf shutdown.

## Risks and Test Signals
Calling complex library cancellation from a signal handler is inherently risky despite direct-output care. Error paths after `hdfsConnectAllocated` failure do not disconnect an allocated `fs`. Tests should cover missing `HADOOP_CONF_DIR`, allocation failure, successful connect, SIGINT during slow connect, repeated cancellation, and leak checks.
