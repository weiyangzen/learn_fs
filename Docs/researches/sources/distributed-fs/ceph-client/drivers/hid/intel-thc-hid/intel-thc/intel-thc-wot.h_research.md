# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-wot.h

Purpose: Wake-on-Touch state and API declarations for Intel THC.

Important APIs/types: `struct thc_wot` stores `gpio_irq` and `gpio_irq_wakeable`. `thc_wot_config()` and `thc_wot_unconfig()` are declared for use by THC transport drivers.

Control flow: included by `intel-thc-dev.h`, making WOT state part of the main THC device object.

State and persistence: the struct records the ACPI-derived IRQ and whether it should be treated as wake-capable.

Dependencies and integration: includes Linux types and GPIO consumer declarations; uses a forward declaration for `struct thc_device`.

Risks: minimal, but the API assumes callers provide a valid ACPI GPIO mapping compatible with the `"wake-on-touch"` lookup.

Test signals: build coverage and WOT setup/unsetup on ACPI THC platforms.
