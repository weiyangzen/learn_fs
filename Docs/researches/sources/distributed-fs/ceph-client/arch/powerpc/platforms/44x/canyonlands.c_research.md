<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/canyonlands.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/canyonlands.c

Purpose: implements AMCC/APM PPC460EX Canyonlands board setup, including OF platform bus population, PCI resource reassignment, UIC interrupt wiring, reset hook, and a USB PHY/GPIO board-control fixup.

Important APIs/types/functions: `ppc460ex_device_probe()` probes `ibm,plb4`, `ibm,opb`, `ibm,ebc`, and `simple-bus`; `ppc460ex_probe()` marks PCI resources for reassignment; `ppc460ex_canyonlands_fixup()` maps the BCSR and PPC4xx GPIO controller, toggles the USB enable/reset bit, and configures GPIO16/GPIO19 alternate output; `define_machine(canyonlands)` supplies platform callbacks.

Control flow: machine probe is selected by compatible `amcc,canyonlands`. Device initcalls populate buses and perform the USB fixup. The fixup disables USB through BCSR7, waits 100 ms, enables USB, then sets OSRH/TSRH mux bits for USB stop signals.

State and persistence: persistent state is board-control and GPIO hardware register configuration. Mappings are temporary and released after init.

Dependencies and integration: depends on OF nodes `amcc,ppc460ex-bcsr` and `ibm,ppc4xx-gpio`, UIC interrupt code, PPC4xx reset, PCI bridge setup, and `44x.h` GPIO offsets.

Risks and test signals: error paths return early without unmapping BCSR if GPIO node lookup fails; hard-coded BCSR/GPIO bits are board-specific. Test Canyonlands boot, USB host/device behavior after reset, PCI enumeration, OF bus devices, and missing-node failure logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/canyonlands.c -->
