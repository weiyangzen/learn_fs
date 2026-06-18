<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_adminq.h -->
# sources/distributed-fs/ceph-client/include/linux/pds/pds_adminq.h

## Purpose
Defines the AMD/Pensando PDS core AdminQ and NotifyQ wire ABI used by the core driver and auxiliary clients. The file is almost entirely command, completion, notification, queue, vDPA, live-migration, and firmware-control descriptor layout. It also exposes `pdsc_adminq_post()` as the submission helper and `pdsc_color_match()` for completion-ring ownership detection.

## Important APIs, Types, And Functions
- `enum pds_core_adminq_opcode` assigns AdminQ opcodes for client registration/proxying, LIF identify/init/reset/getattr/setattr, RX filter placeholders, queue identify/init/control, and VF get/set attributes.
- NotifyQ data is modeled by `enum pds_core_notifyq_opcode`, `struct pds_core_notifyq_event`, `struct pds_core_link_change_event`, `struct pds_core_reset_event`, `struct pds_core_client_event`, and `union pds_core_notifyq_comp`.
- Client command wrappers are `struct pds_core_client_reg_cmd`, `pds_core_client_unreg_cmd`, and `pds_core_client_request_cmd`, with `client_id` returned in `pds_core_client_reg_comp`.
- LIF and queue setup uses `union pds_core_lif_config`, `struct pds_core_lif_info`, `pds_core_lif_identity`, LIF command/completion pairs, `struct pds_core_q_identity`, `pds_core_q_identify_cmd`, and `pds_core_q_init_cmd`; `PDS_CORE_QSIZE_MIN_LG2`/`MAX_LG2` constrain ring sizes.
- vDPA support is described by `enum pds_vdpa_cmd_opcode`, `struct pds_vdpa_ident`, status/setattr/set-features commands, and virtqueue init/reset command/completion records.
- Live migration support is described by `enum pds_lm_cmd_opcode`, state-size/suspend/resume/save/restore commands, dirty-page region and bitmap commands, and host-VF status commands.
- Firmware control support is described by `enum pds_fwctl_cmd_opcode`, identify/query/RPC commands, query data records, `struct pds_sg_elem`, and RPC indirect request/response flags.
- `union pds_core_adminq_cmd` is fixed at 64 bytes and overlays all command variants; `union pds_core_adminq_comp` is fixed at 16 bytes and overlays completion variants.

## Control Flow
Callers fill one member of `union pds_core_adminq_cmd`, submit it through `pdsc_adminq_post()`, and receive a matching `union pds_core_adminq_comp`. Identify-style commands pass DMA addresses for firmware-populated side buffers. Queue/LIF init proceeds from identify to init, with queue descriptors carrying ring base DMA addresses and interrupt indexes. NotifyQ consumption uses the event code to reinterpret `union pds_core_notifyq_comp`. Completion ring processing uses the color bit, where `pdsc_color_match()` compares `PDS_COMP_COLOR_MASK` against the expected ring pass color.

## State And Persistence
Most state is device or firmware state, not kernel-owned persistence: client IDs, LIF identity/config/status, hardware queue indexes, vDPA device indexes and features, live migration state blobs, dirty tracking regions/bitmaps, and firmware-control endpoint metadata. DMA buffers handed to identify, save/restore, dirty tracking, and RPC commands persist only for the transaction unless higher layers keep them. The 64/16/64-byte static assertions are part of the ABI contract and guard persistence/layout compatibility with firmware.

## Dependencies And Integration Points
This header depends on Linux fixed-width little-endian types, bit helpers, DMA-address conventions, and status codes from the PDS core interface. It integrates with the PDS core PCI driver, auxiliary bus clients, vDPA, VFIO live migration, SR-IOV VF management, and firmware-control RPC plumbing. The final external API is `pdsc_adminq_post(struct pdsc *, union pds_core_adminq_cmd *, union pds_core_adminq_comp *, bool fast_poll)`.

## Risks And Edge Cases
Risks are ABI layout drift, endian mistakes, using the wrong union member for a completion, mismatched opcode/client/VF identifiers, DMA buffer lifetime bugs, ring-size values outside the documented log2 range, invalid scatter-gather counts, overlapping dirty-tracking regions, and incorrect completion color toggling. `PDS_CORE_ADDR_MASK`-style address limits in adjacent headers also matter for DMA addresses. `PDS_AQ_FLAG_FASTPOLL` and `fast_poll` affect polling latency, so long-running firmware operations must not be accidentally treated as short operations.

## Test Signals
Useful signals include compile-time static assertions, successful client register/unregister with stable client IDs, LIF identify/init/reset cycles, queue identify/init with valid HW queue IDs, NotifyQ link/reset/client event decoding, vDPA feature and virtqueue lifecycle tests, VFIO live-migration save/restore and dirty-bitmap tests, fwctl identify/query/RPC round trips, DMA fault injection, and completion timeout/color-wrap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_adminq.h -->
