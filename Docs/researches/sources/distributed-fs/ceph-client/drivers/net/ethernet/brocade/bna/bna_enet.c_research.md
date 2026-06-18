# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_enet.c

## Purpose
`bna_enet.c` implements the top-level BNA ethernet control plane. It handles ENET firmware responses and AENs, physical port/admin/link state (`ethport`), ENET start/stop/pause/MTU sequencing, IOCETH lifecycle around the common IOC, resource sizing/init/uninit, CAM module init, and hardware stats requests.

## Important APIs, Types, and Functions
- Response handlers: `bna_msgq_rsp_handler()`, `bna_bfi_ethport_*`, `bna_bfi_pause_set_rsp()`, `bna_bfi_attr_get_rsp()`, `bna_bfi_stats_get_rsp()`.
- Mailbox entry: `bna_mbox_handler()`, which routes errors to IOC error handling and mailbox interrupts to IOC mailbox ISR.
- ETHPORT FSM handles stopped, down, up response wait, down response wait, up, and last response wait states.
- ENET FSM handles stopped, pause init wait, started, config wait, config stop wait, child stop wait, and last response wait.
- IOCETH FSM handles stopped, IOC ready wait, ENET attribute wait, ready, ENET stop wait, IOC disable wait, last response wait, and failed.
- Public APIs implemented here include `bna_res_req()`, `bna_mod_res_req()`, `bna_init()`, `bna_mod_init()`, `bna_uninit()`, `bna_enet_enable()`, `bna_enet_disable()`, `bna_enet_pause_config()`, `bna_enet_mtu_set()`, `bna_ioceth_enable()`, `bna_ioceth_disable()`, `bna_hw_stats_get()`, and CAM handle helpers.

## Control Flow and State
Firmware responses arrive through MSGQ class `BFI_MC_ENET` and are dispatched by `msg_id`. Queue config responses are routed by `enet_id` to active TX/RX objects. RXF configuration and MAC/VLAN/RSS responses go to RXF handlers. Port admin/loopback responses drive the ETHPORT FSM. Pause responses drive ENET. Attribute responses populate `ioceth->attr` once and then advance IOCETH to ready. Link, port enable/disable, and bandwidth AENs update link, ETHPORT readiness, and TX bandwidth state.

ETHPORT readiness combines admin-up, RX-started, and firmware port-enabled flags for regular mode; loopback mode reverses the port-enabled condition. RX start/stop callbacks maintain `rx_started_count` and trigger port up/down transitions when the first RX starts or last RX stops.

ENET start first sends pause configuration. After firmware responds and no newer pause config is pending, it starts ethport, TX module, and RX module. Pause changes while started send a pause request. MTU changes stop RX, then restart RX and complete the MTU callback. Stop waits for ethport/TX/RX children through `bfa_wc`.

IOCETH enable calls `bfa_nw_ioc_enable()`, enables mailbox interrupts on IOC reset, waits for IOC ready, posts ENET attribute get, starts ENET/stats when ready, and calls BNAD ready. Disable stops ENET/stats, disables IOC, disables mailbox interrupts, and calls BNAD disabled. IOC failure disables mailbox interrupts, fails ENET/stats, and reports BNAD failure.

## State and Persistence Behavior
State lives in `struct bna` subobjects: flags, FSM states, pause config, MTU, callbacks, link status, RX-start count, IOC attributes, stats busy flags, RID masks, resource arrays, CAM free/delete queues, and DMA stats buffers. Firmware and hardware state is changed through MSGQ commands for pause, port admin, loopback, attributes, stats, and through IOC enable/disable.

## Dependencies and Integration Points
This file depends on `bna.h`, which brings in BFI ENET ABI, IOC APIs, types, and prototypes for TX/RX modules. It attaches CEE, flash, and MSGQ in `bna_ioceth_init()`, registers ENET response handling with MSGQ, and calls BNAD callbacks for link, IOC ready/failed/disabled, mailbox interrupt enable/disable, and stats completion. It also relies on `bna_hw_defs.h` macros through `bna.h`/types for interrupt register setup.

## Risks
- FSMs are strict; unexpected asynchronous event ordering calls `bfa_sm_fault()`.
- Attribute query is only stored once unless BNAD overrides values; stale default attributes before firmware query limit module resource sizing.
- Stats get is single-flight and copies selected RXF/TXF stats densely according to masks; mismatched firmware packing or RID masks corrupts stats mapping.
- Soft cleanup paths immediately invoke callbacks without hardware teardown.
- Link callbacks occur directly on AEN handling; ordering with port disable and RX stop must be correct to avoid false carrier state.
- Child stop waits depend on each child callback calling `bfa_wc_down()`.

## Test Signals
Signals include IOC enable to BNAD ready, ENET enable start of ethport/TX/RX, pause reconfiguration while starting and started, MTU change stopping/restarting RX, regular and loopback port up/down behavior, link AEN callback correctness, IOC failure and reset recovery, hard and soft disable behavior, stats busy/fail/success returns, CAM free/delete queue allocation, and response routing by `enet_id`.
