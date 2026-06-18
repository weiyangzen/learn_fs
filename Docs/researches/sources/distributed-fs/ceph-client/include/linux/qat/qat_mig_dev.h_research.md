# sources/distributed-fs/ceph-client/include/linux/qat/qat_mig_dev.h

Purpose: declares the Intel QuickAssist Technology virtual-function migration device interface used to save, transfer, and restore VF state.

Important APIs and types: `struct qat_mig_dev` stores parent accelerator device pointer, migration state buffer, setup and remote setup sizes, state size, and VF ID. Lifecycle and migration APIs include create, init, cleanup, reset, open, close, suspend, resume, save state, save setup, load state, load setup, and destroy.

Control flow: a migration-capable QAT VF path creates and initializes a migration device for a PCI VF, opens it for migration, suspends the VF, saves setup/state into buffers, transfers them externally, loads remote setup/state on the target, resumes, then closes and destroys/cleans up.

State and persistence: migration buffers hold device setup and runtime state snapshots. The state is transient during migration but represents hardware/VF state that must be faithfully restored on the destination.

Dependencies and integration points: depends on PCI devices and QAT accelerator driver internals. It integrates QAT VFIO/live-migration flows with hardware-specific state capture.

Risks and test signals: risks include buffer size mismatches between source and destination, stale state after reset, VF ID mismatch, open/close imbalance, suspend/resume ordering bugs, and partial load failures. Test same-version and cross-version migration setup sizes, suspend/save/resume cycles, reset handling, target load failures, and cleanup after interrupted migration.
