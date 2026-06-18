# sources/distributed-fs/ceph-client/drivers/vfio/pci/qat/main.c

Purpose: implements VFIO PCI live migration support for Intel QAT virtual functions using the QAT PF migration-device API.

Important APIs and types: `struct qat_vf_migration_file`, `struct qat_vf_core_device`, save/read and resume/write file ops, pre-copy ioctl, state transition handler, reset handling, VFIO ops/probe/remove glue, and QAT migration calls such as `qat_vfmig_save_setup()`, `save_state()`, `load_setup()`, `load_state()`, `suspend()`, and `resume()`.

Control flow: init installs migration flags for stop-copy, P2P, and pre-copy, initializes VFIO core, finds the PF and VF id, creates and initializes a QAT migration device. Open enables VFIO core and opens QAT migration. Pre-copy saves setup data only and reports remaining setup bytes; stop-copy saves full device state. Restore writes into the QAT state buffer and repeatedly calls setup-load until enough data is available, then RESUMING->STOP loads final state. P2P arcs fully suspend/resume the VF because QAT cannot stop only P2P DMA.

State and persistence: migration data is held in the QAT migration device `state` buffer plus per-FD `filled_size` and disabled flags. Device migration state and active save/restore files are protected by `state_mutex`. There is no disk persistence.

Dependencies and integration: depends on VFIO PCI core, anon inodes, QAT migration API under `CRYPTO_QAT`, PCI VF/PF relationships, and VFIO migration arc helpers.

Risks: write bounds use `state_size`; bad size or repeated writes can fail restore. Pre-copy only carries setup data, so stop-copy must refresh full state. Reset must call QAT reset and disable FDs under the state lock. Errors from `qat_vfmig_load_setup()` other than `-EAGAIN` abort restore early.

Test signals: QAT generations in PCI id table, init failure unwinds, open/close QAT migration lifetime, pre-copy info/read behavior, stop-copy state refresh after pre-copy P2P, restore setup compatibility failures, final load failure, reset during active FDs, and P2P suspend/resume arcs.
