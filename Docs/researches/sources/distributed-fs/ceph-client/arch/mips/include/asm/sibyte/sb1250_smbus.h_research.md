<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_smbus.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_smbus.h

Purpose: Provides bit definitions for the SiByte SMBus controller, covering bus clock setup, command/start formatting, direct line control, interrupt/status bits, data registers, packet-error-check fields, and extended transfer formats.

Important APIs/types/functions: `S_SMB_FREQ_DIV`, `V_SMB_FREQ_DIV`, frequency constants `K_SMB_FREQ_400KHZ`, `K_SMB_FREQ_100KHZ`, `K_SMB_FREQ_10KHZ`; control/status flags `M_SMB_ERR_INTR`, `M_SMB_FINISH_INTR`, `M_SMB_BUSY`, `M_SMB_ERROR`; transaction fields `V_SMB_ADDR`, `V_SMB_TT_*`, `M_SMB_PEC`; data fields `V_SMB_LB`, `V_SMB_MB`; extended-format fields `V_SMB_DFMT_*`, `V_SMB_AFMT_*`, and `M_SMB_DIR`.

Control flow: The header encodes the caller sequence for a transaction: set clock divisor, optionally drive/directly sample the lines, program command/address/data/extra registers, select a transaction type, start the transfer, then poll or handle finish/error status.

State and persistence: Hardware state is in the SMBus controller registers and external bus lines. The macros expose interrupt enable state, busy/error latches, SCL/SDA input samples, queued data, packet error check bytes, and multi-byte command/address layout.

Dependencies and integration points: Depends on `sb1250_defs.h` for bitfield helpers and feature predicates. Integrated by the SiByte I2C/SMBus platform driver and board code that accesses EEPROMs, RTCs, sensors, and other board-management devices.

Risks: Clock divisor assumptions are tied to the controller input clock. Extended transfer and SCL input fields are feature-gated by chip revision. `V_SPEC_MB` appears to build the PEC field despite the name mismatch, so renames must preserve compatibility.

Test signals: Signals include compile coverage for SiByte I2C code, SMBus probe/read/write tests against board EEPROM/RTC devices, interrupt completion/error tests, and bus recovery tests for busy/error conditions.

Source read size: 191 lines, 6365 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_smbus.h -->
