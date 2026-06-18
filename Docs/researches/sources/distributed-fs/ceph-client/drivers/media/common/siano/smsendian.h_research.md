<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsendian.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsendian.h

## Purpose
`smsendian.h` is the small public declaration header for Siano endian conversion helpers.

## Important APIs, Types, and Functions
It declares `smsendian_handle_tx_message()`, `smsendian_handle_rx_message()`, and `smsendian_handle_message_header()`, all taking raw message-buffer pointers.

## Control Flow
Transport code includes this header and invokes the helpers around firmware message transmission/reception. The implementation controls whether any actual work is done through `__BIG_ENDIAN`.

## State and Persistence Behavior
No state is declared. All behavior is in-place transformation of supplied buffers.

## Dependencies and Integration Points
The header includes `<asm/byteorder.h>` and is paired with `smsendian.c`. It deliberately avoids pulling in all Siano core types, because callers only need function prototypes.

## Risks and Test Signals
The primary risk is missing integration in a transport driver, which would make Siano firmware protocol messages fail on big-endian architectures. Test signals include successful builds on endian-diverse configurations and transport tests that exercise both control responses and raw payload messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsendian.h -->
