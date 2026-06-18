<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/sprom.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/sprom.c

Purpose: provides common SSB SPROM helpers shared by host-specific SPROM sysfs implementations and architecture fallback providers.

Important APIs/types/functions: `ssb_attr_sprom_show()` reads a host SPROM image and formats it as a hex string. `ssb_attr_sprom_store()` parses a hex string, checks CRC through the host callback, freezes SSB devices, writes the image, thaws devices, and returns a sysfs byte count or error. `ssb_arch_register_fallback_sprom()` installs one fallback callback, `ssb_fill_sprom_with_fallback()` invokes it, and `ssb_is_sprom_available()` checks ChipCommon SPROM capability for newer PCI chips. Internal `sprom2hex()` and `hex2sprom()` do endian-aware conversion.

Control flow: show allocates a word buffer, locks `sprom_mutex` interruptibly, reads through the supplied callback, unlocks, formats, and frees. Store allocates, parses exact-length hex after stripping trailing whitespace, invokes the host CRC check, locks, freezes devices, writes through the supplied callback, thaws, unlocks, and frees.

State and persistence: local global state is only the fallback callback pointer. Store may persist data through the host-specific SPROM writer; this file coordinates locking and device freeze but does not access hardware directly.

Dependencies and integration: used by PCMCIA/PCI SPROM attributes and platform architecture code. Depends on SSB freeze/thaw and host callbacks for actual read/write/CRC behavior.

Risks: fallback registration is not locked and only prevents a second callback by plain pointer check. Store return precedence can expose write errors before thaw errors. Correctness relies on host callbacks validating CRC and write semantics; PCMCIA currently passes a stub CRC checker.

Test signals: sysfs SPROM read formatting, exact-length and malformed writes, interrupted mutex acquisition, freeze/write/thaw error paths, fallback duplicate registration, and ChipCommon rev >=31 SPROM capability detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/sprom.c -->
