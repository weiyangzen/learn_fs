<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/pm.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/pm.c

## Purpose
Dummy PCI driver for Intel AtomISP2/IUNIT devices. It exists to runtime-suspend the ISP into D3cold and allow low-power S0ix states when no full camera driver is in use.

## Important APIs, Types, And Functions
`isp_set_power()` writes IOSF PMC register `ISPSSPM0` and polls status bits for power on/off. `isp_probe()` enables runtime PM and immediately suspends. `isp_pci_suspend()` disables interrupts and CSI ports, saves PCI state, marks D3cold, and powers down. `isp_pci_resume()` powers up and restores PCI config space.

## Control Flow
The PCI driver binds Intel device IDs `0x0f38` and `0x22b8`. Probe puts the device into runtime suspend. System suspend executes the custom PM path instead of normal PCI power state changes because the PMCSR does not reflect the actual IUNIT power gate.

## State And Persistence
Persistent hardware state is PCI config space plus IOSF PMC power-gate state. The driver saves PCI state before power-off and restores it after power-on.

## Dependencies And Integration Points
Depends on PCI, PM runtime, delay helpers, and `asm/iosf_mbi.h`. It must not coexist with `INTEL_ATOMISP`.

## Risks And Test Signals
Risks include IOSF power transition timeout, accessing config space after the unit is power-gated, and incomplete CSI shutdown. Test with runtime PM status, S0ix residency, suspend/resume, and repeated bind/unbind on both PCI IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/pm.c -->
