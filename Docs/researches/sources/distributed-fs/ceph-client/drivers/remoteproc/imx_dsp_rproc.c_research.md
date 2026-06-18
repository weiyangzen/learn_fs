# sources/distributed-fs/ceph-client/drivers/remoteproc/imx_dsp_rproc.c

## Purpose

`imx_dsp_rproc.c` is the NXP i.MX HiFi4 DSP remoteproc driver. It registers an `imx-dsp-rproc` platform driver for i.MX8QXP, i.MX8QM, i.MX8MP, and i.MX8ULP DSP instances and binds the Linux remoteproc core to SoC-specific DSP reset/start/stop mechanisms, memory carveouts, mailbox/IPI handling, firmware loading, power domains, runtime PM, and system suspend/resume.

The driver is specialized for Xtensa HiFi DSP firmware. It uses SoC address translation tables to expose DSP-owned SRAM/IRAM and DDR windows as remoteproc carveouts, implements 32-bit-only copy and memset helpers for IRAM, handles a DSP-specific resource-table feature that can skip firmware-ready confirmation, and expects optional mailbox channels for kicks, virtqueue notifications, doorbells, and PM acknowledgements.

## Important APIs, types, and functions

- `struct imx_dsp_rproc` is the runtime state: regmap or reset-control start path, `rproc`, SoC config, five optional clocks, mailbox channels (`tx`, `rx`, `rxdb`), PM domains, SCU handle, virtqueue work item, suspend completion, and flags.
- `struct imx_dsp_rproc_dcfg` wraps the common `struct imx_rproc_dcfg` with an optional DSP reset callback.
- `struct fw_rsc_imx_dsp` is a DSP-specific resource-table entry with NXP magic, version, and feature bits. `FEATURE_SKIP_FW_CONFIRMATION` clears `WAIT_FW_CONFIRMATION`.
- `imx8mp_dsp_reset()` resets via DAP debug power control and the `runstall` reset control. `imx8ulp_dsp_reset()` resets/stalls through SIM LPAV sysctrl bits and an SMC call for DSP XRDC setup.
- Start/stop backends are `imx_dsp_rproc_mmio_start/stop()`, `imx_dsp_rproc_reset_ctrl_start/stop()`, and `imx_dsp_rproc_scu_api_start/stop()`.
- `imx_dsp_rproc_add_carveout()` registers DSP-owned address table entries and DT reserved-memory regions with remoteproc and coredump support.
- `imx_dsp_rproc_elf_load_segments()` is a custom ELF loader using `imx_dsp_rproc_memcpy()` and `imx_dsp_rproc_memset()` instead of generic byte writes.
- `imx_dsp_rproc_mbox_alloc()` requests `tx`, `rx`, and `rxdb` channels; `no_mailboxes` switches to a no-op allocator.
- System sleep is handled by `imx_dsp_suspend()` and `imx_dsp_resume()`, including optional mailbox PM handshakes and asynchronous firmware reload after power loss.

## Control flow

Probe gets the matched SoC config, parses `firmware-name`, allocates the `rproc`, initializes `WAIT_FW_CONFIRMATION`, selects mailbox allocation behavior, detects the platform control mode, attaches PM domains, gets clocks, initializes the PM completion, registers the remoteproc, sets Xtensa ELF coredump metadata, and enables runtime PM.

Remoteproc prepare registers carveouts and takes a runtime PM reference. Runtime resume allocates mailbox channels and enables clocks, so the mailbox power domain can idle when the DSP is not prepared. Firmware load optionally resets the DSP, clears existing carveout mappings when offline, then loads each PT_LOAD segment with the custom aligned writer. Start calls the selected SoC backend and, unless the firmware resource table disabled it, waits up to `REMOTE_READY_WAIT_MAX_RETRIES` for the `rxdb` doorbell callback to set `REMOTE_IS_READY`. Kicks send the virtqueue id over `tx`.

Inbound `rx` messages either complete the PM suspend/resume handshake for `RP_MBOX_SUSPEND_ACK` and `RP_MBOX_RESUME_ACK`, or schedule work that services vqid 0 and 1 while holding the remoteproc lock and checking `RPROC_RUNNING`. The `rxdb` mailbox has no payload and only marks the remote as ready. Stop calls the selected backend unless the state is already `RPROC_CRASHED`, then clears `REMOTE_IS_READY`.

System suspend sends `RP_MBOX_SUSPEND_SYSTEM` and waits briefly for an ACK when the DSP is running, mailboxes are present, and firmware confirmation is enabled. It then forces runtime suspend, intentionally powering off the DSP domain. Resume forces runtime resume and, if the DSP had been running, requests firmware asynchronously, reloads segments, starts the core, and kicks vqid 0.

## State and persistence behavior

Driver state is transient in `struct imx_dsp_rproc`; persistent remote state lives in SoC reset/stall registers, SCU-controlled CPU state, clocks, power domains, mailbox FIFOs, and DSP memory. `REMOTE_IS_READY` and `WAIT_FW_CONFIRMATION` are in-memory flags and are reset by stop or resource-table parsing. Carveouts are recreated by prepare and carry coredump segment registrations. Runtime suspend frees mailbox channels and disables clocks; system suspend assumes DSP memory can be lost and reloads firmware on resume.

The address tables define persistent memory topology for each SoC. Entries flagged `ATT_OWN` become carveouts; `ATT_IRAM` marks instruction memory that requires aligned writes. Reserved-memory regions are translated from system address to DSP device address before registration.

## Dependencies and integration points

The file depends on Linux remoteproc, firmware ELF helpers, mailbox, regmap/syscon, reset, clock, runtime PM, PM domains, SCU firmware, ARM SMCCC, and the local shared `imx_rproc.h` address/control config. It integrates with DT through compatible strings, `firmware-name`, `mbox-names`, `fsl,dsp-ctrl`, `runstall`, clocks, PM domains, and reserved-memory phandles. Remote clients see standard remoteproc/rpmsg behavior, while the DSP firmware must match the mailbox and resource-table conventions used here.

## Risks and edge cases

- `imx_dsp_rproc_memcpy()` and `imx_dsp_rproc_memset()` require 32-bit-aligned destinations. A firmware segment ending at an unaligned address is handled by read-modify-write, but an unaligned destination causes load failure.
- `affected_mask = GENMASK(8 * r, 0)` appears to cover one extra bit for partial writes where `r` bytes should normally map to bits `8 * r - 1:0`; this is worth hardware-focused validation.
- `imx8mp_dsp_reset()` maps the DAP region with `ioremap_wc()` and does not check for a NULL mapping before dereferencing.
- `imx_dsp_rproc_free_mbox()` unconditionally calls `mbox_free_channel()` on all channel pointers, so its safety depends on the mailbox API tolerating NULL.
- The module-level function pointer `imx_dsp_rproc_mbox_init` is selected from the global `no_mailboxes` parameter, so all instances share the same mailbox policy.
- A missing `rxdb` mailbox makes `imx_dsp_rproc_ready()` return success immediately; this is intentional for no-doorbell systems but weakens readiness detection.
- `imx_dsp_load_firmware()` runs asynchronously during resume and calls `rproc->ops->start()` directly; failures leave runtime PM already resumed and need careful recovery testing.

## Test signals

Build with i.MX remoteproc, mailbox, SCU, reset, and PM options enabled. DT boot tests should cover all four compatibles and both mailbox and `no_mailboxes` modes. Firmware tests should include resource tables with and without the NXP DSP entry, aligned and partial PT_LOAD segments, IRAM writes, vqid kicks, ready doorbell timeout, suspend/resume ACK timeout, watchdog/crash stop behavior, and coredump segment registration. Hardware register checks should confirm reset/stall bits, SCU start/stop, runtime PM clock gating, and firmware reload after system resume.
