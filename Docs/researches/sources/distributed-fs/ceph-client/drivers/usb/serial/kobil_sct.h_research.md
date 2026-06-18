# sources/distributed-fs/ceph-client/drivers/usb/serial/kobil_sct.h

## Purpose
This header defines the KOBIL smart-card terminal vendor request numbers and bitfields used by `kobil_sct.c`. It maps baud/parity/stop settings, status-line operations, queue purge operations, status-line query bits, and hardware/firmware version selectors.

## Important APIs, Types, and Constants
`SUSBCRequest_SetBaudRateParityAndStopBits` combines `SUSBCR_SBR_*` baud bits, `SUSBCR_SPASB_*` parity bits, and stop-bit bits into one vendor request value. `SUSBCRequest_SetStatusLinesOrQueues` uses `SUSBCR_SSL_*` values for RTS/DTR and queue purge operations. `SUSBCRequest_GetStatusLineState` returns `SUSBCR_GSL_*` status bits including RXCHAR, TXEMPTY, CTS, DSR, RLSD, BREAK, ERR, and RING. `SUSBCRequest_Misc` and `SUSBCRequest_GetMisc` provide reset and version operations.

## Control Flow
`kobil_sct.c` uses these constants during open to set default Adapter B/K line settings and reset queues, during termios changes to encode baud/parity/stop selections, during modem control to set/clear RTS or DTR, during `TIOCMGET` to read DSR state, and during `TCFLSH` to reset all queues.

## State and Persistence
The header is stateless. The values sent with these requests affect transient reader hardware state such as line configuration, queues, and modem outputs.

## Dependencies and Integration Points
It is private to the KOBIL driver and encodes the contract with KOBIL firmware. User-visible integration is indirect through TTY termios, modem ioctls, and flush ioctls.

## Risks
The masks permit more baud rates than the C driver exposes; adding support must validate firmware behavior per product. DTR behavior is product-specific in the driver, and incorrect use of status-line bits could affect smart-card reader operation. Version field comments describe packed values but the driver reads raw bytes.

## Test Signals
Validate baud/parity/stop request values against hardware, RTS/DTR operations per product, queue purge behavior, status-line bit mapping, and hardware/firmware version retrieval for all supported KOBIL products.
