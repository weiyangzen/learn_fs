<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/io_usbvend.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/io_usbvend.h

## Purpose
Provides vendor-specific USB IDs, Edgeport product ID encoding helpers, EPiC compatibility descriptors, legacy manufacturing and boot descriptor layouts, TI UMP I2C descriptor formats, and Edgeport/Watchport hardware constants shared by Edgeport serial drivers.

## Important APIs, Types, And Functions
The header defines vendor IDs for Inside Out Networks, TI, Axiohm, NCR, Symbol, and many Edgeport-compatible devices. It enumerates Edgeport generation, OEM, hub, device, Watchport, and TI-based product IDs consumed by USB ID tables. `struct edge_compatibility_bits` and `struct edge_compatibility_descriptor` describe EPiC feature discovery. Legacy 930 manufacturing state is represented by `struct edge_manuf_descriptor` and `struct edge_boot_descriptor`. TI UMP formats include `struct ti_i2c_desc`, `struct ti_i2c_firmware_rec`, `struct watchport_firmware_version`, `struct ti_i2c_image_header`, `struct ti_basic_descriptor`, and `struct edge_ti_manuf_descriptor`. Macros such as `TI_GET_CPU_REVISION()`, `TI_GET_BOARD_REVISION()`, and `TI_GET_I2C_SIZE()` decode packed manufacturing fields.

## Control Flow
This header has no runtime logic, but its constants drive probe matching, firmware-update decisions, descriptor walking, and hardware validation in `io_ti.c`. The driver searches I2C descriptors by type, validates checksums against descriptor sizes, checks CPU revision through the packed manufacturing descriptor, and uses product IDs to select heartbeat behavior for Edgeport/416 variants.

## State And Persistence
Most structures model persistent device EEPROM or firmware descriptors. The TI I2C records carry type, size, checksum, version, firmware image, Watchport version, and manufacturing metadata. Legacy Edgeport structures model ROM/E2PROM manufacturing state such as serial number, assembly numbers, port count, CPU/board revisions, and boot-code capabilities.

## Dependencies And Integration Points
It integrates with Linux USB device matching through IDs used by `USB_DEVICE()` tables. It also integrates with device firmware and manufacturing tools through fixed descriptor layouts and comments documenting backward compatibility requirements.

## Risks And Edge Cases
The file intentionally preserves older firmware compatibility, so changing IDs or layouts risks binding failures or firmware misinterpretation. Some macros deserve scrutiny: `MAKE_USB_PRODUCT_ID()` uses logical `||` rather than bitwise OR, which would not construct the intended composite ID if used; the current researched driver primarily uses literal IDs instead. Duplicate macro names such as `USB_VENDOR_ID_AXIOHM` and `MANUF_BOARD_REV_A` appear in separate historical sections and depend on identical replacement compatibility. Packed flexible descriptors require callers to bound-check sizes before casting or copying.

## Test Signals
Signals include correct module autoload for every listed product ID, successful parsing of EPiC and TI I2C descriptors, checksum validation on real and malformed EEPROM images, firmware-version comparison, and regression tests ensuring no ID-table product is accidentally removed or remapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/io_usbvend.h -->
