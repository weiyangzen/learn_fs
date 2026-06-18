# sources/distributed-fs/ceph-client/drivers/ntb/hw/mscc/ntb_hw_switchtec.c

## Purpose
Implements the Microsemi/Microchip Switchtec NTB hardware provider. It binds to `switchtec_class` devices, identifies a peer partition, exports `struct ntb_dev_ops`, configures direct and LUT memory windows, manages shared link state, scratchpads, doorbells, messages, and crosslink operation. It is the low-level driver that higher NTB clients such as transport, test, perf, and tool drivers consume through the generic NTB API.

## Important APIs, Types, And Functions
- `struct shared_mw` is the 64 KiB shared control window format. It stores `SWITCHTEC_NTB_MAGIC`, software link state, partition id, advertised memory-window sizes, and 128 scratchpads.
- `struct switchtec_ntb` is the full provider state: embedded `struct ntb_dev`, Switchtec device pointer, partition ids, MMIO register blocks, shared MW mappings, doorbell masks/shifts, direct/LUT MW counts, link status, and async link work.
- `switchtec_ntb_ops` wires the provider to the generic NTB core: MW count/alignment/translation, peer MW address, link up/down, doorbells, scratchpads, and peer address helpers.
- `switchtec_ntb_part_op()` serializes Switchtec partition operations by writing `partition_op` and polling `partition_status` for lock/config/reset transitions.
- `switchtec_ntb_mw_set_trans()` validates peer index, window index, size and address alignment, locks peer control registers, programs direct BAR or LUT translation, commits config, and cleans up on hardware-reported errors.
- `switchtec_ntb_init_crosslink()` handles special crosslink topology by enumerating the virtual peer partition BARs, reserving LUT windows, mirroring requester IDs, mapping peer DB/message registers through a local window, and changing topology to `NTB_TOPO_CROSSLINK`.
- `switchtec_ntb_init_shared_mw()` allocates coherent memory for local shared state, reserves peer LUT entry 0 to expose it, and maps the peer shared window through BAR0.
- `switchtec_ntb_init_db_msg_irq()` assigns Switchtec vectors for doorbells and messages and registers `switchtec_ntb_doorbell_isr()` / `switchtec_ntb_message_isr()`.

## Control Flow
Module init registers a class interface on `switchtec_class`. `switchtec_ntb_add()` filters Switchtec bridge devices, allocates `switchtec_ntb`, initializes partition/MMIO pointers, discovers MW capabilities, programs requester IDs, optionally initializes crosslink, initializes doorbell/message mappings, allocates and maps the shared MW, requests IRQs, sends `MSG_LINK_FORCE_DOWN` to stale peers, and registers the NTB device.

Link enable writes local `self_shared->link_sta`, sends a link message, and recomputes link status. Link status is considered up only when local software state is set and the peer shared MW contains the Switchtec magic plus its high 32-bit link flag. Link and forced-down messages schedule `check_link_status_work`, which either reinitializes the peer shared MW or runs normal link status update and emits `ntb_link_event()`.

Memory-window setup is peer-control-register driven. Direct windows program BAR control/size/translation registers; LUT windows program LUT entries. Direct BAR0 has special layout because LUT regions consume the front of the BAR and the direct shared area starts after `LUT_SIZE * nr_lut_mw`. The driver advertises local MW sizes in the shared page and uses the peer shared page for inbound alignment/size queries.

Doorbells use either split halves of a shared DBMSG block or all bits in crosslink mode. The driver shifts local and peer bits according to partition ordering, masks/unmasks with a spinlock-protected cached mask, clears by writing IDB bits, and rings the peer by writing ODB bits. Message IRQs inspect each inbound message slot, clear status, and treat slot 0 as link-control traffic.

Removal clears the Switchtec notifier, unregisters the NTB device, frees IRQs, unmaps/free shared MW resources, unmaps crosslink windows, cancels work, and frees provider state.

## State And Persistence
Persistent hardware-facing state lives in Switchtec NTB control registers, DBMSG registers, BAR/LUT configuration, requester-ID tables, and the coherent shared MW. In-memory state caches partition ids, masks, MW maps, and link status. Scratchpad values are stored in `self_shared->spad[]` and exposed to peers via the reserved shared window. Link status persists across host crashes from the peer perspective, hence probe sends `MSG_LINK_FORCE_DOWN` to force stale software state down.

## Dependencies And Integration Points
Depends on `linux/switchtec.h` register definitions, PCI resource/iomap APIs, coherent DMA allocation, interrupts, workqueues, and the generic NTB core. It integrates with Switchtec core through `stdev->sndev` and `stdev->link_notifier`, and with NTB clients through `ntb_register_device()`. Upper layers rely on correct MW alignment, peer DB addressing, scratchpad storage, and link event notifications.

## Risks And Edge Cases
- MW translation requires size-power alignment of the DMA address; CMA or large coherent allocations can violate this and return `-EINVAL`.
- `switchtec_ntb_spad_read()` and peer helpers compute `ARRAY_SIZE(sndev->peer_shared->spad)` before null checks; normal initialization sets mappings first, but failures or unexpected calls before mapping would be risky.
- Crosslink setup relies on enumerating virtual BARs and mapping peer DBMSG through a reserved LUT; failures leave partial hardware state unless later cleanup handles it.
- `config_req_id_table()` logs `-EIO` errors but returns `0`, which could hide requester-ID programming failures.
- Doorbell vector mask accepts `db_vector > 1` as invalid, so vector `1` still returns a mask despite `db_vector_count()` returning one vector; consumers normally query vector 0.
- Shared MW and register operations are hardware-coordination sensitive; link churn, peer reset, or stale peer shared data can produce transient false-down or forced-down events.

## Test Signals
Useful validation comes from loading the provider on Switchtec NTB hardware, checking `ntb_transport` link creation, exercising doorbells/scratchpads with `ntb_pingpong` and `ntb_tool`, running `ntb_perf` across direct/LUT windows, and testing crosslink hardware if available. Build coverage should include `CONFIG_NTB`, Switchtec support, and optional clients. Runtime logs around `failed to register ntb device`, `Error setting up reserved lut window`, `Hardware reported an error configuring mw`, and `ntb link up/down` are strong diagnostic signals.
