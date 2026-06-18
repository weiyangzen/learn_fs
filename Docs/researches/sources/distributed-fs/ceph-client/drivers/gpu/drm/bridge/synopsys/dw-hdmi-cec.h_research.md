# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-cec.h

Purpose: declares the callback and platform-data contract for the classic DW-HDMI CEC companion platform driver.

Important APIs/types/functions: `struct dw_hdmi_cec_ops` provides parent callbacks for register `write`, register `read`, hardware CEC `enable`, and `disable`. `struct dw_hdmi_cec_data` passes the parent `dw_hdmi` pointer, ops table, and IRQ to the CEC child.

Control flow: no executable code. The parent HDMI driver creates a `dw-hdmi-cec` platform device with this data; `dw-hdmi-cec.c` consumes it at probe and during CEC adapter operations.

State and persistence: no owned state; all fields are references to parent state or IRQ resources.

Dependencies and integration: depends on an opaque `struct dw_hdmi` and CEC companion driver agreement about register offsets.

Risks: invalid ops pointers or IRQ cause runtime failures. The ABI is private to in-kernel platform data but still must stay synchronized with parent DW-HDMI code.

Test signals: compile coverage for parent and child, CEC platform device creation, and callback invocation during adapter enable/transmit/receive.
