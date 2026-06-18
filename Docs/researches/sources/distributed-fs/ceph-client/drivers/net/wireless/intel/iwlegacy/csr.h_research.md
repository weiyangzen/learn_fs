# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/csr.h

## Purpose
`csr.h` defines iwlegacy host-visible Control and Status Register (CSR) and Host Bus (HBUS) offsets and bit masks. It documents which registers are always PCI MMIO accessible and which HBUS registers are indirect access windows into internal memory or peripherals.

## Important APIs, Types, and Constants
- CSR offsets: `CSR_HW_IF_CONFIG_REG`, `CSR_INT`, `CSR_INT_MASK`, `CSR_FH_INT_STATUS`, `CSR_RESET`, `CSR_GP_CNTRL`, `CSR_HW_REV`, `CSR_EEPROM_REG`, `CSR_UCODE_DRV_GP*`, `CSR_LED_REG`, `CSR_DRAM_INT_TBL_REG`.
- Interrupt masks: `CSR_INT_BIT_FH_RX`, `CSR_INT_BIT_HW_ERR`, `CSR_INT_BIT_FH_TX`, `CSR_INT_BIT_SW_ERR`, `CSR_INT_BIT_RF_KILL`, `CSR_INT_BIT_WAKEUP`, `CSR_INT_BIT_ALIVE`, `CSR_INI_SET_MASK`, FH RX/TX masks for 3945 and 4965.
- Power and access bits: `CSR_GP_CNTRL_REG_FLAG_MAC_ACCESS_REQ`, `MAC_CLOCK_READY`, `GOING_TO_SLEEP`, `INIT_DONE`, `HW_RF_KILL_SW`.
- EEPROM bits: `CSR_EEPROM_REG_READ_VALID_MSK`, command/address/data masks, EEPROM signature masks.
- uCode mailbox bits: `CSR_UCODE_DRV_GP1_BIT_MAC_SLEEP`, `CSR_UCODE_SW_BIT_RFKILL`, `CSR_UCODE_DRV_GP1_BIT_CMD_BLOCKED`, CT-kill exit.
- HBUS windows: `HBUS_TARG_MEM_*` for SRAM, `HBUS_TARG_PRPH_*` for peripheral registers, `HBUS_TARG_WRPTR` for TX queue write pointer updates.

## Control Flow and Integration
CSR registers are accessed with raw `_il_rd()` and `_il_wr()` because the MAC does not need to be awake. Internal memory and PRPH windows under HBUS must be accessed through the higher-level access path after grabbing NIC access, because the target resources may be powered down. Interrupt handlers read/ack `CSR_INT` and `CSR_FH_INT_STATUS`, enable masks through `CSR_INT_MASK`, and use RF kill/CT kill bits to steer power/error handling.

## State and Persistence Behavior
The file is declarative; no state is stored here. The registers it describes expose persistent hardware state such as interrupt latch bits, RF kill state, EEPROM read data, firmware-driver mailbox state, reset state, and target memory access pointers. Many bits are write-one-to-clear or set/clear side-effect registers.

## Dependencies and Integration Points
`common.h` includes this header for inline register helpers and status macros. The implementation uses these constants in interrupt, EEPROM, APM, firmware load, RF kill, LED, and queue code. It pairs with `prph.h`, whose internal registers are accessed via the HBUS offsets defined here.

## Risks and Edge Cases
- CSR and HBUS have different access rules; mixing `_il_*` and `il_*` families can fail during low-power states.
- Interrupt bits are acknowledged by writing one, so careless writes can drop pending events.
- EEPROM reads require the device to be awake and initialized despite the register being in CSR space.
- MAC sleep, command-blocked, and RF kill mailbox bits are shared with firmware; ordering mistakes can strand queues or prevent recovery.

## Test Signals
Exercise interrupt enable/disable paths, EEPROM read polling, RF kill toggles, software reset, firmware alive transition, target SRAM/PRPH reads, and suspend/resume while lockdep or tracing verifies register access sequencing.
