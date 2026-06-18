<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/nvmf.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/nvmf.rs

Purpose: NVMf target location and I/O helpers bridging io-engine nexus/replica metadata to host NVMe devices or SPDK fio target strings.

Important APIs/types: `NvmfLocation { addr, nqn, serial }` can be built from nexus address/name/uuid, opened into an `NmveConnectGuard` plus Linux device path, and converted to SPDK fio transport args. `test_write_to_nvmf()` connects, finds the device by serial, and delegates file write validation. `test_devices_identical()` opens multiple targets and compares their device files. `test_fio_to_nvmf()` configures Fio jobs for SPDK ioengine with NVMf transport args. `test_fio_to_nvmf_aio()` connects through kernel NVMe and runs fio with libaio on the device path.

State and dependencies: mutates host NVMe connection state and target data. Depends on `nvme` helpers, fio wrapper, and file comparison utilities.

Risks and test signals: `test_devices_identical` requires at least two locations and uses byte-for-byte comparison over device files. SPDK fio target args escape colons in NQN; quoting is important. Healthy tests prove both kernel and SPDK I/O paths.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/nvmf.rs -->
