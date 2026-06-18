# sources/distributed-fs/ceph-client/drivers/media/common/cypress_firmware.c

Purpose: downloads Intel HEX-style firmware records into Cypress AN2135/AN2235/FX2 USB controller RAM and restarts the controller CPU.

Important APIs/functions: exported `cypress_load_firmware()` is the public loader. `usb_cypress_writemem()` sends vendor request `0xa0` to write RAM/control-space bytes. `cypress_get_hexline()` parses one firmware record into `struct hexline`. Static `cypress[]` maps loader type to controller name and CPU control/status register (`0x7f92` or `0xe600`).

Control flow: loader allocates a hexline buffer, writes `1` to the CPU control register to stop execution, iterates firmware records, writes each record payload to its target address, then writes `0` to restart. Short USB writes and parse failures become errors.

State/persistence: no persistent kernel state; firmware is written into device RAM and affects device execution after restart.

Dependencies/integration: depends on Linux USB core, firmware loader, and callers passing a valid type constant from `cypress_firmware.h`.

Risks/test signals: no checksum validation is performed despite storing `chk`; type is not bounds-checked before indexing `cypress[]`; extended linear address handling assumes type `0x04`. Tests should cover malformed/truncated records, short USB writes, invalid type handling by callers, stop/start failures, and representative FX2 firmware load.
