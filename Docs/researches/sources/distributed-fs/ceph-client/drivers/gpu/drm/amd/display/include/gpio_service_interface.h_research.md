# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/gpio_service_interface.h

Purpose: Declares the factory/service layer for creating GPIO-related handles from ASIC-specific display context. It sits above low-level hardware GPIO implementations and below display services that need DDC, HPD IRQ, generic mux, and pin metadata.

Important APIs and types: `dal_gpio_service_create`/`dal_gpio_service_destroy` manage `struct gpio_service`. `dal_gpio_create`, `dal_gpio_destroy`, `dal_gpio_create_irq`, `dal_gpio_destroy_irq`, `dal_gpio_service_create_irq`, and `dal_gpio_service_create_generic_mux` allocate different GPIO objects. DDC-specific APIs include `dal_gpio_create_ddc`, `dal_gpio_destroy_ddc`, `dal_ddc_open`, `dal_ddc_change_mode`, `dal_ddc_get_line`, `dal_ddc_set_config`, and `dal_ddc_close`. IRQ helpers translate GPIO IRQ handles to `dc_irq_source` values and configure HPD filtering.

Control flow: Callers create a service for a `dce_version`, environment, and `dc_context`; create typed pin objects by `gpio_id`, enum, offsets, or masks; configure/open them through object APIs; then destroy handles and finally the service. IRQ helpers map register source IDs and HPD read request sources into DC IRQ enums.

State and persistence: The service owns ASIC/environment-specific lookup tables and allocation context. Created GPIO/DDC handles carry pin offsets, masks, output polarity, and open mode. No persistent storage is defined; all lifetime is explicit through create/destroy.

Dependencies and integration points: Includes `gpio_types.h`, `gpio_interface.h`, and `hw/gpio.h`; forward-depends on `dc_context`, `dce_version`, `dce_environment`, `dc_irq_source`, `ddc`, and hardware GPIO objects. Used by BIOS/parser-derived pin configuration, hotplug, AUX/DDC transactions, and interrupt services.

Risks: Factories accept low-level offsets and masks, so wrong BIOS data or caller-provided masks can route interrupts/DDC to the wrong pins. Service lifetime must outlive created handles. DDC open/change/config calls must coordinate with GPIO pin ownership or link detection can fail.

Test signals: Validate service creation across DCE versions, pin metadata lookup, IRQ source translation, HPD filter programming, DDC line selection, and failure cleanup when any create/open step returns NULL or non-OK.
