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
