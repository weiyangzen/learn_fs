# sources/distributed-fs/ceph-client/drivers/edac/highbank_l2_edac.c

## Purpose
This platform EDAC device driver reports Calxeda Highbank L2 cache ECC events. It registers an EDAC device controller, maps status/clear registers, and handles separate single-bit and double-bit ECC IRQs.

## Important APIs and Functions
`struct hb_l2_drvdata` stores the mapped register base and IRQ numbers. `highbank_l2_err_handler()` clears the relevant interrupt and calls `edac_device_handle_ce()` for single-bit ECC or `edac_device_handle_ue()` for double-bit ECC. `highbank_l2_err_probe()` and `highbank_l2_err_remove()` implement platform lifecycle. The OF match table binds `calxeda,hb-sregs-l2-ecc`.

## Control Flow
Probe allocates an EDAC device with one instance/block and two counters, opens a devres group, maps the memory resource, fills names from the OF match, registers the EDAC device, then requests double-bit and single-bit IRQs. The IRQ handler compares the IRQ number with stored single/double IRQs, writes to the corresponding clear register, and reports the event. Remove unregisters and frees the EDAC device.

## State and Persistence
Per-device runtime state is limited to mapped MMIO base and IRQ numbers in the EDAC device private area. Hardware interrupt status is cleared by writes during interrupt handling. No persistent state exists.

## Dependencies and Integration
The file depends on platform devices, Open Firmware matching, managed MMIO/IRQ resources, and EDAC device APIs. It integrates with EDAC's device-class reporting rather than memory-controller reporting because the target is L2 cache.

## Risks
The driver assumes IRQ 0 is double-bit and IRQ 1 is single-bit. If `devres_open_group()` fails after EDAC allocation, the visible path returns without freeing the allocation, so that path should be checked. The handler always returns `IRQ_HANDLED`, even if an unexpected IRQ number is passed.

## Test Signals
Probe should create an EDAC device for matching DT nodes. Injected or hardware L2 ECC IRQs should increment CE/UE counters, write the clear registers, and remove cleanly without dangling sysfs entries.
