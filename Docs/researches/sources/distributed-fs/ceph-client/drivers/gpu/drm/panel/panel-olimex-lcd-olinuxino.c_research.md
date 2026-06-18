# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-olimex-lcd-olinuxino.c

Purpose: I2C-described DRM DPI panel driver for Olimex LCD-OLinuXino modules. Instead of hard-coded timings, it reads a 256-byte panel EEPROM over I2C and builds DRM modes from that data.

Important APIs, types, and functions: packed `struct lcd_olinuxino_eeprom` contains header, ID, revision, serial, panel info, up to four serialized mode records in `reserved`, and CRC checksum. `struct lcd_olinuxino` holds the DRM panel, I2C client, mutex, regulator, enable GPIO, and EEPROM copy. Core functions are `lcd_olinuxino_probe()`, `lcd_olinuxino_prepare()`, `lcd_olinuxino_unprepare()`, and `lcd_olinuxino_get_modes()`.

Control flow: probe verifies I2C functionality, allocates a DPI panel, initializes a mutex, reads 256 EEPROM bytes in SMBus block chunks, validates CRC32 and magic header, logs name/revision/serial, caps `num_modes` to four, obtains `power` regulator and `enable` GPIO, binds OF backlight, and adds the panel. Prepare enables the regulator and enable GPIO. Unprepare clears enable GPIO and disables power. Get-modes decodes each stored timing record into a DRM mode, marks the first preferred, and copies width, height, bpc, bus format, and bus flags from EEPROM.

State and persistence: the panel module EEPROM is persistent hardware data; the driver caches it in memory at probe and does not reread on each mode query. No software persistence is used.

Dependencies and integration points: I2C/SMBus, CRC32, mutex, regulator, GPIO, DRM panel, video timing concepts, media bus format values carried from EEPROM, and OF backlight. Compatible string is `olimex,lcd-olinuxino`.

Risks and test signals: EEPROM content is trusted after checksum, including mode arithmetic and bus flags. The mode data is read from `reserved` by casting, so struct layout and endianness are ABI-like. Test corrupted checksum/header, overlarge mode count, short I2C reads, backlight phandle errors, enable sequencing, and multiple EEPROM configurations.
