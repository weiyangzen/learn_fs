## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/pkey.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/pkey.h` is a protected-key crypto
ioctl ABI in the s390 ceph-client Linux source snapshot. It has 473 lines and 21097 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
APQN identifiers, secure/protected/clear key blobs, EP11/CCA metadata, key-type flags, and pkey
ioctl request structures
Important macros/constants: `_UAPI_PKEY_H`, `PKEY_IOCTL_MAGIC`, `SECKEYBLOBSIZE`, `PROTKEYBLOBSIZE`, `MAXPROTKEYSIZE`, `MAXCLRKEYSIZE`, `MAXAESCIPHERKEYSIZE`, `MINEP11AESKEYBLOBSIZE`, `MAXEP11AESKEYBLOBSIZE`, `MINKEYBLOBSIZE`, `PKEY_KEYTYPE_AES_128`, `PKEY_KEYTYPE_AES_192`, `PKEY_KEYTYPE_AES_256`, `PKEY_KEYTYPE_ECC`, `PKEY_KEYTYPE_ECC_P256`, `PKEY_KEYTYPE_ECC_P384`, `PKEY_KEYTYPE_ECC_P521`, `PKEY_KEYTYPE_ECC_ED25519`, `PKEY_KEYTYPE_ECC_ED448`, `PKEY_KEYTYPE_AES_XTS_128`; plus 32 more.
Important types/layouts: `pkey_apqn`, `pkey_seckey`, `pkey_protkey`, `pkey_clrkey`, `ep11kblob_header`, `pkey_genseck`, `pkey_clr2seck`, `pkey_sec2protk`, `pkey_clr2protk`, `pkey_findcard`, `pkey_skey2pkey`, `pkey_verifykey`, `pkey_genprotk`, `pkey_verifyprotk`, `pkey_kblob2pkey`, `pkey_genseck2`, `pkey_clr2seck2`, `pkey_verifykey2`, `pkey_kblob2pkey2`, `pkey_apqns4key`; plus 5 more.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 17.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
pkey device, zcrypt/AP cards, dm-crypt protected-key flows, and userspace key-management tools.
Direct include dependencies detected here: `linux/ioctl.h`, `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for pkey device, zcrypt/AP cards, dm-crypt
protected-key flows, and userspace key-management tools. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
size/flag mistakes can expose key material or select the wrong crypto adapter/domain

### Test Signals
pkey ioctl selftests, AP queue selection tests, EP11/CCA key conversion, and negative size checks
