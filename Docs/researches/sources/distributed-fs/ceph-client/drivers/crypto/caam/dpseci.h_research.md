<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci.h

Purpose: public DPSECI API header describing object limits, queue configuration, destination types, attributes, SEC capability data, congestion notification configuration, and function prototypes for MC commands.

Important APIs and control flow: defines `DPSECI_MAX_QUEUE_NUM`, `DPSECI_ALL_QUEUES`, `DPSECI_OPT_HAS_CG`, queue option bits, destination enum (`NONE`, `DPIO`, `DPCON`), `dpseci_cfg`, `dpseci_attr`, Rx/Tx queue config/attr structs, `dpseci_sec_attr`, congestion unit/mode flags, and prototypes implemented in `dpseci.c` for open/close/enable/disable/reset/is_enabled/get/set operations.

State and persistence behavior: no runtime state; it models MC object state and wire-level configuration passed by callers.

Dependencies and integration points: forward-declares `struct fsl_mc_io` and is consumed by DPAA2 CAAM object management. Its structs must match DPSECI command layouts and firmware semantics.

Risks and test signals: risks are ABI drift against MC firmware, incomplete validation of priority/destination ranges by callers, and confusion between Rx from SEC and Tx to SEC queue naming. Test signals are compile compatibility with `dpseci.c`, successful configuration of all queues or one queue, congestion group operation when `DPSECI_OPT_HAS_CG` is set, and accurate SEC accelerator counts used by algorithm registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci.h -->
