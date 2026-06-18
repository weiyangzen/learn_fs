# sources/distributed-fs/ceph-client/drivers/counter/rz-mtu3-cnt.c

Purpose: platform driver for Renesas RZ/G2L MTU3a phase-counting counters, exposing two 16-bit counters and one mutually exclusive 32-bit cascaded counter.

Important APIs/types/functions: `struct rz_mtu3_cnt` holds module clock, mutex, MTU channel array, per-logical-count enable flags, and cached 16/32-bit ceilings. Helper functions map logical count IDs to hardware channels, validate shared mode, initialize/terminate 16-bit or cascaded 32-bit counting, and read/write shared register fields. Counter callbacks cover count, function, direction, ceiling, enable, action, and device extensions `cascade_counts_enable` and `external_input_phase_clock_select`.

Control flow: probe obtains parent `struct rz_mtu3`, points at channels 1 and 2, seeds ceilings, sets channel devices, enables runtime PM, fills three counts/four signals/device extensions, and registers. Enable writes request channels, configure TMDR/TCR/TIOR and enable hardware; disabling releases channels and PM references. Count and ceiling operations verify that the logical counter matches the current `TMDR3.LWA` cascade mode. Action reads combine selected function, selected external phase clock pair, and signal ID to report rising/both/none behavior.

State and persistence: hardware state includes TMDR1 mode, TMDR3 shared cascade/clock-select bits, TCNT/TGRA registers, and channel busy/enabled flags managed by the MFD layer. Driver caches ceilings and enable state. Runtime PM gates the shared module clock.

Dependencies and integration: depends on `linux/mfd/rz-mtu3.h`, parent MFD channel ownership helpers, runtime PM, clocks, and Generic Counter. It registers as `rz-mtu3-counter` platform child.

Risks: 16-bit and 32-bit views share hardware; wrong `cascade_counts_enable` changes can invalidate active logical counters and return `-EBUSY`. Some phase-counting modes are TODO/unimplemented. Several `pm_runtime_get_sync()` results are ignored. Channel ownership/busy checks are essential to avoid conflicting with other MTU3 users.

Test signals: enable/disable each logical count, verify channel request/release behavior, switch cascade mode and confirm invalid counters return `-EBUSY`, read/write 16-bit and 32-bit ceilings with range checks, function and action reports for all supported modes and clock-select values, runtime suspend/resume clock behavior, and coexistence with other MTU3 clients.
