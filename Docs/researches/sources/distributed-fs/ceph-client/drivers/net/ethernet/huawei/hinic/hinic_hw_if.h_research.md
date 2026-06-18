# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_if.h

## Purpose
Declares HINIC hardware-interface bitfields, BAR assignments, PCI function type helpers, module/node IDs, MSI-X defaults, function attribute state, register accessors, and HWIF public APIs.

## Important APIs, Types, and Functions
Important enums include PCI no-snoop/TPH settings, `hinic_func_type`, `hinic_mod_type`, `hinic_node_id`, `hinic_pf_action`, outbound/doorbell states, and MSI-X state. Key struct is `hinic_hwif` with `hinic_func_attr`. Inline functions `hinic_hwif_read_reg` and `hinic_hwif_write_reg` perform big-endian CSR access. Macros expose function identity and queue/IRQ counts.

## Control Flow
No standalone flow exists. The inline register helpers are invoked by all hardware modules, and the function-type macros drive PF/VF/PPF branching throughout device, management, mailbox, and EQ code.

## State and Persistence Behavior
`hinic_func_attr` caches hardware function identity and resource counts. BAR pointers persist for the device lifetime. Hardware registers hold the authoritative state for outbound enable, doorbell enable, PF actions, PPF election, DMA attributes, and MSI-X controls.

## Dependencies and Integration Points
Includes Linux PCI/io/type headers and is included by almost every HINIC hardware source file. It links CSR-level access to management modules, mailbox, EQs, command queues, IO queues, and upper NIC code.

## Risks
Bitfield macros are hardware ABI. `HINIC_IS_VF/PF/PPF` decisions affect whether code accesses management directly or through mailbox. Incorrect endianness in the inline accessors would corrupt all CSR interactions. Resource-count macros are trusted by MSI-X and EQ allocation code.

## Test Signals
Compile coverage, PF/VF probe, register read/write smoke tests, MSI-X setup, management routing by function type, and state toggles for outbound/doorbell validate this header.
