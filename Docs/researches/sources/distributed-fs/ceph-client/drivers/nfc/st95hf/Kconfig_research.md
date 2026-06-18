# sources/distributed-fs/ceph-client/drivers/nfc/st95hf/Kconfig

## Purpose
This Kconfig entry enables the ST95HF NFC transceiver driver.

## Important symbol
- `NFC_ST95HF` is a user-visible tristate titled "ST95HF NFC Transceiver driver" and depends on `SPI && NFC_DIGITAL`.

## Control flow and integration
The option builds a driver that communicates with the transceiver over SPI and registers with the NFC digital core, as described by the help text and Makefile.

## State, dependencies, and risks
Kconfig state is compile-time only. Dependency on `NFC_DIGITAL` identifies this as a digital-core driver, not NCI/HCI. Missing SPI or digital NFC support hides the option.

## Test signals
Configuration tests should verify visibility with SPI/NFC_DIGITAL enabled, pruning when either is disabled, and module/built-in builds of the corresponding Makefile objects.
