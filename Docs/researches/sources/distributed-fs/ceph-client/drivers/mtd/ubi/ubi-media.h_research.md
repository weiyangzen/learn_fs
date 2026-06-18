# sources/distributed-fs/ceph-client/drivers/mtd/ubi/ubi-media.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/ubi-media.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/ubi-media.h

Purpose: this header defines UBI's on-flash ABI: magic values, format version, erase-counter headers, volume-identifier headers, volume table records, internal volume ids, compatibility flags, and fastmap data structures. It is the contract between images on flash, attach-time scanners, update/write paths, and external image-building tools.

Important APIs, types, and functions: key constants include `UBI_VERSION`, `UBI_MAX_ERASECOUNTER`, `UBI_CRC32_INIT`, `UBI_EC_HDR_MAGIC`, `UBI_VID_HDR_MAGIC`, `UBI_MAX_VOLUMES`, `UBI_VOL_NAME_MAX`, layout volume constants, and fastmap magic/size limits. Main structs are packed big-endian `struct ubi_ec_hdr`, `struct ubi_vid_hdr`, `struct ubi_vtbl_record`, and fastmap structs `ubi_fm_sb`, `ubi_fm_hdr`, `ubi_fm_scan_pool`, `ubi_fm_ec`, `ubi_fm_volhdr`, and `ubi_fm_eba`.

Control flow: no executable control flow exists here, but the layout drives IO and attach logic. EC headers identify valid UBI PEBs and carry erase counter, image sequence, VID offset, and data offset. VID headers map PEBs to `(vol_id, lnum)`, encode static/dynamic type, copy state, sequence numbers, and optional data CRC/size. Volume table records in the layout volume define user volumes and update markers. Fastmap structures summarize enough PEB and EBA state for faster attach.

State and persistence behavior: all structures are persistent and packed for exact flash representation. Multi-byte fields are big endian. CRC fields cover each header/record excluding the final CRC field. The layout volume stores two redundant LEBs of volume-table data. VID sequence numbers and copy flags are central to recovering from interrupted erase, update, and wear-leveling moves.

Dependencies and integration points: included by `ubi.h` and consumed by IO validation, attach scanning, EBA copy logic, volume table code, fastmap, and user-space tooling that writes UBI images. The compatibility enum for internal volumes tells older implementations whether to delete, preserve, reject, or attach read-only when unknown internal volumes are found.

Risks: any struct packing, field size, endian, or CRC coverage change is an on-flash compatibility break. `UBI_MAX_ERASECOUNTER` remains 31-bit despite a 64-bit EC field. Dynamic-volume VID data CRC fields are normally zero except for wear-leveling copies, which makes validation context-sensitive. Autoresize and skip-CRC flags affect first-boot sizing and static-volume integrity policy.

Test signals: verify binary offsets and sizes of EC/VID/vtbl/fastmap structs; attach old and new images; corrupt magic/CRC fields and confirm expected rejection; simulate duplicate LEB copies and validate sequence/copy-flag selection; test autoresize and skip-CRC volume flags; and fastmap attach fallback when fastmap headers are invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/ubi-media.h -->
