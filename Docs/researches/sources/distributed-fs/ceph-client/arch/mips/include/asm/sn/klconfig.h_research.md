<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/klconfig.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/klconfig.h

Purpose: Defines the SGI SN KLCONFIG firmware inventory format: board lists, component records, console metadata, allocation headers, board/component classes, device-specific structures, and lookup declarations.

Important APIs/types/functions: `KLCFGINFO_MAGIC`, `klconf_off_t`, board/component flags, `console_t`, `klc_malloc_hdr_t`, `kl_config_hdr_t`; access macros `KL_CONFIG_HDR`, `KL_CONFIG_INFO`, `KLCF_*`; class/type constants `KLCLASS_*`, `KLTYPE_*`; structures `lboard_t`, `klinfo_t`, `klcpu_t`, `klhub_t`, `klmembnk_t`, `klxbow_t`, `klbri_t`, `klioc3_t`, `klrou_t`, graphics/SCSI/FDDI/device structs; unions `klcomp_t`, `kldev_t`; and lookup declarations `find_lboard*`, `find_component*`.

Control flow: Firmware builds a linked list of local and remote board records in node-local KLCONFIG memory. Kernel code checks the magic, walks boards through offsets, resolves component offsets through NASID-aware macros, discovers CPUs, memory, bridges, IOC3s, routers, graphics, and devices, then binds drivers or reports inventory/errors.

State and persistence: KLCONFIG is persistent firmware-provided topology and diagnostic state. It encodes board flags, component flags, NIC IDs, physical/widget IDs, NASIDs, ARCS component pointers, error-info offsets, and console/device metadata.

Dependencies and integration points: Depends on Linux types, SN types, SN0/SN1 address definitions, FRU definitions, ARC firmware types, and platform-specific bridge/router headers under IP27/IP35 configurations.

Risks: The file explicitly warns that PROM assembly depends on struct layout; field reordering or insertion breaks firmware ABI. Offset-to-pointer macros assume correct NASID and K1 mapping. Some legacy constants reference IP35-only classes or external headers not present under all configs.

Test signals: IP27/SN boot inventory, CPU/memory/IO discovery, KLCONFIG walker tests, driver binding for IOC3/bridge/SCSI, and struct-offset compile checks are essential signals.

Source read size: 894 lines, 30637 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/klconfig.h -->
