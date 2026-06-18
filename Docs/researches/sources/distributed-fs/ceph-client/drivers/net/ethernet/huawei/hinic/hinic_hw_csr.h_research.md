# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_csr.h

## Purpose
Defines the HINIC PCI BAR register offsets used by the low-level hardware layer. It covers function attributes, DMA attributes, PPF election, API command chains, MSI-X controls/counters, and AEQ/CEQ page and control registers.

## Important APIs, Types, and Functions
There are no functions or runtime types. Important macro families include `HINIC_CSR_FUNC_ATTR*_ADDR`, `HINIC_CSR_DMA_ATTR_ADDR`, `HINIC_CSR_PPF_ELECTION_ADDR`, `HINIC_CSR_API_CMD_*_ADDR`, `HINIC_CSR_MSIX_*_ADDR`, AEQ/CEQ MTT page address macros, and AEQ/CEQ control, consumer, and producer index register macros.

## Control Flow
The header has no direct flow. It drives register access performed in `hinic_hw_if.c`, `hinic_hw_eqs.c`, `hinic_hw_api_cmd.c`, and mailbox setup code.

## State and Persistence Behavior
These offsets address device-resident state: function readiness and type, DMA attributes, PPF election, API command chain descriptors, interrupt moderation counters, event queue page tables, queue lengths, and producer/consumer indices. Values persist in hardware registers until reset or explicit teardown writes.

## Dependencies and Integration Points
Used with `hinic_hwif_read_reg` and `hinic_hwif_write_reg`, which perform big-endian BAR register access. Integrates all higher layers with the PCI config BAR and interrupt BAR register map.

## Risks
This file is pure hardware ABI. Wrong offsets or strides can make code access unrelated CSRs while still compiling. AEQ/CEQ register macros assume queue id and page numbers are within hardware-supported ranges; callers must validate page counts and queue counts.

## Test Signals
Probe on supported PF/VF functions, HWIF readiness reads, MSI-X attr programming, AEQ/CEQ initialization and teardown, API command submission, PPF election, and register dump diagnostics after command timeouts exercise this contract.
