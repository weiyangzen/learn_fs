<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/plpks.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/plpks.h

## Purpose
This header declares the pseries Platform KeyStore (PLPKS) API for persistent secure variables, policy flags, signed updates, wrapping features, and device-tree/sysfs integration.

## Important APIs, Types, And Functions
When `CONFIG_PSERIES_PLPKS` is enabled it defines policy flags such as secure-boot audit/enforce, password-required, world-readable, immutable, transient, signed-update, wrapping-key, and hypervisor-provisioned; signature algorithms; owner/label limits; `struct plpks_var`, name/list structs; read/write/remove/signed-update APIs; availability and capability getters; early device-tree/FDT/sysfs hooks; and wrapping key/object functions. Disabled builds provide minimal stubs.

## Control Flow
Callers check availability, query capabilities and limits, then read/write/remove variables or perform signed/wrapped updates through pseries firmware-backed implementations.

## State And Persistence Behavior
Most variables persist in the platform keystore across reboot unless `PLPKS_TRANSIENT` is set. Capability values describe hypervisor-owned keystore state, used/total space, password length, and supported policies.

## Dependencies And Integration Points
It depends on pseries firmware, kobjects, device-tree/FDT population, secure boot, and key/wrapping consumers.

## Risks And Edge Cases
Maximum name/data/label sizes are strict. Policy flags are security-sensitive and may make objects immutable or inaccessible. Disabled stubs intentionally `BUILD_BUG()` for unsupported capability use.

## Test Signals
On PLPKS-capable pseries, test capability queries, variable write/read/remove, signed update, immutable/transient/world-readable policies, wrapping key generation/wrap/unwrap, reboot persistence, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/plpks.h -->
