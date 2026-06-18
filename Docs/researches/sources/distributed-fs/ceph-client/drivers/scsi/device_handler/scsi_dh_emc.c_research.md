<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_emc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_emc.c

Purpose: implements the EMC CLARiiON AX/CX/FC-family SCSI device handler for active/passive multipath failover. It identifies CLARiiON service processor state through inquiry/VPD page data, blocks I/O on non-owned LUN paths, and activates paths by sending CLARiiON trespass MODE SELECT commands.

Important APIs/types/functions: `struct clariion_dh_data` stores handler flags, command buffer, LUN state, port, default SP, and current SP. Important helpers include `parse_sp_info_reply()`, `parse_sp_model()`, `clariion_std_inquiry()`, `clariion_send_inquiry()`, `send_trespass_cmd()`, `trespass_endio()`, `clariion_check_sense()`, `clariion_prep_fn()`, `clariion_activate()`, and `clariion_set_params()`. The registered `clariion_dh` supplies attach/detach/check_sense/activate/prep_fn/set_params callbacks.

Control flow: attach allocates per-device state, parses standard inquiry data to decide whether short trespass is needed for older FC models, reads VPD page `0xC0`, parses SP ownership/failover mode, updates `sdev->access_state`, and stores handler data. `prep_fn` fails requests unless the LUN is owned by this path. Activation refreshes VPD page `0xC0`; if the LUN is not owned, it builds either a short MODE SELECT(6) or long MODE SELECT(10) page `0x22` trespass request, sends it, then refreshes SP state and invokes the completion callback. Parameter changes update short-trespass and honor-reservation flags, optionally sending a new trespass if the path is already owned.

State and persistence: per-device memory caches the latest CLARiiON LUN/SP state and policy flags. Firmware-side ownership changes persist on the storage array after successful trespass; the handler itself has no persistent local storage. Static trespass templates are copied into the per-device buffer before command execution, but their reservation bit is modified before copy.

Dependencies and integration: depends on SCSI inquiry/VPD, `scsi_execute_cmd()`, MODE SELECT(6/10), sense handling, `sdev->access_state`, and the SCSI device-handler core used by multipath. It integrates with arrays that report failover mode through EMC-specific VPD layout.

Risks: the code mutates static `short_trespass`/`long_trespass` arrays when setting the honor-reservations bit, so parameter changes can have process-wide effects that are not fully reversible. VPD page offsets are vendor-specific and sensitive to malformed or short buffers. The code recognizes ALUA failover mode but remains a CLARiiON trespass handler, so mixed firmware behavior needs care. Passive-path sense handling intentionally returns `SUCCESS` in some cases to let upper layers bypass paths.

Test signals: attach on supported and unsupported CLARiiON models, short versus long trespass selection, VPD page `0xC0` parsing for owned/bound/unbound states, activation from passive to owned, honor-reservation parameters, array-copy/NDU sense handling, `prep_fn` quiet failure on passive paths, and module registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/scsi_dh_emc.c -->
