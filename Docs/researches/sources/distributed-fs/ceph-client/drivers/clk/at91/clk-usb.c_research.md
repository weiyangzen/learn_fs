# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-usb.c

Purpose: USB clock providers for SAM9x5/SAM9x60 mux+divider, SAM9N12 enable-only USB from one parent, and RM9200 divisor-table USB from PLLB.

Important APIs and data: exported helpers are `at91sam9x5_clk_register_usb()`, `sam9x60_clk_register_usb()`, `at91sam9n12_clk_register_usb()`, and `at91rm9200_clk_register_usb()`. Private structs store regmap, PM state, parent count, selector mask, and RM9200 divisor table.

Control flow: SAM9x5 recalc reads `AT91_PMC_USB` divider; determine-rate searches parents and divisors 1-16 while asking parents to round; set_parent writes USBS bits; set_rate writes OHCI divisor. SAM9N12 ops only enable/disable/check `USBS` and reuse divider rate logic. RM9200 uses `PLLBR.USBDIV` table entries.

State and persistence: SAM9x5 save/restore records parent, parent rate, and rate, then replays parent/rate. SAM9N12 and RM9200 variants lack explicit PM callbacks. Hardware registers hold selector/divider state.

Dependencies and integration: used by older SoC setup files, SAM9X60/SAM9X7 setup, and DT compat. It depends on common-clock parent rate propagation and `AT91_PMC_USB` or `CKGR_PLLBR` bit definitions.

Risks: SAM9N12 ops omit get/set parent even though the shared struct has fields; zero or unsupported divisors reject rate changes; SAM9X60 uses a wider selector mask than SAM9x5. Test signals include USB 48 MHz-derived clock accuracy, parent selection across PLL/UTMI/main oscillator, host/device enumeration, and suspend/resume preserving SAM9x5 USB settings.
