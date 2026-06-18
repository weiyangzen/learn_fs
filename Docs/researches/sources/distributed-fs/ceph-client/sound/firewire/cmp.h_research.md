# sources/distributed-fs/ceph-client/sound/firewire/cmp.h

Purpose: declares the CMP connection manager interface for FireWire audio drivers that need to reserve ISO resources and program target plug control registers.

Important APIs/types: `enum cmp_direction`, `struct cmp_connection`, and public functions `cmp_connection_init`, `cmp_connection_check_used`, `cmp_connection_destroy`, `cmp_connection_reserve`, `cmp_connection_release`, `cmp_connection_establish`, and `cmp_connection_break`.

Control flow and state: callers initialize with a FireWire unit, input/output direction, and PCR index; reserve bandwidth/channel; establish the target PCR; later break and release. `struct cmp_connection` persists connection/resource state including actual speed, allocated resources, last PCR value, max speed, and mutex.

Dependencies/integration: includes `iso-resources.h` and Linux mutex/types. Risks are misuse order, such as destroying while connected or establishing without reserved resources, and shared access to the underlying target plug. Test signals are compile-time users in BeBoB and runtime connection state tracking through `connected` and ISO resource allocation.
