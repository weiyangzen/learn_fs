# sources/distributed-fs/ceph-client/tools/perf/util/copyfile.h

Purpose: declares perf file-copy helpers.

Important APIs/types: `copyfile`, `copyfile_mode`, `copyfile_ns`, `copyfile_offset`, and forward declaration of `struct nsinfo`.

Control flow: callers choose default mode, explicit mode, namespace-aware copy, or fd/offset copy.

State and persistence: functions create/copy destination files or write output fds.

Dependencies and integration: includes Linux types, sys/types, and fcntl mode definitions. Used by build-id and file cache code.

Risks: callers must handle errors and destination-exists behavior. Offset copy requires valid fds and coherent offsets/size.

Test signals: namespace and non-namespace copies plus offset copy tests.
