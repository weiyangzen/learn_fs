# sources/distributed-fs/ceph-client/drivers/pci/vpd.c

Purpose: Implements Linux PCI Vital Product Data access. It discovers the VPD capability, probes usable VPD size, exposes binary sysfs access, exports read/write helpers, allocates whole VPD buffers, parses VPD resource tags and keywords, checks checksums, and applies quirks for devices with shared or unsafe VPD storage.

Important APIs and functions: Public entry points are `pci_vpd_init()`, `pci_read_vpd()`, `pci_read_vpd_any()`, `pci_write_vpd()`, `pci_write_vpd_any()`, `pci_vpd_alloc()`, `pci_vpd_find_id_string()`, `pci_vpd_find_ro_info_keyword()`, and `pci_vpd_check_csum()`. The `pci_dev_vpd_attr_group` exposes the `vpd` bin attribute. Internal helpers include tag-size decoding, `pci_vpd_size()`, `pci_vpd_available()`, `pci_vpd_wait()`, and function-0 redirection helpers.

Control flow: Initialization caches the VPD capability offset and initializes the per-device mutex. Reads optionally compute `vpd->len` by walking large and short resource data tags until an end tag or invalid tag. VPD reads issue aligned 32-bit transactions by writing the address register, waiting for `PCI_VPD_ADDR_F`, and reading data; writes require 4-byte alignment, write data first, set address plus flag, and wait for the flag to clear. Sysfs access wraps runtime PM get/put and honors `PCI_DEV_FLAGS_VPD_REF_F0`.

State and persistence: Mutable state is in `dev->vpd`: `cap`, lazily discovered `len`, and `lock`. VPD content is device EEPROM or firmware-backed persistent data, so writes may persist across reboot. Quirks can permanently disable access by setting `PCI_VPD_SZ_INVALID`, extend reported length, or route nonzero functions through function 0.

Dependencies and integration points: Depends on PCI config-space accessors, runtime PM config protection, unaligned helpers, exported PCI symbols, sysfs bin attributes, and PCI fixup infrastructure. Consumers include PCI drivers that read asset fields or serials from VPD.

Risks: VPD hardware has no interrupt completion path and may hang or time out; timeout handling must avoid wedging config access. Size probing trusts VPD format enough to bound future sysfs accesses, so malformed devices require quirks. Writes are especially risky because the backing store may be EEPROM. Function-0 sharing must only apply to genuinely identical multifunction devices.

Test signals: Build with PCI VPD and quirks, read `/sys/bus/pci/devices/.../vpd`, verify reads at odd offsets and truncated EOF behavior, check 4-byte write alignment rejection, exercise `pci_vpd_alloc()` and checksum helpers, and confirm blacklisted or function-0-linked devices behave as intended.
