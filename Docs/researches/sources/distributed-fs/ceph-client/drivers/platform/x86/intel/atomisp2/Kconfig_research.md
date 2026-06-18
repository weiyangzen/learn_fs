<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/Kconfig

## Purpose
Defines build options for the Bay Trail/Cherry Trail AtomISP2 platform helper drivers.

## Important Symbols
`INTEL_ATOMISP2_PDX86` is an internal bool selected by the feature drivers. `INTEL_ATOMISP2_LED` builds a DMI-based camera LED helper using GPIOLIB and `LEDS_GPIO`. `INTEL_ATOMISP2_PM` builds the PCI power-management dummy driver and depends on PCI, IOSF MBI, PM, and absence of the real `INTEL_ATOMISP` driver.

## Control Flow
The LED option creates a platform device for `leds-gpio` on known systems. The PM option binds to ISP PCI IDs to put the ISP/IUNIT into D3 and support S0ix.

## State And Persistence
Build-time state only; selected options decide whether the AtomISP2 child directory is entered and which module names exist.

## Dependencies And Integration Points
Connects Intel platform-x86 to LED, GPIO, PCI, PM runtime, and IOSF MBI subsystems.

## Risks And Test Signals
Dependency mistakes can either leave camera LEDs stuck on at boot or prevent power savings. Validate by building both options and testing known Bay Trail/Cherry Trail systems for LED default-off behavior and ISP D3 transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/Kconfig -->
