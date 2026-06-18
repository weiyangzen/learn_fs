# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-simtec.c

Purpose: Simtec generic memory-mapped bit-banged I2C bus driver. It exposes a simple two-line GPIO-like hardware register through `i2c-algo-bit`.

Important APIs/types/functions: `struct simtec_i2c_data` stores IO resource, mapped register, adapter, and `i2c_algo_bit_data`. Bit operations are `simtec_i2c_setsda()`, `simtec_i2c_setscl()`, `simtec_i2c_getsda()`, and `simtec_i2c_getscl()`. Probe/remove manage resource reservation, mapping, bit algorithm setup, and adapter registration.

Control flow: probe allocates state, records platform driver data, gets the memory resource, reserves and maps it, fills adapter fields, wires bit callbacks and timing (`udelay = 20`, `timeout = HZ`), then calls `i2c_bit_add_bus()`. The algorithm bit-bangs START/STOP/address/data using callbacks that write `CMD_SET_SDA` or `CMD_SET_SCL` plus desired state bits to the register and read line state bits back. Remove unregisters the adapter and releases IO resources.

State and persistence: all bus state is represented by the external hardware latch/line state and the bit-algo core. Driver state is per-platform-device and manually allocated/freed. There is no interrupt, PM, or transfer-specific state in this file.

Dependencies/integration: platform resources, MMIO byte access, I2C core, `i2c-algo-bit`, and module platform driver registration.

Risks: manual resource management requires all probe failure paths to free the correct resource. There is no device-tree match table or PM handling. The single register protocol assumes writes with command bits atomically update one line without disturbing the other. Bit-banged timing is fixed and may be too slow/fast for some boards.

Test signals: successful bit-bus registration, SDA/SCL set/get line transitions, arbitration/clock-stretch behavior through `i2c-algo-bit`, IO resource conflict, ioremap failure, adapter registration failure cleanup, and remove cleanup after active clients are gone.
