# sources/distributed-fs/ceph-client/drivers/input/mouse/appletouch.c

## Purpose

`appletouch.c` is a USB input driver for pre-BCM5974 Apple PowerBook/MacBook touchpads. It switches supported Geyser devices into raw sensor mode, reads USB interrupt reports containing sensor banks, reconstructs touch position and pressure from sensor deltas, detects approximate finger count, and reports an absolute single-touch style input device with tool-count keys.

## Important APIs, Types, and Functions

`struct atp_info` describes per-generation sensor counts, coordinate scale factors, USB report length, callback, and fuzz. `struct atp` stores USB/input state, raw and accumulated sensor arrays, smoothing buffers, old coordinates, finger count, idle counter, and reinit work. The USB ID table is built with `ATP_DEVICE()`.

Important functions include `atp_geyser_init()` for USB class control mode switching, `atp_calculate_abs()` for finger/centroid/pressure calculation, `atp_complete_geyser_1_2()` and `atp_complete_geyser_3_4()` for interrupt report decoding, `atp_status_check()` for URB validation, `atp_detect_size()` for 17-inch sensor range detection, and `atp_probe()` / `atp_disconnect()` / PM callbacks for lifecycle.

## Control Flow

Probe locates the first interrupt-in endpoint, allocates `struct atp`, an input device, an URB, and coherent transfer buffer, fills the interrupt URB with the model-specific callback, switches non-Fountain devices into raw mode, sets ABS_X/Y/PRESSURE and button/tool keys, and registers the input device. `atp_open()` submits the URB; `atp_close()` kills it and cancels reinit work.

On each interrupt, the generation-specific callback checks status and exact report length, reorders packed sensor bytes into `xy_cur`, updates baseline/old values, derives positive sensor deltas into `xy_acc`, calculates X and Y centroids with smoothing, reports touch/position/pressure if coordinates and finger count are stable, reports release on empty data, reports the physical button, and resubmits the URB. Geyser 3/4 devices are reinitialized after repeated idle packets to stop high-rate empty reports.

## State and Persistence Behavior

State persists in memory while the USB interface is bound: raw sample arrays, previous baseline, accumulated deltas, smoothing buffers, last reported coordinate, previous finger count, overflow warning flag, and size-detection flag. `atp_reinit()` work resets device mode after idle streaming. No settings are persisted outside the device; module parameters `threshold` and `debug` affect runtime behavior.

## Dependencies and Integration Points

The driver integrates with USB core, USB input ID conversion, coherent DMA buffers, input core, workqueues, and system suspend/resume/reset_resume. It claims Apple HID mouse-protocol interfaces for specific product IDs and competes with generic HID behavior by switching raw sensor mode.

## Risks and Edge Cases

Exact report lengths are required; short or overflowed URBs are dropped. Geyser mode switching can fail or be lost across reset/resume. Sensor baseline handling differs between Geyser 1/2 and 3/4; wrong model data yields bad coordinates. Finger count changes intentionally reset smoothing, which can drop movement around transitions. `atp_disconnect()` does not explicitly cancel `work`; open/close cancels it, but disconnect racing with scheduled idle reinit deserves attention. The 17-inch size detection only expands X range after seeing nonzero high-index sensors.

## Test Signals

Tests should cover probe for each product ID/model info, mode-switch read/write failures, URB status paths including overflow and short packets, sensor reordering for Geyser 1/2/3/4, centroid/finger count fixtures, release/accumulator reset, idle-triggered reinit, open/close URB lifetime, suspend/resume/reset_resume, and disconnect while URBs or reinit work are active.
