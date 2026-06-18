# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gfw.rs

## Purpose

`gfw.rs` waits for GPU firmware/devinit completion after reset before Nova performs deeper GPU initialization.

## Important APIs, Types, And Functions

The single API is `wait_gfw_boot_completion(bar: &Bar0) -> Result`. It polls `NV_PGC6_AON_SECURE_SCRATCH_GROUP_05_PRIV_LEVEL_MASK` and `NV_PGC6_AON_SECURE_SCRATCH_GROUP_05_0_GFW_BOOT`.

## Control Flow

The function polls every millisecond for up to four seconds. Each poll first checks whether FWSEC lowered the scratch register read protection level so the CPU can safely read the GFW boot status, then reads the completion bit. Success maps to `Ok(())`; timeout or IO errors propagate.

## State And Persistence Behavior

No software state is stored. The observed hardware state is secure scratch privilege and completion bits set by firmware/devinit components running before the driver proceeds.

## Dependencies And Integration Points

It depends on BAR0 IO, register wrappers, and polling. `Gpu::new()` calls it immediately after chipset identification and before sysmem flush/Falcon/GSP setup.

## Risks And Test Signals

Risks include hardcoded four-second timeout, privilege-level check behavior differing by GPU or firmware, and limited diagnostics beyond timeout. Test by probing after cold boot and reset, checking timeout behavior on unsupported/failed firmware, and ensuring no later initialization runs before GFW completion.
