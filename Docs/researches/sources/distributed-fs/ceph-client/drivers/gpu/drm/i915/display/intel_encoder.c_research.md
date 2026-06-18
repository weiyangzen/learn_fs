<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_encoder.c

## Purpose
This file contains generic encoder helper utilities for delayed link checks, HPD blocking, suspend/shutdown fan-out, and digital port allocation.

## Important APIs, Types, and Functions
Public functions are `intel_encoder_link_check_init()`, `intel_encoder_link_check_queue_work()`, `intel_encoder_link_check_flush_work()`, `intel_encoder_block_all_hpds()`, `intel_encoder_unblock_all_hpds()`, `intel_encoder_suspend_all()`, `intel_encoder_shutdown_all()`, and `intel_dig_port_alloc()`. The internal work item callback invokes the encoder's `link_check` function.

## Control Flow
Link-check initialization stores a delayed work item and callback. Queueing schedules it on `display->wq.unordered`; flushing cancels synchronously. HPD block/unblock iterates all encoders if the platform has display. Suspend and shutdown take global modeset locks, call optional per-encoder `suspend` or `shutdown`, unlock, then call optional completion hooks. Digital port allocation zeroes state, initializes invalid MMIO/AUX defaults, sets `max_lanes` to 4, and initializes the HDCP mutex.

## State and Persistence Behavior
Delayed work is stored in each encoder and persists until canceled. Digital port allocation creates persistent encoder-private state initialized to safe invalid values. Suspend/shutdown do not persist additional state but fan out to encoder-specific callbacks.

## Dependencies and Integration Points
The file depends on display workqueues, hotplug helpers, modeset locking, encoder callback fields, and HDCP mutex state in `struct intel_digital_port`. It is used by DP/HDMI and other encoder implementations that need link checks and lifecycle fan-out.

## Risks
Delayed work must be flushed before encoder destruction to avoid use-after-free. Suspend/shutdown callbacks run under global modeset locks, so callback implementations must avoid lock inversions. HPD block/unblock should be paired around operations that cannot tolerate hotplug interrupts.

## Test Signals
Signals include link-check work firing and canceling cleanly, suspend/shutdown callback ordering, HPD interrupt masking during block windows, and default digital-port fields preventing accidental MMIO/AUX access before initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_encoder.c -->
