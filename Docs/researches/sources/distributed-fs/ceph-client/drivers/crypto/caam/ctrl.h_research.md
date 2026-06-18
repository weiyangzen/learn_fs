<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/ctrl.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/ctrl.h

Purpose: minimal public controller header for backend-level CAAM state shared with other modules.

Important APIs and control flow: declares `extern bool caam_dpaa2`, which tells non-controller code whether the probed CAAM instance is DPAA2-capable. There are no functions or inline helpers.

State and persistence behavior: the actual variable is defined and exported in `ctrl.c`; it is set during controller probe from compile-time parameter registers and then read by helpers such as DMA mask selection in `intern.h`.

Dependencies and integration points: included by `intern.h`, `jr.c`, and controller-adjacent code that needs DPAA2 mode knowledge without depending on full controller internals.

Risks and test signals: risk is global singleton state in a driver that otherwise represents per-device data, which can be wrong if multiple heterogeneous CAAM instances existed. Test signals are correct `caam_dpaa2` value before JR probing and DMA mask setup, and no stale value after probe deferral/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/ctrl.h -->
