# sources/distributed-fs/ceph-client/fs/ntfs/layout.h

## Purpose
`layout.h` is the NTFS on-disk format map for this driver. It defines packed structures, constants, magic values, bit masks, and helper macros for boot sectors, MFT records, attributes, file names, security descriptors, indexes, quota records, reparse points, EAs, and LogFile record identification. It is the source of truth for interpreting little-endian NTFS metadata stored on disk.

## Important APIs, Types, and Functions
Key structures include `struct bios_parameter_block`, `struct ntfs_boot_sector`, `struct ntfs_record`, `struct mft_record`, `struct mft_record_old`, `struct attr_def`, `struct attr_record`, `struct standard_information`, `struct attr_list_entry`, `struct file_name_attr`, `struct guid`, `struct object_id_attr`, `struct ntfs_sid`, `struct ntfs_ace`, `struct ntfs_acl`, `struct security_descriptor_relative`, `struct sii_index_key`, `struct sdh_index_key`, `struct volume_information`, `struct index_header`, `struct index_root`, `struct index_block`, `struct reparse_index_key`, `struct quota_control_entry`, `struct index_entry_header`, `struct index_entry`, `struct reparse_point`, `struct ea_information`, and `struct ea_attr`.

Important enums and macros include `magic_*` record identifiers and `ntfs_is_*` helpers, system MFT record numbers (`FILE_MFT`, `FILE_LogFile`, `FILE_Bitmap`, `FILE_first_user`, etc.), MFT reference packing/unpacking (`MK_MREF`, `MREF`, `MSEQNO`, `MREF_LE`), attribute type codes (`AT_STANDARD_INFORMATION`, `AT_DATA`, `AT_INDEX_ROOT`, etc.), collation codes, attribute flags, file attribute flags, SID/RID constants, ACE and access-mask values, security descriptor flags, volume flags, index flags, quota flags, and reparse tags. The header uses `static_assert` for several fixed on-disk sizes.

## Control Flow and State
This header does not execute control flow, but its constants drive nearly every parser and validator in the NTFS implementation. Callers read packed little-endian fields from disk, convert them with `le*_to_cpu()`, check record magics through the helper macros, use offsets and lengths embedded in these structures to find variable data, and validate flags against masks. Structures such as `attr_record` branch conceptually on `non_resident`, while `index_entry` branches on `INDEX_ENTRY_END` and `INDEX_ENTRY_NODE`.

## State and Persistence Behavior
All structures describe persistent NTFS metadata. They are packed to match disk layout and many contain variable-length tails whose bounds must be validated by consumers. Persistent state represented here includes volume identity and geometry, cluster/MFT locations, MFT record allocation and sequence numbers, attribute extents and sizes, initialized size, Windows file flags, timestamps, directory B+ tree nodes, LogFile record magic, security descriptor indexes, quota state, reparse tags, and EA records.

## Dependencies and Integration Points
The header depends on kernel types, bit operations, lists, and byte-order definitions. It is included by `logfile.h` and many NTFS metadata consumers. `logfile.c` uses the magic helpers for `RSTR`, `RCRD`, `CHKD`, and empty records; inode, MFT, attribute, directory, security, and allocation code rely on the packed records and constants.

## Risks
The primary risk is ABI mismatch with disk. Any structure padding, missing `__packed`, wrong endian annotation, or incorrect size assumption can corrupt parsing or writes. Variable-length arrays and offset fields require strict bounds checks in consumers. Several definitions encode historical NTFS variants, so code must distinguish NTFS 1.x/3.x structures and Windows compatibility behavior. Security and reparse constants must be treated carefully because unsupported features may require read-only mounts or explicit rejection.

## Test Signals
Compile-time `static_assert`s catch some layout drift. Runtime signals should include mounting volumes with varied sector and cluster sizes, old and NTFS 3.1 MFT records, resident and non-resident attributes, attribute lists, directory indexes, security descriptor indexes, quota/reparse/EA attributes, dirty-volume flags, and malformed images with bad magic, impossible offsets, or truncated variable-length records.
