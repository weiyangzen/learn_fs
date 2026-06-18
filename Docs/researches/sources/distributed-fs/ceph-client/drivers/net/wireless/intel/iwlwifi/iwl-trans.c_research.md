# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-trans.c

Purpose: Implements the common transport facade for iwlwifi, delegating hardware operations to PCIe/gen-specific backends while managing firmware state, host-command checks, restart escalation, opmode entry/leave, and exported TX/RX/control APIs.

Important APIs and functions: Exports allocation/free, `iwl_trans_send_cmd()`, TX command allocation/free, command-name lookup, opmode enter/leave, start/stop hardware/firmware, direct register/memory helpers, D3 suspend/resume, TX/reclaim/queue APIs, PNVM/reduce-power loading, PM/LTR queries, and restart-list cleanup. Static restart helpers track per-device restart history and schedule reprobe/reset work.

Control flow: Host commands are rejected during RF-kill unless allowed, during firmware error, or outside `FW_ALIVE`; command IDs are converted to wide format when needed before PCIe submission. Firmware start chooses the ucode image and gen-specific backend, then transitions to `FW_STARTED`; alive transitions to `FW_ALIVE`. Stop handles reset/dump races before backend stop and returns to `NO_FW`. Restart work dumps errors through opmode, checks pending reset, honors `fw_restart`, chooses SW reset/reprobe/TOP/function/product reset or backoff, then dispatches.

State and persistence: Mutates `trans->state`, `trans->status`, `trans->conf`, `trans->op_mode`, restart delayed work, top-reset flags, and global per-device restart history list. No on-disk persistence, but restart history persists while module is loaded.

Dependencies and integration points: Bridges opmode, firmware images, host command ABI, PCIe transport internals, gen2 context-info PNVM/reduce-power logic, module parameters, lockdep, workqueues, device reprobe, and TX queue backends.

Risks: State gating must prevent commands/TX after firmware errors or before alive. Restart escalation/backoff affects availability after repeated crashes. Stop/reset dump handshakes are race-prone. `iwl_trans_write_mem()` depends on NIC access and dword counts. Gen1/gen2 backend selection must match `mac_cfg->gen2`.

Test signals: Host command rejection matrix, wide-command ID conversion, firmware start/alive/stop transitions, reset escalation after repeated errors, top-reset support, opmode stop during pending reset, TX/reclaim state checks, PNVM/reduce-power load failures, D3 suspend/resume, and reprobe work cancellation on free.
