# sources/distributed-fs/ceph-client/include/drm/intel/intel_lb_mei_interface.h

Purpose: defines the Intel late-binding MEI component interface for authenticated firmware/configuration payload delivery.

Important APIs/types/functions: `INTEL_LB_FLAG_IS_PERSISTENT` requests flash persistence across warm resets. `enum intel_lb_type` identifies fan-control and Ocode payloads. `enum intel_lb_status` maps firmware response statuses including 4ID mismatch, arbitration failure, invalid signature/payload/FPT/manifest/hash, SVN failure, destination mailbox failure, invalid command/header, timeout, and internal IP errors. `struct intel_lb_component_ops` exposes `push_payload()`.

Control flow: a consumer calls `push_payload(dev, type, flags, payload, payload_size)` on the MEI device. The provider returns 0 on success, negative errno for transport failures, or positive firmware status.

State and persistence: payload persistence is firmware-controlled via the persistent flag. The header itself stores no state.

Dependencies and integration: depends on Linux bit and type helpers plus `struct device`. Integrated by Intel graphics/platform code and MEI late-binding service providers.

Risks and test signals: risks include confusing positive firmware status with errno, mishandling persistent payloads, and accepting wrong payload type/signature. Test all status translations, persistent/nonpersistent payloads, payload-size validation, and MEI disconnect/retry behavior.
