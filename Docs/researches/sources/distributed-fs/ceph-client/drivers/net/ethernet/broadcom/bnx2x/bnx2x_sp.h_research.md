# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sp.h

## Purpose

`bnx2x_sp.h` is the public contract for the bnx2x slow-path verbs implemented in `bnx2x_sp.c`. It declares command flags, state enums, parameter blocks, operation objects, callback tables, credit-pool structures, and exported initialization/configuration entry points used by the rest of the driver. The header is not just prototypes; it defines the object model that lets higher-level driver code configure filters, multicast, RSS, queues, and functions without embedding chip-specific ramrod construction logic.

The header's scope is slow-path device control rather than packet datapath. It describes how asynchronous firmware commands are represented, how pending state is tracked, what software registry mirrors exist, and which fields higher layers must fill before calling the slow-path API.

## Important Types, Flags, and APIs

The general ramrod flag enum defines cross-object command behavior: `RAMROD_TX`, `RAMROD_RX`, `RAMROD_COMP_WAIT`, `RAMROD_DRV_CLR_ONLY`, `RAMROD_RESTORE`, `RAMROD_EXEC`, `RAMROD_CONT`, and `RAMROD_RETRY`. These flags control direction, synchronous waiting, driver-only cleanup, restore, immediate execution, continuation of queued work, and retry of busy function transitions.

`enum bnx2x_obj_type` identifies RX-only, TX-only, and combined RX/TX objects. The public slow-path state enum supplies bitmap indices for pending filter, multicast, RSS, AFEX, FCoE/iSCSI, and VIF-list acknowledgement states. `struct bnx2x_raw_obj` is the common base object: it stores function/client/CID identity, the DMA ramrod buffer and mapping, the pending-state bit and bitmap pointer, object type, and callbacks to wait/check/set/clear pending.

The VLAN/MAC section defines the payload unions for MAC, VLAN, and VLAN-MAC rules, the command enum (`ADD`, `DEL`, `MOVE`), `struct bnx2x_vlan_mac_data`, and the generic execution queue types. `struct bnx2x_exeq_elem` wraps one pending command with a command length; `struct bnx2x_exe_queue_obj` owns the executable and completion-pending lists, a lock, a maximum chunk length, and callback hooks for validate/remove/optimize/execute/get. `struct bnx2x_vlan_mac_registry_elem` is the software mirror of configured classification entries, including CAM offset and flags needed for delete/restore. `struct bnx2x_vlan_mac_obj` embeds `bnx2x_raw_obj`, a registry head, a custom reader/writer coordination state, an execution queue, MAC/VLAN credit-pool pointers, ramrod command id, and callback hooks for rule copying, duplicate checks, credit management, rule encoding, delete-all, restore, completion, and wait.

The receive-mode section defines accept flags such as unicast, multicast, all-unicast, all-multicast, broadcast, unmatched, and any-VLAN. `struct bnx2x_rx_mode_ramrod_params` carries the target object, state bitmap, client/CID/function ids, command flags, special FCoE/iSCSI flags, DMA buffer, and Rx/Tx accept masks. `struct bnx2x_rx_mode_obj` is a small operation table with `config_rx_mode` and `wait_comp`.

The multicast section defines linked-list input elements, multicast command data, `struct bnx2x_mcast_ramrod_params`, `enum bnx2x_mcast_cmd`, and `struct bnx2x_mcast_obj`. The object stores either an approximate 256-bin bit vector with a bin count or an exact-match list with a MAC count, plus pending-command state, scheduled state bit, maximum command length, total pending count, engine id, and callbacks for configuration, restore handling, enqueueing, rule writing, pending/scheduled checks, wait, validation, revert, and registry-size access.

`struct bnx2x_credit_pool_obj` defines the CAM/filter credit allocator: an atomic credit count, pool size, bit-vector mirror, base offset, and get/put/check plus get-entry/put-entry callbacks. The RSS section defines `struct bnx2x_config_rss_params` and `struct bnx2x_rss_config_obj`, including RSS mode/capability flags, result mask, indirection table, Toeplitz key, optional TOE bitmap, engine id, cached indirection table, and UDP RSS flags.

The queue section defines update flags, queue states, logical states, queue commands, setup/init flags, queue type flags, constants for multi-CoS CID layout, and all queue command parameter blocks. `struct bnx2x_queue_state_params` selects a command and supplies the matching union member. `struct bnx2x_queue_sp_obj` stores CIDs, client/function identity, CoS counts, current/next state, type flags, pending bits, the DMA ramrod buffer, and callbacks for sending, pending-bit selection, transition validation, completion, and waiting.

The function section defines update flags, function states, function commands, command parameter blocks for HW init/reset, function start, switch update, AFEX update/vif lists, traffic start, and timesync. `struct bnx2x_func_sp_drv_ops` is the driver-provided hardware/firmware lifecycle interface used by the function state object. `struct bnx2x_func_sp_obj` stores state, pending bits, normal and AFEX ramrod buffers, `one_pending_mutex`, the driver ops pointer, and callbacks for send/check/complete/wait.

Exported entry points include object initializers (`bnx2x_init_func_obj()`, `bnx2x_init_queue_obj()`, `bnx2x_init_mac_obj()`, `bnx2x_init_vlan_obj()`, `bnx2x_init_vlan_mac_obj()`, `bnx2x_init_rx_mode_obj()`, `bnx2x_init_mcast_obj()`, `bnx2x_init_rss_config_obj()`, credit-pool initializers), state/config functions (`bnx2x_func_state_change()`, `bnx2x_queue_state_change()`, `bnx2x_config_vlan_mac()`, `bnx2x_config_rx_mode()`, `bnx2x_config_mcast()`, `bnx2x_config_rss()`), and query helpers (`bnx2x_func_get_state()`, `bnx2x_get_q_logical_state()`, `bnx2x_get_rss_ind_table()`).

## Control Flow Implied by the Header

The header implies a two-phase use pattern. During device initialization, callers allocate DMA command buffers and instantiate slow-path objects with IDs, CIDs, state-bit locations, credit pools, and driver callbacks. The implementation fills the callback slots based on chip family. During runtime, callers create a command-specific parameter struct, set ramrod flags, choose a command enum or accept/update flags, and call the matching config/state-change function.

Asynchronous operations return positive values while pending bits remain set; synchronous callers set `RAMROD_COMP_WAIT` and expect the implementation to block until the relevant bit clears. Restore and cleanup paths reuse the same parameter objects with `RAMROD_RESTORE` or `RAMROD_DRV_CLR_ONLY` so the software registry can be replayed or cleared without inventing separate APIs.

The queue and function objects are state machines. The caller supplies a current command in `bnx2x_queue_state_params` or `bnx2x_func_state_params`; the object checks whether the current state allows it, records a next state, sends the appropriate command or completes a driver-only transition, and later completes when firmware reports the pending command. Logical state queries abstract the detailed queue states into active/stopped for users that do not need the full lifecycle.

## State and Persistence Behavior

All persistence described by the header is in-memory driver state. `pstate` bitmaps outlive individual calls and are shared by raw objects, multicast scheduled state, and public filter/RSS state bits. VLAN/MAC objects persist configured rules in `head`, multicast objects persist exact or approximate registries, RSS objects persist the last indirection table, queue objects persist queue lifecycle and multi-CoS counts, function objects persist function lifecycle state, and credit pools persist the currently available CAM/filter credit.

The structures are built around asynchronous firmware ownership. DMA buffers (`rdata`, `afex_rdata`) must remain valid until command completion. The function object has a separate AFEX buffer because AFEX ramrods may be issued in parallel with other function ramrods. The command flags make state recovery explicit: driver-only cleanup mutates local state without firmware submission, while restore repopulates firmware from the registry mirrors.

## Dependencies and Integration Points

This header depends on kernel types such as `struct list_head`, `spinlock_t`, `atomic_t`, `dma_addr_t`, `mutex`, fixed-width integer types, and Ethernet constants like `ETH_ALEN`. It also depends on bnx2x hardware/firmware constants and HSI sizes declared elsewhere, including `MAX_MAC_CREDIT_E2`, `T_ETH_INDIRECTION_TABLE_SIZE`, `MAX_VLAN_PRIORITIES`, `MAX_TRAFFIC_TYPES`, `NIG_REG_LLH1_FUNC_MEM_SIZE`, VF credit constants, and firmware structures referenced by implementation buffers.

The header is included by `bnx2x_sp.c` and by higher-level bnx2x driver code that needs to initialize slow-path objects or issue slow-path commands. It integrates with event-ring completion handling through the completion callback signatures, with firmware ramrod posting through the state/config entry points, with MCP load/unload phases through function init/reset parameters, with netdevice filter configuration through VLAN/MAC/multicast/rx-mode APIs, with SR-IOV through VF-aware credit macros, and with DCB/tunneling/timesync/AFEX feature code through function and queue command parameter blocks.

## Risks and Edge Cases

The header exposes several contracts that must be used precisely. Command flags are bit positions in `unsigned long`; callers must pass pointers consistently and avoid mixing per-command flags with general ramrod flags. Many structs contain unions selected by a command enum; using the wrong union member will silently build invalid firmware data. The queue and function objects implement one-pending semantics, so callers must respect positive pending returns or use `RAMROD_COMP_WAIT`/`RAMROD_RETRY` only from sleepable contexts.

The object callbacks are function pointers initialized by `bnx2x_sp.c`; using an object before initialization or with chip-incompatible parameters can produce NULL callbacks or intentional `BUG()` paths in the implementation. `rdata` buffers are typed differently depending on command and chip generation, so the caller must provide buffers large enough for the largest command the object can issue. Credit-pool macros rely on valid function counts and VF counts; invalid counts intentionally produce zero-credit pools that block filter operations.

The header declares `bnx2x_vlan_mac_h_write_lock()` and `bnx2x_vlan_mac_move()`, but this source file's visible implementation centers on internal trylock/move handling through `bnx2x_config_vlan_mac()` and object callbacks. Callers and maintainers should verify whether those declarations are implemented elsewhere, conditionally compiled, or stale before introducing new users.

## Test Signals

Compile-time signals include all users agreeing on struct definitions, enum values, and function prototypes across `bnx2x_sp.c` and the rest of the driver. Runtime signals include correct pending-bit transitions, successful synchronous and asynchronous returns, valid object callback initialization for E1/E1H/E2+, and stable state/registry mirrors after reset/restore.

Targeted tests should exercise each public API declared here: initialize all object types, issue legal and illegal queue/function transitions, add/delete/move VLAN/MAC filters, delete-all and restore filters by flags, configure rx mode combinations, configure multicast ADD/DEL/SET/RESTORE/CONT on chip-specific paths, exhaust and refill credit pools, update RSS flags/key/table and read the cached table back, and run driver-only cleanup. Negative tests should cover invalid MACs, duplicate filters, absent deletes, invalid CID indices, unsupported multicast SET on E1/E1H, illegal function/queue states, zero function-count credit sizing, and timeout behavior when pending bits are not cleared.
