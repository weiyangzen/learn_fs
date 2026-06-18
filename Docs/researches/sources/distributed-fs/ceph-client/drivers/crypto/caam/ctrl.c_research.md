<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/ctrl.c

Purpose: top-level CAAM controller platform driver. It maps controller/page registers, detects hardware capabilities and era, configures clocks/DMA/QI, instantiates RNG state handles, initializes debugfs, and populates child job-ring devices.

Important APIs and control flow: descriptor helpers build RNG4 instantiate/deinstantiate jobs; `run_descriptor_deco0()` acquires DECO0 and runs descriptors without JR/QI. `caam_ctrl_rng_init()` detects RNG version, programs TRNG parameters with `kick_trng()`, loops entropy delay on `-EAGAIN`, instantiates handles, records driver-owned handles, and enables RDB. `caam_probe()` allocates `caam_drv_private`, detects i.MX/OP-TEE/MC conditions, enables clocks, maps registers, discovers JR children, chooses endianness and pointer size, sets `caam_dpaa2`/QI/blob flags, initializes QI if present, sets DMA mask, creates debugfs, initializes RNG when page0 is accessible, logs ID/era, and calls `devm_of_platform_populate()`.

State and persistence behavior: exports global `caam_dpaa2`; initializes globals `caam_little_end`, `caam_ptr_sz`, and `caam_imx` through other modules. Per-controller state lives in `caam_drv_private`, including register bases, capability flags, clock handles, IOMMU domain, RNG handle mask, debugfs blobs, and PM save state. Suspend/resume saves MCR/SCFGR and LIODN registers when CAAM loses state and reruns RNG init after restore.

Dependencies and integration points: integrates with OF compatibles `fsl,sec-v4.0`/`fsl,sec4.0`, i.MX SoC matching, OP-TEE and Management Complex policy, QMan/QI, FSL MC versioning, debugfs, DMA/IOMMU, clocks, and JR child platform drivers. The initialized controller private data is consumed by JR, RNG, crypto API, blob, QI, and debugfs modules.

Risks and test signals: risks include register access restrictions under OP-TEE, MC firmware ownership of RNG, fragile era/capability detection, DECO0 polling with busy waits, no security violation IRQ handler despite parsing it, TRNG entropy-delay platform quirks, and assuming child DT order for JR aliases. Test signals are probe on i.MX, Layerscape, DPAA2 and OP-TEE systems, correct DMA mask selection, RNG state-handle instantiation/deinstantiation, QI enablement only when QMan is ready, suspend/resume with and without CAAM power loss, and debugfs/perf counters matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/ctrl.c -->
