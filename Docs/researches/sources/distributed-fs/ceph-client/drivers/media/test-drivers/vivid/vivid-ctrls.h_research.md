# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-ctrls.h

Purpose: declares the Vivid control subsystem entry points and the hardware seek mode enum shared with radio receiver code.

Important APIs and types: `enum vivid_hw_seek_modes` defines bounded seek, wraparound seek, and both-capability seek modes. `vivid_create_controls` builds all V4L2 control handlers for a Vivid instance, and `vivid_free_controls` releases them.

Control flow: Vivid core initialization calls `vivid_create_controls` after device capabilities have been populated. Teardown calls `vivid_free_controls` before the device object is destroyed.

State and persistence: the header stores no state. The implementation uses the passed `struct vivid_dev` to allocate and attach volatile `v4l2_ctrl_handler` state.

Dependencies and integration points: consumers must already know `struct vivid_dev`; the header is included by core, radio, streaming, and node setup code that needs seek modes or control lifecycle functions.

Risks: the public create API takes several capability booleans, so caller and implementation must stay aligned as new node types or controls are added.

Test signals: compile coverage for all Vivid configurations and runtime initialization of all enabled node combinations validate this boundary.
