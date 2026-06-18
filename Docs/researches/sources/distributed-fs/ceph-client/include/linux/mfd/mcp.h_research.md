<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mcp.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mcp.h

This header defines the MCP host/device abstraction used by older Linux MFD-style MCP bus support. `struct mcp` contains module ownership, operation callbacks, a spinlock, use count, serial clock rate, read/write timeout, and an embedded `attached_device`. `struct mcp_ops` supplies host operations for telecom/audio divisors, register read/write, and enable/disable. `struct mcp_driver` wraps a `device_driver` with MCP-specific probe/remove callbacks.

The API exposes wrapper functions for divisors, register access, enable/disable, host allocation/add/delete/free, and driver register/unregister. Control flow is bus-like: a host allocates and adds an `mcp`, a driver registers and probes against the attached device, and child code uses `mcp_reg_read/write` and enable/disable around hardware access. State is software-visible in `use_count`, lock-protected hardware access, clock settings, and driver data stored on the embedded device. `mcp_priv()` returns private memory immediately after the allocated `struct mcp`, so allocation size and type assumptions matter.

Dependencies include Linux device model, modules, spinlocks, and the MCP host implementation. Risks include lifetime and ownership bugs around the embedded device, races if operation wrappers do not consistently hold `lock`, and private-data layout misuse. Test signals include host allocation/free leak checks, driver probe/remove ordering, concurrent register access tests, clock divisor programming, and module unload behavior while devices are attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mcp.h -->
