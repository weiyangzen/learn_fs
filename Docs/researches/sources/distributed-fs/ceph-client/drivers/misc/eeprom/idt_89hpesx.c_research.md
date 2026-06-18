# sources/distributed-fs/ceph-client/drivers/misc/eeprom/idt_89hpesx.c

## Purpose
I2C/SMBus slave-interface driver for IDT 89HPESx PCIe switches. It primarily exposes a switch-attached private EEPROM through a binary sysfs file and also exposes CSR debug access through debugfs for diagnostic reads and writes.

## Important APIs, Types, And Functions
`struct idt_89hpesx_dev` stores EEPROM geometry, EEPROM address/read-only state, initial command bits, current CSR address, selected SMBus read/write methods, mutex, client, and sysfs/debugfs handles. `struct idt_smb_seq`, `struct idt_eeprom_seq`, and `struct idt_csr_seq` describe the transport payloads. The `idt_smb_*` family implements byte, word, SMBus block, and I2C-block variants. `idt_eeprom_read()`, `idt_eeprom_write()`, `idt_csr_read()`, and `idt_csr_write()` provide higher-level operations. `idt_probe()` creates state, selects operations, verifies VID/DID, and creates user interfaces.

## Control Flow
Probe reads child firmware nodes for compatible 24c EEPROMs, EEPROM size, `reg`, and `read-only`, then chooses the fastest read/write operation supported by the adapter. It validates the switch by reading CSR 0 and checking the IDT PCI vendor ID. EEPROM sysfs reads and writes loop byte by byte through the switch SMBus command protocol. Writes read back every byte for verification. CSR debugfs writes parse either an address or address:value pair, validate 4-byte alignment and range, store the shifted CSR address, and optionally issue a CSR write; debugfs reads emit the current CSR address and value.

## State, Persistence, And Dependencies
Persistent state is external EEPROM content and switch CSR state. Driver state includes the current CSR address, the selected transport callbacks, and EEPROM access policy. It depends on I2C/SMBus functionality, firmware child-node parsing, PCI vendor IDs, sysfs bin attributes, debugfs, mutexes, and delay/retry behavior for busy EEPROMs.

## Integration Points
I2C IDs and OF compatibles cover many 89HPESx switch models. Child EEPROM compatible strings map to sizes for 24c32 through 24c512 devices. The sysfs `eeprom` file mirrors EEPROM size and read-only policy. Debugfs is under the I2C client debugfs directory using the client name.

## Risks
The driver performs byte-by-byte EEPROM writes and CSR debug writes from userspace, so misuse can corrupt switch configuration. Debugfs CSR writes are intentionally low-level and privileged. Retry loops hide transient NACKs but may still fail on persistent bus problems. Several SMBus methods cast unaligned byte arrays to `u16 *`, so architecture alignment assumptions matter. EEPROM offsets and counts are narrowed to `u16`, matching supported sizes but still worth boundary testing.

## Test Signals
Test adapter capability selection across byte, word, block, and I2C-block adapters; read-only sysfs mode; child-node parsing with default and custom EEPROM addresses; VID/DID rejection; EEPROM write/readback verification; CSR debugfs parsing failures; and behavior when the EEPROM reports busy or switch command bits report NAERR, LAERR, MSS, RERR, or WERR.
