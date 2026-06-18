# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hdcp_gsc.c

## Purpose
`i915_hdcp_gsc.c` implements the i915 display HDCP-over-GSC interface. It allocates command buffers, pins them in the media GT GGTT, builds GSC HECI headers, submits synchronous HDCP messages to GSC firmware, handles pending replies, and exports callbacks to display HDCP code.

## Important APIs, Types, and Functions
The local `struct intel_hdcp_gsc_context` stores the i915 pointer, pinned VMA, input command mapping, and output command mapping. Interface methods are `intel_hdcp_gsc_check_status()`, `intel_hdcp_gsc_context_alloc()`, `intel_hdcp_gsc_context_free()`, and `intel_hdcp_gsc_msg_send()`. Helpers include `intel_hdcp_gsc_initialize_message()` and `intel_gsc_send_sync()`. The exported interface object is `i915_display_hdcp_interface`.

## Control Flow
Status check verifies a media GT exists and the GSC firmware is running. Context allocation allocates the wrapper, creates a two-page shmem GEM object for input/output, maps it with the GT's coherent map type, creates a VMA in the media GGTT, pins it `PIN_GLOBAL | PIN_HIGH`, zeroes the buffer, and stores input/output page pointers. Message send validates GSC use, rejects payloads larger than one page minus header, clears both pages, generates a host session ID, emits an MTL HECI header for HDCP, copies the input payload, and calls `intel_gsc_send_sync()` with GGTT offsets. If GSC returns message-pending, it retries up to 20 times with 50 ms sleeps using the message handle in the header. On success it bounds the reply size and copies output payload to the caller.

## State and Persistence Behavior
The context persists across display HDCP transactions until freed. The two-page GEM object remains pinned and mapped; input is at page 0 and output at page 1. Each message overwrites headers/payloads and uses a fresh host session ID. Firmware state is external in the media GT GSC.

## Dependencies and Integration Points
This file integrates display HDCP code, media GT/GSC uC firmware, HECI command submission, GEM shmem allocation, VMA GGTT pinning, coherent map selection, random bytes, sleep/retry logic, and DRM KMS logging. It is wired through `i915_driver.c`'s display parent interface.

## Risks
`intel_hdcp_gsc_context_free()` calls `i915_vma_unpin_and_release()` twice on the same `vma` pointer in the inspected source, which is a serious double-release risk unless the helper nulls the pointer and tolerates a second call. Message size arithmetic must include headers correctly to avoid firmware buffer overruns. Pending-message retry has a fixed one-second total wait and may fail slow firmware. Status checks rely on `i915->media_gt`; platforms without media GT return not ready.

## Test Signals
HDCP 2.2 authentication on GSC platforms, GSC firmware-not-running status path, oversized input/output ENOSPC, pending-message retry behavior, command submission failure propagation, reply-size mismatch logs, context allocation failure unwinds, and KASAN/Kmemleak coverage for context free.
