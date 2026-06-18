# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_hw.h

## Purpose

`qlcnic_83xx_hw.h` declares the 83xx/84xx hardware interface for qlcnic. It provides BAR/register offsets, mailbox payload layouts, firmware image constants, reset/IDC data structures, mailbox/AEN state definitions, link/LED/pause/statistics/flash constants, operation prototypes, and helper macros used by `qlcnic_83xx_hw.c`, 83xx initialization, vNIC, minidump, ethtool, and common qlcnic code.

It is the hardware-specific ABI boundary between the common qlcnic driver and 83xx firmware/register semantics.

## Important APIs, Types, And Constants

Register and hardware constants:

- BAR and CRB window definitions: `QLCNIC_83XX_BAR0_LENGTH`, `QLC_83XX_CRB_WIN_BASE`, `QLC_83XX_CRB_WIN_FUNC()`.
- Semaphore/lock registers: `QLC_83XX_SEM_LOCK_FUNC()`, `QLC_83XX_SEM_UNLOCK_FUNC()`, driver lock recovery constants.
- Link and legacy interrupt registers: `QLC_83XX_LINK_STATE()`, `QLC_83XX_LINK_SPEED()`, `QLC_83XX_INTX_PTR`, `QLC_83XX_INTX_TRGR`, `QLC_83XX_INTX_MASK`.
- PEG status, pause registers, PEG PC status registers, and firmware image constants such as `QLC_83XX_FW_FILE_NAME`, `QLC_84XX_FW_FILE_NAME`, and boot-from-file/flash markers.

Mailbox payload structs:

- `struct qlcnic_sds_mbx`: status descriptor ring DMA address, ring size, interrupt ID/value.
- `struct qlcnic_rds_mbx`: regular and jumbo receive descriptor ring DMA addresses, buffer sizes, and ring lengths.
- `struct __host_producer_mbx`: firmware-returned host producer offsets for regular and jumbo rings.
- `struct qlcnic_rcv_mbx_out` and `struct qlcnic_add_rings_mbx_out`: receive context creation/add-rings response fields, including context ID, state, vport, physical port, host consumer offsets, and producer offsets.
- `struct qlcnic_tx_mbx` and `struct qlcnic_tx_mbx_out`: transmit context request and response layouts.
- `struct qlcnic_intrpt_config`: interrupt type/enabled/id/source metadata.
- `struct qlcnic_macvlan_mbx`: endian-specific MAC/VLAN mailbox payload.

Firmware/reset/IDC state:

- `struct qlc_83xx_fw_info`: firmware pointer plus selected firmware file name.
- `struct qlc_83xx_reset`: reset sequence template state, offsets, array scratch, and completion markers.
- `struct qlc_83xx_idc`: inter-driver communication state machine callback, timers, status bits, error/dump flags, current/previous/vNIC states, wait limits, quiesce/delay flags, and state names.
- `enum qlcnic_83xx_states`: firmware/device IDC states from unknown/cold/init/ready through reset/quiescent/failed.
- IDC timing and capability constants such as `QLC_83XX_IDC_INIT_TIMEOUT_SECS`, `QLC_83XX_IDC_RESET_ACK_TIMEOUT_SECS`, `QLC_83XX_IDC_MAX_CNA_FUNCTIONS`, and `QLC_83XX_IDC_FLASH_PARAM_ADDR`.

Mailbox and AEN macros:

- `QLCNIC_MBX_RSP()`, `QLCNIC_MBX_NUM_REGS()`, `QLCNIC_MBX_STATUS()`, `QLCNIC_MBX_HOST()`, and `QLCNIC_MBX_FW()`.
- `QLC_83XX_MBX_AEN_CNT`, `QLC_83XX_MBX_READY`, response states, and command types `QLC_83XX_MBX_CMD_WAIT`, `NO_WAIT`, and `BUSY_WAIT`.
- SFP/link decoding macros: `QLC_83XX_SFP_MODULE_TYPE()`, `QLC_83XX_CURRENT_LINK_SPEED()`, `QLC_83XX_LINK_PAUSE()`, `QLC_83XX_AUTONEG()`, and DCB/FEC/EEE bits.

Feature and configuration constants:

- LED constants `QLC_83XX_ENABLE_BEACON`, `QLC_83XX_LED_CONFIG`, and beacon on/off values.
- Link speed encodings and statistics register counts.
- Function privilege/op-mode macros `QLC_83XX_GET_FUNC_PRIVILEGE()`, `QLC_83XX_DEFAULT_OPMODE`, `QLC_83XX_PRIVLEGED_FUNC`, and `QLC_83XX_VIRTUAL_FUNC`.
- 83xx filter, multicast, unicast, SR-IOV, eSwitch, PVID strip, LRO/LSO/HW-LRO capability bits.

Flash constants:

- Flash register offsets, direct-window helpers, command signatures, read/write/erase modes, read retry counts, status-ready value, write-size bounds, polling delay, OEM command signatures, address temp values, and lock timeout.

Declared functions:

- Hardware ops: register access, mailbox commands, interrupt setup, function number, CAM/API locks, sysfs hooks, NAPI hooks, RX/TX context create/delete, NIC/PCI info, link events, promisc/RSS/LRO/coalescing, MAC/VLAN, MAC address, interrupts, flash access, IDC, vNIC, minidump helpers, ethtool diagnostics, AER, and memory write.
- Notable prototypes include `qlcnic_83xx_issue_cmd()`, `qlcnic_83xx_create_rx_ctx()`, `qlcnic_83xx_create_tx_ctx()`, `qlcnic_83xx_config_intrpt()`, `qlcnic_83xx_lock_flash()`, `qlcnic_83xx_idc_init()`, `qlcnic_83xx_aer_reset()`, and `qlcnic_ms_mem_write128()`.

## Control Flow And State Behavior

The header enables several hardware flows:

1. Initialization code maps BAR0, assigns register tables, detects function/op mode, loads firmware or boots from flash, initializes IDC state, and creates mailbox work state.
2. Context creation packs `qlcnic_sds_mbx`, `qlcnic_rds_mbx`, and `qlcnic_tx_mbx` into mailbox register arrays at fixed offsets. Firmware responds with context IDs and CRB offsets through the corresponding out structs.
3. Interrupt setup stores each interrupt in `qlcnic_intrpt_config`; firmware later fills the source register offset.
4. Mailbox commands use response-state enums, host/FW register macros, and command type to select blocking, nonblocking, or busy-wait behavior.
5. Link, LED, pause, loopback, statistics, SFP, DCB, and autoneg state are encoded in mailbox response words decoded by macros in this header.
6. Flash operations use the flash register constants and status polling values to serialize direct-window reads, writes, sector erase, and descriptor-table reads.
7. IDC state persists across polling work and firmware reset transitions in `struct qlc_83xx_idc`, while `struct qlc_83xx_reset` holds reset template progress.

Persistent state represented by this header includes firmware images in flash, flash descriptor table contents cached elsewhere, IDC control parameters in flash, and device/driver presence registers. Runtime state includes mailbox command queues, interrupt config, reset sequence progress, IDC state, and port/link configuration values.

## Dependencies And Integration Points

This header includes Linux types and Ethernet helpers, plus `qlcnic_hw.h`. It forward-declares `struct qlcnic_adapter` and `struct qlcnic_fw_dump` while relying on full definitions from `qlcnic.h` in implementation files.

Integration points:

- `qlcnic_83xx_hw.c` implements most prototypes and uses all mailbox/register constants.
- `qlcnic_83xx_init.c` and `qlcnic_83xx_vnic.c` use IDC, reset, firmware, and vNIC declarations.
- Common qlcnic code calls these functions through `struct qlcnic_hardware_ops` and `struct qlcnic_nic_template`.
- Etthtool code uses link, pause, LED, register, flash, interrupt, and loopback prototypes.
- Minidump code uses saved-state and template helper prototypes.
- SR-IOV code depends on 83xx PF/VF mode and mailbox behavior.

## Risks And Edge Cases

- Many structs use explicit endian-specific field ordering. Any change must preserve firmware mailbox register layout on both little- and big-endian builds.
- Mailbox register count and fixed offsets such as `QLC_83XX_HOST_SDS_MBX_IDX` and `QLCNIC_HOST_RDS_MBX_IDX` must match firmware expectations and metadata in the implementation.
- Function privilege macros assume two bits per function in the op-mode register; extending function counts or changing register format requires coordinated updates.
- Flash command signatures and polling values are hardware-specific. Incorrect constants can hang flash operations or corrupt persistent firmware/config data.
- Driver-lock recovery constants control force-unlock behavior across PCI functions. Aggressive recovery can break another active function.
- Link/SFP decoding macros pack several concepts into mailbox words; wrong shifts advertise incorrect speed, port type, pause, or module state to ethtool.
- Header prototypes expose many functions across files; changing signatures requires coordinated updates across common, 83xx init, vNIC, SR-IOV, ethtool, and minidump code.

## Test Signals

- Compile tests on little- and big-endian configurations to catch mailbox struct layout issues.
- 83xx/84xx probe, firmware boot-from-flash and boot-from-file, IDC init/reset/quiesce paths.
- Mailbox context create/destroy tests validating register counts and response offsets.
- MSI-X/legacy interrupt registration and firmware interrupt add/delete.
- Etthtool link, pause, LED, stats, register dump, flash, loopback, and interrupt tests.
- Flash descriptor-table read, mfg-id read, and controlled write/erase validation on supported hardware.
- SR-IOV PF/VF and non-privileged function tests for op-mode decoding and mailbox interface ID routing.
- Firmware reset/AER/minidump paths using reset and saved-state helpers.
