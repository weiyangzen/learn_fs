# subset-b-003691 Research

Grouped source-tree-aligned research for the assigned Nouveau, Nova, and OMAP DRM files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk110.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk110.c

## Purpose
Implements GK110 PMU support with embedded GF119-style FUC firmware and a dedicated PGO/B register sequence.

## Important APIs, Types, And Functions
`gk110_pmu_pgob()` writes a fixed sequence of PGRAPH/power registers and waits on bit 31 after each step. `gk110_pmu_new()` exposes the constructor. The `gk110_pmu` function table reuses `gt215_pmu_flcn`, `gf100_pmu_enabled()`, `gf100_pmu_reset()`, and GT215 mailbox handlers.

## Control Flow
Construction installs a no-firmware fwif. During init, GT215 code uploads `gk110_pmu_code` and `gk110_pmu_data`; power-gating callers may invoke `.pgob`, which disables and re-enables control bits around the magic sequence.

## State, Persistence, And Dependencies
State is mostly hardware-side: PMU falcon IMEM/DMEM, host/PMU rings, and power-gating registers. The local magic table is immutable module data.

## Integration Points
Integrated through `priv.h`, the generated `fuc/gf119.fuc4.h` arrays, timer polling via `nvkm_msec()`, and Nouveau chipset PMU construction.

## Risks
The PGO/B sequence is opaque and timeout-based; register drift across steppings can leave the PMU or graphics block wedged. The `enable` argument is ignored, so callers must not expect symmetric enable/disable behavior.

## Test Signals
Hardware probe on GK110/GK208-class cards, PMU mailbox initialization, power-gating transitions, and absence of timeout or PMU interrupt logs are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk208.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk208.c

## Purpose
Provides the PMU constructor and firmware-interface table for GK208 GPUs in Nouveau's nvkm PMU subdevice. It also installs `gk110_pmu_pgob()` for power-gating object block sequencing.

## Important APIs, Types, And Functions
`gk208_pmu_new()` delegates to `nvkm_pmu_new_()`. The local `nvkm_pmu_func` binds the `gt215` falcon operations, embedded `gk208.fuc5` code/data when present, GF100 reset/enabled helpers, GT215 mailbox init/fini/interrupt/send/receive helpers, and optional PGO/B handling.

## Control Flow
Device setup selects the single fwif entry, rejects external firmware through the no-firmware loader where applicable, constructs `struct nvkm_pmu`, and later lets subdev init upload ucode or configure the falcon through the function table.

## State, Persistence, And Dependencies
Persistent state lives in the allocated `nvkm_pmu` object and in PMU falcon registers. Embedded firmware arrays are read-only module data.

## Integration Points
Depends on `priv.h`, PMU base construction, falcon register helpers, and the selected FUC firmware header. It is reached from Nouveau chipset tables that call the chip-specific `_new` function.

## Risks
Firmware/header aliasing must match the chip's microcontroller ABI. Wrong code/data sizes or missing mailbox helpers can stall PMU init; PGO/B magic writes are register-sensitive and hard to validate without hardware.

## Test Signals
Signals are Nouveau probe success on the target GPU, PMU init mailbox readiness, absence of PMU interrupt errors, and successful suspend/resume or power-gating paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk208.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk20a.c

## Purpose
Implements Tegra GK20A PMU support without firmware upload, using PMU falcon performance counters to drive simple DVFS.

## Important APIs, Types, And Functions
`struct gk20a_pmu` extends `nvkm_pmu` with an alarm and DVFS data. Key helpers are `gk20a_pmu_init()`, `gk20a_pmu_fini()`, `gk20a_pmu_dvfs_work()`, `gk20a_pmu_dvfs_get_dev_status()`, and `gk20a_pmu_dvfs_target()`.

## Control Flow
Init acquires the PMU falcon, programs busy/clock counter slots, and schedules a 2-second alarm. Each alarm reads busy and total counters, smooths utilization, maps load to a clock pstate, calls `nvkm_clk_astate()` when a level change is needed, resets counters, and reschedules after 100 ms.

## State, Persistence, And Dependencies
State lives in `gk20a_pmu`, the static DVFS tuning table, the current `nvkm_clk` pstate, falcon counter registers, and the timer alarm list. No filesystem persistence exists.

## Integration Points
Depends on nvkm clock, timer, volt, falcon, and subdev infrastructure. It integrates with GK20A SoC initialization and complements the Tegra regulator-backed voltage code.

## Risks
DVFS assumes performance level equals pstate and may behave poorly if clock states are sparse. It delays work until CLK and VOLT exist but still depends on timer availability. Counter overflow or unexpected falcon register behavior can skew load.

## Test Signals
Signals include pstate changes under GPU load, stable alarm rescheduling, no falcon acquisition errors, and sane utilization trace logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gm107.c

## Purpose
Provides the PMU constructor and firmware-interface table for GM107 GPUs in Nouveau's nvkm PMU subdevice.

## Important APIs, Types, And Functions
`gm107_pmu_new()` delegates to `nvkm_pmu_new_()`. The local `nvkm_pmu_func` binds the `gt215` falcon operations, embedded `gk208.fuc5 aliases` code/data when present, GF100 reset/enabled helpers, GT215 mailbox init/fini/interrupt/send/receive helpers, and optional PGO/B handling.

## Control Flow
Device setup selects the single fwif entry, rejects external firmware through the no-firmware loader where applicable, constructs `struct nvkm_pmu`, and later lets subdev init upload ucode or configure the falcon through the function table.

## State, Persistence, And Dependencies
Persistent state lives in the allocated `nvkm_pmu` object and in PMU falcon registers. Embedded firmware arrays are read-only module data.

## Integration Points
Depends on `priv.h`, PMU base construction, falcon register helpers, and the selected FUC firmware header. It is reached from Nouveau chipset tables that call the chip-specific `_new` function.

## Risks
Firmware/header aliasing must match the chip's microcontroller ABI. Wrong code/data sizes or missing mailbox helpers can stall PMU init; PGO/B magic writes are register-sensitive and hard to validate without hardware.

## Test Signals
Signals are Nouveau probe success on the target GPU, PMU init mailbox readiness, absence of PMU interrupt errors, and successful suspend/resume or power-gating paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gm200.c

## Purpose
Defines GM200 PMU falcon binding operations and a minimal PMU subdevice for chips where PMU firmware is unavailable.

## Important APIs, Types, And Functions
`gm200_pmu_flcn_bind_stat()` selects and reads bind status. `gm200_pmu_flcn_bind_inst()` programs DMA indices and instance pointer state. `gm200_pmu_flcn` supplies GM200 falcon reset, memory PIO, start, command queue, and message queue layout. `gm200_pmu_new()` constructs the subdev.

## Control Flow
Construction uses a no-firmware fwif. If the PMU is used, falcon setup binds an instance block by programming e00-e10 and 0x480, then standard nvkm falcon code handles start and queue access.

## State, Persistence, And Dependencies
State is hardware register state in the falcon and PMU object metadata. There is no embedded ucode and no persistent storage.

## Integration Points
Shared by later secure-PMU implementations such as GM20B/GP10B for falcon layout. Depends on generic GM200 falcon helpers and `gf100_pmu_reset()`.

## Risks
The no-firmware loader only warns and returns success, so features depending on a running PMU may remain unavailable without failing probe. Bind register constants are chip-specific.

## Test Signals
Probe logs should show firmware-unavailable warnings without crashes. Falcon bind/start paths are indirectly tested by secure boot flows on chips that reuse `gm200_pmu_flcn`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gm20b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gm20b.c

## Purpose
Implements secure PMU firmware loading and ACR bootstrap support for GM20B Tegra GPUs.

## Important APIs, Types, And Functions
Important functions include `gm20b_pmu_load()`, `gm20b_pmu_init()`, `gm20b_pmu_recv()`, `gm20b_pmu_initmsg()`, `gm20b_pmu_acr_init_wpr()`, `gm20b_pmu_acr_bld_write()`, `gm20b_pmu_acr_bld_patch()`, and `gm20b_pmu_acr_bootstrap_falcon()`. `gm20b_pmu` is exported for GP10B reuse.

## Control Flow
Firmware is loaded as signed ACR LSF images. Init acquires the falcon, writes secure-mode args into DMEM, starts the falcon, waits for the first PMU init message, initializes HPQ/LPQ/message queues, sends WPR init, and receives later messages through the falcon message queue.

## State, Persistence, And Dependencies
State includes PMU command/message queues, `initmsg_received`, `wpr_ready` completion, WPR image contents, and falcon register/DMEM state. Firmware files under `nvidia/gm20b/pmu/` are module firmware dependencies.

## Integration Points
Integrates PMU, ACR, nvfw PMU/FLCN formats, core memory object access, and Tegra secure boot. FECS/GPCCS bootstrap callbacks rely on this PMU path.

## Risks
Secure boot is fragile: loader config address patching must preserve DMA-base encoding, queue indices are trusted from firmware, and WPR completion is asynchronous. Missing firmware falls back to a warning-only no-firmware mode.

## Test Signals
Signals are successful firmware request/load, init message parsing, WPR init completion, ACR bootstrap command replies matching requested falcon IDs, and no queue timeout logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gm20b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gp102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gp102.c

## Purpose
Provides GP102 PMU falcon metadata for Pascal desktop GPUs when GSP-RM is not managing the device.

## Important APIs, Types, And Functions
`gp102_pmu_new()` gates construction on `nvkm_gsp_rm()`. The local `gp102_pmu_flcn` reuses GM200 falcon memory PIO/start/queue layout with `gp102_flcn_reset_eng()` and GM200 bind helpers.

## Control Flow
If GSP-RM is active, construction returns `-ENODEV`; otherwise `nvkm_pmu_new_()` installs a no-firmware fwif around the GP102 falcon function table.

## State, Persistence, And Dependencies
State is limited to the allocated PMU object and falcon MMIO state. There is no embedded firmware in this file.

## Integration Points
Integrates with the GSP subdevice selection path and shared GM200/GP102 falcon helpers.

## Risks
Returning `-ENODEV` under GSP-RM is intentional; callers must tolerate PMU absence. Without firmware, PMU-backed services are limited.

## Test Signals
Test signals are correct behavior in both GSP-RM and native modes, no PMU construction when RM owns the GPU, and clean native probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gp102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gp10b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gp10b.c

## Purpose
Extends GM20B secure PMU support for GP10B, adding multi-falcon ACR bootstrap support and GP10B firmware declarations.

## Important APIs, Types, And Functions
`gp10b_pmu_acr_bootstrap_multiple_falcons()` sends `NV_PMU_ACR_CMD_BOOTSTRAP_MULTIPLE_FALCONS` and validates the returned mask. The `gp10b_pmu_acr` descriptor reuses GM20B loader write/patch and single-falcon bootstrap callbacks.

## Control Flow
Firmware version 0 loads signed PMU images through `gm20b_pmu_load()` and then uses GM20B PMU runtime handling. ACR may bootstrap PMU, FECS, and GPCCS either singly or by bitmask.

## State, Persistence, And Dependencies
State is the GM20B PMU state plus the ACR falcon mask and firmware images under `nvidia/gp10b/pmu/` on Tegra186 builds.

## Integration Points
Integrates with ACR LSF loading, nvfw PMU message formats, GM20B PMU runtime functions, and Tegra GP10B platform firmware packaging.

## Risks
The WPR low/high fields are left as placeholders in the command, so the firmware ABI must not require them here. Mask mismatch returns `-EIO` and can block dependent falcons.

## Test Signals
Signals include successful signed image load, bootstrap reply mask equality, FECS/GPCCS availability, and no PMU command queue timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gp10b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gt215.c

## Purpose
Implements the classic Nouveau PMU firmware upload, host/PMU mailbox queues, interrupts, and constructor for GT215-style PMUs.

## Important APIs, Types, And Functions
Key APIs are `gt215_pmu_send()`, `gt215_pmu_recv()`, `gt215_pmu_intr()`, `gt215_pmu_init()`, `gt215_pmu_fini()`, and `gt215_pmu_new()`. The function table provides embedded `gt215_pmu_code` and `gt215_pmu_data` from `fuc/gt215.fuc3.h`.

## Control Flow
Init inhibits interrupts, waits idle, resets the PMU, waits for memory scrubbing, uploads DMEM/IMEM words, starts execution, waits for firmware-published send/receive ring descriptors, and enables interrupts. Send/receive exchange five-word packets through data segment windows.

## State, Persistence, And Dependencies
State includes send and receive ring bases/sizes, waitqueue reply state, receive work item, PMU IMEM/DMEM contents, and hardware interrupt status.

## Integration Points
This is the base mailbox implementation reused by many later chip wrappers and by MEMX scripts. It depends on timer polling and nvkm MMIO helpers.

## Risks
Only one synchronous reply is tracked at a time. Send waits can return `-EBUSY`; unexpected messages are logged as warnings. Incorrect firmware ring descriptors can deadlock clients.

## Test Signals
Signals are PMU init success, valid queue descriptor reads, responsive `nvkm_pmu_send()` calls, clean interrupt acking, and MEMX command execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/memx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/memx.c

## Purpose
Builds and optionally executes PMU MEMX scripts used for memory register programming, waits, delays, vblank synchronization, and training.

## Important APIs, Types, And Functions
`struct nvkm_memx` caches batched method/data words. Public helpers include `nvkm_memx_init()`, `nvkm_memx_fini()`, `nvkm_memx_wr32()`, `nvkm_memx_wait()`, `nvkm_memx_nsec()`, `nvkm_memx_wait_vblank()`, `nvkm_memx_train()`, `nvkm_memx_train_result()`, `nvkm_memx_block()`, and `nvkm_memx_unblock()`.

## Control Flow
Init asks the PMU MEMX process for data buffer base/size, locks PMU data access, and positions writes. Commands are coalesced when method-compatible, flushed when full or incompatible, and finally released; optional execution sends `MEMX_MSG_EXEC` and logs execution timing.

## State, Persistence, And Dependencies
State lives in the heap `nvkm_memx` script builder, PMU data segment, cached command buffer, and PMU training result area. No filesystem persistence exists.

## Integration Points
Depends on working PMU mailbox send/receive, MEMX FUC process IDs, display head registers for vblank selection, and memory training callers.

## Risks
The file trusts PMU-reported buffer bounds and has hardware-specific vblank heuristics. WAIT/DELAY/VBLANK are force-flushed because firmware cannot handle multiple combined operations.

## Test Signals
Signals include successful script execution replies, expected register traces, memory training result reads of the expected size, and no PMU data-access lock hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/memx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/priv.h

## Purpose
Defines private PMU function-table contracts and cross-chip helper declarations for Nouveau's nvkm PMU implementations.

## Important APIs, Types, And Functions
`struct nvkm_pmu_func` contains falcon, firmware image, lifecycle, interrupt, mailbox, init-message, and PGO/B callbacks. `struct nvkm_pmu_fwif` ties firmware version/loaders to function tables and optional ACR descriptors.

## Control Flow
Chip files populate these tables; PMU base construction selects a fwif, loads firmware when needed, and dispatches subdev operations through the selected callbacks.

## State, Persistence, And Dependencies
No runtime state is stored in the header, but it describes the persistent fields that `struct nvkm_pmu` and firmware interface tables use.

## Integration Points
Integrated by all PMU chip files, ACR secure firmware code, GT215 mailbox code, GF100/GM200 no-firmware loaders, and the exported constructors in PMU base.

## Risks
ABI changes here affect every PMU implementation. Callback omissions are meaningful and must match the base code's null checks.

## Test Signals
Compile-time coverage is primary; runtime signals are each chip path successfully selecting compatible callback sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/Kbuild

## Purpose
Declares the object files that build the Nouveau privring subdevice implementation into `nvkm-y`.

## Important APIs, Types, And Functions
The file contributes these object targets: `gf100.o`, `gf117.o`, `gk104.o`, `gk20a.o`, `gm200.o`, `gp10b.o`. There are no runtime C APIs.

## Control Flow
Kbuild conditionlessly appends the listed objects when the Nouveau nvkm subtree is built; chip selection happens later through device tables and constructor calls.

## State, Persistence, And Dependencies
No runtime state is persisted. The only dependency is the kernel build system variable expansion for `nvkm-y`.

## Integration Points
Integrated by the parent Nouveau nvkm Kbuild so the privring constructors and helpers are linkable.

## Risks
Missing an object silently removes a chip implementation at link time; adding an object here without matching declarations can create unresolved symbols.

## Test Signals
Build coverage is the primary signal: enabled Nouveau configurations should compile and link all listed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gf100.c

## Purpose
Implements GF100 private-ring initialization and interrupt diagnosis for HUB, ROP, and GPC ring clients.

## Important APIs, Types, And Functions
`gf100_privring_intr()` dispatches to `gf100_privring_intr_hub()`, `_rop()`, and `_gpc()` based on interrupt summary registers. `gf100_privring_init()` programs timeout/control registers. `gf100_privring_new()` constructs the subdev.

## Control Flow
Init writes fixed ring timing values. Interrupt handling reads client address/data/status windows, logs the failing client, then masks 0x121c4c to request recovery and waits for the ring status bits to clear.

## State, Persistence, And Dependencies
State is MMIO-only: ring client error registers, ring control registers, and the `nvkm_subdev` object. No persistent storage exists.

## Integration Points
Integrates with the nvkm subdev interrupt path and timer polling helpers. Later GF117 code reuses this interrupt handler.

## Risks
The handler logs rather than repairs individual client faults. Recovery depends on the hardware clearing status within 2 seconds; incorrect hub/rop/gpc counts can hide interrupts.

## Test Signals
Signals include debug logs identifying the offending ring client and successful clearing of 0x121c4c status bits after injected or real privring faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gf117.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gf117.c

## Purpose
Provides GF117-specific private-ring initialization while reusing the GF100 interrupt decoder.

## Important APIs, Types, And Functions
`gf117_privring_init()` programs 0x122310, 0x122348, and 0x1223b0. `gf117_privring_new()` constructs the subdev using `.intr = gf100_privring_intr`.

## Control Flow
On init the driver applies GF117 timeout/control masks, then normal interrupt flow is handled by the shared GF100 code.

## State, Persistence, And Dependencies
State is limited to private-ring MMIO programming and the subdev allocation.

## Integration Points
Depends on `priv.h`, `nvkm_subdev_new_()`, and GF100 interrupt exports. It is selected by GF117 chipset tables.

## Risks
Because it inherits the GF100 interrupt layout, any GF117 register-layout divergence would be logged incorrectly. Init values are opaque hardware constants.

## Test Signals
Signals are probe/init success on GF117 hardware and privring faults decoded without unhandled interrupt spam.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gf117.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gk104.c

## Purpose
Implements GK104 private-ring init and interrupt decoding with the Kepler-era register layout.

## Important APIs, Types, And Functions
`gk104_privring_intr()` reads 0x120058/0x12005c summaries and per-HUB/ROP/GPC windows with 0x800 spacing. `gk104_privring_init()` programs several 0x1223xx timing/control registers and is used for both preinit and init.

## Control Flow
Preinit/init configures ring timeouts. Interrupts decode each asserted client, log address/data/status, request recovery through 0x12004c, and wait for status bits to clear.

## State, Persistence, And Dependencies
Runtime state is only subdev and MMIO state. No persistent software data is kept.

## Integration Points
Reused by GM200 and GP10B variants for interrupt handling. Integrated through nvkm subdev lifecycle callbacks.

## Risks
Wrong client counts or spacing can hide faults. Running the same programming in preinit and init relies on idempotent register writes.

## Test Signals
Signals are clean init, useful client fault debug messages, and status-clearing waits completing within timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gk20a.c

## Purpose
Implements Tegra GK20A private-ring reset and timeout programming.

## Important APIs, Types, And Functions
`gk20a_privring_init_privring_ring()` performs the ring reset sequence and timeout writes. `gk20a_privring_intr()` detects status bits, reinitializes the ring if needed, and acknowledges interrupts.

## Control Flow
Init disables a bit in 0x137250, toggles 0x000200 bit 5 with a delay, writes ring reset/control registers, then increases clock timeout values for high GPC clock rates. Interrupt handling may repeat that sequence before acking.

## State, Persistence, And Dependencies
State is hardware register state plus the subdev object. The code persists no software counters.

## Integration Points
Depends on nvkm MMIO helpers and timer polling. It is used by Tegra GK20A chipset initialization.

## Risks
The reset sequence is timing-sensitive. The interrupt handler only checks low status bits and performs broad ring reinit, which can mask root causes.

## Test Signals
Signals are absence of privring operation failures at high GPC clocks and successful interrupt ack after ring reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gm200.c

## Purpose
Provides GM200 private-ring subdev construction for native Nouveau operation.

## Important APIs, Types, And Functions
`gm200_privring_new()` skips construction when GSP-RM owns the GPU and otherwise creates a subdev whose only callback is `.intr = gk104_privring_intr`.

## Control Flow
Construction checks `nvkm_gsp_rm(device->gsp)`. Native mode allocates a subdev; interrupts are decoded through the GK104 handler.

## State, Persistence, And Dependencies
There is no file-local runtime state beyond the subdev pointer. GSP-RM mode intentionally leaves the subdev absent.

## Integration Points
Integrates with GSP ownership detection and shared GK104 private-ring interrupt handling.

## Risks
Callers must tolerate `-ENODEV` under GSP-RM. Lack of init callback assumes firmware or earlier boot state has configured the ring.

## Test Signals
Signals are native probe creating the subdev, RM-managed probe skipping it, and no private-ring interrupt regressions on GM200.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gp10b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gp10b.c

## Purpose
Provides GP10B private-ring initialization with GK104-style interrupt decoding.

## Important APIs, Types, And Functions
`gp10b_privring_init()` disables a control register, initializes the ring, and programs timeout register 0x009080. `gp10b_privring_new()` constructs the subdev.

## Control Flow
Init writes 0x1200a8, resets the ring through 0x12004c/0x122204, performs a readback flush, and applies timeout configuration. Interrupts use `gk104_privring_intr()`.

## State, Persistence, And Dependencies
State is hardware MMIO programming and the subdev object only.

## Integration Points
Integrates Tegra GP10B chipset setup with shared Nouveau private-ring interrupt handling.

## Risks
Timeout constants are hardware-specific. Reusing GK104 interrupt decoding assumes GP10B summary/client register compatibility.

## Test Signals
Signals include clean GP10B probe, no privring timeouts under load, and correctly acknowledged fault interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/gp10b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/priv.h

## Purpose
Declares shared private-ring interrupt helpers for Nouveau privring chip files.

## Important APIs, Types, And Functions
Exports `gf100_privring_intr()` and `gk104_privring_intr()` and includes the public `subdev/privring.h` interface.

## Control Flow
Chip implementations include this header and install the exported interrupt functions in their `nvkm_subdev_func` tables.

## State, Persistence, And Dependencies
No runtime state is stored here; it is a private compile-time contract.

## Integration Points
Integrates GF117, GM200, and GP10B wrappers with the shared GF100/GK104 interrupt decoders.

## Risks
Prototype drift breaks multiple chip files. The header intentionally keeps the private API narrow.

## Test Signals
Compile-time coverage of all privring variants is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/Kbuild

## Purpose
Declares the object files that build the Nouveau thermal subdevice implementation into `nvkm-y`.

## Important APIs, Types, And Functions
The file contributes these object targets: `base.o`, `fan.o`, `fannil.o`, `fanpwm.o`, `fantog.o`, `ic.o`, `temp.o`, `nv40.o`, `nv50.o`, `g84.o`, `gt215.o`, `gf100.o`, `gf119.o`, `gk104.o`, `gm107.o`, `gm200.o`, `gp100.o`. There are no runtime C APIs.

## Control Flow
Kbuild conditionlessly appends the listed objects when the Nouveau nvkm subtree is built; chip selection happens later through device tables and constructor calls.

## State, Persistence, And Dependencies
No runtime state is persisted. The only dependency is the kernel build system variable expansion for `nvkm-y`.

## Integration Points
Integrated by the parent Nouveau nvkm Kbuild so the thermal constructors and helpers are linkable.

## Risks
Missing an object silently removes a chip implementation at link time; adding an object here without matching declarations can create unresolved symbols.

## Test Signals
Build coverage is the primary signal: enabled Nouveau configurations should compile and link all listed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/base.c

## Purpose
Implements the common Nouveau thermal subdevice: fan policy, temperature attributes, threshold programming hooks, lifecycle, and clockgating wrappers.

## Important APIs, Types, And Functions
Public entry points include `nvkm_therm_temp_get()`, `nvkm_therm_cstate()`, `nvkm_therm_fan_mode()`, `nvkm_therm_attr_get()`, `nvkm_therm_attr_set()`, `nvkm_therm_clkgate_enable()`, `nvkm_therm_clkgate_fini()`, `nvkm_therm_clkgate_init()`, `nvkm_therm_ctor()`, and `nvkm_therm_new_()`.

## Control Flow
Oneinit constructs sensor, external IC, and fan backends, switches to automatic fan mode, probes sensor availability, and reports clockgating. Init calls chip setup, restores suspend fan mode, starts threshold polling/interrupts, and initializes the fan. Fini disables chip hooks, fan alarms, and sensor alarms.

## State, Persistence, And Dependencies
State includes `therm->mode`, suspend mode, cstate fan target, BIOS sensor/fan thresholds, timer alarms, locks, fan backend, external IC pointer, and clockgating enablement from `NvPmEnableGating`.

## Integration Points
Depends on BIOS parsers, PMU fan-control detection, timer alarms, fan/sensor helpers, chip-specific `nvkm_therm_func` callbacks, and public therm attribute APIs.

## Risks
Automatic mode is rejected if PMU firmware owns fan control or no sensor exists. Attribute setters immediately reprogram alarms, so invalid BIOS or userspace values can alter safety behavior. Lock ordering between fan and alarm paths matters.

## Test Signals
Signals include fan mode transitions, temperature reads, threshold events, suspend/resume fan restoration, clockgating logs, and absence of deadlocks in alarm callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fan.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fan.c

## Purpose
Implements common fan target handling, fan backend discovery, tachometer sensing, and BIOS-derived fan defaults.

## Important APIs, Types, And Functions
Key functions are `nvkm_therm_fan_get()`, `nvkm_therm_fan_set()`, `nvkm_therm_fan_sense()`, `nvkm_therm_fan_user_get()`, `nvkm_therm_fan_user_set()`, `nvkm_therm_fan_ctor()`, `nvkm_therm_fan_init()`, and `nvkm_therm_fan_fini()`.

## Control Flow
`nvkm_fan_update()` clamps targets to BIOS min/max, compares current duty, smooths changes by 3 percent steps unless immediate, invokes backend `set`, and schedules another timer alarm until target duty is reached. Constructor chooses PWM, toggle, or nil backend and parses BIOS fan tables.

## State, Persistence, And Dependencies
State is `struct nvkm_fan`: BIOS/perf data, current target percent, alarm, lock, tach GPIO, and backend callbacks.

## Integration Points
Depends on GPIO discovery, BIOS fan tables, timer alarms, chip PWM callbacks, and optional chip tachometer callbacks.

## Risks
Manual writes are rejected outside manual mode. Tachometer fallback busy-waits with sleep ranges and assumes four GPIO transitions per revolution. Bad BIOS limits can clamp fan behavior despite safety checks.

## Test Signals
Signals include fan backend type logs, RPM readings, smooth fan ramp behavior, suspend alarm cancellation, and successful user fan set/get in manual mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fannil.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fannil.c

## Purpose
Provides a dummy fan backend for boards with no controllable fan or externally managed cooling.

## Important APIs, Types, And Functions
`nvkm_fannil_create()` allocates `struct nvkm_fan`, sets type `none / external`, and installs get/set callbacks that return `-ENODEV`.

## Control Flow
Fan constructor falls back here after PWM and toggle creation fail. Later common fan operations see the backend but receive unsupported-operation errors from hardware access.

## State, Persistence, And Dependencies
State is only the allocated fan object and its type/callback fields.

## Integration Points
Integrates with `nvkm_therm_fan_ctor()` as the safe fallback fan backend.

## Risks
Userspace may see fan controls but operations report `-ENODEV`. Automatic fan policy cannot drive cooling through this backend.

## Test Signals
Signals are fallback logs, successful therm construction without fan hardware, and `-ENODEV` on fan get/set paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fannil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fanpwm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fanpwm.c

## Purpose
Implements the PWM fan backend using chip-specific PWM callbacks and GPIO polarity information.

## Important APIs, Types, And Functions
`struct nvkm_fanpwm` extends `nvkm_fan` with the DCB GPIO function. `nvkm_fanpwm_create()`, `nvkm_fanpwm_get()`, and `nvkm_fanpwm_set()` are the key operations.

## Control Flow
Create validates `NvFanPWM`, rejects toggle-mode BIOS fans, and requires chip PWM support. Get reads div/duty through `pwm_get` when enabled or falls back to GPIO level. Set computes divisor from BIOS PWM frequency or perf divisor, handles inverted polarity, programs duty, and enables PWM control.

## State, Persistence, And Dependencies
State includes fan BIOS/perf parameters and the selected GPIO function; hardware state is PWM divisor, duty, and mux enable registers owned by chip callbacks.

## Integration Points
Depends on BIOS fan parsing, GPIO metadata, `nvkm_boolopt()`, and chip implementations in nv40/nv50/gf119/gm107 paths.

## Risks
Duty calculation depends on polarity bits and valid divisors. PWM frequency of zero falls back to perf divisor; invalid BIOS data can produce poor fan behavior.

## Test Signals
Signals are correct duty percent readback, PWM enablement on supported GPIOs, and fallback to toggle/nil when PWM is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fanpwm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fantog.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fantog.c

## Purpose
Implements a software PWM fan backend by toggling a GPIO at a fixed period.

## Important APIs, Types, And Functions
`struct nvkm_fantog` carries a private alarm, lock, period, target percent, and GPIO function. `nvkm_fantog_create()`, `nvkm_fantog_set()`, `nvkm_fantog_get()`, and the alarm callback drive the backend.

## Control Flow
Set disables hardware PWM if present, stores the target, flips the fan GPIO, and schedules the next toggle according to the requested duty cycle over a 100 ms period.

## State, Persistence, And Dependencies
State is the allocated toggle fan object, its target percent, timer alarm, and GPIO output level. No persistent storage exists.

## Integration Points
Used as a fallback from `nvkm_therm_fan_ctor()` when PWM backend creation fails but a drivable fan GPIO exists.

## Risks
Software PWM depends on timer precision and can jitter. The code uses generic DCB fan GPIO lookup in updates rather than only the saved function, so GPIO metadata consistency matters.

## Test Signals
Signals include visible GPIO toggling, target percent readback, fan speed changes, and no timer-alarm leaks on suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fantog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/g84.c

## Purpose
Implements G84 thermal sensor setup, hardware threshold interrupt handling, and thermal constructor.

## Important APIs, Types, And Functions
`g84_temp_get()`, `g84_sensor_setup()`, `g84_therm_program_alarms()`, `g84_therm_intr()`, `g84_therm_init()`, `g84_therm_fini()`, and `g84_therm_new()` are key functions.

## Control Flow
Init enables sensor readout if fuse 0x1a8 indicates availability. Alarm programming writes shutdown, fan boost, critical, and downclock thresholds. Interrupt handling emulates hysteresis by alternating threshold register values and emitting thermal events.

## State, Persistence, And Dependencies
State includes BIOS threshold values, per-threshold alarm state, PTherm interrupt registers, and the thermal subdev locks. Threshold state is in `therm->sensor.alarm_state`.

## Integration Points
Depends on fuse, nv50 PWM helpers, timer-safe locks, and common sensor event handling in `temp.c`.

## Risks
Threshold hysteresis is emulated in software and must be called with the alarm lock held. Sensor availability depends on fuse state; missing sensor returns `-ENODEV`.

## Test Signals
Signals include internal sensor availability logs, threshold register programming, rising/falling events, and clean PTherm/PBUS interrupt acks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gf100.c

## Purpose
Provides a shared helper for programming Fermi/Kepler-style thermal clockgating initialization packs.

## Important APIs, Types, And Functions
`gf100_clkgate_init()` iterates `nvkm_therm_clkgate_pack` entries and writes repeated register/data pairs. The local `pack_for_each_init` macro walks packs and their init arrays.

## Control Flow
For each init entry, the helper writes `count` registers starting at `addr` with stride 8 and the supplied data, tracing each operation.

## State, Persistence, And Dependencies
State is hardware register programming only; the function reads static pack descriptors supplied by chip code.

## Integration Points
Called through `nvkm_therm_func.clkgate_init` by clockgating-capable thermal implementations such as GK104-derived code.

## Risks
The helper blindly applies opaque pack data. Incorrect counts or addresses can affect unrelated engines. Fermi support is explicitly incomplete in comments.

## Test Signals
Signals are trace logs matching expected register writes and stable clockgating behavior on chips that use this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gf100.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gf100.h

## Purpose
Defines shared GF100-era thermal clockgating data structures.

## Important APIs, Types, And Functions
`struct gf100_idle_filter` carries FECS and HUBMMU idle-filter values used by GK104 clockgating enable code.

## Control Flow
The header is included by `gk104.h` and chip clockgating files; runtime code consumes the constants from chip-specific filter instances.

## State, Persistence, And Dependencies
No runtime state is stored here. It defines a compile-time data contract.

## Integration Points
Integrates GF100 helper declarations with GK104 thermal clockgating code.

## Risks
Adding fields changes all chip-specific filter initializers. Values are hardware-specific and not self-validating.

## Test Signals
Compile-time coverage and clockgating trace behavior are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gf100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gf119.c

## Purpose
Implements GF119 thermal support with updated PWM routing, tachometer setup, and polling-based thermal alarms.

## Important APIs, Types, And Functions
`pwm_info()` maps GPIO lines to PWM controller indices. Public helpers are `gf119_fan_pwm_ctrl()`, `gf119_fan_pwm_get()`, `gf119_fan_pwm_set()`, `gf119_fan_pwm_clock()`, `gf119_therm_init()`, and `gf119_therm_new()`.

## Control Flow
PWM helpers inspect GPIO mode, route or program controller registers, and handle hardwired PTHERM PWM. Init runs G84 sensor setup, configures fan tach count timing, selects tach GPIO line, and enables tach counting.

## State, Persistence, And Dependencies
State is hardware PWM/tach register state plus common thermal/fan state. Thresholds use common polling alarms instead of G84 hardware IRQs.

## Integration Points
Integrates common fan PWM backend, GT215 fan-sense helper, G84 temperature readout, and common polling threshold code.

## Risks
`pwm_info()` returns `-ENODEV` on unknown GPIO modes and logs an error. Hardwired PTHERM paths have different clocks and high-bit semantics than GPIO PWM controllers.

## Test Signals
Signals include correct PWM readback, tachometer RPM readings, internal sensor reads, and one-second threshold polling events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gf119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gk104.c

## Purpose
Adds GK104 thermal support with GF119 fan/sensor behavior and Kepler clockgating controls.

## Important APIs, Types, And Functions
`gk104_clkgate_enable()`, `gk104_clkgate_fini()`, `gk104_therm_new_()`, and `gk104_therm_new()` are key functions. Static data includes `gk104_clkgate_engine_info[]` and `gk104_idle_filter`.

## Control Flow
Clockgating enable iterates the engine order, skips missing subdevs, programs ENG_MANT/ENG_FILTER, writes FECS/HUBMMU idle filters, then switches ENG_CLK to AUTO. Fini moves engines back toward RUN/AUTO states. Construction allocates `struct gk104_therm` and stores order/filter pointers.

## State, Persistence, And Dependencies
State extends `nvkm_therm` with static engine-order and idle-filter pointers. Hardware state is engine clockgate registers and idle filter registers.

## Integration Points
Integrates with common therm base, GF119 fan/sensor callbacks, GF100 clockgate pack initialization, and `nvkm_device_subdev()` engine discovery.

## Risks
Clockgating register values are opaque and engine-list dependent. Missing engines are skipped, so board/chip variants require correct subdev registration.

## Test Signals
Signals include `Clockgating enabled` logs, no hangs entering/exiting suspend, stable engine operation under gated clocks, and correct PWM/tach behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gk104.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gk104.h

## Purpose
Defines the GK104 thermal private structures used for clockgating-capable thermal instances.

## Important APIs, Types, And Functions
`struct gk104_clkgate_engine_info` maps subdev type/instance to register offsets. `struct gk104_therm` embeds `nvkm_therm` and stores engine order plus `gf100_idle_filter` pointers.

## Control Flow
Chip construction fills these pointers and the clockgating callbacks use them to iterate engine registers.

## State, Persistence, And Dependencies
No standalone runtime state exists in the header; it defines the layout allocated by `gk104_therm_new_()`.

## Integration Points
Integrates GK104 C code with shared GF100 idle filter definitions and common `subdev/therm.h` structures.

## Risks
Structure layout changes affect `container_of` users through `gk104_therm()`. Engine offset data must match hardware.

## Test Signals
Compile-time coverage and successful GK104 thermal construction are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gk104.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gm107.c

## Purpose
Provides GM107 thermal support with Maxwell-specific hardwired PWM registers.

## Important APIs, Types, And Functions
`gm107_fan_pwm_ctrl()` is a no-op because PWM is hardwired. `gm107_fan_pwm_get()`, `gm107_fan_pwm_set()`, `gm107_fan_pwm_clock()`, and `gm107_therm_new()` define the chip callbacks.

## Control Flow
The common fan backend calls the PWM helpers, which read 0x10eb20/0x10eb24 and write 0x10eb10/0x10eb14. Init and sensor behavior reuse GF119/G84 helpers.

## State, Persistence, And Dependencies
State is common thermal/fan state plus Maxwell PWM register state. There is no file-local heap extension.

## Integration Points
Integrates common polling thresholds, G84 temperature sensor reads, GT215 fan tach reads, and GF119 initialization.

## Risks
The control hook cannot disable PWM routing, so fallback software-toggle assumptions would not apply. Register semantics differ from GF119 PTHERM paths.

## Test Signals
Signals include correct PWM duty/divisor programming, fan RPM readings, and stable automatic fan behavior on GM107.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gm200.c

## Purpose
Provides a minimal GM200 thermal implementation for temperature monitoring and polling thresholds.

## Important APIs, Types, And Functions
`gm200_therm_new()` constructs a common thermal subdev with `g84_therm_init()`, `g84_therm_fini()`, `g84_temp_get()`, and polling alarm programming.

## Control Flow
Init sets up the G84-style sensor, common code constructs fan/sensor state, and threshold handling is done by periodic polling.

## State, Persistence, And Dependencies
State is entirely common thermal state and hardware sensor registers.

## Integration Points
Integrates with the common thermal base and G84 sensor helpers but does not provide PWM or fan-sense callbacks.

## Risks
Lack of fan callbacks means controllable fan support depends on other paths or may fall back to nil. Sensor availability still depends on G84 fuse logic.

## Test Signals
Signals are temperature read success, polling threshold logs, and clean probe/fini on GM200.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gp100.c

## Purpose
Provides GP100 temperature readout and thermal construction for native Nouveau mode.

## Important APIs, Types, And Functions
`gp100_temp_get()` reads 0x020460, checks valid/shadow bits, and returns the integer temperature. `gp100_therm_new()` skips construction when GSP-RM owns the device.

## Control Flow
Construction either returns `-ENODEV` for GSP-RM or creates a common thermal subdev with temperature read and polling alarm callbacks.

## State, Persistence, And Dependencies
State is common thermal state and GP100 sensor register state only.

## Integration Points
Integrates with GSP ownership detection and common polling threshold code.

## Risks
Temperature readout depends on hardware valid bit; fan/PWM callbacks are absent. GSP-RM mode intentionally disables native handling.

## Test Signals
Signals are valid temperature readings on GP100 native mode, `-ENODEV` under GSP-RM, and polling threshold behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gt215.c

## Purpose
Implements GT215 thermal support, including fan tachometer setup and RPM readout.

## Important APIs, Types, And Functions
`gt215_therm_fan_sense()` reads tach count/control registers. `gt215_therm_init()` configures tach counting and sensor setup. `gt215_therm_new()` installs nv50 PWM helpers, G84 temp reads, and polling thresholds.

## Control Flow
Init runs G84 sensor setup, programs tach count period from crystal frequency, selects the tach GPIO line, and enables counting. Fan sense returns tach count converted to RPM when enabled.

## State, Persistence, And Dependencies
State is common thermal/fan state plus tach control registers. No file-local heap state exists.

## Integration Points
Integrates with common fan backend, nv50 PWM operations, G84 temp sensor setup, and polling thresholds.

## Risks
Fan sense depends on a valid tach GPIO and assumes two pulses per revolution. Missing tach returns `-ENODEV`.

## Test Signals
Signals include fan RPM readback, PWM fan control, stable temperature polling, and clean tach enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/gt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/ic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/ic.c

## Purpose
Discovers external thermal monitoring ICs on the primary I2C bus using VBIOS extdev hints or a static probe list.

## Important APIs, Types, And Functions
`nvkm_therm_ic_ctor()` drives discovery. `probe_monitoring_device()` requests an I2C module, instantiates a client, runs driver detection, and stores `therm->ic` on success.

## Control Flow
Constructor finds the primary I2C bus, first tries LM89 and ADT7473 addresses from VBIOS extdev entries, honors VBIOS skip-probe flags, then probes a static list of common monitor chips and addresses.

## State, Persistence, And Dependencies
State is the registered I2C client pointer in `therm->ic`; device-managed allocations and I2C core own client lifetime after registration.

## Integration Points
Depends on Nouveau I2C bus probing, VBIOS extdev parsing, Linux I2C module autoloading, and lm_sensors-compatible chip drivers.

## Risks
Probing can instantiate then unregister clients on failed detection. Static probing risks touching unexpected devices unless VBIOS requests skip-probe.

## Test Signals
Signals include debug logs naming detected ICs, loaded I2C drivers, and stable thermal reads when external monitor support is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/ic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/nv40.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/nv40.c

## Purpose
Implements NV40-era thermal sensor conversion, PWM fan controls, and basic interrupt acking.

## Important APIs, Types, And Functions
Key functions include `nv40_sensor_style()`, `nv40_sensor_setup()`, `nv40_temp_get()`, `nv40_fan_pwm_ctrl()`, `nv40_fan_pwm_get()`, `nv40_fan_pwm_set()`, `nv40_therm_intr()`, and `nv40_therm_new()`.

## Control Flow
Init selects old/new ADC style by chipset and enables sensor readout. Temperature reads apply BIOS slope/offset calibration. PWM helpers support GPIO lines 2 and 9 through legacy registers. Interrupt handler acknowledges PBUS thermal bits and logs status.

## State, Persistence, And Dependencies
State is common thermal/fan state plus ADC/PWM registers and BIOS calibration data.

## Integration Points
Integrates common fan backend, polling threshold programming, and legacy chipset tables.

## Risks
Unsupported chipsets or missing BIOS calibration return `-ENODEV`. PWM support is limited to known GPIO lines. Interrupt handling is mostly diagnostic.

## Test Signals
Signals include calibrated non-negative temperatures, PWM duty read/write on supported lines, and logged/acked thermal interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/nv40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/nv50.c

## Purpose
Implements NV50-era PWM fan controls and temperature conversion.

## Important APIs, Types, And Functions
`nv50_fan_pwm_ctrl()`, `nv50_fan_pwm_get()`, `nv50_fan_pwm_set()`, `nv50_fan_pwm_clock()`, `nv50_temp_get()`, and `nv50_therm_new()` are the important functions.

## Control Flow
PWM line mapping resolves GPIO lines to control registers and indices, then common fan code calls get/set/enable. Temperature setup clears a sensor control bit, waits for stabilization, and converts raw sensor data through BIOS slope/offset fields.

## State, Persistence, And Dependencies
State is common thermal state plus PWM control registers and BIOS calibration data.

## Integration Points
Integrated by NV50 thermal construction and reused by G84/GT215 thermal function tables for PWM.

## Risks
PWM clock constants are partly empirical. Unknown GPIO lines return errors. Missing BIOS calibration disables temperature reads.

## Test Signals
Signals are correct PWM behavior for lines 0x04/0x09/0x10, valid temperatures, and polling threshold events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/priv.h

## Purpose
Defines private Nouveau thermal structures, callback tables, and cross-file helper declarations.

## Important APIs, Types, And Functions
`struct nvkm_fan` stores fan backend state. `struct nvkm_therm_func` defines chip callbacks for init/fini/intr, PWM, temperature, fan sense, alarm programming, and clockgating. The header declares fan, sensor, PWM, chip, and clockgating helpers.

## Control Flow
Common and chip-specific C files include this header to populate function tables, allocate backends, and call shared helpers.

## State, Persistence, And Dependencies
The header stores no runtime state itself but defines the layout of allocated fan objects and callback contracts.

## Integration Points
Integrates all thermal chip implementations with the public `subdev/therm.h` interface, VBIOS types, and fan/sensor helper files.

## Risks
Changing callback semantics affects many chip families. `container_of` macros require embedded object layout to remain correct.

## Test Signals
Compile coverage across all thermal objects and successful runtime construction for multiple chip generations are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/temp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/temp.c

## Purpose
Implements common thermal threshold defaults, BIOS sensor parsing, polling-based threshold emulation, and emergency actions.

## Important APIs, Types, And Functions
Important functions include `nvkm_therm_sensor_ctor()`, `nvkm_therm_sensor_preinit()`, `nvkm_therm_sensor_init()`, `nvkm_therm_sensor_fini()`, `nvkm_therm_program_alarms_polling()`, `nvkm_therm_sensor_event()`, and threshold state get/set helpers.

## Control Flow
Constructor sets default thresholds, parses VBIOS sensor data, and enforces minimum hysteresis. Polling checks current temperature once per second, detects rising/falling transitions around hysteresis windows, updates state, and emits fan boost, downclock, pause, or shutdown actions.

## State, Persistence, And Dependencies
State includes BIOS threshold values, per-threshold alarm states, the polling alarm, and optional emergency callbacks in `therm->emergency`.

## Integration Points
Depends on chip `temp_get`, timer alarms, orderly poweroff workqueue, common fan control, and BIOS thermal sensor parsing.

## Risks
Shutdown uses atomic allocation for work; allocation failure means no poweroff is scheduled. Polling only continues while `temp_get` succeeds. Emergency callbacks must tolerate repeated threshold transitions.

## Test Signals
Signals include threshold crossing logs, fan forced to 100 percent on fanboost, downclock/pause callback activation, and polling alarm cancellation on suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/temp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/Kbuild

## Purpose
Declares the object files that build the Nouveau timer subdevice implementation into `nvkm-y`.

## Important APIs, Types, And Functions
The file contributes these object targets: `base.o`, `nv04.o`, `nv40.o`, `nv41.o`, `gk20a.o`. There are no runtime C APIs.

## Control Flow
Kbuild conditionlessly appends the listed objects when the Nouveau nvkm subtree is built; chip selection happens later through device tables and constructor calls.

## State, Persistence, And Dependencies
No runtime state is persisted. The only dependency is the kernel build system variable expansion for `nvkm-y`.

## Integration Points
Integrated by the parent Nouveau nvkm Kbuild so the timer constructors and helpers are linkable.

## Risks
Missing an object silently removes a chip implementation at link time; adding an object here without matching declarations can create unresolved symbols.

## Test Signals
Build coverage is the primary signal: enabled Nouveau configurations should compile and link all listed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/base.c

## Purpose
Implements the common nvkm timer subdevice, timed waits, ordered alarm scheduling, and lifecycle wiring.

## Important APIs, Types, And Functions
`nvkm_timer_wait_init()`, `nvkm_timer_wait_test()`, `nvkm_timer_read()`, `nvkm_timer_alarm()`, `nvkm_timer_alarm_trigger()`, and `nvkm_timer_new_()` are core APIs.

## Control Flow
Init programs hardware time to current kernel time and triggers any pending alarms. `nvkm_timer_alarm()` inserts or cancels alarms under a spinlock in timestamp order. Interrupts call chip `.intr`, which eventually invokes `nvkm_timer_alarm_trigger()` to move due alarms to an exec list and run callbacks outside the lock.

## State, Persistence, And Dependencies
State includes the timer function table, alarm list, spinlock, per-alarm timestamps, and wait-test counters. Alarm state is in memory only.

## Integration Points
Depends on chip-specific hardware timer functions, nvkm subdev lifecycle, kernel time, and callback users such as therm and PMU DVFS.

## Risks
Alarm timestamps are `u32` nanosecond offsets and wrap behavior is noted as a worst-case delay. Callbacks can reschedule themselves, so lock ordering is important.

## Test Signals
Signals include stable timed waits, alarm ordering under multiple users, timer interrupt delivery, and no stalled timer fatal logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/gk20a.c

## Purpose
Provides GK20A timer construction by reusing NV04-compatible timer operations.

## Important APIs, Types, And Functions
`gk20a_timer_new()` passes a static function table to `nvkm_timer_new_()` using `nv04_timer_intr`, `nv04_timer_read`, `nv04_timer_time`, `nv04_timer_alarm_init`, and `nv04_timer_alarm_fini`.

## Control Flow
Construction allocates the common timer object; all runtime behavior is delegated to NV04-style register handlers.

## State, Persistence, And Dependencies
State is the common timer object and the NV04-compatible hardware timer registers.

## Integration Points
Integrates Tegra GK20A device setup with the generic timer base and NV04 register accessors.

## Risks
Assumes GK20A timer registers match NV04 semantics. Any SoC-specific clock difference is not handled here.

## Test Signals
Signals are functioning timer alarms on GK20A, especially PMU DVFS and thermal polling alarms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/gk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/nv04.c

## Purpose
Implements NV04-style hardware timer register access, alarm programming, interrupts, and construction.

## Important APIs, Types, And Functions
`nv04_timer_time()`, `nv04_timer_read()`, `nv04_timer_alarm_init()`, `nv04_timer_alarm_fini()`, `nv04_timer_intr()`, and `nv04_timer_new()` are the key operations.

## Control Flow
Time writes split a 64-bit value into high/low registers. Reads retry until the high word is stable. Alarm init writes the low alarm register and enables interrupt bit 0; interrupts acknowledge bit 0 and trigger common alarm dispatch.

## State, Persistence, And Dependencies
State is hardware PTIMER registers plus common timer alarm lists. Init may reuse existing numerator/denominator if input clock is unknown.

## Integration Points
Depends on `regsnv04.h`, nvkm MMIO, and common timer alarm dispatch.

## Risks
Clock setup has an unknown input frequency path and may leave an imprecise timer. Alarm programming uses a 32-bit low timestamp.

## Test Signals
Signals include monotonic reads, correctly delivered alarm interrupts, no unexpected interrupt bits, and usable timer frequency logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/nv40.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/nv40.c

## Purpose
Provides NV40 timer initialization while reusing NV04 read, write, alarm, and interrupt helpers.

## Important APIs, Types, And Functions
`nv40_timer_init()` computes/reduces numerator and denominator values and `nv40_timer_new()` constructs the common timer object.

## Control Flow
Init aims for a 31.25 MHz timer, falls back to current hardware numerator/denominator when input frequency is unknown, reduces the ratio, and writes PTIMER registers.

## State, Persistence, And Dependencies
State is hardware PTIMER numerator/denominator and common timer state.

## Integration Points
Integrates with NV04 timer helpers and the common timer base.

## Risks
Input clock remains a TODO, so accuracy depends on inherited register values when `f` is zero. Ratio reduction must avoid zero denominators.

## Test Signals
Signals are timer frequency debug output, stable timed waits, and alarm delivery on NV40 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/nv40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/nv41.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/nv41.c

## Purpose
Implements NV41 timer initialization using the device crystal and an input multiplier.

## Important APIs, Types, And Functions
`nv41_timer_init()` derives multiplier, numerator, and denominator; `nv41_timer_new()` constructs the timer with NV04-compatible operations.

## Control Flow
Init increases the effective input frequency until it is large enough for the target denominator, reduces the ratio, writes multiplier register 0x009220, and programs PTIMER numerator/denominator.

## State, Persistence, And Dependencies
State is hardware multiplier and PTIMER ratio plus common timer alarm state.

## Integration Points
Depends on `device->crystal`, NV04 register definitions, and common timer base.

## Risks
Bad crystal values would produce inaccurate timing. The multiplier loop and ratio reduction are sensitive to integer arithmetic.

## Test Signals
Signals include expected frequency debug logs, monotonic timer reads, and correct alarm scheduling on NV41-class chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/nv41.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/priv.h

## Purpose
Defines private timer callback contracts and shared NV04 helper declarations.

## Important APIs, Types, And Functions
`struct nvkm_timer_func` contains init, interrupt, read, time set, alarm init, and alarm fini callbacks. The header declares `nvkm_timer_new_()`, `nvkm_timer_alarm_trigger()`, and NV04 helper functions.

## Control Flow
Chip timer files populate the callback table and pass it to common construction.

## State, Persistence, And Dependencies
No runtime state exists in the header; it defines the callback ABI for `struct nvkm_timer`.

## Integration Points
Integrates NV04/NV40/NV41/GK20A implementations with the common timer base.

## Risks
Callback signature changes affect all timer chips and alarm users.

## Test Signals
Compile-time coverage and timer subdev construction across chip variants are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/regsnv04.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/regsnv04.h

## Purpose
Defines NV04 PTIMER MMIO register offsets shared by legacy timer implementations.

## Important APIs, Types, And Functions
Macros cover interrupt status, interrupt enable, numerator, denominator, time low/high, and alarm registers.

## Control Flow
C files include these constants to read/write PTIMER state through nvkm MMIO helpers.

## State, Persistence, And Dependencies
No runtime state exists in the header.

## Integration Points
Integrated by NV04, NV40, and NV41 timer files.

## Risks
Incorrect offsets would break all legacy timer operations. The header intentionally contains only constants.

## Test Signals
Build coverage and correct timer behavior on legacy chips validate these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/regsnv04.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/Kbuild

## Purpose
Declares the object files that build the Nouveau topology subdevice implementation into `nvkm-y`.

## Important APIs, Types, And Functions
The file contributes these object targets: `base.o`, `gk104.o`, `ga100.o`. There are no runtime C APIs.

## Control Flow
Kbuild conditionlessly appends the listed objects when the Nouveau nvkm subtree is built; chip selection happens later through device tables and constructor calls.

## State, Persistence, And Dependencies
No runtime state is persisted. The only dependency is the kernel build system variable expansion for `nvkm-y`.

## Integration Points
Integrated by the parent Nouveau nvkm Kbuild so the topology constructors and helpers are linkable.

## Risks
Missing an object silently removes a chip implementation at link time; adding an object here without matching declarations can create unresolved symbols.

## Test Signals
Build coverage is the primary signal: enabled Nouveau configurations should compile and link all listed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/base.c

## Purpose
Implements common GPU topology parsing storage and lookup helpers for engine addresses, reset bits, interrupt masks, and fault IDs.

## Important APIs, Types, And Functions
Important functions are `nvkm_top_device_new()`, `nvkm_top_addr()`, `nvkm_top_reset()`, `nvkm_top_intr_mask()`, `nvkm_top_fault_id()`, `nvkm_top_fault()`, `nvkm_top_parse()`, and `nvkm_top_new_()`.

## Control Flow
Construction initializes the topology list. `nvkm_top_parse()` lazily invokes the chip parser only once. Lookup helpers scan the list for matching type/instance and return encoded address, reset, interrupt, or fault mapping.

## State, Persistence, And Dependencies
State is the `nvkm_top` subdev and its linked list of `nvkm_top_device` records, freed at dtor.

## Integration Points
Depends on chip parsers in GK104/GA100 files and on `nvkm_device_subdev()` for reverse fault mapping.

## Risks
Lookups return zero or `-ENOENT` for missing data, so callers must distinguish absent topology from valid zero address where relevant. Parser allocation failures stop topology discovery.

## Test Signals
Signals include parsed debug lines, correct engine reset/intr/fault mapping, and no duplicate parse after the list is populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/ga100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/ga100.c

## Purpose
Parses GA100-style topology tables for Ampere engines and subdevices in native Nouveau mode.

## Important APIs, Types, And Functions
`ga100_top_parse()` reads table size from 0x0224fc and entries from 0x022800. `ga100_top_new()` gates construction on GSP-RM and calls `nvkm_top_new_()`.

## Control Flow
The parser groups up to three words per device, decodes type, instance, fault, address, reset, runlist, and engine fields, then translates hardware type IDs to NVKM engine/subdev identifiers.

## State, Persistence, And Dependencies
State is allocated `nvkm_top_device` list entries under the common top object.

## Integration Points
Integrates with GSP ownership detection, common topology lookup helpers, and Ampere engine class mapping.

## Risks
Unknown hardware type IDs leave entries as `NVKM_SUBDEV_NR`. Multiword parsing depends on continuation bit 31 and table size correctness.

## Test Signals
Signals are topology debug logs for GR/SEC2/NVENC/NVDEC/IOCTRL/CE/GSP/NVJPG/OFA/FLA entries and correct fault/reset lookup results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/ga100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/gk104.c

## Purpose
Parses GK104-style topology records for Kepler and later native Nouveau engines.

## Important APIs, Types, And Functions
`gk104_top_parse()` scans 64 entries at 0x022700 and decodes DATA, ENUM, and ENGINE_TYPE record kinds. `gk104_top_new()` skips construction under GSP-RM.

## Control Flow
For each record group, parser accumulates instance, address, fault, engine, runlist, interrupt, reset, and type fields until continuation clears, then maps type IDs to NVKM subdev/engine identifiers.

## State, Persistence, And Dependencies
State is the common topology device list. No filesystem persistence exists.

## Integration Points
Integrates with topology base lookups and GSP-RM ownership gating.

## Risks
Unknown type IDs remain unresolved. The parser assumes a 64-entry fixed table and correct record kind bits.

## Test Signals
Signals include debug output for expected engines, valid interrupt/reset masks, and correct behavior when GSP-RM is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/priv.h

## Purpose
Defines the private topology parser callback contract and shared allocation helper.

## Important APIs, Types, And Functions
`struct nvkm_top_func` contains the chip `parse` callback. The header declares `nvkm_top_new_()` and `nvkm_top_device_new()`.

## Control Flow
Chip files include this header, provide a parse function, and use the helper to allocate list entries.

## State, Persistence, And Dependencies
No runtime state is stored in the header; it defines the callback ABI.

## Integration Points
Integrates GK104 and GA100 topology parsers with the common top base.

## Risks
Callback or structure changes require coordinated updates across topology files.

## Test Signals
Compile-time coverage and successful topology parsing are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/Kbuild

## Purpose
Declares the object files that build the Nouveau VFN subdevice implementation into `nvkm-y`.

## Important APIs, Types, And Functions
The file contributes these object targets: `base.o`, `uvfn.o`, `gv100.o`, `tu102.o`, `ga100.o`, `r535.o`. There are no runtime C APIs.

## Control Flow
Kbuild conditionlessly appends the listed objects when the Nouveau nvkm subtree is built; chip selection happens later through device tables and constructor calls.

## State, Persistence, And Dependencies
No runtime state is persisted. The only dependency is the kernel build system variable expansion for `nvkm-y`.

## Integration Points
Integrated by the parent Nouveau nvkm Kbuild so the VFN constructors and helpers are linkable.

## Risks
Missing an object silently removes a chip implementation at link time; adding an object here without matching declarations can create unresolved symbols.

## Test Signals
Build coverage is the primary signal: enabled Nouveau configurations should compile and link all listed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/base.c

## Purpose
Implements common VFN subdevice construction for usermode register aperture exposure and optional interrupt fanout.

## Important APIs, Types, And Functions
`nvkm_vfn_new_()` allocates `struct nvkm_vfn`, sets private/user address bases, registers optional interrupt leaves through `nvkm_intr_add()`, and installs the user object constructor `nvkm_uvfn_new`.

## Control Flow
Construction computes `addr.user = addr.priv + func->user.addr`; if an interrupt function is provided it creates an interrupt controller with up to eight leaves; then it advertises a user class and aperture size.

## State, Persistence, And Dependencies
State includes `nvkm_vfn`, address fields, interrupt object, and user class metadata.

## Integration Points
Depends on nvkm subdev construction, interrupt infrastructure, and `uvfn.c` for mapping usermode registers to clients.

## Risks
If interrupt registration fails, construction returns an error after allocation. Address arithmetic must match chip BAR0 layouts.

## Test Signals
Signals include successful VFN subdev creation, valid usermode object class exposure, and interrupt leaves dispatching to configured subdevices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/ga100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/ga100.c

## Purpose
Defines GA100 VFN usermode aperture and interrupt routing, selecting native or R535-backed construction depending on GSP-RM.

## Important APIs, Types, And Functions
`ga100_vfn_intrs[]` maps DISP, GPIO, I2C, and PRIVRING interrupts to leaf 4 masks. `ga100_vfn_new()` constructs with private base 0xb80000 and Ampere usermode class.

## Control Flow
When GSP-RM is active, construction delegates to `r535_vfn_new()` so the usermode class comes from RM metadata; otherwise it uses the static GA100 function table.

## State, Persistence, And Dependencies
State is common VFN state plus the static interrupt routing table.

## Integration Points
Integrates with TU102 interrupt register functions, R535 RM GPU metadata, and Ampere usermode class IDs.

## Risks
Interrupt masks must match GA100 hardware routing. GSP-RM and native paths expose similar apertures through different class metadata sources.

## Test Signals
Signals include correct usermode mapping, interrupt delivery for routed subdevices, and successful behavior in both native and RM-managed modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/ga100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/gv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/gv100.c

## Purpose
Defines GV100 VFN usermode aperture support without a private interrupt block.

## Important APIs, Types, And Functions
`gv100_vfn_new()` constructs a VFN with private base 0 and user aperture 0x810000/0x010000 using `VOLTA_USERMODE_A`.

## Control Flow
Construction delegates all behavior to `nvkm_vfn_new_()` with a function table that only describes the user aperture.

## State, Persistence, And Dependencies
State is common VFN state and user mapping metadata.

## Integration Points
Integrates Volta usermode class exposure with the common VFN and UVFN mapping path.

## Risks
No interrupt callbacks are provided; callers must not expect VFN interrupt fanout on GV100 through this file.

## Test Signals
Signals are successful usermode object creation and correct BAR0 mapping size/address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/gv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/priv.h

## Purpose
Defines private VFN function tables and helper declarations.

## Important APIs, Types, And Functions
`struct nvkm_vfn_func` includes optional dtor, interrupt function/data, and user aperture/class metadata. It declares `r535_vfn_new()`, `nvkm_vfn_new_()`, `tu102_vfn_intr`, and `nvkm_uvfn_new()`.

## Control Flow
Chip files populate this table and base construction consumes it to build subdevices and user objects.

## State, Persistence, And Dependencies
No runtime state is held in the header; it defines the ABI for `struct nvkm_vfn` construction.

## Integration Points
Integrates VFN chip wrappers, R535 RM-backed construction, interrupt helpers, and UVFN object mapping.

## Risks
Function table changes affect native and RM-managed VFN paths. User aperture fields must remain consistent with mapping code.

## Test Signals
Compile-time coverage and creation of usermode objects across Volta/Turing/Ampere are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/r535.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/r535.c

## Purpose
Builds a VFN function table for GPUs managed by NVIDIA's R535 GSP-RM firmware interface.

## Important APIs, Types, And Functions
`r535_vfn_new()` allocates a mutable `nvkm_vfn_func`, fills TU102 interrupt ops, standard user aperture dimensions, and the usermode class from `device->gsp->rm->gpu`. `r535_vfn_dtor()` frees that copied table.

## Control Flow
Construction copies RM-provided class metadata, delegates to `nvkm_vfn_new_()`, and frees the table on failure or dtor.

## State, Persistence, And Dependencies
State includes the dynamically allocated function table owned by the VFN object and RM GPU metadata read during construction.

## Integration Points
Integrates VFN with GSP-RM `struct nvkm_rm_gpu` and shared TU102 interrupt register operations.

## Risks
The dtor must be called to avoid leaking the copied table. It assumes RM GPU metadata is initialized before VFN construction.

## Test Signals
Signals include correct usermode class from RM, no leaks across probe/remove, and working interrupt operations in GSP-RM mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/r535.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/tu102.c

## Purpose
Implements TU102 VFN interrupt register operations and Turing usermode aperture construction.

## Important APIs, Types, And Functions
`tu102_vfn_intr_reset()`, `_allow()`, `_block()`, `_rearm()`, `_unarm()`, and `_pending()` form `tu102_vfn_intr`. `tu102_vfn_new()` selects native or R535-backed construction.

## Control Flow
Interrupt methods write per-leaf reset/allow/block registers relative to the private VFN base, arm/unarm top-level bits, and read pending status for eight leaves from status registers gated by top bits.

## State, Persistence, And Dependencies
State is common VFN state plus `intr->stat[]` leaf status snapshots and MMIO interrupt registers.

## Integration Points
Integrated by TU102 native VFN and reused by GA100 and R535 paths.

## Risks
Pending logic checks `BIT(leaf / 2)`, so two leaves share a top bit. Register offsets are tied to the Turing/Ampere VFN layout.

## Test Signals
Signals include correct leaf status capture, interrupt allow/block/reset behavior, and successful usermode mapping in native and GSP-RM modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/uvfn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/uvfn.c

## Purpose
Implements the user-visible VFN object that maps the GPU usermode register aperture.

## Important APIs, Types, And Functions
`struct nvkm_uvfn` embeds `nvkm_object` and stores a VFN pointer. `nvkm_uvfn_new()` creates the object, and `nvkm_uvfn_map()` returns BAR0 physical address, size, and IO mapping type.

## Control Flow
Object creation rejects non-empty constructor arguments, stores `device->vfn`, and returns the object. Mapping adds `vfn->addr.user` to the BAR0 PRI resource base and exposes `func->user.size`.

## State, Persistence, And Dependencies
State is the per-object VFN pointer and nvkm object lifetime state.

## Integration Points
Integrates with VFN base user class metadata and nvkm object mapping APIs.

## Risks
Assumes `device->vfn` exists and BAR0 PRI resource address is valid. No argument ABI is supported yet.

## Test Signals
Signals include successful user object construction with zero args and correct mmap address/size reported to userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/uvfn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/Kbuild

## Purpose
Declares the object files that build the Nouveau voltage subdevice implementation into `nvkm-y`.

## Important APIs, Types, And Functions
The file contributes these object targets: `base.o`, `gpio.o`, `nv40.o`, `gf100.o`, `gf117.o`, `gk104.o`, `gk20a.o`, `gm20b.o`. There are no runtime C APIs.

## Control Flow
Kbuild conditionlessly appends the listed objects when the Nouveau nvkm subtree is built; chip selection happens later through device tables and constructor calls.

## State, Persistence, And Dependencies
No runtime state is persisted. The only dependency is the kernel build system variable expansion for `nvkm-y`.

## Integration Points
Integrated by the parent Nouveau nvkm Kbuild so the voltage constructors and helpers are linkable.

## Risks
Missing an object silently removes a chip implementation at link time; adding an object here without matching declarations can create unresolved symbols.

## Test Signals
Build coverage is the primary signal: enabled Nouveau configurations should compile and link all listed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/base.c

## Purpose
Implements common voltage table parsing, voltage/VID mapping, conditional voltage setting, speedo handling, and subdev construction.

## Important APIs, Types, And Functions
Important APIs include `nvkm_volt_get()`, `nvkm_volt_map_min()`, `nvkm_volt_map()`, `nvkm_volt_set_id()`, `nvkm_volt_ctor()`, and `nvkm_volt_new_()`.

## Control Flow
Constructor parses VBIOS voltage and VMAP tables into VID entries, min/max microvolts, and max voltage IDs. Oneinit reads speedo and calls chip oneinit. Set-by-ID maps VBIOS voltage IDs through polynomial/linked VMAP entries, applies min IDs and condition direction, then sets either direct voltage or VID.

## State, Persistence, And Dependencies
State includes VID table entries, min/max voltage, VID mask, speedo, max voltage IDs, and chip callbacks in `struct nvkm_volt`.

## Integration Points
Depends on BIOS volt/vmap parsers, thermal temperature inputs for maps, GPIO or PWM/regulator chip callbacks, and fuse speedo readers.

## Risks
Mapping math is version/mode sensitive and uses fixed-point integer formulas. Missing speedo blocks mapped voltage. Conditional updates rely on accurate current voltage reads.

## Test Signals
Signals include parsed VID debug lines, current voltage logs, correct voltage changes for pstate transitions, and graceful handling of missing BIOS data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gf100.c

## Purpose
Provides GF100 voltage support using GPIO VID pins and fuse speedo value 0x1cc.

## Important APIs, Types, And Functions
`gf100_volt_speedo_read()`, `gf100_volt_oneinit()`, and `gf100_volt_new()` are the key functions. The function table uses `nvkm_voltgpio_get()` and `nvkm_voltgpio_set()`.

## Control Flow
Construction builds the common voltage object, then initializes valid GPIO VID bits. Oneinit reports an error if speedo was not found, because VMAP-based voltage computation needs it.

## State, Persistence, And Dependencies
State is common voltage state, VID GPIO mask, and speedo value.

## Integration Points
Integrates with fuse, GPIO VID helpers, and common voltage BIOS parsing.

## Risks
No fuse subdev or non-positive speedo leaves voltage control effectively unavailable. Invalid GPIO VID bits are masked by `nvkm_voltgpio_init()`.

## Test Signals
Signals include speedo debug/error logs, VID GPIO readback, and correct voltage table selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gf117.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gf117.c

## Purpose
Provides GF117 voltage support with GPIO VID pins and a GF117-specific speedo fuse offset.

## Important APIs, Types, And Functions
`gf117_volt_speedo_read()` reads fuse 0x3a8. `gf117_volt_new()` constructs the common voltage object and initializes GPIO VID handling.

## Control Flow
Runtime behavior mirrors GF100: read speedo at oneinit, use common voltage mapping, and drive VID GPIO lines for voltage changes.

## State, Persistence, And Dependencies
State is common voltage state plus speedo and valid VID mask.

## Integration Points
Depends on fuse, GPIO, common voltage parsing, and GF100 oneinit validation.

## Risks
If fuse is absent or speedo invalid, mapped voltage control is not possible. The fuse offset is chip-specific.

## Test Signals
Signals are speedo read logs, valid VID GPIO mask, and voltage get/set behavior on GF117 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gf117.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gk104.c

## Purpose
Implements GK104 voltage support with either PWM voltage control or GPIO VID fallback.

## Important APIs, Types, And Functions
`gk104_volt_get()`, `gk104_volt_set()`, `gk104_volt_speedo_read()`, and `gk104_volt_new()` are key functions. `struct gk104_volt` stores the parsed BIOS voltage table.

## Control Flow
Constructor parses the BIOS voltage table, selects PWM mode when a `DCB_GPIO_VID_PWM` GPIO and PWM voltage type match, otherwise uses GPIO VID mode, initializes GPIO bits if needed, and logs the mode. PWM set computes divider from 27.648 MHz and BIOS frequency.

## State, Persistence, And Dependencies
State includes common voltage state plus saved `nvbios_volt` fields for PWM base/range/frequency.

## Integration Points
Depends on BIOS voltage table, GPIO table, fuse speedo, and common voltage mapping.

## Risks
If BIOS says PWM but no matching GPIO exists, the code logs an error and falls back to GPIO. PWM formula assumes requested voltage is within BIOS base/range.

## Test Signals
Signals include `Using PWM/GPIO mode` logs, voltage readback via PWM registers or VID pins, and successful pstate voltage transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gk20a.c

## Purpose
Implements Tegra GK20A regulator-backed voltage tables computed from CVB coefficients and GPU speedo.

## Important APIs, Types, And Functions
`gk20a_volt_get_cvb_voltage()`, `gk20a_volt_get_cvb_t_voltage()`, `gk20a_volt_calc_voltage()`, `gk20a_volt_vid_get()`, `gk20a_volt_vid_set()`, `gk20a_volt_set_id()`, `gk20a_volt_ctor()`, and `gk20a_volt_new()` are important.

## Control Flow
Constructor reads the default regulator voltage, stores the Tegra VDD regulator, computes one VID entry per CVB coefficient using speedo and a fixed temperature point, and clamps to minimum voltage. Set paths call Linux regulator APIs directly.

## State, Persistence, And Dependencies
State is `struct gk20a_volt`, regulator pointer, computed VID table, and Tegra speedo data. Voltage is persisted only in the regulator hardware state.

## Integration Points
Depends on `core/tegra.h`, Linux regulator API, common voltage base, and SoC speedo data.

## Risks
The table uses fixed coefficients and -10 C calculation assumptions. `regulator_set_voltage()` uses 1.2 V as max bound for all entries.

## Test Signals
Signals include computed VID debug table, regulator voltage readback, and DVFS pstate changes successfully adjusting voltage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gk20a.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gk20a.h

## Purpose
Defines shared Tegra GK20A/GM20B voltage coefficient and object structures.

## Important APIs, Types, And Functions
`struct cvb_coef` stores CVB polynomial coefficients. `struct gk20a_volt` embeds `nvkm_volt` and stores the VDD regulator. `gk20a_volt_ctor()` is declared for reuse.

## Control Flow
GM20B and GK20A source files pass chip-specific coefficient arrays into the shared constructor.

## State, Persistence, And Dependencies
No standalone runtime state exists in the header, but it defines the allocated Tegra voltage object layout.

## Integration Points
Integrates Tegra voltage variants with the common GK20A CVB/regulator implementation.

## Risks
Structure changes affect `container_of` and GM20B reuse. Coefficient semantics must match the constructor formulas.

## Test Signals
Compile coverage and successful GK20A/GM20B voltage object construction are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gk20a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gm20b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gm20b.c

## Purpose
Provides GM20B Tegra voltage tables by selecting CVB coefficients and minimum voltage from SoC speedo ID.

## Important APIs, Types, And Functions
`gm20b_volt_new()` chooses between `gm20b_cvb_coef` and `gm20b_na_cvb_coef`, validates `gpu_speedo_id`, allocates `gk20a_volt`, and calls `gk20a_volt_ctor()`.

## Control Flow
Construction maps speedo IDs to minimum voltage, uses the non-automotive coefficient table for speedo ID >= 1, otherwise the base table, and builds regulator-backed VID entries.

## State, Persistence, And Dependencies
State is the shared `gk20a_volt` object plus selected coefficient-derived VID table and Tegra regulator pointer.

## Integration Points
Depends on Tegra device data, GK20A voltage constructor, Linux regulator APIs, and SoC speedo IDs.

## Risks
Unsupported speedo IDs return `-EINVAL`. Correct voltage behavior depends on accurate speedo-to-vmin table and coefficient set selection.

## Test Signals
Signals include expected computed voltage table per speedo ID, no unsupported-speedo errors on known boards, and successful regulator voltage changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gm20b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gpio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gpio.c

## Purpose
Implements GPIO VID bit get/set and validation for voltage controllers using discrete VID pins.

## Important APIs, Types, And Functions
`nvkm_voltgpio_get()`, `nvkm_voltgpio_set()`, and `nvkm_voltgpio_init()` are the public helpers. The static `tags[]` table maps VID bit positions to DCB GPIO functions.

## Control Flow
Init verifies each VID bit has a GPIO function, masking missing bits when the VBIOS advertises more VID bits than the board wires. Get samples each valid bit and assembles a VID value; set writes each valid bit from the requested VID.

## State, Persistence, And Dependencies
State is the mutable `volt->vid_mask` and GPIO hardware levels.

## Integration Points
Depends on VBIOS GPIO metadata and the Nouveau GPIO subdev.

## Risks
Missing GPIOs are tolerated only for `-ENOENT`; other GPIO errors abort. Masking bits can reduce available voltage states.

## Test Signals
Signals include debug logs for missing VID bits, valid VID readback, and voltage changes through GPIO pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/nv40.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/nv40.c

## Purpose
Provides NV40 voltage support through GPIO VID pins.

## Important APIs, Types, And Functions
`nv40_volt_new()` constructs a common voltage object with `nvkm_voltgpio_get()` and `nvkm_voltgpio_set()`, then initializes GPIO VID metadata.

## Control Flow
Runtime voltage get/set behavior is entirely delegated to common VID table mapping and GPIO bit helpers.

## State, Persistence, And Dependencies
State is common voltage object data and valid VID GPIO mask.

## Integration Points
Integrates legacy NV40 chipset voltage support with the shared voltage base and GPIO helpers.

## Risks
No speedo or direct voltage callbacks are available; behavior depends on BIOS VID tables and GPIO metadata.

## Test Signals
Signals include parsed VID table logs, valid GPIO mask initialization, and successful voltage get/set by VID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/nv40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/priv.h

## Purpose
Defines private voltage callback contracts and shared helper declarations.

## Important APIs, Types, And Functions
`struct nvkm_volt_func` includes oneinit, direct voltage get/set, VID get/set, set-by-ID override, and speedo read callbacks. The header declares common constructors and GPIO/PWM/helper functions.

## Control Flow
Chip files populate the callback table, and common voltage base invokes callbacks through `struct nvkm_volt`.

## State, Persistence, And Dependencies
No runtime state exists in the header; it defines voltage subdev ABI.

## Integration Points
Integrates NV40/GF100/GF117/GK104/Tegra voltage implementations with common voltage parsing and GPIO helpers.

## Risks
Callback changes affect all voltage drivers. Declared PWM helpers are not implemented in this assigned subset, so users must link only available objects.

## Test Signals
Compile coverage across voltage variants and successful voltage object construction are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/Kconfig

## Purpose
Defines the build-time configuration option for the experimental Rust Nova DRM driver for NVIDIA GSP-based GPUs.

## Important APIs, Types, And Functions
`config DRM_NOVA` is a tristate depending on 64-bit, built-in DRM, PCI, and Rust; it selects `AUXILIARY_BUS` and `NOVA_CORE`.

## Control Flow
When enabled, Kconfig allows building the `nova` module and pulls in the auxiliary bus and Nova core support required by the Rust DRM frontend.

## State, Persistence, And Dependencies
No runtime state exists here; it controls kernel configuration.

## Integration Points
Integrated by the DRM Kconfig hierarchy and Nova Makefile. It constrains the driver to platforms where Rust, PCI, and DRM prerequisites exist.

## Risks
The option depends on `DRM=y`, not module DRM, which limits build combinations. Help text warns the driver is work in progress and may not function.

## Test Signals
Signals are Kconfig dependency resolution and successful `CONFIG_DRM_NOVA=m/y` builds with Rust enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/Makefile

## Purpose
Connects the Nova DRM Rust module to the kernel build.

## Important APIs, Types, And Functions
`obj-$(CONFIG_DRM_NOVA) += nova.o` builds the Rust module object when the Kconfig option is enabled.

## Control Flow
The kernel build system compiles the Rust crate rooted at `nova.rs` into `nova.o` for enabled configurations.

## State, Persistence, And Dependencies
No runtime state exists here.

## Integration Points
Integrated by the DRM GPU Makefile and Kconfig option `DRM_NOVA`.

## Risks
Any missing Rust module source or symbol errors surface only at build time.

## Test Signals
Build success with `CONFIG_DRM_NOVA` enabled is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/driver.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/driver.rs

## Purpose
Implements the Rust Nova DRM auxiliary driver, DRM device registration, file/object type binding, and ioctl table.

## Important APIs, Types, And Functions
`NovaDriver`, `NovaDevice`, `NovaData`, `INFO`, and the auxiliary device table are central. The `auxiliary::Driver` impl probes `nova-drm` auxiliary devices. The `drm::Driver` impl declares `NOVA_GETPARAM`, `NOVA_GEM_CREATE`, and `NOVA_GEM_INFO` ioctls.

## Control Flow
Probe stores an `ARef` to the auxiliary device, creates a DRM device with that data, registers it as foreign-owned, and returns a driver instance holding the DRM reference.

## State, Persistence, And Dependencies
State is the DRM device reference in `NovaDriver` and the auxiliary device reference in `NovaData`. DRM core owns file and GEM object state.

## Integration Points
Depends on Rust-for-Linux auxiliary and DRM abstractions, Nova core auxiliary devices named `NovaCore.nova-drm`, and the file/GEM modules.

## Risks
The driver version is 0.0.0 and the driver is experimental. Registration lifetime relies on `ARef` and foreign-owned DRM registration semantics.

## Test Signals
Signals include auxiliary probe, DRM device node creation, ioctl registration, and successful open/GEM ioctl smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/driver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/file.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/file.rs

## Purpose
Implements Nova per-file state and ioctl handlers for parameter queries and GEM object management.

## Important APIs, Types, And Functions
`File` implements `drm::file::DriverFile`. Ioctl handlers are `get_param()`, `gem_create()`, and `gem_info()`.

## Control Flow
Open allocates an empty `File`. `get_param` converts the auxiliary parent to a PCI device and returns BAR1 size for `NOVA_GETPARAM_VRAM_BAR_SIZE`. `gem_create` creates a page-aligned `NovaObject` and returns a handle. `gem_info` looks up a handle and reports object size.

## State, Persistence, And Dependencies
Per-open state is currently empty. GEM handles and objects are managed by DRM core; returned ioctl fields persist only to userspace.

## Integration Points
Depends on Rust DRM file/GEM traits, PCI resource access, uapi constants, and `NovaObject` helpers.

## Risks
Unsupported params return `EINVAL`. Parent device conversion assumes the auxiliary parent is PCI. Object sizes are converted with checked conversions.

## Test Signals
Signals include successful DRM open, BAR size query, GEM create with nonzero size, GEM info returning aligned size, and invalid handle/param errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/gem.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/gem.rs

## Purpose
Defines the Nova GEM driver object wrapper and allocation/lookup helpers.

## Important APIs, Types, And Functions
`NovaObject` implements `gem::DriverObject` with no inner fields. `NovaObject::new()` validates size, page-aligns it, and calls `gem::Object::new()`. `lookup_handle()` wraps DRM GEM handle lookup.

## Control Flow
GEM creation rejects zero size, page-aligns with overflow checking, then delegates allocation to DRM GEM core. Lookup returns an owned reference to the GEM object for a file handle.

## State, Persistence, And Dependencies
State is held by DRM GEM core; the driver object currently has no extra fields.

## Integration Points
Depends on Rust DRM GEM abstractions, page alignment helpers, `ARef`, and Nova file/driver types.

## Risks
No placement, VRAM backing, mmap, or GPU binding state exists yet. Large sizes that fail page alignment return `EINVAL`.

## Test Signals
Signals include zero-size rejection, aligned size reporting through `gem_info`, handle lifetime correctness, and object cleanup through DRM core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/gem.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/nova.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/nova.rs

## Purpose
Defines the Nova Rust module root, submodules, and auxiliary driver registration metadata.

## Important APIs, Types, And Functions
Declares `mod driver`, `mod file`, and `mod gem`, imports `NovaDriver`, and invokes `kernel::module_auxiliary_driver!` with module name, author, description, and GPL v2 license.

## Control Flow
At module load, Rust-for-Linux registration hooks register the auxiliary driver type; probe behavior lives in `driver.rs`.

## State, Persistence, And Dependencies
Module-level state is owned by the kernel module/auxiliary driver registration framework.

## Integration Points
Integrates the Nova Rust source files into a single kernel module.

## Risks
Module metadata must match Kbuild/Kconfig expectations. No feature code exists here beyond registration.

## Test Signals
Signals are module load/unload, auxiliary driver registration, and successful compilation of all declared modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/nova.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/Kconfig

## Purpose
Defines OMAP DRM and OMAP Display Subsystem feature options.

## Important APIs, Types, And Functions
`config DRM_OMAP` selects DRM/KMS helpers, bridge connector, display helpers, HDMI, videomode helpers, and optional fbdev DMA helpers. Nested options enable debug, debugfs, IRQ stats, DPI, VENC, OMAP4/OMAP5 HDMI, CEC, SDI, DSI, scaling FCK/PCK ratio, and VENC reset sleep behavior.

## Control Flow
When `DRM_OMAP` is enabled, dependent feature booleans choose which DSS outputs and helpers are compiled by the Makefile.

## State, Persistence, And Dependencies
No runtime state exists here; it controls build-time feature inclusion.

## Integration Points
Integrated by the DRM Kconfig hierarchy and the OMAP DRM Makefile conditional object lists.

## Risks
Platform dependency excludes most non-OMAP builds except compile tests with supported page size. Enabling outputs without matching hardware/device tree still needs runtime probing to succeed.

## Test Signals
Signals are valid Kconfig combinations, build coverage for selected outputs, and expected debug/debugfs features when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/Makefile

## Purpose
Defines the OMAP DRM composite object and conditionally included DSS/output components.

## Important APIs, Types, And Functions
`omapdrm-y` lists core DRM, IRQ, CRTC, plane, overlay, encoder, framebuffer, GEM, DMM/TILER, TCM, and common DSS objects. Conditional entries add fbdev, DPI, VENC, SDI, DSI, HDMI common, HDMI4, CEC, and HDMI5 pieces.

## Control Flow
The kernel build links the selected objects into `omapdrm.o` when `CONFIG_DRM_OMAP` is enabled and adds `-DDEBUG` when OMAP DSS debug is configured.

## State, Persistence, And Dependencies
No runtime state exists here.

## Integration Points
Integrated with OMAP Kconfig options and the DRM driver build.

## Risks
Missing conditional dependencies can produce unresolved references. Optional outputs compile only when their Kconfig symbols are enabled.

## Test Signals
Builds across common OMAP configurations and compile-test variants are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/base.c

## Purpose
Implements OMAP DSS base helpers for DSS device registration, output iteration, device connection, and component readiness discovery from device tree graph links.

## Important APIs, Types, And Functions
Important APIs include `dispc_get_dispc()`, `omapdss_device_register()`, `omapdss_device_unregister()`, `omapdss_device_get()`, `omapdss_device_put()`, `omapdss_find_device_by_node()`, `omapdss_device_next_output()`, `omapdss_device_connect()`, `omapdss_device_disconnect()`, `omapdss_gather_components()`, and `omapdss_stack_is_ready()`.

## Control Flow
DSS devices register on a global protected list. Output iteration returns registered devices with IDs and bridges while managing references. Component gathering walks the DSS node, children, and remote graph endpoints into a component list; readiness checks that OMAPDSS-specific external components have registered.

## State, Persistence, And Dependencies
State includes the global `omapdss_devices_list` protected by `omapdss_devices_lock` and the component list built with devm allocations. Device references are managed through `get_device()`/`put_device()`.

## Integration Points
Depends on OF graph helpers, platform device data, DSS/OMAPDSS structures, bridge-bearing output devices, and Linux device reference counting.

## Risks
Some list traversals such as `omapdss_find_device_by_node()` assume caller-side serialization. Component list is global and reinitialized during gather, so concurrent gather/use would be unsafe. Connect rejects already connected devices with `-EBUSY`.

## Test Signals
Signals include complete component discovery from device tree, stack-ready only after external OMAPDSS components register, balanced device references during output iteration, and successful connect/disconnect logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/base.c -->
