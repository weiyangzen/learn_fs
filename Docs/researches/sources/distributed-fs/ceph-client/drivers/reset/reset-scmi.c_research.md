# sources/distributed-fs/ceph-client/drivers/reset/reset-scmi.c

Purpose: ARM SCMI reset protocol bridge that exposes SCMI reset domains to Linux reset consumers.

Important APIs/types/functions: `struct scmi_reset_data` stores `rcdev` and the SCMI protocol handle. `scmi_reset_assert()`, `scmi_reset_deassert()`, and `scmi_reset_reset()` forward directly to `scmi_reset_proto_ops`. `scmi_reset_probe()` obtains protocol ops through `handle->devm_protocol_get()` and registers `nr_resets` from `num_domains_get()`.

Control flow: SCMI bus matching on `SCMI_PROTOCOL_RESET` invokes probe. Runtime reset requests are synchronous SCMI protocol calls to platform firmware.

State and persistence: software state is device-managed; reset state is owned by SCMI firmware/system controller. The file has a file-scope `reset_ops` pointer shared by instances.

Dependencies and integration: requires SCMI core, SCMI reset protocol, OF node from the SCMI device, and reset-controller consumers.

Risks and test signals: the global `reset_ops` assumes compatible protocol ops across instances. Firmware errors propagate to consumers. Test with multiple SCMI transports if supported, absent handle, zero domains, firmware failure paths, and assert/reset/deassert domain calls.
