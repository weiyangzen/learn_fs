# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nvidia-gpu.c

## Purpose
Implements a PCI I2C master for NVIDIA GPU cards with USB Type-C/UCSI support. The adapter is primarily used to instantiate and communicate with the Cypress CCGx UCSI client behind NVIDIA GPU I2C registers.

## Important APIs, Types, And Functions
`struct gpu_i2c_dev` stores the PCI device, MMIO registers, adapter, and CCGx client. `gpu_i2c_xfer()` is the I2C algorithm transfer function; `gpu_i2c_read()`, `gpu_i2c_write()`, `gpu_i2c_start()`, `gpu_i2c_stop()`, and `gpu_i2c_check_status()` implement register-level cycles. `gpu_i2c_probe()` maps BAR0, allocates MSI, configures the bus, registers the adapter, creates the CCGx UCSI I2C client, and enables runtime PM.

## Control Flow
Probe matches NVIDIA devices with the unknown serial class, maps controller registers, enables pad/timing configuration for 100 kHz I2C, registers an adapter with quirks, and attaches the CCGx/UCSI client using software-node properties. Transfers runtime-resume the device, process each I2C message, use an implicit-start hardware read for reads, manually emit START/address/data for writes, then emit STOP and autosuspend.

## State And Persistence
State is limited to adapter registration, MMIO configuration, runtime PM state, and the child UCSI client. The driver reprograms pad control and timing on resume. It has no filesystem persistence.

## Dependencies And Integration Points
Depends on PCI, MSI allocation, I2C core, runtime PM, power-supply property definitions, and `i2c_new_ccgx_ucsi()` from `i2c-ccgx-ucsi.h`. The adapter advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL` but quirks limit reads to four bytes and combined write-then-read second messages to four bytes.

## Risks
Hardware imposes a maximum four-byte read because the controller sends STOP after each read. Device matching by vendor plus unknown class is intentionally broad and relies on transfer/UCSI failures to reject unexpected devices. `pm_runtime_get_sync()` return handling is not used in the transfer path. STOP error handling is best effort after failures.

## Test Signals
Signals include CCGx UCSI probe success, connector-change handling after runtime resume, bounded read behavior through adapter quirks, NACK returning `-ENXIO`, hardware timeout returning `-ETIMEDOUT`, remove path freeing IRQ vectors, and suspend/resume tests confirming timing/pad registers are restored.
