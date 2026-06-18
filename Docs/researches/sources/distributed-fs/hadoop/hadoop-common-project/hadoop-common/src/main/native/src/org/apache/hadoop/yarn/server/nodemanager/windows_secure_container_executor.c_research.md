# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/yarn/server/nodemanager/windows_secure_container_executor.c

## Purpose
`windows_secure_container_executor.c` implements the JNI bridge between YARN's `WindowsSecureContainerExecutor.Native` Java classes and privileged Windows `winutils` RPC operations. It creates tasks as users, performs elevated filesystem operations, and wraps Windows process handles in Java process-stub objects.

## Important APIs, types, and functions
Initialization functions are `initWsceNative`, `winutils_process_stub_init`, `winutils_process_stub_deinit`, and `winutils_process_stub_create`. Exported JNI operations include `createTaskAsUser0`, elevated kill/chown/mkdir/chmod/copy/create/delete methods, and process-stub methods `destroy`, `waitFor`, `resume`, `exitValue`, `dispose`, and `getFileDescriptorFromHandle`. Cached JNI state includes global class `wps_class`, constructor ID, and field IDs for process/thread handles and disposed state.

## Control flow
Initialization finds the nested `WinutilsProcessStub` class, stores a global reference, resolves fields and constructor, and cleans up on failure. Windows-only native methods convert Java UTF-16 strings to `LPCWSTR`, call `RpcCall_Winutils*` helpers, throw `IOException` via `throw_ioe` on nonzero Win32 status, and release all strings in a `done` block. Task creation receives process/thread/std stream handles, constructs a Java stub, and terminates/closes handles if Java object creation fails. Stub methods directly operate on cached handles.

## State and persistence
The file has process-global JNI metadata and per-process Windows handles stored in Java objects. It does not persist state, but it controls live OS processes and handle ownership. `dispose` marks Java stubs as disposed after closing process and thread handles.

## Dependencies and integration points
It depends on JNI, Windows APIs, `winutils.h`, `file_descriptor.h`, and YARN's Windows secure container executor classes. Unix builds expose the symbols but throw unsupported `IOException`s for platform-specific operations.

## Risks and test signals
Risks include global initialization races if `initWsceNative` is not called as intended, handle leaks for std stream handles after stub creation, double-close or use-after-dispose patterns, broad `TerminateProcess` behavior, and security-sensitive trust in winutils RPC authorization. Test signals include Windows container launch/kill lifecycle tests, elevated filesystem operation tests, Java finalization/dispose paths, failure injection for RPC calls and object construction, and Unix tests confirming unsupported-operation exceptions.
