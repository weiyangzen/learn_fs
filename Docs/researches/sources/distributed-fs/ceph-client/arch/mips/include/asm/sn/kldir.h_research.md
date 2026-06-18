<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/kldir.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/kldir.h

Purpose: Defines the generic SGI SN Kernel Launch Directory entry format and includes SN0-specific directory offsets.

Important APIs/types/functions: `KLDIR_MAGIC`, field offsets `KLDIR_OFF_*`, `KLDIR_ENT_SIZE`, `KLDIR_MAX_ENTRIES`, and `kldir_ent_t` with magic, offset, pointer, size, count, stride, and reserved fields.

Control flow: Boot code treats the KLDIR memory page as an array of fixed-size entries and uses generic plus SN0-specific constants to locate launch, NMI, KLCONFIG, GDA, and other firmware/kernel handoff areas.

State and persistence: The directory is firmware-populated persistent boot metadata. The header defines its in-memory ABI but does not mutate it.

Dependencies and integration points: Includes `asm/sn/sn0/kldir.h` for IP27 offsets and is used by `sn/addrs.h`.

Risks: Entry size and offsets are assembly/firmware ABI. Mis-sized structures break low-level boot and per-node firmware area discovery.

Test signals: Boot-time KLDIR validation, struct-size checks, and SN PROM handoff tests are relevant.

Source read size: 36 lines, 1068 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/kldir.h -->
