<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nxu.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nxu.h

Purpose: Primary NX gzip hardware-format and utility macro header. It defines gzip CRB/CPB layouts, bitfield access helpers, function codes, errors, and helper prototypes.

Important APIs and types: Important types include `nx_dde_t`, `nx_csb_t`, `nx_ccb_t`, `vas_stamped_crb_t`, `nx_stamped_fault_crb_t`, `nx_gzip_cpb_t`, `nx_gzip_crb_t`, `nx_gzip_crb_cpb_t`, and `nx_eft_crb_t`. It defines `getnn/putnn`, CSB completion helpers, gzip function codes, and `ERR_NX_*` values.

Control flow: No executable flow, but the macros are the way compressor/decompressor code encodes and decodes all CRB/CPB fields before and after hardware submission.

State and persistence: No persistent state. It defines memory layouts shared between userspace and NX hardware/kernel.

Dependencies and integration points: Included by all NX gzip C files and relies on endian conversion, PPC timebase when enabled, and matching accelerator documentation.

Risks: Very high ABI risk: bit offsets, endian conversions, and struct alignment must remain exact. Macro misuse can silently write wrong fields.

Test signals: Passing compression/decompression plus correct condition-code handling validate the portions of this header used by the samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nxu.h -->
