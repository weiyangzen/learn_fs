# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/bmi.h

Purpose: Wire-format and API header for ath10k's Bootloader Messaging Interface.

Important APIs/types/functions: Defines transfer sizes (`BMI_MAX_DATA_SIZE`, command buffer sizes, large transfer sizes), `enum bmi_cmd_id`, board/OTP parameter masks, `struct bmi_cmd`, `union bmi_resp`, `struct bmi_target_info`, segmented file headers/metadata, timeout and CE IDs, and prototypes for all BMI operations. Convenience macros `ath10k_bmi_read32` and `ath10k_bmi_write32` access host-interest items through BMI memory transfers.

Control flow: Callers construct one `struct bmi_cmd` with command ID and command-specific union member, then receive a matching `union bmi_resp`. Segmented file constants describe firmware/board-data streams with special high-bit length markers for done, board data, begin address, and immediate execution.

State/persistence: Defines protocol messages that mutate target boot memory/register/app-start state but keeps no host state itself.

Dependencies/integration: Includes `core.h` for `struct ath10k`, host-interest helpers, HZ timeout definitions, and hardware boot code. BMI command structures are shared conceptually with target bootloader firmware and must remain packed/little-endian.

Risks: Flexible arrays and packed unions require exact length calculations by callers. Command IDs alias old names (`READ_SOC_REGISTER`/`READ_SOC_WORD`) and must stay compatible with firmware. Buffer size constants cap transfer chunking; exceeding them would corrupt stack command buffers.

Test signals: Compile-time structure use, firmware download, BMI register/memory readbacks, segmented file processing, and cross-bus boot tests exercise this header.
