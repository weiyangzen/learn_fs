# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-csr.h

## Purpose
Defines control/status register addresses, bit masks, hardware revision extractors, interrupt causes, reset/power bits, mailbox bits, internal HBUS access registers, MSI-X registers, and MAC address CSR offsets for iwlwifi hardware.

## Important APIs, Types, and Functions
Key macro groups cover CSR base registers, `CSR_HW_REV`, `CSR_HW_RF_ID`, EEPROM/OTP, `CSR_GP_CNTRL`, reset, interrupt masks, LTR, IPC sleep/reset, BZ doorbell/status bits, HBUS memory/periphery access, host interrupt timeout, DTS diode fields, MSI-X causes, and MAC address CSR access. Extractors include `CSR_HW_REV_TYPE`, `CSR_HW_RFID_TYPE`, `CSR_HW_RFID_STEP`, `CSR_HW_RFID_IS_CDB`, and silicon-step enums.

## Control Flow
No direct execution. Transport and PCI code use these constants to reset devices, arbitrate MAC access, read identity, handle interrupts, configure MSI-X, access OTP/EEPROM, write memory/periphery windows, and detect RF-kill or power state.

## State and Persistence Behavior
The file maps hardware-visible registers and bitfields. Register contents are live device state, while the macros are static ABI.

## Dependencies and Integration Points
Used by `iwl-io.c`, PCI transport, interrupt handlers, firmware loader, NVM readers, power management, and firmware filename selection.

## Risks
Register definitions are hardware ABI. Wrong bits can corrupt reset/power sequencing, interrupt acknowledgement, bus mastering, or RF identification. Some registers are accessible while MAC is asleep and others require NIC access, so consumers must obey access rules documented here.

## Test Signals
Probe identity reads, reset and stop-master flows, RF-kill interrupts, MSI-X and legacy interrupt paths, EEPROM/OTP reads, BZ MAC access, LTR programming, MAC address reads, and suspend/resume IPC transitions are primary signals.
