# sources/distributed-fs/ceph-client/include/linux/dasd_mod.h

Purpose: Exposes the minimal DASD block-device information hook needed outside the s390 DASD driver implementation.

Important APIs, types, and functions: Includes `<asm/dasd.h>`, forward-declares `struct gendisk`, and declares `dasd_biodasdinfo(struct gendisk *disk, dasd_information2_t *info)`.

Control flow: A caller with a DASD-backed `gendisk` supplies an output `dasd_information2_t`; the architecture DASD implementation fills device information. The header itself contains no inline logic and is guarded by `DASD_MOD_H`.

State and persistence: No state is stored here. Persistent or runtime DASD state lives in the block driver and the architecture-specific DASD definitions.

Dependencies and integration points: Ties generic block-layer code to the s390 DASD ABI. It depends on `struct gendisk` identity and `dasd_information2_t` layout from architecture headers.

Risks and test signals: Risks are ABI/layout drift in `dasd_information2_t`, calls on non-DASD disks, and missing architecture support. Test through DASD ioctl/info paths on s390 builds and by compiling non-s390 configurations that include the header indirectly.
