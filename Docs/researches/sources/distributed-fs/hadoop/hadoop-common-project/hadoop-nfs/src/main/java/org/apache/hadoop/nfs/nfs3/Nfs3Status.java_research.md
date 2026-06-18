<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Status.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Status.java

## Purpose

Protocol constant table for NFSv3 success and error status values used throughout request handlers and response serializers. The source was read as a complete 162-line file for this research item.

## Important APIs, Types, and Functions

Defines NFSv3 numeric status constants including `NFS3_OK=0`, `NFS3ERR_PERM=1`, `NFS3ERR_NOENT=2`, `NFS3ERR_IO=5`, `NFS3ERR_NXIO=6`, `NFS3ERR_ACCES=13`, `NFS3ERR_EXIST=17`, `NFS3ERR_XDEV=18`, `NFS3ERR_NODEV=19`, `NFS3ERR_NOTDIR=20`, `NFS3ERR_ISDIR=21`, `NFS3ERR_INVAL=22`, and additional protocol errors.

## Control Flow

There is no runtime control flow; response code and server logic reference these static integer constants when mapping filesystem/auth/protocol failures to NFS wire status.

## State and Persistence Behavior

No state or persistence; constants are loaded with the class and used process-wide.

## Dependencies and Integration Points

No imports; this file is self-contained at compile time. Integration points include every NFSv3 response class and server-side exception/status mapping.

## Risks and Edge Cases

`NFS3ERR_NOTDIR` is mutable (`static int`) while most constants are final; accidental reassignment would corrupt status mapping. Numeric values are wire ABI and must not drift from RFC/NFSv3 expectations.

## Test Signals

Compile-time use plus status-mapping tests from filesystem errors to NFS3ERR_* values; serialization tests should confirm integer values on the wire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Status.java -->
