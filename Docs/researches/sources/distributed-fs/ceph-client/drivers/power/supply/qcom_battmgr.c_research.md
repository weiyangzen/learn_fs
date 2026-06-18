
# sources/distributed-fs/ceph-client/drivers/power/supply/qcom_battmgr.c

## Purpose
`qcom_battmgr.c` implements the Qualcomm PMIC GLINK battery manager power-supply driver. It registers battery, USB, wireless, and on some variants AC supplies, translates power_supply property reads/writes into PMIC GLINK requests, handles asynchronous firmware replies/notifications, and supports variant-specific firmware protocols for SC8280XP/X1E80100 and SM8350/SM8550-style platforms.

## Important APIs, Types, and Functions
Important state structs are `qcom_battmgr`, `qcom_battmgr_info`, `qcom_battmgr_status`, and source-specific AC/USB/wireless caches. Message/request structs encode PMIC GLINK protocol payloads. Main functions include `qcom_battmgr_probe()`, `qcom_battmgr_request()`, property update helpers, `qcom_battmgr_bat_get_property()`, USB/WLS/AC get-property callbacks, charge-control setters, `qcom_battmgr_notification()`, variant callbacks `qcom_battmgr_sc8280xp_callback()` and `qcom_battmgr_sm8350_callback()`, `qcom_battmgr_callback()`, `qcom_battmgr_enable_worker()`, and `qcom_battmgr_pdr_notify()`.

## Control Flow
Probe chooses a variant from the parent compatible, initializes charge-control thresholds from nvmem, registers variant-appropriate power supplies, allocates a PMIC GLINK client, and registers it. PDR service-up notifications set `service_up` and schedule notification enable work. Property reads reject access while service is down, serialize firmware requests with `lock`, send a request, wait up to one second for callback completion, then return cached decoded values. SC8280XP/X1E80100 batch status/info/time requests; SM8350/SM8550 use property-specific request maps. Firmware notifications invalidate info or call `power_supply_changed()` on the affected supply.

## State and Persistence
The driver caches firmware-reported battery info, status, AC/USB/wireless source values, charge-control thresholds, service state, last request error, and completion. Charge-control defaults can be read from nvmem cells (`charge_limit_en`, `charge_limit_end`, `charge_limit_delta`), and runtime writes send firmware commands then update cached thresholds. No filesystem persistence is performed.

## Dependencies and Integration Points
The driver depends on auxiliary bus binding `pmic_glink.power-supply`, PMIC GLINK owner BATTMGR, PDR service state callbacks, nvmem cells for charge limits, OF compatible-to-variant mapping, the power_supply class, and supplier relationships via `supplied_to = "battery"` for source supplies. It integrates with sysfs through distinct property arrays per variant and with uevents through `power_supply_changed()`.

## Risks and Test Signals
Risk areas include firmware protocol length validation, request timeout handling, callback completion on malformed messages, variant property-map gaps where unmapped properties default to zero, integer unit conversions and capacity percentage overflow avoidance, returning success from charge threshold setters even if firmware request failed, and service-up races. Tests should mock PMIC GLINK replies for both protocol families, verify each property mapping and unit, test notifications, PDR down/up behavior, timeout/error propagation, charge threshold clamping/nvmem init, and power_supply registration per compatible.
