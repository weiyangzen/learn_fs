# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/core.c

## Purpose
`core.c` is the common NCI driver for STMicroelectronics ST_NCI chips. It registers an NCI device on top of an NDLC transport, initializes proprietary NFC mode, exposes secure-element hooks, and registers ST vendor commands.

## Important APIs, types, and functions
- `st_nci_probe()` allocates `struct st_nci_info`, allocates/registers the NCI device, registers vendor commands, and initializes secure-element state.
- `st_nci_remove()` closes NDLC, unregisters, and frees the NCI device.
- `st_nci_open()`/`st_nci_close()` manage `ST_NCI_RUNNING` and call `ndlc_open()`/`ndlc_close()`.
- `st_nci_send()` checks running state, stores the NCI device in `skb->dev`, and queues through `ndlc_send()`.
- `st_nci_init()` sends proprietary `ST_NCI_CORE_PROP` / `ST_NCI_SET_NFC_MODE` to enable NFC mode.
- `st_nci_get_rfprotocol()` maps proprietary ISO15693 protocol id `0x83` to `NFC_PROTO_ISO15693_MASK`.

## Control flow
Physical I2C/SPI probe creates NDLC, then calls `st_nci_probe()`. NCI registration exposes protocols including Jewel, MIFARE, Felica, ISO14443 A/B, ISO15693, and NFC-DEP. Open powers the NDLC link and sets the running bit; send queues frames into NDLC; close sends a proprietary mode-off during NDLC close and disables the transport. Secure-element and HCI callbacks are wired directly into `st_nci_ops`.

## State and persistence
State lives in `struct st_nci_info`: NDLC pointer, flags, and `st_nci_se_info`. There is no file persistence. HCI session identity and secure-element discovery are handled by `se.c` during NCI/HCI setup.

## Dependencies and integration points
The core depends on `net/nfc/nci_core.h`, NDLC, secure-element helpers, and vendor-command registration. It is transport-neutral; I2C and SPI provide `struct nfc_phy_ops` to NDLC.

## Risks
`st_nci_remove()` closes NDLC regardless of current running state. `st_nci_send()` returns `-EBUSY` without freeing the skb if not running, relying on NCI core ownership conventions. Vendor command init failure and NCI register failure share cleanup but do not explicitly unregister vendor commands.

## Test signals
Test probe failure at allocation/vendor/register stages, open/close idempotence, send while stopped, proprietary init response handling, ISO15693 RF protocol mapping, and secure-element hook invocation through NCI core.
