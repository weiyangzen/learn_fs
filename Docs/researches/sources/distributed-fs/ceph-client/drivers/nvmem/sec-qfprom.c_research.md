# sources/distributed-fs/ceph-client/drivers/nvmem/sec-qfprom.c

Purpose: Secure Qualcomm QFPROM read-only provider that accesses corrected fuse space through SCM calls instead of direct MMIO.

Important APIs/types/functions: `struct sec_qfprom` stores the physical base and device. `sec_qfprom_reg_read()` reads byte-granular data by caching each aligned 32-bit `qcom_scm_io_readl()` result and returning selected bytes. Probe stores resource start as physical base and registers byte-granular NVMEM.

Control flow: probe gets memory resource, sets NVMEM size from it, and registers. Reads iterate per requested byte and invoke SCM whenever the current byte starts a new 32-bit word.

State/persistence: fuses persist in hardware and are exposed read-only. Driver state is the physical base and device pointer.

Dependencies/integration: OF compatible `qcom,sec-qfprom`; depends on Qualcomm SCM firmware and NVMEM legacy fixed cells.

Risks: repeated SCM calls can be slow for large reads. Access failures are mapped to `-EINVAL`, losing detailed firmware status. No explicit root-only flag is set, so permissions follow NVMEM defaults/cell policy.

Test signals: unaligned byte reads across word boundaries, SCM read failure, resource sizing, and fixed-cell consumers for secure-only platforms.
