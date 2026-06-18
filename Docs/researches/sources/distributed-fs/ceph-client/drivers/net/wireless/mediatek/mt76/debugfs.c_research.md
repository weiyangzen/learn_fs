# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/debugfs.c

Purpose: provides common mt76 debugfs helpers for register access, queue inspection, NAPI threading control, EEPROM/OTP blobs, and formatted diagnostic arrays.

Important APIs/functions: exports `mt76_queues_read`, `mt76_seq_puts_array`, and `mt76_register_debugfs_fops`. Internal debugfs accessors implement `regval` read/write through `__mt76_rr/__mt76_wr`, `napi_threaded` get/set through `dev_set_threaded`, and RX queue status via a seqfile.

Control flow: driver code calls `mt76_register_debugfs_fops` with a PHY and optional register fops. The helper creates an `mt76` directory under the wiphy debugfs dir, exposes `led_pin`, `regidx`, `regval`, `napi_threaded`, `eeprom`, optional `otp`, and `rx-queues`. The queue readers print head/tail/queued values for TX and RX queues; RX queue displayed queued count is adjusted for USB because its software/hardware accounting is inverted.

State and persistence: debugfs files expose mutable runtime fields such as `dev->debugfs_reg`, `phy->leds.pin`, and `dev->napi_dev->threaded`. EEPROM and OTP are exposed as read-only blobs backed by driver memory. Changes do not persist across driver reload except where hardware/EEPROM data is inherently persistent.

Dependencies and integration: depends on Linux debugfs, seq_file, dummy netdev NAPI state, mt76 register accessors, queue structures, and wiphy debugfs directories. Chip drivers can reuse queue readers in their own debugfs files.

Risks: `regval` is raw register access; writing arbitrary addresses can disturb hardware and should remain privileged debugfs. `napi_threaded` supports MMIO only and returns `-EOPNOTSUPP` otherwise. `debugfs_create_file_unsafe` assumes debugfs lifetime is tied to device cleanup. Queue snapshots are not globally locked and are diagnostic rather than transactional.

Test signals: verify debugfs directory creation for each PHY, register read/write using `regidx/regval`, NAPI threaded toggling on MMIO and rejection on non-MMIO, EEPROM/OTP blob readability, and queue readers under active traffic without crashes.
