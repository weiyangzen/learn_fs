# Research: subset-b-004602

Grouped research for QED hardware, initialization, interrupt, firmware-offset, and iSCSI offload sources. Each section preserves its source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_hw.c

## Purpose
`qed_hw.c` is the low-level hardware access layer for the QLogic/Marvell QED driver. It manages PTT BAR windows, register reads and writes, pretend addressing for PF/VF/port access, DMAE command execution, DMAE resource lifetime, hardware error notification, and a DMAE self-test path.

## Important APIs, Types, and Functions
- `struct qed_ptt` tracks a PTT list node, external BAR window index, cached PXP entry, and owning hwfn id.
- `struct qed_ptt_pool` owns the free PTT list and a spinlock-protected array of external BAR windows.
- `qed_ptt_pool_alloc()` and `qed_ptt_pool_free()` allocate/free PTT state, reserving indices below `RESERVED_PTT_MAX`.
- `qed_ptt_acquire_context()` polls for a free PTT using `udelay()` in atomic context or `usleep_range()` otherwise; `qed_ptt_release()` returns it to the free list.
- `qed_wr()`, `qed_rd()`, `qed_memcpy_from()`, and `qed_memcpy_to()` are the core GRC/BAR access helpers.
- `qed_fid_pretend()`, `qed_port_pretend()`, `qed_port_unpretend()`, and `qed_port_fid_pretend()` program the PXP pretend fields in a PTT entry.
- `qed_dmae_info_alloc()` and `qed_dmae_info_free()` allocate coherent completion, command, and intermediate DMA buffers.
- `qed_dmae_host2grc()`, `qed_dmae_grc2host()`, and `qed_dmae_host2host()` serialize DMAE transfers through `p_hwfn->dmae_info.mutex`.
- `qed_hw_err_notify()` reports hardware errors to recovery logic and management firmware debug data.
- `qed_dmae_sanity()` tests host-to-host DMAE correctness with a known memory pattern.

## Control Flow
Register access flows through `qed_set_ptt()`: the helper checks whether the requested GRC address is within the cached BAR window, retargets the window with `qed_ptt_set_win()` when needed, and returns the BAR-relative address for `REG_RD/REG_WR`. Block copies iterate in chunks no larger than one PXP external BAR window; PFs retarget the PTT for each chunk, while VFs use the supplied address directly.

DMAE operations build an opcode in `qed_dmae_opcode()`, populate command memory with source/destination addresses in `qed_dmae_execute_sub_operation()`, post command words to `DMAE_REG_CMD_MEM`, trigger the per-channel go register, and poll the coherent completion word. Large transfers split at `DMAE_MAX_RW_SIZE`; virtual host buffers are copied through the coherent intermediate buffer.

## State and Persistence
Persistent driver state lives under `p_hwfn`: PTT pool allocation, cached PTT PXP offsets/pretend fields, DMAE coherent buffers, completion word, intermediate buffer, and selected DMAE channel. Hardware-visible state includes PXP window mappings, PXP pretend command fields, DMAE command memory, DMAE go registers, and error/recovery notifications. No disk persistence is involved.

## Dependencies and Integration Points
This file depends on Linux MMIO, DMA mapping, spinlocks, mutexes, PCI device state, QED register definitions, HSI structures, SR-IOV helpers, and management firmware hooks. It is used broadly by initialization, interrupts, context setup, storage offloads, SPQ, debug, and L2 paths that need direct register or internal RAM access.

## Risks
- PTT misuse across hwfns is detected only by logging; a wrong PTT can target the wrong BAR window.
- DMAE waits are bounded but busy-poll with `udelay()` and can return `-EBUSY` on device or firmware failure.
- `qed_dmae_execute_sub_operation()` ignores the return value from `qed_dmae_post_command()`, so invalid command detection depends on later wait behavior in normal paths.
- Virtual host DMAE paths use an intermediate buffer protected by one mutex; callers must not bypass that serialization.
- Pretend state persists in the PTT until overwritten, so callers must intentionally restore/replace function or port identity.

## Test Signals
Useful validation includes successful `qed_dmae_sanity()` during init callbacks, no PTT acquire timeouts under stress, register read/write traces in `NETIF_MSG_HW`, absence of DMAE timeout notices, correct SR-IOV pretend behavior, and hardware recovery events from `qed_hw_err_notify()` when DMAE or attention paths fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_hw.h

## Purpose
`qed_hw.h` declares the public internal interface for QED hardware access. It exposes opaque PTT handling, BAR/GRC accessors, pretend operations, DMAE utilities, firmware data initialization, queue-manager PQ parameter shapes, and hardware error notification.

## Important APIs, Types, and Functions
- `enum reserved_ptts` defines reserved PTT slots for engineering diagnostics, user space, main, and DPC use.
- DMAE command constants define go value, completion value, command size, minimum wait time, and max clients.
- PTT APIs include pool allocation/free, window address accessors, window retargeting, reserved PTT lookup, and raw read/write/copy helpers.
- Pretend APIs switch access identity for function and/or port.
- `union qed_qm_pq_params` supplies protocol-specific PQ parameter variants for iSCSI, core, Ethernet, and RoCE.
- DMAE APIs allocate/free DMAE info, map DMAE indices to go commands, run a sanity copy, and initialize firmware data.
- `qed_hw_err_notify()` is marked cold and printf-checked.

## Control Flow
The header is consumed by most QED modules that need a PTT and low-level hardware access. Typical call flow is acquire or retrieve a PTT, issue `qed_rd/qed_wr` or DMAE operations, and then release the PTT if dynamically acquired.

## State and Persistence
The header declares interfaces that mutate `struct qed_hwfn` state, PTT window hardware state, DMAE coherent buffers, and management firmware error state. The opaque `struct qed_ptt` prevents most callers from depending on the concrete PTT layout.

## Dependencies and Integration Points
It includes Linux type/bit/slab/string headers and QED core device definitions. `qed_init_ops.c`, `qed_init_fw_funcs.c`, `qed_int.c`, `qed_iscsi.c`, and many other driver files use these declarations for register access, runtime init flushing, CAU/IGU programming, statistics reads, and storage offload ramrods.

## Risks
- The API is low-level and assumes callers use the correct PTT context and locking.
- Function comments contain a few stale return descriptions, so implementation should be treated as authoritative.
- DMAE address-type expectations are not encoded in the function prototypes, leaving room for caller-side unit mistakes around bytes versus dwords.

## Test Signals
Compile coverage is important because this header binds many modules. Runtime signals include successful PTT allocation, DMAE sanity checks, and callers being able to gather stats or initialize runtime registers without GRC/DMAE errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_init_fw_funcs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_init_fw_funcs.c

## Purpose
`qed_init_fw_funcs.c` contains firmware-facing initialization helpers. It prepares queue-manager runtime register values, updates live QM scheduling/rate-limit registers, configures tunnel parser/NIG/PBF/DORQ state, configures GFT search profiles, enables context validation, maps protocol and ramrod ids to strings, sets RDMA assert levels, and manages firmware overlay DMA buffers.

## Important APIs, Types, and Functions
- QM helpers include `qed_qm_pf_mem_size()`, `qed_qm_common_rt_init()`, `qed_qm_pf_rt_init()`, `qed_init_pf_wfq()`, `qed_init_pf_rl()`, `qed_init_vport_wfq()`, `qed_init_vport_tc_wfq()`, `qed_init_global_rl()`, and `qed_send_qm_stop_cmd()`.
- Internal QM routines compute external VOQ ids, PBF command queue line allocation, BTB block allocation, PQ base addresses, TX PQ maps, PF/VPORT WFQ, PF/global/VPORT rate-limit credits, and Other-PQ maps.
- Tunnel APIs include VXLAN/GRE/Geneve destination-port and enable functions plus `qed_set_vxlan_no_l2_enable()`.
- GFT APIs include `qed_gft_config()` and `qed_gft_disable()`.
- Debug string APIs are `qed_get_protocol_type_str()` and `qed_get_ramrod_cmd_id_str()`.
- Overlay APIs are `qed_fw_overlay_mem_alloc()`, `qed_fw_overlay_init_ram()`, and `qed_fw_overlay_mem_free()`.

## Control Flow
Initial hardware load stores runtime values with `STORE_RT_REG` and `OVERWRITE_RT_REG`; later the init-op interpreter flushes those values into hardware. Common QM init enables/disables PF RL, PF WFQ, global RL, and VPORT WFQ; then it computes PBF command lines, BTB blocks, and default global RL entries. PF QM init clears first-TX-PQ ids, maps Other PQs, maps TX PQs to VOQs/PFs/VPORT PQs, initializes WFQ/RL, and writes PQ info directly into XSTORM internal RAM.

Live updates bypass runtime storage and write registers directly with `qed_wr()`. QM stop/release commands poll `QM_REG_SDMCMDREADY`, write SDM command address/data, pulse GO, and poll readiness again. Tunnel changes update parser output format plus NIG/PBF/DORQ registers. GFT config builds one CAM line and one mask RAM line per PF, writes them with direct GRC or DMAE fallback, and enables PRS GFT search.

Overlay allocation parses firmware overlay headers by storm id, allocates coherent memory per storm, copies overlay payloads, and later writes physical addresses into per-storm internal RAM slots for the current PF.

## State and Persistence
State is stored in `p_hwfn->rt_data` until the init interpreter writes it, in `init_qm_vport_params.first_tx_pq_id` as a derived map, in hardware QM/PBF/PRS/NIG/DORQ/GFT/CDU registers, and in coherent overlay memory descriptors. The string tables are static read-only state. No filesystem persistence is used.

## Dependencies and Integration Points
The file depends on HSI constants, IRO offsets, register definitions, DMAE/GRC access from `qed_hw.c`, runtime register storage from `qed_init_ops.h`, and QED device init code. Callers include context setup (`qed_cxt.c`), device initialization and stop paths (`qed_dev.c`), SPQ tunnel updates (`qed_sp_commands.c`), L2 GFT setup (`qed_l2.c`), and SPQ logging.

## Risks
- Many calculations encode hardware-specific queue, VOQ, WFQ, and BTB assumptions; invalid params typically log and return `-1` rather than a specific errno.
- Bounds checks are partial and rely on constants such as `MAX_QM_GLOBAL_RLS`, `MAX_NUM_VOQS`, and queue counts being consistent with firmware tables.
- GFT config logs invalid protocol/profile combinations but continues programming, so caller validation matters.
- Endianness is explicit for wide-bus writes and overlay data; regressions can silently misprogram firmware-visible RAM.
- Overlay parsing stops and frees all allocations on malformed storm id or allocation failure.

## Test Signals
Signals include successful device load with QM runtime init, correct min/max bandwidth and rate-limit behavior, tunnel offload enablement through SPQ commands, expected GFT/RFS steering behavior, SPQ debug logs resolving protocol/ramrod names, and clean overlay allocation/free during device init/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_init_fw_funcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_init_ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_init_ops.c

## Purpose
`qed_init_ops.c` interprets firmware initialization scripts and manages runtime initialization data. It loads firmware binary table pointers, stores runtime register values, writes array/zero/inline/runtime init commands, handles polling/read commands, executes callback ops, initializes global GTT windows, and installs the generated IRO array pointer.

## Important APIs, Types, and Functions
- `qed_init_iro_array()` points `cdev->iro_arr` at the E4 IRO triplet array.
- `qed_init_store_rt_reg()` and `qed_init_store_rt_agg()` stage runtime register values in `p_hwfn->rt_data`.
- `qed_init_alloc()` and `qed_init_free()` allocate/free runtime validity and value arrays for PFs.
- `qed_init_run()` is the top-level init-op interpreter.
- `qed_gtt_init()` writes the static PXP global windows.
- `qed_init_fw_data()` parses firmware binary buffer headers into `cdev->fw_data`.
- Internal helpers handle DMAE/PIO array writes, zero fills, zipped arrays, pattern arrays, runtime segments, polling comparisons, mode trees, phase conditionals, and DMAE-ready callbacks.

## Control Flow
The firmware data setup reads `bin_buffer_hdr` entries and records pointers to version info, init ops, array data, mode tree, and overlays. During `qed_init_run()`, the driver allocates an unzip buffer, walks every init op, and dispatches by opcode. Write commands select inline, zeros, array, or runtime data; array commands may unzip compressed payloads or repeat pattern payloads; runtime commands flush only valid staged segments and invalidate them after writing. Read commands can be simple reads or bounded polls with EQ/AND/OR comparison. IF_MODE and IF_PHASE commands skip forward by encoded command offsets when conditions do not match. The DMAE-ready callback runs `qed_dmae_sanity()` and enables DMAE for the rest of engine phase.

## State and Persistence
Runtime state is held in `p_hwfn->rt_data.init_val` and `p_hwfn->rt_data.b_valid`, plus the temporary `p_hwfn->unzip_buf`. Firmware table pointers are stored in `cdev->fw_data`. GTT global-window configuration persists in hardware registers. Runtime validity bits are cleared as each value is emitted.

## Dependencies and Integration Points
This file uses `qed_hw.c` for register and DMAE access, `qed_init_ops.h` macros for runtime storage, `qed_iro_hsi.h` for IRO offset selection, QED HSI init-op structures, and SR-IOV PF/VF checks. It is central to device bring-up and receives runtime values prepared by `qed_init_fw_funcs.c`, interrupt setup, context setup, and other init code.

## Risks
- Init scripts are firmware-defined; incorrect table offsets or corrupted binary data can drive invalid register writes.
- Zipped array expansion depends on `MAX_ZIPPED_SIZE` and `qed_unzip_data()` returning a nonzero output length.
- `qed_init_cmd_wr()` does not propagate the return from `qed_init_rt()` in the runtime case, so runtime DMAE errors could be lost in that path.
- Poll commands log timeouts but do not fail `qed_init_run()`, which may allow later init steps after a hardware readiness issue.
- Runtime arrays are skipped for VFs, so callers must avoid PF-only runtime staging assumptions in VF flows.

## Test Signals
Look for successful firmware-data parsing, clean init phase completion, no "Failed to unzip dmae data" messages, no poll timeout logs, successful DMAE-ready sanity callback, expected runtime values being invalidated after flush, and successful GTT window reads during later hardware access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_init_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_init_ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_init_ops.h

## Purpose
`qed_init_ops.h` declares the firmware init interpreter and runtime register staging interface used during QED hardware bring-up.

## Important APIs, Types, and Functions
- `qed_init_iro_array()` installs the generated IRO array pointer in `struct qed_dev`.
- `qed_init_run()` runs a selected firmware init phase and mode set through a PTT.
- `qed_init_alloc()` and `qed_init_free()` manage `struct qed_rt_data` arrays.
- `qed_init_store_rt_reg()` and `qed_init_store_rt_agg()` stage scalar and aggregate runtime values.
- `STORE_RT_REG`, `OVERWRITE_RT_REG`, and `STORE_RT_REG_AGG` are the convenience macros used by other modules.
- `qed_gtt_init()` initializes PXP/GTT global windows.

## Control Flow
Callers allocate runtime arrays, store runtime values with the macros, run firmware init phases, and free runtime arrays during teardown. Aggregates are passed by address and stored as u32 words.

## State and Persistence
The declarations affect `p_hwfn->rt_data` and hardware GTT/init state through implementations in `qed_init_ops.c`. The header itself has no state.

## Dependencies and Integration Points
It includes QED core types and is included by firmware helper, interrupt, device, and context code that must stage runtime register values before init-script execution.

## Risks
- `STORE_RT_REG_AGG` casts aggregate storage to `u32 *`; callers must pass naturally sized firmware/register structs with correct endianness.
- `OVERWRITE_RT_REG` is identical to `STORE_RT_REG`, so there is no separate overwrite policy beyond replacing the staged value.

## Test Signals
Compile-time users should match the expected signatures. Runtime signals are successful device init and correct staged values flushed by `qed_init_run()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_init_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_int.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_int.c

## Purpose
`qed_int.c` implements QED interrupt and attention handling. It manages slowpath status blocks, attention status blocks, IGU CAM discovery/reset, CAU status-block configuration and coalescing, slowpath callback dispatch, hardware attention decoding, doorbell overflow recovery, interrupt enable/disable, and status-block debug reads.

## Important APIs, Types, and Functions
- `struct qed_pi_info` stores one slowpath producer-index callback and cookie.
- `struct qed_sb_sp_info` combines a slowpath status block with callback slots.
- `struct aeu_invert_reg_bit` and `aeu_descs` describe AEU attention bits, parity status, callbacks, and debug block ids.
- Specific attention callbacks include MCP CPU, PSWHST incorrect access, GRC timeout, PGLUE RBC, firmware assertion, and DORQ.
- `qed_int_sp_dpc()` is the tasklet for default slowpath SB interrupts and attentions.
- `qed_int_sb_init()`, `qed_int_sb_setup()`, and `qed_int_sb_release()` manage client status blocks.
- `qed_int_register_cb()` and `qed_int_unregister_cb()` manage slowpath callback slots.
- `qed_int_igu_read_cam()` and `qed_int_igu_reset_cam()` discover and reprogram IGU mapping memory.
- `qed_int_igu_enable()`, `qed_int_igu_enable_int()`, and `qed_int_igu_disable_int()` control interrupt generation.
- `qed_int_cau_conf_sb()`, `qed_init_cau_sb_entry()`, and `qed_int_set_timer_res()` configure CAU memory and coalescing.
- `qed_db_rec_handler()` and DORQ helpers recover from PF doorbell overflow/drop conditions.

## Control Flow
During allocation, the driver allocates the slowpath SB and attention SB as coherent memory, initializes IGU addresses, computes parity masks, and sets up the tasklet. Setup zeros SBs, programs CAU/attention SB addresses, and prepares the DPC. Enabling interrupts first enables AEU-to-IGU attentions, requests the slowpath IRQ when appropriate, then programs PF interrupt mode bits for INTA/MSI/MSI-X/POLL.

When the slowpath tasklet runs, it disables default SB interrupts, updates the SB index and attention index, checks for a valid DPC PTT, handles attention changes, dispatches registered producer-index callbacks, acknowledges attentions, and re-enables interrupts. Attention assertion masks sources in IGU, records known bits, handles MCP events, and writes IGU attention-set commands. Deassertion reads all AEU-after-invert registers, handles parity first, then walks enabled non-parity causes per attention group, calls callbacks, prints block debug attention data, escalates fatal errors through `qed_hw_err_notify()`, clears IGU deassertion, unmasks benign sources, and clears known state.

Doorbell overflow recovery flushes incomplete EDPM transactions when needed, clears sticky overflow, and replays registered doorbells through the DB recovery mechanism.

## State and Persistence
Driver state includes `p_hwfn->p_sp_sb`, `p_hwfn->p_sb_attn`, `p_hwfn->sp_dpc`, `b_int_requested`, `b_int_enabled`, IGU block usage counters, callback slots, attention parity masks, known attention bits, and doorbell recovery flags. Hardware state includes IGU PF configuration, attention masks/latches, IGU mapping memory, cleanup status, CAU SB/PI memory, AEU enable registers, DORQ sticky/drop registers, and status-block producer/consumer memory.

## Dependencies and Integration Points
The file depends on Linux tasklets, DMA coherent memory, QED hardware access, runtime init storage, management firmware event handling, slowpath IRQ allocation, SR-IOV/VF helpers, debug attention parsing, and doorbell recovery. It integrates with protocol modules through `qed_int_register_cb()`, with device init through IGU CAM and CAU runtime setup, and with error recovery through hardware error notifications.

## Risks
- Attention descriptor tables must match hardware bit layout; incorrect lengths or flags misdecode parity/interrupt causes.
- Some attention callbacks return fatal status and permanently mask future attentions for that source.
- Slowpath callback registration scans without an explicit lock in this file; callers must sequence registration against DPC execution.
- IGU CAM reset depends on MFW resource counts and SR-IOV VF counts matching available mapping entries.
- Doorbell recovery must flush partial EDPM correctly before replay; failure leaves overflow recovery returning `-EBUSY`.
- `qed_int_alloc()` does not free the slowpath SB if attention SB allocation fails, so caller cleanup must handle partial allocation.

## Test Signals
Signals include successful IGU CAM read/reset logs, correct number of PF/VF SBs, tasklet dispatch of SPQ/protocol callbacks, clean attention ack progression, absence of repeated parity/fatal attention storms, successful doorbell recovery after overflow injection, configurable interrupt coalescing reflected in CAU memory, and valid output from `qed_int_get_sb_dbg()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_int.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_int.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_int.h

## Purpose
`qed_int.h` declares the interrupt, attention, IGU, CAU, status-block, and doorbell recovery interfaces used across the QED driver.

## Important APIs, Types, and Functions
- IGU PF/VF configuration bit macros define function, MSI/MSI-X, INTx, attention, single-ISR, and parent-PF fields.
- `enum igu_ctrl_cmd` and `struct igu_ctrl_reg` describe IGU command register encoding.
- `enum qed_coalescing_fsm` selects RX or TX CAU PI state machines.
- `struct qed_igu_block` describes one IGU mapping entry with validity/free/PF/default flags.
- `struct qed_igu_info` stores all IGU mapping entries, default SB id, usage counters, and PF/VF change allowance.
- Public APIs cover SB init/setup/release, SP DPC, SB counts, post-ISR-release cleanup, attention clear behavior, SB debug, doorbell recovery, IGU CAM reset/read/init, callback registration, CAU SB config, interrupt allocation/setup/free, interrupt enable/disable, timer resolution, and PGLUE attention handling.

## Control Flow
Device init code reads and optionally resets the IGU CAM, allocates interrupt state, initializes runtime IGU registers, sets up default and attention SBs, then enables interrupts in the selected mode. Protocols register slowpath callbacks and get firmware consumer pointers for their PI. Teardown disables interrupts, releases IRQ state, releases status blocks, and frees interrupt memory.

## State and Persistence
The header defines state shapes for IGU resource accounting and status-block ownership. Implementations mutate `p_hwfn->hw_info.p_igu_info`, `qed_sb_info`, CAU memory, IGU mapping memory, and interrupt flags.

## Dependencies and Integration Points
It includes QED core types and is used by device init, slowpath, protocol offloads, SR-IOV, debug, and storage paths. `qed_iscsi.c` uses `qed_get_igu_sb_id()` for queue SB mapping.

## Risks
- Incorrect use of `QED_SP_SB_ID` with release paths is explicitly rejected for PFs.
- IGU mapping memory size is derived from `NUM_OF_SBS(dev)`, so device-specific constants must match hardware.
- Timer resolution changes require initialized hardware and PF context.

## Test Signals
Compile coverage across PF/VF builds, successful SB allocation/release, callback registration and DPC dispatch, correct SB counts, and valid CAU/IGU debug reads are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iro_hsi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iro_hsi.h

## Purpose
`qed_iro_hsi.h` is a generated-style HSI header that enumerates internal RAM offset entries and provides accessor macros for storm RAM/GTT structures. It lets C code compute firmware-memory offsets from `IRO[]` base, size, and multiplier fields installed from `iro_arr`.

## Important APIs, Types, and Functions
- The anonymous enum defines IRO indices for LL2, ETH, iSCSI, FCoE, RDMA/RoCE/iWARP, TOE, overlay buffers, assert levels, integration test data, queue zones, producer/consumer locations, and statistics blocks.
- Macros such as `TSTORM_ISCSI_RX_STATS_OFFSET()`, `MSTORM_SCSI_BDQ_EXT_PROD_GTT_OFFSET()`, `XSTORM_PQ_INFO_OFFSET()`, and `PSTORM_RDMA_QUEUE_STAT_OFFSET()` compute byte offsets from `IRO[index].base + argument * multiplier`.
- Companion `*_SIZE` macros expose the firmware-defined structure size for each IRO entry.
- `E4_IRO_ARR_OFFSET` selects the per-chip offset into the flat IRO array.

## Control Flow
There is no executable control flow. Callers include this header, ensure `IRO` points at the active chip's IRO triplets, and use macros to compute RAM offsets for `qed_memcpy_from()`, `qed_wr()`, DMAE writes, or GTT producer/consumer addresses.

## State and Persistence
The macros read the global/device `IRO` array, which is assigned during init. They do not own memory but are a key contract for firmware-visible RAM layout.

## Dependencies and Integration Points
The header depends on `struct iro`/`IRO` definitions from QED HSI/core headers. It is consumed by init firmware helpers, iSCSI stats and BDQ producer mapping, LL2, Ethernet, RDMA, overlay RAM initialization, and queue-manager PQ info writes.

## Risks
- Any mismatch between enum order and `iro_arr` triplets corrupts all computed firmware offsets.
- Macros do not validate arguments, so invalid PF ids, queue ids, BDQ ids, or stat ids compute invalid offsets.
- Size macros must match the structures copied by callers; stale firmware layout can cause short or overlarge RAM copies.

## Test Signals
Device bring-up, protocol stats reads, BDQ producer updates, overlay address programming, and queue producer/consumer accesses succeeding without GRC timeouts are practical validation. Firmware ABI changes should trigger regenerated enum and array updates together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iro_hsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iscsi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iscsi.c

## Purpose
`qed_iscsi.c` implements the QED iSCSI/TCP offload interface. It manages iSCSI function start/stop ramrods, connection resource allocation and hashing, TCP/iSCSI connection offload/update/termination ramrods, BDQ producer address exposure, async event delivery, firmware statistics collection, and the exported `qed_iscsi_ops` table.

## Important APIs, Types, and Functions
- `struct qed_iscsi_conn` stores connection identity, firmware CIDs, queue chains, DMA buffers, TCP offload state, MAC/IP/port tuples, timers, sequence/window state, iSCSI update fields, physical queues, and abortive disconnect state.
- `qed_sp_iscsi_func_start()` and `qed_sp_iscsi_func_stop()` issue function init/destroy ramrods and register/unregister async callbacks for `PROTOCOLID_TCP_ULP`.
- `qed_sp_iscsi_conn_offload()`, `qed_sp_iscsi_conn_update()`, `qed_sp_iscsi_mac_update()`, `qed_sp_iscsi_conn_terminate()`, and `qed_sp_iscsi_conn_clear_sq()` build SPQ ramrods for connection lifecycle operations.
- `qed_iscsi_allocate_connection()`, `qed_iscsi_acquire_connection()`, `qed_iscsi_release_connection()`, and `qed_iscsi_free_connection()` manage connection memory, chains, CIDs, and the free list.
- Stats helpers read T/M/U/X/Y/P storm iSCSI stats from IRO offsets using `qed_memcpy_from()`.
- Public facade functions implement `start`, `stop`, `acquire_conn`, `release_conn`, `offload_conn`, `update_conn`, `destroy_conn`, `clear_sq`, `get_stats`, and `change_mac`.
- `qed_get_iscsi_ops()` and `qed_put_iscsi_ops()` are exported symbols.

## Control Flow
The upper iSCSI client obtains `qed_iscsi_ops`, fills device info, starts storage, acquires connection handles, offloads connection state, updates or changes MAC as needed, destroys/clears connections, releases handles, and finally stops storage. Start posts an init ramrod, sets `QED_FLAG_STORAGE_STARTED`, initializes the connection hash, and optionally returns TID block information. Acquire allocates a hash node, obtains a TCP_ULP CID, allocates or reuses a connection, zeros DMA/query queues, stores handle/fw CID, hashes it, and returns the doorbell address. Offload copies user-supplied TCP/IP/iSCSI parameters into `qed_iscsi_conn`, selects OFLD and ACK physical queues, writes PBL addresses and TCP state into the ramrod, and posts it synchronously. Destroy posts termination and writes upload/query DMA addresses so firmware can return final TCP state and queue counters.

Stats acquisition gets a PTT in atomic or sleeping mode, reads per-storm stats blocks at `BAR0_MAP_REG_*SDM_RAM + *_ISCSI_*_STATS_OFFSET(rel_pf_id)`, converts little-endian register pairs, and releases the PTT. MCP protocol stats are a reduced translation to rx/tx PDUs and bytes.

## State and Persistence
State is stored in `p_hwfn->p_iscsi_info`, its spinlock and free connection list, each connection's coherent DMA buffers/chains, `cdev->connections` hash table, `QED_FLAG_STORAGE_STARTED`, protocol callback pointers, event context/callback, and firmware state created by SPQ ramrods. No disk persistence is used.

## Dependencies and Integration Points
The file depends on QED context CID allocation, SPQ ramrod infrastructure, LL2 operations, interrupt SB id lookup, QED chain allocation, DMA coherent memory, IRO offsets, hardware register access, SR-IOV/resource macros, and the public Linux `qed_iscsi_if.h` API. It integrates with firmware through TCP_ULP/iSCSI ramrods and with management firmware through `qed_get_protocol_stats_iscsi()`.

## Risks
- Stop refuses to proceed while the connection hash is non-empty; leaked handles block shutdown.
- The free-list reuse path returns an existing connection without reallocating chains, so `qed_iscsi_setup_connection()` must reset all reusable firmware-visible memory.
- Several public operations depend on `QED_FLAG_STORAGE_STARTED`; calling them before start yields lookup failure.
- `qed_iscsi_change_mac()` finds the connection but currently posts the existing `con->remote_mac`; it does not copy the `mac` argument into the connection before issuing the ramrod.
- `qed_iscsi_alloc()` initializes the list but `qed_iscsi_setup()` must be called to initialize the spinlock before concurrent use.
- Offload parameter copying is large and field-by-field; missed endian conversion or duplicate source fields can be hard to detect.

## Test Signals
Validation includes function start/stop ramrod success, async event callback delivery, acquire/offload/update/terminate/release cycles under load, no connection hash leaks on stop, correct doorbell and BDQ producer addresses, iSCSI traffic success for IPv4/IPv6/VLAN paths, stats increasing in the expected storm counters, and targeted testing of MAC update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iscsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iscsi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iscsi.h

## Purpose
`qed_iscsi.h` declares internal iSCSI support state and lifecycle/statistics entry points, with compile-time stubs when `CONFIG_QED_ISCSI` is disabled.

## Important APIs, Types, and Functions
- `struct qed_iscsi_info` stores the connection-resource spinlock, reusable connection free list, max outstanding task count, async event context, and event callback.
- Enabled builds declare `qed_iscsi_alloc()`, `qed_iscsi_setup()`, `qed_iscsi_free()`, and `qed_get_protocol_stats_iscsi()`.
- Disabled builds provide stubs that return `-EINVAL` for allocation and no-op setup/free/stats functions.

## Control Flow
The core driver allocates iSCSI info during feature setup, initializes its lock during setup, frees cached connections during teardown, and asks for protocol stats when management firmware or reporting paths need storage counters. Public iSCSI operations are exported from `qed_iscsi.c`, while this header covers internal core-driver integration.

## State and Persistence
The header defines `p_hwfn->p_iscsi_info` contents: free-list state, locking, event callback state, and task limits. State is memory-resident only.

## Dependencies and Integration Points
It includes Linux list/spinlock/slab types, QED TCP/iSCSI public interfaces, QED chains, core QED state, HSI, MCP, and SPQ headers. It is consumed by core QED setup/teardown and `qed_iscsi.c`.

## Risks
- Callers must handle `-EINVAL` when iSCSI support is not built.
- The spinlock is not initialized by allocation alone; setup sequencing matters.
- `max_num_outstanding_tasks` is declared here but not managed in this header, so implementation/users must keep it consistent with PF params and firmware limits.

## Test Signals
Build both with and without `CONFIG_QED_ISCSI`. Runtime signals include successful allocation/setup/free sequencing, no stale free-list entries after teardown, and valid protocol stats when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iscsi.h -->
