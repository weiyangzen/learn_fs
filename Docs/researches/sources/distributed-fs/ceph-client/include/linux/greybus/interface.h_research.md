<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/interface.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/interface.h

Purpose: This header defines Greybus interfaces, the per-module physical/logical attachment points that own control connections, manifests, bundles, identity fields, quirks, and activation state.

Important APIs/types/functions: `enum gb_interface_type` covers invalid, unknown, dummy, UniPro, and Greybus. Quirk bits disable CPort features, init status, GMP IDs, bundle activate, PM, or force disable/legacy mode switch. `struct gb_interface` embeds a device and stores control, bundle list, module linkage, manifest descriptors, interface/device IDs, features, DDBL/vendor/product IDs, serial, host/module pointers, quirks, mutex, disconnected/ejected/removed/active/enabled/mode-switch/DME flags, mode-switch work, and completion. APIs create, activate/deactivate, enable/disable, add/del/put, handle mailbox events, and request mode switch.

Control flow, state, and persistence: A module creates interfaces; activation/control reads identity and manifest, creates bundles, and enables transport. Mode switching uses work/completion state. Flags distinguish physical removal, logical ejection, active control, and enabled runtime state.

Dependencies/integration: It coordinates host devices, modules, control, bundles, manifests, workqueues, completions, and device core.

Risks and test signals: Interface state transitions are complex around ejection, mode switch, forced disable, and PM quirks. Tests should cover activation failure unwind, manifest descriptor list cleanup, enable/disable idempotency, mailbox event handling, mode-switch timeout/completion, quirk behavior, and removal during active operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/interface.h -->
