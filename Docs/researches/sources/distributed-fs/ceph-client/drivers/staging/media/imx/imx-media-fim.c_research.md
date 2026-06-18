# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-fim.c

## Purpose

`imx-media-fim.c` implements the i.MX Frame Interval Monitor. It observes EOF timestamps, compares averaged frame intervals against a nominal interval, and emits `V4L2_EVENT_IMX_FRAME_INTERVAL_ERROR` when timing drift exceeds configured tolerances. It also defines controls for enabling the monitor and tuning averaging, skip count, tolerance bounds, and optional input-capture parameters.

## Important APIs, Types, and Functions

`struct imx_media_fim` stores the owning subdevice, control handler, control clusters, spinlock-protected active values, counters, timestamp sum, nominal interval, input-capture completion, and stream state. Exported functions are `imx_media_fim_init()`, `imx_media_fim_free()`, `imx_media_fim_add_controls()`, `imx_media_fim_set_stream()`, and `imx_media_fim_eof_monitor()`.

Internal functions include `reset_fim()`, `update_fim_nominal()`, `frame_interval_monitor()`, `send_fim_event()`, `fim_acquire_first_ts()`, `fim_s_ctrl()`, and `init_fim_controls()`.

## Control Flow

Initialization allocates the FIM object and control handler. A CSI adds those controls to its subdevice handler when the IDMAC capture link is enabled. On stream-on, `imx_media_fim_set_stream()` locks the enable control, resets cached control values, computes the nominal microsecond frame interval from the active pad interval, and optionally waits for the first input-capture timestamp. EOF monitoring skips configured initial frames, computes absolute interval error from the previous timestamp, optionally ignores out-of-range errors above `tolerance_max`, averages `num_avg` samples, and notifies the subdevice if the average exceeds `tolerance_min`.

## State and Persistence Behavior

All state is volatile. Active control values are copied into the FIM state at reset so streaming behavior is stable. The spinlock protects timing counters and cached control values; the V4L2 control lock serializes stream-on changes with control writes. Input-capture edge changes are rejected while streaming.

## Dependencies and Integration Points

FIM depends on V4L2 custom controls from `media/imx.h`, V4L2 subdevice event notification, IRQ type values for optional input capture configuration, and CSI EOF callbacks. In this source snapshot only the EOF-monitor path is implemented; input capture controls and completion scaffolding exist but no event callback is wired in this file.

## Risks and Edge Cases

If the frame interval denominator is zero, FIM disables itself. EOF-derived timestamps include interrupt latency, so averaging is used to reduce noise but cannot eliminate systematic delay. `tolerance_max <= tolerance_min` disables the upper bound. Without input capture, `num_skip` is forced to at least one because the first EOF interval cannot be measured accurately.

## Test Signals

Test control defaults and clustering, enabling/disabling while idle and streaming, denominator-zero disabling, skip and averaging behavior, tolerance-min event generation, tolerance-max ignored samples, EOF timestamp jitter, event subscription on CSI/capture nodes, and attempted input-capture edge changes during streaming.
