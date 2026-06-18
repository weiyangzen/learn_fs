# Research Group: subset-b-004371

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sp.c

## Purpose

`bnx2x_sp.c` implements most of the bnx2x Ethernet driver's slow-path verbs. It turns driver-level requests for filters, receive mode, multicast state, RSS, queue lifecycle, and function lifecycle into firmware ramrods posted through `bnx2x_sp_post()`, while maintaining software mirrors of pending work and configured state. The file is chip-family aware: E1/E1H paths often use direct Tstorm/NIG/CAM programming or old `ETH_SET_MAC` ramrods, while E2 and newer paths use classification, multicast, filter, RSS, queue, and common-function ramrods with DMA-backed command buffers.

The central design is object based. Public init functions populate operation tables in state objects declared in `bnx2x_sp.h`; public config/state-change functions then call those callbacks. This lets higher driver code work with a uniform `bnx2x_vlan_mac_obj`, `bnx2x_mcast_obj`, `bnx2x_queue_sp_obj`, or `bnx2x_func_sp_obj` while the slow-path implementation selects chip-specific command packing and validation.

## Important APIs, Functions, and Objects

The execution queue helpers at the top of the file (`bnx2x_exe_queue_init()`, `bnx2x_exe_queue_add()`, `bnx2x_exe_queue_step()`, `bnx2x_exe_queue_empty()`) implement a generic bounded command queue used by VLAN/MAC classification. A queue has an `exe_queue` list for work not yet submitted and a `pending_comp` list for the current ramrod chunk. The owner supplies `validate`, `remove`, `optimize`, `execute`, and `get` callbacks. `bnx2x_exe_queue_step()` moves commands into the pending list until the configured `exe_chunk_len` is reached, posts the owner command, and either waits for firmware completion or resets the pending list for driver-only flows.

The raw-object helpers (`bnx2x_raw_check_pending()`, `bnx2x_raw_clear_pending()`, `bnx2x_raw_set_pending()`, `bnx2x_state_wait()`, `bnx2x_raw_wait()`) provide the common pending-bit protocol. They use atomic bit operations plus memory barriers against a shared `pstate` bitmap, and `bnx2x_state_wait()` polls for completion with a timeout, scaling the timeout on emulation hardware and aborting if `bp->panic` is set.

The VLAN/MAC path is exposed through `bnx2x_config_vlan_mac()` and initialized by `bnx2x_init_mac_obj()`, `bnx2x_init_vlan_obj()`, and `bnx2x_init_vlan_mac_obj()`. It supports add, delete, move, delete-all, restore, completion, and wait operations. Important helpers include the validation callbacks (`bnx2x_validate_vlan_mac_add()`, `_del()`, `_move()`), duplicate/existence checks (`bnx2x_check_mac_add()`, `bnx2x_check_vlan_add()`, `bnx2x_check_vlan_mac_add()` and corresponding delete checks), optimization (`bnx2x_optimize_vlan_mac()` cancels queued ADD/DEL pairs), registry management (`bnx2x_vlan_mac_get_registry_elem()`), and command emission (`bnx2x_execute_vlan_mac()`). E2 command builders fill `eth_classify_rules_ramrod_data`; E1/E1H builders fill `mac_configuration_cmd`. The path also updates LLH NIG MAC entries for primary Ethernet and iSCSI L2 MACs in switch-independent/AFEX modes via `bnx2x_set_mac_in_nig()`.

Receive-mode operations are exposed by `bnx2x_config_rx_mode()` and initialized by `bnx2x_init_rx_mode_obj()`. E1x uses `bnx2x_set_rx_mode_e1x()` to update a `tstorm_eth_mac_filter_config` in Tstorm internal memory and complete synchronously. E2 uses `bnx2x_set_rx_mode_e2()` to fill `eth_filter_rules_ramrod_data`, optionally writing separate Rx and Tx/internal-switching rules and extra FCoE queue rules with accept-all flags cleared.

Multicast operations are exposed by `bnx2x_config_mcast()` and initialized by `bnx2x_init_mcast_obj()`. E1 uses exact-match MAC registry lists and `ETH_SET_MAC` ramrods; E1H writes the approximate hash table directly; E2 uses `ETH_MULTICAST_RULES` ramrods over 256 approximate-match bins. The E2 path has a pending-command queue (`bnx2x_pending_mcast_cmd`) that can split large ADD/DEL/RESTORE/SET requests across multiple ramrods and converts SET requests into per-bin add/delete operations once earlier pending commands have been applied. Registry size accounting is handled by chip-specific `validate`, `revert`, `get_registry_size`, and `set_registry_size` callbacks.

Credit pools are implemented by `bnx2x_init_credit_pool()`, `bnx2x_init_mac_credit_pool()`, `bnx2x_init_vlan_credit_pool()`, and helpers for atomic credit accounting and CAM entry allocation. Negative credit means unlimited logical credit; negative base disables explicit CAM entry allocation. MAC and VLAN pool sizing depends on chip generation, emulation, active function count, and VF reservations.

RSS operations are exposed by `bnx2x_config_rss()`, `bnx2x_init_rss_config_obj()`, and `bnx2x_get_rss_ind_table()`. `bnx2x_setup_rss()` fills `eth_rss_update_ramrod_data`, maps driver RSS flags to firmware capabilities for IPv4, IPv6, TCP, UDP, VXLAN, and inner tunnel headers, byte-reverses the Toeplitz key when `BNX2X_RSS_SET_SRCH` is requested, stores the indirection table mirror, and posts `RAMROD_CMD_ID_ETH_RSS_UPDATE`.

Queue lifecycle operations are exposed by `bnx2x_queue_state_change()`, `bnx2x_init_queue_obj()`, and `bnx2x_get_q_logical_state()`. The send path dispatches INIT, SETUP, SETUP_TX_ONLY, UPDATE, UPDATE_TPA, ACTIVATE, DEACTIVATE, HALT, CFC_DEL, TERMINATE, and EMPTY commands. Helpers fill firmware setup/update ramrod data for general, Rx, Tx, pause, TPA, anti-spoofing, default VLAN, VLAN removal, Tx switching, PTP packet handling, coalescing, context validation, and multi-CoS Tx-only queues.

Function lifecycle operations are exposed by `bnx2x_func_state_change()`, `bnx2x_init_func_obj()`, and `bnx2x_func_get_state()`. The implementation checks state transitions, serializes pending commands with `one_pending_mutex`, calls driver-supplied HW/FW init/reset operations for load/unload phases, and sends common function ramrods for START, STOP, SWITCH_UPDATE, AFEX_UPDATE, AFEX_VIF_LISTS, TX_STOP, TX_START, and SET_TIMESYNC.

## Control Flow

Most public verbs follow a common pattern: validate state, set a pending bit, populate a DMA command buffer or direct register data, post a ramrod unless `RAMROD_DRV_CLR_ONLY` is set, optionally wait if `RAMROD_COMP_WAIT` is set, and clear/update state in a completion callback. Return values use the driver's slow-path convention: `0` means completed/no pending work, positive usually means a completion remains pending, and negative values are errors.

For VLAN/MAC classification, callers populate `bnx2x_vlan_mac_ramrod_params` and call `bnx2x_config_vlan_mac()`. Unless `RAMROD_CONT` is set, the request becomes a `bnx2x_exeq_elem`. `bnx2x_exe_queue_add()` may optimize it away, then validates registry state, pending duplicates, move conflicts, and credit availability. Execution is triggered by `RAMROD_EXEC`, `RAMROD_CONT`, or `RAMROD_COMP_WAIT`. `bnx2x_execute_vlan_mac()` sets the raw pending bit, creates or finds registry entries, fills one or more firmware rules, posts the ramrod, and removes deleted or moved entries from the source registry. `bnx2x_complete_vlan_mac()` clears the pending chunk and raw pending bit atomically and can continue with the next chunk when `RAMROD_CONT` is set.

For multicast, `bnx2x_config_mcast()` snapshots the old registry size, validates/accounting-adjusts the request, enqueues work if another ramrod is pending or the request exceeds one ramrod, then sets raw pending and calls the chip-specific setup callback. E2 setup first drains pending commands into the next ramrod, then handles any current command still fitting in the same ramrod, adjusts `total_pending_num`, refreshes actual registry size once all pending work drains, and posts or completes driver-only/no-op work. On failure, the raw pending bit is cleared and `revert()` restores registry counters.

For queue and function state machines, the object transition callback is the gatekeeper. It rejects illegal current-state/command combinations and records `next_state`. The state-change function sets a pending bit before sending the command. Completion handlers verify the expected bit, assign `state = next_state`, clear `next_state`, use write barriers so state is visible before pending is cleared, and then clear the pending bit. Function state changes additionally use `one_pending_mutex` and optionally retry `-EBUSY` transitions when `RAMROD_RETRY` is set.

## State and Persistence Behavior

The file does not persist state outside the kernel driver. Its persistence is in-memory state that mirrors firmware and hardware configuration across asynchronous ramrods and restore flows. Key state includes raw pending bits in caller-provided bitmaps, VLAN/MAC registry lists containing configured rules and CAM offsets, execution queue lists, multicast exact or approximate registries, multicast pending command lists and counters, credit-pool atomic counters and bitmaps, RSS indirection-table mirrors, queue state/next-state/pending fields, function state/next-state/pending fields, and DMA command buffers reused for ramrod data.

Memory ordering is explicit. Raw pending setters/clearers and multicast scheduled-bit helpers wrap bit operations with `smp_mb__before_atomic()` and `smp_mb__after_atomic()`. Queue and function completions update state before clearing pending bits and use `wmb()`. Execution queue movement uses a spacer node plus `mb()` so `bnx2x_exe_queue_empty()` can be called without locking and not observe both lists empty while an element is being moved.

Driver-only cleanup and restore are first-class states. `RAMROD_DRV_CLR_ONLY` updates local registries/pending bits without posting firmware commands, while `RAMROD_RESTORE` rebuilds firmware configuration from software registries after reset/reload using saved flags and registry entries.

## Dependencies and Integration Points

The module depends on Linux kernel list, spinlock, mutex, atomic, DMA, endian, Ethernet address, CRC32C, sleep, and netdevice facilities. It includes `bnx2x.h`, `bnx2x_cmn.h`, and `bnx2x_sp.h`, and depends heavily on hardware/firmware HSI structs and constants such as `eth_classify_rules_ramrod_data`, `eth_filter_rules_ramrod_data`, `eth_multicast_rules_ramrod_data`, `eth_rss_update_ramrod_data`, `client_init_ramrod_data`, `function_start_data`, and `RAMROD_CMD_ID_*`.

Primary external integration points are `bnx2x_sp_post()` for ramrod submission, `REG_WR()`/`REG_WR_DMAE()`/`__storm_memset_struct()` for direct hardware memory programming, `bnx2x_update_coalesce_sb_index()` and `bnx2x_set_ctx_validation()` for queue initialization, driver-supplied function HW/FW init/reset callbacks, chip-family macros (`CHIP_IS_E1`, `CHIP_IS_E1H`, `CHIP_IS_E1x`, `CHIP_REV_IS_SLOW`, `CHIP_REV_IS_EMUL`), function/port macros (`BP_FUNC`, `BP_ABS_FUNC`, `BP_PATH`, `BP_PORT`), and VF credit macros.

Completion handlers elsewhere in the driver must call the object `complete`/`complete_cmd` callbacks with the correct command identifiers. Higher-level netdev operations, queue setup/teardown, multicast list changes, RSS changes, AFEX handling, DCB/timesync, and reload/reset paths all rely on these slow-path objects being initialized with the correct command buffers, CIDs, CL IDs, function IDs, state bits, and credit pools.

## Risks and Edge Cases

The highest-risk areas are asynchronous state consistency, credit accounting, and chip-specific command limits. VLAN/MAC validation consumes or returns credits before firmware success, so all optimization, remove, failure, move, and driver-only paths must balance credits and CAM entries. `bnx2x_execute_vlan_mac()` updates the registry before firmware completion; if `bnx2x_sp_post()` or rule construction fails, error cleanup must delete only newly added entries and restore pending state. Move commands span source and destination objects and consume two rule slots, increasing the chance of registry or credit skew.

Concurrency is subtle. VLAN/MAC registry readers use a custom reader count under the execution queue lock, and writers pend execution while readers are active. The execution queue intentionally permits lockless empty checks, depending on ordering barriers and the spacer list entry. Function state changes are mutex-protected, but AFEX has a separate buffer because AFEX ramrods may arrive in parallel to other requests.

Multicast approximate matching can overestimate pending work because multiple MACs may map to the same bin; SET conversion deliberately postpones exact diffing until earlier pending commands have applied. E1 exact-match registry refresh allocates one array and stores entries in a list; delete frees the first entry pointer and reinitializes the list, which assumes all entries came from a contiguous allocation. E1/E1H command support differs from E2; unsupported SET or VLAN-MAC cases intentionally return errors or `BUG()`.

Timeout behavior in `bnx2x_state_wait()` can surface as `-EBUSY` under firmware stalls. Several paths rely on completion code elsewhere to clear pending bits. Missing, duplicate, or mismatched completions will leave objects stuck or trigger "Bad MC reply" errors.

## Test Signals

Useful dynamic signals include successful interface load/unload across all MCP load phases, queue transitions through RESET -> INITIALIZED -> ACTIVE/INACTIVE -> STOPPED/TERMINATED -> RESET, multi-CoS setup/terminate/CFC delete, VLAN/MAC add/delete/move/restore under credit pressure, multicast ADD/DEL/SET/RESTORE lists larger than one E2 ramrod, rx-mode changes for promiscuous/all-multicast/broadcast/unmatched/any-VLAN modes, RSS key and indirection updates including UDP and tunnel flags, AFEX update/vif-list commands, PTP timesync command posting, and driver-only cleanup paths during reset.

White-box assertions should watch pending bits, `next_state`, registry sizes, credit counters, CAM pool mirrors, `total_pending_num`, and the RSS indirection mirror before and after completions. Error tests should force `bnx2x_sp_post()` failure, invalid MACs, duplicate filters, deletion of absent filters, illegal state transitions, exhausted credit pools, and completion timeout/panic paths. Build coverage should include configurations for E1, E1H, E2/newer, SR-IOV credit reservations, FCoE/iSCSI queues, and emulation/slow-chip limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sp.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sp.h -->
