# sources/distributed-fs/ceph-client/drivers/usb/host/sl811_cs.c

## Purpose
`sl811_cs.c` is PCMCIA/CardBus glue for SL811HS-based CompactFlash USB host cards, specifically the RATOC/REX-CFU1U style device. It does not implement USB transfer logic. Instead, it claims PCMCIA resources, constructs a singleton platform device with IRQ and two IO registers, and lets the exported `sl811-hcd` platform driver probe the actual controller.

## Important APIs, Types, And Functions
The file registers a `struct pcmcia_driver` named `sl811_cs`. `sl811_cs_probe()` allocates a small `local_info_t` and calls `sl811_cs_config()`. `sl811_cs_config()` uses PCMCIA core helpers to select a configuration, require an IRQ and at least two IO ports, enable the device, and call `sl811_hc_init()`. `sl811_hc_init()` fills static `resources[]`, assigns the parent, uses `sl811h_driver.driver.name` for the platform device name, and registers `platform_dev`. `sl811_cs_release()` disables the PCMCIA device and unregisters the platform device. Static `platform_data` describes power-on-to-power-good and a 100 mA power budget.

## Control Flow
The PCMCIA core calls probe for matching manufacturer/card IDs. Probe allocates private bookkeeping and immediately configures the card. Configuration sets auto flags for IRQ, VPP, VCC, and IO; `pcmcia_loop_config()` calls `sl811_cs_config_check()` until a valid config index and IO request are accepted. Once the card is enabled, platform resources map IRQ, address port, and data port. The platform device then triggers the already-linked `sl811-hcd` driver to probe. Remove calls release, unregistering the platform child before freeing private state.

## State And Persistence Behavior
The driver uses static singleton platform resources and platform device storage, which implies only one such PCMCIA SL811 controller is supported at a time. There is no persistent state. The PCMCIA card state lives in `pcmcia_device`, while the actual HCD state lives in `sl811-hcd` after platform registration.

## Dependencies And Integration Points
Integration points are the PCMCIA core, platform-device core, SL811 platform data ABI, and the exported `sl811h_driver` symbol. Link order matters: the reference to `sl811h_driver` intentionally ensures the host-controller driver is initialized before this glue tries to register a matching platform device. The platform device resource ordering must match `sl811h_probe()` expectations: IRQ plus address and data register windows.

## Risks And Edge Cases
The singleton static `platform_dev` returns `-EBUSY` if already parented, so multi-card systems are unsupported. The reset hook is marked FIXME, so cards that require CF reset sequencing may be fragile. Error handling funnels many resource failures to `sl811_cs_release()`, which calls `platform_device_unregister()` even when registration may not have succeeded; the singleton design makes ordering important. The power budget is hardcoded to 100 mA and may not reflect all cards or attached devices.

## Test Signals
Test by inserting/removing a matching PCMCIA card, verifying IO and IRQ resources are assigned, confirming platform probe of `sl811-hcd`, and checking clean unregister on eject. Negative tests should cover missing IRQ, insufficient IO window size, repeated insertion, and failure of `platform_device_register()`.
