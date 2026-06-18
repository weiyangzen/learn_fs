# sources/distributed-fs/ceph-client/include/linux/errname.h

Purpose: optional symbolic errno-name lookup.

Important APIs/types/functions: `errname(int err)`, returning a symbolic name when `CONFIG_SYMBOLIC_ERRNAME` is enabled, otherwise returning `NULL`.

Control flow: diagnostic code can call `errname()` and fall back to numeric formatting if it returns NULL.

State/persistence: no state.

Dependencies/integration: errno tables compiled under `CONFIG_SYMBOLIC_ERRNAME`, logging and debug paths.

Risks/test signals: risks are assuming non-NULL names when config is off or passing positive/non-errno values. Test logging with config on/off and representative negative errno values.
