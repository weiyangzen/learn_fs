<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/pcmcia.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/pcmcia.c

Purpose: implements PCMCIA host-bus access for SSB devices, including core/segment window switching, byte/word/dword and optional block I/O operations, CIS-based invariant extraction, SPROM sysfs access, and PCMCIA hardware setup.

Important APIs/types/functions: `ssb_pcmcia_ops` provides `struct ssb_bus_ops`; `ssb_pcmcia_switch_coreidx()` programs address-window config registers; `ssb_pcmcia_switch_segment()` selects the 0/1 memory segment; `ssb_pcmcia_get_invariants()` parses CISTPL tuples into `ssb_init_invariants`; `ssb_pcmcia_init()`, `ssb_pcmcia_exit()`, and `ssb_pcmcia_hardware_setup()` handle setup and teardown. SPROM support is built from `ssb_pcmcia_sprom_read_all()`, `ssb_pcmcia_sprom_write_all()`, and sysfs `ssb_sprom` show/store callbacks.

Control flow: every MMIO access takes `bus->bar_lock`, selects the requested core and segment, then reads or writes `bus->mmio`. SPROM sysfs calls the common SSB SPROM attribute helpers, which lock `sprom_mutex`, optionally freeze devices, and call the PCMCIA read/write callbacks. Invariant collection first reads the LAN MAC tuple, then vendor-specific tuples for board, PA, country, antenna, flags, and LEDs.

State and persistence: `bus->mapped_device`, `mapped_pcmcia_seg`, `sprom_size`, and `sprom_mutex` are runtime state. SPROM writes persist on card EEPROM and are explicitly user-visible/high-risk.

Dependencies and integration: uses Linux PCMCIA config/CIS APIs, GPIO-free raw MMIO, SSB core freeze/thaw, and common SPROM helpers in `sprom.c`.

Risks: core switching is retry-based and returns all-ones on failed reads, which can mask hardware faults. `ssb_pcmcia_sprom_check_crc()` is a TODO returning success, so sysfs writes rely on upper-layer formatting but not CRC validation here. SPROM writes are slow and destructive if interrupted. Tuple size checks protect parsing but unknown card tuple variants can fail discovery.

Test signals: exercise 8/16/32-bit reads and writes across both segments, scan multiple cores, read the sysfs SPROM hex dump, attempt invalid SPROM stores, parse cards with missing/short tuples, and resume after PCMCIA COR reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/pcmcia.c -->
