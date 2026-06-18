# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/gpio_types.h

Purpose: Centralizes GPIO result codes, pin identity enums, DDC/HPD/generic/sync/GSL classifications, mode enums, and configuration payloads shared by AMD display GPIO objects and services.

Important APIs and types: `enum gpio_result`, `enum gpio_id`, `struct gpio_pin_info`, `enum gpio_pin_output_state`, per-family enums for generic, HPD, GPIO pads, VIP pads, sync and GSL pins, `enum gpio_ddc_line`, `enum gpio_mode`, `enum gpio_signal_source`, `enum gpio_stereo_source`, `enum gpio_config_type`, `enum gpio_ddc_config_type`, `struct gpio_ddc_config`, `struct gpio_hpd_config`, `struct gpio_generic_mux_config`, `struct gpio_gsl_mux_config`, and `struct gpio_config_data`.

Control flow: The data model separates object identity (`gpio_id` plus enum) from operating mode and configuration. `gpio_config_data.type` selects which union payload is meaningful. DDC config switches AUX/I2C/polling modes, HPD config supplies connect/disconnect debounce delays, and mux configs select signal routing.

State and persistence: This header defines only values passed into stateful GPIO implementations. Enum comments note some IDs are vector indices and must remain contiguous, so enum ordering is a persistence-like ABI inside DAL tables.

Dependencies and integration points: Used by `gpio_interface.h`, `gpio_service_interface.h`, HPD IRQ filtering, DDC setup, GSL/stereo sync routing, and BIOS-derived pin mapping. It intentionally avoids some cross-component includes by storing `gsl_group` as `uint32_t`.

Risks: Contiguous enum assumptions can break lookup vectors if values are reordered. Several min/max aliases do not cover every enum value, for example generic max is `GPIO_GENERIC_B` despite more entries, so callers must distinguish physical support from enum capacity. Union payload misuse can silently configure the wrong hardware behavior.

Test signals: Compile-time checks for enum ranges, table sizes, and config union selectors are valuable. Runtime tests should cover DDC AUX/I2C transitions, HPD debounce config, active-low/high output behavior, and invalid enum handling.
