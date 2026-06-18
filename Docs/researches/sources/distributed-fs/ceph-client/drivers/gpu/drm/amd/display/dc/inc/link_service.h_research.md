# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/link_service.h

## Purpose

`link_service.h` is the private DC link-component interface. It intentionally exposes a broad function-pointer service to DC internals while keeping DM consumers behind `dc.h`, preventing DM from depending on private link implementation headers.

## Important APIs, Types, And Functions

The file declares `link_create_link_service`, `link_destroy_link_service`, `link_init_data`, `ddc_service_init_data`, and the large `struct link_service`. The service groups factory, detection, resource, validation, DPMS, DDC/AUX, DP capability, DP PHY/DPIA, DP IRQ handling, eDP panel control, DP CTS, and DP trace functions. It covers link creation/destruction, sink detection, remote sinks, HPD, MST topology reset, HDCP capability, resource maps, mode timing validation, tunnel bandwidth, DPMS on/off, MST payload updates, DSC, DDC/AUX transfers, retimer config, FEC/link settings/LTTPR decisions, DPIA USB4 bandwidth, drive settings, HPD IRQ parsing/handling, eDP backlight/PSR/replay/ALPM/panel power, DP automated tests, preferred link/training settings, and trace counters/timestamps.

## Control Flow

Callers obtain one service from the factory and invoke category-specific function pointers. Detection creates or updates links and sinks; validation chooses timings and bandwidth; DPMS sequences link output; DDC/AUX performs sideband transactions; IRQ handlers parse HPD RX/link loss; panel-control hooks manage eDP backlight and PSR/replay; CTS hooks drive compliance patterns.

## State And Persistence Behavior

The service object is dispatch-only, but it mutates persistent `dc_link`, `dc_sink`, DDC, panel, trace, MST, and resource-map state. Link training decisions, verified caps, trace counters, and panel power/backlight state persist outside the service table.

## Dependencies And Integration Points

It depends on `core_types.h` and intentionally remains private to DC and link subcomponents. It integrates with `dc_link_exports.c`, `link_factory.c`, DP training, AUX/DDC, HDCP, MST, DSC, eDP panel features, HPD IRQ service, and DMUB-assisted PSR/replay.

## Risks And Test Signals

Risks include DM accidentally including this private header, missing service assignments in `link_factory.c`, NULL function pointers for expected features, and broad interface churn. Test signals include all connector detection paths, AUX/I2C transactions, MST, DSC, USB4 DPIA, HPD IRQ/link loss, eDP backlight/PSR/replay, DP CTS patterns, and trace output after link training.
