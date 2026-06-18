
# sources/distributed-fs/openafs/src/update/global.h

`global.h` contains shared constants and the linked-list type used by `upclient`, `upserver`, and update utilities. It defines `TIMEOUT` as the default resync interval, `MAXFNSIZE` as the maximum filename buffer size, `MAXENTRIES` as the maximum exported directory entries accepted by `upserver`, and `UPDATEERR`.

The only type is `struct filestr`, a singly linked list of dynamically allocated names. `utils.c` manages this list with `AddToList` and `ZapList`; `client.c` uses it for requested directories, modified files, and server-manifest files.

There is no direct persistence or control flow here. Dependencies are minimal, with a Windows include for NT builds. Risks are fixed-size constants driving buffer assumptions throughout update code and a generic list type without ownership annotations. Test signals are compile coverage and list lifecycle checks through the client synchronization loop.
