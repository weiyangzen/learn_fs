# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_sandisk.c

Purpose: this small manufacturer file applies a SanDisk timing quirk for SDTNQGAMA devices whose interface timing negotiation must be limited to ONFI SDR mode 0 as the starting point.

Important APIs, types, and functions: `sandisk_nand_manuf_ops` exposes `.init`. `sdtnqgama_choose_interface_config()` fills an SDR mode-0 ONFI interface config and delegates final selection to `nand_choose_best_sdr_timings()`.

Control flow: manufacturer init checks whether `chip->parameters.model` starts with `SDTNQGAMA`; matching devices get `chip->ops.choose_interface_config` replaced with the custom chooser.

State and persistence: the only state change is the function pointer in `chip->ops`; no flash or private memory state is modified.

Dependencies and integration points: it depends on the model string populated during detection, `onfi_fill_interface_config()`, and the NAND core timing negotiation path.

Risks: the model-prefix match is intentionally narrow. If related SanDisk parts need the same limit but use different names, they will negotiate through the generic path. The code assumes `parameters.model` is valid when manufacturer init runs.

Test signals: verify SDTNQGAMA model matching, selected timing mode constraints, successful controller timing setup via `nand_choose_best_sdr_timings()`, and no behavior changes for nonmatching SanDisk devices.
