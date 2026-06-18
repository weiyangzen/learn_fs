# sources/distributed-fs/ceph-client/drivers/memory/brcmstb_memc.c

## Purpose
`brcmstb_memc.c` is a Broadcom STB DDR memory-controller helper focused on DDR self-refresh power-down (SRPD). It exposes a small sysfs control plane for the inactivity timeout that triggers SRPD and keeps the setting coherent across suspend and resume.

## Important APIs, Types, And Functions
The main private state is `struct brcmstb_memc`, which stores the device, mapped DDR controller base, configured timeout cycles, advertised memory frequency, and the SoC-version-specific SRPD register offset. `struct brcmstb_memc_data` carries that offset from the OF match table.

`brcmstb_memc_srpd_config()` validates the 16-bit inactivity count, updates `timeout_cycles`, writes the SRPD enable/count field, and reads back the register to flush the posted write. `brcmstb_memc_uses_lpddr45()` reads `REG_MEMC_CNTRLR_CONFIG` to block runtime SRPD changes on LPDDR4/LPDDR5 because those memories depend on dynamic tuning affected by the same timeout. Sysfs attributes are `frequency` read-only and `srpd` read/write. `brcmstb_memc_probe()` allocates state, maps resource 0, reads optional `clock-frequency`, and creates the sysfs group. PM callbacks disable SRPD before system suspend and restore it on resume.

## Control Flow
Probe selects the SRPD offset using `device_get_match_data()`, maps the controller registers, and publishes sysfs files. A user write to `srpd` parses a decimal cycle count, rejects LPDDR4/5 controllers, then writes the timeout and enable bit. Suspend clears only the enable bit when a nonzero timeout exists; resume calls the same programming helper to restore the saved setting.

## State And Persistence
Persistent driver state is in `timeout_cycles`, `frequency`, and the hardware SRPD register. The timeout survives suspend in RAM and is reprogrammed on resume, but it is not persisted across reboot. Sysfs removal is explicit in remove. Hardware writes use relaxed I/O plus a readback barrier.

## Dependencies And Integration Points
The driver integrates with platform-device probing, device tree compatibles for Broadcom DDR controller revisions, sysfs, MMIO helpers, and simple device PM. It depends on the `clock-frequency` device-tree property only for reporting.

## Risks
The LPDDR4/5 check depends on controller configuration values matching the macros. There is no lock around sysfs writes versus suspend/resume, so concurrent writes and PM transitions rely on normal device PM serialization rather than a private mutex. Invalid match data would dereference `memc_data`, though all supported compatibles provide `.data`.

## Test Signals
Useful tests are sysfs read/write of `srpd`, rejection of values above `0xffff`, `-EOPNOTSUPP` on LPDDR4/5 hardware, register value inspection after writes, and suspend/resume verification that SRPD is disabled during suspend and restored afterward.
