# sources/distributed-fs/ceph-client/include/net/nfc/nci_core.h

Purpose: declares the NCI core runtime device model, driver callbacks, connection/HCI support, request machinery, and SPI/UART transport helper interfaces.

Important APIs and types: `enum nci_flag` and `enum nci_state` model initialization, up/down, discovery, poll/listen activation, and data exchange. `struct nci_ops` provides driver hooks for transport open/close/send, setup, firmware, RF protocol mapping, secure elements, and HCI callbacks. `struct nci_dev` stores NFC core device, NCI/HCI state, connection lists, timers, workqueues, command/rx/tx queues, request completion fields, discovered targets, controller capabilities, reassembly buffers, and activation metadata. SPI and UART helper structs define transport state and callbacks.

Control flow: drivers allocate/register an NCI device, core reset/init and setup run as serialized requests, command/data queues feed transport send, rx workers dispatch rsp/ntf/data packets, and connection credits gate data flow.

State and persistence: runtime-only controller state includes NCI version/features, supported interfaces, active targets, NFCEE/HCI pipe state, current connection parameters, queues, timers, and driver data.

Dependencies and integration points: integrates generic NFC core, NCI wire formats, HCI-over-NCI, SPI, TTY/UART, skbuff queues, workqueues, timers, completions, and secure element callbacks.

Risks and test signals: risks include request timeout races, credit accounting errors, data reassembly leaks, state transition bugs, and transport close while work is pending. Test reset/init, set-config, discovery/select/deactivate, logical connection create/close, data exchange, HCI session init, SPI CRC mode, UART line discipline setup, and unregister teardown.
