# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mcp.h

## Purpose

`qed_mcp.h` is the driver-facing declaration layer for the QED management firmware interface implemented in `qed_mcp.c`. It defines the stable in-driver data structures used to configure link state, expose function information, pass protocol statistics and TLVs, perform mailbox commands, and coordinate resource locks. It also declares the public MCP APIs used by the rest of the QED core, ethernet, storage offload, RDMA, SR-IOV, debug, and management paths.

The header does not define the firmware scratchpad wire layout itself; it includes `qed_mfw_hsi.h` indirectly through implementation use and includes `qed_hsi.h` and `qed_dev_api.h` for driver-visible enums and hardware abstractions. Its role is to hide most firmware mailbox details behind QED-native types while still exposing enough state for initialization and fast-path-adjacent link updates.

## Important Types and API Groups

Link configuration is represented by `struct qed_mcp_link_speed_params`, `struct qed_mcp_link_pause_params`, `enum qed_mcp_eee_mode`, `struct qed_mcp_link_params`, `struct qed_mcp_link_capabilities`, and `struct qed_mcp_link_state`. These types split desired input (`link_input` in `qed_mcp_info`) from firmware-reported output (`link_output`) and default capabilities. They cover base and extended advertised speeds, forced speed, pause autoneg/forced RX/TX, loopback, EEE, FEC, line speed, PF rate after bandwidth constraints, duplex, autoneg completion, PFC, link partner capabilities, SFP fault, EEE advertisements, and active FEC mode.

`struct qed_mcp_function_info` is the driver's cached view of per-PF firmware configuration: pause-on-host, PCI personality, min/max bandwidth, MAC, FCoE WWNs, outer VLAN/stag, and MTU. It is populated from `public_func` shared memory by `qed_mcp_fill_shmem_func_info()`.

Firmware reporting and management data structures include `struct qed_mcp_drv_version`, per-protocol stats structures, `union qed_mcp_protocol_stats`, `enum qed_mcp_protocol_type`, TLV enums and `union qed_mfw_tlv_data`, NVM config flags, and `struct qed_nvm_image_att`.

`struct qed_mcp_info` is the central runtime state container. It owns the pending command list, `cmd_lock`, command blocking flag, `link_lock`, SHMEM section addresses, mailbox sequence state, link input/output/capabilities, cached function info, event current/shadow buffers, MFW message length, MCP reset history, negotiated capability bitmask, atomic debug-data sequence, `unload_lock`, and event handling status bits. `QED_MCP_BYPASS_PROC_BIT` and `QED_MCP_IN_PROCESSING_BIT` coordinate unload with event handling.

`struct qed_mcp_mb_params` is the generic command descriptor for mailbox transactions. It carries command, parameter, optional source and destination union payload pointers, payload sizes, response fields, and flags. `QED_MB_FLAG_CAN_SLEEP` selects sleepable polling, while `QED_MB_FLAG_AVOID_BLOCK` prevents a command failure from globally blocking future mailbox commands.

Resource locking declarations include `enum qed_resc_lock`, `struct qed_resc_lock_params`, `struct qed_resc_unlock_params`, retry/timeout defaults, and APIs for lock, unlock, default initialization, resource allocation reads, and resource max updates. The resource lock range intentionally maps to firmware generic resource IDs 0..31, with debug dump and per-port PTP locks plus a resource-allocation lock.

## Public API Surface

The header declares initialization and mailbox primitives (`qed_mcp_cmd_init()`, `qed_mcp_cmd_port_init()`, `qed_mcp_free()`, `qed_mcp_is_init()`, `qed_mcp_cmd()`, `qed_mcp_cmd_nosleep()`, `qed_mcp_nvm_rd_cmd()`, `qed_mcp_reset()`, `qed_mcp_read_mb()`, `qed_mcp_handle_events()`), lifecycle operations (`qed_mcp_load_req()`, `qed_mcp_load_done()`, `qed_mcp_unload_req()`, `qed_mcp_unload_done()`), link and media operations (`qed_mcp_set_link()`, link accessors, MFW/MBI version reads, media/transceiver/board config reads), and management updates (`qed_mcp_ov_update_*()`, `qed_mcp_set_led()`, `qed_mcp_mask_parities()`).

NVM and diagnostics APIs include `qed_mcp_nvm_read()`, `qed_mcp_nvm_write()`, `qed_mcp_nvm_resp()`, image attribute/image read helpers, BIST helpers, NVM info cache populate/free, NVM config get/set, mdump retained data access, and raw debug data send. SR-IOV and recovery APIs include VF FLR ack, VF MSI-X configuration, PF FLR initiation, process kill counter read, recovery trigger, and recovery prolog. Capability and platform APIs include MFW feature get/set, SmartAN support, extended speed support inline check, UFP config read, engine affinity, PPFID bitmap, enhanced system lockdown support, and ESL active status.

## Control Flow and State Contract

The header encodes the expected call order. A PF creates `qed_mcp_info` with `qed_mcp_cmd_init()`, initializes port address after port mapping is known, reads capabilities and function information, performs load request/done, then uses link, NVM, event, and management APIs during runtime. Callers that only need current state retrieve pointers to `link_input`, `link_output`, or `link_capabilities`; these are owned by `qed_mcp_info` and must not outlive it.

Command callers either use the simple `qed_mcp_cmd()`/`qed_mcp_cmd_nosleep()` wrappers or the more specialized APIs that construct `qed_mcp_mb_params` internally. The `qed_mcp_mb_params` contract is size-bound by `union drv_union_data`, so source and destination payloads are small mailbox payloads rather than arbitrary DMA buffers.

Resource lock callers should use `qed_mcp_resc_lock_default_init()` to initialize retry and aging behavior, then check result booleans in the parameter structures. A zero return from `qed_mcp_resc_lock()` means the firmware protocol completed, not necessarily that the lock was granted.

## Dependencies and Integration Points

This header is included across QED core modules that need MFW services. It depends on Linux primitives (`types`, `delay`, `slab`, `spinlock`), protocol TLV definitions from `linux/qed/qed_fcoe_if.h`, QED hardware/software interface definitions from `qed_hsi.h`, and common device API types from `qed_dev_api.h`. The declarations reference `struct qed_hwfn`, `struct qed_ptt`, `struct qed_dev`, firmware HSI structs such as `bist_nvm_image_att` and `mdump_retain_data_stc`, and QED enums such as `qed_led_mode`, `qed_resources`, `qed_nvm_images`, and `qed_override_force_load`.

The `MCP_PF_ID_BY_REL()` macro is a notable integration point with hardware mode. It maps relative PF IDs to MCP PF IDs differently for BB devices, incorporating the hardware function's absolute PF parity in CMT mode. Incorrect use of `rel_pf_id` without this macro would address the wrong shared-memory PF slot.

## Risks and Edge Cases

Because `qed_mcp_info` is exposed in the header, non-MCP modules can access internal state directly if they include the header. That makes lock discipline important: command list and mailbox state require `cmd_lock`, link state updates require `link_lock`, and unload/event status bits require `unload_lock`.

Several comments in the header contain stale wording, for example `qed_mcp_cmd()` says polling is checked every 10 ms even the implementation uses 10 microsecond intervals with sleep ranges. Consumers should trust implementation constants for timing-sensitive behavior.

The public state accessors return raw pointers, not copies. Callers must handle NULL when MCP is not initialized and avoid unsynchronized mutation except through established QED paths. NVM and management update APIs can alter durable firmware/device state, so tests and callers need to distinguish read-only query helpers from persistent configuration operations.

## Test Signals

Header-level validation is mostly compile-time and integration-oriented: all declared APIs should match implementation signatures; feature flags should map to firmware HSI definitions; and structure sizes used in mailbox payloads must not exceed `union drv_union_data`. Runtime tests should validate initialization order, NULL-safe accessors, MCP PF ID mapping in BB/CMT mode, resource-lock parameter defaults, extended-speed feature gating, and expected error behavior for VF contexts or uninitialized MCP state.
