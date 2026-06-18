# sources/distributed-fs/lizardfs/src/common/io_limit_group.h

Purpose: defines the type used to identify I/O limiting groups.

Important APIs/types/functions: `typedef std::string IoLimitGroupId` and constant `kUnclassified = "unclassified"`.

Control flow: no runtime behavior; consumers pass group IDs to limiting configuration and request paths.

State and persistence: no state; group IDs may be persisted by configuration elsewhere.

Dependencies and integration: included by `io_limiting.h` and config loaders. It standardizes the default unclassified group name.

Risks: plain string typedef does not prevent mixing arbitrary strings with validated group identifiers.

Test signals: no direct tests.
