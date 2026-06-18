# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_nvm.c

## Purpose

`i40e_nvm.c` implements i40e non-volatile memory and Shadow RAM access for the Intel 40GbE driver. It initializes NVM metadata, arbitrates firmware-owned NVM resources through AdminQ, reads and writes Shadow RAM either through `GLNVM_SRCTL` or AdminQ, calculates and validates the software checksum, and exposes the NVM update command state machine used by management/update paths. The file treats "NVM" as FLASH mapped through Shadow RAM and centralizes the locking and firmware completion behavior required to avoid corrupting persistent adapter configuration.

## Important APIs, Types, and Functions

- `i40e_init_nvm()` reads `I40E_GLNVM_GENS` to determine Shadow RAM size and `I40E_GLNVM_FLA` to distinguish normal from blank programming mode. Blank mode sets `hw->nvm.blank_nvm_mode` and returns `-EIO`.
- `i40e_acquire_nvm()` and `i40e_release_nvm()` wrap `i40e_aq_request_resource()` and `i40e_aq_release_resource()` for `I40E_NVM_RESOURCE_ID`, including wait/retry logic based on `I40E_GLVFGEN_TIMER` and firmware-provided timeout.
- `i40e_read_nvm_word()`, `i40e_read_nvm_buffer()`, and `i40e_read_nvm_module_data()` are the exported read APIs. They select AdminQ or SRCTL access based on `I40E_HW_CAP_AQ_SRCTL_ACCESS_ENABLE` and acquire a read lock when `I40E_HW_CAP_NVM_READ_REQUIRES_LOCK` is set.
- `i40e_update_nvm_checksum()` and `i40e_validate_nvm_checksum()` use `i40e_calc_nvm_checksum()` to maintain the Shadow RAM checksum word while skipping VPD and PCIe alternate auto-load regions.
- `i40e_nvmupd_command()` is the public dispatcher for update commands described by `struct i40e_nvm_access`; it delegates to `i40e_nvmupd_state_init()`, `i40e_nvmupd_state_reading()`, and `i40e_nvmupd_state_writing()`.
- `i40e_nvmupd_check_wait_event()` and `i40e_nvmupd_clear_wait_state()` bridge asynchronous AdminQ events back into the NVM update state machine.

## Control Flow

Initialization first calculates `hw->nvm.sr_size` from a register-encoded power-of-two KB value and rejects unsupported blank NVM mode. Most normal reads enter through `i40e_read_nvm_word()` or `i40e_read_nvm_buffer()`: optional NVM resource acquisition, dispatch to an internal caller-locking helper, then release. SRCTL reads poll the done bit, write address plus start, poll again, and extract read data. AdminQ reads validate that a single command does not exceed one sector or cross a sector boundary, then issue `i40e_aq_read_nvm()` with byte offsets.

Buffer AdminQ reads split the caller request into sector-limited transactions and only set `last_command` on the final chunk. Module-data reads first resolve a module pointer, reject invalid or outside-Shadow-RAM pointers, then read a relative pointer and fetch the final data buffer.

Checksum flow allocates one sector-sized virtual buffer, reads VPD and PCIe alternate module pointers, iterates every Shadow RAM word, reloads a sector buffer at each sector boundary, skips the checksum word plus the two variable regions, and returns `I40E_SR_SW_CHECKSUM_BASE - sum`. Validation holds the NVM read lock across checksum calculation and checksum-word read.

NVM update flow starts by validating `cmd->command`, transaction bits, module pointer bits, and data size. Single-transaction reads/writes acquire and release around one command. Multi-command read starts in `INIT`, acquires NVM, transitions to `READING`, continues with `READ_CON`, and releases on `READ_LCB`. Multi-command write starts with `WRITE_SNT`, waits for an AdminQ completion, transitions into `WRITING`, and continues with `WRITE_CON`, `WRITE_LCB`, or checksum commands. Wait states reject most commands with `-EBUSY`; an offset of `0xffff` cancels/clears a wait. AdminQ execute commands optionally stash the expected follow-up opcode in `hw->nvm_wait_opcode`.

## State and Persistence Behavior

The persistent hardware state is the adapter NVM/FLASH content and Shadow RAM checksum. In-memory state lives primarily in `struct i40e_hw`: `hw->nvm.sr_size`, `timeout`, `blank_nvm_mode`, `hw_semaphore_timeout`, AdminQ write-back descriptors, NVM update state, wait opcode, release-on-done flag, event descriptor, and temporary NVM buffer. The NVM semaphore is firmware-global and can be held across multi-command transactions; failure to release it blocks other PFs and management agents. The update state machine is intentionally sticky across calls so user space can stream update chunks and poll completion status.

## Dependencies and Integration Points

This file depends on `i40e_prototype.h`, `i40e_alloc.h`, `i40e_type.h` definitions, AdminQ commands from common i40e code, register constants from `i40e_register.h`, Linux delay helpers, bitfield extraction, and driver debug logging. It integrates with firmware through AdminQ NVM read/update/erase/resource commands and with interrupt/AdminQ event handling through `i40e_nvmupd_check_wait_event()`. Other i40e code calls the exported NVM APIs for probe-time identity/configuration reads, flash update, checksum validation, and management-tool NVM update operations.

## Risks

- NVM update correctness depends on exact state transitions and AdminQ event delivery. Missing `i40e_nvmupd_check_wait_event()` calls can leave the driver in wait state or keep the NVM semaphore held.
- `i40e_nvmupd_get_aq_result()` assumes `hw->nvm_buff.va` is valid if a data remainder exists. Callers must only request result bytes matching prior AdminQ execution.
- The read/write helpers log but do not always immediately return distinct `-EINVAL` for sector/limit violations inside the low-level AdminQ helper; callers see the initialized `-EIO`.
- Multi-write retry on firmware `EBUSY` relies on `hw->nvm.hw_semaphore_timeout` and one retry. Timer wrap or stale semaphore timeout would affect recovery.
- Checksum calculation trusts module pointers enough to define skipped windows. Corrupt pointers can cause incorrect skip coverage even though reads themselves are bounded by Shadow RAM size.
- Direct SRCTL path has no outer semaphore in `i40e_read_nvm_buffer()` unless AdminQ access is enabled; this matches capability expectations but is sensitive to hardware generation.

## Test Signals

Useful validation includes successful probe with NVM init in normal mode, `ethtool -e` or equivalent Shadow RAM reads across sector boundaries, checksum validate/update on known-good adapters, firmware flash update flows covering single and multi-command read/write/checksum transactions, AdminQ event timeout/cancel paths, and concurrent PF/resource acquisition contention. Kernel logs with `I40E_DEBUG_NVM` enabled should show no stuck `I40E_NVMUPD_STATE_*_WAIT`, no repeated semaphore timeout, and no checksum mismatch after update.
