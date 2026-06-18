# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_parent.h

Purpose: declares typed display-to-parent wrapper APIs for shared services outside the display core.

Important APIs: DPT create/destroy/suspend/resume; frontbuffer get/ref/put/flush; HDCP GSC messaging/context; IRQ enabled/synchronize; overlay lifecycle/pin/object lookup; panic setup; PC8 block/unblock; pcode read/write/request; RPS helpers; stolen memory insert/remove/query/node allocation; VMA fence id; AUX CCS/fenced-region/vGPU queries; display fence priority.

Control flow/state: no state. The broad API mirrors parent interface capabilities while keeping display code independent of the raw parent function table.

Dependencies/integration: included by overlay, HDCP, stolen-memory, DPT, power, and display support code. Forward declarations keep it decoupled from concrete parent implementations.

Risks/test signals: wrapper signatures must stay synchronized with `display_parent_interface`. Build failures catch many mismatches; runtime tests should cover optional-parent absence.
