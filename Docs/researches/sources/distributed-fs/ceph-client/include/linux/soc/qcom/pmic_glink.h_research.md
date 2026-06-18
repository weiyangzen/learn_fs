# sources/distributed-fs/ceph-client/include/linux/soc/qcom/pmic_glink.h

Purpose: This header defines the Qualcomm PMIC GLINK client API for battery manager, USB-C, and related PMIC message owners.

Important APIs/types/functions: It defines owner IDs for BATTMGR, USBC, and USBC_PAN, message types request/response and notify, `struct pmic_glink_hdr`, `pmic_glink_send`, `devm_pmic_glink_client_alloc`, and `pmic_glink_client_register`.

Control flow: A client allocates a managed PMIC GLINK client with owner ID, receive callback, PDR callback, and private pointer, registers it, and sends messages containing the common header plus payload.

State and persistence: Client registration and callback/private data live in the PMIC GLINK core. Remote PMIC service state may change during PDR/SSR.

Dependencies and integration: Uses device-managed allocation, GLINK transport, and Qualcomm PMIC subsystems. Integrates with USB-C, battery, charger, and power-supply drivers.

Risks and test signals: Owner/opcode mismatches or endian mistakes break remote protocol. Test client registration before service availability, send/response, notifications, PDR callback delivery, and teardown during remote restart.
