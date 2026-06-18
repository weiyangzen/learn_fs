# subset-b-004385 research

Work item: subset-b-004385

Scope: QLogic/Brocade BNA ethernet driver IOC, message queue, firmware ABI, register, hardware descriptor, and ENET/IOCETH orchestration files under `sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_ioc_ct.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_ioc_ct.c

### Purpose
`bfa_ioc_ct.c` provides the CT and CT2 ASIC-specific implementation behind the common `struct bfa_ioc_hwif` interface used by the BNA network IOC layer. It maps BAR0 register offsets, initializes PLLs and memory blocks, handles firmware ownership/reference counting, synchronizes failure recovery across PCI functions, chooses port mappings, and exposes CT/CT2 hardware operation tables through `bfa_nw_ioc_set_ct_hwif()` and `bfa_nw_ioc_set_ct2_hwif()`.

### Important APIs, Types, and Functions
- `bfa_nw_ioc_set_ct_hwif()` and `bfa_nw_ioc_set_ct2_hwif()` install static `bfa_ioc_hwif` tables into `ioc->ioc_hwif`.
- `bfa_ioc_ct_firmware_lock()` and `bfa_ioc_ct_firmware_unlock()` serialize firmware image ownership with hardware semaphores and the MMIO use-count register.
- `bfa_ioc_ct_reg_init()` and `bfa_ioc_ct2_reg_init()` populate `ioc->ioc_regs` for mailbox, heartbeat, state, semaphores, SRAM, PLL, and error/halt registers.
- `bfa_ioc_ct_map_port()` and `bfa_ioc_ct2_map_port()` read personality registers to assign `ioc->port_id`.
- `bfa_ioc_ct_sync_start()`, `sync_join()`, `sync_leave()`, `sync_ack()`, and `sync_complete()` coordinate multi-function IOC failure recovery using `ioc_fail_sync`.
- `bfa_ioc_ct_pll_init()` performs CT clock, reset, MAC, LMEM, and EDRAM BIST initialization.
- `bfa_ioc_ct2_pll_init()` supports CT2/NFC-assisted and fallback PLL/MAC/memory initialization paths.

### Control Flow and State
The common IOC layer first selects a hardware interface, maps the port, initializes register pointers, then uses these callbacks for firmware locking, PLL initialization, state register updates, mailbox interrupt mode, and recovery. Firmware lock flow returns early for flash/BIOS boot images, otherwise acquires `ioc_usage_sem_reg`, checks `ioc_usage_reg`, verifies the running firmware header with `bfa_nw_ioc_fwver_cmp()`, increments use count, and clears fail sync on first owner.

Failure synchronization stores requested PCI functions in high bits of `ioc_fail_sync` and acknowledgements in low bits. On first startup after an unclean exit, `sync_start()` clears fail sync, sets use count to one, and resets both IOC state registers to `BFI_IOC_UNINIT`. During recovery, `sync_complete()` waits until all required functions have acknowledged, then clears ack bits and writes both current and alternate IOC state registers to `BFI_IOC_FAIL`.

CT and CT2 register setup diverges mainly in function indexing. CT uses function-specific arrays for four PCI functions and port-specific LPU command/status registers. CT2 uses two port entries with changed semaphore/state offsets and includes `lpu_read_stat`.

### State and Persistence Behavior
All meaningful persistence is MMIO-backed hardware state rather than filesystem state. The file reads and writes IOC use counts, firmware states, heartbeat locations, fail-sync bits, semaphore locks, interrupt masks/status, PLL controls, NFC control registers, mailbox command/status registers, and halt bits. These survive long enough to coordinate multiple functions and driver reloads, and wrong values can affect other PCI functions sharing the ASIC.

### Dependencies and Integration Points
The implementation depends on `bfa_ioc.h` for IOC structure/callback contracts, `bfi.h` for firmware state values, `bfi_reg.h` for ASIC offsets and bit masks, and Linux MMIO primitives (`readl`, `writel`, `udelay`). It integrates upward with the common IOC state machine and downward with CT/CT2 register layouts. `bna_enet.c` indirectly relies on these callbacks through `bfa_nw_ioc_enable()`, mailbox interrupts, and IOC ready/failure notifications.

### Risks
- `BUG_ON()` is used for invalid use counts, impossible PLL/NFC states, and semaphore assumptions; hardware or firmware anomalies can panic the kernel.
- The firmware use-count and fail-sync protocol is shared across PCI functions, so missed semaphore handling or stale bits can wedge recovery or reset another function unexpectedly.
- PLL paths rely on fixed delays and polling loops; hardware timing changes or emulation can expose races.
- `bfa_ioc_ct_isr_mode_set()` mutates function personality bits and assumes the CT layout; CT2 has no equivalent callback.

### Test Signals
Useful validation signals include successful IOC enable/disable cycles on CT and CT2 hardware, firmware reload with multiple active PCI functions, forced heartbeat failure recovery, driver reload after unclean exit, MSI-X/INTx mode changes on CT, CT2 NFC-assisted and fallback PLL paths, and absence of stuck `BFI_IOC_FAIL`/`BFI_IOC_UNINIT` states after recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_ioc_ct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_msgq.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_msgq.c

### Purpose
`bfa_msgq.c` implements the host/firmware message queue transport used for larger firmware control messages. It owns a host-to-firmware command DMA ring, a firmware-to-host response DMA ring, mailbox doorbells for producer/consumer index updates, deferred command posting when the command ring is full, and message-class dispatch for response handlers.

### Important APIs, Types, and Functions
- `bfa_msgq_meminfo()` and `bfa_msgq_memclaim()` define and claim aligned DMA storage for command and response rings.
- `bfa_msgq_attach()` initializes command/response queue state, registers the MSGQ mailbox ISR, and registers IOC lifecycle notification.
- `bfa_msgq_regisr()` installs a response handler per BFI message class.
- `bfa_msgq_cmd_post()` copies a command into the command ring if space is available, otherwise queues it on `cmdq.pending_q`.
- `bfa_msgq_rsp_copy()` copies response payload bytes from the response ring without advancing the live queue consumer index.
- Internal FSMs `cmdq_sm_*` and `rspq_sm_*` manage stopped, init wait, ready, and doorbell-wait states.

### Control Flow and State
On `BFA_IOC_E_ENABLED`, `bfa_msgq_notify()` initializes a wait counter, starts both queue FSMs, and sends a MSGQ init mailbox containing command and response DMA addresses/depths. `bfa_msgq_init_rsp()` drives both queues from init-wait to ready. Posting a command uses `ntohs(cmd->msg_hdr->num_entries)` to test free entries, copies one or more 64-byte entries with `__cmd_copy()`, invokes the command callback with `BFA_STATUS_OK`, and sends `CMDQ_E_POST` to trigger a producer-index doorbell. If the ring lacks space, the command entry remains on `pending_q` until firmware sends a command-consumer-index update.

Firmware responses arrive first as mailbox events handled by `bfa_msgq_isr()`. Response producer-index doorbells call `bfa_msgq_rspq_pi_update()`, which walks response entries until consumer equals producer, dispatches each message to `rsphdlr[msg_class]`, advances by `num_entries`, and then sends a response consumer-index doorbell. Firmware can request a command-ring copy using `BFI_MSGQ_I2H_CMDQ_COPY_REQ`; the driver replies in 28-byte chunks through mailbox messages until `bytes_to_copy` reaches zero.

### State and Persistence Behavior
Queue state is in-memory plus DMA-visible rings: producer/consumer indices, ring depths, pending command list, doorbell mailbox commands, copy state (`token`, `offset`, `bytes_to_copy`), and response handlers. IOC disable or failure resets indices and flags and drains pending commands with `BFA_STATUS_FAILED`. The rings themselves are not persisted beyond device lifetime.

### Dependencies and Integration Points
This file depends on `bfi.h` for MSGQ wire formats, `bfa_msgq.h` for queue structures, and `bfa_ioc.h` for mailbox queueing and IOC lifecycle notifications. `bna_enet.c` attaches MSGQ, registers the ENET class handler, and posts ENET commands for port, pause, stats, queue config, MAC, VLAN, RSS, and RIT operations.

### Risks
- Command callbacks indicate that a command was copied into the MSGQ ring, not that firmware completed the requested operation; higher layers must wait for class-specific responses.
- Response dispatch stops if a message class is out of range or lacks a handler, leaving later responses unprocessed until the issue is resolved.
- Ring-depth arithmetic assumes power-of-two depths because indexes are wrapped with bit masks.
- The code trusts `num_entries` in response headers for advancement; corrupt firmware data could desynchronize the ring.
- Stopped/init-wait states record doorbell-update flags when posts occur, so callers must tolerate delayed notification.

### Test Signals
Signals include MSGQ init success after IOC enable, command queue full and pending-list drain behavior, correct producer/consumer doorbells, multi-entry command and response wrapping, class dispatch for ENET responses, copy-request chunk sequencing, pending-command failure callbacks on IOC failure, and no stuck `dbell_wait` state under mailbox backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_msgq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_msgq.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_msgq.h

### Purpose
`bfa_msgq.h` declares the software-side MSGQ transport structures and public API used by BNA modules to send variable-size firmware commands and receive asynchronous responses through DMA rings plus mailbox doorbells.

### Important APIs, Types, and Functions
- `BFA_MSGQ_FREE_CNT()` computes available command entries using producer/consumer indices.
- `BFA_MSGQ_INDX_ADD()` wraps queue indices.
- `BFA_MSGQ_CMDQ_NUM_ENTRY`, `BFA_MSGQ_CMDQ_SIZE`, `BFA_MSGQ_RSPQ_NUM_ENTRY`, and `BFA_MSGQ_RSPQ_SIZE` size the two DMA rings at 128 entries each.
- `bfa_msgq_cmd_set()` initializes a `struct bfa_msgq_cmd_entry` with completion callback, callback argument, byte size, and BFI message header pointer.
- `struct bfa_msgq_cmd_entry` is the caller-owned command descriptor queued or posted by MSGQ.
- `struct bfa_msgq_cmdq` tracks command queue FSM, producer/consumer index, DMA address, mailbox doorbells, copy-request state, and `pending_q`.
- `struct bfa_msgq_rspq` tracks response queue FSM, producer/consumer index, DMA address, handlers indexed by `BFI_MC_MAX`, and doorbell state.
- `struct bfa_msgq` combines command/response queues with IOC notification and init mailbox state.
- Public functions: `bfa_msgq_meminfo()`, `bfa_msgq_memclaim()`, `bfa_msgq_attach()`, `bfa_msgq_regisr()`, `bfa_msgq_cmd_post()`, and `bfa_msgq_rsp_copy()`.

### Control Flow and State
Consumers allocate or reserve DMA memory according to `bfa_msgq_meminfo()`, claim it with `bfa_msgq_memclaim()`, attach MSGQ to an IOC with `bfa_msgq_attach()`, register message-class handlers, then construct commands by filling a BFI message structure and applying `bfa_msgq_cmd_set()`. The header intentionally exposes the command-entry structure so higher layers can embed one command descriptor in persistent objects such as ENET, port, stats, TX, or RX state machines.

### State and Persistence Behavior
The declared structures are runtime state only. They persist across command submissions while the driver is attached, but IOC disable/failure transitions reset active queue state in the implementation. The most important contract is ownership: the command message memory and `bfa_msgq_cmd_entry` must remain valid until MSGQ either copies/posts it or queues it and later invokes the callback.

### Dependencies and Integration Points
The header includes `bfa_defs.h`, `bfi.h`, `bfa_ioc.h`, and `bfa_cs.h`. It uses Linux `list_head`, BFA DMA descriptors, mailbox command structures, IOC notify structures, BFI message classes, and BFI MSGQ entry sizes. ENET and other firmware clients depend on these declarations for command submission and response registration.

### Risks
- Queue free-count and index macros require power-of-two depths; changing queue depths without preserving that invariant breaks wrapping.
- `bfa_msgq_cmd_set()` stores pointers rather than copying message headers; callers must not use stack-allocated message structures for asynchronous commands.
- The handler array is sized by `BFI_MC_MAX`; mismatched message class constants between firmware ABI and driver would cause drops or out-of-range handling.
- The typo-like API name `bfa_msgq_regisr` is part of the local interface and must be used consistently.

### Test Signals
Header-level validation is compile-time and integration-oriented: all call sites should build after structure changes, DMA memory sizing should match implementation expectations, command entries should survive deferred posting, and response class registration should dispatch ENET responses through `bna_msgq_rsp_handler()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_msgq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi.h

### Purpose
`bfi.h` defines the common Brocade/QLogic Firmware Interface ABI shared by IOC, MSGQ, flash, and other message classes. It contains packed firmware message headers, DMA address layouts, message class IDs, IOC firmware image/version/state formats, MSGQ mailbox formats, and flash request/response formats.

### Important APIs, Types, and Functions
- `struct bfi_mhdr` is the common mailbox header, with `msg_class`, `msg_id`, and a union for host-to-firmware function/LPU routing or firmware-to-host token.
- `bfi_h2i_set()` and `bfi_i2h_set()` fill common mailbox headers.
- `BFA_I2HM()` maps host-to-firmware opcode numbers into firmware-to-host opcode space using `BFI_I2H_OPCODE_BASE`.
- `union bfi_addr_u` and `struct bfi_alen` define firmware-visible DMA address and address-length payloads.
- `enum bfi_mclass` assigns class numbers, including `BFI_MC_IOC`, `BFI_MC_FLASH`, `BFI_MC_CEE`, `BFI_MC_MSGQ`, and `BFI_MC_ENET`.
- IOC definitions include ASIC generation/mode enums, IOC control/getattr messages, firmware image header/version structures, firmware boot modes, heartbeat, and `enum bfi_ioc_state`.
- MSGQ definitions include mailbox init/doorbell/copy opcodes, `struct bfi_msgq_mhdr`, queue configuration structures, and copy-request/response structures.
- Flash definitions include query, erase, write, read, boot-version opcodes, and request/response payloads.

### Control Flow and State
This header is declarative, but it determines runtime control flow across the driver. IOC enable/disable/getattr messages use `struct bfi_ioc_ctrl_req`, `struct bfi_ioc_getattr_req`, and matching replies. MSGQ initialization uses `struct bfi_msgq_cfg_req` to hand firmware the DMA rings, then doorbell structures move producer/consumer indices. ENET commands use the MSGQ-specific `struct bfi_msgq_mhdr`, whose `num_entries` determines how many 64-byte queue entries a command or response consumes.

### State and Persistence Behavior
The structures describe firmware-visible state held in DMA memory, mailbox registers, or firmware memory. `struct bfi_ioc_image_hdr` and `struct bfi_ioc_fwver` are used to compare running firmware to the driver image. `enum bfi_ioc_state` values are written into hardware state registers by `bfa_ioc_ct.c` and interpreted by the common IOC state machine.

### Dependencies and Integration Points
`bfi.h` includes `bfa_defs.h` and is included by most files in this work item. `bfa_ioc_ct.c` uses IOC state, firmware header, ASIC mode/generation, and SRAM offsets. `bfa_msgq.c` uses MSGQ mailbox and ring formats. `bfi_cna.h` and `bfi_enet.h` layer class-specific message formats on top of these common headers.

### Risks
- Almost every structure is `__packed` and hardware ABI-sensitive; padding, field order, endian, or size changes can break firmware communication.
- `bfi_msgq_mhdr_set()` does not set `num_entries`; each caller must do so correctly.
- Some fields are host endian while many firmware payloads require big-endian conversions by callers.
- `BFI_MC_MAX` bounds response-handler arrays; adding classes must keep handler users in sync.
- Firmware image comparison and IOC state values affect multi-function firmware ownership and recovery.

### Test Signals
Useful signals include compile-time structure-size expectations, successful IOC enable/getattr/heartbeat handling, MSGQ init and doorbells, ENET responses arriving with expected opcodes, flash query/read/write operations, and firmware-version mismatch detection in `bfa_ioc_ct_firmware_lock()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi_cna.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi_cna.h

### Purpose
`bfi_cna.h` defines firmware mailbox message formats for converged network adapter functions outside the main ENET queue setup path: generic physical port enable/disable/statistics messages and CEE/DCBX/LLDP configuration and statistics messages.

### Important APIs, Types, and Functions
- `enum bfi_port_h2i` and `enum bfi_port_i2h` define port enable, disable, get-stats, and clear-stats opcodes.
- `struct bfi_port_generic_req` and `struct bfi_port_generic_rsp` provide message-tagged request/response layouts for enable/disable/clear style operations.
- `struct bfi_port_get_stats_req` carries a DMA address for port statistics retrieval.
- `union bfi_port_h2i_msg_u` and `union bfi_port_i2h_msg_u` group all port mailbox payloads by direction.
- `enum bfi_cee_h2i_msgs` and `enum bfi_cee_i2h_msgs` define CEE get-config, reset-stats, and get-stats opcodes.
- `struct bfi_cee_get_req`, `struct bfi_cee_get_rsp`, `struct bfi_cee_stats_req`, and `struct bfi_cee_stats_rsp` carry CEE DMA requests and completion status.
- `union bfi_cee_h2i_msg_u` and `union bfi_cee_i2h_msg_u` group CEE payloads.

### Control Flow and State
The file is ABI-only. Runtime users allocate DMA buffers for stats or configuration, fill a `bfi_mhdr`, and send class-specific mailbox messages through IOC mailbox plumbing. Responses carry command status and route back through registered mailbox handlers. The CEE attach and memory claim calls in `bna_ioceth_init()` indicate that CEE uses these formats as a common module attached to the same IOC.

### State and Persistence Behavior
No state is stored in this header. The structs describe transient mailbox messages and firmware-DMA exchanges. Persistent effects occur in firmware or device configuration: port enable/disable state, cleared counters, and fetched CEE/LLDP configuration/statistics.

### Dependencies and Integration Points
The header includes `bfi.h` for common message headers/address types and `bfa_defs_cna.h` for CNA-specific definitions. In this group, its strongest integration point is `bna_ioceth_init()`, which attaches `bfa_nw_cee` and claims DMA memory before MSGQ. The port message class is related to but distinct from the ENET port admin-up path in `bfi_enet.h`.

### Risks
- The file contains two reset-stats structs (`bfi_lldp_reset_stats` and `bfi_cee_reset_stats`) with identical layouts and comments, which can invite confusion at call sites.
- DMA address requests require correct endian/address packing by callers.
- Command status is only an 8-bit field; callers must translate firmware statuses carefully.
- The unions are packed ABI contracts and should not be reordered casually.

### Test Signals
Signals include successful CEE attach and configuration retrieval, CEE statistics DMA completion, reset-stats completion, physical port stat retrieval, and no mailbox class/opcode mismatch when CEE and port modules are enabled with the IOC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi_cna.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi_enet.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi_enet.h

### Purpose
`bfi_enet.h` defines the ethernet-specific hardware/firmware ABI for the BNA driver. It covers data-path descriptor layouts for TX, RX, and completion queues, interrupt block configuration, control-path MSGQ command/response formats, RSS/RIT and MAC/VLAN filtering, pause and loopback requests, attributes, and the full DMA statistics layout.

### Important APIs, Types, and Functions
- Data-path formats: `struct bfi_enet_txq_entry`, `struct bfi_enet_txq_wi_base`, `struct bfi_enet_txq_wi_vector`, `struct bfi_enet_rxq_entry`, and `struct bfi_enet_cq_entry`.
- Queue configuration formats: `struct bfi_enet_q`, `bfi_enet_txq`, `bfi_enet_rxq`, `bfi_enet_cq`, `bfi_enet_ib`, and `bfi_enet_ib_cfg`.
- Control opcodes: `enum bfi_enet_h2i_msgs` and `enum bfi_enet_i2h_msgs`.
- Generic command/response layouts: `struct bfi_enet_req`, `bfi_enet_enable_req`, and `bfi_enet_rsp`.
- Attribute formats: `bfi_enet_attr_req` and `bfi_enet_attr_rsp`.
- TX/RX config messages: `bfi_enet_tx_cfg_req`, `bfi_enet_tx_cfg_rsp`, `bfi_enet_rx_cfg_req`, and `bfi_enet_rx_cfg_rsp`.
- Filter/config commands: RIT, RSS, unicast, multicast, MAC+VLAN, VLAN block, pause, and loopback structures.
- Statistics formats: `struct bfi_enet_stats` and nested MAC, BPC, RAD, FC RX/TX, RXF, and TXF counters.

### Control Flow and State
Higher layers fill these structures, set `bfi_msgq_mhdr` with class `BFI_MC_ENET`, set `num_entries` according to the structure size, and post through MSGQ. Firmware responds with matching I2H opcodes. `bna_enet.c` dispatches responses by `msg_id`: queue config responses go to TX/RX objects, filter responses go to RXF, port admin and loopback responses go to ETHPORT, pause responses go to ENET, attributes go to IOCETH, stats responses update software statistics, and link/port/bandwidth AENs update link/TX state.

### State and Persistence Behavior
The structures configure firmware and hardware state: queue DMA pages, interrupt/coalescing parameters, RX/TX mode, filters, VLAN blocks, RSS keys/RIT, pause mode, loopback mode, WOL, and stats DMA buffers. The host-visible state is stored in BNA objects and DMA memory; firmware-visible state persists until cleared, disabled, or reset.

### Dependencies and Integration Points
The header includes `bfa_defs.h` and `bfi.h`. It is consumed by `bna.h`, `bna_enet.c`, and TX/RX/RXF modules outside this work item. `bna_hw_defs.h` duplicates or mirrors several descriptor constants for the driver-side fast path. The MSGQ header from `bfi.h` is embedded in every ENET control-path command.

### Risks
- The file warns that all values must be written in big-endian; missed conversions cause firmware misconfiguration.
- Packed descriptor and response layouts are hardware ABI-sensitive.
- `BFI_ENET_CFG_MAX` is 32, while masks are 32-bit; out-of-range resource IDs would silently overflow masks.
- Statistics copy logic in `bna_enet.c` assumes firmware packs selected per-RID stats densely according to masks.
- Some command IDs are no longer needed per comments but remain in the ABI; removing them would risk compatibility.

### Test Signals
Strong signals include TX/RX queue configuration success and valid doorbell offsets, RX completions with expected CQ flags, RIT/RSS programming, unicast/multicast/VLAN filter responses, pause and loopback responses, attribute query population, link and port AEN handling, WOL commands if supported, and stats DMA with correct endian-converted counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi_enet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi_reg.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi_reg.h

### Purpose
`bfi_reg.h` is the ASIC register map and bit-definition header for Brocade/QLogic BR-series adapters used by BNA and IOC code. It defines CT and CT2 BAR offsets, PLL controls, semaphores, mailbox registers, personality bits, IOC state aliases, interrupt bits/masks, NFC/CSI/PMM registers, and shared-memory page helpers.

### Important APIs, Types, and Functions
- Host function interrupt status/mask/page registers: `HOSTFN*_INT_STATUS`, `HOSTFN*_INT_MSK`, `HOST_PAGE_NUM_FN*`.
- PLL and reset controls: `APP_PLL_LCLK_CTL_REG`, `APP_PLL_SCLK_CTL_REG`, CT2 PLL registers, and many `__APP_PLL_*` bit fields.
- Hardware semaphores and info registers: `HOST_SEM*`, `CT2_HOST_SEM*`, and aliases like `BFA_IOC0_STATE_REG`.
- Mailbox command/status and mailbox memory offsets for CT and CT2 LPUs.
- Personality and mode registers: `FNC_PERS_REG`, `CT2_HOSTFN_PERSONALITY0`, `OP_MODE`, and function/port/intx bit masks.
- Halt/error/memory registers: `FW_INIT_HALT_P*`, `PSS_CTL_REG`, `PSS_ERR_STATUS_REG`, `ERR_SET_REG`, `MBIST_*`, and CT2 NFC/CSI controls.
- Interrupt status bit masks for CT and CT2, including mailbox, queue, and error bits.
- `PSS_SMEM_PGNUM()` and `PSS_SMEM_PGOFF()` compute SRAM page and offset.

### Control Flow and State
The file has no executable code, but it determines the MMIO control flow in `bfa_ioc_ct.c` and `bna_hw_defs.h`. IOC register initialization stores pointers derived from these offsets. PLL initialization sequences write these bit masks to clock and reset registers. Interrupt handling reads host function status, masks/unmasks mailbox and data interrupt bits, and clears status bits based on these definitions. Shared-memory helpers let the IOC layer address firmware SRAM pages.

### State and Persistence Behavior
The constants point at persistent hardware registers. Writes to use-count aliases, IOC state aliases, fail-sync aliases, interrupt masks, PLL registers, NFC controls, and personality/mode registers change device state that can outlive a single function call and can affect multiple PCI functions.

### Dependencies and Integration Points
This header is included by `bfa_ioc_ct.c` and `bna_hw_defs.h`. Its CT/CT2 distinction is consumed by `bna_reg_addr_init()` and `bfa_ioc_ct2_reg_init()`. Firmware ABI constants in `bfi.h` provide semantic state values, while this file supplies where those states are read/written.

### Risks
- Offset or bit-mask mistakes can cause writes to wrong device registers, with high blast radius.
- CT and CT2 define similar concepts at different offsets; using the wrong generation-specific macro can break interrupts or IOC ownership.
- Some bit names are reused or redefined for CT2, so include-order and semantic clarity matter.
- Register aliases use semaphore info registers as heartbeat/state/use/fail-sync storage; accidental semaphore confusion can corrupt IOC coordination.

### Test Signals
Signals include correct interrupt status/mask reads on CT and CT2, mailbox interrupt delivery, IOC state register transitions, fail-sync behavior, PLL initialization completion, CT2 NFC halt/resume behavior, shared-memory reads using page helpers, and absence of unexpected error/halt interrupts during driver enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna.h

### Purpose
`bna.h` is the central internal interface header for the BNA ethernet driver. It exposes queue arithmetic, DMA address conversion, RX mode state helpers, CAM list helpers, module accessors, and cross-module prototypes for BNA core, mailbox, IOCETH, ENET, ETHPORT, TX, RX, RXF, stats, and BNAD callback integration.

### Important APIs, Types, and Functions
- DMA conversion macros: `BNA_SET_DMA_ADDR()` and `BNA_GET_DMA_ADDR()`.
- Queue macros: `BNA_TXQ_WI_NEEDED()`, `BNA_QE_INDX_ADD()`, `BNA_QE_INDX_INC()`, `BNA_Q_INDEX_CHANGE()`, `BNA_QE_FREE_CNT()`, and `BNA_QE_IN_USE_CNT()`.
- Packet accounting: `BNA_UPDATE_PKT_CNT()`.
- Callback helpers for RXF start/stop/CAM filter completion.
- RX mode helpers for promisc, default, and allmulti enable/disable/inactive state using mode plus bitmask.
- `GET_RXQS()` maps RX path type to large/small/header/data RX queues.
- Resource-ID lookup macros `bna_tx_from_rid()` and `bna_rx_from_rid()`.
- CAM queue accessors and `bna_mac_find()`.
- Prototypes for exported internal APIs such as `bna_init()`, `bna_mod_init()`, `bna_enet_enable()`, `bna_ioceth_enable()`, TX/RX create/destroy/enable/disable/configure, and BNAD callbacks.

### Control Flow and State
The header shapes interactions between the core BNA object and submodules. BNAD calls BNA APIs to initialize resources, enable IOCETH/ENET, create TX/RX objects, adjust MTU and pause settings, set MAC/multicast/VLAN filters, and request stats. Firmware responses enter through `bna_mbox_handler()` and class-specific handlers declared here. TX/RX modules use resource-ID masks and active queues so ENET responses can be routed from firmware `enet_id` back to the right software object.

### State and Persistence Behavior
Most macros operate on state owned by `struct bna` and substructures declared in `bna_types.h`: queue indices, RID masks, RX mode bitmasks, CAM free/delete queues, callback slots, and DMA addresses. The header does not store state itself, but callers must maintain invariants such as stable list membership, valid RID values, and queue depths suitable for bitmask wrapping.

### Dependencies and Integration Points
The header includes `bfa_defs.h`, `bfa_ioc.h`, `bfi_enet.h`, and `bna_types.h`. It integrates the firmware ABI with Linux network-driver glue via BNAD callbacks and module APIs. `bna_enet.c` implements many prototypes in this header; TX/RX/RXF files implement the rest.

### Risks
- Queue index macros assume power-of-two depths.
- DMA conversion macros depend on struct layout casting through `struct bna_dma_addr`; changes to endian/layout would be risky.
- Callback helper macros clear callback fields before invocation, which prevents repeat calls but can hide reentrancy expectations.
- `bna_tx_from_rid()` and `bna_rx_from_rid()` perform linear list searches; stale or duplicate RIDs can misroute firmware responses.
- RX mode macros use separate `mode` and `bitmask` state; callers must keep both consistent.

### Test Signals
Signals include clean build coverage across all BNA modules, TX/RX response routing by RID, queue wrap/free/in-use calculations under boundary conditions, DMA address round-trips, RX mode transitions for promisc/default/allmulti, CAM allocation/free behavior, and BNAD callback invocation for enable, disable, link, stats, and cleanup flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_enet.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_enet.c

### Purpose
`bna_enet.c` implements the top-level BNA ethernet control plane. It handles ENET firmware responses and AENs, physical port/admin/link state (`ethport`), ENET start/stop/pause/MTU sequencing, IOCETH lifecycle around the common IOC, resource sizing/init/uninit, CAM module init, and hardware stats requests.

### Important APIs, Types, and Functions
- Response handlers: `bna_msgq_rsp_handler()`, `bna_bfi_ethport_*`, `bna_bfi_pause_set_rsp()`, `bna_bfi_attr_get_rsp()`, `bna_bfi_stats_get_rsp()`.
- Mailbox entry: `bna_mbox_handler()`, which routes errors to IOC error handling and mailbox interrupts to IOC mailbox ISR.
- ETHPORT FSM handles stopped, down, up response wait, down response wait, up, and last response wait states.
- ENET FSM handles stopped, pause init wait, started, config wait, config stop wait, child stop wait, and last response wait.
- IOCETH FSM handles stopped, IOC ready wait, ENET attribute wait, ready, ENET stop wait, IOC disable wait, last response wait, and failed.
- Public APIs implemented here include `bna_res_req()`, `bna_mod_res_req()`, `bna_init()`, `bna_mod_init()`, `bna_uninit()`, `bna_enet_enable()`, `bna_enet_disable()`, `bna_enet_pause_config()`, `bna_enet_mtu_set()`, `bna_ioceth_enable()`, `bna_ioceth_disable()`, `bna_hw_stats_get()`, and CAM handle helpers.

### Control Flow and State
Firmware responses arrive through MSGQ class `BFI_MC_ENET` and are dispatched by `msg_id`. Queue config responses are routed by `enet_id` to active TX/RX objects. RXF configuration and MAC/VLAN/RSS responses go to RXF handlers. Port admin/loopback responses drive the ETHPORT FSM. Pause responses drive ENET. Attribute responses populate `ioceth->attr` once and then advance IOCETH to ready. Link, port enable/disable, and bandwidth AENs update link, ETHPORT readiness, and TX bandwidth state.

ETHPORT readiness combines admin-up, RX-started, and firmware port-enabled flags for regular mode; loopback mode reverses the port-enabled condition. RX start/stop callbacks maintain `rx_started_count` and trigger port up/down transitions when the first RX starts or last RX stops.

ENET start first sends pause configuration. After firmware responds and no newer pause config is pending, it starts ethport, TX module, and RX module. Pause changes while started send a pause request. MTU changes stop RX, then restart RX and complete the MTU callback. Stop waits for ethport/TX/RX children through `bfa_wc`.

IOCETH enable calls `bfa_nw_ioc_enable()`, enables mailbox interrupts on IOC reset, waits for IOC ready, posts ENET attribute get, starts ENET/stats when ready, and calls BNAD ready. Disable stops ENET/stats, disables IOC, disables mailbox interrupts, and calls BNAD disabled. IOC failure disables mailbox interrupts, fails ENET/stats, and reports BNAD failure.

### State and Persistence Behavior
State lives in `struct bna` subobjects: flags, FSM states, pause config, MTU, callbacks, link status, RX-start count, IOC attributes, stats busy flags, RID masks, resource arrays, CAM free/delete queues, and DMA stats buffers. Firmware and hardware state is changed through MSGQ commands for pause, port admin, loopback, attributes, stats, and through IOC enable/disable.

### Dependencies and Integration Points
This file depends on `bna.h`, which brings in BFI ENET ABI, IOC APIs, types, and prototypes for TX/RX modules. It attaches CEE, flash, and MSGQ in `bna_ioceth_init()`, registers ENET response handling with MSGQ, and calls BNAD callbacks for link, IOC ready/failed/disabled, mailbox interrupt enable/disable, and stats completion. It also relies on `bna_hw_defs.h` macros through `bna.h`/types for interrupt register setup.

### Risks
- FSMs are strict; unexpected asynchronous event ordering calls `bfa_sm_fault()`.
- Attribute query is only stored once unless BNAD overrides values; stale default attributes before firmware query limit module resource sizing.
- Stats get is single-flight and copies selected RXF/TXF stats densely according to masks; mismatched firmware packing or RID masks corrupts stats mapping.
- Soft cleanup paths immediately invoke callbacks without hardware teardown.
- Link callbacks occur directly on AEN handling; ordering with port disable and RX stop must be correct to avoid false carrier state.
- Child stop waits depend on each child callback calling `bfa_wc_down()`.

### Test Signals
Signals include IOC enable to BNAD ready, ENET enable start of ethport/TX/RX, pause reconfiguration while starting and started, MTU change stopping/restarting RX, regular and loopback port up/down behavior, link AEN callback correctness, IOC failure and reset recovery, hard and soft disable behavior, stats busy/fail/success returns, CAM free/delete queue allocation, and response routing by `enet_id`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_enet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_hw_defs.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_hw_defs.h

### Purpose
`bna_hw_defs.h` defines BNA driver-side hardware constants, interrupt helper macros, doorbell encodings, queue descriptor structures, and CT/CT2 register/bit initialization macros. It bridges the raw register map in `bfi_reg.h` to the runtime `struct bna` register and bit-mask fields used by interrupt and queue code.

### Important APIs, Types, and Functions
- Resource defaults and limits: default TXQ/RXP/UCAM/RIT sizes, max MCAM, invalid RID, VLAN block constants, coalescing defaults, WI sizes, TX vector/data limits, small RX buffer size, and max priority.
- Register setup macros: `ct_reg_addr_init()`, `ct_bit_defn_init()`, `ct2_reg_addr_init()`, `ct2_bit_defn_init()`, and `bna_reg_addr_init()`.
- Interrupt classification and control: `BNA_IS_MBOX_INTR()`, `BNA_IS_HALT_INTR()`, `BNA_IS_ERR_INTR()`, `BNA_IS_MBOX_ERR_INTR()`, `BNA_IS_INTX_DATA_INTR()`, `bna_halt_clear()`, `bna_intx_disable()`, `bna_intx_enable()`, `bna_mbox_intr_disable()`, `bna_mbox_intr_enable()`, and `bna_intr_status_get()`.
- Doorbell helpers: `BNA_DOORBELL_Q_PRD_IDX()`, `BNA_DOORBELL_Q_STOP`, `BNA_DOORBELL_IB_INT_ACK()`, `bna_ib_start()`, `bna_ib_stop()`, `bna_txq_prod_indx_doorbell()`, and `bna_rxq_prod_indx_doorbell()`.
- Data structures: `bna_reg_offset`, `bna_bit_defn`, `bna_reg`, `bna_dma_addr`, `bna_txq_entry`, `bna_rxq_entry`, and `bna_cq_entry`.

### Control Flow and State
During `bna_init()`, `bna_reg_addr_init()` selects CT or CT2 based on PCI device ID and stores the correct interrupt status/mask addresses plus mailbox/error/halt bit masks. Interrupt paths use `bna_intr_status_get()` to read and clear non-mailbox interrupt status, then classify mailbox and error conditions. Mailbox interrupts can be masked/unmasked around IOC lifecycle transitions. Data-path queues ring producer-index doorbells with encoded values, and interrupt blocks are started/stopped by programming coalescing/ack/disable doorbell values.

### State and Persistence Behavior
The macros manipulate MMIO interrupt mask/status registers, IOC halt bits, IB doorbells, and queue doorbells. Driver state includes `struct bna_reg` and `struct bna_bit_defn` fields initialized from the device generation. Descriptor structs define DMA-visible queue entries consumed by hardware.

### Dependencies and Integration Points
The header includes `bfi_reg.h` for raw offsets and bit masks. It is included through `bna.h`/types by BNA core and datapath modules. It mirrors some descriptor constants from `bfi_enet.h`; both must stay ABI-compatible with firmware/hardware expectations.

### Risks
- Macro bodies evaluate arguments directly and may have side effects if passed complex expressions.
- Interrupt clear logic preserves mailbox bits while clearing other status; wrong masks can lose interrupts or leave interrupt storms.
- `bna_ib_ack()` ORs event counts into a cached doorbell value and relies on `BNA_IB_MAX_ACK_EVENTS` discipline elsewhere to avoid 16-bit overflow.
- CT/CT2 device ID selection lacks a default case; unsupported IDs leave register fields uninitialized.
- Descriptor structs require explicit endian handling by users.

### Test Signals
Signals include correct register initialization for CT and CT2 devices, mailbox interrupt masking/unmasking during IOC enable/disable, halt interrupt clear behavior, INTx data interrupt classification, IB start/stop with expected interrupt state, TX/RX producer doorbells advancing hardware queues, and descriptor layout compatibility with firmware completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_hw_defs.h -->
