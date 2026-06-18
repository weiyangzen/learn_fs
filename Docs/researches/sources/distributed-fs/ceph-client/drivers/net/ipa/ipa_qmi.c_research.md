# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi.c

Purpose: implements the AP/modem QMI handshake that gates normal IPA modem operation after IPA setup and after modem restarts.

Important APIs/functions: `ipa_qmi_setup()` creates a host QMI server for modem requests and a client lookup for the modem service. `ipa_qmi_teardown()` cancels pending init work and releases handles. Server handlers process `INDICATION_REGISTER` and `DRIVER_INIT_COMPLETE` requests. Client work sends `INIT_DRIVER` to the modem and waits up to one minute. `ipa_qmi_ready()` starts the modem netdev when modem driver and microcontroller readiness requirements are satisfied.

Control flow: when the modem QMI service appears, `ipa_client_new_server()` records its QRTR address and schedules `ipa_client_init_driver_work()`. That work builds an init request from IPA memory/endpoints, sends it, and marks `modem_ready` on response. The modem sends `DRIVER_INIT_COMPLETE`, setting `uc_ready`. On first boot, the modem must also register for and receive `INIT_COMPLETE`; subsequent boots only require modem and UC readiness. `server_bye` resets modem-ready and indication flags when the modem node disappears.

State/persistence: `struct ipa_qmi` stores server/client handles, modem QRTR address, work item, and readiness flags. The init request is a static structure reused after one-time field population, with `skip_uc_load` refreshed for each request.

Dependencies/integration: depends on Linux QRTR/QMI, QMI element-info tables, IPA local memory offsets, endpoint name map, modem netdev start, and UC loaded state.

Risks: the static init request assumes a single IPA instance and mostly immutable memory configuration. Stats size fields appear to add `ipa->mem_offset` to sizes, which should be scrutinized against modem protocol expectations. Handshake ordering is subtle: first boot requires an indication, later boots intentionally do not.

Test signals: QMI services register, init-driver requests contain expected TLVs, first modem boot waits for indication registration, subsequent SSR boot restarts after init-driver/UC ready, and modem netdev starts only once readiness is complete.
