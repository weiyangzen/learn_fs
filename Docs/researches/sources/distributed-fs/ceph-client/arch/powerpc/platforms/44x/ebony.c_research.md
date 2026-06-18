<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ebony.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ebony.c

Purpose: provides IBM Ebony board machine support: OF device population, RTC instantiation, PCI resource reassignment, UIC interrupt setup, and reset/progress hooks.

Important APIs/types/functions: `ebony_device_probe()` probes PLB4/OPB/EBC buses and calls `of_instantiate_rtc()`; `ebony_probe()` enables `PCI_REASSIGN_ALL_RSRC`; `define_machine(ebony)` binds the compatible string `ibm,ebony`.

Control flow: early machine probing accepts the board and sets PCI reassignment. The machine device initcall later registers child platform devices and RTC. Interrupt handling uses `uic_init_tree()`/`uic_get_irq()`.

State and persistence: no local runtime state; persistent effects are registered platform devices, RTC device, PCI flags, and machine callbacks.

Dependencies and integration: depends on OF bus nodes, UIC, PPC4xx reset, generic PCI bridge code, and udbg progress output.

Risks and test signals: simple board file assumes the DT fully describes devices. Test Ebony boot, RTC creation, PCI enumeration, UIC interrupts, and reset path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ebony.c -->
