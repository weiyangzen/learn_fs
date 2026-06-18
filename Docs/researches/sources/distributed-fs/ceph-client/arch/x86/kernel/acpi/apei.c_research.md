<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/apei.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/apei.c

Purpose: Implements x86 architecture hooks for ACPI Platform Error Interface handling, especially firmware-first corrected machine checks and conversion of APEI/CPER records into x86 MCE reports.

Important APIs/types/functions: `arch_apei_enable_cmcff()`, `arch_apei_report_mem_error()`, and `arch_apei_report_x86_error()`.

Control flow: APEI HEST parsing calls `arch_apei_enable_cmcff()` for corrected machine-check firmware-first entries. When `CONFIG_X86_MCE` is enabled, it saves the firmware threshold, checks firmware-first flags and hardware bank count, logs enablement, and disables listed MCE banks so firmware handles corrected errors first. Memory and processor error report hooks delegate to MCE/SMCA reporting helpers.

State and persistence behavior: With MCE enabled, persistent effects include saved APEI threshold limits and disabled machine-check banks for firmware-first corrected errors. Without `CONFIG_X86_MCE`, the functions compile to minimal success/delegation behavior where applicable.

Dependencies and integration points: Depends on ACPI APEI/HEST and x86 MCE/TLB flush headers. Integrates with ACPI HEST, corrected machine-check firmware-first mode, CPER memory error reporting, SMCA processor-context reporting, and RAS logging.

Risks and test signals: Risks include disabling the wrong MCE banks, ignoring malformed HEST bank lists, threshold mismatch, and behavior differences when MCE is disabled. Test ACPI APEI firmware-first systems, HEST tables with and without hardware banks, corrected error injection, CPER memory error reporting, SMCA error records, and `CONFIG_X86_MCE` off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/apei.c -->
