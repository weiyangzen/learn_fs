# sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/hexium_orion.c

Purpose: V4L2/SAA7146 extension driver for Hexium HV-PCI6 and Orion frame grabber cards. It detects old and newer Orion variants, initializes a Philips SAA7110 decoder, exposes nine camera inputs, and registers a common SAA7146 video capture device.

Important APIs, types, and functions: `struct hexium` carries video device, I2C adapter, card type, and current input. `hexium_saa7110[]` is the default decoder register table. `hexium_input_select[]` holds eight-register routing sequences per input. `hexium_probe()` performs variant detection and I2C setup for old generic IDs and known subsystem IDs. `hexium_init_done()` writes the decoder defaults; `hexium_set_input()` applies input routing; the V4L2 handlers enumerate/get/set input. `hexium_attach()` initializes `saa7146_vv` and registers the video node; `hexium_detach()` unwinds it.

Control flow: module init registers the extension. Probe rejects SAA7146 revision 0, allocates state, enables I2C pins, configures DD1, registers an I2C adapter, toggles decoder/control GPIOs, then identifies the card from subsystem IDs or by probing an SAA7110 at I2C address `0x4e`. Attach assumes successful probe state in `dev->ext_priv`, initializes vv, installs input ioctl hooks, registers the video device, initializes decoder registers, and selects input 0.

State and persistence: current input and card type persist only while the driver is loaded. Hardware decoder routing and SAA7146 register writes are volatile. `hexium_num` is a module-global active-device counter.

Dependencies and integration points: integrates with SAA7146 extension registration, SAA7146 I2C adapter preparation, SMBus byte-data transfers, V4L2 input ioctls, PCI subsystem matching, and the shared `saa7146_vv` capture framework.

Risks: old-card detection binds generic `0x0000:0x0000` subsystem IDs after probing, which is inherently risky if hardware is misidentified. Attach does not fully release vv if `saa7146_register_device()` fails. `std_callback()` is a no-op, so standard-specific decoder changes are not applied beyond common vv timing. I2C errors during default initialization are logged but not fatal.

Test signals: probe known Orion subsystem IDs and old-card detection, verify rejection of revision 0 hardware, enumerate/switch all nine inputs, stream PAL/NTSC/SECAM through the common vv layer, monitor dmesg for SAA7110 write failures, and unload/reload while checking I2C adapter cleanup.
