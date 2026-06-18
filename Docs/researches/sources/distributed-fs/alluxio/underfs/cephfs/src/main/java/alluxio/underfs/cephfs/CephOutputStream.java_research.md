# Research: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephOutputStream.java

Purpose: output stream over a native CephFS file descriptor, returned by direct create paths in `CephFSUnderFileSystem`.

Important APIs and control flow: the stream stores `CephMount` and fd. `write(int)` and byte-array writes delegate to Ceph write calls; `flush` maps to Ceph fsync/sync behavior if supported by the binding; `close` closes the fd and prevents duplicate close effects. It is used after `CephFSUnderFileSystem.openInternal` opens a file with write/create/truncate flags.

State, dependencies, integration, risks, tests: state is the native fd and closed status. Persistence occurs immediately in the remote CephFS file. Dependencies include the Ceph Java binding and `OutputStream` contract. Risks include partial native writes, close/fdatasync error handling, and ensuring descriptor closure if stream construction succeeds but later Alluxio operations fail.
