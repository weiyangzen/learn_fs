<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/sam440ep.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/sam440ep.c

Purpose: implements ACube Sam440ep board support with OF bus probing, PCI resource reassignment, UIC interrupt setup, common reset hook, and static I2C RTC registration.

Important APIs/types/functions: `sam440ep_device_probe()` probes PLB4/OPB/EBC buses; `sam440ep_probe()` enables `PCI_REASSIGN_ALL_RSRC`; `define_machine(sam440ep)` binds `acube,sam440ep`; `sam440ep_setup_rtc()` registers an `m41st85` I2C board device at address `0x68`.

Control flow: machine probe selects the board and sets PCI flags. Device init probes buses and separately registers the RTC board info on I2C bus 0.

State and persistence: persistent effects are registered platform devices, static I2C RTC info, PCI flags, and machine callbacks. No local mutable state remains.

Dependencies and integration: depends on UIC, generic PPC4xx reset, PCI bridge setup, OF buses, and I2C adapter 0 existing for the RTC.

Risks and test signals: static I2C board info assumes bus numbering and RTC address; DT/board mismatch can duplicate RTC representation. Test Sam440ep boot, RTC detection, PCI enumeration, UIC interrupts, and reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/sam440ep.c -->
