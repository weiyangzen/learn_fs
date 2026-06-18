# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_qm_tensor_0_regs.h

Purpose: generated register map for queue-manager tensor slot 0 configuration in the TPC CFG block. It exports 20 `mmDCORE0_TPC0_CFG_QM_TENSOR_0_*` constants from `0x400B5DC` to `0x400B628`.

Important APIs/types/functions: macro-only API for tensor base address low/high, padding value, tensor configuration, dimension sizes, strides, and dimension 4 high size/stride fields.

Control flow: none. Runtime programming is performed by external queue submission or firmware paths that set tensor descriptors before issuing TPC work through the QM route.

State and persistence behavior: names MMIO state controlling tensor memory layout as seen by the QM-driven TPC execution path. State persists in registers until reset/rewrite and influences memory address generation and bounds interpretation.

Dependencies and integration points: included through `gaudi2_regs.h`; mirrors `dcore0_tpc0_cfg_kernel_tensor_0_regs.h` at a separate address range. It is used alongside `dcore0_tpc0_cfg_qm_regs.h` and sync-object registers.

Risks: parallel non-QM/QM tensor maps can be confused. Bad base/stride/size programming risks data corruption, invalid access, or command hangs. High/low address pieces must be coherent.

Test signals: TPC QM tensor execution tests using tensor 0; descriptor readback after programming; generated layout comparison against hardware register source; stress cases for multidimensional strides and padding.
