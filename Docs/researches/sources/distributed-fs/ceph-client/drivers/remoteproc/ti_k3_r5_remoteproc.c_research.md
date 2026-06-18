# sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_r5_remoteproc.c

## Purpose

This file implements the Linux remoteproc platform driver for TI K3 R5F clusters. It binds R5F subsystem device-tree nodes such as `ti,am654-r5fss`, `ti,j7200-r5fss`, `ti,am64-r5fss`, `ti,am62-r5fss`, and `ti,j721s2-r5fss`, constructs one or more `struct rproc` instances, and controls reset, halt/run, boot vectors, TCM layout, reserved memory, SRAM, and mailbox integration for firmware running on the R5 cores.

The driver supports split mode, lockstep mode, AM64x single-CPU mode, and AM62x single-core mode. It also has IPC-only attach support when a bootloader has already loaded and started firmware before Linux probes the device.

## Important APIs, Types, And Functions

Key local types are `enum cluster_mode`, `struct k3_r5_soc_data`, `struct k3_r5_cluster`, and `struct k3_r5_core`. `k3_r5_soc_data` carries SoC differences such as doubled TCM windows, TCM ECC auto-init, single-CPU support, and single-core IP. `k3_r5_cluster` owns cluster mode, the list of `k3_r5_core` children, and a wait queue used to enforce core sequencing. `k3_r5_core` stores child device state, its `struct k3_rproc`, SRAM descriptors, TCM configuration bits, and `released_from_reset`.

Remoteproc operations are exported through `k3_r5_rproc_ops`: `.prepare`, `.unprepare`, `.start`, `.stop`, `.kick`, and `.da_to_va`. Preparation and unpreparation release or assert resets so firmware can be loaded into TCMs. Start and stop program the boot vector and clear or set the TI-SCI halt bit. Address translation first checks optional SRAM regions and then delegates to the shared K3 remoteproc translation helper.

Reset and power helpers split into `k3_r5_split_reset()`, `k3_r5_split_release()`, `k3_r5_lockstep_reset()`, and `k3_r5_lockstep_release()`. Processor control uses `ti_sci_proc_get_status()`, `ti_sci_proc_set_config()`, and `ti_sci_proc_set_control()` from `ti_sci_proc.h`, plus TI-SCI device `get_device` and `put_device` operations.

Probe and initialization flow is anchored by `k3_r5_probe()`, `k3_r5_cluster_of_init()`, `k3_r5_core_of_init()`, and `k3_r5_cluster_rproc_init()`. Static match data maps compatibles to SoC capabilities and the common `r5_data` memory layout for ATCM and BTCM.

## Control Flow

`k3_r5_probe()` allocates the cluster object, reads `ti,cluster-mode` or chooses a SoC-specific default, validates the number of child cores, populates child platform devices, parses per-core DT properties, and initializes remoteproc objects. Per-core init defaults to ATCM disabled, BTCM enabled, and `loczrama` true unless `ti,atcm-enable`, `ti,btcm-enable`, or `ti,loczrama` override those settings. Optional `sram` phandles are converted to memory mappings.

`k3_r5_cluster_rproc_init()` walks each child core, parses firmware name, allocates a `rproc`, obtains TI-SCI and reset handles, creates a `ti_sci_proc` helper from `ti,sci-proc-ids`, maps internal memories, requests processor ownership, and later requests mailboxes, detects remoteproc versus IPC-only mode, configures TI-SCI boot flags, initializes reserved memory, and registers the `rproc`. In lockstep, single-CPU, and single-core modes only one remoteproc is registered.

Booting through remoteproc calls `.prepare`, `.start`, `.stop`, and `.unprepare`. Split mode enforces power-up order, waiting up to two seconds for core0 before core1, and power-down order, waiting for core1 before core0. Lockstep start programs core0 boot configuration and unhalts cores in reverse order; stop halts core0 then core1. Single-CPU mode reuses lockstep reset release/assert for combined TCM access but only runs core0.

IPC-only detection in `k3_r5_rproc_configure_mode()` queries TI-SCI device power, local reset status, and halt control. If the module is powered, local reset is deasserted, and the core is unhalted, the rproc is marked `RPROC_DETACHED` and its operations are reduced to attach/detach/resource-table support.

## State And Persistence

Runtime state is in devm-managed cluster/core structures and remoteproc private data. `released_from_reset` is the key local sequencing flag, protected by ordering through remoteproc callbacks and signaled via `cluster->core_transition`. Firmware-visible state is persistent in System Firmware controlled boot configuration bits: lockstep, single-core, ATCM/BTCM enable, TCM reset base, TEINIT, halt/run control, and boot vector. The driver also updates TCM device addresses when IPC-only mode reveals actual bootloader settings.

Memory mappings for ATCM/BTCM, SRAM, and reserved memory are held for the lifetime of the device. `k3_reserved_mem_init()` integrates carveouts with remoteproc. Cleanup is devm-action based: `k3_r5_cluster_of_exit()` drops child core resources and `k3_r5_cluster_rproc_exit()` detaches attached remoteprocs in a mode-aware order.

## Dependencies And Integration Points

The driver depends on the remoteproc core, TI-SCI protocol, TI K3 common remoteproc helpers, reset framework, OMAP/K3 mailbox support, devicetree child devices, reserved-memory bindings, and SoC match data. It includes `omap_remoteproc.h`, `remoteproc_internal.h`, `ti_sci_proc.h`, and `ti_k3_common.h`.

Important DT properties are `ti,cluster-mode`, `firmware-name`, `ti,sci`, `ti,sci-dev-id`, `ti,sci-proc-ids`, `ti,atcm-enable`, `ti,btcm-enable`, `ti,loczrama`, and optional `sram` phandles. Integration with rpmsg happens indirectly through remoteproc and mailbox kick support.

## Risks And Edge Cases

The source contains visible duplicate lines and an apparently stray extra closing brace after `k3_r5_cluster_rproc_exit()`, which is a source-integrity risk in this tree. Functionally, boot address sanity checking is explicitly marked TODO, so invalid firmware entry points are not rejected here. Split-mode sequencing relies on a two-second timeout and shared `released_from_reset` state, which can fail if remoteproc requests are concurrent or core0 is not progressing. IPC-only mode is strict: mismatched power, local reset, or halt state returns `-EINVAL`.

TCM address modeling is simplified: comments note that R5 region registers can place ATCM/BTCM elsewhere, but the driver currently assigns only address 0 and `0x41010000` based on `loczrama`. Lockstep configuration works around System Firmware limitations by temporarily programming both cores symmetrically, so TI-SCI NACK behavior and eFUSE status bits are important failure points. Error recovery is disabled for remoteproc instances.

## Test Signals

There is no direct KUnit coverage in this file. Test signals are platform probe success, remoteproc sysfs lifecycle behavior, IPC-only attach/detach behavior, TI-SCI status/config/control results, correct reserved-memory and TCM loading, mailbox/rpmsg operation, and DT validation for supported SoCs and modes. The duplicated/extra-brace source signals should also be caught by compile testing.
