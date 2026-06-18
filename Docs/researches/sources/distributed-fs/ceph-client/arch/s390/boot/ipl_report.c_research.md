<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/ipl_report.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/ipl_report.c

Purpose: Handles early Secure IPL report discovery and preservation for the s390 boot decompressor. It reads the IPL report list behind the IPL parameter list, identifies certificate and component report blocks, reserves the original report while placement decisions are still being made, then copies certificate and component data into boot data for the decompressed kernel.

Important APIs/types/functions: Uses `struct ipl_pl_hdr`, `struct ipl_rl_hdr`, `struct ipl_rb_hdr`, `struct ipl_rb_certificates`, `struct ipl_rb_components`, and the `for_each_rb_entry` macro. Exports boot data such as `ipl_secure_flag`, `ipl_cert_list_addr`, `ipl_cert_list_size`, `early_ipl_comp_list_addr`, and `early_ipl_comp_list_size`. Key functions are `read_ipl_report()`, `save_ipl_cert_comp_list()`, `ipl_report_certs_intersects()`, `copy_components_bootdata()`, `copy_certificates_bootdata()`, and `get_cert_comp_list_size()`.

Control flow: `read_ipl_report()` first verifies that the copied IPL parameter block is valid and advertises an IPL report. It derives the report-list address from lowcore, walks bounded report blocks, records the certificate and component blocks, and reserves the whole report with `physmem_reserve(RR_IPLREPORT, ...)`. If either block is missing, it clears the certificate pointer and returns failure. Later `save_ipl_cert_comp_list()` sizes both lists, allocates a consolidated `RR_CERT_COMP_LIST` block, copies component entries and certificate payloads, frees `RR_IPLREPORT`, and clears `ipl_report_needs_saving`.

State and persistence: The file persists secure IPL state in bootdata-preserved globals consumed after decompression. The transient static pointers `certs` and `comps` reference the firmware-owned report while it is reserved. Once copied, `early_ipl_comp_list_*` and `ipl_cert_list_*` describe stable kernel-owned storage.

Dependencies and integration points: Integrates with `startup_kernel()` ordering, lowcore IPL parameter pointers, `physmem_info` reservation/allocation, `boot.h` intersection helpers, and UAPI IPL report structures. `physmem_info.c` calls `ipl_report_certs_intersects()` to avoid allocating over certificate bodies before they are copied.

Risks: Report walking trusts firmware lengths after simple bounds checks; malformed zero-length or overlapping blocks would be dangerous in early boot. Copying certificates from physical addresses must happen before the report reservation is released. Allocation alignment is only `sizeof(int)`, so consumers must not assume page alignment.

Test signals: Secure IPL boot with valid certificates/components, missing report-block fallbacks, KASLR-enabled placement avoiding certificate ranges, and checking exported certificate/component lists after boot are the strongest signals. Negative tests should corrupt report flags and block lengths in an s390 IPL test harness.

Source read size: 164 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/ipl_report.c -->
