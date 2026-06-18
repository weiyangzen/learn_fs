<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gameport.h -->
# sources/distributed-fs/ceph-client/include/linux/gameport.h

Purpose: Defines the legacy gameport bus/device API for joystick/gameport hardware and drivers.

Important APIs/types/functions: `struct gameport` stores private data, name/physical path, I/O address/speed/fuzz, hardware callbacks (`trigger`, `read`, `cooked_read`, `calibrate`, `open`, `close`), polling timer fields, parent/child links, bound driver, driver mutex, device, and list node. `struct gameport_driver` defines connect/reconnect/disconnect callbacks and a `device_driver`. APIs include open/close, port register/unregister, name/phys setters, allocate/free, drvdata access, driver pin/unpin, driver register/unregister, polling start/stop, and `module_gameport_driver()`.

Control flow: Port providers allocate and register a `gameport`; bus matching calls driver connect/open; input drivers read raw or cooked values, optionally using periodic polling callbacks. Driver unregister/disconnect tears down binding.

State and persistence behavior: Runtime state lives in `gameport`, including timer/poll counters, parent-child topology, device model registration, and driver binding. No persistent storage is defined.

Dependencies and integration points: Depends on device core, timers, mutexes, lists, slab allocation, and UAPI gameport modes. Integrates with legacy input subsystem drivers.

Risks: Legacy GPIO-like I/O callbacks may sleep or run in timer context depending on use. `gameport_pin_driver()` is interruptible and callers must handle failure. Disabled `CONFIG_GAMEPORT` port registration stubs silently no-op.

Test signals: Build with reachable and disabled gameport configs, driver registration/unregistration, polling start/stop races, cooked-read/calibrate fallback behavior, and module unload while attributes pin the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gameport.h -->
