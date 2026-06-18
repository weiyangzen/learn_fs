# sources/distributed-fs/ceph-client/drivers/clk/qcom/q6sstop-qcs404.c

## Purpose
This driver registers QCS404 Q6SSTOP/LCC clocks and one reset used around the Hexagon/Q6 subsystem, and also registers a TCSR clock region in the same probe path.

## Important APIs, types, and functions
- `clk_branch` descriptors expose AHB fabric, Q6SS AHBS/AHBM/AXIM, TCM slave, sleep, and TCSR LCC CSR branch clocks.
- `q6sstop_qcs404_clocks[]` and `q6sstop_qcs404_resets[]` describe the main Q6SSTOP clock/reset block.
- `tcsr_qcs404_clocks[]` and `tcsr_qcs404_desc` describe the secondary TCSR region.
- `q6sstopcc_qcs404_probe()` enables runtime PM, acquires an interface clock through `pm_clk_add()`, resumes the device, and probes MMIO resource index 1 for TCSR then index 0 for Q6SSTOP.
- `q6sstopcc_pm_ops` uses `pm_clk_suspend`/`pm_clk_resume`.

## Control flow
After matching `"qcom,qcs404-q6sstopcc"`, probe sets up runtime PM and an unnamed PM clock. It resumes the device so register access is safe, names the shared regmap config `"q6sstop_tcsr"` and registers the TCSR clock at resource index 1, then renames it `"q6sstop_cc"` and registers the main controller at index 0. On failure it releases the runtime PM reference synchronously.

## State and persistence behavior
Hardware registers hold branch gate states and the `Q6SSTOP_BCR_RESET` bit. Software state is limited to static descriptors and runtime-PM/devres bookkeeping. The mutable `q6sstop_regmap_config.name` is reused between the two qcom CC probe calls.

## Dependencies and integration points
The file depends on qcom common CC/reset helpers, CCF branch ops, regmap, platform resources, runtime PM, and PM clock support. It integrates with device tree through `qcom,q6sstopcc-qcs404` clock binding IDs and the platform node's two MMIO resources.

## Risks
Probe assumes resource index 1 is TCSR and index 0 is Q6SSTOP; a device-tree resource order mismatch will register the wrong register block. The shared mutable regmap config name is simple but must not be used concurrently. Runtime PM failures leave the controller unregistered, and missing interface clock acquisition fails probe.

## Test signals
Validation should include successful probe with two mapped regions, `clk_summary` entries for Q6SS and TCSR clocks, working runtime suspend/resume, and reset-controller operation for `Q6SSTOP_BCR_RESET`. Boot logs should not contain `"failed to acquire iface clock"` or qcom CC probe errors.
