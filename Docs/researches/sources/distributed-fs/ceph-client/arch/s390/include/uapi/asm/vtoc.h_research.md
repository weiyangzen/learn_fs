# sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/vtoc.h

## Purpose
Defines packed user-visible layouts for s390 DASD volume labels and VTOC data set control blocks. These structures let DASD tooling and filesystems parse CKD/FBA labels, extents, free-space descriptors, and CMS labels exactly as stored on disk.

## Important APIs, Types, And Functions
Core address types are `vtoc_ttr`, `vtoc_cchhb`, and `vtoc_cchh`. Label structures include `vtoc_volume_label_cdl`, `vtoc_volume_label_ldl`, and `vtoc_cms_label`. VTOC DSCB layouts include `vtoc_format1_label`, `vtoc_format4_label`, `vtoc_format5_label`, and `vtoc_format7_label`, plus extent helper structs such as `vtoc_extent`, `vtoc_ds5ext`, and `vtoc_ds7ext`.

## Control Flow
No code executes here. DASD code reads raw label sectors or records, overlays these packed structures, and interprets fields such as volume IDs, VTOC addresses, data set extents, device constants, free extents, and CMS allocation metadata.

## State And Persistence
The structures mirror persistent on-disk state. Packing is critical because padding would corrupt interpretation. Many fields are EBCDIC strings or hardware-specific binary values rather than native Linux text.

## Dependencies And Integration Points
Depends on Linux UAPI integer types. Integrates with s390 DASD block drivers, partition parsing, label utilities, and any userspace code reading VTOC records through kernel-exported headers.

## Risks And Edge Cases
Risks are ABI layout drift, endian assumptions, EBCDIC text handling, and confusing CDL, LDL, and CMS label variants. The one-byte year fields and packed multi-byte device geometry values require careful parsing. Structure changes can break disk tools.

## Test Signals
Useful tests parse known DASD label images, verify `sizeof` and `offsetof` for every exported struct, run partition discovery on CDL/LDL/CMS examples, and check userspace header compilation.
