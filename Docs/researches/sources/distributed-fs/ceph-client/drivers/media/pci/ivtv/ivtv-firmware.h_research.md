# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-firmware.h

## Purpose
`ivtv-firmware.h` declares the firmware lifecycle API used by driver probe, first open, file operations, and remove paths.

## Important APIs, Types, and Functions
It declares `ivtv_firmware_init()`, `ivtv_firmware_versions()`, `ivtv_halt_firmware()`, `ivtv_init_mpeg_decoder()`, and `ivtv_firmware_check()`.

## Control Flow
The header itself has no executable flow. `ivtv-driver.c` calls init/version/decoder setup on first open and halt on remove. `ivtv-fileops.c` calls `ivtv_firmware_check()` during open to reject or recover dead firmware.

## State and Persistence
No state is held here. The declared functions mutate firmware memory, mailbox pointers, standard/output state, and flags inside `struct ivtv`.

## Dependencies and Integration Points
The prototypes depend on `struct ivtv` from the core header and connect the firmware implementation to the driver lifecycle and exported firmware health checks used by related modules.

## Risks and Edge Cases
The simple interface hides whether calls require idle hardware, loaded firmware files, valid MMIO mappings, or initialized mailbox structures. Calling these helpers too early or while streams are active can fail or disrupt hardware.

## Test Signals
Build coverage should ensure callers see consistent prototypes. Runtime signals include successful first-open firmware initialization, remove-time halt, decoder setup on output-capable cards, and open-time recovery from idle firmware failures.
