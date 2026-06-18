# sources/distributed-fs/ceph-client/drivers/misc/mei/mei_lb.c

## Purpose
This MEI client driver exposes Intel Late Binding firmware payload upload services to Intel graphics drivers through the Linux component framework. Late Binding delivers signed runtime configuration packages, such as fan-controller or voltage-regulator data, to authentication firmware without flashing platform firmware.

## Important APIs, types, and functions
The file defines v1 MKHI request/response structures `mei_lb_req` and `mei_lb_rsp`, v2 protocol structures `mei_lb2_header`, `mei_lb2_rsp_header`, `mei_lb2_req`, and `mei_lb2_rsp`, and GUIDs for MKHI and LB services. Main helpers are `mei_lb_push_payload_v1()`, `mei_lb_check_response_v1()`, `mei_lb_push_payload_v2()`, `mei_lb_check_response_v2()`, and `mei_lb_push_payload()`. The exported component operation is `intel_lb_component_ops.push_payload`. Probe/remove are `mei_lb_probe()` and `mei_lb_remove()`.

## Control flow and state
On MEI client probe, the driver registers a component master and matches Intel PCI requesters for `INTEL_COMPONENT_LB`. A requester calls `push_payload`, which enables the MEI client, selects protocol v2 for `MEI_GUID_LB` or v1 for MKHI, sends one request or multiple chunks, waits for firmware responses, and disables the client. V1 rejects payloads larger than the MEI MTU; v2 splits payloads into MTU-sized chunks and marks first/last flags.

## State and persistence behavior
The driver keeps no persistent private payload state. Each upload is transient and synchronous over MEI. Firmware may apply volatile configuration, while the driver only holds stack or heap request buffers and component binding state.

## Dependencies and integration points
Dependencies include `linux/mei_cl_bus.h`, `linux/component.h`, PCI helpers, UUID helpers, `mkhi.h`, and DRM Intel component headers. It integrates with i915/Xe-style graphics requesters through `drm/intel/intel_lb_mei_interface.h`, with MEI client matching through `mei_cl_device_id`, and with firmware services selected by GUID.

## Risks and test signals
Important risks are protocol mismatch, incorrect endian conversion, chunk boundary errors, MTU underflow for v2 header sizing, firmware error-code propagation, requester/component matching across PCI and auxiliary parent topologies, and leaving the MEI client enabled after failure. Test signals include v1 and v2 upload success, over-MTU v1 rejection, multi-chunk v2 first/last behavior, bad response command/status handling, component bind/unbind, and probe/remove races with graphics drivers.
