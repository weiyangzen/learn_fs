# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ibm-cffps.c

Purpose: PMBus driver for IBM Common Form Factor power supplies. It supports CFFPS1/CFFPS2 variants, manufacturer-specific status mapping, 12V current-share monitoring, debugfs maintenance files, input history retrieval, and LED control.

Important APIs/types/functions: `struct ibm_cffps` stores version, I2C client, input-history buffer, debugfs entry indexes, LED name/state, and LED class device. `ibm_cffps_read_byte_data()` and `ibm_cffps_read_word_data()` merge manufacturer-specific fault bits into standard PMBus status and expose virtual VMON from `CFFPS_12VCS_VOUT_CMD`. Debugfs handlers read max power, CCIN, firmware version, on/off config, and long input history via raw I2C transfer. LED callbacks write `CFFPS_SYS_CONFIG_CMD`. `ibm_cffps_probe()` detects unknown variants from CCIN/MFR ID, runs PMBus probe, then optionally registers LED and debugfs.

Control flow: probe determines variant from I2C/OF match or auto-detection, sets PMBus platform flags `PMBUS_SKIP_STATUS_CHECK | PMBUS_NO_CAPABILITY`, calls `pmbus_do_probe()` with version-specific descriptors, then allocates optional private state. LED class registration writes initial LED off. Debugfs files use PMBus locks and page selection before raw SMBus/I2C commands. Input history uses raw I2C because the payload exceeds SMBus block length.

State and persistence: PMBus core owns hwmon state after probe. Optional state includes LED brightness/blink mode and cached input-history bytes for debugfs reads. Hardware LED state and on/off config persist in PSU registers. Debugfs compatibility symlink preserves old naming.

Dependencies and integration: depends on PMBus core lock/page helpers, I2C raw transfer, debugfs, LED class, OF/I2C matching, bitfields, and manufacturer PMBus commands. Kconfig requires `LEDS_CLASS`.

Risks: optional allocation failure after PMBus probe silently disables LED/debugfs but leaves hwmon working. Auto-detection relies on CCIN version/revision and manufacturer prefixes. Debugfs write to `on_off_config` accepts one raw byte from userspace. Raw input-history transfer must hold PMBus lock and page zero to avoid racing with core operations.

Test signals: cffps1/cffps2 auto-detection, status bit mapping from `STATUS_MFR_SPECIFIC`, VMON reading, LED on/off/blink behavior, debugfs files and input history, operation without debugfs/LED allocation, and PMBus lock correctness under concurrent reads.
