# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/auxadc.h

## Purpose
`wm831x/auxadc.h` defines WM831x auxiliary ADC data/control/comparator bitfields, ADC input IDs, request tracking, and the public asynchronous/synchronous read APIs.

## Important APIs, Types, and Functions
Bitfields cover ADC data source and 12-bit data, AUX enable/convert/sleep/force/rate, input selection bits for calibration/backup/wall/battery/USB/system/battery-temp/chip-temp/AUX1-4, comparator status/enable bits, and comparator source/reference fields. `enum wm831x_auxadc` lists all readable inputs and calibration inputs. `enum wm831x_auxadc_src` names hardware data-source values. `struct wm831x_auxadc_req` stores list node, owner chip, input, completion, data source, and data. APIs are `wm831x_auxadc_read()`, `wm831x_auxadc_read_irq()`, `wm831x_auxadc_read_result()`, `wm831x_auxadc_read_uv()`, `wm831x_auxadc_read_temp()`, and `wm831x_auxadc_read_data()`.

## Control Flow
Callers request a conversion for an input; the implementation queues/serializes requests through the parent auxadc state, starts conversion, completes via IRQ or polling, and returns raw data, microvolts, temperature, or split source/data depending on API. IRQ completion uses `wm831x_auxadc_read_irq()`.

## State and Persistence Behavior
Hardware persists AUX control, selected inputs, comparator thresholds/enables, and latest conversion data. Software request state persists in `struct wm831x_auxadc_req` until completion and parent queues/active masks in `struct wm831x`.

## Dependencies and Integration Points
The header depends on completions, lists, and the parent `struct wm831x`. It integrates with power/charger, thermal, hwmon/IIO-like consumers, interrupt handling, and calibration paths.

## Risks and Test Signals
Risks include reading stale data before source matches requested input, request lifetime misuse for async reads, comparator enable/status confusion, calibration errors in uV/temp helpers, and concurrent conversions without parent locking. Test signals are conversion completion tests, source/data mismatch tests, concurrent request queue tests, uV/temp conversion validation, comparator interrupt tests, and suspend/resume ADC control restoration.
