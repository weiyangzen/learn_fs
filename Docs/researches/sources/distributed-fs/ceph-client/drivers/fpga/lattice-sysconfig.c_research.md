# sources/distributed-fs/ceph-client/drivers/fpga/lattice-sysconfig.c

Purpose: common Lattice sysCONFIG FPGA manager logic independent of the transport. It sequences refresh/program mode, ISC enable/erase, address initialization, bitstream burst write, status polling, finish, and cleanup for devices such as ECP5.

Important APIs and functions: transport callbacks are invoked through `struct sysconfig_priv`. Core helpers include `sysconfig_cmd_write`, `sysconfig_cmd_read`, `sysconfig_read_busy`, `sysconfig_poll_busy`, `sysconfig_read_status`, `sysconfig_poll_status`, `sysconfig_refresh`, `sysconfig_isc_enable`, `sysconfig_isc_erase`, `sysconfig_lsc_init_addr`, `sysconfig_bitstream_burst_write`, `sysconfig_isc_finish`, and `sysconfig_cleanup`. FPGA manager ops are `sysconfig_ops_state`, `sysconfig_ops_write_init`, `sysconfig_ops_write`, and `sysconfig_ops_write_complete`. `sysconfig_probe` validates callbacks, gets optional PROGRAM/INIT/DONE GPIOs, and registers the manager.

Control flow: write-init rejects partial reconfiguration, enters program mode through GPIO refresh if all GPIOs exist or LSC refresh otherwise, enables ISC, erases, initializes the address shift register, and starts burst mode. Write streams bitstream chunks through the transport. Write-complete closes burst mode, waits not busy, verifies DONE/status or DONE GPIO, disables ISC, and invokes cleanup on failure. State reports operating through DONE GPIO when present or the status DONE bit otherwise.

State and persistence: state is `struct sysconfig_priv`, optional GPIO descriptors, and transport callbacks. Hardware state includes sysCONFIG command mode, busy/status bits, optional PROGRAM/INIT/DONE pins, flash/SRAM configuration state, and the target bitstream contents.

Dependencies and integration points: depends on FPGA manager core, gpiod, iopoll, delay helpers, and transport-specific modules such as `lattice-sysconfig-spi.c`. It exports `sysconfig_probe` for those transports.

Risks and test signals: risks include optional GPIO combinations changing refresh semantics, cleanup issuing erase/refresh after partial failures, status-error bit interpretation, and transport completion being required to release bus resources. Test signals are manager state from DONE/status, successful ISC enable/erase sequence, polling timeouts, cleanup after injected transport errors, and registration failure when callbacks are missing.
