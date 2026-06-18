# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi_reg.h

## Purpose
`bfi_reg.h` is the ASIC register map and bit-definition header for Brocade/QLogic BR-series adapters used by BNA and IOC code. It defines CT and CT2 BAR offsets, PLL controls, semaphores, mailbox registers, personality bits, IOC state aliases, interrupt bits/masks, NFC/CSI/PMM registers, and shared-memory page helpers.

## Important APIs, Types, and Functions
- Host function interrupt status/mask/page registers: `HOSTFN*_INT_STATUS`, `HOSTFN*_INT_MSK`, `HOST_PAGE_NUM_FN*`.
- PLL and reset controls: `APP_PLL_LCLK_CTL_REG`, `APP_PLL_SCLK_CTL_REG`, CT2 PLL registers, and many `__APP_PLL_*` bit fields.
- Hardware semaphores and info registers: `HOST_SEM*`, `CT2_HOST_SEM*`, and aliases like `BFA_IOC0_STATE_REG`.
- Mailbox command/status and mailbox memory offsets for CT and CT2 LPUs.
- Personality and mode registers: `FNC_PERS_REG`, `CT2_HOSTFN_PERSONALITY0`, `OP_MODE`, and function/port/intx bit masks.
- Halt/error/memory registers: `FW_INIT_HALT_P*`, `PSS_CTL_REG`, `PSS_ERR_STATUS_REG`, `ERR_SET_REG`, `MBIST_*`, and CT2 NFC/CSI controls.
- Interrupt status bit masks for CT and CT2, including mailbox, queue, and error bits.
- `PSS_SMEM_PGNUM()` and `PSS_SMEM_PGOFF()` compute SRAM page and offset.

## Control Flow and State
The file has no executable code, but it determines the MMIO control flow in `bfa_ioc_ct.c` and `bna_hw_defs.h`. IOC register initialization stores pointers derived from these offsets. PLL initialization sequences write these bit masks to clock and reset registers. Interrupt handling reads host function status, masks/unmasks mailbox and data interrupt bits, and clears status bits based on these definitions. Shared-memory helpers let the IOC layer address firmware SRAM pages.

## State and Persistence Behavior
The constants point at persistent hardware registers. Writes to use-count aliases, IOC state aliases, fail-sync aliases, interrupt masks, PLL registers, NFC controls, and personality/mode registers change device state that can outlive a single function call and can affect multiple PCI functions.

## Dependencies and Integration Points
This header is included by `bfa_ioc_ct.c` and `bna_hw_defs.h`. Its CT/CT2 distinction is consumed by `bna_reg_addr_init()` and `bfa_ioc_ct2_reg_init()`. Firmware ABI constants in `bfi.h` provide semantic state values, while this file supplies where those states are read/written.

## Risks
- Offset or bit-mask mistakes can cause writes to wrong device registers, with high blast radius.
- CT and CT2 define similar concepts at different offsets; using the wrong generation-specific macro can break interrupts or IOC ownership.
- Some bit names are reused or redefined for CT2, so include-order and semantic clarity matter.
- Register aliases use semaphore info registers as heartbeat/state/use/fail-sync storage; accidental semaphore confusion can corrupt IOC coordination.

## Test Signals
Signals include correct interrupt status/mask reads on CT and CT2, mailbox interrupt delivery, IOC state register transitions, fail-sync behavior, PLL initialization completion, CT2 NFC halt/resume behavior, shared-memory reads using page helpers, and absence of unexpected error/halt interrupts during driver enable.
