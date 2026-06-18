# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mcu.h

Purpose: Defines the MT7601U MCU register addresses, memory map bases, command ids, function ids, power modes, calibration ids, and exported MCU helper prototypes. It is the contract between firmware command construction in `mcu.c` and call sites such as PHY calibration.

Important APIs and types: `enum mcu_cmd` maps in-band firmware command types such as `CMD_FUN_SET_OP`, `CMD_BURST_WRITE`, `CMD_RANDOM_WRITE`, and `CMD_CALIBRATION_OP`. `enum mcu_function` defines function-select ids used by queue selection and TSSI setup. `enum mcu_calibrate` names calibration operations including R, DCOC, LOFT, TXIQ, RXIQ, TXDCOC, BW, and DPD. Constants such as `MT_MCU_IVB_SIZE`, `MT_MCU_DLM_OFFSET`, `MT_MCU_MEMMAP_BBP`, and `INBAND_PACKET_MAX_LEN` control firmware upload and in-band register access.

Control flow: This header does not execute logic, but its constants drive command payload layout and maximum command chunking in `mcu.c`. `MT_MCU_MEMMAP_BBP` and `MT_MCU_MEMMAP_RF` distinguish BBP/RF write spaces passed to MCU random-write commands.

State and persistence: It declares no persistent state. Its ids are persisted indirectly in firmware-visible command packets and calibration requests.

Dependencies and integration points: Forward-declares `struct mt7601u_dev` and exports `mt7601u_mcu_init()`, `mt7601u_mcu_cmd_init()`, `mt7601u_mcu_cmd_deinit()`, `mt7601u_mcu_calibrate()`, and `mt7601u_mcu_tssi_read_kick()`. Included by `mcu.c`, `phy.c`, and any code that needs firmware-mediated operations.

Risks: Command id values are firmware ABI. Renumbering or mixing memory map bases would silently target the wrong firmware operation or hardware register space. `INBAND_PACKET_MAX_LEN` must remain consistent with firmware command parsing limits.

Test signals: Build coverage catches missing prototypes. Runtime signals include successful firmware command initialization, calibration commands, and batch register writes that honor the packet maximum.
