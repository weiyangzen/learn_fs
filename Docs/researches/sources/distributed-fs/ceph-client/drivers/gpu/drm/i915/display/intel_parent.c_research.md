# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_parent.c

Purpose: provides typed convenience wrappers from display code to the generic parent interface in `display->parent`. It adapts display-driver types to parent callbacks for DPT, frontbuffer, HDCP GSC, IRQ, overlay, panic, PC8, pcode, RPS, stolen memory, VMA, and generic feature queries.

Important functions: wrappers are named `intel_parent_<subsystem>_<operation>()`, such as `intel_parent_overlay_pin_fb()`, `intel_parent_stolen_insert_node()`, `intel_parent_pcode_request()`, `intel_parent_hdcp_gsc_msg_send()`, and `intel_parent_irq_synchronize()`. Several functions guard optional subinterfaces with `if` checks or `drm_WARN_ON_ONCE()`, while many mandatory callbacks are called directly.

Control flow: most functions immediately dispatch to `display->parent->...` with `display->drm` or translated object pointers. Optional subsystems return neutral values (`NULL`, `false`, `-1`, `0`, `-ENODEV`) or no-op when unavailable. Overlay wrappers are used by the legacy overlay implementation to isolate GEM/VMA/frontbuffer details outside display.

State and persistence: this file owns no state; all persistence is in parent subsystems and objects passed through callbacks. It can affect parent-managed references, pinned buffers, stolen-memory nodes, pcode mailbox transactions, and power-management blocks through delegated calls.

Dependencies/integration: depends on `drm/intel/display_parent_interface.h` and `intel_display_core.h`. It is an integration boundary between i915 display code and the parent GPU driver/services.

Risks/test signals: direct dereferences assume mandatory parent subinterfaces exist; optional checks must match real platform capabilities. Tests should cover configurations lacking optional RPS/VMA/overlay/PC8/stolen callbacks, overlay pin/unpin failure paths, pcode timeout behavior, HDCP GSC allocation/free, and stolen-memory allocation/free symmetry.
