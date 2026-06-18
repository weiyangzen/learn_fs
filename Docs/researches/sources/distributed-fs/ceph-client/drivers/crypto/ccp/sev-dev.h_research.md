# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev.h

## Purpose

`sev-dev.h` defines the private SEV device state, command-response register bit masks, misc-device reference wrapper, and SEV/SNP helper prototypes used by PSP, TIO, and KVM-facing code.

## Important APIs, Types, And Functions

It defines `struct sev_misc_dev` and `struct sev_device`. `sev_device` contains PSP/MMIO references, SEV vdata, interrupt wait state, firmware API/build fields, primary and backup command buffers, SNP initialized flag, SEV/SNP cached platform status, SNP feature info, and TIO state. It declares core lifecycle, locked command submission, PCI init/exit, HV-fixed page allocation, TSM init/uninit, and TIO command length lookup.

## Control Flow

No executable flow lives here. The header establishes the shared state contract used by `sev-dev.c`, `psp-dev.c`, `sev-dev-tio.c`, and `sev-dev-tsm.c`.

## State And Persistence Behavior

The state model is persistent per PSP device. Command-buffer flags track nested firmware command use, while SNP/TIO fields represent platform state that may outlive individual file descriptors.

## Dependencies And Integration Points

It includes SEV UAPI, misc-device, waitqueue, DMA, interrupt, and capability headers. The declared functions are consumed by PSP init, KVM SEV support, SFS HV-fixed allocation, and TIO integration.

## Risks And Test Signals

Risks include structure field misuse across files and stale cached platform status. Compile coverage with PSP/SEV/TIO configurations and runtime tests that initialize, shut down, and reinitialize SEV/SNP validate the shared state contract.
