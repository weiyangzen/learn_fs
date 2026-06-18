<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/chpid.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/chpid.h

Purpose: Defines channel-path ID descriptors and iteration helpers.

Important APIs/types/functions: `channel_path_desc_fmt0`, `chp_id_init()`, equality, increment, validity, and `chp_id_for_each()`. Source-visible declarations include: #define _ASM_S390_CHPID_H; struct channel_path_desc_fmt0 {; static inline void chp_id_init(struct chp_id *chpid); static inline int chp_id_is_equal(struct chp_id *a, struct chp_id *b); static inline void chp_id_next(struct chp_id *chpid); static inline int chp_id_is_valid(struct chp_id *chpid); #define chp_id_for_each(c) \.

Control flow: Helpers walk CSSID/ID combinations and compare or validate channel path identifiers.

State and persistence behavior: State is caller-owned channel-path ID values and hardware-provided descriptors.

Dependencies and integration points: Direct includes are #include <uapi/asm/chpid.h>, #include <asm/cio.h>. Integrated with Integrates CHSC, CSS path management, sysfs, and CCW path lookup..

Risks: Iteration bounds must match channel subsystem limits or path discovery misses valid paths.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 51 lines, 979 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/chpid.h -->
