# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi_msg.h

Purpose: defines the IPA QMI protocol message IDs, maximum encoded sizes, wire-facing C structures, platform/memory helper structures, and extern descriptors implemented by `ipa_qmi_msg.c`.

Important APIs/types: message IDs cover modem indication registration, AP init-driver request, AP init-complete indication, and modem driver-init-complete request. Structures include standard-response wrappers, `ipa_init_modem_driver_req` with platform, route/filter/header/modem memory, endpoint, UC load, hash table, and stats fields, and `ipa_init_modem_driver_rsp` with modem control/default endpoint information.

Control flow: `ipa_qmi.c` populates `ipa_init_modem_driver_req` from runtime IPA memory and endpoint state, sends it to the modem, responds to modem requests using response structures, and sends `ipa_init_complete_ind` when the modem has registered for it.

State/persistence: the header itself is static protocol definition. The request fields encode persistent shared-memory layout and boot-state (`skip_uc_load`) that affect modem initialization.

Dependencies/integration: includes Linux QMI types and is intentionally limited to `ipa_qmi` and descriptor code. It shares memory IDs/offset meaning with `ipa_mem.c`.

Risks: protocol structures are ABI-like. Changing field order/types or size constants without matching descriptor and modem firmware expectations breaks boot. Several fields use "end" as maximum table index rather than byte end; misuse can over-advertise memory.

Test signals: encoded message sizes stay within constants, QMI descriptor arrays compile against every field, modem accepts AP init-driver request, and first/subsequent boot handshakes follow documented message sequence.
