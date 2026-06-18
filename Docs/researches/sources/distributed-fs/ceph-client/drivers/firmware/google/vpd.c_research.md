# sources/distributed-fs/ceph-client/drivers/firmware/google/vpd.c

Purpose: Exposes Google Vital Product Data from coreboot CBMEM through `/sys/firmware/vpd`, including raw RO/RW sections and decoded key/value binary attributes.

Important APIs/types/functions: `vpd_cbmem` models the VPD header with magic and section sizes. `vpd_section` stores per-section mapping/sysfs state. `vpd_section_init()` maps a section, creates raw and decoded sysfs files, and marks it enabled. `vpd_section_attrib_add()` creates one sysfs binary file per valid key. `vpd_sections_init()` validates magic and initializes RO/RW sections.

Control flow: The coreboot driver binds tag `CB_TAG_VPD`, creates the top-level kobject, maps the VPD header, validates `VPD_CBMEM_MAGIC`, maps RO then RW sections if present, and decodes each section by repeatedly calling `vpd_decode_string()`. Remove destroys attributes, sections, mappings, and kobjects.

State and persistence behavior: Global `ro_vpd`, `rw_vpd`, and `vpd_kobj` store sysfs/mapping state. The driver exposes firmware-provided data as read-only sysfs attributes and does not persist writes.

Dependencies and integration points: Depends on the coreboot bus, memory remapping, sysfs binary attributes, `vpd_decode.c`, and firmware kobjects.

Risks and test signals: Section sizes and value pointers come from firmware; malformed blobs can stop decoding silently because `vpd_section_create_attribs()` ignores final decode errors. Key names with non-alnum/underscore are intentionally skipped. Test with valid RO/RW VPD, raw file reads, invalid key names, malformed length encodings, absent sections, and remove cleanup.
