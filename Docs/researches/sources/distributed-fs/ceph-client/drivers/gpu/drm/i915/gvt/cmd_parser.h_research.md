# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/cmd_parser.h

Purpose: exposes the GVT command parser lifecycle and scan entry points to the rest of the GVT scheduler/submission code.

Important APIs/types/functions: declares `GVT_CMD_HASH_BITS`, forward declarations for `struct intel_gvt`, `struct intel_shadow_wa_ctx`, `struct intel_vgpu`, and `struct intel_vgpu_workload`, and prototypes for `intel_gvt_init_cmd_parser()`, `intel_gvt_clean_cmd_parser()`, `intel_gvt_scan_and_shadow_ringbuffer()`, `intel_gvt_scan_and_shadow_wa_ctx()`, `intel_gvt_update_reg_whitelist()`, and `intel_gvt_scan_engine_context()`.

Control flow and state: no executable logic. The prototypes define the parser phases used by GVT: initialize opcode tables, scan/shadow ring buffers, scan/shadow workaround contexts, update the register whitelist from default contexts, scan engine contexts, and clean parser state.

Dependencies and integration points: included by GVT core/scheduler code that owns `intel_gvt`, `intel_vgpu_workload`, and workaround-context objects. The hash-bit constant must match the command table declaration in the owning `intel_gvt` structure.

Risks and test signals: API misuse can skip command validation before workload submission. Test signals are successful GVT builds, parser init before workload execution, cleanup on GVT teardown, and scheduler paths invoking ring, WA context, and engine context scans at the expected points.
