# Research: subset-b-004976

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_devlink.h -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_devlink.h

Purpose: declares the IOSM devlink-facing firmware flashing and coredump contract. It defines the firmware image header, RPSI commands, devlink parameter IDs, coredump region metadata, EBL response context, and the `struct iosm_devlink` object tying devlink, PCIe, SIO channel, flash parameters, and coredump regions together.

Important APIs/types: `iosm_devlink_sio`, `iosm_flash_params`, `iosm_devlink_image`, `iosm_ebl_ctx_data`, `iosm_coredump_file_info`, `iosm_rpsi_cmd`, and exported prototypes `ipc_devlink_init`, `ipc_devlink_deinit`, `ipc_devlink_send_cmd`. Constants such as `IOSM_DEVLINK_HDR_SIZE`, `IOSM_EBL_RSP_SIZE`, and `IOSM_NOF_CD_REGION` form ABI-sized parsing limits.

Control flow and integration: implementation users allocate this object during boot-stage imem initialization, open the devlink SIO channel through imem ops, then use the flash and coredump helpers to exchange RPSI/EBL commands with the modem. State is in-memory only: `rx_list`, `read_sem`, `channel_id`, erase flags, EBL response bytes, and region handles. Dependencies include Linux devlink, SKBs, completions, PCIe, and imem ops.

Risks: the packed firmware header and fixed buffer sizes must match firmware tooling exactly; malformed image headers or unexpected component types can drive incorrect flashing behavior. Test signals include devlink registration, parameter read/write, component-type parsing, coredump region registration, command CRC behavior, and erase flag transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_flash.c -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_flash.c

Purpose: implements modem flashing over the devlink SIO channel, including PSI transfer, EBL transfer, capability negotiation, SWID reading, flash erase checks, full erase, regional FLS download, and secpack flashing.

Important functions: `ipc_flash_link_establish`, `ipc_flash_boot_psi`, `ipc_flash_boot_ebl`, `ipc_flash_boot_set_capabilities`, `ipc_flash_read_swid`, and `ipc_flash_send_fls`. Internal helpers format EBL packets, compute checksums, validate EBL responses, write payload chunks, poll erase completion, and stream raw image regions.

Control flow: link establishment opens the devlink channel and reads the LER response. PSI is written in ROM phase and waits for a two-byte ACK, with coredump list retrieval on the coredump ACK. EBL is loaded only from PSI execution stage via an RPSI command/length/data handshake, then stores the EBL response. FLS flashing optionally full-erases NAND, sends either `FLASH_SEC_START` for monolithic images or per-region erase/address/raw-write commands, and sends `FLASH_SEC_END` on the last region.

State and dependencies: it mutates `ipc_devlink->param` erase flags and `ebl_ctx` response/capability bytes. It depends on imem devlink read/write, MMIO execution stage, coredump helpers, firmware blobs, devlink status notifications, and sleeps for erase polling. Risks are endian assumptions in response casting, firmware/header size trust, timeout sensitivity, and destructive full erase. Test signals: mocked read/write transcripts, invalid stage rejection, short reads, erase timeout, region splitting, SWID notification, and coredump ACK path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_flash.h -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_flash.h

Purpose: defines IOSM flashing wire constants, EBL/FLS command IDs, capability bits, response offsets, packet sizes, erase timing, and C structs used by `iosm_ipc_flash.c`.

Important APIs/types: `enum iosm_flash_package_type`, `iosm_out_of_session_action`, `iosm_out_of_session_type`, `iosm_ebl_caps`, `iosm_ebl_rsp`, `iosm_mdm_send_recv_data`, `iosm_ebl_error`, `iosm_swid_table`, `iosm_flash_msg_control`, and `iosm_flash_data`. It exports boot and flash entry points for PSI, EBL, capabilities, link establishment, SWID read, and FLS send.

Control flow role: this header is the protocol schema for flash.c. Packet sizes choose write-vs-data-write EBL frame lengths; response offsets select capability fields; erase timeout/interval drive polling. State is not persistent in the header, but constants define persistent modem flash effects such as full NAND erase.

Dependencies: requires `struct iosm_devlink`, `struct iosm_imem`, and `struct firmware` from the including translation units. Risks center on ABI drift with modem firmware: incorrect offsets like `EBL_OOS_CONFIG`, maximum payload sizes, or checksum field order can brick an update path. Test signals include compile-time inclusion in flash/devlink code, command encoding fixtures, bounds checks against `IOSM_EBL_HEAD_SIZE`, and mocked response buffers at every enum offset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_flash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem.c -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem.c

Purpose: owns the IOSM shared-memory runtime state machine. It initializes MMIO, protocol shared memory, task queue, timers, devlink boot channel, runtime mux/WWAN/control ports, and processes MSI events into message-ring, UL, DL, boot, crash, and power-management actions.

Important functions: `ipc_imem_init`, `ipc_imem_cleanup`, `ipc_imem_irq_process`, `ipc_imem_phase_update`, `ipc_imem_ipc_init_check`, channel allocation/open/close/update/cleanup helpers, TD update timers, `ipc_imem_ul_write_td`, `ipc_imem_ul_send`, and `ipc_imem_devlink_trigger_chip_info`. `ipc_imem_run_state_worker` creates mux, WWAN, control ports, debugfs, and sends modem-ready events once CP reaches `IPC_MEM_DEVICE_IPC_RUNNING`.

Control flow: IRQs are debounced into task-queue work; the handler updates AP phase from CP execution stage, runs boot/ROM completions, processes protocol messages, drains DL TDs to devlink/trace/WWAN ports, frees UL TDs, encodes mux uplink data, and schedules HP doorbells. Timers handle delayed TD updates, fast DL updates, DL buffer allocation retry, startup polling, and aggregation flush.

State/dependencies: `struct iosm_imem` holds phase, channel array, timer state, completions, CP status, flags, and subsystem pointers. Dependencies include MMIO, PCIe DMA, protocol ops, mux codec, WWAN, devlink, task queue, uevents, debugfs, trace, and hrtimers. Risks: race-sensitive phase transitions, completion waits, timer cancellation on cleanup, channel index/state mismatches, and bounded DL SKB allocation retries. Test signals include simulated execution-stage transitions, IRQ vector debounce, channel open/close failure unwind, pending UL/DL close waits, and runtime worker device-specific port filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem.h -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem.h

Purpose: declares the central IOSM shared-memory model: IPC phases, channel states/types, pipe directions, HP update identifiers, pipe/channel layouts, and the `struct iosm_imem` root object shared across PCIe, protocol, mux, devlink, WWAN, trace, debugfs, timers, and task queues.

Important types/APIs: `ipc_pipe`, `ipc_mem_channel`, `ipc_phase`, and `iosm_imem`; exported functions cover initialization, cleanup, IRQ dispatch, PM suspend/resume/s2idle, channel lifecycle, pipe cleanup/close, TD update timers, UL send, phase update/stringification, feature-set messages, IPC init handshake, and devlink chip-info trigger.

Control flow role: this header defines the invariants the implementation enforces. Channels move FREE -> RESERVED -> ACTIVE -> CLOSING/FREE. Phases progress OFF/ROM/PSI/EBL/RUN or crash/coredump. Pipes carry TD rings and SKB rings with old head/tail tracking. Timers and completions are embedded for asynchronous IRQ/tasklet coordination.

State/dependencies: all state is volatile driver memory except CP state mirrored through MMIO and DMA descriptors shared with the modem. Dependencies include Linux SKB/completion/hrtimer/work_struct plus local MMIO, PCIe, WWAN, uevent, and task-queue APIs. Risks include ABI-size assumptions in SKB control block use, channel count limits, timer state shared through one `hrtimer_period`, and incorrect phase assumptions. Test signals: structure initialization, phase strings, channel bounds, reserved/active transitions, and cleanup clearing subsystem flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem_ops.c -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem_ops.c

Purpose: provides the system-facing operations that WWAN netdevs, WWAN control ports, and devlink flashing/coredump paths use to open channels, write uplink data, close channels, and read downlink SIO data.

Important functions: `ipc_imem_sys_wwan_open/close/transmit`, `ipc_imem_wwan_channel_init`, `ipc_imem_sys_port_open/close`, `ipc_imem_sys_cdev_write`, `ipc_imem_sys_devlink_open/close/read/write/notify_rx`, and internal PSI transfer/DMA mapping helpers.

Control flow: WWAN open validates RUN phase then delegates to mux session open; transmit routes SKBs into mux encoding. Port open reserves and opens a control channel; writes DMA-map SKBs, queue them on the channel UL list, and schedule imem UL send. Devlink open has phase-specific behavior: in ROM/OFF it reserves the flash channel and enqueues chip info; in PSI/EBL it opens the real pipes. ROM writes perform PSI transfer through MMIO scratchpad and doorbell; later writes allocate DMA SKBs and block until CP consumes them. Reads wait on `read_sem` and copy queued SKBs.

State/dependencies: uses imem channel state, mux sessions, devlink SIO queues, completions, PCIe DMA helpers, MMIO execution/IP state, and protocol head/tail queries. Risks include blocking waits in close/write/read paths, ROM/PSI phase coupling, `nr_of_channels--` in devlink close, SKB ownership on failed writes, and timeout-dependent boot behavior. Test signals: phase rejection, DMA map failure, read timeout/short destination, pending TD close waits, PSI ROM exit codes, and mux aggregation channel sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem_ops.h -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem_ops.h

Purpose: declares the public operation boundary between imem and upper consumers: WWAN network interfaces, WWAN control ports, and devlink SIO flashing/coredump access.

Important APIs/constants: `IPC_READ_TIMEOUT`, `PSI_START_DEFAULT_TIMEOUT`, `BOOT_CHECK_DEFAULT_TIMEOUT`, mux session range constants, and prototypes for system port open/close/write, WWAN open/close/transmit/channel init, and devlink open/close/read/write/notify_rx.

Control flow role: callers do not manipulate pipes directly; they use these APIs so imem can enforce phase checks, channel reservation/opening, DMA mapping, task-queue scheduling, blocking read/write completions, and mux session routing. State is owned by `iosm_imem`, `iosm_cdev`, and `iosm_devlink`; this header does not persist data itself.

Dependencies: includes mux codec, which pulls in mux/imem/protocol types, so include ordering is important and circularity is managed through the local driver headers. Risks are API misuse from wrong phase or wrong channel ID, especially because some calls are blocking and may be used from contexts that must sleep. Test signals: build coverage for all upper layers, phase/unit tests around open calls, timeout behavior for read and boot, and mux session bounds 0..7.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_irq.c -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_irq.c

Purpose: implements IOSM doorbell writes and MSI interrupt acquisition/release. It is the lowest-level interrupt bridge between AP driver code and CP hardware.

Important functions: `ipc_doorbell_fire`, `ipc_acquire_irq`, and `ipc_release_irq`; internal `ipc_write_dbell_reg` computes the doorbell register address from the mapped BAR, IRQ number, and configured offset; `ipc_msi_interrupt` forwards MSI instances to `ipc_imem_irq_process` unless the PCIe object is in s2idle suspend.

Control flow: probe maps registers and calls `ipc_acquire_irq`, which allocates exactly one MSI vector and registers a threaded IRQ handler with `IRQF_ONESHOT`. Runtime callers fire doorbells for HPDA, IPC state transitions, and sleep control. Remove/error paths call `ipc_release_irq`, freeing requested IRQs and PCI vectors.

State/dependencies: state lives in `iosm_pcie` fields `ipc_regs`, `nvec`, doorbell offsets, PCI IRQ base, and `suspend` bit. Dependencies include PCI MSI APIs, threaded IRQs, IO writes, and imem IRQ dispatch. Risks include bad BAR/offset configuration, `irq - pci->irq` instance assumptions, suspend races dropping interrupts, and release loops depending on `nvec`. Test signals: MSI allocation failure, request_irq failure unwind, doorbell write offsets, IRQ ignored while suspended, and vector bounds returning `IRQ_NONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_irq.h -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_irq.h

Purpose: declares the IOSM IRQ/doorbell interface used by PCIe, protocol, PM, and imem layers.

Important APIs: forward-declares `struct iosm_pcie` and exposes `ipc_doorbell_fire`, `ipc_release_irq`, and `ipc_acquire_irq`. These functions hide BAR register layout and PCI MSI setup from higher layers.

Control flow role: `ipc_doorbell_fire` is called for IPC state requests, HPDA head-pointer updates, PSI boot notification, and PM sleep/active control. `ipc_acquire_irq` is called during PCI resource setup; `ipc_release_irq` is called during teardown and resource unwind.

State/dependencies: no persistent state in the header; all state is carried by `iosm_pcie`. The prototypes depend on `u32` being available through include context, normally via local PCIe/protocol headers. Risks are mostly integration risks: include ordering, misuse before BAR mapping, and firing doorbells after resources release. Test signals include compile coverage from `iosm_ipc_pcie.c`, `iosm_ipc_pm.h`, `iosm_ipc_protocol.h`, and imem boot paths plus runtime smoke tests that exercise each doorbell type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mmio.c -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mmio.c

Purpose: maps the CP scratchpad MMIO layout into helper functions for execution stage, chip info, ROM exit code, PSI address/size, IPC status, context info, CP version, and CP capabilities.

Important functions: `ipc_mmio_init`, `ipc_mmio_get_exec_stage`, `ipc_mmio_get_ipc_state`, `ipc_mmio_get_rom_exit_code`, `ipc_mmio_copy_chip_info`, `ipc_mmio_config`, `ipc_mmio_set_psi_addr_and_size`, `ipc_mmio_set_contex_info_addr`, `ipc_mmio_get_cp_version`, and `ipc_mmio_update_cp_capability`.

Control flow: initialization polls until CP writes a valid execution stage, validates fixed chip-info size, stores register offsets, and returns a small state object. Runtime boot writes PSI DMA address/size and later writes context-info/AP window registers during IPC init. Capability update reads CP version and capability bits to select MUX Lite vs aggregation and UL credit support.

State/dependencies: keeps base MMIO pointer, offsets, chip info metadata, context info physical address, mux protocol, and capability flags. Dependencies include Linux IO accessors, 64-bit nonatomic IO helpers, device logging, and mux capability constants. Risks: hard-coded offsets and chip-info size must match firmware; polling uses a 50*20ms bound; no locking around capability fields; CP version `0xffffffff` is treated by callers. Test signals: invalid exec stage timeout, unexpected chip info rejection, endian/64-bit writes for context/PSI, capability matrix tests, and null-pointer getter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mmio.h -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mmio.h

Purpose: defines the IOSM scratchpad ABI exposed by CP firmware: IPC states, ROM exit codes, execution-stage magic values, MMIO offset storage, capability masks, and the `iosm_mmio` state object.

Important types/APIs: `ipc_mem_device_ipc_state`, `rom_exit_code`, `ipc_mem_exec_stage`, `mmio_offset`, `iosm_mmio`, and prototypes for MMIO init, PSI/context writes, state getters, chip-info copy, configuration, and capability refresh. Capability masks `DL_AGGR`, `UL_AGGR`, and `UL_FLOW_CREDIT` control mux selection and credit mode.

Control flow role: imem maps execution-stage magic values to AP phases; flash uses ROM/PSI/EBL/RUN gating; protocol writes context info; imem ops perform PSI boot handoff through address/size registers. State is volatile MMIO plus cached capability metadata.

Dependencies: requires Linux types such as `dma_addr_t`, `phys_addr_t`, `size_t`, `u32`, `BIT`, and `struct device` from include context. Risks include treating firmware magic constants as stable ABI, unexpected CP capability versions, and offset mismatches. Test signals: compile include checks, mapping every execution stage to phase behavior, null-safe getters, and capability parsing for old and new CP versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mmio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux.c -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux.c

Purpose: manages the IP mux object and session lifecycle over the WWAN IPC channel. It creates the mux channel, opens/closes per-session interfaces, handles channel teardown, allocates mux transmit buffers, and restarts/stops network TX based on flow-control state.

Important functions: `ipc_mux_init`, `ipc_mux_deinit`, `ipc_mux_open_session`, `ipc_mux_close_session`, `ipc_mux_get_max_sessions`, `ipc_mux_get_active_protocol`, `ipc_mux_check_n_restart_tx`, plus internal channel/session scheduling helpers.

Control flow: opening the first session allocates and opens the WWAN channel through imem, suspends TD update timer while sending a blocking open-session ACB command, initializes session padding/flow state, and marks the mux active. Closing a session sends close-session, resets queues, and closes the channel when the last session is gone. Initialization preallocates DMA-backed UL ADB/ADGH SKBs and aggregation QLT tables based on MUX Lite vs aggregation.

State/dependencies: `iosm_mux` tracks sessions, channel ID, protocol, UL flow mode, transaction IDs, round-robin scheduling, ADB state, pending byte counters, and flags. Dependencies include imem channel APIs, mux codec command sending, WWAN flow control, PCIe SKB allocation, and protocol constants. Risks include session ID bounds, allocation unwind for aggregation QLTs, blocking command timeouts, mux state transition errors, and `nr_sessions` consistency. Test signals: open/close state machine, device-specific mux protocol allocation sizes, flow-control restart thresholds, deinit with active channel, and invalid session IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux.h -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux.h

Purpose: declares the IOSM IP mux protocol model, command IDs, session state, aggregation data structures, and mux lifecycle APIs.

Important types/APIs: `mux_event`, `mux_state`, `ipc_mux_protocol`, `ipc_mux_ul_flow`, command parameter structs, `mux_session`, `mux_adb`, `mux_acb`, `iosm_mux`, `ipc_mux_config`, and exported APIs `ipc_mux_init/deinit`, `ipc_mux_open_session`, `ipc_mux_close_session`, `ipc_mux_get_max_sessions`, `ipc_mux_get_active_protocol`, and `ipc_mux_check_n_restart_tx`.

Control flow role: upper WWAN open/close calls map to mux session events; imem DL processing sends IP SKBs to mux decode; imem UL processing calls mux encode and completion recycling. The header encodes limits such as 8 sessions, ADB sizes, Lite/aggregation TD counts, and command numbers.

State/dependencies: state is in-memory and per-device; packet data is carried in SKB queues and DMA-backed ADB buffers. Dependencies include protocol/imem/WWAN/PCIe types and mux codec structs. Risks include `__packed` on the large `iosm_mux` object, array sizing for per-session datagram tables, command ABI drift, and flow-control counters going stale. Test signals: struct size/layout build checks, max-session boundary tests, command ID compatibility, and queue/flow-control behavior across MUX Lite and aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux_codec.c -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux_codec.c

Purpose: encodes and decodes IOSM MUX Lite and aggregation wire formats. It sends mux commands, decodes command responses/flow-control/link-status tables, decodes DL datagrams, encodes UL datagrams into ADGH or ADBH/ADTH/QLTH blocks, manages UL credits/pending bytes, and recycles mux SKBs after CP consumes TDs.

Important functions: `ipc_mux_dl_decode`, `ipc_mux_dl_acb_send_cmds`, `ipc_mux_netif_tx_flowctrl`, `ipc_mux_ul_trigger_encode`, `ipc_mux_ul_data_encode`, `ipc_mux_ul_encoded_process`, `ipc_mux_ul_adb_finish`, and `ipc_mux_ul_adb_update_ql`.

Control flow: netdev TX queues SKBs into a session and schedules task-queue encode. Encoder round-robins sessions, respects flow masks, queue thresholds, byte watermarks, and credit limits, then queues mux SKBs on the IPC channel and starts TD update timers. DL decode switches on signatures for ADBH, ADGH, FCTH, ACBH, and CMDH, forwarding cloned packet payloads to WWAN or replying to commands. Blocking command sends wait on channel completion.

State/dependencies: uses `iosm_mux` sessions, transaction IDs, ACB/ADB scratch state, DMA SKB free lists, imem UL write/timers, task queue, WWAN RX/TX flow control, nospec bounds hardening, and PCIe SKB free. Risks: packet offset/length validation gaps, session index plus `wwan_q_offset` handling, underflow of pending bytes, flow-control deadlock, and blocking waits. Test signals: signature fuzzing, invalid if_id, FCT credit update, flow-control enable/disable ACKs, high/low watermark TX stop/restart, ADB size overflow, and SKB ownership on encode failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux_codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux_codec.h -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux_codec.h

Purpose: defines mux codec wire headers, signatures, queue/flow-control thresholds, command timeout, and codec function prototypes used by mux and imem.

Important types/APIs: `mux_cmdh`, `mux_acbh`, `mux_adbh`, `mux_adth`, `mux_adgh`, `mux_lite_cmdh`, `ipc_mem_lite_gen_tbl`, `mux_type_cmdh`, `mux_type_header`, and functions for DL decode, ACB command send, netif flow control, UL trigger/encode/completion, ADB finish, and queue-level update.

Control flow role: the header separates mux session management from byte-level codec layout. MUX Lite uses `mux_lite_cmdh`, ADGH, generic QL/FCT tables; aggregation uses ACBH/CMDH and ADBH/ADTH/QLTH. Constants define when TX should stop or resume and how long open/close commands may block.

State/dependencies: no persistent state here; structs overlay SKB data and must match firmware byte layout. Dependencies include `iosm_ipc_mux.h` for session and command parameter types. Risks: ABI signatures and `offsetof`-based variable headers must stay aligned with CP; duplicate buffer-size constants with mux.h invite drift; threshold tuning affects throughput and backpressure. Test signals: layout/size assertions, encode/decode round trips, command timeout path, and boundary cases around queue-level and flow-credit tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux_codec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pcie.c -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pcie.c

Purpose: implements the IOSM PCI driver: probe/remove, BAR mapping, MSI setup, DMA helpers, ASPM/BIOS sleep policy, suspend/resume callbacks, hibernation unregister/re-register, and module registration.

Important functions: `ipc_pcie_probe`, `ipc_pcie_remove`, resource request/release helpers, `ipc_pcie_config_aspm`, `ipc_pcie_check_aspm_enabled`, `ipc_pcie_check_data_link_active`, `ipc_pcie_suspend/resume`, SKB/DMA helpers `ipc_pcie_addr_map/unmap`, `ipc_pcie_alloc_skb`, `ipc_pcie_alloc_local_skb`, `ipc_pcie_kfree_skb`, and module init/exit.

Control flow: probe allocates `iosm_pcie`, enables PCI, sets 64-bit DMA mask, reads ACPI WWAN RTD3 policy, maps BAR0 doorbells and BAR2 scratchpad, acquires MSI, and initializes imem. Remove cleans imem first, then IRQ/BAR/PCI resources. Suspend chooses force-sleep s2idle or host-sleep D3L2 path based on BIOS policy; resume reverses it. Hibernation unregisters the PCI driver around restore.

State/dependencies: `iosm_pcie` stores PCI device, BAR pointers, doorbell offsets, suspend bit, and RTD3 mode. Dependencies include PCI, ACPI DSM, PM notifier, rtnetlink include, local IRQ/imem/protocol, DMA mapping, and SKB allocation. Risks: unwind ordering, DMA mapping lifetime in SKB cb, ACPI object type assumptions, ASPM only logged not changed, and hibernation registration races. Test signals: probe failure injection at each step, DMA map error, remove after partial init, suspend/resume modes, hibernation notifier, and supported PCI IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pcie.h -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pcie.h

Purpose: declares IOSM PCIe constants, `iosm_pcie` device state, SKB DMA control-block metadata, UL operation types, and exported PCIe/DMA/PM helper APIs.

Important types/APIs: device IDs for Intel 7560/7360, BAR/doorbell register constants, MSI/vector counts, `ipc_pcie_sleep_state`, `iosm_pcie`, `ipc_skb_cb`, `ipc_ul_usr_op`, DMA map/unmap, SKB alloc/free helpers, data-link-active check, suspend/resume, ASPM checks, and ASPM config.

Control flow role: upper layers use `IPC_CB(skb)` from imem.h to store DMA mapping, direction, length, and operation type so UL completion can either unblock writers, recycle mux ADBs, or free ordinary SKBs. PM/protocol layers use doorbell constants through IRQ/PM wrappers.

State/dependencies: persistent state exists only in the per-device `iosm_pcie`; SKB metadata persists until SKB completion/free. Dependencies include Linux PCI/device/SKB APIs and the IRQ header. Risks: SKB cb size collision with other users, doorbell bit constants matching hardware, single MSI vector assumption, and PM state bit misuse. Test signals: compile-time `BUILD_BUG_ON` in users, DMA map/unmap pairing, SKB headroom behavior, data link checks on missing root port, and suspend bit interaction with IRQ handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pcie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pm.c -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pm.c

Purpose: implements IOSM protocol power management for host sleep, device sleep notifications, link wake/sleep handshakes, pending HPDA doorbells, and s2idle state forcing.

Important functions: `ipc_pm_init`, `ipc_pm_deinit`, `ipc_pm_signal_hpda_doorbell`, `ipc_pm_trigger`, `ipc_pm_wait_for_device_active`, `ipc_pm_prepare_host_sleep`, `ipc_pm_prepare_host_active`, `ipc_pm_set_s2idle_sleep`, and `ipc_pm_dev_slp_notification`.

Control flow: HPDA doorbell requests are gated by host PM state and link readiness; if link wake is needed or host sleep disallows update, `pending_hpda_update` is set. Device sleep notifications update CP/AP states and may fire sleep-control doorbells. Host suspend prepares sleep, wakes device if needed, waits for active, then sends host sleep through protocol. Resume prepares active and sends exit sleep. When link wakes, pending host-sleep completions and pending HPDA updates are replayed.

State/dependencies: `iosm_pm` tracks host PM state, AP/CP device PM states, condition bitfield, last device sleep notification, completion, pending bit, and PCIe/device pointers. Dependencies include protocol/imem for doorbells and completions. Risks include state-machine desynchronization, pending HPDA starvation, timeouts in active wait, and no explicit locking around PM fields in IRQ/task contexts. Test signals: state transition matrix, pending HPDA replay, active wait timeout, duplicate sleep notifications, s2idle force sleep/active, and suspend/resume failure restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pm.h -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pm.h

Purpose: declares the IOSM PM state machines and public PM operations. It also provides macros that map sleep-control and HPDA updates to doorbell writes.

Important types/APIs: `ipc_pm_cond`, `ipc_mem_host_pm_state`, `ipc_mem_dev_pm_state`, `iosm_pm`, `ipc_pm_unit`, and prototypes for init/deinit, device sleep notification, s2idle update, host sleep/active preparation, active wait, HPDA signaling, and PM trigger. Macros `ipc_cp_irq_sleep_control` and `ipc_cp_irq_hpda_update` centralize doorbell IDs/data.

Control flow role: protocol suspend/resume and runtime HP updates use these APIs to avoid sending head-pointer updates while host or device sleep state makes the link unavailable. State is volatile per protocol instance, with a completion used for active-state waits.

Dependencies: requires `ipc_doorbell_fire`, `IPC_DOORBELL_IRQ_SLEEP`, `IPC_DOORBELL_IRQ_HPDA`, and IOSM PM constants from protocol/imem context. Risks: include-order reliance, bitfield condition races, stale `pending_hpda_update`, and CP/AP state mismatch. Test signals: enum-to-wire values for sleep doorbells, PM unit condition transitions, compile coverage from protocol.c, and suspend/resume sequencing with mocked CP notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_port.c -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_port.c

Purpose: bridges IOSM control channels into the Linux WWAN port subsystem for AT/MBIM/RPC-style control communication.

Important functions: `ipc_port_init`, `ipc_port_deinit`, and WWAN port ops `ipc_port_ctrl_start`, `ipc_port_ctrl_stop`, `ipc_port_ctrl_tx`. The ops open/close imem control channels and route TX SKBs through `ipc_imem_sys_cdev_write`.

Control flow: runtime worker calls `ipc_port_init` for each configured control channel with a non-unknown WWAN port type. WWAN core calls `.start`, which opens a control channel using the configured channel ID and HP update identifier; `.tx` writes SKBs to CP; `.stop` closes the channel. Deinit removes all created WWAN ports and frees the per-port structures.

State/dependencies: `iosm_cdev` stores WWAN port pointer, imem, PCIe, device, port type, channel, and channel ID. Dependencies include channel config, imem ops, WWAN framework, and SKB ownership conventions. Risks: `wwan_create_port` result is not checked before returning the allocated wrapper, stop assumes a valid channel, and deinit iterates a fixed max-channel array. Test signals: port creation failure handling, open refused outside RUN phase, TX failure SKB ownership, close with pending TDs, and device-specific skipped port types from the imem runtime worker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_port.h -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_port.h

Purpose: declares the IOSM WWAN control-port wrapper and lifecycle APIs.

Important types/APIs: `struct iosm_cdev` holds the Linux `wwan_port`, imem, device, PCIe object, WWAN port type, active IPC channel, and configured channel ID. APIs are `ipc_port_init` and `ipc_port_deinit`.

Control flow role: imem runtime setup creates one `iosm_cdev` per supported configured control channel. The implementation registers WWAN port operations that call imem ops for open, close, and TX. State persists only while the modem is fully functional and is cleaned when imem clears `FULLY_FUNCTIONAL`.

Dependencies: includes Linux WWAN APIs and imem ops, which provide channel and protocol access. Risks: header-level circular include pressure through imem_ops, channel lifetime tied to WWAN callbacks, and port arrays limited by `IPC_MEM_MAX_CHANNELS`. Test signals: build coverage with all configured WWAN port types, init/deinit balance, stop after failed start, and channel pointer validity during modem crash/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol.c -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol.c

Purpose: owns protocol shared-memory allocation, message send/wait orchestration, PM wrappers, and AP context-info publication to CP.

Important functions: `ipc_protocol_init`, `ipc_protocol_deinit`, `ipc_protocol_tq_msg_send`, `ipc_protocol_msg_send`, `ipc_protocol_doorbell_trigger`, `ipc_protocol_pm_dev_sleep_handle`, `ipc_protocol_suspend`, `ipc_protocol_resume`, and `ipc_protocol_s2idle_sleep`.

Control flow: init allocates coherent AP shared memory containing context info, device info, head/tail arrays, and message ring; fills physical addresses into the context info; writes context address to MMIO; and initializes PM. Blocking message send schedules preparation in the IPC task queue, stores a response completion in `rsp_ring`, triggers message HP update, and waits with boot/run timeout. On timeout it removes the response pointer and sends modem-timeout uevent. Suspend/resume perform PM state preparation and send host sleep messages.

State/dependencies: `iosm_protocol` stores coherent shared-memory pointer/physical address, PM state, PCIe/imem/device, response ring, and old message tail. Dependencies include protocol_ops for message/TD details, task queue, imem, MMIO, PM, uevents, and DMA coherent allocation. Risks: response pointer lifetime after timeout, task-queue synchronous semantics, DMA allocation/free balance, and PM/message deadlocks. Test signals: message success/error/timeout, response-ring cleanup, boot vs run timeout selection, coherent memory fields, suspend/resume failures, and deinit while waiters exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol.h -->
## sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol.h

Purpose: declares the IOSM protocol shared-memory layout, doorbell IDs, IRQ vector assignments, message-ring size/timeouts, protocol object, task-queue message arguments, and public protocol APIs.

Important types/APIs: `ipc_protocol_context_info`, `ipc_protocol_device_info`, `ipc_protocol_ap_shm`, `iosm_protocol`, `ipc_call_msg_send_args`, and functions for task-queue message send, blocking message send, PM suspend/resume/s2idle/device-sleep handling, doorbell triggering, sleep notification string, init, and deinit.

Control flow role: imem and protocol_ops use the shared-memory layout for CP-visible descriptors: head/tail arrays for pipes, message ring, device info, and context info physical addresses. Doorbell constants identify HPDA, IPC state, and sleep-control interrupts. Blocking message timeouts define failure detection for boot and runtime.

State/dependencies: protocol state persists for the device lifetime and owns DMA-coherent AP shared memory plus PM state. Dependencies include imem, PM, and protocol_ops headers; this creates tight layering but keeps the shared ABI central. Risks: CP-visible struct layout drift, one-vector IRQ assumptions, response-ring size coupling to message ring entries, and blocking API use from non-sleepable contexts. Test signals: layout offset verification, timeout behavior, doorbell type coverage, init/deinit allocation balance, and include-cycle compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol.h -->
