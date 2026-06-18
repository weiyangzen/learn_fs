# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AuthUtil.m

Purpose: implements the singleton Authorization Services bridge for privileged operations.

Important APIs and control flow: `shared` lazily allocates the singleton through `allocWithZone:`. `autorize` first tries `AuthorizationCopyRights` on any existing ref, creates one if absent, and requests `kAuthorizationRightExecute` with interaction/preauthorization/extend-rights flags. `deautorize` frees owned refs. `setAuthorization:` releases an internally owned ref before adopting an external one. `extFormAuth` calls `AuthorizationMakeExternalForm`. `execUnixCommand:args:output:` uses `AuthorizationExecuteWithPrivileges`, reads the returned pipe into an optional `NSMutableString`, closes the stream, and waits for a child.

State and persistence: state is only in-process. The singleton may either own the ref it created or borrow a ref supplied by the preference pane authorization view.

Dependencies and integration: used by `TaskUtil` for authorization and by `FileUtil`/`PListManager` for older privileged file manipulation. Depends on Security.framework and POSIX `read`/`wait`.

Risks: `AuthorizationExecuteWithPrivileges` is deprecated and the `wait()` call may reap unrelated children. The output append uses a fixed buffer as a C string without explicitly null-terminating each read. `authorizationRef` can be nil when `AuthorizationCopyRights` is first called. Manual singleton retain overrides complicate ownership analysis.

Test signals: denied authorization, user-cancel paths, borrowed vs owned refs, serialization with nil refs, command output larger than 1024 bytes, nonzero command exits, and concurrent singleton acquisition.
