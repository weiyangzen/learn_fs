<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-elkhartlake.c -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-elkhartlake.c

Purpose: This board wrapper supplies Elkhart Lake GPIO line mappings for SIMATIC IPC GPIO LEDs.

Important APIs and state: A single `gpiod_lookup_table` maps six active-high GPIOs on ACPI controller `INTC1020:04` to `leds-gpio` indices 0-5. Probe and remove directly wrap the shared core helper with no extra GPIO table.

Control flow: Probe calls `simatic_ipc_leds_gpio_probe()` with the lookup table and `NULL` extra table. Remove calls the common remove helper with the same arguments.

Dependencies and integration: It integrates with `leds-gpio`, the Elkhart Lake pinctrl provider, and the SIMATIC IPC platform base driver. The module soft dependency names the common helper and Elkhart Lake pinctrl platform provider.

Risks and test signals: The key risk is ACPI/pinctrl naming and active-high polarity drift across board revisions. Test on BX-21A hardware by checking each of the six status LED names against physical LEDs and by unloading/reloading the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-elkhartlake.c -->
