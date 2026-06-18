# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_kernel_regs.h

Purpose: generated register map for the TPC kernel configuration region of `DCORE0_TPC0_CFG`. It exports 53 `mmDCORE0_TPC0_CFG_KERNEL_*` address macros from `0x400B508` to `0x400B5D8`.

Important APIs/types/functions: no functions or types. Macro families define the kernel base address low/high registers, thread-id base and size registers for dimensions 0 through 4, tensor ID, kernel configuration registers, coefficient/preload sections, and low/high combined base-size registers for each dimension.

Control flow: none locally. Runtime code uses these constants while preparing TPC kernel execution descriptors or debug access sequences, programming address and geometry registers before execution is triggered through the broader TPC CFG block.

State and persistence behavior: names hardware state that describes the active TPC kernel: instruction base pointer, TID ranges, dimensional sizes, and kernel configuration metadata. Values persist in device MMIO state until overwritten or reset and directly influence the tensor processor's work partitioning.

Dependencies and integration points: included through `gaudi2_regs.h` with adjacent tensor, QM, sync-object, AXUSER, CFG, and mask headers. It is coupled to `dcore0_tpc0_cfg_kernel_tensor_0_regs.h` for tensor memory descriptors and to `dcore0_tpc0_cfg_regs.h` for command, execute, status, and interrupt registers.

Risks: off-by-one address generation in dimensional arrays can corrupt neighbor kernel or tensor configuration fields. The split low/high address registers require callers to preserve 64-bit address ordering and alignment. Mismatched TID size programming can lead to wrong work distribution or hardware faults.

Test signals: compile inclusion through `gaudi2_regs.h`; generated register-database consistency checks; command submission tests that launch TPC kernels with multidimensional TID spaces; negative tests for invalid tensor geometry and address alignment.
