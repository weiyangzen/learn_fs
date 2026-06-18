<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/gpio.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/gpio.c

### Purpose

Parser for GPIO function tables referenced from DCB. It maps logical GPIO functions to line numbers, polarity, parameters, and optional extended GPIO provider data.

### Important APIs, types, and functions

`dcb_gpio_table()`, `dcb_gpio_entry()`, `dcb_gpio_parse()`, `dcb_gpio_match()`, and iteration helpers decode GPIO records. It also coordinates with XPIO parsing for external GPIO blocks.

### Control flow

The parser finds the GPIO table through DCB v0x30+ header fields or older DCB backpointers, handles pre-0x30 and 0x30-0x41 header formats, computes entry offsets, and decodes function/line/log/param/polarity fields by table version.

### State and persistence behavior

No persistent state. Decoded GPIO records are transient, while the GPIO subdevice later owns live line state.

### Dependencies and integration points

Depends on DCB, XPIO, and generic BIOS reads. GPIO, therm, fan, hotplug, and init-script code consume these mappings.

### Risks

Version-specific bitfields are fragile. Bad parsing can invert GPIO polarity, drive wrong lines, or miss HPD/fan/thermal GPIOs.

### Test signals

Source read size: 150 lines, 4315 bytes. GPIO table dump comparison, hotplug GPIO interrupts, fan/tach GPIO tests, init-script GPIO opcode tests, and old/new DCB compatibility coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/gpio.c -->
