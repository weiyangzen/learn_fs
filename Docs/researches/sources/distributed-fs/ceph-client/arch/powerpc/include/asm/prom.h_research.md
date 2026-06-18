# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/prom.h

Purpose: This header defines PowerPC Open Firmware / flattened device tree boot structures and client-architecture-support option vector constants used during early boot and firmware capability negotiation.

Important APIs/types/functions: `struct boot_param_header` describes the flattened device tree block passed by prom_init or kexec, including structure/string/reserve-map offsets, version fields, boot CPU ID, string size, and structure size. It defines OF token constants such as `OF_DT_BEGIN_NODE`, `OF_DT_PROP`, and `OF_DT_END`, `MIN_RMA`, `of_parse_dma_window`, `of_instantiate_rtc`, `of_get_ibm_chip_id`, `struct of_drc_info`, `of_read_drc_info_cell`, and `boot_cpu_node_count`. It also defines CAS option vector bits from architecture levels through firmware options, PAPR features, XIVE, MMU modes, dynamic reconfiguration, and Linux OS hint bits.

Control flow: Early boot receives and parses the FDT header, memory reserve map, structure block, and strings block. Firmware negotiation uses option vector constants either through root `ibm,client-architecture-support` or legacy fake ELF notes. Later platform code parses DMA windows, RTC nodes, chip IDs, and DRC info cells.

State and persistence: The FDT boot block and reserved memory map persist through boot long enough to instantiate kernel device nodes. `boot_cpu_node_count` records boot CPU node discovery. Option vectors influence firmware-selected capabilities for the lifetime of the boot.

Dependencies and integration points: It depends on Linux types, device-tree structures, and firmware feature logic. It integrates prom_init, kexec boot, pseries/PAPR negotiation, dynamic reconfiguration, XIVE, radix/hash MMU selection, NUMA affinity, MSI, large pages, memory hotplug, and RTC initialization.

Risks and test signals: FDT offsets and endian fields must be parsed exactly. Option vector bits overlap by vector index, so `OV5_FEAT` and `OV5_INDX` must be used correctly. CAS negotiation mistakes can disable required features or request unsupported ones. Tests include pseries boot under firmware/PowerVM/QEMU, kexec, memory hotplug DRC parsing, DMA window parsing, XIVE/radix/hash negotiation, and old firmware fallback paths.
