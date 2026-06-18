<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/options.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/options.cc

## Purpose
Defines out-of-line constants and constructors for libhdfspp `Options` and simple `NamenodeInfo` accessors.

## Important APIs, Types, And Functions
The file provides storage for static defaults such as RPC timeout, retry counts, host exclusion duration, failover limits, and block size. `Options::Options()` initializes runtime defaults. `NamenodeInfo::get_host()` and `get_port()` expose host/port from the contained `URI`.

## Control Flow
Constructing `Options` copies default constants into scalar fields, initializes default URI/services state, sets default authentication, block size, and I/O thread count. `get_port()` returns the URI port as a string or `-1` when absent.

## State And Persistence
Each `Options` is an in-memory value object. Static constants have process lifetime.

## Dependencies And Integration Points
Used by filesystem construction, configuration parsing, bad DataNode tracking, and retry policy selection.

## Risks
Out-of-line constant definitions must match declarations in `hdfspp/options.h`. Returning `-1` as a port string is useful as a sentinel but can be passed accidentally into resolver/connect paths if callers skip validation.

## Test Signals
Tests should assert default option values, configuration override behavior, and `NamenodeInfo` host/port output for URIs with and without ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/options.cc -->
