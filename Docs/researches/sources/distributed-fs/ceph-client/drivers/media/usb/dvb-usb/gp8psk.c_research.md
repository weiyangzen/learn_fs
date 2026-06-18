# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/gp8psk.c

## Purpose
This is the Genpix 8PSK/SkyWalker DVB-S USB driver. It provides Cypress FX2 firmware loading, device power sequencing, BCM4500 secondary firmware loading for rev1 hardware, frontend operations glue, streaming control, and USB ID/property registration.

## Important APIs, types, and functions
`struct gp8psk_state` provides an 80-byte USB control scratch buffer. `gp8psk_usb_in_op()` and `gp8psk_usb_out_op()` serialize vendor control transfers with `usb_mutex`. `gp8psk_power_ctrl()` boots the 8PSK core, powers the Intersil LNB supply, starts CW3K devices, optionally loads BCM4500 firmware, and aborts stale transport streams. `gp8psk_fe_ops` bridges `gp8psk-fe.c` to USB in/out/reload callbacks. `gp8psk_streaming_ctrl()` arms or disarms transport transfer.

## Control flow and state
Probe calls `dvb_usb_device_init()` against `gp8psk_properties`. The framework handles the first firmware image for cold rev1 devices. Power-on reads device configuration, performs hardware-specific initialization, loads secondary firmware when required, and enables LNB power. Frontend attach calls `gp8psk_fe_attach()` with a rev1 flag and the operations table. Streaming starts by sending `ARM_TRANSFER`.

## Dependencies and integration
The driver depends on `gp8psk.h`, `gp8psk-fe.h`, DVB USB generic write helpers, firmware loading, Genpix USB IDs, rc/debug support through the framework, and bulk streaming on endpoint `0x82`.

## Risks and test signals
Important risks are bounded scratch-buffer assumptions, retry semantics in reads, firmware parser termination at `0xff`, product-ID-specific secondary firmware, and NULL buffer use for zero-length out transfers. Test with rev1 and newer warm devices, missing firmware, power cycles, frontend tune/reload, stream arm/disarm, and unplug during a control transfer.
