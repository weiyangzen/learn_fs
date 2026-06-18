# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-rnm-defs.h

Purpose: describes the OCTEON Random Number Module (RNM) CSR address map and register bitfields for entropy collection, random-number enable/reset control, extended entropy register access, BIST status, and serial number access.

Important APIs/types/functions: address macros include `CVMX_RNM_CTL_STATUS`, `CVMX_RNM_BIST_STATUS`, `CVMX_RNM_EER_KEY`, `CVMX_RNM_EER_DBG`, and `CVMX_RNM_SERIAL_NUM`. Unions include `cvmx_rnm_bist_status`, `cvmx_rnm_ctl_status`, `cvmx_rnm_eer_dbg`, `cvmx_rnm_eer_key`, and `cvmx_rnm_serial_num`. `cvmx_rnm_ctl_status` has generic plus CN30XX, CN50XX, and CN63XX views for feature-specific fields such as entropy enable, RNG enable, resets, entropy-source select, extended entropy validity/lock, and mask-disable behavior.

Control flow: this header has no executable control flow. Drivers read or write the generated CSR addresses through `cvmx_read_csr`/`cvmx_write_csr`, select the chip-specific union view, and interpret or set bitfields.

State and persistence: state is entirely in hardware CSRs. Reset and enable bits affect live RNM/RNG operation. Serial number and EER registers expose hardware-provided values; no software cache is maintained.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG` from `cvmx.h` and the kernel/OCTEON bitfield convention. It is included by `octeon-feature.h`, where fuse/feature checks use RNM-related definitions, and by random or crypto-capability initialization code.

Risks: writing reset and enable fields in the wrong sequence can disable entropy generation. Chip-specific struct views differ, so using the generic view on older models can read or write reserved bits. The header does not enforce locking around EER access despite fields such as `eer_lck`.

Test signals: build tests should verify the header compiles for big- and little-endian bitfields. Runtime hardware tests should check BIST pass bits, RNG enable/reset transitions, EER valid/lock behavior, and feature-probe paths that include this header.
