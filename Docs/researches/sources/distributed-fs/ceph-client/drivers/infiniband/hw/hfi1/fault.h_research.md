# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/fault.h

Purpose: conditional public interface and state definition for HFI1 packet fault injection.

Important APIs/types: when fault injection debugfs is enabled, `struct fault` contains `fault_attr`, debugfs dentry, per-opcode RX/TX counters, skip controls, opcode bitmap, enable/suppress/opcode flags, and direction. It declares `hfi1_fault_init_debugfs()`, `hfi1_fault_exit_debugfs()`, `hfi1_dbg_should_fault_tx()`, `hfi1_dbg_should_fault_rx()`, and `hfi1_dbg_fault_suppress_err()`. Otherwise it provides inline stubs returning no fault and success.

Control flow: callers can invoke the API unconditionally. Build configuration decides whether debugfs controls exist and whether runtime checks can inject faults.

State and persistence: with fault injection enabled, state persists per `struct hfi1_ibdev` through `ibd->fault`. With the stub configuration, no state exists and packet paths are unaffected.

Dependencies and integration: includes Linux fault injection, dcache, bitops, kernel, RDMA VT, and `hfi.h`. Integrated into debugfs setup and send/receive packet paths.

Risks: because the enabled structure is directly manipulated by debugfs files and fast paths, any layout or synchronization change affects packet processing. Stub behavior must remain semantically neutral so production builds do not pay behavior cost.

Test signals: both config variants compile, receive/send code links against stubs, debugfs-enabled builds allocate/free `ibd->fault`, and runtime helpers return false when disabled or not configured.
