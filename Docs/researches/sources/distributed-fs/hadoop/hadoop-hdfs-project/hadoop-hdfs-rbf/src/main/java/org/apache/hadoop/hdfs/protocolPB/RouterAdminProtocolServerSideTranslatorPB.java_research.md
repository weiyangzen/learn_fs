# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocolServerSideTranslatorPB.java

## Purpose
Server-side protobuf translator for Router admin RPCs. It receives generated protobuf requests, converts them to native federation store protocol objects, calls `RouterAdminServer`, and converts native PBImpl responses back to protobuf messages.

## Important APIs, Types, and Functions
The class implements `RouterAdminProtocolPB` and holds a final `RouterAdminServer server`. It covers mount-table operations (`addMountTableEntry`, `addMountTableEntries`, `removeMountTableEntry`, `updateMountTableEntry`, `getMountTableEntries`, `refreshMountTableEntries`, `getDestination`), router state (`enterSafeMode`, `leaveSafeMode`, `getSafeMode`), nameservice state (`disableNameservice`, `enableNameservice`, `getDisabledNameservices`), and refresh (`refreshSuperUserGroupsConfiguration`).

## Control Flow
Each RPC method has a consistent synchronous adapter flow: construct the matching request PBImpl from the incoming proto, call the server method, cast the returned native response to the matching response PBImpl, and return `getProto()`. `IOException` is caught and rethrown as protobuf `ServiceException`.

## State and Persistence Behavior
The translator itself is stateless except for the server reference. Persistent effects are delegated to `RouterAdminServer`, which may mutate mount table entries, nameservice disabled state, router safe mode state, and refresh router/user-group configuration.

## Dependencies, Risks, and Test Signals
It connects generated `HdfsServerFederationProtos` messages, native store protocol interfaces, PBImpl classes, and the router admin server. The file relies on response implementations being PBImpl instances; a non-PB implementation returned by `RouterAdminServer` would cause a `ClassCastException`. Expected tests should verify one-to-one request/response translation, `IOException` to `ServiceException` conversion, mount-table CRUD behavior, bulk add support, safe-mode transitions, nameservice enable/disable, and proxy-user refresh status.
