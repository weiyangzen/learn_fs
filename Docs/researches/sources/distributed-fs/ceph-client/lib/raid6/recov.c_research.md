# sources/distributed-fs/ceph-client/lib/raid6/recov.c

Purpose: implements scalar fallback RAID6 recovery for two failed data blocks or one data block plus P.

Important APIs and flow: `raid6_2data_recov_intx1()` temporarily replaces failed data pointers with zero pages and P/Q pointers with failed buffers, regenerates syndromes to get deltas, restores `ptrs`, picks `pbmul` and `qmul`, then reconstructs both data blocks byte by byte. `raid6_datap_recov_intx1()` follows the same pattern for data+P failure and updates P. `raid6_recov_intx1` exposes priority 0 fallback. Userspace-only `raid6_dual_recov()` dispatches failure cases for tests.

State and persistence: mutates caller-provided data/parity buffers and temporarily mutates the `ptrs` array, restoring it before returning.

Dependencies and integration: depends on selected `raid6_call.gen_syndrome`, GF tables, and zero-page helper.

Risks and test signals: temporary pointer rewriting must be restored exactly, and failure indexes drive GF table selection. Signals include RAID6 recovery tests over all disk positions and fallback selection logs.
