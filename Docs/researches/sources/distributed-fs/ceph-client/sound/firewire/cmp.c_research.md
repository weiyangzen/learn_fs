# sources/distributed-fs/ceph-client/sound/firewire/cmp.c

Purpose: implements IEC 61883-1 Connection Management Procedures for point-to-point FireWire isochronous connections used by drivers such as BeBoB.

Important APIs/functions: `cmp_connection_init`, `cmp_connection_check_used`, `cmp_connection_destroy`, `cmp_connection_reserve`, `cmp_connection_release`, `cmp_connection_establish`, and `cmp_connection_break`. Internal helpers compute MPR/PCR addresses, perform compare-swap PCR modification, encode oPCR speed/overhead, and validate plug availability.

Control flow and state: init reads iMPR/oMPR, validates plug index, initializes ISO resources, and records max speed. Reserve allocates channel/bandwidth. Establish compare-swaps the target iPCR/oPCR to set point-to-point connection/channel/speed, retrying resource update on bus reset. Break clears broadcast/P2P bits and leaves resources for the caller to release. State is held in `cmp_connection` and protected by its mutex.

Dependencies/integration: depends on FireWire CSR register constants, `snd_fw_transaction`, `fw_iso_resources`, and device max speed. Risks include PCR races with other hosts, bus-reset generation handling, oPCR overhead encoding limits, stale `last_pcr_value`, and resource leaks if callers skip release. Test signals are successful reserve/establish/break/release cycles, `-EBUSY` when plug is in use, and recovery after `-EAGAIN` bus reset updates.
