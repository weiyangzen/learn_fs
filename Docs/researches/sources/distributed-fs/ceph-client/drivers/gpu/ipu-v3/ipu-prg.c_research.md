# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-prg.c

## Purpose
Implements the i.MX6QP IPU Prefetch Resolve Gasket, which connects IPU display channels to PRE engines and configures stride, height, base addresses, bypass, shadow updates, and runtime power for tiled framebuffer scanout.

## Important APIs, Types, and Functions
`struct ipu_prg_channel` tracks the PRE assigned to each PRG channel. `struct ipu_prg` stores list membership, device, IPU pointer, MMIO base, clocks, regmap to IOMUXC GPR, and channel state. Exported APIs include `ipu_prg_lookup_by_phandle()`, `ipu_prg_max_active_channels()`, `ipu_prg_present()`, `ipu_prg_format_supported()`, `ipu_prg_enable()/disable()`, `ipu_prg_channel_disable()`, `ipu_prg_channel_configure()`, and `ipu_prg_channel_configure_pending()`. Probe/remove and PM ops manage platform lifetime.

## Control Flow
Probe maps registers, gets IPG/AXI clocks, obtains a syscon regmap, enables clocks, deasserts bypass/shadow defaults, sets thresholds, enables runtime PM, and adds the PRG to a global list. The IPU core looks up PRG by phandle during probe. Display code enables runtime PM, configures a channel by mapping IPU channel to PRG channel, obtaining a PRE, programming stride/height/base/offset/control fields, triggering register update, and polling buffer-ready status. Disable clears channel control, triggers update, releases PRE, and drops runtime PM.

## State and Persistence
Global state is `ipu_prg_list` protected by `ipu_prg_list_mutex`. Per-PRG state includes clock/runtime-PM state, register values, PRE assignments, and IOMUXC GPR linkage. Hardware register state persists until runtime suspend/reset/reconfiguration.

## Dependencies and Integration Points
Built only with DRM and registered alongside the IPU core. Depends on DRM fourcc, runtime PM, clk, regmap/syscon for `fsl,imx6q-iomuxc-gpr`, platform/OF, PRE APIs, and IPU channel definitions. It integrates with `ipu-common.c` through `ipu->prg_priv` and with CPMEM setup, which avoids setting nonzero AXI IDs when PRG is present.

## Risks
Channel mapping only supports selected IPU display channels. PRE acquisition can fail when no compatible PRE is free. Runtime PM and direct clock suspend/resume must stay balanced, or register access can occur while clocks are disabled. Polling `IPU_PRG_STATUS` for buffer readiness can time out. Format support is intentionally narrow, mostly tiled RGB paths; unsupported modifiers/formats must be rejected by callers.

## Test Signals
Probe deferral via phandle, runtime PM cycles, channel configure/disable for every mapped display channel, PRE exhaustion, unsupported format rejection, suspend/resume register access, and display CRCs for tiled framebuffer scanout are important. Timeout logs from configure-pending or status polling indicate PRG/PRE handoff failures.
