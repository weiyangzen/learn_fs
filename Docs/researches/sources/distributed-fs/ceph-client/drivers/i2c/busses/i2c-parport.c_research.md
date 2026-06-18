# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-parport.c

## Purpose
Implements bit-banged I2C over legacy parallel-port adapters. It supports several historical adapter wiring types, optional SMBus Alert for one board type, and binds selected parport numbers through module parameters.

## Important APIs, Types, And Functions
`struct adapter_parm` describes per-adapter SDA/SCL set/get/init line operations. `struct i2c_par` stores the parport device, I2C adapter, bit-bang algorithm data, optional alert client, and list node. `line_set()` and `line_get()` abstract parallel-port register bits. `i2c_parport_attach()` claims a parport and registers an `i2c_bit_add_bus()` adapter; `i2c_parport_detach()` tears it down.

## Control Flow
The parport core calls `match_port` for each port. Attach validates `type` and configured port numbers, allocates state, registers an exclusive parport device, claims the port, sets SDA/SCL high, runs optional init/power line setup, registers the bit-bang I2C bus, optionally creates an SMBus Alert Response Address client and enables parport IRQs, then adds the adapter to a protected list. Detach finds matching adapters, unregisters alert/client and I2C adapter, powers down optional init line, releases parport, and frees state.

## State And Persistence
Module parameters `parport[]` and `type` configure binding. Runtime state is held in a global adapter list protected by `adapter_list_lock`. No durable state exists.

## Dependencies And Integration Points
Depends on parport, `i2c-algo-bit`, I2C core, SMBus alert handling, module parameters, and legacy hardware adapter wiring. It marks adapters as `I2C_CLASS_HWMON`.

## Risks
Wrong `type` can drive incorrect parallel-port pins. Some adapters cannot read SCL, forcing slower timing and reducing clock-stretching visibility. Exclusive parport claiming may fail when another driver owns the port. SMBus Alert depends on parport IRQ support and ARA client registration.

## Test Signals
Test each adapter type with an electrical loopback or known I2C device, verify SDA/SCL idle high and optional init line behavior, scan/read HWMON devices, detach/re-attach ports, module parameter filtering for up to four ports, no-SCL-read slow mode, and SMBus Alert interrupt handling on type 4.
