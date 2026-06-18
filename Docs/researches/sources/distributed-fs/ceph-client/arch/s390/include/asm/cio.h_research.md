<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cio.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cio.h

Purpose: Defines core channel I/O command, status, interruption, and DMA interfaces.

Important APIs/types/functions: `ccw0`, `ccw1`, ERW/ESW/IRB structures, CIW/node descriptors, `ccw_dev_id`, path helpers, CIO status flags, DMA allocator APIs, and CHSC helper declarations. Source-visible declarations include: #define _ASM_S390_CIO_H_; #define LPM_ANYPATH 0xff; #define __MAX_CSSID 0; #define __MAX_SUBCHANNEL 65535; #define __MAX_SSID 3; #define CCW_MAX_BYTE_COUNT 65535; struct ccw1 {; struct ccw0 {; #define CCW_FLAG_DC 0x80; #define CCW_FLAG_CC 0x40.

Control flow: CCW drivers construct channel command words and the CSS returns interruption response blocks with status and extended-status words; helpers allocate DMA-safe memory and schedule reprobes.

State and persistence behavior: Persistent state includes channel program buffers, subchannel/device IDs, DMA pools, path masks, and hardware status captured in IRBs.

Dependencies and integration points: Direct includes are #include <linux/bitops.h>, #include <linux/genalloc.h>, #include <asm/dma-types.h>, #include <asm/types.h>, #include <asm/tpi.h>, #include <asm/scsw.h>. Integrated with Integrates CCW bus, CSS, CHSC, FCX, EADM, DASD/tape/net drivers, and device DMA handling..

Risks: All packed status layouts are hardware ABI. Incorrect byte counts, flags, or path masks can hang I/O or mis-handle device errors.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 383 lines, 9263 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cio.h -->
