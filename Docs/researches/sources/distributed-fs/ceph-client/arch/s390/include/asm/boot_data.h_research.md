<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/boot_data.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/boot_data.h

Purpose: Declares early boot data buffers and boot debug filtering helpers.

Important APIs/types/functions: `early_command_line`, IPL block globals, secure IPL certificate/component list addresses, boot ring buffer state, `boot_rb_foreach()`, `bootdebug_filter_match()`, and `skip_timestamp()`. Source-visible declarations include: extern char early_command_line[COMMAND_LINE_SIZE];; extern struct ipl_parameter_block ipl_block;; extern int ipl_block_valid;; extern int ipl_secure_flag;; extern unsigned long ipl_cert_list_addr;; extern unsigned long ipl_cert_list_size;; extern unsigned long early_ipl_comp_list_addr;; extern unsigned long early_ipl_comp_list_size;; extern char boot_rb[PAGE_SIZE * 2];; extern bool boot_earlyprintk;.

Control flow: Early boot appends messages to a ring buffer, optional debug filters test message text after timestamps, and later code iterates buffered output.

State and persistence behavior: Persistent early state includes command line, IPL metadata, secure boot flags, certificate/component list addresses, and boot debug ring buffer content.

Dependencies and integration points: Direct includes are #include <linux/string.h>, #include <asm/setup.h>, #include <asm/ipl.h>. Integrated with Integrates IPL parsing, secure boot, early printk, boot debug, and s390 setup code..

Risks: Ring-buffer offsets and filter matching run early with limited facilities; bad bounds or stale IPL metadata can misreport boot security state.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 69 lines, 1662 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/boot_data.h -->
