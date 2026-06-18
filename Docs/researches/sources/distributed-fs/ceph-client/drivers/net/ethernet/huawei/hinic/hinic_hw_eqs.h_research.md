# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_eqs.h

## Purpose
Declares the HINIC event queue register bit encodings, queue geometry constants, event type enums, EQ software structures, callback state, and AEQ/CEQ lifecycle APIs.

## Important APIs, Types, and Functions
Important constants include queue maxima, AEQE/CEQE sizes, default queue lengths, page size, and `HINIC_CEQ_ID_CMDQ`. Important enums are `hinic_eq_type`, `hinic_aeq_type`, `hinic_ceq_type`, and `hinic_eqe_state`. Core structs are `hinic_aeq_elem`, `hinic_eq_work`, `hinic_eq`, `hinic_hw_event_cb`, `hinic_aeqs`, `hinic_ceq_cb`, and `hinic_ceqs`. Public functions register/unregister callbacks, initialize/free AEQs and CEQs, and dump EQ state.

## Control Flow
No direct control flow is implemented here. The definitions drive `hinic_hw_eqs.c` interrupt handling and allow other modules to register event callbacks.

## State and Persistence Behavior
The header describes both host state and hardware-visible state. The host tracks callback running/enabled state, DMA pages, consumer index and wrap bit. Hardware consumes encoded control registers, element descriptors, and CI checksum/armed fields.

## Dependencies and Integration Points
Includes Linux workqueue, PCI, interrupt, bitops, and HINIC HWIF definitions. It is central to mailbox, management, command queue, and device initialization.

## Risks
AEQ and CEQ event IDs are ABI values. `HINIC_MAX_AEQ_EVENTS` and `HINIC_MAX_CEQ_EVENTS` size callback arrays, so new event IDs require range updates. Bitfield macros must match hardware documentation, especially CI checksum and wrapped fields.

## Test Signals
Compile coverage, registration/unregistration of all event types used by the driver, command CEQ completions, mailbox AEQs, management AEQs, and EQ state dumps validate the header.
