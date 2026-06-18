# sources/distributed-fs/ceph-client/drivers/sbus/char/bbc_i2c.h

Purpose: declares the private BBC I2C bus/client ABI shared between the low-level I2C controller and its environmental-control client implementation.

Important APIs/types/functions: `struct bbc_i2c_client` stores parent bus, platform child, bus number, and I2C address. `struct bbc_i2c_bus` stores controller mappings, waitqueue/IRQ wait state, child device slots, and per-bus temperature/fan lists. Environmental-control structs `bbc_cpu_temperature` and `bbc_fan_control` track sensor readings, fan actions, and fan output state. The header declares attach/detach, device lookup, byte/buffer read/write, and envctrl init/cleanup functions.

Control flow: `bbc_i2c.c` owns bus discovery and transfer primitives, while `bbc_envctrl.c` attaches clients to OF child platform devices and calls the blocking I2C operations.

State and persistence: this header defines volatile in-kernel state only. Sensor and fan list nodes exist simultaneously on per-bus and global lists managed by `bbc_envctrl.c`.

Dependencies and integration: depends on Linux OF and list APIs, platform devices via forward declarations/includes, and the composite `bbc` module linking both implementation files together.

Risks and test signals: the shared structures expose mutable fields directly, so both implementation files must preserve list and client lifetime invariants. `NUM_CHILDREN` limits discovery to eight children. Test ABI consistency by building `bbc_i2c.o` and `bbc_envctrl.o` together, attaching/detaching clients, and cleaning up list nodes for multiple sensors/fans.
