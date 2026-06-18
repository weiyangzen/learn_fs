# sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_clp.h

Purpose: This header defines packed CLP request/response layouts and constants for s390 PCI firmware discovery and function control.

Important APIs/types/functions: It declares CLP command codes, `struct clp_fh_list_entry`, CLP response codes, list-entry sizing, set-operation controls, utility/PFIP sizes, function type constants, global `zpci_unique_uid`, and packed request/response structures for SLPC, list PCI, query function, query function group, set PCI, and combined request/response blocks.

Control flow: zPCI firmware code issues CLP list commands with resume tokens, queries each function handle for BARs, DMA ranges, RID/topology, utility strings, MIO data, and group capabilities, then enables/disables functions through set-PCI commands.

State and persistence: Persistent state is not stored here, but the packed responses populate `struct zpci_dev` and bus capabilities. Resume tokens and function handles are firmware-visible transient state.

Dependencies and integration points: It depends on `asm/clp.h` and Linux PCI BAR constants, integrating zPCI core with IBM Z CLP firmware.

Risks and test signals: Packed bitfields and byte order must match firmware exactly. Tests should cover list pagination, query of optional MIO/util/RID/TID fields, group capability parsing, response-code error paths, and enable/disable commands.
