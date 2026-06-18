<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umc.c

## Purpose
`amdgpu_umc.c` implements common UMC RAS orchestration: memory error address conversion, bad-page retirement, poison-consumption handling, ECC interrupt dispatch, channel iteration, ECC logging, and PA/MCA address translation glue. Version-specific UMC details are delegated through function pointers or IP-specific helpers.

## Important APIs, Types, And Functions
`amdgpu_umc_page_retirement_mca` converts an MCA error address and records retired pages. `amdgpu_umc_handle_bad_pages` queries error counts/addresses from SMU firmware, direct hardware callbacks, or RAS EEPROM, then saves bad pages and notifies DPM of bad-page/channel counts. `amdgpu_umc_pasid_poison_handler` handles poison events with optional PASID callbacks and reset policy, routing to direct retirement, UniRAS manager, deferred page-retirement queue, SR-IOV hooks, or CPU-connected/APU reset-only handling. `amdgpu_umc_ras_sw_init` and `amdgpu_umc_ras_late_init` register the RAS block and ECC IRQ. `amdgpu_umc_process_ecc_irq` and `amdgpu_umc_uniras_process_ecc_irq` dispatch interrupts. Utility APIs include `amdgpu_umc_fill_error_record`, `amdgpu_umc_loop_channels`, `amdgpu_umc_update_ecc_status`, `amdgpu_umc_logs_ecc_err`, `amdgpu_umc_lookup_bad_pages_in_a_row`, `amdgpu_umc_mca_to_addr`, and `amdgpu_umc_pa2mca`.

## Control Flow
On ECC/poison events, callers reach `amdgpu_umc_poison_handler` or `amdgpu_umc_pasid_poison_handler`. Non-SR-IOV pre-UMC12 devices do immediate page retirement and aggregate counts into the UMC RAS manager. UniRAS-enabled devices package interrupt info for the central RAS manager. Other devices enqueue poison requests and wake the page-retirement worker. SR-IOV delegates to virtualization ops.

Page retirement initializes `ras_err_data`, allocates an error-address array sized by `adev->umc.max_ras_err_cnt_per_query`, runs conversion/query callbacks, adds bad pages if the threshold allows, saves EEPROM state, and may trigger GPU reset for uncorrectable/deferred errors or RMA state. Channel iteration walks active AIDs using `active_mask`, node/UMC/channel geometry, or the older flat loops.

## State And Persistence
UMC state is held under `adev->umc`: geometry, active mask, channel offsets, retire unit, RAS callbacks, current `ras_if`, flip-bit data, and last error count. Persistent bad-page data lives in the global RAS context EEPROM control and bad-page tables. `con->page_retirement_lock`, workqueue counters, `gpu_reset_flags`, channel-update flags, and ECC radix trees coordinate longer-lived RAS behavior.

## Dependencies And Integration Points
The file depends on RAS manager APIs, SMU/DPM ECC queries, PSP RAS address translation, KFD SRAM ECC flagging, virtualization RAS hooks, IRQ dispatch, radix tree tags, and UMC v6.7-specific address conversion. It is the common layer between hardware/IP-specific UMC callbacks and driver-wide page retirement/reset policy.

## Risks
Allocation and clearing of `err_data->err_addr` is repeated in several paths, so double allocation/leak risk should be watched. The code intentionally calls query callbacks even when allocation fails to clear hardware status; tests must verify callback behavior with null storage. Reset decisions combine `reset`, UE/DE counts, and RMA state, so incorrect counts can over-reset or miss required recovery. Address conversion support is version-limited in the direct helper and otherwise delegated; unsupported versions can return success in some callback-free paths.

## Test Signals
Inject CE/UE/DE errors through direct and firmware query modes, validate bad-page EEPROM updates, exercise no-memory paths while confirming hardware status clears, cover SR-IOV and UniRAS routing, test active-mask channel iteration on multi-AID devices, verify PASID poison callbacks and reset policies, and validate PA-to-MCA/MCA-to-PA conversion for supported NPS modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umc.c -->
