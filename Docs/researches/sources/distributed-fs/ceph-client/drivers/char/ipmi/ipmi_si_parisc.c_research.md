<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_parisc.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_parisc.c

## Purpose
Adds PA-RISC-specific discovery for IPMI KCS system interfaces exposed as PA-RISC management controller devices. It converts a `parisc_device` into a standard `si_sm_io` and registers it with the generic IPMI SI core.

## Important APIs, Types, and Functions
- `ipmi_si_parisc_init()` registers `ipmi_parisc_driver`.
- `ipmi_si_parisc_shutdown()` unregisters it if registration happened.
- `ipmi_parisc_probe()` builds a memory-space KCS `si_sm_io` at `dev->hpa.start`.
- `ipmi_parisc_remove()` calls `ipmi_si_remove_by_dev()`.
- `ipmi_parisc_tbl` matches PA-RISC management controller hardware IDs.

## Control Flow
Driver init registers a PA-RISC bus driver. Probe zeroes an `si_sm_io`, fills KCS metadata, marks the source as device tree, configures 8-bit memory registers with no IRQ, and calls `ipmi_si_add_smi()`. Remove tears down by device.

## State and Persistence
Only `parisc_registered` is file-local persistent state. Per-interface state is owned by the SI core after `ipmi_si_add_smi()`.

## Dependencies and Integration Points
Depends on PA-RISC bus APIs, `asm/hardware.h`, `asm/parisc-device.h`, and generic IPMI SI registration. It integrates only when PA-RISC support builds this file.

## Risks
The address source is reported as `SI_DEVICETREE` even though the bus is PA-RISC-specific, which may affect diagnostics. The file hardcodes KCS, memory space, byte registers, and no interrupt; any PA-RISC platform that differs will need new detection logic.

## Test Signals
Boot/probe on matching PA-RISC management controller hardware, verify `ipmi_si_add_smi()` succeeds, and verify unregister removes only devices attached through this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_parisc.c -->
