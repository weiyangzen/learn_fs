# sources/distributed-fs/ceph-client/tools/crypto/ccp/test_dbc.py

Purpose: unittest suite for AMD DBC userspace wrappers and kernel ioctl behavior across unsupported, secured, and unfused systems.

Important APIs, types, and functions: `system_is_secured()` reads CCP `fused_part`. `DynamicBoostControlTest` opens/closes `DEVICE_NODE` and supplies dummy signature/UID. Test classes cover unsupported systems, invalid ioctl structs via `ioctl_opt`, invalid signatures on fused systems, and valid/unfused parameter operations.

Control flow: Tests skip based on device existence, ioctl_opt availability, and fused state. Invalid ioctl tests construct bad ioctl numbers/structures and expect `EINVAL`. Secured tests expect unauthenticated nonce success but authenticated operations with dummy signatures to fail. Unfused tests establish identity, read ranges, set and restore fmax/power caps, and expect graphics mode to be unimplemented.

State and persistence: Mutates DBC device state for UID and power/fmax caps, attempting to restore original values. Adds delays between set commands. Reads sysfs fused state.

Dependencies and integration points: Depends on `dbc.py`, optional `ioctl_opt`, `/dev/dbc`, CCP PCI sysfs, and live hardware/firmware behavior.

Risks: `glob(...)[0]` in `system_is_secured()` can raise if no CCP path exists. Set tests alter hardware limits and rely on restoration paths. Dummy signatures and errno expectations are firmware/kernel behavior dependent.

Test signals: Running the suite itself is the signal, with skip accounting for unsupported systems. Hardware-backed CI would need isolated unfused/fused platforms.
