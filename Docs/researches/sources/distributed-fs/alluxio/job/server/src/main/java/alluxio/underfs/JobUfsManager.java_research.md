# Research: sources/distributed-fs/alluxio/job/server/src/main/java/alluxio/underfs/JobUfsManager.java

Purpose: job-service implementation of `UfsManager`, responsible for resolving and caching UFS clients used by job workers. It extends `AbstractUfsManager` and queries the master for mount information on cache misses.

Important APIs and control flow: the constructor registers a `FileSystemMasterClient` with the closer. `connectUfs` connects a filesystem from the job worker RPC host. `get(mountId)` first tries `super.get`; if missing, it calls `mMasterClient.getUfsInfo`, validates URI/properties, adds the mount with mount-specific configuration, acquires a UFS resource, and calls `connectFromWorker` using the worker RPC host. On connection failure it removes the mount and throws `UnavailableException`.

State, dependencies, integration, risks, tests: state is the inherited mount cache plus master client lifecycle. Dependencies include master RPC, `UfsInfo`, `UnderFileSystemConfiguration`, and network address resolution. Risk is duplicated logic with worker UFS manager, explicit TODO noted in source, and possible service-type mismatch between job-worker and worker RPC host usage.
