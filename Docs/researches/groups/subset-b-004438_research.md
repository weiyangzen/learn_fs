# subset-b-004438 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_cmdq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_cmdq.c

## Purpose
Implements the HINIC synchronous command queue used by the driver to send low-level commands to firmware or on-card modules after the management and CEQ infrastructure is available. It owns command-buffer allocation, WQE construction, command doorbells, completion handling from the command CEQ, and firmware command queue context setup.

## Important APIs, Types, and Functions
Public entry points are `hinic_alloc_cmdq_buf`, `hinic_free_cmdq_buf`, `hinic_cmdq_direct_resp`, `hinic_init_cmdqs`, and `hinic_free_cmdqs`. Important helpers include `cmdq_prepare_wqe_ctrl`, `cmdq_set_lcmd_wqe`, `cmdq_set_direct_wqe`, `cmdq_sync_cmd_direct_resp`, `cmdq_ceq_handler`, `cmdq_init_queue_ctxt`, `init_cmdqs_ctxt`, and `hinic_set_cmdq_depth`.

## Control Flow
Initialization creates a DMA pool for 2 KiB command buffers, allocates command work queues, initializes each `hinic_cmdq`, writes command queue contexts to firmware through `HINIC_COMM_CMD_CMDQ_CTXT_SET`, registers `cmdq_ceq_handler` on CEQ event `HINIC_CEQ_CMDQ`, and sets the firmware command queue depth. A synchronous command allocates a WQE under `cmdq_lock`, stores stack-local completion and error-code pointers by producer index, formats the WQE in big endian, writes the first 8 bytes last, rings the command doorbell, and waits up to `CMDQ_TIMEOUT`. CEQ processing drains completed WQEs, distinguishes arm commands from regular commands through saved header data, completes waiters, clears the hardware busy bit, returns WQEs, and sends a follow-up arm command when needed.

## State and Persistence Behavior
Persistent runtime state is in `struct hinic_cmdqs` and per-queue `struct hinic_cmdq`: DMA pool, saved WQs, command queue page metadata, doorbell bases, completion pointer tables, errcode pointer tables, lock, and wrapped bit. Hardware-visible state includes command WQ pages, command queue context PFNs, CEQ arm/en bits, command depth, and doorbell writes. No disk state is kept.

## Dependencies and Integration Points
Depends on `hinic_hw_wq` for WQE allocation, `hinic_hw_wqe` layouts, `hinic_hw_mgmt` for context commands, `hinic_hw_eqs` for CEQ callbacks, and `hinic_hw_io` for doorbell areas. It is used by IO setup to program SQ/RQ contexts and clean offload context, and by other modules that need direct-response firmware commands.

## Risks
Timeout handling must null stack-local completion and errcode pointers before returning, otherwise late CEQ completions could dereference invalid stack addresses. Doorbell ordering relies on `wmb()` and first-8-byte-last WQE writes. The CEQ handler assumes WQE size inference from header and correct saved arm bit semantics. Error unwinds must unregister CEQ callbacks before freeing command queue tables. Endian conversion mistakes silently corrupt firmware commands.

## Test Signals
Useful signals include command queue init/free across PF and VF paths, direct response success and nonzero firmware error code, command timeout with CEQ dump, CEQ arm command completion, queue full returning `-EBUSY`, command buffer size validation, module unload with outstanding command activity, and fault injection through failed WQ/DMA-pool/context setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_cmdq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_cmdq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_cmdq.h

## Purpose
Declares the command queue ABI and software state for HINIC firmware command submission. It defines command queue context bitfields, doorbell encoding, command-buffer limits, queue types, and the public API used by IO and device setup.

## Important APIs, Types, and Functions
Key types are `hinic_cmdq_buf`, `hinic_cmdq_arm_bit`, `hinic_cmdq_ctxt_info`, `hinic_cmdq_ctxt`, `hinic_cmdq`, and `hinic_cmdqs`. Public functions are `hinic_alloc_cmdq_buf`, `hinic_free_cmdq_buf`, `hinic_cmdq_direct_resp`, `hinic_init_cmdqs`, and `hinic_free_cmdqs`. Macros such as `HINIC_CMDQ_CTXT_PAGE_INFO_SET`, `HINIC_CMDQ_CTXT_BLOCK_INFO_SET`, `HINIC_SAVED_DATA_SET`, and `HINIC_CMDQ_DB_INFO_SET` encode hardware fields.

## Control Flow
The header has no runtime control flow. Its declarations support the init path in `hinic_hw_io.c`, command submission in `hinic_hw_cmdq.c`, and firmware context validation in PF mailbox handling.

## State and Persistence Behavior
The header defines in-memory software state plus hardware-serialized context layouts. `curr_wqe_page_pfn`, `wq_block_pfn`, CEQ id, arm/en flags, wrapped bit, command type, and function ids are persistent for the lifetime of the hardware command queue context.

## Dependencies and Integration Points
Includes Linux PCI, spinlock, completion, and HINIC hardware interface/work-queue headers. It is integrated with CEQ event `HINIC_CEQ_CMDQ`, management command `HINIC_COMM_CMD_CMDQ_CTXT_SET`, and VF mailbox validation of command queue contexts.

## Risks
Bitfield masks and shifts are hardware ABI. The command buffer size allows only `HINIC_CMDQ_MAX_DATA_SIZE` after reserved bytes; callers that exceed it fail validation. Include order matters because `struct hinic_hwdev` and `struct hinic_cmdq_pages` are supplied by other HINIC headers.

## Test Signals
Compile coverage, command queue context setup for PF/VF, VF command queue context mailbox validation, boundary command buffer sizes, and CEQ command completions are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_cmdq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_csr.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_csr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_dev.c

## Purpose
Implements the main HINIC hardware-device lifecycle and firmware-facing device control. It initializes the hardware interface, MSI-X, AEQs, PF/VF management and mailbox channels, device reset/capability discovery, VF bookkeeping, firmware context, resource state, and later brings IO queues up and down for data traffic.

## Important APIs, Types, and Functions
Public functions include `hinic_init_hwdev`, `hinic_free_hwdev`, `hinic_hwdev_ifup`, `hinic_hwdev_ifdown`, `hinic_port_msg_cmd`, `hinic_hilink_msg_cmd`, callback registration helpers, queue accessors, MSI-X helpers, `hinic_hwdev_hw_ci_addr_set`, `hinic_set_interrupt_cfg`, and `hinic_get_board_info`. Important internal routines include `parse_capability`, `get_capability`, `init_msix`, `init_fw_ctxt`, `set_hw_ioctxt`, `clear_io_resources`, `set_resources_state`, `get_base_qpn`, `init_pfhwdev`, `free_pfhwdev`, and `hinic_l2nic_reset`.

## Control Flow
`hinic_init_hwdev` allocates and initializes `hinic_hwif`, allocates `hinic_pfhwdev`, enables MSI-X, waits for outbound state, initializes AEQs, initializes PF/VF management and mailbox infrastructure, performs L2NIC reset, obtains capabilities, initializes VF functions, initializes firmware tables, and marks resources active. `hinic_hwdev_ifup` gets the global base QPN, initializes CEQs/command queues/work queues, creates QPs, waits or re-enables doorbells, and sends HW IO context. `hinic_hwdev_ifdown` clears IO resources, destroys QPs, and frees IO infrastructure. Free reverses resource state, VF state, management/mailbox, AEQs, MSI-X, and HWIF mappings.

## State and Persistence Behavior
Long-lived state is rooted in `struct hinic_hwdev` inside `struct hinic_pfhwdev`: hardware interface, MSI-X entries, AEQs, IO channel, function-to-function mailbox, NIC capabilities, port id, devlink private data, PF-to-management channel, NIC event callbacks, and self-command handlers. Firmware-persistent state includes resource active/clean state, firmware context, function table, interrupt config, SQ high-CI DMA address, base QPN, and queue depths.

## Dependencies and Integration Points
Integrates with PCI, MSI-X, devlink health reporters, SR-IOV helper `hinic_vf_func_init/free`, event queues, management messages, mailbox, IO/QP setup, and NIC-facing modules that use port commands. `hinic_msg_to_mgmt` is the common transport for most firmware commands, routing VF requests through mailbox.

## Risks
Initialization has many firmware-dependent stages and must unwind in exact reverse order. `hinic_hwdev_get_sq/rq` indexes `qps[i]` before range validation, so callers must pass valid queue indices. Some state waits try to re-enable outbound or doorbell state after timeout, which may hide hardware readiness issues. Callback unregister paths spin until running callbacks complete, so hung handlers can block teardown. Capability parsing relies on firmware-reported IRQ and queue counts.

## Test Signals
Probe/remove, PF and VF init, devlink health reporter creation, L2NIC reset failures, capability negotiation, resource state set/clear, ifup/ifdown loops, MSI-X config read/write, SQ CI address setup, board-info query, queue accessor bounds tests, and fault/watchdog event reporting are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_dev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_dev.h

## Purpose
Defines the central HINIC hardware device model, firmware command IDs, capabilities, management event IDs, resource state values, command payload structs, fault/watchdog payloads, PF extension state, and the public hardware-device API.

## Important APIs, Types, and Functions
Important enums include `hinic_port_cmd`, `hinic_hilink_cmd`, `hinic_ucode_cmd`, `hinic_mgmt_msg_cmd`, `hinic_cb_state`, `hinic_res_state`, fault types and fault levels. Important structs include `hinic_cap`, `hinic_cmd_fw_ctxt`, `hinic_cmd_hw_ioctxt`, `hinic_ceq_ctrl_reg`, `hinic_msix_config`, `hinic_board_info`, `hinic_hwdev`, `hinic_nic_cb`, `hinic_pfhwdev`, `hinic_dev_cap`, `hinic_fault_event`, and `hinic_mgmt_watchdog_info`. Public APIs cover lifecycle, port/hilink messaging, ifup/ifdown, callback registration, queue lookup, MSI-X configuration, SQ CI configuration, and board-info retrieval.

## Control Flow
The header has no execution, but it defines the staged contracts used by `hinic_hw_dev.c`, `hinic_hw_mgmt.c`, `hinic_hw_mbox.c`, `hinic_hw_io.c`, and the upper NIC driver. The port command enum maps user-facing NIC operations to firmware messages.

## State and Persistence Behavior
`struct hinic_hwdev` is the long-lived root object for one PCI function. Payload structs are serialized to firmware and therefore represent persistent hardware/firmware state such as queue depths, page sizes, resource state, interrupt moderation, VF random IDs, firmware context, board information, and health events.

## Dependencies and Integration Points
Includes devlink and the HINIC hardware interface, event queue, management, QP, IO, and mailbox headers. It links the hardware layer to SR-IOV, devlink health, L2NIC port configuration, queue operations, and management event callbacks.

## Risks
Command IDs and struct layouts are firmware ABI. Duplicate enum values exist in the port command list for compatibility and require careful command routing. Several structs start with `status` and `version` fields expected by firmware; changing field order or endian handling breaks responses. `HINIC_MGMT_NUM_MSG_CMD` depends on command-base arithmetic.

## Test Signals
Build coverage, firmware command round trips for common port commands, fault/watchdog devlink events, MSI-X config get/set, capability parsing, VF command validation, and queue lifecycle tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_eqs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_eqs.c

## Purpose
Implements HINIC asynchronous and completion event queues. AEQs carry mailbox and management events and are processed through a workqueue; CEQs carry command queue completions and are processed through tasklets. The file allocates DMA pages, programs EQ registers, handles interrupts, dispatches callbacks, and tears queues down safely.

## Important APIs, Types, and Functions
Public APIs are `hinic_aeq_register_hw_cb`, `hinic_aeq_unregister_hw_cb`, `hinic_ceq_register_cb`, `hinic_ceq_unregister_cb`, `hinic_aeqs_init`, `hinic_aeqs_free`, `hinic_ceqs_init`, `hinic_ceqs_free`, `hinic_dump_ceq_info`, and `hinic_dump_aeq_info`. Internal logic centers on `eq_update_ci`, `aeq_irq_handler`, `ceq_irq_handler`, `ceq_event_handler`, `set_eq_ctrls`, `alloc_eq_pages`, `init_eq`, and `remove_eq`.

## Control Flow
Initialization clears hardware CI/PI registers, derives element size and page counts, programs control registers, arms the queue, allocates coherent pages, initializes elements with the current wrapped bit, configures MSI-X attributes, and requests an IRQ. AEQ IRQs clear resend counters and queue work; CEQ IRQs clear counters and schedule a tasklet. Handlers scan elements until the hardware wrapped bit indicates no more events, dispatch registered callbacks with running-state guards, advance consumer index and wrap state, then update the hardware CI with checksum and arm bit.

## State and Persistence Behavior
Each `hinic_eq` stores queue id, type, length, page size, consumer index, wrap bit, element/page geometry, MSI-X entry, IRQ name, coherent DMA addresses, and deferred execution object. Hardware state includes MTT page addresses, queue controls, producer/consumer index registers, and MSI-X resend counters.

## Dependencies and Integration Points
Uses CSR offsets from `hinic_hw_csr.h`, BAR access from `hinic_hw_if.h`, Linux IRQ/workqueue/tasklet APIs, and DMA coherent allocation. AEQ callbacks are registered by mailbox and management code; CEQ callbacks are registered by command queue code.

## Risks
Callback unregister waits for running flags but does not cancel already queued external work created by callbacks. Element wrap handling and endian conversion are critical for not skipping or replaying events. VF CEQ control programming goes through management firmware rather than direct CSR writes. Teardown must disable MSI-X, free IRQ, cancel work/tasklet, clear queue length registers, update CI unarmed, and only then free DMA pages.

## Test Signals
AEQ/CEQ init/free, MSI-X interrupt delivery, mailbox AEQs, management AEQs, command CEQs, callback unregister under traffic, VF CEQ control through firmware, EQ page-count boundary failures, forced unknown event types, and command timeout diagnostics exercise the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_eqs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_eqs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_eqs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_if.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_if.c

## Purpose
Implements direct PCI BAR hardware-interface access for a HINIC function. It maps config and interrupt BARs, waits for management/PF readiness, reads function attributes, elects PPF when applicable, initializes DMA attributes, controls outbound and doorbell state, programs MSI-X attributes, and masks/unmasks MSI-X entries.

## Important APIs, Types, and Functions
Public functions include `hinic_msix_attr_set`, `hinic_msix_attr_cnt_clear`, `hinic_set_pf_action`, `hinic_outbound_state_get/set`, `hinic_db_state_get/set`, `hinic_set_msix_state`, `hinic_glb_pf_vf_offset`, `hinic_global_func_id_hw`, `hinic_pf_id_of_vf_hw`, `hinic_init_hwif`, and `hinic_free_hwif`. Internal helpers include `hwif_ready`, `wait_hwif_ready`, `read_hwif_attr`, `set_hwif_attr`, `set_ppf`, and `dma_attr_init`.

## Control Flow
`hinic_init_hwif` maps BAR0 and BAR2, waits up to about 10 seconds for management readiness and PF readiness for VFs, reads attributes from CSR function registers, performs PPF election for PFs, and sets default DMA attributes before transactions proceed. Runtime helpers perform read-modify-write updates for function action, outbound state, doorbell state, DMA attrs, and MSI-X controls.

## State and Persistence Behavior
`struct hinic_hwif` stores the PCI device, mapped BAR pointers, and decoded function attributes: function index/type, PF index, PCI interface, PPF index, number of IRQs/AEQs/CEQs/DMA attrs, and VF offset. Hardware registers persist readiness, election, DMA attr, PF action, outbound, DB, and MSI-X state until reset or explicit writes.

## Dependencies and Integration Points
Uses CSR offsets from `hinic_hw_csr.h`, Linux PCI ioremap APIs, and big-endian register access wrappers declared in `hinic_hw_if.h`. It underpins every other hardware module by providing BAR access and decoded function identity.

## Risks
Register values are read as big endian. A `HINIC_PCIE_LINK_DOWN` value in attr1 indicates link failure and limits diagnostics. Readiness polling and automatic PPF election are timing-sensitive. MSI-X masking writes directly into the interrupt BAR's table layout, so wrong BAR mapping or index validation would affect interrupt delivery.

## Test Signals
Probe readiness timeout, BAR mapping failures, PF and VF attribute decoding, PPF election, DMA attr initialization, MSI-X attr/counter programming, MSI-X mask/unmask, outbound/doorbell state toggles, and PCI link-down diagnostics are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_if.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_io.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_io.c

## Purpose
Builds and tears down the HINIC IO channel beneath the NIC data path. It initializes CEQs, allocates work queues, maps the doorbell BAR, manages doorbell page allocation, initializes command queues, creates SQ/RQ queue pairs, writes queue contexts to firmware through command queue commands, and restores page-size state on free.

## Important APIs, Types, and Functions
Public APIs are `hinic_io_init`, `hinic_io_free`, `hinic_io_create_qps`, `hinic_io_destroy_qps`, and `hinic_set_wq_page_size`. Internal helpers include `init_db_area_idx`, `get_db_area`, `return_db_area`, `write_sq_ctxts`, `write_rq_ctxts`, `write_qp_ctxts`, `hinic_clean_queue_offload_ctxt`, `init_qp`, and `destroy_qp`.

## Control Flow
`hinic_io_init` initializes CEQs, allocates the shared WQ manager, maps the 4 MiB doorbell BAR, initializes the free doorbell-page ring, allocates command queue doorbell pages, asks firmware to use 256 KiB WQ pages, and initializes command queues. `hinic_io_create_qps` allocates QP, SQ WQ, RQ WQ, SQ doorbell, and CI table arrays, initializes each SQ/RQ pair, writes SQ and RQ contexts to firmware with `IO_CMD_MODIFY_QUEUE_CTXT`, and cleans offload context. Destruction reverses QP allocation, coherent CI memory, devm arrays, command queues, WQ page size, doorbell pages, BAR mapping, WQs, and CEQs.

## State and Persistence Behavior
`hinic_func_to_io` stores global QPN, CEQs, WQ manager, SQ/RQ work queues, QPs, depths, SQ doorbells, DB base, coherent CI table, command queue DB areas, command queues, VF info, link status, and NIC config. Firmware-visible persistent state includes queue contexts, WQ page size, offload context cleanup, and command queue context.

## Dependencies and Integration Points
Depends on event queues, command queues, work queues, QP context builders, PCI DMA APIs, and management messages. Called from `hinic_hwdev_ifup/ifdown`; upper NIC code later uses the returned SQ/RQ objects for TX/RX.

## Risks
Doorbell allocation uses a semaphore-protected ring over fixed 4 KiB DB pages; leaks or double returns corrupt DB assignment. `write_qp_ctxts` returns a booleanized OR, so exact failing command error can be lost. Queue context programming depends on command queue availability, creating tight init ordering. Non-VF free restores hardware WQ page size, but VF behavior differs. Partial QP creation unwinds only initialized queues and must preserve coherent memory cleanup.

## Test Signals
Ifup/ifdown cycles, CEQ and command queue init failures, doorbell exhaustion, QP allocation failure at each queue index, SQ/RQ context firmware errors, offload context clean failure, VF and PF WQ page-size behavior, and DMA leak checks are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_io.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_io.h

## Purpose
Declares the HINIC IO-channel state and lifecycle APIs. It defines doorbell sizing, WQ page sizing, DB types, IO paths, doorbell free-list bookkeeping, NIC config cache, and the `hinic_func_to_io` aggregate used by the hardware device.

## Important APIs, Types, and Functions
Key constants are `HINIC_DB_PAGE_SIZE`, `HINIC_DB_SIZE`, `HINIC_HW_WQ_PAGE_SIZE`, `HINIC_DEFAULT_WQ_PAGE_SIZE`, and `HINIC_DB_MAX_AREAS`. Important types are `hinic_db_type`, `hinic_io_path`, `hinic_free_db_area`, `hinic_nic_cfg`, `hinic_func_to_io`, and `hinic_wq_page_size`. Public APIs create/destroy QPs, init/free IO, and set WQ page size.

## Control Flow
The header has no execution. It defines the state consumed by `hinic_hw_io.c`, `hinic_hw_dev.c`, command queue code, QP code, and upper NIC modules.

## State and Persistence Behavior
`hinic_func_to_io` is long-lived during interface-up state and stores queue arrays, depths, doorbells, coherent CI memory, command queue resources, VF metadata, link status, and cached pause/autoneg configuration. `hinic_wq_page_size` is serialized to firmware.

## Dependencies and Integration Points
Includes HWIF, EQs, WQs, command queue, and QP headers. It bridges the control-plane hardware setup and the actual SQ/RQ data path.

## Risks
DB area sizing assumes a 4 MiB doorbell BAR with 4 KiB slots. `max_qps`, `sq_depth`, and `rq_depth` must match firmware capabilities and QP context encoding. The NIC config mutex protects only cached config state, not queue lifetime.

## Test Signals
Compile coverage, IO init/free, QP create/destroy, WQ page-size command success, DB allocation/return, and PF/VF paths validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mbox.c

## Purpose
Implements HINIC function-to-function mailbox transport used for VF-to-PF management proxying, PF-to-VF commands, mailbox responses, random-id validation for VF messages, and PF-side validation of common VF commands before forwarding to management firmware.

## Important APIs, Types, and Functions
Public APIs include callback registration/unregistration, `hinic_mbox_to_pf`, `hinic_mbox_to_vf`, `hinic_mbox_to_func`, `hinic_func_to_func_init/free`, `hinic_vf_mbox_random_id_init`, `hinic_mbox_check_func_id_8B`, and `hinic_mbox_check_cmd_valid`. Internal transport helpers include `recv_mbox_handler`, `send_mbox_to_func`, `send_mbox_seg`, `wait_for_mbox_seg_completion`, `resp_mbox_handler`, `recv_func_mbox_handler`, `response_for_recv_func_mbox`, and random-id helpers.

## Control Flow
Initialization allocates per-function receive and response buffers for up to 512 functions, allocates a coherent mailbox writeback status area, points the send mailbox at the CSR mailbox data area, registers AEQ callbacks for mailbox receive and send-result events, and registers a PF common mailbox callback for non-VF functions. Sending serializes under mailbox semaphores, segments messages into 48-byte chunks, writes header and segment data to mailbox CSRs, triggers the target AEQ, waits for writeback status, then waits for a response completion if ACK is requested. Receive AEQ handling validates source id and optional VF random id, reassembles segments by sequence id, dispatches responses to waiters or queues direct-send work, invokes PF/VF callbacks, and sends response mailboxes when requested.

## State and Persistence Behavior
State is in `hinic_mbox_func_to_func`: send/response semaphores, send mailbox CSR/writeback state, workqueue, per-function send/response assembly buffers, callback tables and bit states, send message id, event flag, mailbox lock, and VF random-id arrays. Hardware-visible state includes mailbox data CSRs, control/int registers, writeback status DMA address, AEQ delivery, and firmware-provisioned VF random ids.

## Dependencies and Integration Points
Depends on HWIF CSR access, AEQ callbacks, management messages, random number generation, workqueues, completions, and semaphores. `hinic_hw_mgmt.c` routes VF management requests through this file; PF handling forwards validated VF common commands to management firmware.

## Risks
Mailbox segmentation is concurrency-sensitive: sequence, length, message id, event flag, and response buffers must match under concurrent traffic. `hinic_func_to_func_free` always unregisters the PF common callback, so VF paths rely on callback state being harmless when not registered. Random-id checking reads from a fixed offset in the mailbox buffer and queues refresh work on mismatch. PF validation must reject forged function ids, invalid queue depths, invalid command queue contexts, and unsupported commands; gaps become VF isolation risks.

## Test Signals
VF-to-PF management commands, PF-to-VF commands, multi-segment messages, response timeout, mailbox writeback error codes, send-result AEQs, source function id mismatch, random-id unsupported/supported paths, random-id mismatch refresh, unsupported VF command rejection, FLR command handling, and teardown with queued mailbox work are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mbox.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mbox.h

## Purpose
Declares mailbox constants, CSR offsets, callback signatures, mailbox send/receive state, function-to-function mailbox aggregate state, validation helpers, and PF/VF mailbox APIs.

## Important APIs, Types, and Functions
Important types include `vf_cmd_check_handle`, `mbox_msg_info`, `hinic_recv_mbox`, `hinic_send_mbox`, callback typedefs, `mbox_event_state`, `hinic_mbox_cb_state`, `hinic_mbox_func_to_func`, `hinic_mbox_work`, and `vf_cmd_msg_handle`. Public APIs cover callback registration, mailbox init/free, message send to PF/VF/function, VF random-id init, and command validation.

## Control Flow
The header has no runtime flow. It defines state and contracts implemented by `hinic_hw_mbox.c` and consumed by management, SR-IOV, and NIC control paths.

## State and Persistence Behavior
The mailbox aggregate stores transient in-memory send/receive state plus VF random ids cached from firmware. CSR offsets and writeback status describe hardware-persistent mailbox coordination points.

## Dependencies and Integration Points
Forward references `hinic_hwdev` and uses `hinic_mod_type` from HWIF definitions. It integrates VF mailbox callbacks with PF management forwarding and VF NIC event delivery.

## Risks
Callback state bit numbering is ABI only within the driver but drives teardown waits. `HINIC_MAX_FUNCTIONS` sizes large per-function arrays. CSR offsets must match hardware. `HINIC_MBOX_DATA_SIZE` is the maximum payload and must remain aligned with segmentation constants.

## Test Signals
Compile coverage, callback register/unregister, VF and PF mailbox send paths, oversized payload rejection, random-id initialization, and PF command validation cover this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mgmt.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mgmt.c

## Purpose
Implements PF-to-management CPU messaging and the shared `hinic_msg_to_mgmt` API. PF/PPF functions use API command chains and AEQ responses directly; VF functions are transparently proxied to their PF through mailbox. The file also handles unsolicited management messages and callback dispatch.

## Important APIs, Types, and Functions
Public APIs are `hinic_register_mgmt_msg_cb`, `hinic_unregister_mgmt_msg_cb`, `hinic_msg_to_mgmt`, `hinic_pf_to_mgmt_init`, and `hinic_pf_to_mgmt_free`. Key helpers include `prepare_header`, `prepare_mgmt_cmd`, `send_msg_to_mgmt`, `msg_to_mgmt_sync`, `msg_to_mgmt_async`, `recv_mgmt_msg_handler`, `mgmt_msg_aeqe_handler`, and `recv_mgmt_msg_work_handler`.

## Control Flow
PF initialization creates devlink health reporters, a single-threaded management workqueue, send/receive buffers, API command chains, and registers the AEQ callback for management CPU messages. Synchronous sends serialize through `sync_msg_lock`, increment a 9-bit message id, write a formatted command to the API command chain, and wait for a matching response completion. Incoming AEQs append segments into the direct or response receive buffer; response messages complete the waiter, while direct messages are copied into work items, dispatched to module callbacks, and answered asynchronously when the management CPU requested ACK.

## State and Persistence Behavior
`hinic_pf_to_mgmt` stores HWIF/HWDEV pointers, sync semaphore, message id, command buffer, ack buffer, direct and response receive messages, API command chains, callback table, and workqueue. Firmware-visible state includes API command chain descriptors and serialized message headers containing module, command, length, direction, PF/interface, and message id.

## Dependencies and Integration Points
Depends on API command chains, AEQs, mailbox for VF proxying, devlink health reporters, completions, workqueues, and the hardware device model. Used by command queue context setup, IO setup, port commands, board-info queries, interrupt config, fault/watchdog event handling, and capability discovery.

## Risks
Only synchronous management messages are accepted by the public API. Response matching relies on message id and single outstanding send under `sync_msg_lock`. Segment reassembly checks `seq_id` bounds but assumes received segment lengths fit the allocated buffer. VF routing changes timeout values for selected commands. Callback unregister waits for running state and can block if a callback stalls.

## Test Signals
PF management command success/failure, VF management command routed by mailbox, timeout with AEQ dump, wrong response message id, unsolicited L2NIC and COMM callbacks, direct management message response, oversized input rejection, API command init failure, and health reporter teardown are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mgmt.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mgmt.h

## Purpose
Declares the management-message header layout, management/config/common command IDs, management callback state, receive-message state, PF-to-management channel state, work item layout, and public management messaging APIs.

## Important APIs, Types, and Functions
Important enums include `hinic_mgmt_msg_type`, `hinic_cfg_cmd`, `hinic_comm_cmd`, and `hinic_mgmt_cb_state`. Core structs include `hinic_recv_msg`, `hinic_mgmt_cb`, `hinic_pf_to_mgmt`, and `hinic_mgmt_msg_handle_work`. Public APIs register/unregister module callbacks, send management messages, and initialize/free the PF-to-management channel.

## Control Flow
The header has no execution. Its header bit macros drive message formatting and parsing in `hinic_hw_mgmt.c`; command IDs are used across device, IO, command queue, mailbox validation, and devlink health code.

## State and Persistence Behavior
`hinic_pf_to_mgmt` contains transient host state, while the 64-bit message header and command payload structs are firmware ABI. Message ids, sequence ids, direction, ACK flag, module, command, function routing, and segment length persist across API command and AEQ exchanges.

## Dependencies and Integration Points
Includes HWIF and API command headers. It is consumed by most HINIC hardware modules for firmware commands and callback registration.

## Risks
Header bitfields are firmware ABI. `HINIC_COMM_CMD_*` values are also used in VF mailbox allow-list validation; adding commands without validation can open unsafe VF control paths. Buffer sizes and segmentation constants in the implementation must remain compatible with `MSG_LEN` and `SEG_LEN` widths.

## Test Signals
Compile coverage, management command send/response, callback register/unregister, VF mailbox proxy use, command ID allow-list validation, and response parsing validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_qp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_qp.c

## Purpose
Implements HINIC send and receive queue-pair primitives. It prepares firmware SQ/RQ contexts, initializes per-queue software resources, builds TX and RX WQEs, handles queue doorbells, tracks SKBs by WQE index, manages receive CQEs and producer-index DMA memory, and exposes helpers used by the upper NIC TX/RX path.

## Important APIs, Types, and Functions
Public APIs include context builders `hinic_qp_prepare_header`, `hinic_sq_prepare_ctxt`, `hinic_rq_prepare_ctxt`, SQ/RQ init/clean, free-space queries, TX offload task setters, WQE prepare/get/write/read/put helpers, SGE extraction, RQ WQE prepare/read/update helpers, and SQ doorbell writing. Important internals allocate `saved_skb` arrays, RQ CQEs, and RQ PI coherent memory.

## Control Flow
SQ/RQ initialization attaches HWIF/WQ/MSI-X state, sets queue ids and doorbells, and allocates saved-SKB arrays; RQ additionally allocates one coherent CQE per descriptor and a coherent PI word. Context builders read WQ first page PFNs and block PFNs, encode queue ids, CI/PI, prefetch values, interrupt ids, CQE addresses, and endianness for firmware. TX flow gets a WQE, prepares control/task/buffer descriptors, writes the WQE big-endian into the work queue, stores the SKB, and rings the SQ doorbell. RX flow prepares WQEs with buffer SGEs and CQE SGEs, updates PI memory, reads CQE `RXDONE`, retrieves the saved SKB and SGE length, clears done, and returns the WQE.

## State and Persistence Behavior
`hinic_sq` persists WQ pointer, qid, IRQ/MSI-X entry, hardware CI coherent address, doorbell base, and saved SKBs. `hinic_rq` persists WQ pointer, qid, affinity mask, IRQ/MSI-X entry, buffer size, saved SKBs, coherent CQEs, and coherent PI address. Firmware-visible state includes SQ/RQ contexts, WQ pages, CQE DMA addresses, SQ doorbells, and RQ PI memory.

## Dependencies and Integration Points
Depends on HINIC common/WQE/WQ/QP-context definitions, PCI DMA APIs, SKBs, and the IO layer. Upper NIC TX/RX code uses these helpers to enqueue packets and harvest completions.

## Risks
Saved SKB indexing assumes masked producer/consumer indices match WQ allocation. RQ allocates one coherent CQE object per descriptor, which is simple but memory intensive. Endian conversion must be applied exactly once when writing WQEs and reading SGEs/CQEs. `hinic_sq_read_wqe` does not check `IS_ERR` before dereferencing, so callers must only read when a completion is available. Doorbell writes require memory barriers before notifying hardware.

## Test Signals
TX/RX queue init/clean, descriptor allocation failures, TX WQE size variants, checksum and TSO task-field setup, SQ doorbells, RQ CQE RXDONE handling, RQ PI update, SKB recovery on TX/RX completion, endian validation, and queue wraparound are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_qp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_qp.h

## Purpose
Declares HINIC queue-pair constants, SQ doorbell bitfields, default SQ/RQ geometry, RX buffer size mapping, SQ/RQ/QP structures, and public queue-pair helper APIs for context setup and WQE manipulation.

## Important APIs, Types, and Functions
Important constants include `HINIC_SQ_WQEBB_SIZE`, `HINIC_RQ_WQEBB_SIZE`, 256 KiB SQ/RQ page sizes, 4K default depths, min/max queue depths, and `HINIC_RX_BUF_SZ`. Core structs are `hinic_sq`, `hinic_rq`, and `hinic_qp`. Public helpers prepare contexts, initialize/clean SQ/RQ, get free WQEBBs, set TX offload task fields, get/write/read/put SQ/RQ WQEs, extract SGEs, prepare RQ WQEs, and update RQ PI.

## Control Flow
The header has no direct flow. It defines the API used by IO creation and the upper NIC data path to manage WQEs and hardware queue contexts.

## State and Persistence Behavior
SQ/RQ structs store per-queue runtime state and pointers to hardware-visible coherent memory. Queue depth, page size, RX buffer size index, MSI-X entry, and doorbell fields are firmware/hardware contracts.

## Dependencies and Integration Points
Includes common HINIC definitions, HWIF, WQE, WQ, and QP context headers plus Linux SKB and PCI APIs. It bridges the hardware IO setup to packet TX/RX code.

## Risks
Changing queue geometry constants impacts firmware context layout, WQ allocation, and NIC buffer sizing. `HINIC_RX_BUF_SZ` and `HINIC_RX_BUF_SZ_IDX` must remain synchronized. Doorbell bitfields and offload task setters must match hardware WQE format.

## Test Signals
Compile coverage, queue create/destroy, firmware context setup, RX buffer-size negotiation, TX checksum/TSO field generation, doorbell writes, RX CQE handling, and queue depth boundary validation cover this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_qp.h -->
