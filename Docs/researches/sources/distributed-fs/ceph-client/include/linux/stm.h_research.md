<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stm.h -->
# sources/distributed-fs/ceph-client/include/linux/stm.h

Purpose: Declares System Trace Module infrastructure for registering STM devices and trace sources and writing STP packets.

Important APIs/types/functions: `enum stp_packet_type`, `enum stp_packet_flags`, `enum stm_source_type`, `struct stm_data`, `stm_register_device()`, `stm_unregister_device()`, `struct stm_source_data`, `stm_source_register_device()`, `stm_source_unregister_device()`, and `stm_source_write()`.

Control flow: An STM hardware driver fills `struct stm_data` with master/channel ranges and callbacks, then registers it. Source drivers fill `struct stm_source_data` and register sources. When linked, writes flow through `stm_source_write()` to the selected STM device `packet()` callback with master/channel/packet metadata.

State and persistence behavior: Runtime state is owned by STM class internals through opaque `stm` and `src` pointers plus source/device linkage. Hardware state includes channel configuration and packet output.

Dependencies: Linux device model, module ownership, trace/ftrace source users, and hardware-specific STM packet callbacks.

Integration points: Intel STM and other system trace modules, ftrace-to-STM routing, userspace trace sources, and policy-managed channel allocation.

Risks: `packet()` callbacks must report consumed payload accurately and return `-ENOTSUPP` for unsupported type/flag combinations. Bad link/unlink handling can leave channels active or leak source associations.

Test signals: STM device/source registration tests, packet callback contract tests, ftrace source writes, policy/channel allocation tests, and unregister cleanup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stm.h -->
