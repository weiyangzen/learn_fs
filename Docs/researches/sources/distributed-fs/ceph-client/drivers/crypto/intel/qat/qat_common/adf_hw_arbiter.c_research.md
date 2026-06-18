# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_hw_arbiter.c

Purpose: configures the QAT hardware service arbiter, maps AE worker threads to arbiters, updates per-bank ring arbitration enable bits, and supports disabling one thread for heartbeat error injection.

Important APIs: `adf_init_arb`, `adf_update_ring_arb`, `adf_exit_arb`, and `adf_disable_arb_thd`. CSR write macros compute service arbiter and worker-thread mapping register addresses.

Control flow and state: init reads `arb_info` and platform thread-to-arbiter mapping, writes four service-arbiter config registers, and maps active AEs. Ring updates compute enabled TX/RX pair intersections and write per-bank arbitration enable masks. Exit clears all thread mappings and ring enables. Error injection clears one thread nibble in the AE mapping.

Dependencies and integration: depends on `adf_hw_device_data` callbacks, transport bank CSR base, CSR ops, and ring mask conventions. Called during device init/exit and ring lifecycle.

Risks and test signals: wrong mapping can starve rings or route services incorrectly. Test transport with each service mix, ring pair enable/disable, SR-IOV modes, and heartbeat injection thread disable on strand/admin-thread aliases.
