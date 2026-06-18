# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/devlink.h

Purpose: declares the mv88e6xxx devlink integration surface used by the main switch driver and DSA callbacks.

Important APIs/types/functions: prototypes cover devlink parameter setup/teardown, resource setup, parameter get/set, global and per-port region setup/teardown, and `mv88e6xxx_devlink_info_get()`.

Control flow: no executable flow. The header defines lifecycle ordering expectations: setup functions are called during switch initialization, teardown functions during unwind/remove, and parameter/info functions are called by DSA devlink dispatch.

State and persistence: no state is stored here. Implementations in `devlink.c` write runtime region pointers into `struct mv88e6xxx_chip` and per-port state.

Dependencies/integration: includes only the local include guard and relies on including translation units to have DSA/devlink types visible. It is a private driver header, not a stable external API.

Risks: prototypes must stay aligned with DSA hook signatures as kernel devlink APIs evolve. Missing includes are acceptable only while all consumers include DSA headers first.

Test signals: compile coverage is the main signal; setup/remove paths should link all declared functions and DSA hooks should receive expected return codes for unsupported operations.
