<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/zorro.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/zorro.h

Purpose: defines Amiga Zorro AutoConfig bus identifiers, ROM/config structures, helper macros, and GVP product flag handling.

Important APIs and types: `ZORRO_MANUF`, `ZORRO_PROD`, `ZORRO_EPC`, and `ZORRO_ID` encode and decode 32-bit board IDs. `zorro_id` is the public ID type. GVP masks and flags classify I/O, accelerator, SCSI, DMA, bank, and clock properties. `struct Node`, `ExpansionRom`, and `ConfigDev` mirror AutoConfig data. Type bits distinguish Zorro II and III boards, and `ZORRO_NUM_AUTO` sets the autoconfig slot count.

Control flow, state, and persistence: firmware/kernel AutoConfig reads ROMs, builds config-device records, and matches IDs against drivers. Physical board configuration persists in hardware; kernel state is bus enumeration data.

Dependencies and integration points: includes `zorro_ids.h` and integrates with m68k Amiga bus drivers and legacy expansion cards.

Risks and test signals: risks include packed big-endian layout drift, GVP extended product masking, ID macro misuse, and slot-size limits. Test ID matching, ROM parsing, Zorro II/III devices, GVP variants, and big-endian build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/zorro.h -->
