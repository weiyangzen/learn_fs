<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/pci.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/pci.h

Purpose: defines the register offsets, bit masks, and SoC-specific SDR/DCR constants used by PPC4xx PCI, PCI-X, and PCI Express bridge setup code.

Important APIs/types/functions: includes PCI-X register offsets (`PCIX0_*`), older PCI local bridge offsets (`PCIL0_*`), PCIe global DCR offsets (`DCRO_PEGPL_*`), SDR offsets for 440SPe/405EX/460EX/460SX/476FPE style PCIe PHYs, outbound mapping masks such as `GPL_DMER_MASK_DISA`, OMR/PIM constants, UTL/config offsets, lane width and port type fields, and SoC-specific link/status bits consumed by `pci.c`.

Control flow: no executable code. `pci.c` uses these constants to program bridge windows, mask config transaction errors, set up PCIe PHY/link registers, and access internal config/UTL spaces.

State and persistence: no software state; constants describe persistent hardware registers.

Dependencies and integration: tightly coupled to `pci.c`, PPC DCR/SDR accessors, PCI config-space helpers, and 4xx device-tree compatible strings selecting the right hardware path.

Risks and test signals: a wrong register offset can break PCI initialization or corrupt SoC state; this header encodes several subtly different hardware generations. Test by compiling all 44x/47x PCIe variants and boot-enumerating PCI/PCI-X/PCIe on representative hardware or simulators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/pci.h -->
