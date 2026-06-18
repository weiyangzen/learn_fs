# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sibyte.c

Purpose: SiByte board SMBus adapter driver. It registers two fixed numbered SMBus adapters backed by SB1250 CSR registers, one at 100 kHz and one at 400 kHz.

Important APIs/types/functions: `struct i2c_algo_sibyte_data` records private data, bus number, and CSR base. `smbus_xfer()` implements SMBus quick, byte, byte-data, and word-data operations by writing SB1250 command/start/data registers. `bit_func()` advertises functionality. `i2c_sibyte_add_bus()` assigns the algorithm, sets frequency/control registers, and registers the adapter. Static arrays define the two adapters and their CSR bases.

Control flow: module init registers adapter 0, then adapter 1; failure to add the second removes the first. Each transaction busy-waits while `M_SMB_BUSY`, programs command/data fields according to SMBus size and direction, writes `R_SMB_START`, busy-waits again, clears and maps errors, and copies one or two returned bytes from `R_SMB_DATA`.

State and persistence: adapters and algo data are static globals. Hardware base addresses are fixed CKSEG1 CSR addresses. There is no locking, timeout, interrupt handling, or dynamic device discovery in this driver.

Dependencies/integration: MIPS SiByte headers and CSR accessors, Linux I2C SMBus algorithm, HWMON class scanning, and module init/exit.

Risks: busy waits have no timeout and can spin forever if hardware remains busy. Only a subset of SMBus is supported; no block or process-call support. Fixed adapter numbers and static globals assume a narrow board environment. Error mapping depends on `M_SMB_ERROR_TYPE` only.

Test signals: module init/exit cleanup, both bus frequencies, quick/byte/byte-data/word-data read/write, SMBus error and NACK mapping, adapter numbering collisions, and behavior if busy never clears.
