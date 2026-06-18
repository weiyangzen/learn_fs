## sources/distributed-fs/openafs/src/WINNT/client_osi/osi.h

Purpose: Aggregates the Windows OSI utility layer definitions for locks, sleeps, queues, logging, debug RPC, file descriptors, and utilities.

Important APIs/types: Defines `osi_hyper_t` as `LARGE_INTEGER`, `osi_uid_t` as `GUID`, and `int32`. Provides large-integer compatibility declarations/macros for newer MSVC and includes subsystem headers such as `osiutils.h`, `osibasel.h`, `osistatl.h`, `osidb.h`, and `osilog.h`.

Control flow/state: Header has no runtime logic but selects compatibility paths based on compiler version.

Dependencies/integration: Included by OSI implementation and test files. Pulls in RPC/GUID and thread abstractions.

Risks/tests: Aggregated headers can hide dependency cycles and macro conflicts. Test C and C++ consumers, older/newer MSVC versions, and consistency of large-integer comparison macros.
