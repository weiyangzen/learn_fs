## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_nbio.c

Purpose: implements shared NBIO/PCIe-BIF RAS registration, PCIe replay counter access, replay-counter support checks, and NBIO RAS late init interrupt enabling.

Important APIs/functions: `amdgpu_nbio_ras_sw_init()` registers the NBIO RAS block, names it `"pcie_bif"`, sets block `AMDGPU_RAS_BLOCK__PCIE_BIF`, type `AMDGPU_RAS_ERROR__MULTI_UNCORRECTABLE`, and stores `adev->nbio.ras_if`. `amdgpu_nbio_get_pcie_replay_count()` delegates to `adev->nbio.funcs->get_pcie_replay_count()` when available. `amdgpu_nbio_is_replay_cnt_supported()` rejects SRIOV VF and missing ASIC/NBIO callbacks. `amdgpu_nbio_ras_late_init()` calls generic RAS late init, then enables NBIO RAS controller and ATHUB error event IRQs when supported.

Control flow: software init is a no-op without an installed RAS object. Late init first initializes RAS block state; if RAS is supported for the block, it calls `amdgpu_irq_get()` for two NBIO IRQ sources. Any failure jumps to RAS late fini and returns the error.

State and persistence: updates `adev->nbio.ras_if` and uses IRQ enable counters in `adev->nbio.ras_controller_irq` and `ras_err_event_athub_irq`. Replay counts are read live from hardware via callbacks. No persistence exists.

Dependencies/integration: depends on RAS framework, AMDGPU IRQ subsystem, NBIO function table, ASIC function table, and SRIOV mode checks.

Risks: if the first IRQ get succeeds and the second fails, this function calls RAS late fini but does not explicitly put the first IRQ; correctness depends on late fini or caller cleanup. Replay support requires both ASIC and NBIO callbacks even though the getter itself only calls NBIO funcs. RAS object absence silently disables registration.

Test signals: RAS-enabled boot, NBIO/PCIe error injection, IRQ enable failure cleanup, PCIe replay count queries on PF versus VF, and RAS late init/fini balance.
