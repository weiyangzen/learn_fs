## sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_tc.c

## Purpose
Implements TSNEP traffic-control offload for `taprio`, translating gate-control schedules into the hardware's two gate-control lists and handling live schedule changes with cut/extend/insert operations.

## Important APIs, Types, and Functions
Exports `tsnep_tc_init`, `tsnep_tc_cleanup`, and `tsnep_tc_setup`. Internal helpers validate schedules, write GCL operations, compute change limits, choose start times, insert transition operations, extend/cut current cycles, enable a new GCL, handle `TAPRIO_CMD_REPLACE`/`DESTROY`, and answer `TC_QUERY_CAPS`. State is held in `adapter->gate_control_active`, `adapter->gcl[2]`, `adapter->next_gcl`, and `gate_control_lock`.

## Control Flow and State
Validation requires nonzero cycle time, command `TC_TAPRIO_CMD_SET_GATES`, masks within `TSNEP_GCL_MASK`, intervals above hardware minimum, exact sum equal to cycle time, and extension shorter than cycle time. Replace writes the next inactive GCL, selects the current active GCL if any, enables the hardware timeout guard, calculates a safe future start/change time, writes either `TSNEP_GC_TIME` or `TSNEP_GC_CHANGE`, enables list A/B, retries on timeout, marks gate control active, and toggles the next list. Destroy disables gate control. Cleanup disables active gate control.

## Dependencies and Integration Points
Depends on kernel TC taprio offload structures, TSNEP gate-control registers and constants, `tsnep_get_system_time`, netdev `ndo_setup_tc`, and self-test coverage in `tsnep_selftests.c`.

## Risks and Test Signals
Risks are mostly timing and arithmetic: selecting start times beyond 32-bit hardware time reach, incorrect cut/extend choices near phase boundaries, stale inserted-operation bits after timeout or cleanup, off-by-one GCL count handling due to the reserved insertion slot, and lock contention with ethtool self-tests. Test using `tc qdisc replace ... taprio` with valid/invalid schedules, live schedule changes with shorter/longer/different-phase cycle times, destroy/recreate loops, `TC_QUERY_CAPS`, and the optional TSNEP offline self-tests.
