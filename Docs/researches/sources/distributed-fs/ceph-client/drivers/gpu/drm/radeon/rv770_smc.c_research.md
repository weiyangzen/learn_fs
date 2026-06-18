# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_smc.c

## Purpose
`rv770_smc.c` implements the host-side SMC SRAM, reset/clock, firmware-load, interrupt-vector, and mailbox-message operations used by RV770-family Radeon dynamic power management. It is the low-level transport layer beneath the DPM code: higher-level code prepares firmware blobs, SMC state tables, and soft-register values, while this file safely moves bytes and dwords into SMC address space and coordinates with the microcontroller through MMIO registers.

## Important APIs and functions
The file includes Linux firmware support plus Radeon core, RV770 register definitions, DPM declarations, SMC table declarations, AtomBIOS helpers, and firmware metadata. It defines static interrupt-vector byte arrays for RV770, RV730, RV710, RV740, Evergreen (`CEDAR`, `REDWOOD`, `JUNIPER`, `CYPRESS`/`HEMLOCK`), Northern Islands/BTC (`BARTS`, `TURKS`, `CAICOS`), and Cayman. `FIRST_SMC_INT_VECT_REG` and `FIRST_INT_VECT_S19` define the relevant high SMC vector/register area.

`rv770_set_smc_sram_address` is the private address gate: it requires 4-byte alignment, rejects dword accesses beyond `limit`, sets `SMC_SRAM_AUTO_INC_DIS`, and writes `SMC_SRAM_ADDR`. `rv770_copy_bytes_to_smc` copies an arbitrary byte count into SMC SRAM with big-endian dword packing and a read-modify-write tail for non-multiple-of-four lengths. It serializes access with `rdev->smc_idx_lock`. `rv770_program_interrupt_vectors` writes big-endian vector dwords into `SMC_ISR_FFD8_FFDB` and skips any vector data before `FIRST_SMC_INT_VECT_REG`.

Lifecycle helpers are direct MMIO bit updates: `rv770_start_smc`, `rv770_reset_smc`, `rv770_stop_smc_clock`, `rv770_start_smc_clock`, and `rv770_is_smc_running` manipulate or inspect `SMC_IO` bits `SMC_RST_N`, `SMC_CLK_EN`, and `SMC_STOP_MODE`. `rv770_send_msg_to_smc` writes a `PPSMC_Msg` into `SMC_MSG`, polls `HOST_SMC_RESP` up to `rdev->usec_timeout`, and returns a `PPSMC_Result`. `rv770_wait_for_smc_inactive` polls stop mode when the SMC is running. `rv770_clear_smc_sram` zeros the SRAM window in aligned dword steps. `rv770_load_smc_ucode` chooses per-family firmware start/size and interrupt-vector metadata, clears SRAM, copies `rdev->smc_fw->data`, and programs the vectors. `rv770_read_smc_sram_dword` and `rv770_write_smc_sram_dword` provide locked aligned dword accessors.

## Control flow
Firmware load starts by rejecting a missing `rdev->smc_fw`, clearing SRAM up to the caller-provided `limit`, selecting ucode and vector constants based on `rdev->family`, copying the firmware payload into SMC SRAM, then programming interrupt vectors. Unknown families log `DRM_ERROR` and call `BUG()`, reflecting that this path is only valid for known ASIC tables. Message flow first verifies the SMC is out of reset with its clock enabled, then writes the host message and busy-waits in microsecond increments for firmware response.

## State and persistence behavior
Persistent state lives in hardware: SMC SRAM contents, SMC interrupt-vector registers, `SMC_IO` reset/clock/stop bits, and `SMC_MSG` mailbox fields. Driver state consumed by this file includes `rdev->smc_fw`, `rdev->family`, `rdev->usec_timeout`, and `rdev->smc_idx_lock`. SRAM writes persist until cleared, overwritten, reset, or power-cycled, and DPM later relies on these contents for firmware execution and state-table interpretation.

## Dependencies and integration points
The implementation depends on register macros from `rv770d.h`, SMC ucode location/size constants from `radeon_ucode.h`, firmware ownership in `struct radeon_device`, and SMC message/result enums from `ppsmc.h` through `rv770_smc.h`. `rv770_dpm.c`, `cypress_dpm.c`, and later DPM code call these helpers to upload firmware, write state tables and soft registers, halt/resume the SMC, switch states, and inspect SRAM.

## Risks and test signals
High-risk areas are endianness, alignment, SRAM bounds, per-family ucode constants, interrupt-vector offsets, timeout handling, and lock coverage around the SMC SRAM index register. A bad copy or vector table can prevent DPM from starting; an incorrect limit can corrupt adjacent SMC data; a missing response can stall state transitions. Test signals include successful SMC firmware upload, `PPSMC_Result_OK` for halt/resume/state-switch messages, no `unknown asic` path, stable DPM enable/disable, suspend/resume, forced-level changes, and register/SRAM readback on hardware with RV7xx/Evergreen/NI/Cayman variants.
