<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_events.go -->
# sources/cloud-native/moby/daemon/images/image_events.go

Purpose: emits image events with stable label and reference attributes.

Important APIs and control flow: `LogImageEvent` detaches from cancellation with `context.WithoutCancel`, attempts to load the image to copy config labels, adds the event `name` attribute when provided, and logs through the daemon events service. `copyAttributes` uses `maps.Copy` to avoid mutating the source labels map.

State and persistence: reads image config labels and writes daemon event records.

Dependencies and integration: used by pull, push, tag, delete, import, commit, and prune-related image operations. It integrates `ImageService.GetImage`, API event types, and event actor attributes.

Risks: delete events often happen after image removal, so missing images are ignored. Event emission surviving caller cancellation is intentional but means events may be emitted after request abort.

Test signals: no direct tests here; event assertions in image operation tests cover behavior indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_events.go -->
