# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk_sip_svc.h

Purpose: This MediaTek header defines Secure Monitor Call/SIP service IDs used by kernel drivers to request secure firmware services.

Important APIs/types/functions: It provides preprocessor constants for MediaTek SIP service function IDs and related arguments. No local state or implementation is present.

Control flow: Consumers pass these IDs to ARM SMCCC helpers to invoke secure-world services for power, clocks, memory, or SoC-specific controls.

State and persistence: State is maintained by secure firmware and affected hardware registers. Results may persist across normal-world driver lifetimes.

Dependencies and integration: Integrates with MediaTek platform drivers and ARM SMCCC firmware interfaces.

Risks and test signals: Wrong function IDs can fail silently, return firmware errors, or alter secure hardware state unexpectedly. Test firmware return codes, unavailable-firmware handling, and SoC-specific service compatibility.
