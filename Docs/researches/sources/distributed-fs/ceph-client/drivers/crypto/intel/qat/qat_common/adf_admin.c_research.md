# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_admin.c

## Purpose
This file implements synchronous admin-message communication between the host driver and QAT firmware. It allocates DMA mailboxes, writes admin request/response addresses to CSRs, serializes messages, initializes firmware constants, reads capabilities/counters/PM/CNV/TL/RL/SVN data, and sends firmware init commands.

## Important APIs, Types, And Functions
Key public APIs include `adf_init_admin_comms()`, `adf_exit_admin_comms()`, `adf_send_admin_init()`, `adf_init_admin_pm()`, `adf_get_pm_info()`, `adf_get_fw_timestamp()`, `adf_get_ae_fw_counters()`, `adf_send_admin_tim_sync()`, `adf_send_admin_hb_timer()`, `adf_get_cnv_stats()`, `adf_send_admin_tl_start()`, `adf_send_admin_tl_stop()`, rate-limit commands, and anti-rollback SVN query/commit helpers. `struct adf_admin_comms` stores DMA buffers, constant-table buffer, mailbox MMIO address, and a mutex.

## Control Flow
`adf_init_admin_comms()` allocates coherent pages for request/response messages and a 1 KiB constants table, copies `const_tab`, gets generation-specific admin CSR offsets, and programs admin message address registers. `adf_put_admin_msg_sync()` locks, writes one 32-byte request for a target AE, signals mailbox ownership, polls for firmware clearing, then copies the response. `adf_send_admin()` iterates over an AE mask. `adf_send_admin_init()` sets constants, optionally initializes DC chaining, gathers DC/FW capabilities, then initializes AEs.

## State And Persistence Behavior
Admin state is per-device volatile memory in `accel_dev->admin`. Coherent DMA buffers persist from admin init to exit. Firmware capability fields and extended DC capabilities are cached in `hw_device`.

## Dependencies And Integration Points
It depends on hardware-data admin offsets, MMIO CSR macros, DMA APIs, QAT firmware admin message structures, config services, heartbeat, anti-rollback, PM/TL/RL users, and the common init sequence.

## Risks
The admin mutex serializes all admin commands; timeouts or firmware status failures return coarse errors. AE masks must avoid targeting absent/admin-only engines incorrectly. The constant table is large static data and must remain aligned. SVN retry behavior affects anti-rollback workflows.

## Test Signals
Successful device init, firmware capabilities populated, DC capabilities visible, AE counters in debugfs, heartbeat timer programming, PM info reads, CNV stats reads, TL/RL admin operations, anti-rollback SVN query/commit, and timeout handling on broken firmware.
