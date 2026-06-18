# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/nova-t-usb2.c

## Purpose
This driver supports Hauppauge WinTV-NOVA-T USB2 DVB-T receivers using the DiBUSB framework helpers. It mainly supplies Hauppauge-specific remote-control decoding, MAC readout, USB IDs, and DVB USB property wiring.

## Important APIs, types, and functions
`rc_map_haupp_table` maps Hauppauge RC5 scancodes to Linux input keys. `nova_t_rc_query()` sends `DIBUSB_REQ_POLL_REMOTE`, decodes the RC5 custom/data/toggle fields, suppresses immediate repeats via `dibusb_device_state`, and emits legacy RC events. `nova_t_read_mac_address()` constructs a MAC using a fixed Hauppauge OUI and three EEPROM bytes read with `dibusb_read_eeprom_byte()`.

## Control flow and state
Probe calls `dvb_usb_device_init()` with `nova_t_properties`. Framework callbacks then use `dibusb2_0_power_ctrl`, DiBUSB I2C, DiB3000MC frontend/tuner attach, PID filter callbacks, and bulk streaming on endpoint `0x06`. Remote polling is legacy and runs every 100 ms.

## Dependencies and integration
The file depends on `dibusb.h` for common power, streaming, I2C, EEPROM, PID filter, frontend, and tuner helpers. It integrates Cypress FX2 firmware `dvb-usb-nova-t-usb2-02.fw`.

## Risks and test signals
Risks are firmware delivering stale key codes, guessed MAC offset, legacy RC repeat behavior, and DiBUSB helper compatibility. Test cold/warm probe, firmware load, EEPROM MAC read, RC key and repeat behavior, PID filter toggling, and bulk TS streaming under feed start/stop.
