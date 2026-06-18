# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop.c

Purpose: main common FlexCop module. It wires the chip into DVB core, coordinates reset/initialization/teardown, exports demux data injection helpers, and owns the debug module parameter and global zero register value.

Important APIs/functions: exported `flexcop_device_kmalloc()`, `flexcop_device_kfree()`, `flexcop_device_initialize()`, `flexcop_device_exit()`, `flexcop_pass_dmx_data()`, `flexcop_pass_dmx_packets()`, and `flexcop_reset_block_300()`. Internal `flexcop_dvb_init()` registers `dvb_adapter`, `dvb_demux`, `dmxdev`, hardware/memory frontends, and `dvb_net`; `flexcop_dvb_exit()` unwinds them.

Control flow: initialization zeroes `ibi_zero`, resets the chip/peripherals, determines revision, initializes SRAM and filters, disables SMC, registers DVB, initializes I2C, reads/programs MAC filtering, attaches frontend, then logs completion. Any failure calls `flexcop_device_exit()`, which tears down frontend, I2C, and DVB based on init state.

State/persistence: `init_state` gates teardown; `dvb_adapter.proposed_mac` stores the runtime MAC; no durable persistence. `b2c2_flexcop_debug` is a module parameter.

Dependencies/integration: bus drivers allocate `struct flexcop_device`, fill register callbacks and bus-specific operations, then call initialize/exit. Depends heavily on Linux DVB demux/net, I2C, and frontend helper code.

Risks/test signals: partial-init unwinding, MAC-read failure path, reset timing, and missing bus callbacks are key risks. Tests should simulate failures after DVB/I2C/frontend stages, feed start/stop through demux callbacks, and verify no adapter/I2C leaks.
