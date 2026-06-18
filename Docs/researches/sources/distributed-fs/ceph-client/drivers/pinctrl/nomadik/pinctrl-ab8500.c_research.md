# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-ab8500.c

Purpose: this is the AB8500-specific pin inventory and mux table for the ABx500 pinctrl/GPIO core. It names GPIO-capable balls, groups them by default/alternate function columns, maps functions to groups, describes mux register bit encodings, and lists interrupt-capable GPIO clusters.

Important APIs, types, and functions: `ab8500_pins[]` lists GPIO1-42 with holes at GPIO5 and GPIO33. `ab8500_pinranges[]` maps GPIO number ranges to the altsetting needed for GPIO mode. `ab8500_groups[]` and `ab8500_functions[]` expose functions such as `sysclkreq`, `ycbcr`, `gpio`, `pwmout`, `adi1`, `usbuicc`, `dmic`, `extcpena`, `apespi`, `modsclsda`, `hiqclkena`, `i2ctrig`, and `usbvdat`. `ab8500_alternate_functions[]` describes GPIOSEL/ALTFUN bit usage per GPIO. `abx500_pinctrl_ab8500_init()` returns `ab8500_soc`.

Control flow: the common ABx500 probe calls `abx500_pinctrl_ab8500_init()` for compatible `stericsson,ab8500-gpio`. The core then registers pins, groups, functions, GPIO ranges, and uses the alternate-function table whenever a pinmux or GPIO request changes a pin mode.

State and persistence behavior: all AB8500 data is static. Runtime state is maintained by the common core and AB8500 hardware registers. The table has no write path except returning a pointer to the static SoC descriptor.

Dependencies and integration points: dependencies include `pinctrl-abx500.h`, pinctrl pin descriptors, and AB8500 interrupt constants. It integrates with AB8500 MFD IRQ domains through clusters for GPIO6-13, GPIO24-25, and GPIO36-41.

Risks and test signals: holes require the core's homogeneous GPIO numbering to include absent offsets while pin descriptors omit them. Some pins share one GPIOSEL bit across multiple GPIOs, especially GPIO17-20, so mux changes can affect grouped pins. Test GPIO requests across all ranges, IRQ mapping for each cluster, default versus ALT_A/B/C muxing, and DT group/function names for multi-group functions like YCbCr and USBUICC.
