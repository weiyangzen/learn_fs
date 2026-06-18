
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-budget/Kconfig

## Purpose
This Kconfig entry enables DVB support for Technotrend/Hauppauge Nova-USB budget adapters.

## Important APIs, Types, and Functions
The symbol is `DVB_TTUSB_BUDGET`, a `tristate` depending on `DVB_CORE && USB && I2C && PCI`. It conditionally selects frontend/tuner helpers (`DVB_CX22700`, `DVB_TDA1004X`, `DVB_VES1820`, `DVB_TDA8083`, `DVB_STV0299`, `DVB_STV0297`, `DVB_LNBP21`) when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

## Control Flow
Enabling the symbol builds the budget USB DVB driver and, under autoselect, pulls in the demodulator and LNB helper modules used by runtime frontend probing.

## State and Persistence
The file contributes compile-time configuration only. Runtime firmware and DVB state live in `dvb-ttusb-budget.c`.

## Dependencies and Integration Points
It integrates with DVB core, USB, I2C, historical PCI dependency requirements for DVB infrastructure, and the media subdevice autoselection system.

## Risks and Edge Cases
If `MEDIA_SUBDRV_AUTOSELECT` is disabled, users must manually enable the relevant frontend modules or runtime frontend attach will fail. The PCI dependency is surprising for a USB device and reflects shared DVB adapter infrastructure expectations in this tree.

## Test Signals
Build with autoselect on/off, verify frontend symbols are selected as expected, and test module loading with the required demodulator modules present.
