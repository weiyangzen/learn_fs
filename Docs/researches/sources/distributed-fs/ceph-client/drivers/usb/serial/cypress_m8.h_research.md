<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/cypress_m8.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/cypress_m8.h

Purpose: constants for the Cypress M8 USB serial driver, including HID report requests, USB IDs, config requests, throttle flags, chip types, and RS-232 control/status bits.

Important APIs/types/functions: `HID_REQ_GET_REPORT`, `HID_REQ_SET_REPORT`, device IDs for DeLorme/Cypress/SAI/FRWD/Powercom/Dazzle, `CYPRESS_SET_CONFIG`, `CYPRESS_GET_CONFIG`, `THROTTLED`, `ACTUALLY_THROTTLED`, `CT_EARTHMATE`, `CT_CYPHIDCOM`, `CT_CA42V2`, `CT_GENERIC`, `CONTROL_DTR`, `CONTROL_RTS`, `CONTROL_RESET`, `UART_RI`, `UART_CD`, `UART_DSR`, `UART_CTS`, and `CYP_ERROR`.

Control flow and state: no executable flow or storage; `cypress_m8.c` uses these definitions to match devices, issue HID feature reports, encode line control, and decode modem/error status.

Dependencies and integration points: Cypress M8 driver, USB HID class requests, USB serial tty behavior, and Cypress firmware application-note protocol.

Risks and test signals: risks include missing ID-table updates for new devices, bit-definition drift, and ambiguous `CYP_ERROR`. Test compile coverage, USB ID matching, report encode/decode paths, throttle flags, and chip-type routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/cypress_m8.h -->
