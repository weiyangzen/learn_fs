<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/belkin_sa.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/belkin_sa.h

Purpose: protocol constants for the Belkin serial adapter driver: USB IDs, vendor requests, baud/framing conversions, flow-control bits, and 16550-like status masks.

Important APIs/types/functions: `BELKIN_*_VID/PID`, `BELKIN_SA_SET_*_REQUEST`, `BELKIN_SA_SET_REQUEST_TYPE`, `BELKIN_SA_BAUD()`, `BELKIN_SA_STOP_BITS()`, `BELKIN_SA_DATA_BITS()`, parity/flow constants, `BELKIN_SA_LSR_*`, and `BELKIN_SA_MSR_*`.

Control flow and state: no executable flow or storage; `belkin_sa.c` uses the constants to issue USB control messages and decode interrupt bytes.

Dependencies and integration points: Belkin driver, USB serial core indirectly, and hardware/firmware protocol inferred from adapter behavior.

Risks and test signals: risks include reverse-engineered constants, placeholder unsupported requests, and misuse of baud macro with zero. Test compile coverage and runtime exercise of every request through termios, modem-control, break, flow, and status paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/belkin_sa.h -->
