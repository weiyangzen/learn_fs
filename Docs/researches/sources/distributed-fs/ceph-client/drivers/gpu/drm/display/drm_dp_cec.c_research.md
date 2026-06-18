# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_cec.c

Purpose: implements HDMI CEC tunneling over DisplayPort AUX for DP-to-HDMI/USB-C-to-HDMI adapters that advertise the DP CEC tunneling DPCD capability.

Important APIs/functions: CEC adapter ops write `DP_CEC_TUNNELING_CONTROL` to enable, update `DP_CEC_LOGICAL_ADDRESS_MASK`, write TX message buffer/info with retry count, optionally toggle snooping, and print adapter status from DP branch descriptor. `drm_dp_cec_irq()` handles IRQ_HPD service interrupts by checking `DP_DEVICE_SERVICE_IRQ_VECTOR_ESI1`, reading tunneling IRQ flags, receiving RX messages, reporting TX success/error/NACK to CEC core, and clearing flags. `drm_dp_cec_attach()` creates or updates a CEC adapter based on current DPCD capabilities and connector physical address, including monitor-all and multi-logical-address capability. `drm_dp_cec_set_edid()` derives physical address from EDID; `drm_dp_cec_unset_edid()` invalidates it and optionally schedules delayed unregister; register/unregister connector helpers initialize delayed work and tear down the adapter.

Control flow: all public paths first reject AUX adapters without a transfer function. `aux->cec.lock` protects adapter lifecycle and DPCD capability checks. The module parameter `drm_dp_cec_unregister_delay` debounces HPD low events, with 0 immediate unregister and values >=1000 meaning never unregister.

State and persistence: state lives in `aux->cec`: connector pointer, CEC adapter pointer, lock, and delayed unregister work. Hardware state is DPCD CEC control/logical-address/TX/RX registers. Adapter lifetime tracks EDID/HPD capability rather than merely connector lifetime.

Dependencies and integration points: depends on CEC core, DRM connector/EDID helpers, DP DPCD helpers, and IRQ_HPD handling by DP drivers. Used by drivers that call DP CEC register/attach/unset functions when connector EDID or HPD changes.

Risks: many adapters advertise tunneling but lack a physical CEC wire, producing isolated `/dev/cecX` devices. MST CEC is not supported. DPCD reads may fail when HPD is low; delayed unregister intentionally trades stale device presence for HPD glitch tolerance. `attempts - 1` underflows if CEC core ever passes zero attempts, though normal CEC callers should not.

Test signals: known working DP-to-HDMI adapters, CEC adapter creation/removal on EDID changes, HPD glitch debounce, RX/TX IRQ handling, logical address programming, monitor-all capability, and unregister-delay module parameter behavior.
