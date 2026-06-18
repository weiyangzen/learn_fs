# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/targethw.h

Purpose: Defines target hardware configuration and the `struct s_smt_hw` hardware state block embedded in the SMT context for the FDDI adapter.

Important APIs/types/functions: Provides PCI watermarks `RX_WATERMARK`/`TX_WATERMARK`, board IDs `SK_ML_ID_1`/`SK_ML_ID_2`, default `HW_PTR` as `void __iomem *`, optional `struct s_oem_ids`, and `struct s_smt_hw`. The state block stores I/O base, DMA channel, IRQ, flash state, PCI slot/handle/masks, hardware start/stop state, 64-bit adapter flag, hardware timer fields, PIC snapshots, FDDI home/canonical/physical addresses, MAC parameters/counters, ring-up flag, FORMAC state `struct s_smt_fp`, and optional OEM identity pointers.

Control flow: No executable flow. The structure layout is initialized by probe/board setup and then consumed by hardware modules. The `STARTED`/`STOPPED` constants gate destructive operations such as descriptor repair and queue clear.

State and persistence behavior: `struct s_smt_hw` is runtime adapter state. Register and descriptor code mutates `hw_state`, `mac_ring_is_up`, `t_start`, `t_stop`, `timer_activ`, MAC counters, address fields, and FORMAC queue state. The values are not durable, but some mirror persistent adapter configuration such as factory address and OEM ID selection.

Dependencies and integration points: Includes `skfbi.h` plus `fplus.h` or `fplustm.h` depending on `TAG_MODE`. The state is referenced by `hwt.c`, `hwmtm.c`, `pcmplc.c`, MAC/RMT code, and OS glue from `targetos.h`. PCI-specific members integrate with the Linux PCI driver and interrupt source masking.

Risks: This is a cross-module ABI inside the driver; field order and conditional compilation must match all users. The OS-specific and hardware-specific parts share one structure, so stale or partially initialized fields can affect interrupts, DMA, or state-machine decisions. `hw_state` assertions are used to prevent queue cleanup while BMUs are active.

Test signals: Adapter probe and reset should populate I/O, IRQ, address, and FORMAC fields; timer APIs should update `t_start/t_stop/timer_activ`; ring transitions should toggle `mac_ring_is_up`; queue clear/repair paths should reject calls when `hw_state != STOPPED`.
