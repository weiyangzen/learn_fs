# sources/distributed-fs/ceph-client/include/linux/soc/qcom/smd-rpm.h

Purpose: This header defines Qualcomm SMD RPM request structures and APIs for communicating resource votes to the Resource Power Manager.

Important APIs/types/functions: It declares RPM resource/request IDs, `struct qcom_smd_rpm`, `struct qcom_smd_rpm_req`, and request/write helpers used to send key/value resource state to RPM over SMD.

Control flow: A client builds one or more RPM requests for a resource, submits them to the RPM handle, and waits for acknowledgement or error from the transport.

State and persistence: RPM keeps active/sleep resource votes for clocks, regulators, bus, and power resources. Client-side request data is transient.

Dependencies and integration: Integrates with Qualcomm SMD, regulators, clocks, interconnect/bus scaling, and legacy RPM power-management code.

Risks and test signals: Resource IDs and state sets are firmware contracts; bad IDs can affect unrelated resources. Test vote apply/remove, sleep/active sets, transport failure, and suspend/resume resource retention.
