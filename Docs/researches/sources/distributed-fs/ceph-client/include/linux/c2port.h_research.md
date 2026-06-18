## sources/distributed-fs/ceph-client/include/linux/c2port.h

**Purpose:** This header defines the Silicon Labs C2 debug/programming port framework interface.

**Important APIs/types/functions:** `C2PORT_NAME_LEN` limits device names. `struct c2port_device` stores access flags, ID, name, operations, mutex, device pointer, and private data. `struct c2port_ops` supplies flash geometry plus GPIO-like callbacks for access enable, C2D direction/read/write, and C2CK clock writes. Functions are `c2port_device_register()` and `c2port_device_unregister()`.

**Control flow, state, persistence:** Framework code serializes read/write through the per-device mutex and delegates signal toggling to provider callbacks. Flash persistence belongs to the target device accessed over C2; this header only models the host-side control surface.

**Dependencies/integration:** Requires `struct device` and mutex support from included users. Integrates platform-specific bit-banging drivers with the C2 core and sysfs/debug interfaces implemented elsewhere.

**Risks and test signals:** Risks are timing-sensitive line toggling, missing mutual exclusion, incorrect flash block geometry, and failing to disable access on unregister/error. Test signals include register/unregister tests, concurrent sysfs access, flash read/write/erase on known C2 devices, and GPIO trace validation.
