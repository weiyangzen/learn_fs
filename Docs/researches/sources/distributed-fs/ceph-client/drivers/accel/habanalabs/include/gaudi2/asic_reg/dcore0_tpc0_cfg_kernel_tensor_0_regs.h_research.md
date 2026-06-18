# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_kernel_tensor_0_regs.h

Purpose: generated register map for TPC kernel tensor slot 0 in `DCORE0_TPC0_CFG`. It exports 20 `mmDCORE0_TPC0_CFG_KERNEL_TENSOR_0_*` constants from `0x400B000` to `0x400B04C`.

Important APIs/types/functions: no executable API. The macros describe tensor base address low/high, padding value, tensor configuration, and five dimensions worth of size and stride registers, including high size/stride forms for dimension 4.

Control flow: none. External driver paths program these registers before launching or emulating a TPC kernel, typically paired with `dcore0_tpc0_cfg_kernel_regs.h` for kernel geometry and `dcore0_tpc0_cfg_regs.h` for execution control.

State and persistence behavior: MMIO register values define tensor memory layout for hardware. They persist in the TPC CFG block until reset/reprogramming and affect address generation, padding behavior, dimensional iteration, and stride calculation.

Dependencies and integration points: included by `gaudi2_regs.h`; semantically paired with the QM tensor version in `dcore0_tpc0_cfg_qm_tensor_0_regs.h`. It depends on callers knowing hardware packing semantics, as this header provides only addresses, not field masks for each tensor descriptor field.

Risks: wrong stride or size address use causes data corruption or invalid DMA-like tensor accesses. High/low address register ordering is error-prone. Because this file only maps tensor 0, callers must not assume it covers every tensor slot without consulting neighboring generated headers.

Test signals: register generation checks, compile checks through aggregate include, TPC kernel tests using nontrivial strides/padding/dimensions, and hardware debug reads confirming descriptor writes land at expected offsets.
