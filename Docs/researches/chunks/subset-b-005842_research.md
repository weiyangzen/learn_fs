# sources/distributed-fs/ceph-client/include/linux/bnge/hsi.h lines 12028-12609

## Scope

This chunk is the final section of the Broadcom NetGExreme (`bnge`) HSI header. It starts in the middle of `hwrm_nvm_install_update_output`, then defines the remaining NVM command error/result contracts, NVM variable/profile/VPD command payloads, firmware self-test command payloads, doorbell record formats, firmware status bits, the host-communication status locator, and the header guard close.

The file is a firmware ABI definition, not executable driver logic. All structs are packed-by-layout C declarations with little-endian integer fields where the HWRM protocol crosses the host/firmware boundary. The surrounding BNGE driver includes this header from HWRM helper, netdev, TX/RX, resource, and devlink code; closely matching BNXT code in the same source tree shows the same HWRM contracts being used for devlink NVM parameters, ethtool self-tests, firmware package update defrag, and firmware health status mapping.

## Purpose

The chunk provides the typed ABI surface for late-stage firmware management and low-level runtime signaling:

- NVM install/update result tails communicate why a firmware package install failed, which package item was responsible, and whether PCI or power reset is required afterward.
- NVM flush, get/set variable, defrag, VPD field, and profile commands define the request/response buffers sent through HWRM for persistent firmware configuration and package maintenance.
- Self-test query/execute/IRQ commands expose firmware diagnostics to host tools such as ethtool-style self tests.
- `dbc_dbc`, `db_push_start`, `db_push_end`, and `db_push_info` define 64-bit doorbell and doorbell-push record bit layouts for queue notification, queue arming, and debug tracing paths.
- `fw_status_reg` and `hcomm_status` define the firmware-health status register bits and a discoverable host-communication structure used to locate that status register in PCI config, GRC, BAR0, or BAR1 space.

Because these definitions sit in an exported kernel include path under `include/linux/bnge`, they are the source of truth for BNGE's binary contract with Broadcom firmware. The driver code should not reinterpret these fields with independent constants unless those constants are deliberately mirrored for convenience, as `bnge_db.h` does for doorbell writes.

## Important APIs, Types, and Constants

### NVM install/update tail

The chunk begins with the final result constants in `struct hwrm_nvm_install_update_output`. These include unsupported subsystem/platform result codes, duplicate and zero-length item failures, checksum/data/authentication failures during install, item-not-found, and item-locked. The following fields complete the response:

- `problem_item`: reports no problem item or the package as the problem item.
- `reset_required`: reports none, PCI reset, or power reset.
- `valid`: firmware-owned response-valid marker common to HWRM outputs.

`struct hwrm_nvm_install_update_cmd_err` is the command-error side channel for install/update failures. It distinguishes generic unknown errors from fragmentation, no-space, anti-rollback, missing voltage-regulator support, defrag failure, and unknown directory errors. In the older BNXT ethtool path, matching install result codes are mapped into user-visible extack errors such as invalid image, authentication error, unsupported device, no space, or internal error; BNGE can use the same HSI meanings when adding or reviewing firmware update paths.

### NVM flush and variable commands

`struct hwrm_nvm_flush_input/output/cmd_err` define a small no-payload HWRM command that asks firmware to flush pending NVM state. The error extension only distinguishes unknown from fail, so callers must rely on the main HWRM `error_code` for most transport/status handling.

`struct hwrm_nvm_get_variable_input` and `struct hwrm_nvm_set_variable_input` are 40-byte requests for persistent option variables. Their common fields are:

- HWRM header fields: `req_type`, `cmpl_ring`, `seq_id`, `target_id`, and `resp_addr`.
- DMA payload address: `dest_data_addr` for reads and `src_data_addr` for writes.
- `data_len`: the option data length, represented by the HWRM contract for the selected option.
- `option_num`: the NVM option identifier, with only reserved sentinels defined in this header chunk.
- `dimensions` and `index_0` through `index_3`: selectors for scalar or array-like option instances, such as per-port or per-function configuration.
- `flags`: get supports factory-default reads and option-value validation; set supports force-flush, encryption/authentication modes, and factory-default writes.

`struct hwrm_nvm_get_variable_output` returns `data_len`, `option_num`, validation flags, and `valid`; set only returns the standard HWRM output header plus `valid`. Their command-error structs enumerate variable-not-found, corrupt variable, short length, invalid index, access denied, callback failure, invalid data length, and no-memory cases; set additionally reports unsupported action.

In the matching BNXT devlink implementation, `HWRM_NVM_GET_VARIABLE` and `HWRM_NVM_SET_VARIABLE` allocate an HWRM DMA slice, set `dest_data_addr`, `data_len`, `option_num`, `index_0`, and `dimensions`, and translate `NVM_GET_VARIABLE_CMD_ERR_CODE_VAR_NOT_EXIST` to `-EOPNOTSUPP`. That is a useful integration model for BNGE because the same field semantics determine how devlink parameters should persist in firmware NVM.

### NVM defrag, VPD, and profile commands

`struct hwrm_nvm_defrag_input/output/cmd_err` define a 24-byte request with `NVM_DEFRAG_REQ_FLAGS_DEFRAG`. The error extension distinguishes unknown, fail, and check-fail. In the matching BNXT firmware package resize flow, a failed update-area resize caused by `-ENOSPC` triggers `HWRM_NVM_DEFRAG` once before retrying the resize, so this ABI is part of firmware update reliability and space recovery.

`struct hwrm_nvm_get_vpd_field_info_input/output/cmd_err` and `struct hwrm_nvm_set_vpd_field_info_input/output` provide tag-based VPD field access. Get accepts a two-byte `tag_id` and returns up to 256 bytes plus `data_len`; set provides `host_src_addr`, `tag_id`, and `data_len`. Get-specific command errors cover not-cached, VPD parse failure, and invalid tag ID. BNGE devlink currently reads board part number and serial number through PCI VPD helper APIs, but these HWRM VPD definitions are the firmware-managed alternative for VPD keyword access.

`struct hwrm_nvm_set_profile_input/output/cmd_err` and `struct hwrm_nvm_set_profile_sb` describe profile writes composed of option sub-blocks. The request points to a DMA block at `src_data_addr`, provides total `data_len`, `option_count`, flags, and `profile_type`. Defined flags support force-flush, validate-only, and factory-default behavior. The only named profile type in this chunk is `EROCE`, tying profile provisioning to RDMA/RoCE capability. The command-error payload includes `err_index`, allowing firmware to report which sub-block failed, and adds `PROVISION_ERROR` beyond the ordinary NVM variable errors. Each `hwrm_nvm_set_profile_sb` contains one option's data length, option number, dimensional selectors, and reserved flags.

### Self-test commands

`struct hwrm_selftest_qlist_input/output` lets the host ask firmware which tests are available. The output includes:

- `num_tests`.
- `available_tests` and `offline_tests` bitmasks for NVM, link, register, memory, PCIe SerDes, and Ethernet SerDes tests.
- `test_timeout`, eight fixed-width test names, and `eyescope_target_BER_support` levels from BER 1e8 through 1e12.

`struct hwrm_selftest_exec_input/output` executes a selected test mask and returns `requested_tests` and `test_success` bitmasks using the same six firmware test bits. `struct hwrm_selftest_irq_input/output` verifies interrupt delivery for a supplied completion ring.

The matching BNXT ethtool path queries `HWRM_SELFTEST_QLIST` at initialization to size and name test entries, uses `resp->test_timeout` for `HWRM_SELFTEST_EXEC`, and copies `resp->test_success` into ethtool results. It also loops over completion rings and sends `HWRM_SELFTEST_IRQ` with each ring's firmware ID. BNGE has the same HWRM command definitions available if it wires equivalent ethtool diagnostics.

### Doorbell records

`struct dbc_dbc` is an 8-byte doorbell completion/debug record split into:

- `index`: a 24-bit producer/consumer index plus epoch and toggle bits.
- `type_path_xid`: a 20-bit queue XID, path selector (`ROCE`, `L2`, or `ENGINE`), valid/debug-trace flags, and a 4-bit doorbell type.

The doorbell types include SQ, RQ, SRQ, SRQ arm variants, CQ, CQ arm variants, CQ cutoff ack, NQ, NQ arm, CQ reassign, NQ mask, and null.

`struct db_push_start` and `struct db_push_end` are 64-bit packed MMIO payload formats for push-start and push-end doorbells. They carry a 24-bit index, split producer index low/high bits, 20-bit XID, type, and for push-end also path and debug-trace fields. `struct db_push_info` records a 24-bit push index and 5-bit push size.

BNGE driver doorbell helpers mirror these layouts in `bnge_db.h` and `bnge_netdev` code with `DBR_*` constants. Ring allocation builds `db_key64` from path, ring type, XID, and valid bit; TX/RX and completion paths then OR in `DB_RING_IDX()` and issue 64-bit writes to the doorbell BAR. On 32-bit hosts, `bnge_writeq()` serializes the split 64-bit write under `bd->db_lock`, matching the ABI requirement that doorbell writes be atomic from firmware's perspective.

### Firmware status and host-communication locator

`struct fw_status_reg` defines a 32-bit firmware health word. The low 16 bits carry the status code, with `FW_STATUS_REG_CODE_READY` as the named ready value. Higher bits indicate degraded image, recoverable condition, crashdump ongoing/complete, shutdown, crashed-with-no-master, recovering, and manufacturing debug status.

`struct hcomm_status` defines an 8-byte discovery record:

- `sig_ver`: version in the low byte and signature in the upper 24 bits. The signature value is `0x484353 << 8`.
- `fw_status_loc`: a packed location whose low two bits select address space (`PCIE_CFG`, `GRC`, `BAR0`, or `BAR1`) and whose upper bits give the aligned offset.

`HCOMM_STATUS_STRUCT_LOC` is the fixed GRC address `0x31001F0` used to find the `hcomm_status` record. Matching BNXT health code maps this address, checks the signature, reads `fw_status_loc`, and falls back to a known P5 BAR0 status register when the signature is absent on supported chips. It then uses `FW_STATUS_REG_CRASHED_NO_MASTER` to trigger OP-TEE firmware reset. BNGE should preserve the same interpretation when adding or auditing firmware health handling.

## Control Flow and Data Flow

These declarations do not execute by themselves; their control flow is imposed by HWRM request helpers:

1. Driver code allocates a typed request with an HWRM helper and command ID such as `HWRM_NVM_GET_VARIABLE`, `HWRM_NVM_DEFRAG`, or `HWRM_SELFTEST_EXEC`.
2. The helper initializes common header fields and points `resp_addr` at a DMA response buffer.
3. The caller fills command-specific fields from this chunk: DMA data addresses, option selectors, flags, tag IDs, profile metadata, test masks, completion ring IDs, or defrag flags.
4. The request is sent to firmware, usually synchronously.
5. The driver reads the typed output only after successful HWRM completion and valid response ownership, then maps `error_code`, command-specific `cmd_err`, and result/status fields into kernel errors or user-visible diagnostics.

Doorbell flow is MMIO rather than HWRM:

1. Ring setup assigns each queue/ring an XID and a doorbell BAR address.
2. The driver precomputes the stable `db_key64` fields: path, type, XID, and valid bit.
3. Runtime TX/RX/CQ/NQ code ORs in the ring index, epoch/toggle fields, and arm/mask type as needed.
4. A 64-bit MMIO write notifies hardware/firmware of new producer index or interrupt-arm state.

Firmware health flow is register-based:

1. The host maps `HCOMM_STATUS_STRUCT_LOC`.
2. It validates the `hcomm_status` signature/version.
3. It decodes the real firmware status register address space and offset.
4. Periodic or recovery code reads `fw_status_reg` bits and decides whether firmware is healthy, recovering, crashed, or requesting an out-of-band reset path.

## State and Persistence Behavior

Most structs in this chunk are transient command or MMIO formats, but several operations affect persistent device state:

- NVM variable writes persist firmware options across driver reload and device reset unless sent as validate-only or factory-default operations.
- `FORCE_FLUSH` on NVM set/profile requests and explicit `HWRM_NVM_FLUSH` control when staged NVM changes are committed to nonvolatile storage.
- NVM defrag reorganizes persistent NVM directory/storage layout to recover space; failure can block firmware package updates.
- VPD field writes update device identity/configuration fields that can be observed by firmware, PCI VPD tooling, or inventory systems.
- NVM install/update result fields report whether the newly installed package requires a PCI function reset or full power cycle before becoming active.
- Self-test commands are diagnostic and should not normally persist state, but offline tests can disrupt link or device operation while running.
- Doorbell writes update hardware-visible queue producer/arm state and are not persistent beyond queue lifetime.
- Firmware status and host-communication records are device runtime state; they survive long enough for crash/recovery coordination but are not normal configuration storage.

## Dependencies and Integration Points

This chunk depends on kernel fixed-width and endian types such as `u8`, `u32`, `u64`, `__le16`, `__le32`, and `__le64`. It also depends on the HWRM command ID namespace defined earlier in the same header, including `HWRM_SELFTEST_QLIST`, `HWRM_SELFTEST_EXEC`, `HWRM_SELFTEST_IRQ`, `HWRM_NVM_SET_PROFILE`, `HWRM_NVM_GET_VPD_FIELD_INFO`, `HWRM_NVM_SET_VPD_FIELD_INFO`, `HWRM_NVM_DEFRAG`, `HWRM_NVM_FLUSH`, `HWRM_NVM_GET_VARIABLE`, `HWRM_NVM_SET_VARIABLE`, and `HWRM_NVM_INSTALL_UPDATE`.

Driver integration points include:

- `drivers/net/ethernet/broadcom/bnge/bnge_hwrm.c` and `bnge_hwrm_lib.c`, which allocate/send HWRM requests and include this HSI header.
- `drivers/net/ethernet/broadcom/bnge/bnge_db.h`, `bnge.h`, `bnge_netdev.c`, and `bnge_txrx.c`, which mirror the doorbell layouts and issue 64-bit doorbell writes.
- `drivers/net/ethernet/broadcom/bnge/bnge_devlink.c`, which already consumes nearby NVM device-info HWRM structs and could use the variable/VPD/profile definitions for additional persistent devlink controls.
- Matching `drivers/net/ethernet/broadcom/bnxt` code, which is not BNGE code but is a strong in-tree reference for the same Broadcom HWRM ABI: devlink NVM get/set variable handling, NVM defrag during firmware package resize, ethtool self-test qlist/exec/irq, and firmware health status discovery through `hcomm_status`.
- RDMA/RoCE integration through the `EROCE` profile type and the doorbell path selector values for `ROCE` versus `L2`.

## Risks

- ABI drift is the main risk. Field offsets, sizes, endian annotations, and bit masks must exactly match firmware; changing a struct member or constant can silently break firmware commands.
- The chunk starts mid-struct, so merge/reconciliation should include the preceding `hwrm_nvm_install_update_input/output` fields to give complete install/update semantics.
- NVM write/profile/VPD commands can permanently alter device state. Callers need privilege checks, accurate `data_len` units, correct DMA direction, and careful handling of `FORCE_FLUSH`, factory-default, validation, and encryption/authentication flags.
- `dimensions` and `index_0..index_3` are easy to misuse. A wrong index can read or modify a different port/function/profile instance than intended.
- Command-specific error codes must not be flattened too early. For example, variable-not-found often means unsupported option, while access-denied means an admin/privilege issue.
- Defrag and install/update operations can be long-running and disruptive. Callers need suitable HWRM timeouts and must handle no-space, anti-rollback, voltage-regulator, authentication, and reset-required outcomes distinctly.
- Self-tests may require PF privileges and offline state. Running offline diagnostics while RDMA, traffic, or auxiliary devices are active can cause false failures or operational disruption.
- Doorbell bit composition must remain synchronized with the HSI definitions. Incorrect XID, path, type, epoch, toggle, valid, or mask bits can stall queues, drop completions, or arm interrupts incorrectly.
- Atomicity of 64-bit doorbell writes matters on 32-bit systems; bypassing `bnge_writeq()` can expose torn writes.
- Firmware status location decoding requires validating `hcomm_status` signature/version and address space before reading; otherwise recovery code may read the wrong register and misclassify firmware health.

## Test and Validation Signals

Useful validation for this chunk is ABI and integration oriented:

- Build BNGE and any code including `<linux/bnge/hsi.h>` with warnings enabled; this catches missing type definitions and incompatible struct references.
- Add or run compile-time layout checks if available for generated HSI headers, especially the documented sizes: 16-byte flush outputs, 40-byte variable requests, 272-byte VPD get output, 280-byte selftest qlist output, and 8-byte doorbell/status records.
- Exercise HWRM NVM get/set variable paths on hardware or firmware simulation with valid, nonexistent, access-denied, invalid-index, and short-length options, verifying command-error translation.
- Test NVM defrag as part of a firmware package update flow where update-area resize first returns no space, then succeeds after one defrag retry.
- Validate VPD get with known two-byte tags and invalid tags; confirm returned `data_len` never exceeds the 256-byte output buffer.
- Validate profile set in both `VALIDATE_ONLY` and real write modes, including error-index reporting for a deliberately invalid sub-block.
- Run firmware self-test query and execution paths, checking that available/offline bitmasks, timeout, test names, requested tests, and success masks remain consistent.
- Run IRQ self-test against all completion rings and verify failures identify ring allocation or interrupt mapping issues rather than generic HWRM transport failure.
- Stress TX/RX/CQ/NQ doorbells under traffic and interrupt moderation; watch for queue stalls, missed completions, or unexpected debug/doorbell drop events.
- Simulate or observe firmware health transitions: ready, recovering, crashdump ongoing/complete, shutdown, and crashed-no-master. Confirm the host-communication locator maps the intended address space and recovery code chooses the correct reset path.

## Cross-Chunk Notes

The first visible lines belong to `hwrm_nvm_install_update_output`, whose request and initial output fields start in the previous chunk. Earlier chunks also define the HWRM command IDs and generic input/output header conventions used by every command here. The final per-file research pass should merge this tail with the earlier NVM directory/update sections and with BNGE driver usage notes so the complete report distinguishes BNGE-specific consumers from matching BNXT reference integrations.
