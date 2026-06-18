
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/stm.h

Purpose: private STM framework header shared by core, policy, and protocol modules.

Important APIs/types/functions: declares policy/configfs helpers, `struct stp_master`, `struct stm_device`, `struct stm_output`, `struct stm_file`, `struct stm_source_device`, and `struct stm_protocol_driver`. It also declares device/protocol lookup and data-write functions used across STM modules.

Control flow: no standalone execution. It defines the internal contracts used when devices register, policies allocate outputs, protocols format writes, and sources link to devices.

State and persistence: structures describe volatile kernel state: device policy/protocol pointers, master bitmaps, source links, output allocations, and protocol private output state.

Dependencies and integration: includes configfs and relies on public `linux/stm.h` types included by users. It is the main integration point between `core.c`, `policy.c`, `p_basic.c`, and `p_sys-t.c`.

Risks: fields are protected by different locks documented in implementation files; header-only changes must preserve those locking assumptions. `stm_protocol_driver.write()` may be called from sensitive tracing contexts, so protocol implementations must avoid unsafe behavior.

Test signals: full STM build, protocol registration/unregistration, policy creation with protocol-private attributes, source link/write, and static analysis for lock-protected field access.
