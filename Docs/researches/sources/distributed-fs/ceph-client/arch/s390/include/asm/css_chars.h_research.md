<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/css_chars.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/css_chars.h

Purpose: Defines channel-subsystem characteristics returned by STSCH/CHSC discovery.

Important APIs/types/functions: `struct css_general_char` and `struct css_chsc_char` style bitfields for CSS feature availability. Source-visible declarations include: #define _ASM_CSS_CHARS_H; struct css_general_char {; u64 : 12;; u64 dynio : 1; /* bit 12 */; u64 : 4;; u64 eadm : 1; /* bit 17 */; u64 : 23;; u64 aif : 1; /* bit 41 */; u64 : 3;; u64 mcss : 1; /* bit 45 */.

Control flow: Discovery code stores hardware characteristic blocks and drivers test feature bits to select optional channel functions.

State and persistence behavior: Persistent state is probed CSS feature data.

Dependencies and integration points: Direct includes are #include <linux/types.h>. Integrated with Integrates channel subsystem initialization, CHSC, path management, and I/O feature gating..

Risks: Bit numbering and packed layout must match the architecture or features will be incorrectly enabled.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 47 lines, 904 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/css_chars.h -->
