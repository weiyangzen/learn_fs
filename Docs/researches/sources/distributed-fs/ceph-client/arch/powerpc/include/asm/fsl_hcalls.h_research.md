# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_hcalls.h

Purpose: Provides inline wrappers for Freescale/ePAPR vendor hypercalls used to control partitions, DMA isolation, virtual MPIC MSI routing, error queues, nap state, device claims, and system reset.

Important APIs, types, and functions: Defines `FH_*` hcall numbers, `FH_HCALL_TOKEN()`, partition status constants, VCPU state constants, and `struct fh_sg_list`. Wrappers include `fh_send_nmi()`, device-tree property get/set, partition restart/status/start/stop/memcpy/stop_dma, `fh_dma_enable()`, `fh_dma_disable()`, `fh_vmpic_get_msir()`, `fh_system_reset()`, `fh_err_get_info()`, `fh_get_core_state()`, `fh_enter_nap()`, `fh_exit_nap()`, and `fh_claim_device()`.

Control flow: Each inline wrapper marshals arguments into registers, uses the ePAPR `ev_hcall*` helpers, then decodes return registers into output pointers. `CONFIG_PHYS_64BIT` changes physical-address argument packing for dtprops and memcpy scatter-gather entries.

State and persistence: No state is stored in the header. Hypercalls mutate hypervisor-owned partition/device/DMA/core state and copy results back through caller-provided buffers.

Dependencies and integration points: Depends on `asm/epapr_hcalls.h`, `asm/byteorder.h`, Linux errno/types, and Freescale hypervisor ABI. It integrates with board management, partition lifecycle code, error handling, DMA setup, and virtual interrupt controller paths.

Risks: ABI register ordering is brittle, especially where 64-bit physical addresses are split. Buffer length limits for dtprops and error queues must match hypervisor expectations. Some wrappers accept output pointers directly and assume callers provide valid storage. Hypercall failures are returned as Freescale status values, not normal Linux errno in all cases.

Test signals: Hypervisor ABI tests should cover 32-bit and `CONFIG_PHYS_64BIT` builds, property buffers at max length, partition state transitions, DMA enable/disable idempotence, scatter-gather memcpy packing, long/error returns, and output register decoding for MSIR and core-state calls.
